import streamlit as st
import google.generativeai as genai
from io import StringIO
import nltk
import os
import ssl
import re

# Configura la clave de API de Gemini desde los secretos de streamlit
GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
genai.configure(api_key=GOOGLE_API_KEY)

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

# Descargar los datos de nltk al inicio
download_nltk_data()
    
def mejorar_texto_gemini(text):
    model = genai.GenerativeModel('gemini-pro')
    prompt = f"""
    Por favor, mejora la siguiente transcripción para que sea más adecuada para un lector de voz.
    Agrega puntuación (comas, puntos, etc.), crea oraciones claras y breves,
    y considera el flujo natural de la lectura.
    Devuelve SOLO el texto mejorado, sin incluir ningún texto adicional.
    
    {text}
    """

    response = model.generate_content(prompt)
    return response.text.strip()

def eliminar_prompt(text):
    """Elimina el texto del prompt del resultado."""
    prompt_text = "Por favor, mejora la siguiente transcripción para que sea más adecuada para un lector de voz. Agrega puntuación (comas, puntos, etc.), crea oraciones claras y breves, y considera el flujo natural de la lectura. Devuelve SOLO el texto mejorado, sin incluir ningún texto adicional. Transcripción:"
    cleaned_text = re.sub(re.escape(prompt_text), '', text, flags=re.IGNORECASE).strip()
    return cleaned_text

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
      if st.button("Procesar con Gemini"):
        with st.spinner("Procesando con Gemini..."):
          fragments = dividir_transcripcion(texto_transcripcion)
          textos_mejorados = []
          for i, fragment in enumerate(fragments):
            st.write(f"Procesando fragmento {i+1}/{len(fragments)}...")
            texto_mejorado = mejorar_texto_gemini(fragment)
            texto_mejorado = re.sub(r'\*','', texto_mejorado)  # Eliminar asteriscos
            texto_mejorado = eliminar_prompt(texto_mejorado) # Eliminar el prompt
            textos_mejorados.append(texto_mejorado)
          texto_completo = " ".join(textos_mejorados)
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
