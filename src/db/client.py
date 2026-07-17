from supabase import acreate_client , AsyncClient
from ..config import SUPABASE_KEY , SUPABASE_URL

_supabase = None
async def get_client() -> AsyncClient :
    global _supabase
    if _supabase is None :
        _supabase = await acreate_client(SUPABASE_URL,SUPABASE_KEY)
    return _supabase