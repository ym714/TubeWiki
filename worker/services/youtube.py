from youtube_transcript_api import YouTubeTranscriptApi
from urllib.parse import urlparse, parse_qs
import logging

logger = logging.getLogger(__name__)

class YouTubeService:
    def extract_video_id(self, url: str) -> str:
        """
        Extracts video ID from various YouTube URL formats.
        """
        parsed = urlparse(url)
        if parsed.hostname == 'youtu.be':
            return parsed.path[1:]
        if parsed.hostname in ('www.youtube.com', 'youtube.com'):
            if parsed.path == '/watch':
                p = parse_qs(parsed.query)
                return p['v'][0]
            if parsed.path[:7] == '/embed/':
                return parsed.path.split('/')[2]
            if parsed.path[:3] == '/v/':
                return parsed.path.split('/')[2]
        # Fail safe or raise error
        raise ValueError(f"Invalid YouTube URL: {url}")

    def get_transcript(self, video_url: str) -> str:
        try:
            video_id = self.extract_video_id(video_url)
            # Instantiate API (Required in this env)
            yt = YouTubeTranscriptApi()
            
            # Use .list() instead of .list_transcripts()
            transcript_list = yt.list(video_id)
            
            # Filter: prefer 'ja', then 'en'
            try:
                transcript = transcript_list.find_transcript(['ja', 'en'])
            except:
                # If manual not found, try generated
                try:
                    transcript = transcript_list.find_generated_transcript(['ja', 'en'])
                except:
                    # Fallback to the first available
                    transcript = next(iter(transcript_list))
            
            # Fetch the actual data
            data = transcript.fetch()
            
            # Combine text
            parts = []
            for t in data:
                if hasattr(t, 'text'):
                    parts.append(t.text)
                elif isinstance(t, dict) and 'text' in t:
                    parts.append(t['text'])
            
            full_text = " ".join(parts)
            return full_text
        except Exception as e:
            logger.error(f"Failed to fetch transcript for {video_url}: {e}")
            raise

youtube_service = YouTubeService()
