"""
Case detail page - View individual case with recordings, transcripts, and summaries
"""

import streamlit as st
from src.services.case_service import case_service
from src.services.audio_service import audio_service
from src.services.transcription_service import transcription_service
from src.services.summarization_service import summarization_service


def show():
    """Display case detail page"""
    
    # Check if case is selected
    if 'selected_case_id' not in st.session_state:
        st.warning("⚠️ No case selected. Please select a case from the Cases page.")
        if st.button("📝 Go to Cases"):
            st.session_state.current_page = 'cases'
            st.rerun()
        return
    
    case_id = st.session_state.selected_case_id
    
    # Fetch case details
    case = case_service.get_case_by_id(case_id)
    
    if not case:
        st.error("❌ Case not found")
        return
    
    # Header
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.title(f"📁 {case.case_reference_id}")
        st.markdown(f"**Client:** {case.client_initials}")
        st.markdown(f"*Created: {case.created_at.strftime('%Y-%m-%d')} | Last updated: {case.last_updated.strftime('%Y-%m-%d %H:%M')}*")
    
    with col2:
        if st.button("← Back to Cases", use_container_width=True):
            # Clear query params to go back to cases
            st.query_params.clear()
            st.rerun()
    
    st.markdown("---")
    
    # Fetch recordings
    recordings = case_service.get_recordings_by_case(case_id)
    
    if not recordings:
        st.info("📭 No recordings for this case yet.")
        if st.button("🎙️ Add Recording", type="primary"):
            st.session_state.current_page = 'record'
            st.rerun()
        return
    
    # Display recordings count
    st.subheader(f"🎙️ Recordings ({len(recordings)})")
    
    # Recordings list
    for idx, recording in enumerate(recordings, 1):
        with st.expander(
            f"Recording {idx} - {recording.recording_type.replace('_', ' ').title()} - "
            f"{recording.recording_date.strftime('%Y-%m-%d')} - "
            f"Status: {recording.transcription_status.upper()}",
            expanded=(idx == 1)  # Expand first recording by default
        ):
            show_recording_detail(recording)


def show_recording_detail(recording):
    """
    Display detailed view of a single recording
    
    Args:
        recording: Recording object
    """
    
    # Recording metadata
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Duration", f"{recording.duration_seconds:.1f}s" if recording.duration_seconds else "N/A")
    
    with col2:
        st.metric("Type", recording.recording_type.replace('_', ' ').title())
    
    with col3:
        status_color = {
            'pending': '🟡',
            'processing': '🔵',
            'completed': '🟢',
            'failed': '🔴'
        }
        st.metric("Status", f"{status_color.get(recording.transcription_status, '⚪')} {recording.transcription_status.title()}")
    
    st.markdown("---")
    
    # Tabs for different views
    tab1, tab2, tab3, tab4 = st.tabs(["🎵 Audio", "📝 Transcript", "📄 Summary", "⚙️ Actions"])
    
    with tab1:
        show_audio_player(recording)
    
    with tab2:
        show_transcript(recording)
    
    with tab3:
        show_summary(recording)
    
    with tab4:
        show_actions(recording)


def show_audio_player(recording):
    """Display audio player"""
    
    st.markdown("### 🎵 Audio Player")
    
    try:
        # Load audio
        audio_bytes = audio_service.load_audio(recording.file_path)
        
        # Display audio player
        st.audio(audio_bytes)
        
        # Metadata
        if recording.additional_notes:
            st.markdown("**Notes:**")
            st.info(recording.additional_notes)
        
        if recording.tags:
            st.markdown("**Tags:**")
            st.write(recording.tags)
    
    except Exception as e:
        st.error(f"❌ Error loading audio: {str(e)}")


def show_transcript(recording):
    """Display transcript with option to generate if pending"""
    
    st.markdown("### 📝 Transcript")
    
    if recording.transcription_status == 'completed' and recording.transcript_text:
        # Display transcript
        st.markdown("---")
        st.markdown(recording.transcript_text)
        
        # Download option
        st.download_button(
            label="📥 Download Transcript",
            data=recording.transcript_text,
            file_name=f"transcript_{recording.recording_id}.txt",
            mime="text/plain",
            key=f"download_transcript_{recording.recording_id}"
        )
    
    elif recording.transcription_status == 'pending':
        st.warning("⏳ Transcription pending. Click below to start transcription.")
        
        if st.button("🚀 Start Transcription Now", type="primary", use_container_width=True, key=f"start_transcribe_{recording.recording_id}"):
            with st.spinner("🔄 Transcribing audio... This may take a few minutes."):
                result = transcription_service.transcribe_recording(
                    recording.recording_id,
                    recording.file_path
                )
                
                if result['success']:
                    st.success(f"✅ Transcription completed! ({result['word_count']} words)")
                    st.rerun()
                else:
                    st.error(f"❌ Transcription failed: {result['error']}")
    
    elif recording.transcription_status == 'processing':
        st.info("🔄 Transcription in progress... Please wait.")
        if st.button("🔄 Refresh", key=f"refresh_transcript_{recording.recording_id}"):
            st.rerun()
    
    elif recording.transcription_status == 'failed':
        st.error("❌ Transcription failed.")
        
        if st.button("🔁 Retry Transcription", use_container_width=True, key=f"retry_transcribe_{recording.recording_id}"):
            with st.spinner("🔄 Retrying transcription..."):
                result = transcription_service.transcribe_recording(
                    recording.recording_id,
                    recording.file_path
                )
                
                if result['success']:
                    st.success("✅ Transcription completed!")
                    st.rerun()
                else:
                    st.error(f"❌ Failed again: {result['error']}")


