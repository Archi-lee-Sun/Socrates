import os 
from dotenv import load_dotenv

load_dotenv

def _require(key : str) -> str :
    value = os.getenv(key)
    if value is None :
        raise RuntimeError(f"Missing required env var: {key}")
    else :
        return value 
    

SUPABASE_KEY = _require("SUPABASE_KEY")
SUPABASE_URL = _require("SUPABASE_URL")
GROQ_API_KEY = _require("GROQ_API_KEY")
TAVILY_API_KEY = _require("TAVILY_API_KEY")