from fastapi import FastAPI, HTTPException, Path, Query, status,Depends
from pydantic import BaseModel, Field

# 创建 FastAPI 应用实例，并加上标题和版本号提升规范度
app = FastAPI(title="FastAPI 综合实战演练", version="1.0.0")

# 1. 模拟一个内存中的数据库（用字典存放店铺/商品数据）
fake_tasks_db = {
    1: {"name": "A", "price": 100, "comments": 100000},
    2: {"name": "B", "price": 20, "comments": 29}
}

# ==========================================
# 2. 定义一个专门管分页的“类依赖项”（Class-based Dependency）
# ==========================================
class PaginationParams:
    def __init__(
        self,
        skip: int = Query(0, description="跳过多少条数据"),
        limit: int = Query(10, le=100, description="每页返回数量，最大 100")
    ):
        # 用 self 把参数绑定到当前实例对象身上
        self.skip = skip
        self.limit = limit


# ==========================================
# 3. 接口一：店铺商品查询接口（同时运用 Path、Query 与类依赖项）
# ==========================================
@app.get("/api/shops/{shop_id}/items", summary="获取店铺商品列表")
def get_shop_items(
    # 路径参数安检
    shop_id: int = Path(..., gt=0, description="店铺的唯一 ID,必须大于 0"),
    # 分类查询参数安检
    category: str = Query("all", min_length=2, max_length=20, description="商品分类筛选"),
    # 注入我们刚刚写好的类依赖项！(IDE 会自动帮你提示 commons.skip 和 commons.limit)
    pagination: PaginationParams = Depends()
):
    """
    - **shop_id**: 路径参数
    - **category**: 查询参数
    - **pagination**: 通过类注入的分页参数对象
    """
    shop = fake_tasks_db.get(shop_id)
    
    # 业务防线：如果没有查到该店铺，抛出标准 404 异常
    if not shop:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"未找到 ID 为 {shop_id} 的店铺！"
        )
    
    # 成功查到，返回数据与分类
    return {
        "status": "success",
        "shop_result": shop,
        "query_filter": {
            "category": category,
            "skip": pagination.skip,   # 使用类的点语法获取属性
            "limit": pagination.limit
        }
    }


# ==========================================
# 4. 接口二：用户下单接口（结合 Pydantic Field 约束 + 201 状态码）
# ==========================================
class OrderCreate(BaseModel):
    """
    Pydantic 安检模型：加入了 Field 字段精细化约束
    """
    item_name: str = Field(..., min_length=2, max_length=30, description="商品名称")
    quantity: int = Field(default=1, gt=0, description="购买数量，必须大于 0")
    express_shipping: bool = Field(default=False, description="是否加急配送")


@app.post("/api/orders", status_code=status.HTTP_201_CREATED, summary="创建新订单")
def create_order(order: OrderCreate):
    """
    POST 接口：接收并通过精细化安检的订单数据，成功创建返回 201 Created
    """
    return {
        "status": "success",
        "message": "订单创建成功，且通过严苛安检！",
        "order_data": order
    }