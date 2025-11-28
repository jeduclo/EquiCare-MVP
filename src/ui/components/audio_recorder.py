"""
Audio recorder component
Provides browser-based audio recording functionality using Streamlit's native audio_input
"""

import streamlit as st


def show_audio_recorder():
    """
    Display audio recorder widget and return recorded audio bytes
    Uses Streamlit's native audio_input (available in Streamlit 1.28+)
    
    Returns:
        bytes: Audio data if recorded, None otherwise
    """
    
    st.markdown("""
        <style>
        /* Center the audio recorder */
        .stAudioInput {
            display: flex;
            justify-content: center;
            margin: 20px 0;
        }
        </style>
    """, unsafe_allow_html=True)
    
    st.markdown("### 🎤 Click to Record")
    
    # Native Streamlit audio input (works in browser)
    audio_bytes = st.audio_input("Record your audio", label_visibility="collapsed")
    
    return audio_bytes


def show_manual_upload():
    """
    Display manual file upload as fallback option
    
    Returns:
        tuple: (audio_bytes, filename) if uploaded, (None, None) otherwise
    """
    
    st.markdown("### Or Upload an Audio File")
    st.markdown("*If browser recording doesn't work, you can upload a pre-recorded file*")
    
    uploaded_file = st.file_uploader(
        "Choose an audio file",
        type=['mp3', 'm4a', 'wav', 'aac', 'ogg', 'webm'],
        help="Supported formats: MP3, M4A, WAV, AAC, OGG, WebM"
    )
    
    if uploaded_file is not None:
        audio_bytes = uploaded_file.read()
        return audio_bytes, uploaded_file.name
    
    return None, None