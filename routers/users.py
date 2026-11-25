# routers/users.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select
from database import get_session
from models import User
from auth import get_password_hash, verify_password, create_access_token, get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])

# 1. 用户注册接口
@router.post("/register")
def register(username: str, password: str, session: Session = Depends(get_session)):
    # 检查用户名是否已被占用
    existing_user = session.exec(select(User).where(User.username == username)).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    # 密码加密后存入数据库
    hashed_password = get_password_hash(password)
    new_user = User(username=username, hashed_password=hashed_password)
    
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    return {"message": "注册成功", "username": new_user.username}

# 2. 用户登录接口（获取 JWT 令牌）
# 注意：这里用了 OAuth2PasswordRequestForm，它能完美契合 Swagger 页面的 Authorize 按钮！
@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_session)):
    # 查找用户
    statement = select(User).where(User.username == form_data.username)
    user = session.exec(statement).first()
    
    # 校验账号和密码
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 验证通过，签发 JWT 令牌 (把用户名存进 sub 字段)
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

# 3. 🛡️ 路由保护测试接口（必须登录携带 Token 才能访问）
@router.get("/me")
def read_users_me(current_user: User = Depends(get_current_user)):
    return {
        "status": "success",
        "message": "欢迎！你已经通过了 JWT 身份验证",
        "current_username": current_user.username
    }