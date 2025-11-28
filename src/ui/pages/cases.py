"""
Cases page - View and manage cases
"""

import streamlit as st
from src.services.case_service import case_service


def show():
    """Display cases list page"""
    
    st.title("📝 My Cases")
    st.markdown("View and manage your case recordings")
    
    st.markdown("---")
    
    # Search and filter
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        search_term = st.text_input(
            "🔍 Search cases",
            placeholder="Search by Case Reference or Client Initials",
            label_visibility="collapsed"
        )
    
    with col2:
        show_all = st.checkbox("Show all cases", value=False, 
                              disabled=st.session_state.role != 'administrator',
                              help="Admin only: View cases from all users")
    
    with col3:
        if st.button("🔄 Refresh", use_container_width=True):
            st.rerun()
    
    st.markdown("---")
    
    # Fetch cases
    if search_term:
        # Search mode
        user_id = None if show_all else st.session_state.user_id
        cases = case_service.search_cases(search_term, user_id)
    else:
        # List all
        if show_all and st.session_state.role == 'administrator':
            cases = case_service.get_all_cases()
        else:
            cases = case_service.get_cases_by_user(st.session_state.user_id)
    
    # Display results
    if not cases:
        st.info("📭 No cases found. Create your first recording!")
        
        if st.button("🎙️ New Recording", type="primary", use_container_width=True):
            st.session_state.current_page = 'record'
            st.rerun()
    else:
        st.markdown(f"**Found {len(cases)} case(s)**")
        st.markdown("")
        
        # Display cases as cards
        for case in cases:
            # Get recordings count
            recordings = case_service.get_recordings_by_case(case.case_id)
            recording_count = len(recordings)
            
            # Calculate stats
            pending_count = sum(1 for r in recordings if r.transcription_status == 'pending')
            completed_count = sum(1 for r in recordings if r.transcription_status == 'completed')
            
            # Create card
            with st.container():
                col1, col2, col3 = st.columns([3, 2, 1])
                
                with col1:
                    st.markdown(f"### 📁 {case.case_reference_id}")
                    st.markdown(f"**Client:** {case.client_initials}")
                    st.markdown(f"*Last updated: {case.last_updated.strftime('%Y-%m-%d %H:%M')}*")
                
                with col2:
                    st.metric("Recordings", recording_count)
                    if pending_count > 0:
                        st.warning(f"⏳ {pending_count} pending transcription")
                    if completed_count > 0:
                        st.success(f"✅ {completed_count} completed")
                
                with col3:
                    if st.button("View Details", key=f"view_{case.case_id}", use_container_width=True):
                        # Store case ID and trigger rerun
                        st.session_state.selected_case_id = case.case_id
                        # Use query params to navigate
                        st.query_params.update({"page": "case_detail", "case_id": str(case.case_id)})
                        st.rerun()
                
                st.markdown("---")