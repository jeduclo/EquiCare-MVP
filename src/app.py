"""
EquiCare MVP - Main Streamlit Application
Entry point for the application
"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import streamlit as st
from src.config.settings import Settings
# NEW: Import the DB manager and seeding function
from src.database.db_manager import db_manager, seed_admin_user

# Configure page
st.set_page_config(
    page_title=Settings.PAGE_TITLE,
    page_icon=Settings.PAGE_ICON,
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load custom CSS
def load_custom_css():
    """Load custom CSS for styling"""
    css = f"""
    <style>
        /* Main theme colors */
        :root {{
            --primary-color: {Settings.THEME['primary_color']};
            --background-color: {Settings.THEME['background_color']};
            --secondary-bg: {Settings.THEME['secondary_background_color']};
            --text-color: {Settings.THEME['text_color']};
        }}
        
        /* Hide Streamlit branding */
        #MainMenu {{visibility: hidden;}}
        footer {{visibility: hidden;}}
        
        /* Custom styling */
        .main {{
            background-color: var(--background-color);
        }}
        
        /* Card styling */
        .card {{
            background-color: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }}
        
        /* Button styling */
        .stButton > button {{
            border-radius: 8px;
            padding: 10px 24px;
            font-weight: 500;
        }}
        
        /* Primary buttons - Navy blue */
        .stButton > button[kind="primary"],
        .stButton > button[data-testid="baseButton-primary"] {{
            background-color: {Settings.THEME['primary_color']} !important;
            color: white !important;
            border: none !important;
        }}
        
        /* Form submit buttons - Navy blue */
        button[kind="primaryFormSubmit"],
        .stFormSubmitButton > button {{
            background-color: {Settings.THEME['primary_color']} !important;
            color: white !important;
            border: none !important;
        }}
        
        /* SIDEBAR SPECIFIC - Active navigation buttons LIGHT GREY */
        [data-testid="stSidebar"] button[kind="primary"],
        [data-testid="stSidebar"] .stButton > button[kind="primary"] {{
            background-color: #E5E7EB !important;
            color: #1F2937 !important;
            border: none !important;
            font-weight: 500 !important;
        }}
        
        /* SIDEBAR - Inactive navigation buttons */
        [data-testid="stSidebar"] button[kind="secondary"],
        [data-testid="stSidebar"] .stButton > button[kind="secondary"] {{
            background-color: transparent !important;
            color: #6B7280 !important;
            border: 1px solid #D1D5DB !important;
        }}
        
        /* SIDEBAR - Hover effect for inactive */
        [data-testid="stSidebar"] button[kind="secondary"]:hover,
        [data-testid="stSidebar"] .stButton > button[kind="secondary"]:hover {{
            background-color: #F9FAFB !important;
            border-color: #9CA3AF !important;
        }}
        
        /* Recording button */
        .record-button {{
            background-color: {Settings.THEME['primary_color']} !important;
            color: white !important;
            font-size: 18px !important;
            padding: 20px 40px !important;
            border-radius: 50px !important;
        }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)


# Initialize session state
def init_session_state():
    """Initialize session state variables"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'user_id' not in st.session_state:
        st.session_state.user_id = None
    if 'username' not in st.session_state:
        st.session_state.username = None
    if 'role' not in st.session_state:
        st.session_state.role = None
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'home'


def main():
    """Main application function"""
    
    # Load custom CSS
    load_custom_css()
    
    # Initialize session state
    init_session_state()
    
    # --- AUTOMATIC DATABASE INITIALIZATION ---
    # This block ensures that when deployed to Supabase (fresh DB),
    # the tables are created and the admin user is seeded AUTOMATICALLY.
    try:
        # Create tables if they don't exist
        db_manager.init_db()
        # Ensure default admin user exists
        seed_admin_user()
    except Exception as e:
        # In case of DB connection errors, we log it but don't crash immediately
        # to allow the error UI to show if needed
        print(f"DB Init Warning: {e}")
    # -----------------------------------------
    
    # Check if database needs setup (This will now likely be FALSE because we just seeded the admin)
    needs_setup = False
    if not st.session_state.authenticated and not st.session_state.get('setup_complete', False):
        try:
            from src.database.db_manager import get_db_session
            from src.database.models import User
            
            with get_db_session() as session:
                user_count = session.query(User).count()
                needs_setup = user_count == 0
        except Exception as e:
            # If any error (no table, no database, etc.), we need setup
            needs_setup = True
        
        if needs_setup:
            # Show setup page
            from src.ui.pages.setup import show as show_setup
            show_setup()
            return
    
    # Check authentication
    if not st.session_state.authenticated:
        # Show login page
        from src.ui.pages.login import show_login_page
        show_login_page()
    else:
        # Show main application
        from src.ui.components.sidebar import show_sidebar
        from src.ui.pages import home, record, cases, case_detail, admin, settings
        
        # Get page from sidebar
        page = show_sidebar()
        
        # Route to appropriate page
        if page == 'home':
            home.show()
        elif page == 'record':
            record.show()
        elif page == 'cases':
            cases.show()
        elif page == 'case_detail':
            case_detail.show()
        elif page == 'admin':
            admin.show()
        elif page == 'settings':
            settings.show()


if __name__ == "__main__":
    main()