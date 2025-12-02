from openai import AsyncOpenAI
from worker.config import config
import logging

logger = logging.getLogger(__name__)

class AIService:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=config.OPENAI_API_KEY)

    async def generate_note_content(self, transcript: str) -> str:
        """
        Generates a structured study note from the transcript using GPT-4o.
        """
        system_prompt = """
        You are an expert tutor. Your goal is to create a perfect study guide from a video transcript.
        
        Output Format: Markdown.
        Structure:
        # [Title]
        ## Overview
        (3 lines summary)
        ## Key Concepts
        (Detailed explanation with H3 headers)
        ## Vocabulary
        (Table of important terms)
        ## Quiz
        (3 multiple choice questions in Toggle format if possible, or just Q&A)
        """
        
        user_prompt = f"Here is the transcript:\n\n{transcript[:20000]}" # Truncate for safety if too long, though 4o context is large.

        try:
            response = await self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.2
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Failed to generate note content: {e}")
            raise

    async def generate_diagram(self, content: str) -> str:
        """
        Generates a Mermaid diagram based on the note content.
        """
        system_prompt = """
        Create a Mermaid.js diagram that visualizes the key concepts of the provided text.
        Return ONLY the mermaid code block, e.g.:
        ```mermaid
        graph TD
        A --> B
        ```
        """
        
        try:
            response = await self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": content[:10000]}
                ],
                temperature=0.0
            )
            # Extract code block if wrapped
            raw = response.choices[0].message.content
            if "```mermaid" in raw:
                return raw.split("```mermaid")[1].split("```")[0].strip()
            if "```" in raw:
                return raw.split("```")[1].split("```")[0].strip()
            return raw
        except Exception as e:
            logger.error(f"Failed to generate diagram: {e}")
            # Return empty or error string, don't fail the whole job
            return ""

ai_service = AIService()
