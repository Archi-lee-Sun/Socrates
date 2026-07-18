from ..client import get_client

async def get_by_name(agent_name: str) -> dict:
    client = await get_client()

    response = await client.table("agents") \
        .select("*") \
        .eq("name" , agent_name) \
        .limit(1) \
        .execute()
    
    if not response.data :
        raise ValueError(f"No agent found with name: {agent_name}")
    
    return response.data[0]
    