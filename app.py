import streamlit as st
import google.generativeai as genai
import os
import textwrap

# Obtener la API Key de los secretos de Streamlit
try:
    GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=GOOGLE_API_KEY)
    MODEL = "gemini-pro"
except KeyError:
    st.error("La API Key de Gemini no está configurada en los secretos de Streamlit.")
    st.stop() # Detener la app si no hay API Key

def dividir_texto(texto, max_tokens=2000):
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
    """
    Limpia una transcripción usando Gemini.

    Args:
      texto (str): La transcripción sin formato.

    Returns:
      str: La transcripción formateada.
    """
    prompt = f"""
        Por favor, analiza y corrige el siguiente texto que es una transcripción de un video de Youtube.
        Asegúrate de que el texto tenga una gramática correcta, puntuación adecuada, respetando los puntos finales, comas y mayúsculas al principio de cada oración.
        Asegúrate de que el texto sea legible, coherente y fácil de entender.
        El texto debe estar lo mas adaptado posible para IA de Text‐to‐Speech.
        Manten el contenido lo más fiel posible a la transcripción original.

        Transcripcion:
        {texto}

        Texto corregido:
    """
    try:
        model = genai.GenerativeModel(MODEL)
        response = model.generate_content(prompt)
        return response.text

    except Exception as e:
        st.error(f"Error al procesar con Gemini: {e}")
        return None


def procesar_transcripcion(texto):
    """Procesa el texto dividiendo en fragmentos y usando Gemini."""
    fragmentos = dividir_texto(texto)
    texto_limpio_completo = ""
    for i, fragmento in enumerate(fragmentos):
        st.write(f"Procesando fragmento {i+1}/{len(fragmentos)}")
        texto_limpio = limpiar_transcripcion_gemini(fragmento)
        if texto_limpio:
            texto_limpio_completo += texto_limpio + " " # Agregar espacio para evitar que las frases se unan
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

st.title("Limpiador de Transcripciones de YouTube (con Gemini)")

transcripcion = st.text_area("Pega aquí tu transcripción sin formato:")

if transcripcion:
    with st.spinner("Procesando con Gemini..."):
        texto_limpio = procesar_transcripcion(transcripcion)
        if texto_limpio:
            st.subheader("Transcripción Formateada:")
            st.write(texto_limpio)
            descargar_texto(texto_limpio)
