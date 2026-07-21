from ..client import get_client

async def insert(debate_id: str, round: int, agent_id: str | None, node_id: str | None,
                  edge_id: str | None, content: str, accepted: bool) -> None:
    client = await get_client()

    await client.table("transcript").insert({
        "debate_id": debate_id,
        "round": round,
        "agent_id": agent_id,
        "node_id": node_id,
        "edge_id": edge_id,
        "content": content,
        "accepted": accepted
    }).execute()


async def get_by_debate(debate_id: str, agent_id: str | None = None,
                         accepted: bool | None = None) -> list[dict]:
    client = await get_client()

    query = (
        client.table("transcript")
        .select("*")
        .eq("debate_id", debate_id)
        .order("sequence", desc=False)
    )
    
    if agent_id is not None:
        query = query.eq("agent_id", agent_id)

    if accepted is not None:
        query = query.eq("accepted", accepted)

    response = await query.order("sequence").execute()
    return response.data


