from fastapi import FastAPI, Depends, HTTPException, status, Form
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from passlib.context import CryptContext
from jose import JWTError, jwt
from typing import Optional
from models import User
from database import get_session, create_db_and_tables
from settings import settings
from notes.routes import router as notes_router
from auth.dependencies import get_current_user, oauth2_scheme
from celery_app import send_mock_email
from redis_cache import close_redis_client

app = FastAPI()

SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@app.on_event("startup")
async def on_startup():
    await create_db_and_tables()
    await create_default_admin()

@app.on_event("shutdown")
async def on_shutdown():
    await close_redis_client()

async def create_default_admin():
    async for session in get_session():
        admin = await session.execute(select(User).where(User.username == "admin"))
        if not admin.scalar():
            session.add(User(
                username="admin",
                password=pwd_context.hash("admin123"),
                role="admin"
            ))
            await session.commit()
        await session.close()
        break

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict):
    to_encode = data.copy()
    from datetime import datetime, timedelta
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def require_role(required_role: str):
    def role_dependency(current_user: User = Depends(get_current_user)):
        if current_user.role != required_role:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return current_user
    return role_dependency

@app.post("/register")
async def register(
    username: str = Form(...),
    password: str = Form(...),
    session: AsyncSession = Depends(get_session)
):
    existing_user = await session.execute(select(User).where(User.username == username))
    if existing_user.scalar():
        raise HTTPException(status_code=400, detail="Username already exists")
    new_user = User(
        username=username,
        password=get_password_hash(password),
        role="user"
    )
    session.add(new_user)
    await session.commit()
    return {"message": "User registered"}

@app.post("/login")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_session)
):
    result = await session.execute(select(User).where(User.username == form_data.username))
    user = result.scalars().first()
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/trigger-task")
async def trigger_task(token: str = Depends(oauth2_scheme)):
    send_mock_email.delay("user@example.com")
    return {"message": "Task started"}

@app.get("/admin/users")
async def get_all_users(current_user: User = Depends(require_role("admin")), session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(User))
    users = result.scalars().all()
    return users

@app.get("/users/me")
async def read_users_me(current_user: User = Depends(get_current_user)):
    return {"id": current_user.id, "username": current_user.username, "role": current_user.role}

@app.get("/")
def root():
    return {"message": "RBAC FastAPI is running!"}

app.include_router(notes_router) 