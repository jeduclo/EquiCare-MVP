"""
User service
Business logic for managing users
"""

from datetime import datetime
from src.database.db_manager import get_db_session
from src.database.models import User
from src.auth.password_utils import hash_password, validate_password_strength


class UserService:
    """Service for managing users"""
    
    @staticmethod
    def create_user(username: str, password: str, role: str, full_name: str = None, email: str = None):
        """
        Create a new user
        
        Args:
            username: Username (must be unique)
            password: Plain text password
            role: User role (social_worker or administrator)
            full_name: Optional full name
            email: Optional email
            
        Returns:
            dict with success status and message
        """
        # Validate password strength
        is_valid, error_msg = validate_password_strength(password)
        if not is_valid:
            return {
                'success': False,
                'error': error_msg
            }
        
        with get_db_session() as session:
            # Check if username exists
            existing_user = session.query(User).filter_by(username=username).first()
            if existing_user:
                return {
                    'success': False,
                    'error': f'Username "{username}" already exists'
                }
            
            # Create user
            new_user = User(
                username=username,
                password_hash=hash_password(password),
                role=role,
                full_name=full_name,
                email=email,
                is_active=True,
                created_at=datetime.utcnow(),
                failed_login_attempts=0
            )
            
            session.add(new_user)
            session.commit()
            
            return {
                'success': True,
                'message': f'User "{username}" created successfully',
                'user_id': new_user.user_id
            }
    
    @staticmethod
    def get_all_users():
        """Get all users"""
        with get_db_session() as session:
            users = session.query(User).order_by(User.created_at.desc()).all()
            
            # Convert to dicts
            user_list = []
            for user in users:
                user_list.append({
                    'user_id': user.user_id,
                    'username': user.username,
                    'role': user.role,
                    'full_name': user.full_name,
                    'email': user.email,
                    'is_active': user.is_active,
                    'created_at': user.created_at,
                    'last_login': user.last_login
                })
            
            return user_list
    
    @staticmethod
    def deactivate_user(user_id: int):
        """
        Deactivate a user (don't delete for audit trail)
        
        Args:
            user_id: User ID to deactivate
            
        Returns:
            dict with success status
        """
        with get_db_session() as session:
            user = session.query(User).filter_by(user_id=user_id).first()
            
            if not user:
                return {
                    'success': False,
                    'error': 'User not found'
                }
            
            user.is_active = False
            session.commit()
            
            return {
                'success': True,
                'message': f'User "{user.username}" deactivated'
            }
    
    @staticmethod
    def activate_user(user_id: int):
        """
        Reactivate a user
        
        Args:
            user_id: User ID to activate
            
        Returns:
            dict with success status
        """
        with get_db_session() as session:
            user = session.query(User).filter_by(user_id=user_id).first()
            
            if not user:
                return {
                    'success': False,
                    'error': 'User not found'
                }
            
            user.is_active = True
            user.failed_login_attempts = 0
            user.locked_until = None
            session.commit()
            
            return {
                'success': True,
                'message': f'User "{user.username}" activated'
            }
    
    @staticmethod
    def reset_password(user_id: int, new_password: str):
        """
        Reset a user's password (admin function)
        
        Args:
            user_id: User ID
            new_password: New password
            
        Returns:
            dict with success status
        """
        # Validate password strength
        is_valid, error_msg = validate_password_strength(new_password)
        if not is_valid:
            return {
                'success': False,
                'error': error_msg
            }
        
        with get_db_session() as session:
            user = session.query(User).filter_by(user_id=user_id).first()
            
            if not user:
                return {
                    'success': False,
                    'error': 'User not found'
                }
            
            user.password_hash = hash_password(new_password)
            user.failed_login_attempts = 0
            user.locked_until = None
            session.commit()
            
            return {
                'success': True,
                'message': f'Password reset for "{user.username}"'
            }
    
    @staticmethod
    def change_own_password(user_id: int, current_password: str, new_password: str):
        """
        Change user's own password
        
        Args:
            user_id: User ID
            current_password: Current password for verification
            new_password: New password
            
        Returns:
            dict with success status
        """
        from src.auth.password_utils import verify_password
        
        # Validate new password strength
        is_valid, error_msg = validate_password_strength(new_password)
        if not is_valid:
            return {
                'success': False,
                'error': error_msg
            }
        
        with get_db_session() as session:
            user = session.query(User).filter_by(user_id=user_id).first()
            
            if not user:
                return {
                    'success': False,
                    'error': 'User not found'
                }
            
            # Verify current password
            if not verify_password(current_password, user.password_hash):
                return {
                    'success': False,
                    'error': 'Current password is incorrect'
                }
            
            # Update password
            user.password_hash = hash_password(new_password)
            session.commit()
            
            return {
                'success': True,
                'message': 'Password changed successfully'
            }
    
    @staticmethod
    def get_user_stats():
        """Get user statistics"""
        with get_db_session() as session:
            total_users = session.query(User).count()
            active_users = session.query(User).filter_by(is_active=True).count()
            social_workers = session.query(User).filter_by(role='social_worker', is_active=True).count()
            administrators = session.query(User).filter_by(role='administrator', is_active=True).count()
            
            return {
                'total_users': total_users,
                'active_users': active_users,
                'social_workers': social_workers,
                'administrators': administrators
            }


# Global user service instance
user_service = UserService()