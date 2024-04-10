from supabase_py import create_client

from supamodel.config import settings

client = create_client(
    supabase_url=settings.supabase_url,
    supabase_key=settings.supabase_url,
    postgrest_client_timeout=30,
)
