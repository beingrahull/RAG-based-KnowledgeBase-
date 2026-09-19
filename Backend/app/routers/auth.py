from fastapi import FastAPI,APIRouter, HTTPException,Response
from app.schemas.auth import RegisterResponse,RegisterRequest,UserPublic,LoginRequest,LoginResponse
from app.services.user_service import find_by_email,register_user,authenticate
from app.utils.security import generate_token

router=APIRouter(prefix="/api/auth", tags=["auth"])

@router.post("/register",response_model=RegisterResponse, status_code=201)
async def registration_process(payload:RegisterRequest):
    existing_user=await find_by_email(payload.email)
    if existing_user :
        raise HTTPException(status_code=401, detail="User exists. Try logging in.")

    user=await register_user(payload)

    return {
        "message": "Account Registered",
        "user": UserPublic(id=str(user.id), name=user.name, email=user.email),
    }

@router.post("/login", response_model=LoginResponse)
async def login_request(payload: LoginRequest, response: Response):
    user = await authenticate(payload.email, payload.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = generate_token(str(user.id))

    response.set_cookie(
        "Access_Token",
        token,
        httponly=True,
        samesite="lax",
        secure=False,
        max_age=60 * 60 * 24 * 7,
    )

    return {
        "message": "Login successful",
        "user": UserPublic(id=str(user.id), name=user.name, email=user.email),
    }