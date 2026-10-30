import json
import os
import time
from collections import defaultdict
from pathlib import Path
from typing import Literal, Optional

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from . import llm, prompts
from .validation import check_tweets, check_voice, parse_json

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
app = FastAPI(title="Brand Tweet Generator")
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")


class BrandInput(BaseModel):
    brand_name: Optional[str] = Field(None, max_length=80)
    industry: Optional[str] = Field(None, max_length=80)
    objective: Literal["engagement", "promotion", "awareness", "education", "launch", "community"] = "engagement"
    products: Optional[str] = Field(None, max_length=1000)
    sample_posts: Optional[str] = Field(None, max_length=3000, description="Optional pasted posts to learn voice from")


# Very small in-memory rate limiter so a public link can't drain your API key.
_hits = defaultdict(list)


def rate_limit(ip: str):
    limit = int(os.getenv("RATE_LIMIT_PER_HOUR", "20"))
    now = time.time()
    _hits[ip] = [t for t in _hits[ip] if now - t < 3600]
    if len(_hits[ip]) >= limit:
        raise HTTPException(429, "Rate limit reached. Please try again in a while.")
    _hits[ip].append(now)


@app.get("/")
def home():
    return FileResponse(BASE_DIR / "static" / "index.html")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/api/generate")
async def generate(data: BrandInput, request: Request):
    rate_limit(request.client.host if request.client else "unknown")

    brand = (data.brand_name or "").strip()
    industry = (data.industry or "").strip()
    products = (data.products or "").strip()
    if not (brand or products):
        raise HTTPException(422, "Please provide a brand name or a short description of the products.")

    try:
        # Step 1: brand voice analysis
        voice_raw = await llm.complete(
            prompts.VOICE_SYSTEM,
            prompts.voice_prompt(brand, industry, data.objective, products, (data.sample_posts or "").strip()),
            temperature=0.4,
        )
        voice = parse_json(voice_raw)
        problem = check_voice(voice)
        if problem:
            raise HTTPException(502, problem)

        # Step 2: tweet generation, with up to 2 self-correcting retries
        voice_json = json.dumps(voice, ensure_ascii=False, indent=2)
        feedback, tweets = None, []
        for _ in range(3):
            raw = await llm.complete(
                prompts.TWEET_SYSTEM,
                prompts.tweet_prompt(brand, industry, data.objective, products, voice_json, feedback),
                temperature=0.9,
            )
            try:
                tweets, feedback = check_tweets(parse_json(raw))
            except ValueError:
                tweets, feedback = [], "Output was not valid JSON."
            if feedback is None:
                break
        if feedback is not None:
            raise HTTPException(502, f"Could not produce valid tweets: {feedback}")
    except llm.LLMError as e:
        raise HTTPException(502, str(e))
    except ValueError:
        raise HTTPException(502, "The model returned an unreadable response. Please try again.")

    return {"voice": voice, "tweets": tweets}
