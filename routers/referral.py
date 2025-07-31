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
