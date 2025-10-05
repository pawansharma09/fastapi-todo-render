# app/auth.py
from datetime import datetime, timedelta
from typing import Optional
from jose import jwt
import os
from pwdlib import PasswordHash
from pwdlib.hashers.bcrypt import BcryptHasher

# Initialize pwdlib with bcrypt (automatically handles 72-byte truncation!)
pwd_hash = PasswordHash(hashers=[BcryptHasher()])

SECRET_KEY = os.environ.get("SECRET_KEY", "your-secret-key-change-in-prod")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_hash.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_hash.hash(password)  # ✅ Automatically safe for bcrypt

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
