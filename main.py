from fastapi import FastAPI
from pydantic import BaseModel

# 创建 FastAPI 应用实例，并加上标题和版本号提升规范度
app = FastAPI(title="FastAPI 综合实战演练", version="1.0.0")

# 1. 模拟一个内存中的数据库（用字典存放店铺/商品数据）
fake_tasks_db = {
    1: {"name": "A", "price": 100, "comments": 100000},
    2: {"name": "B", "price": 20, "comments": 29}
}

# ==========================================
# 2. 接口一：店铺商品查询接口（结合 路径参数 + 查询参数）
# ==========================================
@app.get("/api/shops/{shop_id}/items")
def get_shop_items(shop_id: int, category: str = "all"):
    """
    - shop_id: 路径参数（动态身份证号，如 /api/shops/1/items）
    - category: 查询参数（可选筛选条件，默认值为 "all"）
    """
    shop = fake_tasks_db.get(shop_id)
    
    # 防御性判断：如果没有查到该店铺
    if not shop:
        return {
            "status": "error",
            "message": f"未找到 ID 为 {shop_id} 的店铺！"
        }
    
    # 成功查到，返回数据与分类
    return {
        "status": "success",
        "shop_result": shop,
        "category": category
    }


# ==========================================
# 3. 接口二：用户下单接口（结合 Pydantic 安检模型 + POST）
# ==========================================
class OrderCreate(BaseModel):
    """
    Pydantic 安检模型：用来自动拦截并校验前端传过来的 JSON 数据格式
    """
    item_name: str                  # 必填：商品名称
    quantity: int = 1               # 可选：购买数量（默认值 1）
    express_shipping: bool = False  # 可选：是否加急（默认值 False）


@app.post("/api/orders")
def create_order(order: OrderCreate):
    """
    POST 接口：接收并安检用户提交的订单数据
    """
    return {
        "status": "success",
        "message": "订单创建成功！",
        "order_data": order
    }