from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from supamodel.exceptions import SupabaseConfigError


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env.dev", env_file_encoding="utf-8", extra="ignore"
    )


class SupabaseSettings(Settings):
    """
    Represents the settings for the Supabase client.

    Attributes:
        supabase_url (str | None): The URL of the Supabase server.
        supabase_key (str | None): The API key for accessing the Supabase server.
        schema (str): The default database schema.
        postgrest_client_timeout (int): The timeout value for the PostgREST client.
    """

    supabase_url: str | None = None
    supabase_key: str | None = None

    # -------------------------
    # client options
    # -------------------------
    schema: str = "public"
    postgrest_client_timeout: int = 30

    @model_validator(pre=True)
    @staticmethod
    def check_url_key_set(self):
        if not self.supabase_url or not self.supabase_key:
            raise SupabaseConfigError

    def options(self) -> dict:
        """
        Returns a dictionary of the Supabase client options.

        Returns:
            dict: A dictionary containing the Supabase client options.
        """
        return {
            "schema": self.schema,
            "postgrest_client_timeout": self.postgrest_client_timeout,
        }


settings = SupabaseSettings()
