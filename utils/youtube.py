import re
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import (
    TranscriptsDisabled,
    NoTranscriptFound,
    VideoUnavailable,
)


def get_video_id(url: str) -> str | None:
    patterns = [
        r"youtube\.com/watch\?v=([0-9A-Za-z_-]{11})",
        r"youtu\.be/([0-9A-Za-z_-]{11})",
        r"youtube\.com/shorts/([0-9A-Za-z_-]{11})",
        r"youtube\.com/embed/([0-9A-Za-z_-]{11})",
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None


def get_transcript(url: str) -> str:
    video_id = get_video_id(url)
    if not video_id:
        raise Exception("Invalid YouTube URL — video ID nahi mila.")

    yt = YouTubeTranscriptApi()

    # ── Try 1: English transcript ──
    try:
        transcript = yt.fetch(video_id, languages=["en"])
        return _join(transcript)
    except Exception:
        pass

    # ── Try 2: Hindi transcript ──
    try:
        transcript = yt.fetch(video_id, languages=["hi"])
        return _join(transcript)
    except Exception:
        pass

    # ── Try 3: Auto-generated (any language) ──
    try:
        transcript_list = yt.list(video_id)
        for t in transcript_list:
            try:
                fetched = t.fetch()
                return _join(fetched)
            except Exception:
                continue
    except TranscriptsDisabled:
        raise Exception(
            "Is video pe transcripts disabled hain. "
            "Koi aur video try karo ya seedha topic paste karo."
        )
    except VideoUnavailable:
        raise Exception(
            "Video unavailable hai — private ya deleted ho sakta hai."
        )
    except NoTranscriptFound:
        raise Exception(
            "Is video ka koi transcript available nahi hai. "
            "Seedha topic/article paste karo instead."
        )
    except Exception as e:
        raise Exception(
            f"YouTube se transcript fetch nahi hua: {str(e)}\n\n"
            "💡 Fix: Seedha topic paste karo jaise — 'Python for beginners'"
        )

    raise Exception(
        "Koi bhi transcript nahi mila. "
        "Seedha topic ya article text paste karo."
    )


def _join(transcript) -> str:
    """Transcript object se clean text banao."""
    try:
        # New API — object with .text attribute
        return " ".join(item.text for item in transcript)
    except AttributeError:
        # Old API — dict list
        return " ".join(item["text"] for item in transcript)