import streamlit as st
import os
from moviepy.editor import ImageSequenceClip, AudioFileClip
from bs4 import BeautifulSoup
import requests
import spacy
from gtts import gTTS
from transformers import pipeline
from PIL import Image, ImageDraw, ImageFont

nlp = spacy.load("es_core_news_sm")
resumidor = pipeline("summarization")

# Funciones mejoradas (ver las funciones de los ejemplos anteriores, pero con mejor manejo de errores)

def texto_a_voz_mejorado(texto, ruta_audio, idioma="es", velocidad=1.0, tono=0.0):
    try:
        tts = gTTS(text=texto, lang=idioma)
        tts.save(ruta_audio)
        return True, None
    except Exception as e:
        return False, str(e)

def crear_fotogramas_mejorado(textos, rutas_imagenes, carpeta_fotogramas):
  try:
    imagenes_generadas = []
    for i, texto in enumerate(textos):
        img = Image.new('RGB', (800, 600), color=(255, 255, 255))
        d = ImageDraw.Draw(img)
        font = ImageFont.truetype('arial.ttf', size=30) # Ajusta la fuente
        
        d.text((50, 50), texto, fill=(0, 0, 0), font=font)
        if i < len(rutas_imagenes):
            try:
              imagen_web = Image.open(rutas_imagenes[i])
              imagen_web.thumbnail((200,200))
              img.paste(imagen_web, (400, 200))
            except:
              pass # Si no se puede, no pasa nada

        nombre_archivo = f"frame_{i:04d}.png"
        ruta_archivo = os.path.join(carpeta_fotogramas, nombre_archivo)
        img.save(ruta_archivo)
        imagenes_generadas.append(ruta_archivo)
    return True, imagenes_generadas
  except Exception as e:
      return False, str(e)

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
                      textos_resumen.append(item["texto"]) # si no se puede resumir lo dejamos igual
                else:
                    textos_resumen.append(item["texto"]) # añadimos el encabezado

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
