from ..client import get_client

async def insert(debate_id: str, author_id: str, source_node_id: str,
                  target_node_id: str, type: str, round: int) -> dict:
    client = await get_client()
    response = await client.table("edges").insert({
        "debate_id": debate_id,
        "author_id": author_id,
        "source_node_id": source_node_id,
        "target_node_id": target_node_id,
        "type": type,
        "round": round
    }).execute()
    return response.data[0]


async def get_by_debate(debate_id: str, author_id: str | None = None,
                         type: str | None = None) -> list[dict]:
    client = await get_client()
    query = client.table("edges").select("*").eq("debate_id", debate_id)

    if author_id is not None:
        query = query.eq("author_id", author_id)

    if type is not None:
        query = query.eq("type", type)

    response = await query.execute()
    return response.data