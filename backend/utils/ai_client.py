"""
ReplyGenius – AI Client (v2)
=============================
Priority order:
1. Groq  – llama-3.3-70b-versatile  (best free model, fast, very human-sounding)
2. Gemini – gemini-2.0-flash        (good fallback)
3. OpenRouter – llama-3.3-70b free  (last resort)

Why llama-3.3-70b over llama3-8b?
- 70B is MUCH better at casual, natural language
- 8B tends to be stiff and uses fancy words
- 70B understands context, platform vibe, and slang properly
"""

import os
import requests

# ── Config ──────────────────────────────────────────────────────────────────
GROQ_API_KEY       = os.environ.get("GROQ_API_KEY", "")
GEMINI_API_KEY     = os.environ.get("GEMINI_API_KEY", "")
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")

# !! IMPORTANT CHANGE: upgraded from llama3-8b → llama-3.3-70b
# This is the single biggest improvement for natural-sounding replies
GROQ_MODEL        = "llama-3.3-70b-versatile"   # Free on Groq, much smarter
GEMINI_MODEL      = "gemini-2.0-flash"           # Free tier
OPENROUTER_MODEL  = "meta-llama/llama-3.3-70b-instruct:free"  # Free


# ── System prompt – injected as "system" role, not inside user message ───────
# Keeping it short and direct works better than a long essay
SYSTEM_PROMPT = """You are a real person replying on social media.
Write exactly like a normal person would type — not like an AI, not like a corporate blog.
Use everyday words. Match the energy of the post.
Output ONLY the reply. No intro. No explanation. No quotes around it."""


# ── Main entry point ────────────────────────────────────────────────────────
def generate_reply(prompt: str) -> tuple[str, str | None]:
    errors = []

    if GROQ_API_KEY:
        result, err = call_groq(prompt)
        if result:
            return clean_output(result), None
        errors.append(f"Groq: {err}")

    if GEMINI_API_KEY:
        result, err = call_gemini(prompt)
        if result:
            return clean_output(result), None
        errors.append(f"Gemini: {err}")

    if OPENROUTER_API_KEY:
        result, err = call_openrouter(prompt)
        if result:
            return clean_output(result), None
        errors.append(f"OpenRouter: {err}")

    if not errors:
        return None, "No API keys configured. Add GROQ_API_KEY, GEMINI_API_KEY, or OPENROUTER_API_KEY to your .env file."

    return None, f"All AI providers failed. Details: {' | '.join(errors)}"


# ── Clean up common AI output artifacts ─────────────────────────────────────
def clean_output(text: str) -> str:
    """
    Models sometimes wrap output in quotes or add preambles like
    'Here is your reply:' — strip all of that.
    """
    text = text.strip()

    # Remove wrapping quotes
    if (text.startswith('"') and text.endswith('"')) or \
       (text.startswith("'") and text.endswith("'")):
        text = text[1:-1].strip()

    # Remove common AI preambles
    preambles = [
        "here's a reply:", "here is a reply:", "here's your reply:",
        "here is your reply:", "reply:", "response:", "my reply:",
        "sure!", "sure,", "of course!", "absolutely!",
        "here you go:", "here's one:", "here is one:",
    ]
    lower = text.lower()
    for p in preambles:
        if lower.startswith(p):
            text = text[len(p):].strip()
            break

    return text


# ── Groq ─────────────────────────────────────────────────────────────────────
def call_groq(prompt: str) -> tuple[str | None, str | None]:
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": GROQ_MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": prompt},
        ],
        "temperature": 0.9,      # slightly higher = more natural variation
        "max_tokens": 300,       # most good replies are short
        "top_p": 0.95,
        "frequency_penalty": 0.4,  # discourages repetitive/formal patterns
        "presence_penalty": 0.3,
    }

    try:
        r = requests.post(url, headers=headers, json=payload, timeout=20)
        r.raise_for_status()
        text = r.json()["choices"][0]["message"]["content"].strip()
        return (text or None), (None if text else "Empty response")
    except requests.exceptions.HTTPError as e:
        return None, f"HTTP {e.response.status_code}: {e.response.text[:200]}"
    except Exception as e:
        return None, str(e)


# ── Gemini ───────────────────────────────────────────────────────────────────
def call_gemini(prompt: str) -> tuple[str | None, str | None]:
    url = (
        f"https://generativelanguage.googleapis.com/v1beta/models/"
        f"{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"
    )
    payload = {
        "system_instruction": {"parts": [{"text": SYSTEM_PROMPT}]},
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.9,
            "maxOutputTokens": 300,
            "topP": 0.95,
        },
        "safetySettings": [
            {"category": "HARM_CATEGORY_HARASSMENT",        "threshold": "BLOCK_ONLY_HIGH"},
            {"category": "HARM_CATEGORY_HATE_SPEECH",       "threshold": "BLOCK_ONLY_HIGH"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_ONLY_HIGH"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_ONLY_HIGH"},
        ],
    }

    try:
        r = requests.post(url, json=payload, timeout=20)
        r.raise_for_status()
        text = (
            r.json()
             .get("candidates", [{}])[0]
             .get("content", {})
             .get("parts", [{}])[0]
             .get("text", "")
             .strip()
        )
        return (text or None), (None if text else "Empty response")
    except requests.exceptions.HTTPError as e:
        return None, f"HTTP {e.response.status_code}: {e.response.text[:200]}"
    except Exception as e:
        return None, str(e)


# ── OpenRouter ────────────────────────────────────────────────────────────────
def call_openrouter(prompt: str) -> tuple[str | None, str | None]:
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://replygenius.app",
        "X-Title": "ReplyGenius",
    }
    payload = {
        "model": OPENROUTER_MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": prompt},
        ],
        "temperature": 0.9,
        "max_tokens": 300,
        "frequency_penalty": 0.4,
    }

    try:
        r = requests.post(url, headers=headers, json=payload, timeout=25)
        r.raise_for_status()
        text = r.json()["choices"][0]["message"]["content"].strip()
        return (text or None), (None if text else "Empty response")
    except requests.exceptions.HTTPError as e:
        return None, f"HTTP {e.response.status_code}: {e.response.text[:200]}"
    except Exception as e:
        return None, str(e)
