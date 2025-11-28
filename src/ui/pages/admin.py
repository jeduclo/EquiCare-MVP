"""
Admin page - User management
"""

import streamlit as st
from src.services.user_service import user_service


def show():
    """Display admin panel"""
    
    # Check if user is admin
    if st.session_state.role != 'administrator':
        st.error("⛔ Access Denied: Administrator privileges required")
        return
    
    # Header with back button
    col1, col2 = st.columns([4, 1])
    
    with col1:
        st.title("👥 Admin Panel")
        st.markdown("Manage users and system settings")
    
    with col2:
        if st.button("← Back", use_container_width=True):
            st.query_params.clear()
            st.rerun()
    
    st.markdown("---")
    
    # Tabs for different admin functions
    tab1, tab2, tab3 = st.tabs(["👤 Users", "📊 Statistics", "⚙️ System"])
    
    with tab1:
        show_users_tab()
    
    with tab2:
        show_statistics_tab()
    
    with tab3:
        show_system_tab()


def show_users_tab():
    """Display user management tab"""
    
    st.subheader("User Management")
    
    # Add new user section
    with st.expander("➕ Add New User", expanded=False):
        with st.form("add_user_form", clear_on_submit=True):
            st.markdown("### Create New User Account")
            
            col1, col2 = st.columns(2)
            
            with col1:
                new_username = st.text_input(
                    "Username *",
                    placeholder="e.g., jdoe",
                    help="Must be unique"
                )
                new_password = st.text_input(
                    "Password *",
                    type="password",
                    help="Min 8 chars, 1 number, 1 special char"
                )
                new_role = st.selectbox(
                    "Role *",
                    ["social_worker", "administrator"],
                    format_func=lambda x: "Social Worker" if x == "social_worker" else "Administrator"
                )
            
            with col2:
                new_full_name = st.text_input(
                    "Full Name",
                    placeholder="e.g., John Doe"
                )
                new_email = st.text_input(
                    "Email",
                    placeholder="e.g., john.doe@example.com"
                )
            
            st.markdown("**Password Requirements:** Min 8 characters, 1 number, 1 special character")
            
            submitted = st.form_submit_button("✅ Create User", type="primary", use_container_width=True)
            
            if submitted:
                # Validation
                if not new_username or not new_password:
                    st.error("⚠️ Username and password are required")
                elif len(new_username) < 3:
                    st.error("⚠️ Username must be at least 3 characters")
                else:
                    # Try to create user
                    try:
                        result = user_service.create_user(
                            username=new_username.strip(),
                            password=new_password,
                            role=new_role,
                            full_name=new_full_name.strip() if new_full_name else None,
                            email=new_email.strip() if new_email else None
                        )
                        
                        if result['success']:
                            st.success(f"✅ {result['message']}")
                            st.balloons()
                            # Force reload to show new user
                            import time
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error(f"❌ {result['error']}")
                    
                    except Exception as e:
                        st.error(f"❌ Error creating user: {str(e)}")
                        import traceback
                        with st.expander("Error Details"):
                            st.code(traceback.format_exc())
    
    st.markdown("---")
    
    # List all users
    st.subheader("All Users")
    
    users = user_service.get_all_users()
    
    if not users:
        st.info("No users found")
        return
    
    # Display users in a table-like format
    for user in users:
        with st.container():
            col1, col2, col3, col4 = st.columns([2, 2, 1, 2])
            
            with col1:
                status_icon = "🟢" if user['is_active'] else "🔴"
                st.markdown(f"### {status_icon} {user['username']}")
                if user['full_name']:
                    st.markdown(f"*{user['full_name']}*")
            
            with col2:
                role_display = "👤 Social Worker" if user['role'] == 'social_worker' else "👑 Administrator"
                st.markdown(f"**Role:** {role_display}")
                if user['email']:
                    st.markdown(f"**Email:** {user['email']}")
            
            with col3:
                st.markdown(f"**Status:**")
                st.markdown("Active" if user['is_active'] else "Inactive")
            
            with col4:
                # Don't allow admin to deactivate themselves
                if user['user_id'] == st.session_state.user_id:
                    st.info("(Current User)")
                else:
                    if user['is_active']:
                        if st.button("🚫 Deactivate", key=f"deactivate_{user['user_id']}", use_container_width=True):
                            result = user_service.deactivate_user(user['user_id'])
                            if result['success']:
                                st.success(result['message'])
                                st.rerun()
                            else:
                                st.error(result['error'])
                    else:
                        if st.button("✅ Activate", key=f"activate_{user['user_id']}", use_container_width=True):
                            result = user_service.activate_user(user['user_id'])
                            if result['success']:
                                st.success(result['message'])
                                st.rerun()
                            else:
                                st.error(result['error'])
                    
                    # Reset password button
                    if st.button("🔑 Reset Password", key=f"reset_{user['user_id']}", use_container_width=True):
                        st.session_state[f'show_reset_{user["user_id"]}'] = True
                
                # Show password reset form if button clicked
                if st.session_state.get(f'show_reset_{user["user_id"]}', False):
                    new_pwd = st.text_input("New Password", type="password", key=f"pwd_{user['user_id']}")
                    col_a, col_b = st.columns(2)
                    with col_a:
                        if st.button("Save", key=f"save_{user['user_id']}"):
                            if new_pwd:
                                result = user_service.reset_password(user['user_id'], new_pwd)
                                if result['success']:
                                    st.success(result['message'])
                                    st.session_state[f'show_reset_{user["user_id"]}'] = False
                                    st.rerun()
                                else:
                                    st.error(result['error'])
                            else:
                                st.warning("Enter a password")
                    with col_b:
                        if st.button("Cancel", key=f"cancel_{user['user_id']}"):
                            st.session_state[f'show_reset_{user["user_id"]}'] = False
                            st.rerun()
            
            st.markdown("---")


