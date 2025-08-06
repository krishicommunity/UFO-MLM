from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from src.routers.referral import get_upline_list
from src.database import get_user_by_id, update_user_balance
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

def distribute_swap_level_income(user_id: str, swap_amount: float):
    """Distribute 1% swap income to 10-level uplines equally."""
    upline_ids = get_upline_list(user_id, max_levels=10)
    income_per_level = swap_amount * 0.01  # 1%

    for level, upline_id in enumerate(upline_ids, start=1):
        upline = get_user_by_id(upline_id)
        if upline:
            update_user_balance(upline_id, income_per_level, wallet_type="usdt_income_wallet")
            print(f"Swap income: Level {level} | ${income_per_level:.2f} → {upline_id}")
