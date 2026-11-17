# models.py
from typing import Optional
from sqlmodel import SQLModel, Field

class ItemModel(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, description="商品名称")
    price: float = Field(description="商品价格")
    comments_count: int = Field(default=0, description="评论数")