from groq import AsyncGroq
from .prompts import turn_generation_prompt
from ..db.repositories.evidence import get_by_agent
from ..db.repositories.transcript import get_by_debate
from ..db.repositories.agents import get_by_id
from  ..config import GROQ_API_KEY
from ..orchestration.scheduler import schedule_next

groq_client = AsyncGroq(api_key=GROQ_API_KEY)
MODEL_NAME = "llama-3.3-70b-versatile"

async def generate_turn(debate_id: str , decay_base: float = 0.8) :
    res = await schedule_next(debate_id , decay_base)
    agent_id = res["agent_id"]
    agent = await get_by_id(agent_id)
    agent_prompt = agent["system_prompt"]
    transcript_row = await get_by_debate(res["debate_id"],None,True)
    evidence = await get_by_agent(res["debate_id"])
    generation_prompt = turn_generation_prompt(res["topic"] , transcript_row , res["attack_candidates"] , res["defend_candidates"] , res["propose_available"] , evidence)
    response = await groq_client.chat.completions.create(
        model=MODEL_NAME
    )