"""
One-time setup page for creating admin user on Streamlit Cloud
This page appears only when the database is empty
"""

import streamlit as st
from src.database.db_manager import db_manager, get_db_session
from src.database.models import User
from src.auth.password_utils import hash_password
from datetime import datetime


def show():
    """Display setup page for first-time initialization"""
    
    st.title("🔧 EquiCare First-Time Setup")
    
    # Check if already initialized
    try:
        with get_db_session() as session:
            admin_exists = session.query(User).filter_by(username='admin').first()
        
        if admin_exists:
            st.error("⚠️ Setup already completed! Admin user exists.")
            st.info("👉 Please go to the login page to access EquiCare.")
            if st.button("🔐 Go to Login"):
                st.session_state.setup_complete = True
                st.rerun()
            return
    except Exception as e:
        # Database might not exist yet
        pass
    
    st.markdown("---")
    
    st.markdown("""
    ## Welcome to EquiCare! 👋
    
    This is a **one-time setup** to create your administrator account.
    
    **What happens next:**
    1. Database will be initialized
    2. Admin account will be created
    3. You'll be able to login and start using EquiCare
    """)
    
    st.markdown("---")
    
    st.markdown("### Create Administrator Account")
    
    with st.form("setup_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            username = st.text_input(
                "Username *",
                value="admin",
                help="Login username for administrator"
            )
            password = st.text_input(
                "Password *",
                type="password",
                help="Must be at least 8 characters"
            )
        
        with col2:
            full_name = st.text_input(
                "Full Name *",
                value="System Administrator",
                help="Your full name"
            )
            email = st.text_input(
                "Email (optional)",
                help="Your email address"
            )
        
        st.markdown("""
        **Password Requirements:**
        - Minimum 8 characters
        - At least 1 number
        - At least 1 special character
        """)
        
        submitted = st.form_submit_button("✅ Create Account & Initialize", type="primary", use_container_width=True)
        
        if submitted:
            # Validation
            if not username or not password or not full_name:
                st.error("⚠️ Username, password, and full name are required!")
            elif len(password) < 8:
                st.error("⚠️ Password must be at least 8 characters!")
            elif not any(char.isdigit() for char in password):
                st.error("⚠️ Password must contain at least one number!")
            elif not any(char in '!@#$%^&*()_+-=[]{}|;:,.<>?' for char in password):
                st.error("⚠️ Password must contain at least one special character!")
            else:
                # Try to create admin
                with st.spinner("🔄 Initializing database and creating admin account..."):
                    try:
                        # Initialize database
                        db_manager.init_db()
                        
                        # Create admin user
                        with get_db_session() as session:
                            admin = User(
                                username=username,
                                password_hash=hash_password(password),
                                role='administrator',
                                full_name=full_name,
                                email=email if email else None,
                                is_active=True,
                                created_at=datetime.utcnow(),
                                failed_login_attempts=0
                            )
                            session.add(admin)
                            session.commit()
                        
                        st.success("✅ Setup complete! Admin account created successfully.")
                        st.balloons()
                        
                        st.markdown("---")
                        st.info(f"""
                        **Your login credentials:**
                        - Username: `{username}`
                        - Password: `{password}`
                        
                        **⚠️ Please save these credentials!**
                        """)
                        
                        # Set session state to show login page
                        st.session_state.setup_complete = True
                        st.markdown("---")
                        st.info("🎉 Setup complete! Please refresh the page to login.")
                    
                    except Exception as e:
                        st.error(f"❌ Setup failed: {str(e)}")
                        with st.expander("Error Details"):
                            import traceback
                            st.code(traceback.format_exc())
    
    st.markdown("---")
    
    st.markdown("""
    ### ℹ️ About EquiCare
    
    **EquiCare** is an AI-powered case recording and management system designed for social workers.
    
    **Features:**
    - 🎙️ Browser-based audio recording
    - 🤖 AI transcription (OpenAI Whisper)
    - 📝 AI-generated case notes (GPT-4)
    - 🔒 Secure encrypted storage
    - 👥 User management
    - 📊 Case tracking
    """)