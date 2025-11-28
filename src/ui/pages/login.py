"""
Login page for user authentication
"""

import streamlit as st
import base64
from datetime import datetime, timedelta
from src.database.db_manager import get_db_session
from src.database.models import User, AuditLog
from src.auth.password_utils import verify_password
from src.config.settings import Settings


def get_image_base64(image_path):
    """Helper to convert image to base64 string for HTML embedding"""
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except Exception:
        return None


def show_login_page():
    """Display the login page"""
    
    # Center the login form on the screen
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # Logo Section - Using HTML for perfect mobile/desktop centering
        try:
            from pathlib import Path
            logo_path = Path(__file__).parent.parent.parent / "assets" / "logo.jpg"
            
            if logo_path.exists():
                img_base64 = get_image_base64(logo_path)
                if img_base64:
                    # HTML allows us to force centering with Flexbox, which survives mobile stacking
                    st.markdown(
                        f"""
                        <div style="display: flex; justify-content: center; margin-bottom: 20px;">
                            <img src="data:image/jpg;base64,{img_base64}" width="250">
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
        except Exception:
            pass
        
        # Logo and title
        st.markdown("<h1 style='text-align: center;'>🏥 EquiCare</h1>", unsafe_allow_html=True)
        st.markdown("<h3 style='text-align: center; color: #6B7280;'>Case Recording System</h3>", unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Login form
        with st.form("login_form"):
            st.markdown("### Sign In")
            
            username = st.text_input("Username", key="login_username")
            password = st.text_input("Password", type="password", key="login_password")
            
            submit = st.form_submit_button("Login", use_container_width=True)
            
            if submit:
                if authenticate_user(username, password):
                    st.success("Login successful! Redirecting...")
                    st.rerun()
                else:
                    st.error("Invalid username or password")
        
        # Info box
        # st.info("👤 **First time?** Use username: `admin` and password: `admin123`")


def authenticate_user(username: str, password: str) -> bool:
    """
    Authenticate user credentials
    
    Args:
        username: Username
        password: Password
        
    Returns:
        True if authentication successful, False otherwise
    """
    
    if not username or not password:
        return False
    
    with get_db_session() as session:
        # Find user
        user = session.query(User).filter_by(username=username).first()
        
        if not user:
            return False
        
        # Check if user is active
        if not user.is_active:
            st.error("This account has been deactivated. Please contact an administrator.")
            return False
        
        # Check if account is locked
        if user.locked_until and user.locked_until > datetime.utcnow():
            remaining_minutes = int((user.locked_until - datetime.utcnow()).total_seconds() / 60)
            st.error(f"Account is locked. Try again in {remaining_minutes} minutes.")
            return False
        
        # Verify password
        if not verify_password(password, user.password_hash):
            # Increment failed attempts
            user.failed_login_attempts += 1
            
            # Lock account if max attempts exceeded
            if user.failed_login_attempts >= Settings.MAX_LOGIN_ATTEMPTS:
                user.locked_until = datetime.utcnow() + timedelta(minutes=Settings.LOCKOUT_DURATION_MINUTES)
                session.commit()
                st.error(f"Too many failed attempts. Account locked for {Settings.LOCKOUT_DURATION_MINUTES} minutes.")
            else:
                remaining = Settings.MAX_LOGIN_ATTEMPTS - user.failed_login_attempts
                st.warning(f"Invalid password. {remaining} attempts remaining.")
            
            session.commit()
            
            # Log failed attempt
            log_audit(session, user.user_id, "login_failed", None, None, f"Failed login attempt for {username}")
            
            return False
        
        # Successful login
        user.failed_login_attempts = 0
        user.locked_until = None
        user.last_login = datetime.utcnow()
        session.commit()
        
        # Log successful login
        log_audit(session, user.user_id, "login", None, None, f"User {username} logged in")
        
        # Set session state
        st.session_state.authenticated = True
        st.session_state.user_id = user.user_id
        st.session_state.username = user.username
        st.session_state.role = user.role
        st.session_state.full_name = user.full_name or user.username
        
        return True


def log_audit(session, user_id: int, action: str, target_type: str, target_id: int, details: str):
    """Log an audit entry"""
    audit_log = AuditLog(
        user_id=user_id,
        action=action,
        target_type=target_type,
        target_id=target_id,
        details=details,
        timestamp=datetime.utcnow()
    )
    session.add(audit_log)