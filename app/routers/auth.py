from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from datetime import datetime, timedelta
import jwt
from app.services.user_auth import verify_user
from app.models.auth_models import LoginResponse

# JWT Secret and algorithm
SECRET_KEY = "nmbs-secreat-key"
ALGORITHM = "HS256"

router = APIRouter()

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

@router.post("/login", response_model=LoginResponse)
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Login endpoint for user authentication.
    """
    username = form_data.username
    password = form_data.password

    if not verify_user(username, password):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    # Create access token
    access_token = create_access_token(data={"sub": username}, expires_delta=timedelta(minutes=30))

    return LoginResponse(access_token=access_token, token_type="bearer")
