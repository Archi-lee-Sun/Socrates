from .intake import check_topic_vagueness , generate_topic_variants
from .retrieval import get_debate_data

from ..db.repositories.debates import insert as insert_debate
from ..db.repositories.evidence import insert as insert_evidence

async def scope_topic(raw_topic: str) -> dict :
    topic_vagueness = await check_topic_vagueness(raw_topic)

    if topic_vagueness.get("is_vague") == False :
        return {"is_vague" : False , "topic" : raw_topic}
    
    variants = await generate_topic_variants(raw_topic)

    return {
        "is_vague" : True ,
        "variants" : variants
    }

async def start_debate(topic: str, pro_name: str, anti_name: str, max_turns: int):
    debate_data = await get_debate_data(topic, 20)
    debate = await insert_debate(pro_name, anti_name, topic, max_turns)
    debate_id = debate["id"]

    for item in debate_data:
        await insert_evidence(debate_id, None, item["url"], item["content"], item["vector"])
