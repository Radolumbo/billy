from datetime import datetime
from typing import Optional
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from ..congress.api import Bill, BillType
from ..dependencies.congress import CongressAPIClient, get_congress_api_client
from ..dependencies.gemini import GeminiLLMProvider, get_gemini_provider

# TODO: I always forget if I prefer plural or singular for API routes
router = APIRouter(prefix="/bill")


class BillFindResponse(BaseModel):
    results: list[Bill]


class BillAskRequest(BaseModel):
    congress: int
    type: BillType
    number: str
    query: str


class BillAskResponse(BaseModel):
    result: str


@router.get("/")
async def list(
    from_datetime: Optional[datetime] = None,
    to_datetime: Optional[datetime] = None,
    congress: CongressAPIClient = Depends(get_congress_api_client),
) -> BillFindResponse:
    bills = congress.list_bills(
        from_datetime=(
            from_datetime.astimezone(ZoneInfo("UTC")).isoformat().replace("+00:00", "Z") if from_datetime else None
        ),
        to_datetime=(
            to_datetime.astimezone(ZoneInfo("UTC")).isoformat().replace("+00:00", "Z") if to_datetime else None
        ),
    )
    return BillFindResponse(results=bills)


@router.post("/ask")
async def ask(
    request: BillAskRequest,
    llm: GeminiLLMProvider = Depends(get_gemini_provider),
    congress: CongressAPIClient = Depends(get_congress_api_client),
) -> BillAskResponse:
    bill_text = congress.get_bill_text(
        congress=request.congress,
        type=request.type,
        number=request.number,
    )

    result = llm.prompt(
        prompt=f"""
        User query: {request.query}

        Bill text:
        {bill_text.text}
        """,
        system_prompt=(
            "You are a helpful AI assistant that helps users understand legislation and legal documents. "
            "You are given a bill and you need to understand it and answer the user's query. "
            "Provide exact quotes from the bill when you can in your response. If you don't know or can't "
            "find the answer, say so. Be as concise as possible, unless the query is asking for a detailed explanation."
        ),
    )
    return BillAskResponse(result=result)
