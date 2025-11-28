"""
Audio service
Handles audio file storage, encryption, and management
"""

import os
from pathlib import Path
from datetime import datetime
from cryptography.fernet import Fernet
from src.config.settings import Settings
import wave
import struct


class AudioService:
    """Service for managing audio files"""
    
    def __init__(self):
        """Initialize audio service"""
        self.audio_dir = Settings.AUDIO_DIR
        self.encryption_key = self._get_or_create_encryption_key()
        self.cipher = Fernet(self.encryption_key)
    
    def _get_or_create_encryption_key(self):
        """Get or create encryption key for audio files"""
        key_file = Settings.DATA_DIR / "audio_encryption.key"
        
        if key_file.exists():
            with open(key_file, 'rb') as f:
                return f.read()
        else:
            # Create new key
            key = Fernet.generate_key()
            with open(key_file, 'wb') as f:
                f.write(key)
            return key
    
    def save_audio(self, audio_bytes: bytes, case_id: int, user_id: int) -> dict:
        """
        Save audio file to disk with encryption
        
        Args:
            audio_bytes: Raw audio data
            case_id: Database case ID
            user_id: User who uploaded the file
            
        Returns:
            dict with file_path, file_size, duration_seconds
        """
        
        # Generate unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"case_{case_id}_user_{user_id}_{timestamp}.enc"
        file_path = self.audio_dir / filename
        
        # Encrypt audio data
        encrypted_data = self.cipher.encrypt(audio_bytes)
        
        # Save to disk
        with open(file_path, 'wb') as f:
            f.write(encrypted_data)
        
        # Get file size
        file_size = os.path.getsize(file_path)
        
        # Try to calculate duration (for WAV files)
        duration = self._calculate_duration(audio_bytes)
        
        return {
            'file_path': str(file_path.relative_to(Settings.ROOT_DIR)),
            'file_size': file_size,
            'duration_seconds': duration
        }
    
    def _calculate_duration(self, audio_bytes: bytes) -> float:
        """
        Calculate audio duration in seconds
        
        Args:
            audio_bytes: Raw audio data
            
        Returns:
            Duration in seconds, or None if cannot determine
        """
        try:
            # Try to parse as WAV file
            # WAV header is 44 bytes
            if len(audio_bytes) < 44:
                return None
            
            # Check if it's a WAV file (RIFF header)
            if audio_bytes[:4] != b'RIFF' or audio_bytes[8:12] != b'WAVE':
                # Not a WAV file, estimate based on file size
                # Assume 16kHz, 16-bit, mono
                bytes_per_second = 16000 * 2  # 16kHz * 2 bytes
                return len(audio_bytes) / bytes_per_second
            
            # Parse WAV header
            sample_rate = struct.unpack('<I', audio_bytes[24:28])[0]
            byte_rate = struct.unpack('<I', audio_bytes[28:32])[0]
            
            # Calculate duration
            data_size = len(audio_bytes) - 44  # Subtract header
            duration = data_size / byte_rate
            
            return round(duration, 2)
            
        except Exception:
            # If we can't calculate, estimate based on file size
            bytes_per_second = 16000 * 2
            return round(len(audio_bytes) / bytes_per_second, 2)
    
    def load_audio(self, file_path: str) -> bytes:
        """
        Load and decrypt audio file
        
        Args:
            file_path: Path to encrypted audio file
            
        Returns:
            Decrypted audio bytes
        """
        full_path = Settings.ROOT_DIR / file_path
        
        with open(full_path, 'rb') as f:
            encrypted_data = f.read()
        
        # Decrypt
        audio_bytes = self.cipher.decrypt(encrypted_data)
        
        return audio_bytes
    
    def delete_audio(self, file_path: str):
        """
        Delete audio file from disk
        
        Args:
            file_path: Path to audio file
        """
        full_path = Settings.ROOT_DIR / file_path
        
        if full_path.exists():
            full_path.unlink()
    
    def get_audio_info(self, file_path: str) -> dict:
        """
        Get information about an audio file
        
        Args:
            file_path: Path to audio file
            
        Returns:
            dict with file info
        """
        full_path = Settings.ROOT_DIR / file_path
        
        if not full_path.exists():
            return None
        
        file_size = os.path.getsize(full_path)
        
        return {
            'file_path': file_path,
            'file_size': file_size,
            'exists': True
        }


# Global audio service instance
audio_service = AudioService()