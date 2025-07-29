from fastapi import FastAPI
from routers import auth, users, wallet, roi, admin, swap, referral

app = FastAPI(title="UFO MLM Backend API")

# Include all routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(wallet.router)
app.include_router(roi.router)
app.include_router(admin.router)
app.include_router(swap.router)
app.include_router(referral.router)

@app.get("/")
def root():
    return {"message": "UFO MLM Backend is Live!"}
