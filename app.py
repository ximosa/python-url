import streamlit as st
import google.generativeai as genai
import os
import tiktoken

st.set_page_config(page_title="texto-corto", layout="wide")

# Obtener la API Key de las variables de entorno
try:
    GOOGLE_API_KEY = os.environ["GOOGLE_API_KEY"]
    print(f"API Key: '{GOOGLE_API_KEY}'")  # Imprime la API Key para verificar

    genai.configure(api_key=GOOGLE_API_KEY)

    # Listar los modelos disponibles
    st.write("Modelos disponibles:")
    available_models = list(genai.list_models())
    for model in available_models:
        st.write(model)

    if not available_models:
        st.error("No se encontraron modelos disponibles. Verifica tu API Key y permisos.")
        st.stop()

    # Selecciona un modelo (prioriza 'gemini-1.5-flash-001', luego 'gemini-1.0-pro', luego cualquier 'gemini-pro')
    MODEL = None
    for model in available_models:
        if "gemini-1.5-flash-001" in model.name.lower():
            MODEL = model.name
            break
    if MODEL is None:
        for model in available_models:
            if "gemini-1.0-pro" in model.name.lower():
                MODEL = model.name
                break
    if MODEL is None:
        for model in available_models:
            if "gemini-pro" in model.name.lower():
                MODEL = model.name
                break


    if MODEL is None:
        st.error("No se encontró un modelo 'gemini-1.5-flash-001', 'gemini-1.0-pro' o similar en la lista de modelos disponibles. Revisa la salida de ListModels().")
        st.stop()

    st.write(f"Usando modelo: {MODEL}")  # Imprime el modelo que se va a usar

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

def dividir_texto_dinamico(texto, tamano_fragmento_pequeno=750, tamano_fragmento_mediano=1500):
    longitud_texto = contar_tokens(texto)
    if longitud_texto < 1000:
        return [texto]
    elif longitud_texto < 5000:
        max_tokens = tamano_fragmento_mediano
        st.info(f"Dividiendo en fragmentos medianos (max {max_tokens} tokens).")
    else:
        max_tokens = tamano_fragmento_pequeno
        st.info(f"Dividiendo en fragmentos pequeños (max {max_tokens} tokens).")

    fragmentos = []
    fragmento_actual = []
    cuenta_tokens_actual = 0

    palabras = texto.split()
    for palabra in palabras:
        tokens_palabra = contar_tokens(palabra)

        if cuenta_tokens_actual + tokens_palabra <= max_tokens:
            fragmento_actual.append(palabra)
            cuenta_tokens_actual += tokens_palabra
        else:
            fragmentos.append(" ".join(fragmento_actual))
            fragmento_actual = [palabra]
            cuenta_tokens_actual = tokens_palabra

    if fragmento_actual:
        fragmentos.append(" ".join(fragmento_actual))

    st.info(f"Texto dividido en {len(fragmentos)} fragmentos.")
    return fragmentos

def limpiar_transcripcion_gemini(texto):
    prompt = f"""
       Reescribe el siguiente texto con un tono más profesional y formal. Escribe en primera persona, como si tú hubieras vivido la experiencia o reflexionado sobre los temas presentados.
    Sigue estas pautas:
    - Reescribe el siguiente texto utilizando tus propias palabras, y asegúrate de que **el texto resultante tenga entre el 90% y el 110% de la longitud (en número de tokens) del texto de entrada**.
    - No reduzcas la información, e intenta expandir cada punto si es posible. Si el texto parece incompleto o le falta algo, añade detalles relevantes.
    - No me generes un resumen, quiero un texto parafraseado y expandido con una longitud comparable al texto original.
    - Dale un titulo preciso y llamativo.
    - Evita mencionar nombres de personajes o del autor.
    - Concentra el resumen en la experiencia general, las ideas principales, los temas y las emociones transmitidas por el texto.
    - Utiliza un lenguaje serio y profesional, como si estuvieras compartiendo tus propias conclusiones tras una profunda reflexión.
    - No uses nombres propios ni nombres de lugares específicos, refiérete a ellos como "un lugar", "una persona", otro personaje", etc.
    - Usa un lenguaje claro y directo
    - Escribe como si estuvieras narrando una historia
    - Evita decir hola amigos,o cosas similrares, se más serio y estricto en tu informacion.
    -Importante, el texto debe adaptarse para que el lector de voz de google lo lea lo mejor posible
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
    fragmentos = dividir_texto_dinamico(texto)
    texto_limpio_completo = ""
    for i, fragmento in enumerate(fragmentos):
        st.write(f"Procesando fragmento {i + 1}/{len(fragmentos)}")
        texto_limpio = limpiar_transcripcion_gemini(fragmento)
        if texto_limpio:
            texto_limpio_completo += texto_limpio + " "
    return texto_limpio_completo.strip()

def descargar_texto(texto_formateado):
    return st.download_button(
        label="Descargar Texto",
        data=texto_formateado.encode('utf-8'),
        file_name="transcripcion_formateada.txt",
        mime="text/plain"
    )

st.title("Limpiador de Transcripciones de YouTube (con Gemini)")

transcripcion = st.text_area("Pega aquí tu transcripción sin formato:")

if 'texto_procesado' not in st.session_state:
    st.session_state['texto_procesado'] = ""

if st.button("Procesar Texto"):
    if transcripcion:
        longitud_original = contar_tokens(transcripcion)
        st.info(f"Longitud del texto original: {longitud_original} tokens.")

        with st.spinner("Procesando con Gemini..."):
            texto_limpio = procesar_transcripcion(transcripcion)
            if texto_limpio:
                st.session_state['texto_procesado'] = texto_limpio
                st.success("¡Texto procesado!")

                longitud_resultante = contar_tokens(texto_limpio)
                st.info(f"Longitud del texto resultante: {longitud_resultante} tokens.")
    else:
        st.warning("Por favor, introduce el texto a procesar.")

if st.session_state['texto_procesado']:
    st.subheader("Transcripción Formateada:")
    st.write(st.session_state['texto_procesado'])
    descargar_texto(st.session_state['texto_procesado'])
