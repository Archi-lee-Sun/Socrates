from ..client import get_client
from .agents import get_by_name
from datetime import datetime, timezone

async def validate_agent_selection(pro_name: str, anti_name: str) -> tuple[dict, dict] :
    pro_agent = await get_by_name(pro_name)
    anti_agent = await get_by_name(anti_name)

    if pro_agent["type"] != "pro" :
        raise ValueError(f"Agent '{pro_name}' is not a pro-type agent (found type: {pro_agent['type']})")
    
    if anti_agent["type"] != "anti" :
        raise ValueError(f"Agent '{anti_name}' is not an anti-type agent (found type: {anti_agent['type']})")
    
    return pro_agent , anti_agent



async def insert(pro_name: str , anti_name: str , topic: str , max_turns : int) :
    pro_agent , anti_agent = await validate_agent_selection(pro_name , anti_name)

    client = await get_client()

    response = await client.table("debates").insert({
        "topic" : topic ,
        "pro_id" : pro_agent["id"] ,
        "anti_id" : anti_agent["id"] ,
        "max_turns": max_turns ,
        "status" : "pending"
    }).execute()

    return response.data[0]



async def archive(debate_id : str) -> None :
    client = await get_client()

    await client.table("debates").update({
        "archived_at": datetime.now(timezone.utc).isoformat()
    }).eq("id" , debate_id).execute()



async def set_status(debate_id : str , status : str) -> None :
    client = await get_client()

    await client.table("debates").update({
        "status" : status
    }).eq("id" , debate_id).execute()



async def get_by_id(id: str) -> dict :
    client  = await get_client()

    response = await client.table("debates") \
        .select("*") \
        .eq("id" , id) \
        .limit(1) \
        .execute()
    
    if not response.data :
        raise ValueError(f"No debate found with id: {id}")
    
    return response.data[0]
