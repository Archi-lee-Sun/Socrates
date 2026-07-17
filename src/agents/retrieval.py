from ..config import TAVILY_API_KEY
from tavily import AsyncTavilyClient

tavily_client = AsyncTavilyClient(api_key=TAVILY_API_KEY)

async def get_debate_data(topic : str , max_results: int = 20) -> list[dict] :
    try :
        response = await tavily_client.search(
            query=topic,
            search_depth="advanced",
            max_results=max_results
        )
    except Exception as e :
        raise RuntimeError(
            f"Failed to fetch search results from Tavily API.\n"
            f"Query: {topic}\n"
            f"Error detail: {e}"
        )
    
    results = response.get("results" , [])
    formatted_data = []
    for result in results :
        title = (result.get("title") or "untitled").strip()
        url = (result.get("url") or "").strip()
        content = (result.get("content") or "").strip()
        
        if not url :
            continue

        if len(content) < 100 :
            continue

        formatted_data.append({
            "title": title,
            "url" : url ,
            "content" : content
        })

    return formatted_data