# update check
from src.database import db
from src.utils.jwt_handler import create_access_token
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
import random, string, time, os, smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from passlib.context import CryptContext
from utils.jwt_handler import create_access_token
from datetime import timedelta

router = APIRouter(prefix="/auth", tags=["Authentication"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

otp_store = {}
users_db = {}

# ENV config
SMTP_EMAIL = os.getenv("SMTP_EMAIL")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

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
    email: EmailStr
    password: str

# Email sender
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

def send_credentials(to_email, user_id, password):
    msg = MIMEMultipart("alternative")
    msg["Subject"] = "Your UFO Account Credentials"
    msg["From"] = SMTP_EMAIL
    msg["To"] = to_email
    html = f"""
    <html><body>
    <h3>Welcome to UFO MLM Platform</h3>
    <p><strong>User ID:</strong> {user_id}<br>
    <strong>Password:</strong> {password}</p>
    <p>Login and change your password anytime from your dashboard.</p>
    </body></html>
    """
    msg.attach(MIMEText(html, "html"))
    server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
    server.starttls()
    server.login(SMTP_EMAIL, SMTP_PASSWORD)
    server.sendmail(SMTP_EMAIL, to_email, msg.as_string())
    server.quit()

# Endpoints
@router.post("/register")
def register_user(req: RegisterRequest):
    otp = str(random.randint(100000, 999999))
    otp_store[req.email] = {"otp": otp, "timestamp": time.time(), "data": req}
    send_email_otp(req.email, otp)
    return {"message": "OTP sent to your email"}

@router.post("/verify")
def verify_otp(req: VerifyOTPRequest):
    record = otp_store.get(req.email)
    if not record:
        raise HTTPException(status_code=400, detail="OTP not found or expired")
    if time.time() - record["timestamp"] > 300:
        del otp_store[req.email]
        raise HTTPException(status_code=400, detail="OTP expired")
    if req.otp != record["otp"]:
        raise HTTPException(status_code=400, detail="Invalid OTP")

    reg_data = record["data"]
    user_id = f"UFO{random.randint(100000, 999999)}"
    raw_password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
    hashed_password = pwd_context.hash(raw_password)

    users_db[reg_data.email] = {
        "user_id": user_id,
        "sponsor_id": reg_data.sponsor_id,
        "name": reg_data.name,
        "email": reg_data.email,
        "mobile": reg_data.mobile,
        "password": hashed_password
    }

    send_credentials(reg_data.email, user_id, raw_password)
    del otp_store[req.email]
    return {"message": "Registration complete", "user_id": user_id}

@router.post("/login")
def login_user(req: LoginRequest):
    user = users_db.get(req.email)
    if not user or not pwd_context.verify(req.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token(data={"sub": user["user_id"]}, expires_delta=timedelta(minutes=60))
    return {"access_token": token, "token_type": "bearer"}