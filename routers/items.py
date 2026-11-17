# routers/items.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from database import get_session
from models import ItemModel

# 创建一个商品专属的路由组，统一加上前缀 /items
router = APIRouter(prefix="/items", tags=["items"])

@router.post("", response_model=ItemModel, status_code=status.HTTP_201_CREATED)
def create_item(item: ItemModel, session: Session = Depends(get_session)):
    session.add(item)
    session.commit()
    session.refresh(item)
    return item

@router.get("", response_model=list[ItemModel])
def read_items(skip: int = 0, limit: int = 10, session: Session = Depends(get_session)):
    statement = select(ItemModel).offset(skip).limit(limit)
    return session.exec(statement).all()

@router.get("/{item_id}", response_model=ItemModel)
def read_item_by_id(item_id: int, session: Session = Depends(get_session)):
    item = session.get(ItemModel, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

@router.put("/{item_id}", response_model=ItemModel)
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

@router.delete("/{item_id}")
def delete_item(item_id: int, session: Session = Depends(get_session)):
    db_item = session.get(ItemModel, item_id)
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
        
    session.delete(db_item)
    session.commit()
    return {"message": f"Item {item_id} deleted successfully"}