def show_summary(recording):
    """Display AI-generated summary with option to generate/regenerate"""
    
    st.markdown("### 📄 Case Note Summary")
    
    if recording.summary_text:
        # Display summary
        st.markdown("---")
        st.markdown(recording.summary_text)
        
        st.markdown("---")
        
        # Regenerate option
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔄 Regenerate Summary", use_container_width=True, key=f"regen_summary_{recording.recording_id}"):
                if recording.transcript_text:
                    with st.spinner("🔄 Generating new summary..."):
                        result = summarization_service.generate_summary(
                            recording.recording_id,
                            recording.transcript_text,
                            recording.recording_type
                        )
                        
                        if result['success']:
                            st.success("✅ Summary regenerated!")
                            st.rerun()
                        else:
                            st.error(f"❌ Failed: {result['error']}")
                else:
                    st.warning("⚠️ Transcript needed first. Please transcribe the audio.")
        
        with col2:
            st.download_button(
                label="📥 Download Summary",
                data=recording.summary_text,
                file_name=f"summary_{recording.recording_id}.txt",
                mime="text/plain",
                use_container_width=True,
                key=f"download_summary_{recording.recording_id}"
            )
    
    elif recording.transcript_text:
        # Transcript available but no summary
        st.info("📝 Transcript available. Generate case note summary?")
        
        if st.button("🚀 Generate Summary Now", type="primary", use_container_width=True, key=f"gen_summary_{recording.recording_id}"):
            with st.spinner("🤖 AI is generating your case note summary..."):
                result = summarization_service.generate_summary(
                    recording.recording_id,
                    recording.transcript_text,
                    recording.recording_type
                )
                
                if result['success']:
                    st.success(f"✅ Summary generated! (Used {result['tokens_used']} tokens)")
                    st.rerun()
                else:
                    st.error(f"❌ Failed: {result['error']}")
    
    else:
        st.warning("⚠️ Transcript needed first. Please transcribe the audio before generating summary.")


def show_actions(recording):
    """Display available actions for the recording"""
    
    st.markdown("### ⚙️ Actions")
    
    # Process All button
    if recording.transcription_status == 'pending':
        st.markdown("#### 🚀 Quick Process")
        st.info("Transcribe audio and generate summary in one click!")
        
        if st.button("⚡ Transcribe & Summarize", type="primary", use_container_width=True, key=f"process_all_{recording.recording_id}"):
            process_recording_full(recording)
    
    # Manual actions
    st.markdown("#### Manual Actions")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if recording.transcription_status in ['pending', 'failed']:
            if st.button("🎯 Transcribe Only", use_container_width=True, key=f"transcribe_only_{recording.recording_id}"):
                with st.spinner("🔄 Transcribing..."):
                    result = transcription_service.transcribe_recording(
                        recording.recording_id,
                        recording.file_path
                    )
                    
                    if result['success']:
                        st.success("✅ Done!")
                        st.rerun()
                    else:
                        st.error(f"❌ Failed: {result['error']}")
    
    with col2:
        if recording.transcript_text and not recording.summary_text:
            if st.button("📝 Summarize Only", use_container_width=True, key=f"summarize_only_{recording.recording_id}"):
                with st.spinner("🔄 Summarizing..."):
                    result = summarization_service.generate_summary(
                        recording.recording_id,
                        recording.transcript_text,
                        recording.recording_type
                    )
                    
                    if result['success']:
                        st.success("✅ Done!")
                        st.rerun()
                    else:
                        st.error(f"❌ Failed: {result['error']}")
    
    # Edit summary (if exists)
    if recording.summary_text:
        st.markdown("---")
        st.markdown("#### ✏️ Edit Summary")
        
        edited_summary = st.text_area(
            "Edit the summary below:",
            value=recording.summary_text,
            height=300,
            key=f"edit_summary_{recording.recording_id}"
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("💾 Save Changes", use_container_width=True, key=f"save_summary_{recording.recording_id}"):
                case_service.update_recording_summary(recording.recording_id, edited_summary)
                st.success("✅ Summary updated!")
                st.rerun()
        
        with col2:
            if st.button("↩️ Reset", use_container_width=True, key=f"reset_summary_{recording.recording_id}"):
                st.rerun()


def process_recording_full(recording):
    """
    Process recording completely: transcribe and summarize
    
    Args:
        recording: Recording object
    """
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    # Step 1: Transcribe
    status_text.text("🔄 Step 1/2: Transcribing audio...")
    progress_bar.progress(25)
    
    result = transcription_service.transcribe_recording(
        recording.recording_id,
        recording.file_path
    )
    
    if not result['success']:
        st.error(f"❌ Transcription failed: {result['error']}")
        return
    
    progress_bar.progress(50)
    status_text.text("✅ Step 1/2: Transcription complete!")
    
    # Step 2: Summarize
    status_text.text("🔄 Step 2/2: Generating case note summary...")
    progress_bar.progress(75)
    
    summary_result = summarization_service.generate_summary(
        recording.recording_id,
        result['transcript'],
        recording.recording_type
    )
    
    if not summary_result['success']:
        st.error(f"❌ Summarization failed: {summary_result['error']}")
        return
    
    progress_bar.progress(100)
    status_text.text("✅ Step 2/2: Summary generated!")
    
    st.success(f"""
    🎉 **Processing Complete!**
    
    - Transcript: {result['word_count']} words
    - Summary: Generated
    - Tokens used: {summary_result['tokens_used']}
    """)
    
    st.balloons()
    
    # Refresh page
    import time
    time.sleep(2)
    st.rerun()