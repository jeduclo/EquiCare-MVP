"""
Transcription service
Handles audio transcription using OpenAI Whisper
"""

import logging
from openai import OpenAI
from src.config.settings import Settings
from src.services.audio_service import audio_service
from src.services.case_service import case_service

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TranscriptionService:
    """Service for transcribing audio files using OpenAI Whisper"""
    
    def __init__(self):
        """Initialize OpenAI client"""
        self.client = OpenAI(api_key=Settings.OPENAI_API_KEY)
        self.model = Settings.AI_TRANSCRIPTION_MODEL
    
    def transcribe_recording(self, recording_id: int, file_path: str) -> dict:
        """
        Transcribe an audio recording
        
        Args:
            recording_id: Recording ID in database
            file_path: Path to encrypted audio file
            
        Returns:
            dict with transcript text and metadata
        """
        try:
            logger.info(f"Starting transcription for recording {recording_id}")
            
            # Update status to processing
            from src.database.db_manager import get_db_session
            from src.database.models import Recording
            from datetime import datetime
            
            with get_db_session() as session:
                recording = session.query(Recording).filter_by(recording_id=recording_id).first()
                if recording:
                    recording.transcription_status = 'processing'
                    recording.transcription_started_at = datetime.utcnow()
                    session.commit()
            
            # Load and decrypt audio
            logger.info("Loading audio file...")
            audio_bytes = audio_service.load_audio(file_path)
            
            # Save to temporary file for Whisper API
            import tempfile
            import os
            
            with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
                temp_file.write(audio_bytes)
                temp_path = temp_file.name
            
            try:
                # Call Whisper API
                logger.info("Calling OpenAI Whisper API...")
                with open(temp_path, 'rb') as audio_file:
                    transcript = self.client.audio.transcriptions.create(
                        model=self.model,
                        file=audio_file,
                        response_format="verbose_json",
                        timestamp_granularities=["segment"]
                    )
                
                # Extract transcript text
                transcript_text = transcript.text
                
                # Format with timestamps if available
                if hasattr(transcript, 'segments') and transcript.segments:
                    formatted_transcript = self._format_transcript_with_timestamps(transcript.segments)
                else:
                    formatted_transcript = transcript_text
                
                logger.info(f"Transcription completed: {len(transcript_text)} characters")
                
                # Update database with completed transcript
                case_service.update_recording_transcript(recording_id, formatted_transcript)
                
                return {
                    'success': True,
                    'transcript': formatted_transcript,
                    'text_only': transcript_text,
                    'word_count': len(transcript_text.split()),
                    'duration': getattr(transcript, 'duration', None)
                }
                
            finally:
                # Clean up temp file
                os.unlink(temp_path)
        
        except Exception as e:
            logger.error(f"Transcription failed for recording {recording_id}: {str(e)}")
            
            # Update status to failed
            from src.database.db_manager import get_db_session
            from src.database.models import Recording
            
            with get_db_session() as session:
                recording = session.query(Recording).filter_by(recording_id=recording_id).first()
                if recording:
                    recording.transcription_status = 'failed'
                    session.commit()
            
            return {
                'success': False,
                'error': str(e)
            }
    
    def _format_transcript_with_timestamps(self, segments) -> str:
        """
        Format transcript with timestamps
        
        Args:
            segments: Whisper segments with timestamps
            
        Returns:
            Formatted transcript string
        """
        formatted_lines = []
        
        for segment in segments:
            # Access as attributes, not dict keys
            start_time = self._format_timestamp(segment.start)
            text = segment.text.strip()
            formatted_lines.append(f"[{start_time}] {text}")
        
        return "\n\n".join(formatted_lines)
    
    def _format_timestamp(self, seconds: float) -> str:
        """
        Format seconds as MM:SS
        
        Args:
            seconds: Time in seconds
            
        Returns:
            Formatted string
        """
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes:02d}:{secs:02d}"


# Global transcription service instance
transcription_service = TranscriptionService()