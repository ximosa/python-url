import streamlit as st
import google.generativeai as genai
import os
import time

st.set_page_config(
    page_title="Naturalizador de Textos",
    layout="wide"
)

# Obtener la API Key de las variables de entorno
try:
    GOOGLE_API_KEY = os.environ["GOOGLE_API_KEY"]
    genai.configure(api_key=GOOGLE_API_KEY)
    MODEL = "gemini-pro"
except KeyError:
    st.error("La variable de entorno GOOGLE_API_KEY no está configurada.")
    st.stop()

def dividir_texto(texto, max_tokens=3500):  # Aumentar un poco el tamaño del fragmento
    """Divide el texto en fragmentos más pequeños."""
    tokens = texto.split()
    fragmentos = []
    fragmento_actual = []
    cuenta_tokens = 0

    for token in tokens:
        cuenta_tokens += 1
        if cuenta_tokens <= max_tokens:
            fragmento_actual.append(token)
        else:
            fragmentos.append(" ".join(fragmento_actual))
            fragmento_actual = [token]
            cuenta_tokens = 1
    if fragmento_actual:
        fragmentos.append(" ".join(fragmento_actual))
    return fragmentos


def limpiar_transcripcion_gemini(texto, iteracion=1):
    """Limpia una transcripción usando Gemini, y genera títulos llamativos."""

    if iteracion == 1:
        prompt = f"""
        Actúa como un redactor, narrador y experto en SEO para YouTube, con un estilo conversacional, cercano y atractivo. Imagina que estás adaptando un guion para una audiencia en un auditorio repleto de personas, buscando hacerlo más natural y cautivador, y que además necesitas generar títulos atractivos para el video resultante.

        Sigue estas instrucciones con precisión:

        - **Parafrasea, expande y enriquece el texto:** No te limites a reescribir; profundiza en las ideas, añade detalles, ejemplos, analogías y reflexiones personales. El texto resultante debe ser sustancialmente más extenso que el original, apuntando a al menos el doble de longitud.
        - **Mantén un tono conversacional y cercano:** Escribe como si estuvieras hablando directamente a un oyente, utilizando un lenguaje claro, sencillo y accesible. Evita la jerga técnica o el lenguaje formal.
        - **Elimina cualquier referencia directa:** Evita nombres propios, lugares específicos o menciones directas al autor original. Utiliza referencias genéricas como "una persona", "un lugar", "otro personaje", etc.
        - **Concéntrate en la experiencia y las emociones:** Transmite las sensaciones, las ideas y las reflexiones que el texto original te inspiró. ¿Qué aprendiste? ¿Cómo te hizo sentir? ¿Qué preguntas te planteó?
        - **Adopta un estilo narrativo cautivador:** Escribe como si estuvieras contando una historia, utilizando descripciones vívidas, diálogos (si son apropiados) y un ritmo que mantenga al oyente enganchado.
        - **Evita fórmulas repetitivas y clichés:** **Específicamente, evita el uso de frases como "querido amigo" o cualquier otra fórmula de saludo similar.** Busca formas más originales y naturales de conectar con el oyente.
        - **Optimiza para la escucha:** Utiliza frases cortas, párrafos concisos y una puntuación clara para facilitar la comprensión auditiva. Asegúrate de que el texto fluya de forma natural y sea agradable de escuchar.
        - **Crea un título si es necesario:** Si el texto no tiene un título claro, crea uno que sea atractivo y relevante.
        - **Genera 5 títulos llamativos para un video de YouTube basado en el contenido transformado:** Estos títulos deben ser concisos, atractivos y optimizados para SEO.  Incluye palabras clave relevantes y elementos que inciten al clic (por ejemplo, preguntas, números, promesas).  Enumera los títulos del 1 al 5.
        - **Entrega primero los 5 títulos en formato de lista enumerada, y luego el texto transformado:** Sin encabezados, negritas, asteriscos ni ningún otro tipo de formato.

        Aquí está el texto que debes transformar:

        {texto}

        Lista de títulos:
        """

    else:
        prompt = f"""
            Actúa como un coferenciante en un auditorio repleto de personas y experto en SEO para YouTube, revisando un borrador para pulirlo y maximizar su impacto en el oyente, y optimizando los títulos del video. Tu objetivo es refinar el texto existente, haciéndolo aún más natural, atractivo y envolvente, y generando mejores títulos.

            Sigue estas pautas con atención:

            - **Profundiza en la narración:** Añade más detalles sensoriales, anécdotas personales y reflexiones profundas. Haz que el texto cobre vida y conecte con el oyente a un nivel emocional. Amplía la información.
            - **Varía la estructura de las oraciones:** Combina frases cortas y directas con frases más largas y elaboradas para crear un ritmo más dinámico y cautivador.
            - **Utiliza un lenguaje más rico y evocador:** Reemplaza palabras comunes con sinónimos más precisos y descriptivos. Utiliza metáforas, símiles y otras figuras retóricas para enriquecer el texto y hacerlo más memorable.
            - **Añade más "voz" y personalidad:** Inyecta tu propio estilo y perspectiva en el texto. Haz que se sienta como si estuvieras hablando directamente con el oyente, compartiendo una experiencia genuina.
            - **Optimiza para la escucha:** Presta especial atención al ritmo, la fluidez y la claridad del texto. Asegúrate de que sea agradable y fácil de seguir para el oído.
            - **Evita la repetición y la redundancia:** Identifica y elimina cualquier palabra, frase o idea que se repita innecesariamente.
            - **Mantén la coherencia y la cohesión:** Asegúrate de que todas las partes del texto encajen entre sí y fluyan de forma lógica, creando una experiencia auditiva fluida y armoniosa.
            - **Evita nombres propios y alusión a personas:** **Específicamente, evita el uso de frases como "querido amigo" o cualquier otra fórmula de saludo similar.** Busca formas más originales y naturales de conectar con el oyente.
            - **Revisa los 5 títulos generados anteriormente y optimízalos para maximizar su atractivo y SEO:** Asegúrate de que sean concisos, incluyan palabras clave relevantes y sean irresistibles para el espectador.
            - **Entrega primero los 5 títulos revisados en formato de lista enumerada, y luego el texto transformado:** Sin encabezados, negritas, asteriscos ni ningún otro tipo de formato.

            Aquí está el texto que debes refinar:

            {texto}

            Lista de títulos revisados:
        """

    try:
        model = genai.GenerativeModel(MODEL)
        response = model = genai.GenerativeModel(MODEL)
        response = model.generate_content(prompt)
        full_text = response.text
        # Separar los títulos del texto principal
        try:
            titulo_separador = "Texto transformado:" if iteracion == 1 else "Texto Refinado:"
            titulos_texto, texto_transformado = full_text.split(titulo_separador, 1)

            # Limpiar los títulos y convertirlos en una lista
            titulos = [t.strip() for t in titulos_texto.split('\n') if t.strip() and t.strip()[0].isdigit()]
        except ValueError:
            titulos = ["Error al extraer los títulos"]
            texto_transformado = full_text  # Usar el texto completo si no se pueden separar

        return titulos, texto_transformado

    except Exception as e:
        st.error(f"Error al procesar con Gemini: {e}")
        return [], None


