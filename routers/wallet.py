from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime

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
