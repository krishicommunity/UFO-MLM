from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime
from src.database import update_user_balance, get_user_by_id
from src.routers.referral import get_upline_list

router = APIRouter(prefix="/wallet", tags=["Wallet"])

# Ledger structure: in-memory for now
ledger_db = []

class TransferRequest(BaseModel):
    sender_email: str
    receiver_email: str
    amount: float

@router.post("/transfer")
def internal_transfer(req: TransferRequest):
    from_user = mock_users.get(req.sender_email)
    to_user = mock_users.get(req.receiver_email)

    if not from_user or not to_user:
        raise HTTPException(status_code=404, detail="User not found")

    if from_user["usdt_wallet"] < req.amount:
        raise HTTPException(status_code=400, detail="Insufficient balance")

    from_user["usdt_wallet"] -= req.amount
    to_user["usdt_wallet"] += req.amount

    # Add to ledger
    ledger_db.append({
        "from": req.sender_email,
        "to": req.receiver_email,
        "amount": req.amount,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "type": "internal_transfer"
    })

    return {"message": "Transfer successful", "from_balance": from_user["usdt_wallet"]}

class LedgerRequest(BaseModel):
    email: str

@router.post("/ledger")
def get_user_ledger(req: LedgerRequest):
    user_entries = [entry for entry in ledger_db if entry["from"] == req.email or entry["to"] == req.email]
    return {"ledger": user_entries}

@router.post("/stake_krishi")
def stake_krishi(user_id: str, amount: float):
    user = get_user_by_id(user_id)
    if user["krishi_withdrawable_wallet"] < amount:
        return {"status": "error", "message": "Insufficient KRISHI balance."}
    
    # Deduct from withdrawable
    update_user_balance(user_id, -amount, wallet_type="krishi_withdrawable_wallet")
    
    # Store stake entry in database
    store_stake_entry(user_id, amount, stake_type="user_stake", unlock_after_days=1080, return_multiplier=2)

    # Distribute level income
    distribute_stake_upline_income(user_id, amount)

    return {"status": "success", "message": f"{amount} KRISHI successfully staked for 36 months. Upline rewarded."}

@router.get("/my_stakes")
def get_user_stakes(user_id: str):
    active = db.stakes.find({"user_id": user_id, "status": "pending"})
    matured = db.stakes.find({"user_id": user_id, "status": "completed"})
    return {
        "active_stakes": list(active),
        "matured_stakes": list(matured)
    }
@router.get("/my_krishi_bonus")
def get_krishi_bonus_logs(user_id: str):
    logs = db.bonus_logs.find({"user_id": user_id, "coin_type": "KRISHI"}).sort("date", -1)
    return {"krishi_bonus_history": list(logs)}
