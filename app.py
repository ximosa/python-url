import streamlit as st
import google.generativeai as genai
import os
import textwrap
import time

st.set_page_config(
    page_title="Texto Naturalizador",
    layout="wide"
)

# Obtener la API Key de las variables de entorno
try:
    GOOGLE_API_KEY = os.environ["GOOGLE_API_KEY"]
    genai.configure(api_key=GOOGLE_API_KEY)
    MODEL = "gemini-pro"  # Puedes experimentar con "gemini-pro-vision" si quieres que el modelo pueda analizar imagenes
except KeyError:
    st.error("La variable de entorno GOOGLE_API_KEY no está configurada.")
    st.stop() # Detener la app si no hay API Key

def dividir_texto(texto, max_tokens=3000): # Reducir el tamaño de los fragmentos para mejor procesamiento
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
    """
    Limpia una transcripción usando Gemini, añadiendo más "humanidad" al texto.

    Args:
      texto (str): La transcripción sin formato.
      iteracion (int): Número de iteración del proceso (para ajustar el prompt).

    Returns:
      str: La transcripción formateada.
    """

    # Ajustar el prompt para que sea más adaptable a diferentes iteraciones
    if iteracion == 1:
        prompt = f"""
           Actúa como un narrador de historias experto, con un tono conversacional, cercano y entusiasta. Imagina que estás compartiendo una experiencia personal con un amigo, lleno de detalles vívidos y emociones genuinas.

        Sigue estas pautas con cuidado:

        - **Parafrasea y expande el texto original:** No te limites a reescribir; profundiza en las ideas, añade ejemplos, anécdotas y reflexiones personales.  Haz que cada punto sea más rico y completo. El texto resultante debería ser significativamente más largo que el original.
        - **Crea un título atractivo y relevante:**  El título debe captar la esencia del texto y despertar la curiosidad del lector.
        - **Elimina referencias directas:** Evita nombres propios, lugares específicos o menciones directas al autor original.  En su lugar, utiliza referencias genéricas como "una persona", "un lugar", "otro personaje", etc.
        - **Enfócate en la experiencia humana:**  Transmite las emociones, las ideas y las reflexiones que el texto original te inspiró.  ¿Qué aprendiste? ¿Cómo te hizo sentir? ¿Qué preguntas te planteó?
        - **Adopta un estilo narrativo:**  Escribe como si estuvieras contando una historia, utilizando un lenguaje descriptivo, diálogos (si son apropiados) y un ritmo que mantenga al lector enganchado.
        - **Utiliza un lenguaje claro, sencillo y accesible:** Evita la jerga técnica o el lenguaje rebuscado.  Escribe como si estuvieras hablando con alguien que no está familiarizado con el tema.
        - **Optimiza para la lectura en voz alta:**  Utiliza frases cortas, párrafos concisos y una puntuación clara para facilitar la lectura por parte de un lector de voz.  Asegúrate de que el texto fluya de forma natural y agradable al oído.
        - **Evita cualquier formato innecesario:**  Entrégame solo el texto, sin encabezados, negritas, asteriscos ni ningún otro tipo de formato.

            Aquí está el texto que debes transformar:

            {texto}

            Texto transformado:
        """
    else:
        prompt = f"""
            Actúa como un escritor profesional puliendo un borrador.  Tu objetivo es refinar el texto existente, haciéndolo aún más natural, atractivo y humano.  Adopta un tono conversacional, cercano y entusiasta, como si estuvieras compartiendo una experiencia personal con un amigo.

            Sigue estas pautas con cuidado:

            - **Profundiza en la narración:**  Añade más detalles sensoriales, anécdotas personales y reflexiones profundas.  Haz que el texto cobre vida y resuene con el lector a un nivel emocional.
            - **Varía la estructura de las oraciones:**  Combina frases cortas y directas con frases más largas y elaboradas para crear un ritmo más dinámico y atractivo.
            - **Utiliza un lenguaje más evocador:**  Reemplaza palabras comunes con sinónimos más precisos y descriptivos.  Utiliza metáforas, símiles y otras figuras retóricas para enriquecer el texto.
            - **Añade más "voz":**  Inyecta tu propia personalidad y perspectiva en el texto.  Haz que se sienta como si estuvieras hablando directamente con el lector.
            - **Optimiza para la lectura en voz alta:**  Presta especial atención al ritmo, la fluidez y la claridad del texto.  Asegúrate de que sea agradable y fácil de escuchar.
            - **Evita la repetición:**  Identifica y elimina cualquier palabra, frase o idea que se repita innecesariamente.
            - **Mantén la coherencia:**  Asegúrate de que todas las partes del texto encajen entre sí y fluyan de forma lógica.

            Aquí está el texto que debes refinar:

            {texto}

            Texto Refinado:
        """


    try:
        model = genai.GenerativeModel(MODEL)
        response = model.generate_content(prompt)
        return response.text

    except Exception as e:
        st.error(f"Error al procesar con Gemini: {e}")
        return None


def procesar_transcripcion(texto, num_iteraciones=2): #Permite definir el numero de interaciones
    """Procesa el texto dividiendo en fragmentos y usando Gemini iterativamente."""
    fragmentos = dividir_texto(texto)
    texto_limpio_completo = ""

    for i, fragmento in enumerate(fragmentos):
        st.write(f"Procesando fragmento {i+1}/{len(fragmentos)}")
        texto_procesado = fragmento
        for j in range(num_iteraciones):
             st.write(f"Iteración {j+1}/{num_iteraciones} del fragmento {i+1}")
             texto_procesado = limpiar_transcripcion_gemini(texto_procesado, iteracion=j+1)
             if not texto_procesado:
                 return None # Detener si falla una iteración

        texto_limpio_completo += texto_procesado + " " # Agregar espacio para evitar que las frases se unan
        time.sleep(2) # Pausa para evitar saturar la API

    return texto_limpio_completo.strip()

def descargar_texto(texto_formateado):
    """
    Genera un enlace de descarga para el texto formateado.

    Args:
        texto_formateado (str): El texto formateado.

    Returns:
        streamlit.components.v1.html: Enlace de descarga.
    """
    return st.download_button(
        label="Descargar Texto",
        data=texto_formateado.encode('utf-8'),
        file_name="transcripcion_formateada.txt",
        mime="text/plain"
    )

st.title("Naturalizador de Textos (con Gemini)")

transcripcion = st.text_area("Pega aquí tu transcripción sin formato:", height=300) # Aumentar el tamaño del text_area

num_iteraciones = st.slider("Número de iteraciones:", min_value=1, max_value=3, value=2, step=1) # Permitir al usuario controlar las iteraciones

if transcripcion:
    if st.button("Procesar y Naturalizar"): # Botón para iniciar el proceso
        with st.spinner(f"Procesando con Gemini ( {num_iteraciones} iteraciones )..."):
            texto_limpio = procesar_transcripcion(transcripcion, num_iteraciones=num_iteraciones)
            if texto_limpio:
                st.subheader("Texto Naturalizado:")
                st.write(texto_limpio)
                descargar_texto(texto_limpio)
            else:
                st.error("Ocurrió un error durante el procesamiento.  Revisa tu API key y el texto de entrada.")
