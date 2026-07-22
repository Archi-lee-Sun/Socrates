from groq import AsyncGroq
from .prompts import turn_generation_prompt
from ..db.repositories.evidence import get_by_agent
from ..db.repositories.transcript import get_by_debate
from ..db.repositories.agents import get_by_id
from ..db.repositories.debates import get_by_id as get_debate_by_id
from  ..config import GROQ_API_KEY
from ..orchestration.scheduler import schedule_next
import json

groq_client = AsyncGroq(api_key=GROQ_API_KEY)
MODEL_NAME = "llama-3.3-70b-versatile"

def _format_transcript(rows: list[dict] ,acting_agent_id: str, agent_names : dict[str , str]) -> str :
    res = ""
    for row in rows :
        label = "YOU" if row["agent_id"] == acting_agent_id else "OPPONENT"
        name = agent_names[row["agent_id"]]
        res += f"{label} ({name}) : {row['content']}\n"
    
    return res

def _format_evidence(rows: list[dict]) -> str:
    res = ""
    for row in rows:
        res += f"source_url : {row['source_url']} content : {row['content']} \n"
    return res

async def generate_turn(debate_id: str, decay_base: float = 0.8):
    res = await schedule_next(debate_id, decay_base)

    agent_id = res["agent_id"]
    opponent_id = res["opponent_id"]

    acting_agent = await get_by_id(agent_id)
    opponent_agent = await get_by_id(opponent_id)

    agent_names = {
        agent_id: acting_agent["name"],
        opponent_id: opponent_agent["name"]
    }
    agent_prompt = acting_agent["system_prompt"]

    transcript_row = await get_by_debate(debate_id, None, True)
    transcript = _format_transcript(transcript_row, agent_id, agent_names)

    evidence_row = await get_by_agent(debate_id, agent_id)
    evidence = _format_evidence(evidence_row)

    generation_prompt = turn_generation_prompt(
        res["topic"],
        transcript,
        res["attack_candidates"],
        res["defend_candidates"],
        res["propose_available"],
        evidence
    )

    response = await groq_client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": agent_prompt},
            {"role": "user", "content": generation_prompt}
        ],
        response_format={"type": "json_object"}
    )

    raw_content = response.choices[0].message.content

    try:
        return json.loads(raw_content)
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Failed to parse turn generation response: {e}\nRaw content: {raw_content}") from e