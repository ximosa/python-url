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
    """Procesa el texto sin IA agregando puntuación avanzada."""
    # Eliminar saltos de línea
    text = re.sub(r'\n', ' ', text)
    # Eliminar espacios en blanco redundantes
    text = re.sub(r'\s+', ' ', text).strip()

    # Patrones para dividir oraciones (sin referencias a grupos)
    patterns = [
        r',\s+(y|o|pero|porque|aunque|sin embargo)\s+',
        r'\b(cuando|mientras|después|antes|si)\b',
        r',\s+que\s+',
        r'\.\s+(y|o|pero|porque|aunque|sin embargo)\s+'
    ]
    for pattern in patterns:
        text = re.sub(pattern, r', \1, ', text)
    
    # Agregar comas después de frases introductorias
    text = re.sub(r'(en consecuencia|por lo tanto|además|sin embargo|en definitiva|por el contrario)\b', r'\1,', text, flags=re.IGNORECASE)

    # Agregar comas antes de "que"
    text = re.sub(r'\s+(que)\s+', r', \1, ', text)
   
    # Manejar enumeraciones (ej. "uno la vibración del...")
    text = re.sub(r'(\b\d+\b)\s+la', r'\1, la', text)

    # Agregar punto al final de las oraciones
    sentences = nltk.sent_tokenize(text, language='spanish')
    puntuated_sentences = [sentence.strip() + "." for sentence in sentences]

    return " ".join(puntuated_sentences)


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
            texto_procesado = procesar_texto_sin_ia(texto_transcripcion)
            st.markdown("#### Transcripción Mejorada:")
            st.write(texto_procesado)
            st.markdown("#### Descargar como TXT:")
            texto_descarga = crear_archivo_descarga(texto_procesado)
            st.download_button(
                label="Descargar TXT",
                data=texto_descarga,
                file_name="transcripcion_mejorada.txt",
                mime="text/plain"
            )

if __name__ == "__main__":
    main()
