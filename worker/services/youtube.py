from youtube_transcript_api import YouTubeTranscriptApi
from urllib.parse import urlparse, parse_qs

from shared.utils.logger import get_logger
from shared.utils.retry import with_retry, timeout
from shared.utils.exceptions import YouTubeAPIError, TranscriptNotAvailableError
from shared.utils.validators import validate_youtube_url

logger = get_logger(__name__)


class YouTubeService:
    def extract_video_id(self, url: str) -> str:
        """
        Extracts video ID from various YouTube URL formats.
        
        Args:
            url: YouTube URL
            
        Returns:
            Video ID
            
        Raises:
            InvalidYouTubeURLError: If URL is invalid
        """
        return validate_youtube_url(url)

    @with_retry(max_retries=3, initial_delay=1.0, exceptions=(Exception,))
    @timeout(30.0)
    async def get_transcript(self, video_url: str) -> str:
        """
        Fetch transcript for a YouTube video with retry and timeout.
        
        Args:
            video_url: YouTube video URL
            
        Returns:
            Full transcript text
            
        Raises:
            TranscriptNotAvailableError: If transcript is not available
            YouTubeAPIError: If YouTube API fails
        """
        try:
            video_id = self.extract_video_id(video_url)
            logger.info(f"Fetching transcript for video: {video_id}")
            
            # Get transcript list using static method
            try:
                transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            except Exception as e:
                # If listing fails, try direct fetch as fallback (sometimes works when list fails)
                logger.warning(f"list_transcripts failed, trying direct get_transcript: {e}")
                try:
                    # Try fetching ja, then en, then en-US
                    data = YouTubeTranscriptApi.get_transcript(video_id, languages=['ja', 'en', 'en-US'])
                    
                    # Helper to format data same as fetch()
                    full_text = " ".join([t['text'] for t in data])
                    logger.info(f"Successfully fetched transcript via fallback", extra={"video_id": video_id, "length": len(full_text)})
                    return full_text
                except Exception as direct_error:
                    raise e  # Raise the original list error if fallback also fails

            # Filter: prefer 'ja', then 'en'
            transcript = None
            try:
                # Try manual first
                transcript = transcript_list.find_manually_created_transcript(['ja', 'en', 'en-US'])
            except Exception:
                # Try generated
                try:
                    transcript = transcript_list.find_generated_transcript(['ja', 'en', 'en-US'])
                except Exception:
                    # Fallback to the first available
                    try:
                        transcript = next(iter(transcript_list))
                    except StopIteration:
                        raise TranscriptNotAvailableError(
                            video_id,
                            details={"reason": "No transcripts available"}
                        )
            
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
            
            logger.info(
                f"Successfully fetched transcript",
                extra={
                    "video_id": video_id,
                    "length": len(full_text)
                }
            )
            
            return full_text
            
        except TranscriptNotAvailableError:
            raise
        except Exception as e:
            logger.error(
                f"Failed to fetch transcript",
                extra={
                    "video_url": video_url,
                    "error": str(e)
                }
            )
            raise YouTubeAPIError(
                f"Failed to fetch transcript: {str(e)}",
                details={"video_url": video_url}
            )


youtube_service = YouTubeService()

