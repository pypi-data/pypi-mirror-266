class SupamodelError(Exception):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)


class SupabaseAPIError(SupamodelError):
    def __init__(self, message: str, status_code: int, **kwargs):
        self.message = message
        self.status_code = status_code
        super().__init__(message, **kwargs)


class EmptyInputError(Exception):
    def __init__(
        self,
        data_input: list[dict] | dict,
        message: str = "The data entered shouldn't be empty. Either provide a list with a content of dictionaries or a dictionary with values within it.",
        **kwargs
    ):
        self.data_input = data_input
        self.message = message
        super().__init__(message, **kwargs)


class EmptyResponseError(Exception):
    def __init__(
        self,
        message: str = "The response from the database is empty. There is no data to process. We needed at least one record to proceed.",
        **kwargs
    ):
        self.message = message
        super().__init__(message, **kwargs)


class SupabaseConfigError(Exception):
    def __init__(
        self,
        message: str = "The Supabase `SUPABASE_URL` and `SUPABASE_KEY` is missing from environment variables, .env files, file secret, nor are they set. Please provide the Supabase URL and the Supabase Key.",
        **kwargs
    ):
        self.message = message
        super().__init__(message, **kwargs)
