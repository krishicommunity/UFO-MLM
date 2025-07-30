from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
import random
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

router = APIRouter(prefix="/auth", tags=["Authentication"])

# Temporary in-memory OTP store
otp_store = {}

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str

class VerifyOTPRequest(BaseModel):
    email: EmailStr
    otp: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

# Configure your email credentials
SMTP_EMAIL = os.getenv("SMTP_EMAIL")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

def send_email_otp(to_email, otp):
    msg = MIMEMultipart("alternative")
    msg["Subject"] = "Your UFO OTP Code"
    msg["From"] = SMTP_EMAIL
    msg["To"] = to_email

    html = f"<html><body><h2>Your OTP is: <strong>{otp}</strong></h2><p>Do not share this code.</p></body></html>"
    msg.attach(MIMEText(html, "html"))

    server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
    server.starttls()
    server.login(SMTP_EMAIL, SMTP_PASSWORD)
    server.sendmail(SMTP_EMAIL, to_email, msg.as_string())
    server.quit()

@router.post("/register")
def register_user(req: RegisterRequest):
    otp = str(random.randint(100000, 999999))
    otp_store[req.email] = otp
    send_email_otp(req.email, otp)
    return {"message": "OTP sent to your email."}

@router.post("/verify")
def verify_otp(req: VerifyOTPRequest):
    if otp_store.get(req.email) == req.otp:
        del otp_store[req.email]
        return {"message": "Email verified. Registration complete."}
    else:
        raise HTTPException(status_code=400, detail="Invalid OTP")

@router.post("/login")
def login_user(req: LoginRequest):
    # Example: test login
    if req.email == "testuser@ufokrishi.com" and req.password == "UFOtest@123":
        return {"message": "Login successful", "token": "demo-token"}
    else:
        raise HTTPException(status_code=401, detail="Invalid credentials")