def show_statistics_tab():
    """Display system statistics"""
    
    st.subheader("System Statistics")
    
    # User stats
    user_stats = user_service.get_user_stats()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Users", user_stats['total_users'])
    
    with col2:
        st.metric("Active Users", user_stats['active_users'])
    
    with col3:
        st.metric("Social Workers", user_stats['social_workers'])
    
    with col4:
        st.metric("Administrators", user_stats['administrators'])
    
    st.markdown("---")
    
    # Case stats
    from src.services.case_service import case_service
    
    st.subheader("Case Statistics")
    
    all_cases = case_service.get_all_cases(limit=1000)
    
    from src.database.db_manager import get_db_session
    from src.database.models import Recording
    
    with get_db_session() as session:
        total_recordings = session.query(Recording).count()
        pending_transcriptions = session.query(Recording).filter_by(transcription_status='pending').count()
        completed_transcriptions = session.query(Recording).filter_by(transcription_status='completed').count()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Cases", len(all_cases))
    
    with col2:
        st.metric("Total Recordings", total_recordings)
    
    with col3:
        st.metric("Pending", pending_transcriptions)
    
    with col4:
        st.metric("Completed", completed_transcriptions)


def show_system_tab():
    """Display system settings"""
    
    st.subheader("System Information")
    
    from src.config.settings import Settings
    
    st.markdown(f"""
    **Application:** {Settings.APP_NAME} v{Settings.APP_VERSION}
    
    **Configuration:**
    - AI Transcription: {Settings.AI_TRANSCRIPTION_MODEL}
    - AI Summarization: {Settings.AI_SUMMARIZATION_MODEL}
    - Max Recording Duration: {Settings.MAX_RECORDING_DURATION // 60} minutes
    - Database: SQLite
    
    **Security:**
    - Password Min Length: {Settings.PASSWORD_MIN_LENGTH} characters
    - Max Login Attempts: {Settings.MAX_LOGIN_ATTEMPTS}
    - Lockout Duration: {Settings.LOCKOUT_DURATION_MINUTES} minutes
    """)
    
    st.markdown("---")
    
    st.subheader("Database Backup")
    
    if st.button("📥 Backup Database", use_container_width=True):
        import shutil
        from datetime import datetime
        
        backup_name = f"equicare_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        backup_path = Settings.DATA_DIR / backup_name
        
        db_path = Settings.ROOT_DIR / "data" / "equicare.db"
        
        if db_path.exists():
            shutil.copy(db_path, backup_path)
            st.success(f"✅ Database backed up to: {backup_name}")
        else:
            st.error("❌ Database file not found")