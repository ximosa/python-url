import streamlit as st
import subprocess
import json
from io import BytesIO
import base64

def search_most_popular_music(limit=5):
    """Busca la música más popular en YouTube usando yt-dlp."""
    try:
        # Ejecuta yt-dlp para buscar videos
        command = [
            "yt-dlp",
            "--dump-json",
            "--skip-download",
            f"ytsearch{limit}:top music"  # Término de búsqueda
        ]
        result = subprocess.run(command, capture_output=True, text=True, check=False) #check=False
        output = result.stdout
        stderr = result.stderr
        
        #Procesa la salida
        videos = []
        for line in output.strip().split("\n"):
            try:
                video_data = json.loads(line)
                videos.append(video_data)
            except json.JSONDecodeError:
                st.error(f"Error al decodificar json: {line}")
        
        #Filtrar videos que dieron error
        filtered_videos = []
        for video in videos:
            if f"Video unavailable. The uploader has not made this video available" in stderr:
                if not stderr.find(video.get("id")) == -1:
                     st.warning(f"El video {video.get('title')} no está disponible en tu pais")
            else:
                filtered_videos.append(video)
        return filtered_videos

    except subprocess.CalledProcessError as e:
        st.error(f"Error al buscar en YouTube con yt-dlp: {e.stderr}")
        return []
    except Exception as e:
        st.error(f"Error inesperado al buscar en YouTube: {e}")
        return []

def get_audio_link(video_url):
    """Obtiene el link de audio de un video de YouTube usando yt-dlp."""
    try:
        command = [
            "yt-dlp",
            "--dump-json",
            "--skip-download",
            "--format", "bestaudio[ext=mp4]",
            video_url
        ]
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        video_data = json.loads(result.stdout)
        
        audio_url = video_data.get("url")
        title = video_data.get("title")
        return audio_url, title
    
    except subprocess.CalledProcessError as e:
        st.error(f"Error al obtener audio de {video_url} con yt-dlp: {e.stderr}")
        return None, None
    except json.JSONDecodeError:
         st.error(f"Error al decodificar json {video_url} con yt-dlp.")
         return None, None
    except Exception as e:
        st.error(f"Error inesperado al obtener audio de {video_url}: {e}")
        return None, None
    
def create_download_link(audio_url, filename):
    """Crea un link de descarga para el audio."""
    try:
        command = [
            "yt-dlp",
            "--print",
            "url",
             "--format", "bestaudio[ext=mp4]",
            audio_url
        ]
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        audio_url= result.stdout.strip()
        
        command = [
             "yt-dlp",
            "--print",
            "url",
            "--format", "bestaudio[ext=mp4]",
            audio_url
        ]
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        audio_url_final = result.stdout.strip()

        command = [
              "yt-dlp",
              "--print",
              "url",
             "--format", "bestaudio[ext=mp4]",
             audio_url_final
        ]
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        
        command = [
            "yt-dlp",
            "--format", "bestaudio[ext=mp4]",
            "-o", "-", #Imprime la descarga en stdout
           audio_url_final
        ]

        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()

        if process.returncode != 0:
            raise Exception(f"yt-dlp download failed with error: {stderr.decode('utf-8')}")
            return None

        buffer = BytesIO(stdout)
        b64 = base64.b64encode(buffer.read()).decode()
        href = f'<a href="data:audio/mp4;base64,{b64}" download="{filename}.mp4">Descargar</a>'
        return href
    except subprocess.CalledProcessError as e:
            st.error(f"Error al crear link de descarga: {e.stderr}")
            return None
    except Exception as e:
        st.error(f"Error al crear link de descarga: {e}")
        return None

def play_audio_sequence(audio_urls):
    """Reproduce una secuencia de audios."""
    if not audio_urls:
        st.warning("No hay URLs de audio para reproducir.")
        return

    for audio_url in audio_urls:
        try:
            st.audio(audio_url)
        except Exception as e:
             st.error(f"Error al reproducir {audio_url}: {e}")
    st.success("Reproducción completada.")

def main():
    st.title("Música Popular de YouTube")
    
    limit = st.number_input("Número de resultados:", min_value=1, max_value=10, value=5)
    
    search_results = search_most_popular_music(limit)

    if not search_results:
        st.warning("No se encontraron resultados. Inténtalo de nuevo.")
        return

    audio_links_data = []
    for video in search_results:
        video_url = f"https://www.youtube.com/watch?v={video['id']}"
        try:
            audio_url, title = get_audio_link(video_url)
            if audio_url:
                audio_links_data.append({"title":title, "audio_url":audio_url})
            else:
              st.warning(f"No se pudo obtener el audio de: {video_url}")
        except Exception as e:
            st.error(f"Error inesperado al procesar {video_url}: {e}")

    if not audio_links_data:
        st.warning("No se encontraron URLs de audio. Inténtalo de nuevo.")
        return

    st.subheader("Lista de Música")
    audio_urls = []
    for item in audio_links_data:
        audio_url = item["audio_url"]
        title = item["title"]
        
        col1, col2, col3 = st.columns(3)

        with col1:
            st.write(title)
        with col2:
            if audio_url:
                st.audio(audio_url, format="audio/mp4")
        with col3:
           if audio_url:
                download_link = create_download_link(audio_url, title)
                if download_link:
                   st.markdown(download_link, unsafe_allow_html=True)
        audio_urls.append(audio_url)

    if audio_urls:
            if st.button("Reproducir Todos"):
                play_audio_sequence(audio_urls)
                
if __name__ == "__main__":
    main()
