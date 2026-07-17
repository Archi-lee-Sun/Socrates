from ..config import TAVILY_API_KEY
from tavily import AsyncTavilyClient
from sentence_transformers import SentenceTransformer

tavily_client = AsyncTavilyClient(api_key=TAVILY_API_KEY)
model = SentenceTransformer("all-MiniLM-L6-v2")


def embed_batch(texts: list[str]) -> list[list[float]]:
    return model.encode(texts).tolist()


async def get_debate_data(topic: str, max_results: int = 20) -> list[dict]:
    try:
        response = await tavily_client.search(
            query=topic,
            search_depth="advanced",
            max_results=max_results
        )
    except Exception as e:
        raise RuntimeError(
            f"Failed to fetch search results from Tavily API.\n"
            f"Query: {topic}\n"
            f"Error detail: {e}"
        )

    results = response.get("results", [])

    filtered = []
    for result in results:
        title = (result.get("title") or "untitled").strip()
        url = (result.get("url") or "").strip()
        content = (result.get("content") or "").strip()

        if not url or len(content) < 100:
            continue

        filtered.append({"title": title, "url": url, "content": content})

    if not filtered:
        return []

    vectors = embed_batch([item["content"] for item in filtered])

    for item, vector in zip(filtered, vectors):
        item["vector"] = vector

    return filtered