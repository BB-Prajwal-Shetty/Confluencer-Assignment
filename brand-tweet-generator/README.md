# Brand Tweet Generator

An AI tool that takes a brand name, industry, campaign objective and product details, infers the brand's social media voice, and generates **10 on-brand tweets** (engaging, promotional, witty/meme, informative) with a short brand voice summary.

- Approach write-up: [APPROACH.md](APPROACH.md)
- Example outputs for 2 brands with very different tones: [examples/zomato.md](examples/zomato.md), [examples/tanishq.md](examples/tanishq.md)
- Live link: **ADD YOUR RENDER URL HERE AFTER DEPLOYING**

## Run locally

```bash
python -m venv venv
# Windows: venv\Scripts\activate    Mac/Linux: source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env        # Windows: copy .env.example .env
# open .env and paste your API key
uvicorn app.main:app --reload
```
Open http://127.0.0.1:8000

### Getting an API key (pick one)
- **Gemini (free tier):** https://aistudio.google.com/apikey -> set `LLM_PROVIDER=gemini` and `GEMINI_API_KEY`
- **Anthropic:** set `LLM_PROVIDER=anthropic` and `ANTHROPIC_API_KEY`
- **OpenAI:** set `LLM_PROVIDER=openai` and `OPENAI_API_KEY`

If a model name is rejected, set `GEMINI_MODEL`, `ANTHROPIC_MODEL` or `OPENAI_MODEL` in `.env` to one currently available on your account.

## Run tests
```bash
pytest
```

## Deploy for a live link (Render, free)
1. Push this repo to GitHub (see below).
2. On https://render.com choose **New > Web Service** and connect the repo.
3. Build command: `pip install -r requirements.txt`
   Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   (`render.yaml` already contains these.)
4. Under **Environment**, add `LLM_PROVIDER` and the matching API key.
5. Deploy, then paste the URL into the "Live link" line above and into your submission email.

Never commit your `.env` file. It is already in `.gitignore`.

## Push to GitHub
```bash
git init
git add .
git commit -m "Brand tweet generator"
git branch -M main
git remote add origin https://github.com/<your-username>/<repo-name>.git
git push -u origin main
```

## Project structure
```
app/main.py         FastAPI app, two-step pipeline, rate limit
app/prompts.py      Voice-analysis and tweet-writing prompts
app/llm.py          Gemini / Anthropic / OpenAI client
app/validation.py   JSON parsing and output checks (10 tweets, 280 chars, style mix)
static/index.html   Input form and results UI
tests/              Unit tests for validation
examples/           Sample outputs for 2 brands
```
