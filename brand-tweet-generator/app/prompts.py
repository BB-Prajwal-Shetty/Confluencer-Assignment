"""Prompt templates for the two-step chain: (1) analyse brand voice, (2) write tweets."""

# Fixed mix so every run has variety: 3 + 2 + 3 + 2 = 10
TWEET_MIX = {
    "engaging": 3,      # conversational, asks a question, invites replies
    "promotional": 2,   # pushes the product/offer, aligned with campaign objective
    "witty": 3,         # humour / meme-style / relatable moments
    "informative": 2,   # tip, fact, how-to, value-driven
}

VOICE_SYSTEM = """You are a senior brand strategist who decodes how brands sound on social media.
Return ONLY valid JSON. No markdown, no commentary."""


def voice_prompt(brand, industry, objective, products, sample_posts):
    return f"""Infer the social media brand voice for the brand below.

BRAND NAME: {brand or "not provided"}
INDUSTRY: {industry or "not provided"}
CAMPAIGN OBJECTIVE: {objective}
PRODUCTS / ABOUT: {products or "not provided"}
SAMPLE POSTS FROM THE BRAND (may be empty):
{sample_posts or "none provided - rely on what you know about the brand and the inputs above"}

Rules:
- If sample posts are given, treat them as the strongest evidence of voice.
- If the brand is well known, use what you know of its real tweeting style (language, emoji use, humour level).
- If it is unknown or no name is given, infer a fitting voice from industry + products and do not invent facts.

Return JSON with exactly these keys:
{{
  "tone": ["3-4 adjectives, e.g. witty, bold, warm"],
  "personality": "one sentence describing the brand as a person",
  "target_audience": "who they talk to (age, interests, mindset)",
  "content_themes": ["4-6 themes: offers, product features, trends, memes, education, etc."],
  "language_style": "sentence length, slang or language mix, emoji usage, hashtag habits, capitalisation",
  "dos": ["3 things this brand's tweets always do"],
  "donts": ["3 things this brand would never do"],
  "summary_bullets": ["exactly 4 short bullets summarising the voice for a human reader"]
}}"""


TWEET_SYSTEM = """You are the in-house social media writer for the brand described. You write tweets that
sound like the brand, not like an AI. Return ONLY valid JSON. No markdown, no commentary."""


def tweet_prompt(brand, industry, objective, products, voice_json, feedback=None):
    mix = "\n".join(f"- {n} x {style}" for style, n in TWEET_MIX.items())
    fix = f"\nPREVIOUS ATTEMPT PROBLEM (fix this): {feedback}\n" if feedback else ""
    return f"""Write exactly 10 tweets for this brand.

BRAND NAME: {brand or "not provided"}
INDUSTRY: {industry or "not provided"}
CAMPAIGN OBJECTIVE: {objective}
PRODUCTS / ABOUT: {products or "not provided"}

BRAND VOICE PROFILE (follow it closely):
{voice_json}

REQUIRED MIX:
{mix}

Style definitions:
- engaging: conversational, relatable, ends in a question or invites replies
- promotional: highlights the product/offer, clear but not pushy, supports the campaign objective
- witty: humour, meme-style or relatable-moment tweets in the brand's own humour level
- informative: a useful tip, fact or how-to that gives value

Hard rules:
- Each tweet is 280 characters or fewer.
- Every tweet must sound like the same brand, matching its language style, emoji and hashtag habits.
- No two tweets may open the same way or reuse the same joke structure.
- Do not invent prices, discounts, statistics, awards or launch dates. Keep offers generic unless given in the input.
- Do not copy real tweets or slogans word for word.
- Hashtags: use at most 1 per tweet and only if the brand style uses them.
{fix}
Return JSON exactly like:
{{"tweets": [{{"style": "engaging|promotional|witty|informative", "text": "..."}}]}}"""
