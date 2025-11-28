"""
Database models using SQLAlchemy ORM
Defines the schema for Users, Cases, Recordings, and Audit Log
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class User(Base):
    """User model for authentication and user management"""
    __tablename__ = 'users'
    
    user_id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False, default='social_worker')  # social_worker or administrator
    full_name = Column(String(100))
    email = Column(String(100))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime)
    failed_login_attempts = Column(Integer, default=0)
    locked_until = Column(DateTime, nullable=True)
    
    # Relationships
    cases = relationship("Case", back_populates="creator")
    recordings = relationship("Recording", back_populates="uploader", foreign_keys="Recording.uploaded_by")
    audit_logs = relationship("AuditLog", back_populates="user")
    
    def __repr__(self):
        return f"<User(username='{self.username}', role='{self.role}')>"


class Case(Base):
    """Case model representing a client case file"""
    __tablename__ = 'cases'
    
    case_id = Column(Integer, primary_key=True, autoincrement=True)
    case_reference_id = Column(String(50), nullable=False, index=True)  # User-provided reference
    client_initials = Column(String(10), nullable=False)
    created_by = Column(Integer, ForeignKey('users.user_id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    status = Column(String(20), default='active')  # active or archived
    
    # Relationships
    creator = relationship("User", back_populates="cases")
    recordings = relationship("Recording", back_populates="case", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Case(case_reference_id='{self.case_reference_id}', client_initials='{self.client_initials}')>"


class Recording(Base):
    """Recording model for audio files and their transcripts/summaries"""
    __tablename__ = 'recordings'
    
    recording_id = Column(Integer, primary_key=True, autoincrement=True)
    case_id = Column(Integer, ForeignKey('cases.case_id'), nullable=False)
    uploaded_by = Column(Integer, ForeignKey('users.user_id'), nullable=False)
    
    # Recording metadata
    recording_date = Column(DateTime, nullable=False)
    recording_type = Column(String(20), nullable=False)  # phone, home_visit, office
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer)  # in bytes
    duration_seconds = Column(Float)
    
    # Processing status
    transcription_status = Column(String(20), default='pending')  # pending, processing, completed, failed
    transcription_started_at = Column(DateTime, nullable=True)
    transcription_completed_at = Column(DateTime, nullable=True)
    
    # Content
    transcript_text = Column(Text, nullable=True)
    summary_text = Column(Text, nullable=True)
    additional_notes = Column(Text, nullable=True)
    tags = Column(String(500), nullable=True)  # Comma-separated tags
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    last_edited_at = Column(DateTime, nullable=True)
    last_edited_by = Column(Integer, ForeignKey('users.user_id'), nullable=True)
    
    # Relationships
    case = relationship("Case", back_populates="recordings")
    uploader = relationship("User", back_populates="recordings", foreign_keys=[uploaded_by])
    
    def __repr__(self):
        return f"<Recording(recording_id={self.recording_id}, case_id={self.case_id}, status='{self.transcription_status}')>"


class AuditLog(Base):
    """Audit log for tracking all user actions"""
    __tablename__ = 'audit_log'
    
    log_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)
    action = Column(String(50), nullable=False)  # login, logout, upload, edit, delete, etc.
    target_type = Column(String(50), nullable=True)  # case, recording, user
    target_id = Column(Integer, nullable=True)
    details = Column(Text, nullable=True)  # JSON string with additional details
    ip_address = Column(String(45), nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="audit_logs")
    
    def __repr__(self):
        return f"<AuditLog(user_id={self.user_id}, action='{self.action}', timestamp='{self.timestamp}')>"