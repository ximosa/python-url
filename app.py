import streamlit as st
import re

def limpiar_transcripcion(texto):
    """
    Limpia y formatea una transcripción de YouTube.

    Args:
        texto (str): La transcripción sin formato.

    Returns:
        str: La transcripción formateada para mejor lectura.
    """

    # 1. Eliminar saltos de línea redundantes y espacios extra
    texto = re.sub(r'\s+', ' ', texto).strip()

    # 2. Separar oraciones por puntos (si no los tienen)
    # Asumimos que después de una mayúscula seguida de una palabra y espacio, sigue una nueva oración
    texto = re.sub(r'([A-Z][a-z\s]*)\s', r'\1. ', texto)
    
    # 3. Corregir puntos al final de frases con comas
    texto = re.sub(r'\.\,', ',', texto)
    
     # 4. Corregir espacios antes de los puntos
    texto = re.sub(r'\s+\.', '.', texto)

    # 5. Capitalizar la primera letra de la primera oración
    if texto:
         texto = texto[0].upper() + texto[1:]
    # 6. Capitalizar la primera letra después de un punto
    texto = re.sub(r'\. ([a-z])', lambda m: '. ' + m.group(1).upper(), texto)

    return texto

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

st.title("Limpiador de Transcripciones de YouTube")

transcripcion = st.text_area("Pega aquí tu transcripción sin formato:")

if transcripcion:
    texto_limpio = limpiar_transcripcion(transcripcion)
    st.subheader("Transcripción Formateada:")
    st.write(texto_limpio)
    descargar_texto(texto_limpio)
