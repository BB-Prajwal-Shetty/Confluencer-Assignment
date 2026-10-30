# Approach Document

## 1. How brand voice is analysed
The tool uses **prompt-based inference**, with an optional evidence boost:

1. The user gives a brand name, industry, campaign objective and product description (brand name or product description is required, the rest optional).
2. **Step 1 - Voice analysis prompt.** An LLM acts as a brand strategist and returns a structured JSON *voice profile*: tone adjectives, personality, target audience, content themes, language style (sentence length, language mix, emoji and hashtag habits), dos and don'ts, and 4 summary bullets.
3. For well-known brands the model uses what it knows of the brand's real social style. For unknown brands it infers a fitting voice from industry + products, and is told not to invent facts.
4. **Optional:** the user can paste real posts from the brand. These are treated as the strongest evidence of voice. I chose paste-in over scraping because X/Twitter's API and scraping are restricted, so pasting is more reliable and works for any platform.

## 2. How prompts and logic are structured
**Two-step prompt chain** rather than one big prompt:

- Step 1 produces the voice profile (low temperature, 0.4, for consistency).
- Step 2 receives the profile plus the inputs and writes the tweets (higher temperature, 0.9, for creativity).

Why split it: the voice profile acts as an explicit "style guide" that every tweet must follow, which keeps all 10 tweets consistent and makes the reasoning visible to the user (the summary bullets).

**Variety is enforced, not hoped for.** The prompt requires a fixed mix: 3 engaging, 2 promotional, 3 witty/meme, 2 informative. It also forbids repeated openings and repeated joke structures.

**Guardrails in code (`app/validation.py`).** Output must be valid JSON, exactly 10 tweets, each at most 280 characters, all unique, with the exact style mix. If any check fails, the problem is sent back to the model as feedback and it retries (up to 3 attempts). The prompt also forbids invented prices, discounts or statistics, since a real brand would never post made-up offers.

## 3. Tools used
- **Python + FastAPI** backend, plain **HTML/CSS/JS** frontend (no build step, easy to test)
- **LLM provider is swappable** through one environment variable: Gemini (free tier), Anthropic Claude or OpenAI
- **httpx** for API calls, **pytest** for the validation tests
- Deployed on **Render** (config included in `render.yaml`)
- A simple per-IP rate limit protects the API key on the public link

## 4. Possible improvements
- Fetch recent posts automatically through the official X API
- Let users regenerate a single tweet
- Add tone sliders (more humour, more formal) and image or thread suggestions
