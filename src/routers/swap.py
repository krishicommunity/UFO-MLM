from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/swap", tags=["Swap"])

# Default KRISHI rate (adjustable via admin)
current_krishi_rate = {"rate": 0.012}

class SwapRequest(BaseModel):
    email: str
    usdt_amount: float

@router.post("/usdt-to-krishi")
def swap_usdt_to_krishi(req: SwapRequest):
    user = mock_users.get(req.email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user["usdt_wallet"] < req.usdt_amount:
        raise HTTPException(status_code=400, detail="Insufficient income wallet balance")

    krishi_received = req.usdt_amount / current_krishi_rate["rate"]

    # Swap logic (only income balance allowed)
    user["usdt_wallet"] -= req.usdt_amount
    user["krishi_wallet"] += krishi_received

    return {
        "message": "Swap successful",
        "krishi_received": round(krishi_received, 4),
        "rate": current_krishi_rate["rate"]
    }
