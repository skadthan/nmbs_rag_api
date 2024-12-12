from fastapi import APIRouter, HTTPException
from datetime import datetime, timedelta
import jwt
from app.services.user_auth import verify_user
from app.models.auth_models import LoginRequest, LoginResponse
from passlib.context import CryptContext


# JWT Secret and algorithm
SECRET_KEY = "nmbs-secret-key"
ALGORITHM = "HS256"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Store hashed passwords
USER_CREDENTIALS = {
    "admin": pwd_context.hash("Ananya#2021"),  # Hashed password
    "skadthan": pwd_context.hash("Ashu#123")  # Hashed password
}

#print("Hashed User Credentials",USER_CREDENTIALS)


router = APIRouter()

import jwt

def decode_access_token(token: str):
    """
    Decodes a JWT and retrieves its expiration time.
    """
    try:
        payload = jwt.decode(token, options={"verify_signature": False})
        return payload.get("exp", None)  # Return the expiration time
    except jwt.DecodeError:
        return None


def verify_user(username: str, password: str) -> bool:
    """
    Verifies if the provided username and password are correct.
    """
    if username in USER_CREDENTIALS:
        # Verify the provided password against the stored hash
        return pwd_context.verify(password, USER_CREDENTIALS[username])
    return False


def create_access_token(data: dict, expires_delta: timedelta = None):
    """
    Creates a JWT token for the given data with an expiration time.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def create_refresh_token(data: dict, expires_delta: timedelta = None):
    """
    Creates a JWT refresh token.
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(days=7))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

@router.post("/login", response_model=LoginResponse)
def login(credentials: LoginRequest):
    """
    Login endpoint for user authentication.
    Accepts JSON payloads with `username` and `password`.
    """
    username = credentials.username
    password = credentials.password

    if not verify_user(username, password):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    # Create access token
    access_token = create_access_token(data={"sub": username}, expires_delta=timedelta(minutes=30))
    refresh_token = create_refresh_token(data={"sub": username})

    # Example usage
    exp_timestamp = decode_access_token(access_token)
    print(f"Access Token expires at: {exp_timestamp}")
    exp_timestamp = decode_access_token(refresh_token)
    print(f"Refresh Token expires at: {exp_timestamp}")

    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}
