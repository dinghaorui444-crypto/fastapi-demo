from typing import Optional
from fastapi import FastAPI, Depends, HTTPException, status
from sqlmodel import SQLModel, Field, create_engine, Session, select

# 1. 创建 FastAPI 实例
app = FastAPI(title="CRUD 全套核心实战", version="1.0.0")

# 2. 定义数据库模型蓝图
class ItemModel(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, description="商品名称")
    price: float = Field(description="商品价格")
    comments_count: int = Field(default=0, description="评论数")

# 3. 配置数据库引擎与自动建表
sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"
engine = create_engine(sqlite_url)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

create_db_and_tables()


# ==================== C (Create) : 新增商品 ====================
@app.post("/items", response_model=ItemModel)
def create_item(item: ItemModel):
    with Session(engine) as session:
        session.add(item)
        session.commit()
        session.refresh(item)
        return item


# ==================== R (Read List) : 查询所有商品 ====================
@app.get("/items", response_model=list[ItemModel])
def read_items():
    with Session(engine) as session:
        statement = select(ItemModel)
        items = session.exec(statement).all()
        return items


# ==================== R (Read by ID) : 按 ID 精准查询单个商品 ====================
@app.get("/items/{item_id}", response_model=ItemModel)
def read_item_by_id(item_id: int):
    with Session(engine) as session:
        item = session.get(ItemModel, item_id)
        if not item:
            raise HTTPException(status_code=404, detail="Item not found")
        return item


# ==================== U (Update) : 修改商品 ====================
@app.put("/items/{item_id}", response_model=ItemModel)
def update_item(item_id: int, new_item: ItemModel):
    with Session(engine) as session:
        # 1. 先找旧人
        db_item = session.get(ItemModel, item_id)
        if not db_item:
            raise HTTPException(status_code=404, detail="Item not found")
            
        # 2. 动态字典循环覆盖新属性
        item_data = new_item.model_dump(exclude_unset=True)
        for key, value in item_data.items():
            setattr(db_item, key, value)
            
        # 3. 重新结账提交
        session.add(db_item)
        session.commit()
        session.refresh(db_item)
        return db_item


# ==================== D (Delete) : 删除商品 ====================
@app.delete("/items/{item_id}")
def delete_item(item_id: int):
    with Session(engine) as session:
        # 1. 先找人
        db_item = session.get(ItemModel, item_id)
        if not db_item:
            raise HTTPException(status_code=404, detail="Item not found")
            
        # 2. 执行删除并提交
        session.delete(db_item)
        session.commit()
        
        return {"message": f"Item {item_id} deleted successfully"}