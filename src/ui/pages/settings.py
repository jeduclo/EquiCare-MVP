"""
Settings page - User preferences and password change
"""

import streamlit as st
from src.services.user_service import user_service


def show():
    """Display settings page"""
    
    st.title("⚙️ Settings")
    st.markdown("Manage your account settings")
    
    st.markdown("---")
    
    # Tabs for different settings
    tab1, tab2 = st.tabs(["🔑 Change Password", "👤 Profile"])
    
    with tab1:
        show_change_password()
    
    with tab2:
        show_profile()


def show_change_password():
    """Display change password form"""
    
    st.subheader("Change Password")
    
    with st.form("change_password_form"):
        current_password = st.text_input("Current Password", type="password")
        new_password = st.text_input("New Password", type="password")
        confirm_password = st.text_input("Confirm New Password", type="password")
        
        st.markdown("""
        **Password Requirements:**
        - Minimum 8 characters
        - At least one number
        - At least one special character (!@#$%^&*()_+-=[]{}|;:,.<>?)
        """)
        
        submitted = st.form_submit_button("🔒 Change Password", use_container_width=True)
        
        if submitted:
            if not current_password or not new_password or not confirm_password:
                st.error("⚠️ All fields are required")
            elif new_password != confirm_password:
                st.error("⚠️ New passwords do not match")
            else:
                result = user_service.change_own_password(
                    user_id=st.session_state.user_id,
                    current_password=current_password,
                    new_password=new_password
                )
                
                if result['success']:
                    st.success("✅ " + result['message'])
                    st.info("👉 Please login again with your new password")
                else:
                    st.error("❌ " + result['error'])


def show_profile():
    """Display user profile information"""
    
    st.subheader("Profile Information")
    
    # Get user info from session
    st.markdown(f"""
    **Username:** {st.session_state.username}
    
    **Full Name:** {st.session_state.full_name}
    
    **Role:** {st.session_state.role.replace('_', ' ').title()}
    
    **User ID:** {st.session_state.user_id}
    """)
    
    st.markdown("---")
    
    st.info("""
    **Note:** To update your full name or email, please contact an administrator.
    """)
    
    st.markdown("---")
    
    # About section
    st.subheader("About EquiCare")
    
    from src.config.settings import Settings
    
    st.markdown(f"""
    **Version:** {Settings.APP_VERSION}
    
    **EquiCare** is an AI-powered case recording and management system designed for social workers.
    
    **Features:**
    - 🎙️ Browser-based audio recording
    - 🤖 AI transcription (OpenAI Whisper)
    - 📝 AI case note generation (GPT-4)
    - 🔒 Secure encrypted storage
    - 📱 Mobile-responsive interface
    """)