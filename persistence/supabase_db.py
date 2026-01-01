from supabase import create_client, Client
from typing import Optional


class SupabaseDatabase:
    """
    Supabase database client following the same pattern as Database class.
    Provides connection management and client access for Supabase operations.
    """

    def __init__(self, url: str, key: str) -> None:
        """
        Initialize Supabase database client.

        Args:
            url: Supabase project URL
            key: Supabase anon/service key
        """
        self._url = url
        self._key = key
        self._client: Optional[Client] = None

    async def connect(self) -> None:
        """
        Establish connection to Supabase.
        Creates the Supabase client instance.
        """
        self._client = create_client(self._url, self._key)

    async def close(self) -> None:
        """
        Close Supabase connection.
        Note: Supabase client doesn't require explicit closure,
        but kept for interface consistency.
        """
        self._client = None

    def get_client(self) -> Client:
        """
        Get the Supabase client instance.

        Returns:
            Supabase client

        Raises:
            AssertionError: If client is not initialized
        """
        assert self._client is not None, "Database not connected"
        return self._client
