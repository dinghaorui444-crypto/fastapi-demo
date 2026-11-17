from typing import Optional
from fastapi import FastAPI, Depends, HTTPException, status
from sqlmodel import SQLModel, Field, create_engine, Session, select

app = FastAPI(title="CRUD 全套核心实战 - 进阶版", version="1.1.0")

class ItemModel(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, description="商品名称")
    price: float = Field(description="商品价格")
    comments_count: int = Field(default=0, description="评论数")

sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"
engine = create_engine(sqlite_url)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

create_db_and_tables()


# ==================== 1. 抽离数据库会话依赖（Depends 供水站） ====================
def get_session():
    with Session(engine) as session:
        yield session


# ==================== C (Create) : 新增商品（升级 201 状态码） ====================
@app.post("/items", response_model=ItemModel, status_code=status.HTTP_201_CREATED)
def create_item(item: ItemModel, session: Session = Depends(get_session)):
    # 借助 Depends，连 with Session 都不用手动写啦！
    session.add(item)
    session.commit()
    session.refresh(item)
    return item


# ==================== R (Read List) : 查询所有商品（升级分页） ====================
@app.get("/items", response_model=list[ItemModel])
def read_items(
    skip: int = 0,   # 默认跳过前 0 个
    limit: int = 10, # 默认每页限制 10 个
    session: Session = Depends(get_session)
):
    # 用 offset 和 limit 控制分页，防止数据量大时撑爆服务器
    statement = select(ItemModel).offset(skip).limit(limit)
    items = session.exec(statement).all()
    return items


# ==================== R (Read by ID) : 按 ID 精准查询 ====================
@app.get("/items/{item_id}", response_model=ItemModel)
def read_item_by_id(item_id: int, session: Session = Depends(get_session)):
    item = session.get(ItemModel, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


# ==================== U (Update) : 修改商品 ====================
@app.put("/items/{item_id}", response_model=ItemModel)
def update_item(item_id: int, new_item: ItemModel, session: Session = Depends(get_session)):
    db_item = session.get(ItemModel, item_id)
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
        
    item_data = new_item.model_dump(exclude_unset=True)
    for key, value in item_data.items():
        setattr(db_item, key, value)
        
    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    return db_item


# ==================== D (Delete) : 删除商品 ====================
@app.delete("/items/{item_id}")
def delete_item(item_id: int, session: Session = Depends(get_session)):
    db_item = session.get(ItemModel, item_id)
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
        
    session.delete(db_item)
    session.commit()
    return {"message": f"Item {item_id} deleted successfully"}