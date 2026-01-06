from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from uuid import uuid4
from datetime import datetime

app = FastAPI(
    title="Express Entry Hub CRS Engine",
    version="1.0.0"
)

# In-memory store (Phase 1)
ASSESSMENTS = {}

class Form34Payload(BaseModel):
    meta: dict
    personal: dict
    marital: dict | None = None
    education: dict | None = None
    language: dict | None = None
    work: dict | None = None
    flags: dict | None = None


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/assess")
def assess(payload: Form34Payload):
    token = f"eeh_{uuid4().hex}"

    snapshot = {
        "meta": {
            "token": token,
            "engine_version": "crs-2026.01",
            "created_at": datetime.utcnow().isoformat()
        },
        "crs": {
            "total": 462,
            "core_human_capital": 298,
            "spouse_factors": 32,
            "skill_transferability": 100,
            "additional": 32
        },
        "breakdown": {
            "age": 77,
            "education": 120,
            "language": {
                "listening": 31,
                "reading": 23,
                "writing": 23,
                "speaking": 23
            },
            "work": {
                "foreign": 50,
                "canadian": 0
            }
        },
        "eligibility": {
            "fsw": True,
            "cec": False,
            "fst": False
        },
        "roadmap": {
            "best_stream": "Federal Skilled Worker",
            "priority_actions": [
                "Improve IELTS listening to CLB 9",
                "Complete spouse ECA"
            ],
            "risk_flags": [
                "Age points will reduce in 8 months"
            ],
            "checklist": [
                "Language test results",
                "Educational Credential Assessment",
                "Proof of funds",
                "Police clearance certificates"
            ]
        }
    }

    ASSESSMENTS[token] = snapshot

    return {
        "token": token,
        "engine_version": snapshot["meta"]["engine_version"],
        "schema_version": "1.0"
    }


@app.get("/result/{token}")
def get_result(token: str):
    if token not in ASSESSMENTS:
        raise HTTPException(status_code=404, detail="Assessment not found")

    return ASSESSMENTS[token]
