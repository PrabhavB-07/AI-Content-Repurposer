import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def _is_youtube(text: str) -> bool:
    return "youtube.com" in text or "youtu.be" in text


def _error_result(msg: str) -> str:
    return (
        f"INSTAGRAM:\n{msg}\n"
        f"LINKEDIN:\n{msg}\n"
        f"TWITTER:\n{msg}\n"
        f"BLOG:\n{msg}"
    )


def generate_content(user_input: str, tone: str) -> str:

    if _is_youtube(user_input):
        return _error_result(
            "YouTube URLs are not supported in the hosted version.\n\n"
            "Please copy the video description or paste the topic directly.\n\n"
            "Example: 'How to learn Python programming from scratch'"
        )

    content = user_input.strip()

    if not content:
        return _error_result("Please enter a topic or paste your article text.")

    prompt = f"""You are a professional content repurposing expert.

Tone: {tone}
Make ALL content match this tone exactly.

STRICT FORMAT RULES:
- Return ONLY the 4 sections below
- No markdown, no bold, no extra headings
- No text outside these 4 sections
- Each section must have real, high quality content

INSTAGRAM:
<write instagram post with emojis and hashtags>
LINKEDIN:
<write professional linkedin post>
TWITTER:
<write twitter thread, number each tweet like 1/, 2/, 3/>
BLOG:
<write full blog post with intro, body and conclusion>

Content to repurpose:
{content}
"""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.75,
            max_tokens=2000,
        )
        return response.choices[0].message.content

    except Exception as e:
        return _error_result(f"AI generation failed: {str(e)}")