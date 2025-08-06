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
    def add_to_partner_pool(new_activation_amount: float = 0):
    """Add 5% of activations & 0.25% of yesterday’s closing balance."""
    if new_activation_amount > 0:
        pool_fund = new_activation_amount * 0.05
        credit_partner_pool(pool_fund, source="activation")

    # Daily run at 12:01AM
    closing_balance = get_system_closing_balance()
    daily_yield = closing_balance * 0.0025
    credit_partner_pool(daily_yield, source="daily_yield")

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
def check_and_unlock_user_stakes():
    stakes = get_all_matured_stakes(today_date())  # Returns list of matured entries
    for stake in stakes:
        user_id = stake["user_id"]
        amount = stake["amount"]
        multiplier = stake.get("return_multiplier", 2)
        unlock_amount = amount * multiplier
        update_user_balance(user_id, unlock_amount, wallet_type="krishi_withdrawable_wallet")
        mark_stake_as_completed(stake["stake_id"])
        log_bonus(user_id, "stake_maturity", unlock_amount)
