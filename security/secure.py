import os
from fastapi import Depends, Request
from fastapi import HTTPException
from fastapi.security import OAuth2PasswordBearer
from dotenv import load_dotenv
from passlib.context import CryptContext
from datetime import datetime
from datetime import timedelta
from jose import jwt, JWTError
from models.request.schemas import UserReq
from config.models import User
from config.neo4j_connect import neo4j_driver as db


load_dotenv('.env')
# Configuration
SECRET_KEY = os.getenv('SECRET_KEY')
if SECRET_KEY is None:
    raise BaseException('Missing SECRET_KEY env var.')
ALGORITHM = os.getenv('ALGORITHM') or 'HS256'
ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES') or None 

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/login/token')


def verify_password(plain_password, hashed_password):
    verification = pwd_context.verify(plain_password, hashed_password)
    return verification


def get_password_hash(password):
    return pwd_context.hash(password)


def authenticate_user(email: str, password: str):
    user = valid_email_from_db(email)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    
    if not verify_password(password, user.password):
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    return user

# Create token internal function
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=90)
    to_encode.update({'exp': expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(request: Request):
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            raise HTTPException(status_code=401, detail="Not authorized user.")
        token = auth_header.split(' ')[1]
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Not authorized user.")
    except JWTError as e:
        print(f"Error decoding token: {e}")
        raise HTTPException(status_code=401, detail="Not authorized user.")
    
    user = get_user_by_email(email)
    if user == None:
        raise HTTPException(status_code=401, detail="Not authorized user.")
    return user

def get_user_by_email( email: str):
    try:
        user = User.nodes.get_or_none(email=email)
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        return {'uid': user.uid, 'name': user.name}
    except HTTPException as e:
        raise e
    except Exception as e:
        return False
    
def valid_email_from_db(email: str):
    try:
        result = User.nodes.get_or_none(email=email)
        if result is None:
            return False
        return result
    except Exception as e:
        return False


def decode_token(token):
    try:
        decoded_token = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return decoded_token
    except (JWTError) as e: 
        print(f"Error decoding token: {e}")
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")

def is_superuser(current_user: UserReq = Depends(get_current_user)):
    user = User.nodes.get_or_none(email = current_user.email)
    if user.is_superuser:
        return current_user
    else:
        raise HTTPException(status_code=401, detail="Not enough privileges")