"""
Recording page - Browser-based audio recording
"""

import streamlit as st
from datetime import datetime
from src.ui.components.audio_recorder import show_audio_recorder, show_manual_upload
from src.services.audio_service import audio_service
from src.services.case_service import case_service


def show():
    """Display recording page"""
    
    st.title("🎙️ New Recording")
    st.markdown("Record a case interaction directly in your browser")
    
    st.markdown("---")
    
    # Two-column layout
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Case information form
        st.subheader("📋 Case Information")
        
        with st.form("recording_form"):
            case_reference = st.text_input(
                "Case Reference ID *",
                placeholder="e.g., CASE-2025-001",
                help="Enter the case reference number. If it exists, the recording will be added to that case."
            )
            
            client_initials = st.text_input(
                "Client Initials *",
                max_chars=10,
                placeholder="e.g., JD",
                help="Enter client's initials (e.g., John Doe = JD)"
            )
            
            recording_type = st.selectbox(
                "Recording Type *",
                ["phone", "home_visit", "office"],
                format_func=lambda x: {
                    "phone": "📞 Phone Call",
                    "home_visit": "🏠 Home Visit", 
                    "office": "🏢 Office Meeting"
                }[x]
            )
            
            recording_date = st.date_input(
                "Recording Date *",
                value=datetime.now(),
                help="Date of the interaction"
            )
            
            additional_notes = st.text_area(
                "Additional Notes (Optional)",
                placeholder="Any additional context or notes...",
                height=100
            )
            
            tags = st.text_input(
                "Tags (Optional)",
                placeholder="e.g., urgent, follow-up, assessment",
                help="Comma-separated tags"
            )
            
            # Form submission flag
            submitted = st.form_submit_button("✅ Save Recording Information", use_container_width=True)
            
            if submitted:
                if not case_reference or not client_initials:
                    st.error("⚠️ Please fill in all required fields (Case Reference and Client Initials)")
                else:
                    # Store form data in session state
                    st.session_state.recording_metadata = {
                        'case_reference': case_reference,
                        'client_initials': client_initials,
                        'recording_type': recording_type,
                        'recording_date': recording_date,
                        'additional_notes': additional_notes,
                        'tags': tags
                    }
                    st.success("✅ Recording information saved! Now record or upload audio below.")
    
    with col2:
        # Instructions
        st.info("""
        **📝 Instructions:**
        
        1. Fill in case information
        2. Click "Save Recording Information"
        3. Record audio or upload file
        4. Your recording will be automatically transcribed!
        """)
    
    st.markdown("---")
    
    # Audio recording section
    st.subheader("🎤 Audio Recording")
    
    # Check if metadata is saved
    if 'recording_metadata' not in st.session_state:
        st.warning("⚠️ Please fill in and save the case information above before recording.")
        return
    
    # Show metadata summary
    metadata = st.session_state.recording_metadata
    with st.expander("📋 Current Recording Details", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**Case Reference:** {metadata['case_reference']}")
            st.write(f"**Client Initials:** {metadata['client_initials']}")
        with col2:
            st.write(f"**Type:** {metadata['recording_type'].replace('_', ' ').title()}")
            st.write(f"**Date:** {metadata['recording_date'].strftime('%Y-%m-%d')}")
    
    st.markdown("---")
    
    # Tab for recording vs upload
    tab1, tab2 = st.tabs(["🎙️ Record Now", "📁 Upload File"])
    
    with tab1:
        st.markdown("### Record Audio")
        st.markdown("Click the button below to start recording. Click again to stop.")
        
        # Audio recorder (returns audio bytes directly)
        audio_value = show_audio_recorder()
        
        if audio_value is not None:
            st.success("✅ Recording captured!")
            
            # Show audio player
            st.audio(audio_value)
            
            # Save button
            if st.button("💾 Save and Process Recording", type="primary", use_container_width=True):
                save_recording(audio_value, None)
    
    with tab2:
        st.markdown("### Upload Audio File")
        st.markdown("*Use this if browser recording doesn't work*")
        
        audio_bytes, filename = show_manual_upload()
        
        if audio_bytes:
            st.success(f"✅ File uploaded: {filename}")
            
            # Show audio player
            st.audio(audio_bytes)
            
            # Save button
            if st.button("💾 Save and Process Recording", type="primary", use_container_width=True, key="upload_save"):
                save_recording(audio_bytes, filename)


def save_recording(audio_value, filename: str = None):
    """
    Save recording to database and file system
    
    Args:
        audio_value: Audio data (can be bytes or file-like object)
        filename: Optional filename for uploaded files
    """
    
    metadata = st.session_state.recording_metadata
    
    with st.spinner("💾 Saving recording..."):
        try:
            # Convert audio to bytes if it's not already
            if hasattr(audio_value, 'read'):
                # It's a file-like object
                audio_bytes = audio_value.read()
                if hasattr(audio_value, 'seek'):
                    audio_value.seek(0)  # Reset for audio player
            elif hasattr(audio_value, 'getvalue'):
                # It's a BytesIO object
                audio_bytes = audio_value.getvalue()
            else:
                # Assume it's already bytes
                audio_bytes = audio_value
            
            # Validate we have bytes
            if not isinstance(audio_bytes, bytes):
                st.error(f"❌ Invalid audio data type: {type(audio_bytes)}")
                return
            
            # Get or create case (returns dict)
            case = case_service.get_or_create_case(
                case_reference_id=metadata['case_reference'],
                client_initials=metadata['client_initials'],
                user_id=st.session_state.user_id
            )
            
            # Save audio file
            audio_info = audio_service.save_audio(
                audio_bytes=audio_bytes,
                case_id=case['case_id'],  # Access dict key
                user_id=st.session_state.user_id
            )
            
            # Create recording entry
            recording_data = {
                'recording_date': datetime.combine(metadata['recording_date'], datetime.min.time()),
                'recording_type': metadata['recording_type'],
                'file_path': audio_info['file_path'],
                'file_size': audio_info['file_size'],
                'duration_seconds': audio_info['duration_seconds'],
                'additional_notes': metadata['additional_notes'],
                'tags': metadata['tags']
            }
            
            recording = case_service.create_recording(
                case_id=case['case_id'],  # Access dict key
                user_id=st.session_state.user_id,
                recording_data=recording_data
            )
            
            st.success(f"""
            ✅ **Recording saved successfully!**
            
            - Case: {metadata['case_reference']}
            - Recording ID: {recording['recording_id']}
            - Duration: {audio_info['duration_seconds']:.1f} seconds
            - Status: Pending transcription
            """)
            
            # Clear session state
            del st.session_state.recording_metadata
            
            # Show next steps
            st.info("""
            **Next Steps:**
            - Your recording is queued for transcription
            - Check the "Cases" page to view progress
            - Transcription typically takes 2x the recording duration
            """)
            
            # Button to view cases
            if st.button("📝 View My Cases", use_container_width=True, key="goto_cases"):
                st.query_params.clear()
                st.rerun()
            
        except Exception as e:
            st.error(f"❌ Error saving recording: {str(e)}")
            import traceback
            st.code(traceback.format_exc())