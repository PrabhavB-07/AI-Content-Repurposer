from youtube_transcript_api import YouTubeTranscriptApi
import re


def get_video_id(url):
    patterns = [
        r"youtube\.com/watch\?v=([^&]+)",
        r"youtu\.be/([^?&]+)"
    ]

    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)

    return None


def get_transcript(url):
    video_id = get_video_id(url)

    if not video_id:
        return None

    transcript = YouTubeTranscriptApi.get_transcript(video_id)

    text = " ".join([item["text"] for item in transcript])

    return text