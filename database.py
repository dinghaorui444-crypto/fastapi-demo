# database.py
from sqlmodel import create_engine, Session

# 1. 定义 SQLite 数据库文件名和连接地址
sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

# 2. 创建全局唯一的数据库引擎（相当于水库的总阀门）
engine = create_engine(sqlite_url)

# 3. 编写依赖注入的“供水站”函数
def get_session():
    """
    FastAPI 依赖注入专用：
    自动开启一个 Session 连接，用完之后无论如何都会安全关闭。
    """
    with Session(engine) as session:
        yield session