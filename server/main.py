from dotenv import load_dotenv
from fastapi import FastAPI, Response

from .routers.bill import router as bill_router

load_dotenv()

app = FastAPI(
    title="Billy", description="AI-powered legislation understanding", version="0.1.0"
)

app.include_router(bill_router)


@app.get("/")
async def root() -> Response:
    return Response(content="Hello world, it's me, Billy!")


@app.get("/health")
async def health() -> Response:
    return Response(content="healthy")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
