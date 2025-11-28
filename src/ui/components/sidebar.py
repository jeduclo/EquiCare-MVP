"""
Navigation sidebar component
"""

import streamlit as st


def show_sidebar():
    """Display navigation sidebar and return selected page"""
    
    with st.sidebar:
        # Logo
        try:
            from pathlib import Path
            logo_path = Path(__file__).parent.parent.parent / "assets" / "logo.jpg"
            if logo_path.exists():
                st.image(str(logo_path), width=150)  # Smaller for sidebar
        except:
            pass
        
        # Logo and app name
        st.markdown("# 🏥 EquiCare")
        st.markdown(f"**{st.session_state.full_name}**")
        st.markdown(f"*{st.session_state.role.replace('_', ' ').title()}*")
        st.markdown("---")
        
        # Get current page
        query_params = st.query_params
        if "page" in query_params:
            if query_params["page"] == "case_detail" and "case_id" in query_params:
                st.session_state.selected_case_id = int(query_params["case_id"])
                current_page = "case_detail"
            else:
                current_page = query_params.get("page", "home")
        else:
            current_page = "home"
        
        # Navigation buttons with custom styling
        st.markdown("### Navigation")
        
        # Custom CSS for button alignment and colors
        st.markdown("""
            <style>
            /* Left-align all sidebar buttons - HIGHEST PRIORITY */
            [data-testid="stSidebar"] button[kind="primary"],
            [data-testid="stSidebar"] button[kind="secondary"],
            [data-testid="stSidebar"] .stButton button {
                text-align: left !important;
                justify-content: flex-start !important;
                padding-left: 1rem !important;
                display: flex !important;
                align-items: center !important;
            }
            
            /* Active navigation buttons - LIGHT GREY */
            [data-testid="stSidebar"] button[kind="primary"],
            [data-testid="stSidebar"] .stButton > button[data-testid="baseButton-primary"] {
                background-color: #E5E7EB !important;
                color: #1F2937 !important;
                border: none !important;
                font-weight: 500 !important;
            }
            
            /* Inactive navigation buttons */
            [data-testid="stSidebar"] button[kind="secondary"],
            [data-testid="stSidebar"] .stButton > button[data-testid="baseButton-secondary"] {
                background-color: transparent !important;
                color: #6B7280 !important;
                border: 1px solid #D1D5DB !important;
            }
            
            /* Hover effect for inactive */
            [data-testid="stSidebar"] button[kind="secondary"]:hover,
            [data-testid="stSidebar"] .stButton > button[data-testid="baseButton-secondary"]:hover {
                background-color: #F9FAFB !important;
            }
            
            /* Force button content to align left */
            [data-testid="stSidebar"] button p,
            [data-testid="stSidebar"] button div {
                text-align: left !important;
                justify-content: flex-start !important;
            }
            </style>
        """, unsafe_allow_html=True)
        
        # Home button
        if st.button("🏠 Home", use_container_width=True, 
                    type="primary" if current_page == "home" else "secondary", 
                    key="nav_home"):
            st.query_params.clear()
            st.query_params.update({"page": "home"})
            st.rerun()
        
        # Record button
        if st.button("🎙️ Record", use_container_width=True, 
                    type="primary" if current_page == "record" else "secondary", 
                    key="nav_record"):
            st.query_params.clear()
            st.query_params.update({"page": "record"})
            st.rerun()
        
        # Cases button
        if st.button("📝 Cases", use_container_width=True, 
                    type="primary" if current_page == "cases" else "secondary", 
                    key="nav_cases"):
            st.query_params.clear()
            st.query_params.update({"page": "cases"})
            st.rerun()
        
        # Settings button
        if st.button("⚙️ Settings", use_container_width=True, 
                    type="primary" if current_page == "settings" else "secondary", 
                    key="nav_settings"):
            st.query_params.clear()
            st.query_params.update({"page": "settings"})
            st.rerun()
        
        # Admin link (only for administrators)
        if st.session_state.role == 'administrator':
            st.markdown("---")
            if st.button("👥 Admin Panel", use_container_width=True, key="nav_admin"):
                st.query_params.clear()
                st.query_params.update({"page": "admin"})
                st.rerun()
        
        st.markdown("---")
        
        # Logout button
        if st.button("🚪 Logout", use_container_width=True, key="nav_logout"):
            st.session_state.authenticated = False
            st.session_state.user_id = None
            st.session_state.username = None
            st.session_state.role = None
            st.query_params.clear()
            st.rerun()
    
    # Return current page
    return current_page