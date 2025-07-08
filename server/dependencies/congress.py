import os
from functools import lru_cache

from ..congress.api import CongressAPIClient


@lru_cache()
def get_congress_api_client() -> CongressAPIClient:
    api_key = os.getenv("CONGRESS_API_KEY")
    if not api_key:
        raise ValueError("CONGRESS_API_KEY environment variable is required")

    return CongressAPIClient(api_key=api_key)
