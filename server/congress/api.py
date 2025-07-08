from typing import Any, Literal, Optional

import requests
from fastapi import HTTPException
from pydantic import BaseModel

# TODO: Create a shared types file probably
BillType = Literal["HR", "S", "HJRES", "SJRES", "HCONRES", "SCONRES", "HRES", "SRES"]


class BillAction(BaseModel):
    """Information about a bill action"""

    action_date: str
    text: str


class Bill(BaseModel):
    """Information about a bill"""

    # TODO: Unclear to me which fields are optional still
    congress: int
    number: str
    origin_chamber: str
    origin_chamber_code: str
    title: str
    type: BillType
    update_date: str
    update_date_including_text: str
    url: str
    latest_action: Optional[BillAction]


class BillText(BaseModel):
    """Bill text content"""

    congress: int
    type: BillType
    number: str
    text: str
    # TODO: Figure out what the possible values are for this
    # We want to always get whatever the latest/best version is
    text_type: str  # e.g. "Enrolled Bill"


class CongressAPIClient:
    """Client for the Congress.gov API"""

    def __init__(self, api_key: str, base_url: str = "https://api.congress.gov/v3"):
        self.base_url = base_url
        self.api_key = api_key

    def list_bills(
        self,
        from_datetime: Optional[str] = None,
        to_datetime: Optional[str] = None,
        limit: int = 250,
        offset: int = 0,
        sort: str = "updateDate+desc",
    ) -> list[Bill]:
        """
        List bills from Congress.gov

        Args:
            from_datetime: Start date to filter bills in YYYY-MM-DDT00:00:00Z format
            to_datetime: End date to filter bills in YYYY-MM-DDT00:00:00Z format
            limit: Number of results to return (max 250)
            offset: Number of results to skip for pagination
        """
        endpoint = "/bill"
        params: dict[str, Any] = {"limit": limit, "offset": offset, "sort": sort}

        if from_datetime:
            params["fromDateTime"] = from_datetime
        if to_datetime:
            params["toDateTime"] = to_datetime

        data = self._make_request(endpoint, params=params)

        bills = []
        for bill_data in data.get("bills", []):
            bill = Bill(
                congress=bill_data.get("congress"),
                number=bill_data.get("number"),
                origin_chamber=bill_data.get("originChamber"),
                origin_chamber_code=bill_data.get("originChamberCode"),
                title=bill_data.get("title"),
                type=bill_data.get("type"),
                update_date=bill_data.get("updateDate"),
                update_date_including_text=bill_data.get("updateDateIncludingText"),
                url=bill_data.get("url"),
                latest_action=(
                    BillAction(
                        action_date=bill_data["latestAction"]["actionDate"],
                        text=bill_data["latestAction"]["text"],
                    )
                    if bill_data.get("latestAction")
                    else None
                ),
            )
            bills.append(bill)

        return bills

    def get_bill_text(self, congress: int, type: BillType, number: str) -> BillText:
        """
        Get the text of a specific bill

        Args:
            congress: Congress number
            type: Type of bill (one of "hr", "s", "hjres", "sjres", "hconres", "sconres", "hres", "sres")
            number: Bill number
        """
        endpoint = f"/bill/{congress}/{type.lower()}/{number}/text"
        params = {"format": "json"}

        data = self._make_request(endpoint, params=params)

        # Find the requested text type
        text_versions = data.get("textVersions")
        if not text_versions:
            raise HTTPException(
                status_code=404,
                detail=f"No text found for bill {congress}/{type}/{number}",
            )

        # Default to the first text version if no preferred text type is found
        target_version: dict[str, Any] = text_versions[0]

        # Add order of preferred text types once I know what they are
        preferred_text_types = ["Enrolled Bill"]
        for text_type in preferred_text_types:
            found_preferred_text_type = False
            for version in text_versions:
                if version.get("type") == text_type:
                    target_version = version
                    found_preferred_text_type = True
                    break
            if found_preferred_text_type:
                break

        # Choose formatted text version
        target_url: str | None = None
        for format in target_version.get("formats", []):
            if format.get("type") == "Formatted Text":
                target_url = format.get("url")
                break

        if not target_url:
            raise HTTPException(
                status_code=404,
                detail=f"No formatted text URL found for bill {congress}/{type}/{number}",
            )

        try:
            response = requests.get(target_url)
            response.raise_for_status()
            text_content = response.text
        except requests.HTTPError as e:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Failed to fetch bill text: {e}",
            )
        except requests.RequestException as e:
            raise HTTPException(status_code=500, detail=f"Failed to fetch bill text: {e}")

        return BillText(
            congress=congress,
            type=type,
            number=number,
            text=text_content,
            text_type=target_version.get("type", ""),
        )

    def _make_request(
        self,
        endpoint: str,
        method: str = "GET",
        params: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """Make a request to the Congress.gov API"""
        url = f"{self.base_url}{endpoint}"

        if params is None:
            params = {"api_key": self.api_key}
        else:
            params["api_key"] = self.api_key

        try:
            response = requests.request(method, url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.HTTPError as e:
            if response.status_code == 401:
                raise HTTPException(status_code=401, detail="Invalid API key for Congress.gov")
            elif response.status_code == 429:
                raise HTTPException(
                    status_code=429,
                    detail="Rate limit exceeded for Congress.gov API",
                )
            else:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Congress.gov API error: {e}",
                )
        except requests.RequestException as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to connect to Congress.gov API: {e}",
            )
