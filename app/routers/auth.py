from fastapi import APIRouter, HTTPException, Request, Response
from datetime import datetime, timedelta
import jwt
from typing import Optional
from fastapi import Depends, HTTPException, Security
from app.services.user_auth import verify_user
from app.models.auth_models import LoginRequest, LoginResponse
from passlib.context import CryptContext
from fastapi.security import HTTPBearer



# JWT Secret and algorithm
SECRET_KEY = "nmbs-secret-key"
ALGORITHM = "HS256"

bearer_scheme = HTTPBearer()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Store hashed passwords
USER_CREDENTIALS = {
    "admin": pwd_context.hash("Ananya#2021"),  # Hashed password
    "skadthan": pwd_context.hash("Ashu#123")  # Hashed password
}

#print("Hashed User Credentials",USER_CREDENTIALS)


router = APIRouter()

def decode_access_token(token: str):
    """
    Decodes a JWT and retrieves its expiration time.
    """
    try:
        payload = jwt.decode(token, options={"verify_signature": False})
        return payload.get("exp", None)  # Return the expiration time
    except jwt.DecodeError:
        return None


def verify_user_bkp(username: str, password: str) -> bool:
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
        expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
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

def get_current_user(token: str = Depends(bearer_scheme)) -> Optional[str]:
    """
    Validate the access token and return the username (subject).
    """
    try:
        payload = jwt.decode(token.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return username
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


@router.post("/login", response_model=LoginResponse)
def login(credentials: LoginRequest, response: Response):
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

    # Set refresh token in HttpOnly cookie
    response.set_cookie(
        key="refreshToken",
        value=refresh_token,
        httponly=True,
        secure=True,  # Ensure cookies are sent only over HTTPS
        samesite="Strict",  # Prevent CSRF
        max_age=7 * 24 * 60 * 60,  # 7 days in seconds
    )

    # Example usage
    exp_timestamp = decode_access_token(access_token)
    print(f"Access Token expires at: {exp_timestamp}")
    exp_timestamp = decode_access_token(refresh_token)
    print(f"Refresh Token expires at: {exp_timestamp}")

    # Debugging expiration times
    #print(f"Access Token expires at: {decode_access_token(access_token)}")
    #print(f"Refresh Token expires at: {decode_access_token(refresh_token)}")

     # Return access token only
    return {"access_token": access_token, "token_type": "bearer"}
    #return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

@router.post("/logout")
def logout(response: Response):
    """
    Logout endpoint to clear the refresh token cookie.
    """
    response.delete_cookie("refreshToken")  # Delete the refreshToken cookie
    return {"message": "Logged out successfully"}


@router.post("/refresh")
def refresh_token(request: Request):
    refresh_token = request.cookies.get('refreshToken')
    if not refresh_token:
        raise HTTPException(status_code=401, detail="No refresh token found")

    # Decode and validate the refresh token
    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if not username:
            raise HTTPException(status_code=401, detail="Invalid refresh token")

        # Create a new access token
        new_access_token = create_access_token(data={"sub": username})
        return {"access_token": new_access_token, "token_type": "bearer"}
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Refresh token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
