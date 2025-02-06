import streamlit as st
import google.generativeai as genai
import os
import textwrap
import tiktoken  # Importa la librería tiktoken

st.set_page_config(
    page_title="texto-corto",
    layout="wide"
)

# Obtener la API Key de las variables de entorno
try:
    GOOGLE_API_KEY = os.environ["GOOGLE_API_KEY"]
    genai.configure(api_key=GOOGLE_API_KEY)
    MODEL = "gemini-pro"
except KeyError:
    st.error("La variable de entorno GOOGLE_API_KEY no está configurada.")
    st.stop()  # Detener la app si no hay API Key

# Inicializa el tokenizador (¡IMPORTANTE!)
try:
    encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")  # O el modelo que uses
except Exception as e:
    st.error(f"Error al cargar el tokenizador: {e}. Asegúrate de tener tiktoken instalado (`pip install tiktoken`).")
    st.stop()


def contar_tokens(texto):
    """Cuenta tokens usando tiktoken."""
    return len(encoding.encode(texto))


def dividir_texto_dinamico(texto, tamano_fragmento_pequeno=750, tamano_fragmento_mediano=1500):
    """Divide el texto en fragmentos más pequeños dinámicamente."""
    longitud_texto = contar_tokens(texto)

    if longitud_texto < 1000:
        return [texto]  # No dividir si es muy corto
    elif longitud_texto < 5000:
        max_tokens = tamano_fragmento_mediano
        st.info(f"Dividiendo en fragmentos medianos (max {max_tokens} tokens).")
    else:
        max_tokens = tamano_fragmento_pequeno
        st.info(f"Dividiendo en fragmentos pequeños (max {max_tokens} tokens).")
    
    fragmentos = []
    fragmento_actual = []
    cuenta_tokens_actual = 0

    palabras = texto.split()  # Dividir por palabras para mejor control
    for palabra in palabras:
        tokens_palabra = contar_tokens(palabra)  # Tokenizar cada palabra

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
    """
    Limpia una transcripción usando Gemini.

    Args:
      texto (str): La transcripción sin formato.

    Returns:
      str: La transcripción formateada.
    """
    prompt = f"""
       Actúa como un escritor usando un tono conversacional y ameno, como si le contaras la historia a un amigo. Escribe en primera persona, como si tú hubieras vivido la experiencia o reflexionado sobre los temas presentados.
    Sigue estas pautas:
    - Reescribe el siguiente texto utilizando tus propias palabras, y asegúrate de que **el texto resultante tenga entre el 90% y el 110% de la longitud (en número de tokens) del texto de entrada**.
    - No reduzcas la información, e intenta expandir cada punto si es posible. Si el texto parece incompleto o le falta algo, añade detalles relevantes.
    - No me generes un resumen, quiero un texto parafraseado y expandido con una longitud comparable al texto original.
    - Dale un titulo preciso y llamativo.
    - Evita mencionar nombres de personajes o del autor.
    - Concentra el resumen en la experiencia general, las ideas principales, los temas y las emociones transmitidas por el texto.
    - Utiliza un lenguaje evocador y personal, como si estuvieras compartiendo tus propias conclusiones tras una profunda reflexión.
    - No uses nombres propios ni nombres de lugares específicos, refiérete a ellos como "un lugar", "una persona", "otro personaje", etc.
    - Usa un lenguaje claro y directo
    - Escribe como si estuvieras narrando una historia
    - Evita los asteriscos en el texto, dame tan solo el texto sin encabezados ni texto en negrita
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
    """Procesa el texto dividiendo en fragmentos y usando Gemini."""
    fragmentos = dividir_texto_dinamico(texto)
    texto_limpio_completo = ""
    for i, fragmento in enumerate(fragmentos):
        st.write(f"Procesando fragmento {i + 1}/{len(fragmentos)}")
        texto_limpio = limpiar_transcripcion_gemini(fragmento)
        if texto_limpio:
            texto_limpio_completo += texto_limpio + " "  # Agregar espacio para evitar que las frases se unan
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

# Inicializar el estado de la sesión para almacenar el texto procesado
if 'texto_procesado' not in st.session_state:
    st.session_state['texto_procesado'] = ""

# Botón para procesar el texto
if st.button("Procesar Texto"):
    if transcripcion:
        # Antes de procesar, muestra la longitud del texto original
        longitud_original = contar_tokens(transcripcion)
        st.info(f"Longitud del texto original: {longitud_original} tokens.")

        with st.spinner("Procesando con Gemini..."):
            texto_limpio = procesar_transcripcion(transcripcion)
            if texto_limpio:
                st.session_state['texto_procesado'] = texto_limpio  # Guardar el texto procesado en el estado de la sesión
                st.success("¡Texto procesado!")

                # Después de procesar, muestra la longitud del texto resultante
                longitud_resultante = contar_tokens(texto_limpio)
                st.info(f"Longitud del texto resultante: {longitud_resultante} tokens.")


    else:
        st.warning("Por favor, introduce el texto a procesar.")

# Mostrar el texto procesado y el botón de descarga solo si hay texto procesado
if st.session_state['texto_procesado']:
    st.subheader("Transcripción Formateada:")
    st.write(st.session_state['texto_procesado'])
    descargar_texto(st.session_state['texto_procesado'])
