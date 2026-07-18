from ..client import get_client

async def insert(debate_id: str, agent_id: str, node_id: str, type: str, round: int) -> None:
    client = await get_client()

    await client.table("cards").insert({
        "debate_id" : debate_id ,
        "agent_id" : agent_id ,
        "node_id" : node_id ,
        "type" : type ,
        "round" : round
    }).execute()


async def get_by_agent(debate_id: str, agent_id: str) -> list[dict] :
    client = await get_client()

    response = await client.table("cards") \
        .select("*") \
        .eq("debate_id" , debate_id) \
        .eq("agent_id", agent_id) \
        .execute()
    
    return response.data