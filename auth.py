# auth.py
from datetime import datetime, timedelta, timezone
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from sqlmodel import Session, select
from database import get_session
from models import User

# 1. 密码加密上下文（使用 bcrypt 算法）
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 2. 密钥与算法（生产环境中必须保存在环境变量中）
SECRET_KEY = "your-super-secret-key-change-it-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30  # 令牌有效期 30 分钟

# 告诉 FastAPI 令牌去哪获取（指向咱们稍后要写的登录接口 /auth/login）
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# 密码哈希与验证函数
def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# 生成 JWT 令牌
def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# 核心“验票员”依赖注入：校验 JWT 并获取当前登录用户
def get_current_user(token: str = Depends(oauth2_scheme), session: Session = Depends(get_session)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # 解密 Token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception
    
    # 去数据库确认用户是否依然存在
    statement = select(User).where(User.username == username)
    user = session.exec(statement).first()
    if user is None:
        raise credentials_exception
        
    return user  # 验证通过，放行并返回当前用户对象！