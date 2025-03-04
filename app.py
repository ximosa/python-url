import streamlit as st
import google.generativeai as genai
import os
import tiktoken

st.set_page_config(page_title="texto-corto", layout="wide")

# Obtener la API Key de las variables de entorno
try:
    GOOGLE_API_KEY = os.environ["GOOGLE_API_KEY"]
    genai.configure(api_key=GOOGLE_API_KEY)

    # Listar los modelos disponibles para encontrar el correcto
    available_models = [model.name for model in genai.list_models() if 'generateContent' in model.supported_generation_methods]

    if not available_models:
        st.error("No se encontraron modelos compatibles con `generateContent`.  Revisa tu API Key y permisos.")
        st.stop()

    # Selecciona un modelo (prioriza 'gemini-1.5-flash-001' si está disponible)
    MODEL = None
    if 'gemini-1.5-flash-001' in available_models:
        MODEL = 'gemini-1.5-flash-001'
    elif 'gemini-1.5-pro' in available_models: #cambio por si el flash no esta
        MODEL = 'gemini-1.5-pro'
    elif 'gemini-1.0-pro' in available_models and 'gemini-1.0-pro' not in ['gemini-1.0-pro-vision','gemini-pro-vision']:#evitar vision, ya no esta soportado
         MODEL = 'gemini-1.0-pro'   # Más robusto si flash no está disponible
    elif any("gemini-pro" in model for model in available_models):
        MODEL = next(model for model in available_models if "gemini-pro" in model) #elige uno generico gemini-pro
    else:
        st.error("No se encontró un modelo Gemini adecuado (flash o pro) en la lista de modelos disponibles. Revisa la salida de ListModels().")
        st.stop()


    st.write(f"Usando modelo: {MODEL}")

except KeyError:
    st.error("La variable de entorno GOOGLE_API_KEY no está configurada.")
    st.stop()

# Inicializa el tokenizador
try:
    encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")  # O el modelo que uses
except Exception as e:
    st.error(f"Error al cargar el tokenizador: {e}. Asegúrate de tener tiktoken instalado (`pip install tiktoken`).")
    st.stop()

def contar_tokens(texto):
    return len(encoding.encode(texto))

def limpiar_transcripcion_gemini(texto):
    prompt = f"""
       Reescribe el siguiente texto para que sea adecuado para la lectura por voz de Google.  Adopta un tono profesional, formal y narrativo en primera persona, como si compartieras tus propias reflexiones sobre el tema.

       Sigue estas pautas estrictamente:

       *   **Objetivo Principal:** Optimiza el texto para la claridad y fluidez de la lectura por voz.  Considera la entonación y las pausas naturales.
       *   **Longitud:**  Mantén la longitud del texto resultante entre el 95% y el 105% del texto original.
       *   **Expansión:** No te limites a resumir.  Expande las ideas, añade detalles y ejemplos relevantes para enriquecer el texto.  Si el texto parece incompleto, complétalo con información adicional.
       *   **Título:** Genera un título conciso y atractivo que resuma el tema principal.
       *   **Anonimato:** Evita mencionar nombres propios de personas o lugares específicos. Refiérete a ellos como "un individuo", "un lugar", "otro personaje", etc. Esto facilita la comprensión auditiva.
       *   **Estilo:**
            *   Utiliza un lenguaje claro, directo y profesional.  Evita jerga innecesaria.
            *   Escribe en primera persona, como si estuvieras compartiendo tus propias experiencias y conclusiones.
            *   Adopta un tono narrativo y reflexivo.
       *   **Elimina:** Evita saludos informales como "Hola amigos" o introducciones similares. Comienza directamente con el tema.
       *   **Adaptación para Voz:**
            *   Considera cómo se pronunciarán las palabras y ajusta la redacción para facilitar la dicción del lector de voz.
            *   Utiliza oraciones bien estructuradas con pausas naturales.
            *   Asegúrate de que el texto fluya lógicamente para una fácil comprensión auditiva.

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
    with st.spinner("Procesando con Gemini..."):
        texto_limpio = limpiar_transcripcion_gemini(texto)
        if texto_limpio:
            st.success("¡Texto procesado!")
            return texto_limpio
        else:
            return None

def descargar_texto(texto_formateado):
    return st.download_button(
        label="Descargar Texto",
        data=texto_formateado.encode('utf-8'),
        file_name="transcripcion_formateada.txt",
        mime="text/plain"
    )

st.title("Optimizador de Texto para Lectura por Voz")
st.markdown("Introduce el texto que quieres optimizar para la lectura por voz de Google.")

transcripcion = st.text_area("Texto a optimizar:", height=300) #Aumentar el area

if st.button("Optimizar Texto"):
    if transcripcion:
        longitud_original = contar_tokens(transcripcion)
        st.info(f"Longitud del texto original: {longitud_original} tokens.")

        texto_limpio = procesar_transcripcion(transcripcion)

        if texto_limpio:
            longitud_resultante = contar_tokens(texto_limpio)
            st.info(f"Longitud del texto resultante: {longitud_resultante} tokens.")

            st.subheader("Texto Optimizado:")
            st.write(texto_limpio) #Muestra directo el texto optimizado
            descargar_texto(texto_limpio) #Permite descargarlo
    else:
        st.warning("Por favor, introduce el texto a procesar.")
