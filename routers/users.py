from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/users", tags=["Users"])

# Temporary in-memory user data
mock_users = {
    "testuser@ufokrishi.com": {
        "email": "testuser@ufokrishi.com",
        "wallet_address": "0x8432Ab27901D9Dfc79029fEEBA8ebe97bFD7868A",
        "package": "Executive",
        "status": "active",
        "usdt_wallet": 250.00,
        "krishi_wallet": 1000.00,
        "frozen_krishi": 500.00,
        "referrer": "admin@ufokrishi.com"
    }
}

class UserInfoRequest(BaseModel):
    email: str

@router.post("/info")
def get_user_info(req: UserInfoRequest):
    user = mock_users.get(req.email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

class WalletUpdateRequest(BaseModel):
    email: str
    usdt: float = 0.0
    krishi: float = 0.0

@router.post("/update-wallet")
def update_user_wallet(req: WalletUpdateRequest):
    if req.email in mock_users:
        mock_users[req.email]["usdt_wallet"] += req.usdt
        mock_users[req.email]["krishi_wallet"] += req.krishi
        return {"message": "Wallet updated."}
    else:
        raise HTTPException(status_code=404, detail="User not found")
