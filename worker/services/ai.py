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
        
        IMPORTANT: Output in the same language as the transcript (likely Japanese).

        Structure:
        # Title
        ## Summary
        (Provide a detailed and comprehensive summary of the video content, capturing the main narrative and arguments.)
        
        ## Key Concepts
        (List the most important concepts, terms, and ideas discussed. Use bullet points with brief explanations for each.)
        
        ## Detailed Notes
        (Provide an in-depth explanation of the content, organized by logical sections or topics. Include specific examples and details mentioned in the video.)
        
        ## Quiz
        (Create 3 multiple choice or short answer questions to test understanding. 
        Format:
        **Q1:** [Question]
        **A:** [Answer]
        )

        Transcript:
        {transcript[:15000]} 
        """
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant. You output in the same language as the input text."},
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
        
        RULES:
        1. Return ONLY the mermaid code block. Do not include markdown backticks (```).
        2. Use `graph TD` (Top-Down) orientation.
        3. Use alphanumeric node IDs (e.g., A, B, C) and put the text in quotes (e.g., A["Text"]).
        4. DO NOT use special characters or spaces in node IDs.
        5. Ensure the graph syntax is valid.
        6. The text inside quotes should be in the same language as the study guide (Japanese).

        Example:
        graph TD
        A["Main Concept"] --> B["Sub Concept 1"]
        A --> C["Sub Concept 2"]
        
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
