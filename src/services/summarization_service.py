"""
Summarization service
Handles case note generation using GPT-4
"""

import logging
from openai import OpenAI
from src.config.settings import Settings
from src.services.case_service import case_service

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SummarizationService:
    """Service for generating case note summaries using GPT-4"""
    
    def __init__(self):
        """Initialize OpenAI client"""
        self.client = OpenAI(api_key=Settings.OPENAI_API_KEY)
        self.model = Settings.AI_SUMMARIZATION_MODEL
        self.max_tokens = Settings.AI_SUMMARIZATION_MAX_TOKENS
        self.temperature = Settings.AI_SUMMARIZATION_TEMPERATURE
    
    def generate_summary(self, recording_id: int, transcript: str, recording_type: str = None) -> dict:
        """
        Generate a case note summary from transcript
        
        Args:
            recording_id: Recording ID in database
            transcript: Transcript text
            recording_type: Type of recording (phone, home_visit, office)
            
        Returns:
            dict with summary text
        """
        try:
            logger.info(f"Starting summarization for recording {recording_id}")
            
            # Build prompt
            system_prompt = self._get_system_prompt()
            user_prompt = self._build_user_prompt(transcript, recording_type)
            
            # Call GPT-4
            logger.info("Calling OpenAI GPT-4 API...")
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )
            
            summary = response.choices[0].message.content.strip()
            
            logger.info(f"Summary generated: {len(summary)} characters")
            
            # Update database with summary
            case_service.update_recording_summary(recording_id, summary)
            
            return {
                'success': True,
                'summary': summary,
                'tokens_used': response.usage.total_tokens
            }
        
        except Exception as e:
            logger.error(f"Summarization failed for recording {recording_id}: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt for case note generation"""
        return """You are an expert social worker assistant specializing in writing professional case notes.

Your task is to generate clear, concise, and professional case notes from conversation transcripts.

Guidelines:
- Write in third person, professional tone
- Use clear, objective language
- Focus on facts and observations
- Organize information logically
- Include relevant context
- Highlight key points and action items
- Keep notes concise but comprehensive
- Use appropriate social work terminology

Structure your case notes with these sections:
1. **Overview**: Brief summary of the interaction
2. **Key Discussion Points**: Main topics covered
3. **Client Situation**: Current circumstances and concerns
4. **Decisions/Agreements**: What was decided or agreed upon
5. **Action Items**: Next steps and follow-up needed
6. **Risk Assessment** (if applicable): Any concerns or risks identified

Write professional case notes suitable for official records."""
    
    def _build_user_prompt(self, transcript: str, recording_type: str = None) -> str:
        """
        Build user prompt with transcript
        
        Args:
            transcript: Transcript text
            recording_type: Type of recording
            
        Returns:
            Formatted prompt
        """
        interaction_type = {
            'phone': 'phone call',
            'home_visit': 'home visit',
            'office': 'office meeting'
        }.get(recording_type, 'interaction')
        
        return f"""Please generate a professional case note from this {interaction_type} transcript:

---
TRANSCRIPT:
{transcript}
---

Generate a structured case note following the format specified in the system prompt."""
    
    def regenerate_summary(self, recording_id: int, transcript: str, custom_instructions: str = None) -> dict:
        """
        Regenerate summary with custom instructions
        
        Args:
            recording_id: Recording ID
            transcript: Transcript text
            custom_instructions: Custom instructions for regeneration
            
        Returns:
            dict with new summary
        """
        try:
            system_prompt = self._get_system_prompt()
            
            if custom_instructions:
                user_prompt = f"""Please generate a professional case note from this transcript.

CUSTOM INSTRUCTIONS: {custom_instructions}

---
TRANSCRIPT:
{transcript}
---

Generate the case note following the system instructions and custom instructions provided."""
            else:
                user_prompt = self._build_user_prompt(transcript)
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )
            
            summary = response.choices[0].message.content.strip()
            
            # Update database
            case_service.update_recording_summary(recording_id, summary)
            
            return {
                'success': True,
                'summary': summary,
                'tokens_used': response.usage.total_tokens
            }
        
        except Exception as e:
            logger.error(f"Summary regeneration failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }


# Global summarization service instance
summarization_service = SummarizationService()