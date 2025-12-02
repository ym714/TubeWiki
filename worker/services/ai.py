from openai import AsyncOpenAI
from worker.config import config
import logging

logger = logging.getLogger(__name__)

class AIService:
    def __init__(self):
        if config.GROQ_API_KEY:
            self.client = AsyncOpenAI(
                api_key=config.GROQ_API_KEY,
                base_url="https://api.groq.com/openai/v1"
            )
            self.model = "llama-3.3-70b-versatile"
        else:
            logger.warning("GROQ_API_KEY not found. AI features will fail.")
            self.client = None
            self.model = None

    async def generate_note_content(self, transcript: str) -> str:
        if not self.client:
            raise ValueError("GROQ_API_KEY is missing")

        prompt = f"""
        You are an expert study assistant. Create a comprehensive study guide from the following YouTube transcript.
        The output must be in Markdown format.
        
        Structure:
        # Title
        ## Summary
        (Brief summary of the video)
        ## Key Concepts
        (Bulleted list of key points)
        ## Detailed Notes
        (In-depth explanation of the content)
        ## Quiz
        (3 multiple choice questions. Format each question using HTML <details> tags so the answer is hidden by default.
        Example:
        <details>
        <summary>Question 1: ...</summary>
        Answer: ...
        </details>
        )

        Transcript:
        {transcript[:15000]} 
        """
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Groq generation failed: {e}")
            raise

    async def generate_diagram(self, content: str) -> str:
        if not self.client:
            raise ValueError("GROQ_API_KEY is missing")

        prompt = f"""
        Create a Mermaid.js diagram code that visualizes the key concepts from the following study guide.
        Return ONLY the mermaid code block (e.g. graph TD...). Do not include markdown backticks.
        
        Study Guide:
        {content[:5000]}
        """

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Groq diagram generation failed: {e}")
            # Return empty or None if diagram fails, don't fail the whole job
            return None

ai_service = AIService()
