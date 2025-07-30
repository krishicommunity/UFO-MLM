from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
import random
import os
import smtplib
import time
import string
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from passlib.context import CryptContext

router = APIRouter(prefix="/auth", tags=["Authentication"])

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# In-memory stores
otp_store = {}         # {email: (otp, timestamp)}
pending_users = {}     # {email: {name, sponsor_id, mobile}}
users_db = {}          # {user_id: {user_data}}

# Models
class RegisterRequest(BaseModel):
    sponsor_id: str
    name: str
    email: EmailStr
    mobile: str

class VerifyOTPRequest(BaseModel):
    email: EmailStr
    otp: str

class LoginRequest(BaseModel):
    user_id: str
    password: str

# SMTP Config
SMTP_EMAIL = os.getenv("SMTP_EMAIL") or "nextaimindia@gmail.com"
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD") or "your_app_password_here"  # use actual app password
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

# --- Helper Functions ---
def send_email_otp(to_email, otp):
    msg = MIMEMultipart("alternative")
    msg["Subject"] = "Your UFO OTP Code"
    msg["From"] = SMTP_EMAIL
    msg["To"] = to_email
    html = f"<html><body><h2>Your OTP is: <strong>{otp}</strong></h2><p>Valid for 5 minutes.</p></body></html>"
    msg.attach(MIMEText(html, "html"))
    server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
    server.starttls()
    server.login(SMTP_EMAIL, SMTP_PASSWORD)
    server.sendmail(SMTP_EMAIL, to_email, msg.as_string())
    server.quit()

def send_login_credentials(to_email, user_id, password):
    msg = MIMEMultipart("alternative")
    msg["Subject"] = "🎉 Welcome to UFO MLM - Your Login Info"
    msg["From"] = SMTP_EMAIL
    msg["To"] = to_email
    html = f"""
    <html><body>
        <h2>Welcome to UFO MLM!</h2>
        <p><b>User ID:</b> {user_id}<br>
           <b>Password:</b> {password}</p>
        <p>🔐 Please change your password after login.</p>
    </body></html>
    """
    msg.attach(MIMEText(html, "html"))
    server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
    server.starttls()
    server.login(SMTP_EMAIL, SMTP_PASSWORD)
    server.sendmail(SMTP_EMAIL, to_email, msg.as_string())
    server.quit()

def generate_user_id():
    return "UFO" + ''.join(random.choices(string.digits, k=6))

def generate_password():
    return ''.join(random.choices(string.ascii_letters + string.digits + "@#$!", k=10))

# --- Routes ---
@router.post("/register")
def register_user(req: RegisterRequest):
    if req.email in otp_store or req.email in pending_users:
        raise HTTPException(status_code=400, detail="OTP already sent or user already pending verification.")
    otp = str(random.randint(100000, 999999))
    otp_store[req.email] = (otp, time.time())
    pending_users[req.email] = {
        "name": req.name,
        "sponsor_id": req.sponsor_id,
        "mobile": req.mobile
    }
    send_email_otp(req.email, otp)
    return {"message": "OTP sent to your email (valid 5 mins)."}

@router.post("/verify")
def verify_otp(req: VerifyOTPRequest):
    otp_data = otp_store.get(req.email)
    if not otp_data:
        raise HTTPException(status_code=400, detail="OTP not found or expired.")

    otp, timestamp = otp_data
    if time.time() - timestamp > 300:
        otp_store.pop(req.email, None)
        raise HTTPException(status_code=400, detail="OTP expired.")
    if req.otp != otp:
        raise HTTPException(status_code=400, detail="Invalid OTP")

    user_data = pending_users.pop(req.email)
    otp_store.pop(req.email, None)

    user_id = generate_user_id()
    raw_password = generate_password()
    hashed_password = pwd_context.hash(raw_password)

    users_db[user_id] = {
        "user_id": user_id,
        "name": user_data["name"],
        "email": req.email,
        "mobile": user_data["mobile"],
        "sponsor_id": user_data["sponsor_id"],
        "password": hashed_password
    }

    send_login_credentials(req.email, user_id, raw_password)
    return {"message": "Registration complete. Login credentials sent to email.", "user_id": user_id}

@router.post("/login")
def login_user(req: LoginRequest):
    user = users_db.get(req.user_id)
    if not user or not pwd_context.verify(req.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"message": "Login successful", "token": "demo-token"}
