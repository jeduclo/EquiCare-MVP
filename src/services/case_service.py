"""
Case service
Business logic for managing cases
"""

from datetime import datetime
from src.database.db_manager import get_db_session
from src.database.models import Case, Recording, User


class CaseService:
    """Service for managing cases"""
    
    @staticmethod
    def get_or_create_case(case_reference_id: str, client_initials: str, user_id: int):
        """
        Get existing case or create new one
        
        Args:
            case_reference_id: User-provided case reference
            client_initials: Client initials
            user_id: User creating/accessing the case
            
        Returns:
            dict with case information
        """
        with get_db_session() as session:
            # Try to find existing case
            case = session.query(Case).filter_by(
                case_reference_id=case_reference_id
            ).first()
            
            if case:
                # Update last_updated
                case.last_updated = datetime.utcnow()
                session.commit()
                # Return dict instead of object
                return {
                    'case_id': case.case_id,
                    'case_reference_id': case.case_reference_id,
                    'client_initials': case.client_initials,
                    'created_by': case.created_by,
                    'created_at': case.created_at,
                    'last_updated': case.last_updated,
                    'status': case.status
                }
            else:
                # Create new case
                new_case = Case(
                    case_reference_id=case_reference_id,
                    client_initials=client_initials,
                    created_by=user_id,
                    created_at=datetime.utcnow(),
                    last_updated=datetime.utcnow(),
                    status='active'
                )
                session.add(new_case)
                session.commit()
                # Return dict instead of object
                return {
                    'case_id': new_case.case_id,
                    'case_reference_id': new_case.case_reference_id,
                    'client_initials': new_case.client_initials,
                    'created_by': new_case.created_by,
                    'created_at': new_case.created_at,
                    'last_updated': new_case.last_updated,
                    'status': new_case.status
                }
    
    @staticmethod
    def get_case_by_id(case_id: int):
        """Get case by ID"""
        with get_db_session() as session:
            case = session.query(Case).filter_by(case_id=case_id).first()
            if case:
                session.expunge(case)  # Detach from session
            return case
    
    @staticmethod
    def get_cases_by_user(user_id: int, limit: int = 100):
        """Get all cases created by a user"""
        with get_db_session() as session:
            cases = session.query(Case).filter_by(
                created_by=user_id
            ).order_by(
                Case.last_updated.desc()
            ).limit(limit).all()
            
            # Detach from session
            for case in cases:
                session.expunge(case)
            
            return cases
    
    @staticmethod
    def get_all_cases(limit: int = 100):
        """Get all cases (for admin)"""
        with get_db_session() as session:
            cases = session.query(Case).order_by(
                Case.last_updated.desc()
            ).limit(limit).all()
            
            for case in cases:
                session.expunge(case)
            
            return cases
    
    @staticmethod
    def search_cases(search_term: str, user_id: int = None):
        """
        Search cases by reference ID or client initials
        
        Args:
            search_term: Search string
            user_id: Optional user ID to filter by
            
        Returns:
            List of matching cases
        """
        with get_db_session() as session:
            query = session.query(Case)
            
            # Filter by user if provided
            if user_id:
                query = query.filter_by(created_by=user_id)
            
            # Search in case_reference_id and client_initials
            query = query.filter(
                (Case.case_reference_id.contains(search_term)) |
                (Case.client_initials.contains(search_term))
            )
            
            cases = query.order_by(Case.last_updated.desc()).all()
            
            for case in cases:
                session.expunge(case)
            
            return cases
    
    @staticmethod
    def create_recording(case_id: int, user_id: int, recording_data: dict):
        """
        Create a new recording entry
        
        Args:
            case_id: Case ID
            user_id: User ID
            recording_data: Dict with recording details
            
        Returns:
            dict with recording information
        """
        with get_db_session() as session:
            recording = Recording(
                case_id=case_id,
                uploaded_by=user_id,
                recording_date=recording_data['recording_date'],
                recording_type=recording_data['recording_type'],
                file_path=recording_data['file_path'],
                file_size=recording_data.get('file_size'),
                duration_seconds=recording_data.get('duration_seconds'),
                transcription_status='pending',
                additional_notes=recording_data.get('additional_notes', ''),
                tags=recording_data.get('tags', ''),
                created_at=datetime.utcnow()
            )
            
            session.add(recording)
            session.commit()
            
            # Return dict instead of object
            return {
                'recording_id': recording.recording_id,
                'case_id': recording.case_id,
                'uploaded_by': recording.uploaded_by,
                'recording_date': recording.recording_date,
                'recording_type': recording.recording_type,
                'file_path': recording.file_path,
                'file_size': recording.file_size,
                'duration_seconds': recording.duration_seconds,
                'transcription_status': recording.transcription_status,
                'created_at': recording.created_at
            }
    
    @staticmethod
    def get_recordings_by_case(case_id: int):
        """Get all recordings for a case"""
        with get_db_session() as session:
            recordings = session.query(Recording).filter_by(
                case_id=case_id
            ).order_by(
                Recording.recording_date.desc()
            ).all()
            
            for recording in recordings:
                session.expunge(recording)
            
            return recordings
    
    @staticmethod
    def update_recording_transcript(recording_id: int, transcript: str):
        """Update recording with transcript"""
        with get_db_session() as session:
            recording = session.query(Recording).filter_by(
                recording_id=recording_id
            ).first()
            
            if recording:
                recording.transcript_text = transcript
                recording.transcription_status = 'completed'
                recording.transcription_completed_at = datetime.utcnow()
                session.commit()
    
    @staticmethod
    def update_recording_summary(recording_id: int, summary: str):
        """Update recording with summary"""
        with get_db_session() as session:
            recording = session.query(Recording).filter_by(
                recording_id=recording_id
            ).first()
            
            if recording:
                recording.summary_text = summary
                session.commit()


# Global case service instance
case_service = CaseService()