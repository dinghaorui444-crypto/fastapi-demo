# routers/items.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from database import get_session
from models import ItemModel, User
from auth import get_current_user  # 引入“保安”模块，用于校验用户的 JWT 令牌

# 创建一个商品专属的路由组，统一加上前缀 /items，并在 Swagger 文档中归类为 items
router = APIRouter(prefix="/items", tags=["items"])

# ==================== 1. 创建商品（受保护：需要登录） ====================
@router.post("", response_model=ItemModel, status_code=status.HTTP_201_CREATED)
def create_item(
    item: ItemModel, 
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)  # 👈 “保安”上岗：只有携带有效 Token 的登录用户才能创建商品
):
    session.add(item)
    session.commit()
    session.refresh(item)
    return item


# ==================== 2. 获取商品列表（公开：任何人可看） ====================
@router.get("", response_model=list[ItemModel])
def read_items(
    skip: int = 0, 
    limit: int = 10, 
    session: Session = Depends(get_session)
):
    statement = select(ItemModel).offset(skip).limit(limit)
    return session.exec(statement).all()


# ==================== 3. 根据 ID 获取单个商品（公开：任何人可看） ====================
@router.get("/{item_id}", response_model=ItemModel)
def read_item_by_id(
    item_id: int, 
    session: Session = Depends(get_session)
):
    item = session.get(ItemModel, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


# ==================== 4. 修改商品（受保护：需要登录） ====================
@router.put("/{item_id}", response_model=ItemModel)
def update_item(
    item_id: int, 
    new_item: ItemModel, 
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)  # 👈 “保安”上岗：防止未登录用户随意修改商品
):
    db_item = session.get(ItemModel, item_id)
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
        
    # 仅更新传过来的字段（exclude_unset=True 代表没传的字段不修改）
    item_data = new_item.model_dump(exclude_unset=True)
    for key, value in item_data.items():
        setattr(db_item, key, value)
        
    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    return db_item


# ==================== 5. 删除商品（受保护：需要登录） ====================
@router.delete("/{item_id}")
def delete_item(
    item_id: int, 
    session: Session = Depends(get_session), # 👈 基础依赖
    current_user: User = Depends(get_current_user)  # 👈 “保安”上岗：只有登录用户才能删商品
):
    db_item = session.get(ItemModel, item_id)
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
        
    session.delete(db_item)
    session.commit()
    
    # 返回成功提示，顺便记录是谁删的商品
    return {
        "message": "商品删除成功", 
        "deleted_by": current_user.username
    }