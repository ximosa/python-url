import streamlit as st
from pytube import Search, YouTube
from io import BytesIO
import base64

def search_most_popular_music(limit=5):
    """Busca la música más popular en YouTube."""
    try:
        s = Search("top music")
        results = s.results[:limit]
        return results
    except Exception as e:
        st.error(f"Error al buscar en YouTube: {e}")
        return []

def get_audio_link(video_url):
    """Obtiene el link de audio de un video de YouTube."""
    try:
        yt = YouTube(video_url)
        # Primero intentar obtener el stream con mejor calidad
        audio_stream = yt.streams.filter(only_audio=True, file_extension="mp4").order_by('abr').desc().first()
        if audio_stream:
             return audio_stream.url, yt.title
        # Si no se encuentra un stream de alta calidad, buscar cualquiera
        audio_stream = yt.streams.filter(only_audio=True).first()
        if audio_stream:
            return audio_stream.url, yt.title
        else:
             st.error(f"No se encontró stream de audio para {video_url}")
             return None, None
    except Exception as e:
        st.error(f"Error al obtener el audio de {video_url}: {e}")
        return None, None

def create_download_link(audio_url, filename):
    """Crea un link de descarga para el audio."""
    try:
        yt = YouTube(audio_url)
        audio_stream = yt.streams.filter(only_audio=True).first()
        buffer = BytesIO()
        audio_stream.stream_to_buffer(buffer)
        buffer.seek(0)
        b64 = base64.b64encode(buffer.read()).decode()
        href = f'<a href="data:audio/mp4;base64,{b64}" download="{filename}.mp4">Descargar</a>'
        return href
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
       audio_url, title= get_audio_link(f"https://www.youtube.com/watch?v={video.video_id}")
       if audio_url:
          audio_links_data.append({"title":title, "audio_url":audio_url})
       else:
           st.warning(f"No se pudo obtener el audio de: https://www.youtube.com/watch?v={video.video_id}")


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
