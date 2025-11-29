"""
Database manager
Handles database connections and provides query interface
"""

import streamlit as st
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from contextlib import contextmanager
from src.config.settings import Settings
from src.database.models import Base
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manages database connections and sessions"""
    
    def __init__(self):
        """Initialize database connection"""
        
        # 1. Check for Streamlit Secrets (Production/Supabase)
        # We look for the [connections.supabase] section in secrets.toml
        if "connections" in st.secrets and "supabase" in st.secrets["connections"]:
            try:
                secrets = st.secrets["connections"]["supabase"]
                # Construct the PostgreSQL connection string
                # We use postgresql:// for SQLAlchemy compatibility
                self.db_url = f"postgresql://{secrets['username']}:{secrets['password']}@{secrets['host']}:{secrets['port']}/{secrets['database']}"
                self.is_sqlite = False
                logger.info("Using Supabase PostgreSQL connection")
            except KeyError as e:
                logger.error(f"Missing key in secrets: {e}")
                raise
        
        # 2. Fallback to Settings (Local Development/SQLite)
        else:
            if Settings.DATABASE_URL.startswith('sqlite'):
                # For SQLite, create full path
                db_path = Settings.ROOT_DIR / Settings.DATABASE_URL.replace('sqlite:///', '')
                self.db_url = f'sqlite:///{db_path}'
                self.is_sqlite = True
            else:
                self.db_url = Settings.DATABASE_URL
                self.is_sqlite = False
            logger.info(f"Using Local connection: {self.db_url}")
        
        # 3. Create engine with specific arguments based on DB type
        connect_args = {}
        engine_args = {
            "echo": Settings.DEBUG_MODE
        }

        if self.is_sqlite:
            # SQLite specific args
            connect_args['check_same_thread'] = False
        else:
            # PostgreSQL/Supabase specific args
            # pool_pre_ping=True helps prevent "connection closed" errors in cloud
            engine_args['pool_pre_ping'] = True
            
            # --- CRITICAL FIX FOR SUPABASE TRANSACTION POOLER (Port 6543) ---
            # The Transaction Pooler does not support prepared statements.
            # Setting prepare_threshold to None disables them in psycopg2.
            connect_args["prepare_threshold"] = None
            # ----------------------------------------------------------------

        self.engine = create_engine(
            self.db_url,
            connect_args=connect_args,
            **engine_args
        )
        
        # Create session factory
        self.session_factory = sessionmaker(bind=self.engine)
        self.Session = scoped_session(self.session_factory)
        
    def create_tables(self):
        """Create all tables defined in models"""
        Base.metadata.create_all(self.engine)
        logger.info("Database tables created")
    
    def drop_tables(self):
        """Drop all tables (use with caution!)"""
        Base.metadata.drop_all(self.engine)
        logger.warning("All database tables dropped")
    
    @contextmanager
    def get_session(self):
        """
        Context manager for database sessions
        
        Usage:
            with db_manager.get_session() as session:
                user = session.query(User).first()
        """
        session = self.Session()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            session.close()
    
    def init_db(self):
        """Initialize database with tables"""
        self.create_tables()


# Global database manager instance
db_manager = DatabaseManager()


# Convenience function for getting sessions
def get_db_session():
    """Get a database session (context manager)"""
    return db_manager.get_session()


# --- HELPER TO CREATE ADMIN USER ---
# This is called from app.py to ensure an admin exists on fresh deployments
def seed_admin_user():
    from src.database.models import User
    from src.auth.password_utils import get_password_hash # Assuming you have this
    
    with get_db_session() as session:
        # Check if admin already exists
        existing_admin = session.query(User).filter_by(username="admin").first()
        
        if not existing_admin:
            logger.info("Creating default admin user...")
            admin_user = User(
                username="admin",
                full_name="System Administrator",
                role="administrator",
                # You must verify this matches your password hashing function
                password_hash=get_password_hash("admin123"), 
                is_active=True
            )
            session.add(admin_user)
            logger.info("Admin user created: admin / admin123")
        else:
            logger.info("Admin user already exists.")