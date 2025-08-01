from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from src.routers import auth, users, wallet, roi, admin, swap, referral
from src.database import db
print("✅ Import test success from main.py")


app = FastAPI(title="UFO MLM Backend API")

# Optional: Allow CORS if frontend is separate
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or restrict to your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all routers
app.include_router(auth.router, prefix="/auth")
app.include_router(users.router, prefix="/users")
app.include_router(wallet.router, prefix="/wallet")
app.include_router(roi.router, prefix="/roi")
app.include_router(admin.router, prefix="/admin")
app.include_router(swap.router, prefix="/swap")
app.include_router(referral.router, prefix="/referral")


@app.get("/", response_class=HTMLResponse)
async def root():
    return """
    <html>
        <head><title>UFO MLM</title></head>
        <body>
            <h1>🚀 UFO MLM Backend is Live!</h1>
            <ul>
                <li><a href="/docs" target="_blank">API Docs</a></li>
                <li><a href="/auth/register" target="_blank">/auth/register</a> → Register endpoint</li>
                <li><a href="/auth/login" target="_blank">/auth/login</a> → Login endpoint</li>
                <li><a href="/admin/dashboard" target="_blank">/admin/dashboard</a> → Admin Dashboard</li>
                <li><a href="/swap/calculate" target="_blank">/swap/calculate</a> → ROI Calculator</li>
            </ul>
        </body>
    </html>
    """
