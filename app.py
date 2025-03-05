import streamlit as st
import google.generativeai as genai
import os
import tiktoken

st.set_page_config(page_title="texto-corto", layout="wide")

# Obtener la API Key de las variables de entorno
try:
    GOOGLE_API_KEY = os.environ["GOOGLE_API_KEY"]
    genai.configure(api_key=GOOGLE_API_KEY)

    # Listar los modelos disponibles que soporten generateContent
    available_models = [model.name for model in genai.list_models() if 'generateContent' in model.supported_generation_methods]

    if not available_models:
        st.error("No se encontraron modelos compatibles con `generateContent`.  Revisa tu API Key y permisos.")
        st.stop()

    # Permitir al usuario seleccionar un modelo
    MODEL = st.selectbox("Selecciona un modelo Gemini:", available_models)

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

def dividir_texto_coherente(texto, tamano_fragmento_pequeno=750, tamano_fragmento_mediano=1500, overlap_tokens=100):
    """
    Divide el texto intentando mantener la coherencia semántica (oraciones completas).
    Agrega superposición para dar contexto.
    """
    longitud_texto = contar_tokens(texto)
    print(f"Longitud del texto: {longitud_texto} tokens")  # Depuración
    if longitud_texto < 1000:
        return [texto]
    elif longitud_texto < 5000:
        max_tokens = tamano_fragmento_mediano
        st.info(f"Dividiendo en fragmentos medianos (max {max_tokens} tokens).")
    else:
        max_tokens = tamano_fragmento_pequeno
        st.info(f"Dividiendo en fragmentos pequeños (max {max_tokens} tokens).")

    fragmentos = []
    inicio = 0
    while inicio < len(texto):
        print(f"Inicio del bucle: inicio = {inicio}, len(texto) = {len(texto)}")  # Depuración
        fin = encontrar_punto_division(texto, inicio, max_tokens, encoding)
        print(f"Después de encontrar_punto_division: fin = {fin}")  # Depuración

        fragmento = texto[inicio:fin]
        fragmentos.append(fragmento)

        inicio = fin - overlap_tokens if fin - overlap_tokens > 0 else fin
        print(f"Nuevo valor de inicio: inicio = {inicio}")  # Depuración

    print(f"Número de fragmentos creados: {len(fragmentos)}")  # Depuración
    return fragmentos


def encontrar_punto_division(texto, inicio, max_tokens, encoding):
    """
    Encuentra un buen punto para dividir, priorizando el final de una oración.
    """
    # Calcula el punto ideal basado en tokens, no caracteres.
    punto_ideal = inicio
    tokens_acumulados = 0
    for i in range(inicio, len(texto)):
        tokens_acumulados += len(encoding.encode(texto[i]))
        if tokens_acumulados > max_tokens:
            punto_ideal = i
            break

    print(f"Punto ideal calculado: punto_ideal = {punto_ideal}")  # Depuración

    # Busca el final de una oración hacia atrás desde el punto ideal.
    for i in range(min(len(texto) - 1, punto_ideal), inicio, -1):
        print(f"Búsqueda de final de oración: i = {i}, texto[i] = {texto[i]}")  # Depuración
        if texto[i] in ['.', '!', '?']:
            print(f"Final de oración encontrado en i = {i}")  # Depuración
            return i + 1  # Divide después del signo de puntuación.

    # Si no se encuentra un final de oración, divide en el punto ideal (puede romper una oración).
    print(f"No se encontró final de oración, dividiendo en punto_ideal = {punto_ideal}")  # Depuración
    return punto_ideal if punto_ideal > inicio else len(texto)

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
    fragmentos = dividir_texto_coherente(texto)
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
