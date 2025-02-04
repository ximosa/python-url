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
    """Limpia una transcripción usando Gemini, y genera títulos llamativos, *separados* del texto principal."""

    prompt = f"""
    Actúa como un redactor y narrador experto, con un estilo conversacional, cercano y atractivo. Imagina que estás adaptando un guion para una lectura en voz alta ante una audiencia, buscando hacerlo más natural y cautivador. Además, necesitas generar títulos llamativos para promocionar la lectura en YouTube.

    Sigue estas instrucciones con precisión:

    1.  **Texto Naturalizado:**
        *   Parafrasea, expande y enriquece el texto original. Profundiza en las ideas, añade detalles, ejemplos, analogías y reflexiones personales. El texto resultante debe ser sustancialmente más extenso que el original.
        *   Mantén un tono conversacional y cercano. Escribe como si estuvieras hablando directamente a un oyente, utilizando un lenguaje claro, sencillo y accesible. Evita la jerga técnica o el lenguaje formal.
        *   Elimina cualquier referencia directa: Evita nombres propios, lugares específicos o menciones directas al autor original. Utiliza referencias genéricas como "una persona", "un lugar", "otro personaje", etc.
        *   Concéntrate en la experiencia y las emociones: Transmite las sensaciones, las ideas y las reflexiones que el texto original te inspiró.
        *   Adopta un estilo narrativo cautivador: Escribe como si estuvieras contando una historia, utilizando descripciones vívidas y un ritmo que mantenga al oyente enganchado.
        *   Evita fórmulas repetitivas y clichés: Evita frases como "querido amigo".
        *   Optimiza para la escucha: Utiliza frases cortas, párrafos concisos y una puntuación clara.
        *   **Importante:** NO incluyas ningún título, encabezado o lista dentro del texto naturalizado. Este texto debe ser fluido y continuo, listo para ser leído en voz alta.

    2.  **Títulos para YouTube (Separados):**
        *   Genera 5 títulos llamativos y concisos para un video de YouTube que promocione esta lectura en voz alta.
        *   Estos títulos deben ser atractivos, optimizados para SEO e incluir palabras clave relevantes y elementos que inciten al clic (por ejemplo, preguntas, números, promesas).

    3.  **Formato de la Respuesta:**
        *   Primero, entrega el texto naturalizado completo.
        *   Después, en una sección completamente separada, lista los 5 títulos para YouTube, numerados del 1 al 5.

    Aquí está el texto que debes transformar:

    {texto}

    Texto Naturalizado:
    """

    try:
        model = genai.GenerativeModel(MODEL)
        response = model.generate_content(prompt)
        full_text = response.text

        # Separar el texto naturalizado de los títulos
        try:
            texto_transformado, titulos_texto = full_text.split("Títulos para YouTube (Separados):", 1)
            texto_transformado = texto_transformado.replace("Texto Naturalizado:", "").strip() # Eliminar el encabezado y espacios

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
