from passlib.context import CryptContext
from app import config

# Use Passlib to hash and verify passwords
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_user(username: str, password: str) -> bool:
    """
    Verifies if the provided username and password are correct.
    """
    if username in config.USER_CREDENTIALS:
        return pwd_context.verify(password, config.USER_CREDENTIALS[username])
    return False
