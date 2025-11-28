"""
Database manager
Handles database connections and provides query interface
"""

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
        # Create database URL
        if Settings.DATABASE_URL.startswith('sqlite'):
            # For SQLite, create full path
            db_path = Settings.ROOT_DIR / Settings.DATABASE_URL.replace('sqlite:///', '')
            db_url = f'sqlite:///{db_path}'
        else:
            db_url = Settings.DATABASE_URL
        
        # Create engine
        self.engine = create_engine(
            db_url,
            echo=Settings.DEBUG_MODE,
            connect_args={'check_same_thread': False} if 'sqlite' in db_url else {}
        )
        
        # Create session factory
        self.session_factory = sessionmaker(bind=self.engine)
        self.Session = scoped_session(self.session_factory)
        
        logger.info(f"Database initialized: {db_url}")
    
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