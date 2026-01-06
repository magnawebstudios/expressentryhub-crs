# deploy-trigger: defensive Form34 schema sync (Render redeploy)

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from uuid import uuid4
from datetime import datetime
from typing import Optional, Dict, Any

app = FastAPI(
    title="Express Entry Hub CRS Engine",
    version="1.0.0"
)

# ======================================================
# IN-MEMORY STORE (PHASE 1 — SAFE, RESET ON RESTART)
# ======================================================

ASSESSMENTS: Dict[str, Dict[str, Any]] = {}

# ======================================================
# FORM 34 PAYLOAD (SCHEMA v1.0 — DEFENSIVE & FORGIVING)
# ======================================================

class Form34Payload(BaseModel):
    age: Optional[int] = 0
    country: Optional[str] = ""
    marital_status: Optional[str] = ""
    education: Optional[str] = ""
    test_type: Optional[str] = ""

    clb_listening: Optional[int] = 0
    clb_reading: Optional[int] = 0
    clb_writing: Optional[int] = 0
    clb_speaking: Optional[int] = 0

    foreign_exp: Optional[int] = 0
    canadian_exp: Optional[int] = 0
    teer: Optional[int] = 0

    schema_version: Optional[str] = "1.0"
    submitted_at: Optional[str] = None

    class Config:
        extra = "ignore"  # 🔒 ignore unknown fields from WP / Fluent Forms

# ======================================================
# HEALTH CHECK
# ======================================================

@app.get("/health")
def health():
    return {"status": "ok"}

# ======================================================
# ASSESSMENT ENDPOINT (AUTHORITATIVE BRAIN)
# ======================================================

@app.post("/assess")
def assess(payload: Form34Payload):

    token = f"eeh_{uuid4().hex}"

    snapshot = {
        "meta": {
            "token": token,
            "engine_version": "crs-2026.01",
            "schema_version": "1.0",
            "created_at": datetime.utcnow().isoformat()
        },
        "input": payload.dict(),
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

    # 🔒 CONTRACT FIX — WordPress expects THIS shape only
    return {
        "success": True,
        "token": token
    }

# ======================================================
# RESULT FETCH (READ-ONLY SNAPSHOT)
# ======================================================

@app.get("/result/{token}")
def get_result(token: str):

    if token not in ASSESSMENTS:
        raise HTTPException(status_code=404, detail="Assessment not found")

    return ASSESSMENTS[token]
