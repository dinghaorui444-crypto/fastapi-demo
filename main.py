from contextlib import asynccontextmanager
from fastapi import FastAPI
from database import engine
from models import SQLModel
from routers import items

@asynccontextmanager
async def lifespan(app: FastAPI):
    # ================= 1. 启动时执行的逻辑 =================
    print("🚀 正在初始化数据库和表...")
    SQLModel.metadata.create_all(engine)
    
    yield  # <-- 这里是分水岭：yield 前面是启动，yield 后面是关闭
    
    # ================= 2. 关闭时执行的逻辑（可选） =================
    print("👋 应用正在关闭，清理资源...")

# ================= 3. 把 lifespan 注册给 FastAPI =================
app = FastAPI(
    title="Modular FastAPI Project", 
    version="2.0.0",
    lifespan=lifespan  # 🎯 注入这里！
)

# 挂载商品路由
app.include_router(items.router)