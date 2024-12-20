import streamlit as st
from io import StringIO
import nltk
import os
import ssl
import re

# Descargar los datos de nltk al inicio
def download_nltk_data():
    try:
        _create_unverified_https_context = ssl._create_unverified_context
    except AttributeError:
         pass
    else:
        ssl._create_default_https_context = _create_unverified_https_context
    try:
        nltk.data.find("tokenizers/punkt_tab/spanish")
    except LookupError:
        st.write("Descargando los datos de nltk...")
        nltk.download('punkt', quiet=True)
        nltk.download('punkt_tab', quiet=True)
        st.success("Datos de NLTK descargados con éxito!")

download_nltk_data()

def procesar_texto_sin_ia(text):
    """Procesa el texto sin IA agregando puntuación básica."""
    sentences = nltk.sent_tokenize(text, language='spanish')
    puntuated_sentences = []
    for sentence in sentences:
         sentence = re.sub(r'\s+', ' ', sentence).strip() # Limpiar espacios
         sentence = re.sub(r',(\s+)(y|o|pero)\b', r', \2', sentence) # espacios después de las comas
         sentence = re.sub(r'\b(y|o|pero)\b', r', \1', sentence).strip() # comas después de conjunciones
         puntuated_sentences.append(sentence + ".")
    return " ".join(puntuated_sentences)

def dividir_transcripcion(text, max_chars=5000):
    """Divide la transcripción en fragmentos más pequeños, por oracion."""
    sentences = nltk.sent_tokenize(text, language='spanish')
    fragments = []
    current_fragment = ""
    for sentence in sentences:
        if len(current_fragment) + len(sentence) < max_chars:
            current_fragment += sentence + " "
        else:
            fragments.append(current_fragment.strip())
            current_fragment = sentence + " "
    fragments.append(current_fragment.strip())
    return fragments


def crear_archivo_descarga(texto, filename="texto_mejorado.txt"):
    stringio = StringIO()
    stringio.write(texto)
    return stringio.getvalue().encode('utf-8')

def main():
    st.title("Optimizador de Transcripciones para Lector de Voz")
    st.markdown("Pega aquí tu transcripción sin puntuación:")

    texto_transcripcion = st.text_area("Transcripción", height=200)
    if texto_transcripcion:
      if st.button("Procesar Texto"):
        with st.spinner("Procesando Texto..."):
            fragments = dividir_transcripcion(texto_transcripcion)
            textos_procesados = []
            for i, fragment in enumerate(fragments):
                st.write(f"Procesando fragmento {i+1}/{len(fragments)}...")
                texto_procesado = procesar_texto_sin_ia(fragment)
                textos_procesados.append(texto_procesado)

            texto_completo = "".join(textos_procesados)
            st.markdown("#### Transcripción Mejorada:")
            st.write(texto_completo)
            st.markdown("#### Descargar como TXT:")
            texto_descarga = crear_archivo_descarga(texto_completo)
            st.download_button(
                label="Descargar TXT",
                data=texto_descarga,
                file_name="transcripcion_mejorada.txt",
                mime="text/plain"
            )

if __name__ == "__main__":
    main()
