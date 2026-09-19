from app.models.user import User
from app.schemas.auth import RegisterRequest
from app.utils.security import hash_password,verify_password


async def find_by_email(email:str)->User | None:
    return await User.find_one(User.email==email)

async def register_user(payload:RegisterRequest) -> User:
    user = User(
        name=payload.name,
        password_hash=hash_password(payload.password),
        email=payload.email
    )

    await user.insert()
    return user

async def authenticate(email: str, password: str) -> User | None:
    check_user = await find_by_email(email)
    

    if not check_user:
        return None
        

    if not verify_password(password, check_user.password_hash):
        return None
        
    return check_user


# async def authenticate(email: str, password: str) -> User | None:
#     user = await find_by_email(email)
#     print("DEBUG user found:", user is not None)
#     if not user:
#         return None
#     print("DEBUG hash in db:", user.password_hash[:20], "...")
#     ok = verify_password(password, user.password_hash)
#     print("DEBUG password ok:", ok)
#     return user if ok else None