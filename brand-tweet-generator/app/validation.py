"""Pure-Python helpers (no network) so they are easy to unit test."""
import json
import re
from collections import Counter

from .prompts import TWEET_MIX

VALID_STYLES = set(TWEET_MIX)


def parse_json(text: str) -> dict:
    """Parse model output as JSON, tolerating ```json fences or stray text around it."""
    cleaned = re.sub(r"^```(?:json)?|```$", "", text.strip(), flags=re.MULTILINE).strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        start, end = cleaned.find("{"), cleaned.rfind("}")
        if start != -1 and end > start:
            return json.loads(cleaned[start : end + 1])
        raise


def check_tweets(data: dict):
    """Return (tweets, problem). problem is None when output is acceptable."""
    tweets = data.get("tweets") if isinstance(data, dict) else None
    if not isinstance(tweets, list):
        return [], "Output must be a JSON object with a 'tweets' list."
    clean = []
    for t in tweets:
        if isinstance(t, dict) and isinstance(t.get("text"), str) and t["text"].strip():
            style = str(t.get("style", "")).lower().strip()
            clean.append({"style": style if style in VALID_STYLES else "engaging", "text": t["text"].strip()})
    if len(clean) != 10:
        return clean, f"You returned {len(clean)} tweets; exactly 10 are required."
    too_long = [i + 1 for i, t in enumerate(clean) if len(t["text"]) > 280]
    if too_long:
        return clean, f"Tweets {too_long} exceed 280 characters. Shorten them."
    if len({t["text"].lower() for t in clean}) != 10:
        return clean, "Some tweets are duplicates. Every tweet must be unique."
    counts = Counter(t["style"] for t in clean)
    if counts != Counter(TWEET_MIX):
        return clean, f"Style mix was {dict(counts)}; required is {TWEET_MIX}."
    return clean, None


def check_voice(data: dict):
    needed = ["tone", "personality", "target_audience", "content_themes", "summary_bullets"]
    if not isinstance(data, dict):
        return "Voice profile must be a JSON object."
    missing = [k for k in needed if k not in data]
    if missing:
        return f"Voice profile missing keys: {missing}"
    return None
