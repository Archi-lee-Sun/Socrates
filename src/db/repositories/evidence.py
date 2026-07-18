from ..client import get_client
from .agents import get_by_name
from .debates import get_by_id

async def insert(debate_id: str, agent_name: str | None, source_url: str, content: str, embedding: list[float]) -> None:
    agent_id = None
    if agent_name is not None:
        agent = await get_by_name(agent_name)
        agent_id = agent["id"]

    await get_by_id(debate_id) 

    client = await get_client()
    await client.table("evidence").insert({
        "debate_id": debate_id,
        "agent_id": agent_id,
        "source_url": source_url,
        "content": content,
        "embedding": embedding
    }).execute()


async def get_by_agent(debate_id: str , agent_id: str) -> list[dict] :
    client = await get_client()

    response = await client.table("evidence") \
        .select("*") \
        .eq("debate_id" , debate_id) \
        .or_(f"agent_id.eq.{agent_id},agent_id.is.null") \
        .execute()
    
    return response.data

