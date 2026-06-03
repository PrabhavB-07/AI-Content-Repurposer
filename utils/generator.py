import os
import re

from dotenv import load_dotenv
from groq import Groq
from youtube_transcript_api import YouTubeTranscriptApi

load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)


def get_video_id(url):

    patterns = [
        r"v=([0-9A-Za-z_-]{11})",
        r"youtu\.be\/([0-9A-Za-z_-]{11})"
    ]

    for pattern in patterns:

        match = re.search(pattern, url)

        if match:
            return match.group(1)

    return None


def get_youtube_transcript(url):

    video_id = get_video_id(url)

    if not video_id:
        raise Exception("Invalid YouTube URL")

    try:

        transcript = YouTubeTranscriptApi().fetch(video_id)

        text = " ".join(
            [item.text for item in transcript]
        )

        return text

    except Exception as e:
        raise Exception(f"Transcript not available: {str(e)}")


def generate_content(
    user_input,
    tone
):
    content = user_input

    if (
        "youtube.com" in user_input
        or
        "youtu.be" in user_input
    ):

        try:

            content = get_youtube_transcript(
                user_input
            )

            content = content[:8000]

        except Exception as e:

            return f"""
INSTAGRAM:
Transcript Error: {str(e)}

LINKEDIN:
Transcript Error: {str(e)}

TWITTER:
Transcript Error: {str(e)}

BLOG:
Transcript Error: {str(e)}
"""

    prompt = f"""
You are a professional content repurposing expert.

Selected Tone:
{tone}

Make all content match this tone.

IMPORTANT:

Return response ONLY in this exact format.

INSTAGRAM:
<instagram post>

LINKEDIN:
<linkedin post>

TWITTER:
<twitter thread>

BLOG:
<blog post>

Do not add any extra headings.
Do not use markdown.
Do not use bold text.
Do not write anything outside these sections.

Content:

{content}
"""

    try:

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.7,
            max_tokens=1200
        )

        return response.choices[0].message.content

    except Exception as e:

        return f"""
INSTAGRAM:
ERROR: {str(e)}

LINKEDIN:
ERROR: {str(e)}

TWITTER:
ERROR: {str(e)}

BLOG:
ERROR: {str(e)}
"""