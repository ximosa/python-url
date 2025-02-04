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

def dividir_texto(texto, max_tokens=3500):
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


def limpiar_transcripcion_gemini(texto):
    """Limpia una transcripción usando Gemini, y genera títulos llamativos."""

    prompt = f"""
    Actúa como un redactor, narrador y experto en SEO para YouTube, con un estilo conversacional, cercano y atractivo. Imagina que estás adaptando un guion para un video de YouTube, buscando hacerlo más natural y cautivador, y generando títulos atractivos.

    Sigue estas instrucciones con precisión:

    - **Parafrasea, expande y enriquece el texto:** No te limites a reescribir; profundiza en las ideas, añade detalles, ejemplos, analogías y reflexiones personales. El texto resultante debe ser sustancialmente más extenso que el original.
    - **Mantén un tono conversacional y cercano:** Escribe como si estuvieras hablando directamente a un oyente, utilizando un lenguaje claro, sencillo y accesible. Evita la jerga técnica o el lenguaje formal.
    - **Elimina cualquier referencia directa:** Evita nombres propios, lugares específicos o menciones directas al autor original. Utiliza referencias genéricas como "una persona", "un lugar", "otro personaje", etc.
    - **Concéntrate en la experiencia y las emociones:** Transmite las sensaciones, las ideas y las reflexiones que el texto original te inspiró.
    - **Adopta un estilo narrativo cautivador:** Escribe como si estuvieras contando una historia, utilizando descripciones vívidas y un ritmo que mantenga al oyente enganchado.
    - **Evita fórmulas repetitivas y clichés:** Evita frases como "querido amigo".
    - **Optimiza para la escucha:** Utiliza frases cortas, párrafos concisos y una puntuación clara.
    - **Genera 5 títulos llamativos para YouTube:** Deben ser concisos, atractivos y optimizados para SEO. Incluye palabras clave relevantes y elementos que inciten al clic. Enumera los títulos del 1 al 5.
    - **Entrega primero los 5 títulos en formato de lista enumerada, y luego el texto transformado.** Sin encabezados, negritas, ni formato adicional.

    Aquí está el texto que debes transformar:

    {texto}

    Lista de títulos:
    """

    try:
        model = genai.GenerativeModel(MODEL)
        response = model.generate_content(prompt)
        full_text = response.text

        # Separar los títulos del texto principal
        try:
            titulos_texto, texto_transformado = full_text.split("Texto transformado:", 1)

            # Limpiar los títulos y convertirlos en una lista
            titulos = [t.strip() for t in titulos_texto.split('\n') if t.strip() and t.strip()[0].isdigit()]
        except ValueError:
            titulos = ["Error al extraer los títulos"]
            texto_transformado = full_text  # Usar el texto completo si no se pueden separar
            print("Error al separar títulos y texto") # Añadido para depuración

        return titulos, texto_transformado

    except Exception as e:
        st.error(f"Error al procesar con Gemini: {e}")
        print(f"Error en limpiar_transcripcion_gemini: {e}")  # Añadido para depuración
        return [], None


def procesar_transcripcion(texto):
    """Procesa el texto dividiendo en fragmentos y usando Gemini."""
    fragmentos = dividir_texto(texto)
    texto_limpio_completo = ""
    todos_los_titulos = []

    for i, fragmento in enumerate(fragmentos):
        st.write(f"Procesando fragmento {i+1}/{len(fragmentos)}")
        titulos, texto_procesado = limpiar_transcripcion_gemini(fragmento)

        if not texto_procesado:
            return None, None

        todos_los_titulos.extend(titulos)
        texto_limpio_completo += texto_procesado + " "
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


if transcripcion:
    if st.button("Procesar y Naturalizar"):
        with st.spinner("Procesando con Gemini..."):
            titulos_generados, texto_limpio = procesar_transcripcion(transcripcion)
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
