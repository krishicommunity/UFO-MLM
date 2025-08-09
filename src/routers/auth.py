# app/routers/auth.py
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, EmailStr
from app.db.mongo import get_db
from app.utils.security import hash_password, verify_password, make_jwt, generate_password
from app.utils.emailer import send_otp, verify_otp, send_welcome_email
from app.utils.refcode import generate_ref_code, generate_login_code

router = APIRouter(prefix="/auth", tags=["Auth"])

# ===== Models =====
class RegisterInit(BaseModel):
    sponsor_id: str   # public sponsor code (e.g., UFO000001)
    name: str
    mobile: str
    email: EmailStr

class RegisterVerify(BaseModel):
    email: EmailStr
    otp_code: str

class Login(BaseModel):
    email: EmailStr
    password: str

# Built-in system sponsor codes that are ALWAYS treated as active
SYSTEM_SPONSOR_CODES = {"ROOT", "UFO000001", "root@ufokrishi.com"}

# ===== Optional helper to check sponsor from UI =====
@router.get("/check-sponsor")
async def check_sponsor(code: str = Query(...)):
    db = get_db()
    if code in SYSTEM_SPONSOR_CODES:
        return {"active": True, "sponsor": {"name": "System Sponsor", "package_activated": True}}
    sp = await db.users.find_one({"referral_code": code}, {"_id": 0, "package_activated": 1, "name": 1})
    if not sp:
        raise HTTPException(404, "Sponsor code not found")
    return {"active": bool(sp.get("package_activated")), "sponsor": sp}

# ===== STEP 1: Init registration (send OTP) =====
@router.post("/register-init")
async def register_init(data: RegisterInit):
    db = get_db()

    # Email must not already exist
    if await db.users.find_one({"email": data.email}):
        raise HTTPException(400, "Email already exists")

    # Resolve sponsor
    if data.sponsor_id in SYSTEM_SPONSOR_CODES:
        sponsor_user_id = "system-root"
        sponsor_code = data.sponsor_id
        sponsor_active = True
    else:
        sponsor = await db.users.find_one({"referral_code": data.sponsor_id})
        if not sponsor:
            raise HTTPException(400, "Sponsor code not found")
        sponsor_active = bool(sponsor.get("package_activated"))
        if not sponsor_active:
            raise HTTPException(400, "Non Active Sponcer — registration blocked")
        sponsor_user_id = sponsor["user_id"]
        sponsor_code = data.sponsor_id

    # Store/refresh pending registration
    await db.pending_regs.update_one(
        {"email": str(data.email)},
        {"$set": {
            "email": str(data.email),
            "name": data.name,
            "mobile": data.mobile,
            "sponsor_code": sponsor_code,
            "sponsor_user_id": sponsor_user_id,
        }},
        upsert=True
    )

    # Send OTP (cooldown handled inside)
    info = send_otp(str(data.email))
    if not info.get("sent"):
        raise HTTPException(429, f"Please wait {info.get('retry_after',60)} seconds before resending OTP")

    return {"status": "otp_sent", "retry_after": info.get("retry_after", 60)}

# ===== STEP 2: Verify OTP and create user =====
@router.post("/register-verify")
async def register_verify(data: RegisterVerify):
    db = get_db()

    # 1) OTP check
    if not verify_otp(str(data.email), data.otp_code):
        raise HTTPException(400, "Invalid or expired OTP")

    # 2) Load pending
    pending = await db.pending_regs.find_one({"email": str(data.email)})
    if not pending:
        raise HTTPException(400, "No pending registration found; please start again")

    sponsor_user_id = pending.get("sponsor_user_id")
    sponsor_code = pending.get("sponsor_code")

    # 3) Sponsor re-check (allow system-root bypass)
    if sponsor_user_id != "system-root":
        sp = await db.users.find_one({"user_id": sponsor_user_id})
        if not sp or not sp.get("package_activated"):
            raise HTTPException(400, "Sponsor inactive; use another sponsor")

    # 4) Generate codes & password
    # unique referral_code
    while True:
        my_ref = generate_ref_code()
        exists = await db.users.find_one({"referral_code": my_ref})
        if not exists:
            break
    login_code = generate_login_code()
    raw_password = generate_password(10)

    # 5) Create user (internal ID remains email)
    user_id = str(data.email)
    await db.users.insert_one({
        "user_id": user_id,
        "email": str(data.email),
        "password": hash_password(raw_password),
        "name": pending["name"],
        "mobile": pending["mobile"],
        "sponsor_id": sponsor_user_id,   # "system-root" or actual user_id
        "sponsor_code": sponsor_code,    # public code used at signup
        "referral_code": my_ref,         # new public code for this user
        "login_code": login_code,        # optional UI login code
        "package_activated": False,
        "package_tier": None,
        "total_invested_usd": 0.0,
        "usdt_wallet": 0.0,
        "usdt_income_wallet": 0.0,
        "krishi_withdrawable_wallet": 0.0,
        "krishi_frozen_wallet": 0.0,
        "flags": {
            "user_blocked": False,
            "withdrawal_locked": False,
            "roi_blocked": False
        }
    })

    # 6) Clean pending + email credentials
    await db.pending_regs.delete_one({"email": str(data.email)})
    send_welcome_email(str(data.email), pending["name"], login_code, raw_password)

    # 7) Return creds to show in popup
    return {
        "status": "registered",
        "login_id": login_code,
        "password": raw_password,
        "referral_code": my_ref
    }

# ===== Normal email login =====
@router.post("/login")
async def login(data: Login):
    db = get_db()
    u = await db.users.find_one({"email": data.email})
    if not u or not verify_password(data.password, u["password"]):
        raise HTTPException(400, "Invalid credentials")
    token = make_jwt(u["user_id"])
    return {"token": token, "user_id": u["user_id"]}
