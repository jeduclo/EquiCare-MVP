"""
Home/Dashboard page
"""

import streamlit as st
from src.services.case_service import case_service
from src.database.db_manager import get_db_session
from src.database.models import Recording
from datetime import datetime, timedelta


def show():
    """Display home page"""
    
    st.title("🏠 Dashboard")
    st.markdown(f"Welcome back, **{st.session_state.full_name}**!")
    
    st.markdown("---")
    
    # Get real statistics
    cases = case_service.get_cases_by_user(st.session_state.user_id, limit=1000)
    
    with get_db_session() as session:
        # Total recordings by this user
        total_recordings = session.query(Recording).filter_by(
            uploaded_by=st.session_state.user_id
        ).count()
        
        # Pending transcriptions
        pending = session.query(Recording).filter_by(
            uploaded_by=st.session_state.user_id,
            transcription_status='pending'
        ).count()
        
        # This week's recordings
        week_ago = datetime.utcnow() - timedelta(days=7)
        this_week = session.query(Recording).filter(
            Recording.uploaded_by == st.session_state.user_id,
            Recording.created_at >= week_ago
        ).count()
    
    # Quick stats
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Cases", len(cases))
    
    with col2:
        st.metric("Recordings", total_recordings)
    
    with col3:
        st.metric("Pending Transcriptions", pending, delta=f"-{pending}" if pending > 0 else "0")
    
    with col4:
        st.metric("This Week", this_week, delta=f"+{this_week}")
    
    st.markdown("---")
    
    # Quick actions
    st.subheader("Quick Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("🎙️ **New Recording**")
        st.caption("Click Record in sidebar →")
    
    with col2:
        st.markdown("📝 **View Cases**")
        st.caption("Click Cases in sidebar →")
    
    with col3:
        st.markdown("⚙️ **Settings**")
        st.caption("Click Settings in sidebar →")
    
    st.markdown("---")
    
    # Recent activity
    st.subheader("Recent Cases")
    
    if not cases:
        st.info("📭 No cases yet. Create your first recording!")
    else:
        # Show last 5 cases
        recent_cases = cases[:5]
        
        for case in recent_cases:
            # Get recordings for this case
            recordings = case_service.get_recordings_by_case(case.case_id)
            
            with st.container():
                col1, col2, col3 = st.columns([3, 2, 1])
                
                with col1:
                    st.markdown(f"**📁 {case.case_reference_id}** - {case.client_initials}")
                
                with col2:
                    st.markdown(f"*{len(recordings)} recording(s)*")
                
                with col3:
                    if st.button("View", key=f"view_{case.case_id}", use_container_width=True):
                        st.query_params.update({"page": "case_detail", "case_id": str(case.case_id)})
                        st.rerun()
                
                st.markdown("---")
        
        if len(cases) > 5:
            st.info(f"📊 Showing 5 of {len(cases)} cases")
    
    # Tips section
    st.markdown("---")
    st.subheader("💡 Tips")
    
    tips = [
        "🎙️ **Record in a quiet environment** for best transcription quality",
        "📝 **Review AI summaries** before finalizing - they're meant to assist, not replace your judgment",
        "🔒 **All recordings are encrypted** at rest for security",
        "⏱️ **Transcription takes ~2x the audio duration** - be patient!",
        "✏️ **Edit summaries directly** if the AI misses something important"
    ]
    
    import random
    st.info(random.choice(tips))