from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

app = FastAPI(
    title="FedGuard AI API",
    description="Backend API for FedGuard AI - Debt Governance Platform",
    version="1.0.0"
)

# --- CORS Configuration ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for demo purposes
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Data Models ---
class UserLogin(BaseModel):
    username: str
    password: str
    role: str  # 'admin' or 'user'

class Case(BaseModel):
    id: str
    title: str
    status: str
    risk_score: int
    created_at: str

# --- Mock Data ---
MOCK_CASES = [
    {
        "id": "CASE-2024-001",
        "title": "Corporate Loan Default - TechSol Pvt Ltd",
        "status": "Critical",
        "risk_score": 92,
        "created_at": "2024-01-15T10:00:00Z"
    },
    {
        "id": "CASE-2024-002",
        "title": "SME Credit Recovery - GreenAgro",
        "status": "Review",
        "risk_score": 45,
        "created_at": "2024-01-20T14:30:00Z"
    },
    {
        "id": "CASE-2024-003",
        "title": "Retail Fraud Detection - Multiple Accounts",
        "status": "Safe",
        "risk_score": 12,
        "created_at": "2024-01-22T09:15:00Z"
    }
]

# --- Routes ---

@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.post("/api/v1/auth/login")
async def login(user: UserLogin):
    """Mock login endpoint."""
    # In a real app, verify password hash
    if user.password == "password": # Simple check for demo
        return {
            "access_token": "mock-jwt-token-12345",
            "token_type": "bearer",
            "role": user.role,
            "message": f"Welcome back, {user.role}"
        }
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid credentials"
    )

@app.get("/api/v1/cases", response_model=List[Case])
async def get_cases():
    """Retrieve all cases (Mock Data)."""
    return MOCK_CASES

@app.get("/api/v1/ai/risk-assessment/{case_id}")
async def get_risk_assessment(case_id: str):
    """Get AI risk assessment for a specific case."""
    # Simulate AI processing
    case = next((c for c in MOCK_CASES if c["id"] == case_id), None)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    return {
        "case_id": case_id,
        "risk_score": case["risk_score"],
        "analysis": "High probability of default based on cash flow anomalies.",
        "recommendation": "Initiate early recovery process." if case["risk_score"] > 80 else "Monitor closely."
    }
