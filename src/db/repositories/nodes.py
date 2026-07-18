from ..client import get_client

async def insert(debate_id: str, author_id: str, claim: str,
                  falsification_condition: str, round: int) -> dict:
    client = await get_client()
    response = await client.table("nodes").insert({
        "debate_id": debate_id,
        "author_id": author_id,
        "claim": claim,
        "falsification_condition": falsification_condition,
        "status": "open",
        "round": round
    }).execute()
    return response.data[0]


async def get_by_id(node_id: str) -> dict:
    client = await get_client()
    response = await client.table("nodes") \
        .select("*") \
        .eq("id", node_id) \
        .limit(1) \
        .execute()

    if not response.data:
        raise ValueError(f"No node found with id: {node_id}")

    return response.data[0]


async def get_by_debate(debate_id: str, author_id: str | None = None,
                         status: str | None = None) -> list[dict]:
    client = await get_client()
    query = client.table("nodes").select("*").eq("debate_id", debate_id)

    if author_id is not None:
        query = query.eq("author_id", author_id)

    if status is not None:
        query = query.eq("status", status)

    response = await query.execute()
    return response.data


async def update_status(node_id: str, status: str) -> None:
    client = await get_client()
    await client.table("nodes").update({"status": status}).eq("id", node_id).execute()