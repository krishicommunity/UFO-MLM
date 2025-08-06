from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/roi", tags=["ROI"])

class ROICalcRequest(BaseModel):
    email: str

@router.post("/daily-roi")
def generate_daily_roi(req: ROICalcRequest):
    user = mock_users.get(req.email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    usdt_roi = user["usdt_wallet"] * 0.00111  # 0.111% USDT daily ROI
    krishi_roi_value = user["usdt_wallet"] * 0.001666  # 0.1666% worth of KRISHI
    krishi_rate = 0.012  # system rate, adjustable from admin
    krishi_coins = krishi_roi_value / krishi_rate

    half = krishi_coins / 2
    user["usdt_wallet"] += usdt_roi
    user["krishi_wallet"] += half
    user["frozen_krishi"] += half

    return {
        "usdt_roi": round(usdt_roi, 6),
        "krishi_roi": round(krishi_coins, 6),
        "added_to_krishi_wallet": round(half, 6),
        "added_to_frozen": round(half, 6),
        "krishi_rate_used": krishi_rate,
        "status": "Daily ROI Added"
    }
def check_and_trigger_diamond_bonus(user_id, total_team_business, direct_exec_count):
    if direct_exec_count >= 5 and total_team_business >= 100000:
        if not user_has_active_diamond_bonus(user_id):  # Write this check separately
            start_bonus_cycle(user_id, amount=total_team_business * 0.001, duration=100, bonus_type="diamond")
            print(f"Diamond Bonus activated for {user_id}")
            
def check_and_trigger_team_leader_bonus(user_id, total_downline_business, active_directs, has_exec_direct):
    if active_directs >= 5 and has_exec_direct and total_downline_business >= 100000:
        if not user_has_active_leader_bonus(user_id):
            start_bonus_cycle(user_id, amount=total_downline_business * 0.0001, duration=100, bonus_type="leader")
            print(f"Team Leader Bonus activated for {user_id}")
