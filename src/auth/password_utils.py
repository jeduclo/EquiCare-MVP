"""
Password utilities for secure password hashing and verification
"""

import bcrypt


def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt
    
    Args:
        password: Plain text password
        
    Returns:
        Hashed password as string
    """
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')


def verify_password(password: str, password_hash: str) -> bool:
    """
    Verify a password against its hash
    
    Args:
        password: Plain text password to verify
        password_hash: Stored password hash
        
    Returns:
        True if password matches, False otherwise
    """
    password_bytes = password.encode('utf-8')
    hash_bytes = password_hash.encode('utf-8')
    return bcrypt.checkpw(password_bytes, hash_bytes)


def validate_password_strength(password: str) -> tuple[bool, str]:
    """
    Validate password meets minimum requirements
    
    Args:
        password: Password to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    from src.config.settings import Settings
    
    if len(password) < Settings.PASSWORD_MIN_LENGTH:
        return False, f"Password must be at least {Settings.PASSWORD_MIN_LENGTH} characters"
    
    if not any(char.isdigit() for char in password):
        return False, "Password must contain at least one number"
    
    if not any(char in '!@#$%^&*()_+-=[]{}|;:,.<>?' for char in password):
        return False, "Password must contain at least one special character"
    
    return True, ""