import asyncio
import os
import logging
import sys

logging.basicConfig(level=logging.INFO)


# Add project root to path
sys.path.append(os.getcwd())

from worker.services.youtube import youtube_service
from worker.services.ai import ai_service

async def main():
    video_url = "https://www.youtube.com/watch?v=a0qCbmFARlo"
    print(f"--- Testing with URL: {video_url} ---")

    # 1. Fetch Transcript
    print("\n[1] Fetching Transcript...")
    try:
        transcript = await youtube_service.get_transcript(video_url)
        print(f"Success! Transcript length: {len(transcript)} chars")
        print(f"Preview: {transcript[:200]}...")
    except Exception as e:
        print(f"Failed to fetch transcript: {e}")
        return

    # 2. AI Generation
    print("\n[2] Generating Summary (AI)...")
    if "GROQ_API_KEY" not in os.environ:
        print("GROQ_API_KEY not found. Skipping real AI call.")
        print("Simulating AI response...")
        content = "# Study Guide (Simulated)\n\nThis is a simulated summary because GROQ_API_KEY is missing in this shell."
        diagram = "graph TD; A[Start] --> B[End];"
    else:
        try:
            content = await ai_service.generate_note_content(transcript)
            diagram = await ai_service.generate_diagram(content)
            print("Success! AI Content generated.")
        except Exception as e:
            print(f"AI Generation failed: {e}")
            content = "Failed"
            diagram = None

    # 3. Output
    print("\n[3] Saving Output to output.md...")

    # Extract video ID for embed
    video_id = video_url.split("v=")[1]
    embed_html = f'<iframe width="560" height="315" src="https://www.youtube.com/embed/{video_id}" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>'

    final_output = f"# Video\n{embed_html}\n\n{content}\n\n## Diagram\n```mermaid\n{diagram}\n```"

    with open("output.md", "w") as f:
        f.write(final_output)

    print("Success! Saved to output.md")

if __name__ == "__main__":
    asyncio.run(main())
