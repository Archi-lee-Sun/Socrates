import json
from groq import AsyncGroq
from ..config import GROQ_API_KEY 
from .prompts import vagueness_check_prompt, variant_generation_prompt

groq_client = AsyncGroq(api_key=GROQ_API_KEY)
MODEL_NAME = "llama-3.3-70b-versatile"


async def check_topic_vagueness(raw_topic: str) -> dict:
    prompt = vagueness_check_prompt(raw_topic)

    response = await groq_client.chat.completions.create(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"}
    )

    raw_content = response.choices[0].message.content

    try:
        return json.loads(raw_content)
    except json.JSONDecodeError as e:
        raise RuntimeError(
            f"LLM returned invalid JSON during vagueness check.\n"
            f"Raw content: {raw_content}\n"
            f"Error detail: {e}"
        )


async def generate_topic_variants(raw_topic: str) -> list[str]:
    prompt = variant_generation_prompt(raw_topic)

    response = await groq_client.chat.completions.create(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"}
    )

    raw_content = response.choices[0].message.content

    try:
        data = json.loads(raw_content)
        return data.get("variants", [])
    except json.JSONDecodeError as e:
        raise RuntimeError(
            f"LLM returned invalid JSON during variant generation.\n"
            f"Raw content: {raw_content}\n"
            f"Error detail: {e}"
        )