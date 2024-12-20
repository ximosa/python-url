```python
import streamlit as st
import os
from moviepy.editor import ImageSequenceClip, AudioFileClip
from bs4 import BeautifulSoup
import requests
import spacy
from gtts import gTTS
# from transformers import pipeline # Comentado para evitar conflictos
from PIL import Image, ImageDraw, ImageFont
import time
import subprocess
import numpy as np

# --- Configuración de spaCy ---
MODEL_NAME = "es_core_news_sm"
MODEL_INSTALLED = False

EXPECTED_NUMPY_VERSION = "1.23.4" # Variable para verificar versión de numpy

if np.__version__ != EXPECTED_NUMPY_VERSION:
    st.error(f"¡Error! La versión de numpy no es la esperada. Streamlit Cloud tiene la versión {np.__version__}, se esperaba la versión {EXPECTED_NUMPY_VERSION}. Por favor, contacta a soporte o vuelve a intentar desplegar más tarde.")
    st.stop()  # Detener la ejecución si la versión no es la correcta.
    
def descargar_modelo_spacy(model_name):
    """Descarga el modelo de spaCy si no está instalado."""
    try:
        import spacy
        spacy.load(model_name)
        return True
    except OSError:
        st.info(f"Descargando modelo de spaCy '{model_name}'...")
        try:
            subprocess.check_call(["python", "-m", "spacy", "download", model_name])
            return True
        except Exception as e:
            st.error(f"Error al descargar el modelo: {e}")
            return False
    except Exception as e:
        st.error(f"Error desconocido al cargar o descargar el modelo: {e}")
        return False

if not MODEL_INSTALLED:
    MODEL_INSTALLED = descargar_modelo_spacy(MODEL_NAME)

if MODEL_INSTALLED:
    try:
        nlp = spacy.load(MODEL_NAME)
        st.write("Modelo de spaCy cargado correctamente.")
    except Exception as e:
        st.error(f"Error al cargar el modelo de spaCy: {e}")
        nlp = None
else:
    nlp = None
    st.write("Error en el proceso.")

# --- Funciones ---
def obtener_contenido_web_mejorado(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        titulo = soup.title.string if soup.title else "Sin título"
        elementos_texto = soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
        textos_estructurados = []

        for elemento in elementos_texto:
            text = elemento.get_text(strip=True)
            if text:
                tipo_elemento = elemento.name
                textos_estructurados.append({"tipo": tipo_elemento, "texto": text})
        imagenes = [img['src'] for img in soup.find_all('img') if 'src' in img.attrs]
        if nlp:
            docs = [nlp(item["texto"]) for item in textos_estructurados]
        else:
           docs = []
        return True, {
            "titulo": titulo,
            "textos_estructurados": textos_estructurados,
            "documentos": docs,
            "imagenes": imagenes
        }
    except requests.exceptions.RequestException as e:
        return False, str(e)
    except Exception as e:
        return False, str(e)

def descargar_imagenes(lista_urls, carpeta_destino):
    try:
        imagenes_descargadas = []
        for i, url in enumerate(lista_urls):
            if not url.startswith("http"):
                continue
            try:
                response = requests.get(url, stream=True)
                response.raise_for_status()
                extension = os.path.splitext(url)[1]
                nombre_archivo = f"imagen_{i}{extension}"
                ruta_archivo = os.path.join(carpeta_destino, nombre_archivo)
                with open(ruta_archivo, 'wb') as archivo:
                    for chunk in response.iter_content(chunk_size=8192):
                        archivo.write(chunk)
                imagenes_descargadas.append(ruta_archivo)
        except requests.exceptions.RequestException as e:
            print(f"Error al descargar imagen {url}: {e}")
        return True, imagenes_descargadas
    except Exception as e:
        return False, str(e)

def texto_a_voz_mejorado(texto, ruta_audio, idioma="es", velocidad=1.0, tono=0.0):
    try:
        tts = gTTS(text=texto, lang=idioma)
        tts.save(ruta_audio)
        return True, None
    except Exception as e:
        return False, str(e)

# resumidor = pipeline("summarization") # Eliminado para evitar problemas con torch
def resumir_texto(texto, longitud_maxima=150):
  return True, texto
    # try:
    #  resumen = resumidor(texto, max_length=longitud_maxima, min_length=30)[0]['summary_text']
    #  return True, resumen
    # except Exception as e:
    #  return False, str(e)

def crear_fotogramas_mejorado(textos, rutas_imagenes, carpeta_fotogramas):
    try:
        imagenes_generadas = []
        for i, texto in enumerate(textos):
            img = Image.new('RGB', (800, 600), color=(255, 255, 255))
            d = ImageDraw.Draw(img)
            font = ImageFont.truetype('arial.ttf', size=30)

            d.text((50, 50), texto, fill=(0, 0, 0), font=font)

            if i < len(rutas_imagenes):
                try:
                    imagen_web = Image.open(rutas_imagenes[i])
                    imagen_web.thumbnail((200,200))
                    img.paste(imagen_web, (400, 200))
                except:
                    pass # si no se puede, no pasa nada

            nombre_archivo = f"frame_{i:04d}.png"
            ruta_archivo = os.path.join(carpeta_fotogramas, nombre_archivo)
            img.save(ruta_archivo)
            imagenes_generadas.append(ruta_archivo)
        return True, imagenes_generadas
    except Exception as e:
        return False, str(e)

def reconstruir_video(ruta_fotogramas, ruta_audio, ruta_video_salida, fps=2):
    try:
        image_files = [os.path.join(ruta_fotogramas, img) for img in os.listdir(ruta_fotogramas) if img.endswith((".jpg", ".png"))]
        image_files.sort()
        clip = ImageSequenceClip(image_files, fps=fps)
        audio = AudioFileClip(ruta_audio)
        clip_con_audio = clip.set_audio(audio)
        clip_con_audio.write_videofile(ruta_video_salida, codec="libx264")
        return True, None
    except Exception as e:
        return False, str(e)

# --- Interfaz de Streamlit ---
def main():
    st.title("Generador de Videos Inteligente")
    url = st.text_input("Ingresa la URL de la página web:")

    if url:
        if st.button("Generar Video"):
            ruta_carpeta_temporal = "temporal"
            ruta_imagenes_web = os.path.join(ruta_carpeta_temporal, "imagenes_web")
            ruta_audio = os.path.join(ruta_carpeta_temporal, "audio.mp3")
            ruta_fotogramas = os.path.join(ruta_carpeta_temporal, "fotogramas")
            ruta_video_salida = os.path.join(ruta_carpeta_temporal, "video_final.mp4")

            if not os.path.exists(ruta_carpeta_temporal):
                os.makedirs(ruta_carpeta_temporal)
            if not os.path.exists(ruta_imagenes_web):
                os.makedirs(ruta_imagenes_web)
            if not os.path.exists(ruta_fotogramas):
                os.makedirs(ruta_fotogramas)

            st.info("Obteniendo contenido de la web...")
            exito, contenido = obtener_contenido_web_mejorado(url)
            if exito:
                st.success("Contenido web obtenido.")
            else:
                st.error(f"Error al obtener contenido web: {contenido}")
                return

            st.info("Descargando imagenes...")
            exito, rutas_imagenes = descargar_imagenes(contenido["imagenes"], ruta_imagenes_web)
            if exito:
                st.success("Imagenes descargadas.")
            else:
                st.error(f"Error descargando imágenes: {rutas_imagenes}")
                return

            st.info("Resumiendo texto...")
            textos_resumen = []
            for item in contenido["textos_estructurados"]:
                if item["tipo"] == "p":
                    exito_resumen, resumen = resumir_texto(item["texto"])
                    if exito_resumen:
                        textos_resumen.append(resumen)
                    else:
                        textos_resumen.append(item["texto"])
                else:
                    textos_resumen.append(item["texto"])
            st.info("Creando audio a partir del texto...")
            texto_completo = " ".join(textos_resumen)
            exito_audio, error_audio = texto_a_voz_mejorado(texto_completo, ruta_audio)
            if exito_audio:
               st.success("Audio creado.")
            else:
               st.error(f"Error creando audio: {error_audio}")
               return

            st.info("Creando fotogramas...")
            exito_fotogramas, error_fotogramas = crear_fotogramas_mejorado(textos_resumen, rutas_imagenes, ruta_fotogramas)
            if exito_fotogramas:
                st.success("Fotogramas creados.")
            else:
                st.error(f"Error creando fotogramas: {error_fotogramas}")
                return

            st.info("Reconstruyendo video...")
            exito_reconstruir, error_reconstruir = reconstruir_video(ruta_fotogramas, ruta_audio, ruta_video_salida)
            if exito_reconstruir:
                st.success("Video creado!")
                with open(ruta_video_salida, "rb") as file:
                    btn = st.download_button(
                        label="Descargar Video",
                        data=file,
                        file_name="video_web.mp4",
                        mime="video/mp4"
                    )
            else:
                st.error(f"Error reconstruyendo video: {error_reconstruir}")

if __name__ == "__main__":
    main()
```
