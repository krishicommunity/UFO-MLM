from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/admin", tags=["Admin"])

# Admin credentials (can be enhanced later)
admin_email = "admin@ufokrishi.com"
admin_password = "UFOadmin@123"

# Access to global KRISHI rate
from .swap import current_krishi_rate
from .users import mock_users

class AdminLoginRequest(BaseModel):
    email: str
    password: str

class RateUpdateRequest(BaseModel):
    rate: float

class UserControlRequest(BaseModel):
    email: str
    action: str  # "block" or "unblock"

@router.post("/login")
def admin_login(req: AdminLoginRequest):
    if req.email == admin_email and req.password == admin_password:
        return {"message": "Admin login successful"}
    else:
        raise HTTPException(status_code=401, detail="Unauthorized")

@router.post("/update-rate")
def update_krishi_rate(req: RateUpdateRequest):
    current_krishi_rate["rate"] = req.rate
    return {"message": f"KRISHI rate updated to {req.rate}"}

@router.post("/user-control")
def block_or_unblock_user(req: UserControlRequest):
    if req.email not in mock_users:
        raise HTTPException(status_code=404, detail="User not found")

    mock_users[req.email]["status"] = "blocked" if req.action == "block" else "active"
    return {"message": f"User {req.email} is now {mock_users[req.email]['status']}"}

@router.post("/distribute_partner_pool")
def distribute_partner_pool(beneficiary_list: List[dict], krishi_rate: float = 0.012):
    """
    beneficiary_list: List of {user_id, percent}
    krishi_rate: Current KRISHI USDT price
    """
    pool_amount = get_partner_pool_balance()
    for item in beneficiary_list:
        uid = item["user_id"]
        pct = item["percent"] / 100
        usdt_part = pool_amount * pct * 0.70
        krishi_part = (pool_amount * pct * 0.30) / krishi_rate
        credit_wallet(uid, usdt_part, "usdt_income_wallet")
        credit_wallet(uid, krishi_part, "krishi_wallet")
        log_bonus(uid, "partner_pool", usdt_part, krishi_part)
    reset_partner_pool()
    return {"status": "success", "message": "Partner pool distributed successfully"}

