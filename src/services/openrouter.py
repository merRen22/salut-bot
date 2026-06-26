import asyncio
import os
from typing import Any

import httpx

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"


SYSTEM_PROMPT = """You are a French language tutor. Analyze the user's French message and provide:
1. **Corrections** — Fix grammar, conjugation, spelling, and word choice errors.
2. **Explanations** — Briefly explain *why* each change was made (e.g., gender agreement, verb tense, preposition usage). Keep explanations concise.
3. **Vocabulary Boost** — Suggest 1-3 more precise or natural French synonyms or phrases the user could have used instead.

Format your response in clear sections labeled "Corrections", "Explanations", and "Vocabulary Boost".
If the message has no errors, say "Votre français est excellent! Pas de corrections nécessaires." and skip the other sections."""


async def analyze_french(text: str) -> dict[str, Any]:
    api_key = os.getenv("OPEN_ROUTER_API_KEY")
    if not api_key:
        return {"error": "OPEN_ROUTER_API_KEY not set"}

    for attempt in range(4):
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(
                OPENROUTER_URL,
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": "openrouter/free",
                    "messages": [
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": text},
                    ],
                    "reasoning": {"enabled": False},
                },
            )
            if response.status_code == 429 and attempt < 3:
                await asyncio.sleep(2 ** attempt)
                continue
            response.raise_for_status()
            data = response.json()
            content = data["choices"][0]["message"]["content"]
            return {"analysis": content}