def procesar_transcripcion(texto, num_iteraciones=2):
    """Procesa el texto dividiendo en fragmentos y usando Gemini iterativamente."""
    fragmentos = dividir_texto(texto)
    texto_limpio_completo = ""
    todos_los_titulos = []  # Lista para acumular todos los títulos

    for i, fragmento in enumerate(fragmentos):
        st.write(f"Procesando fragmento {i+1}/{len(fragmentos)}")
        texto_procesado = fragmento
        for j in range(num_iteraciones):
            st.write(f"Iteración {j+1}/{num_iteraciones} del fragmento {i+1}")
            titulos, texto_procesado = limpiar_transcripcion_gemini(texto_procesado, iteracion=j+1)
            if not texto_procesado:
                return None, None  # Devolver None para ambos si hay un error

            todos_los_titulos.extend(titulos)  # Acumular los títulos
            time.sleep(2)
    return todos_los_titulos, texto_limpio_completo.strip()


def descargar_texto(texto_formateado):
    """Genera un enlace de descarga para el texto formateado."""
    return st.download_button(
        label="Descargar Texto",
        data=texto_formateado.encode('utf-8'),
        file_name="transcripcion_formateada.txt",
        mime="text/plain"
    )


st.title("Naturalizador de Textos (con Gemini)")

transcripcion = st.text_area("Pega aquí tu transcripción sin formato:", height=300)

num_iteraciones = st.slider("Número de iteraciones:", min_value=1, max_value=3, value=2, step=1)

if transcripcion:
    if st.button("Procesar y Naturalizar"):
        with st.spinner(f"Procesando con Gemini ( {num_iteraciones} iteraciones )..."):
            titulos_generados, texto_limpio = procesar_transcripcion(transcripcion, num_iteraciones=num_iteraciones)
            if texto_limpio:
                st.subheader("Texto Naturalizado:")
                st.write(texto_limpio)
                descargar_texto(texto_limpio)

                if titulos_generados:
                    st.subheader("Títulos Sugeridos:")
                    for titulo in titulos_generados:
                        st.write(f"- {titulo}")

                else:
                    st.warning("No se pudieron generar títulos.")
            else:
                st.error("Ocurrió un error durante el procesamiento. Revisa tu API key y el texto de entrada.")
