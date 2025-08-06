from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/referral", tags=["Referral"])

# Sample referral mapping (for testing)
referrals = {
    "testuser@ufokrishi.com": [
        "user1@example.com",
        "user2@example.com",
        "user3@example.com"
    ]
}

class ReferralRequest(BaseModel):
    email: str

@router.post("/directs")
def get_direct_referrals(req: ReferralRequest):
    direct = referrals.get(req.email, [])
    return {
        "direct_referrals": direct,
        "count": len(direct)
    }
def distribute_stake_upline_income(user_id: str, staked_amount: float):
    upline_ids = get_upline_list(user_id, max_levels=10)
    level_percentages = [0.03, 0.02, 0.01] + [0.005] * 7  # Levels 4–10

    for i, upline_id in enumerate(upline_ids):
        if i >= 10:
            break
        level_pct = level_percentages[i]
        krishi_income = staked_amount * level_pct
        update_user_balance(upline_id, krishi_income, wallet_type="krishi_withdrawable_wallet")
        log_bonus(upline_id, "stake_level_income", krishi_income, level=i+1)
