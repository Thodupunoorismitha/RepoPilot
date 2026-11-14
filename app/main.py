
from fastapi import FastAPI

app = FastAPI(
    title="RepoPilot API",
    description="AI-powered codebase intelligence platform",
    version="0.1.0",
)


@app.get("/health")
def health_check():
    """Return the operational status of the API."""
    return {
        "status": "ok",
        "service": "repopilot-api",
    }
