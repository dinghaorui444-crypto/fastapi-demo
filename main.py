from fastapi import FastAPI, HTTPException, Path, Query, status  # 规范导入模块
from pydantic import BaseModel, Field

# 创建 FastAPI 应用实例，并加上标题和版本号提升规范度
app = FastAPI(title="FastAPI 综合实战演练", version="1.0.0")

# 1. 模拟一个内存中的数据库（用字典存放店铺/商品数据）
fake_tasks_db = {
    1: {"name": "A", "price": 100, "comments": 100000},
    2: {"name": "B", "price": 20, "comments": 29}
}

# ==========================================
# 2. 接口一：店铺商品查询接口（包含 Path 与 Query 精细化安检）
# ==========================================
@app.get("/api/shops/{shop_id}/items", summary="获取店铺商品列表")
def get_shop_items(
    # 路径参数安检：shop_id 必须大于 0 (gt=0)
    shop_id: int = Path(..., gt=0, description="店铺的唯一 ID，必须大于 0"),
    # 查询参数安检：category 限制长度 2-20，limit 限制 1-50
    category: str = Query("all", min_length=2, max_length=20, description="商品分类筛选"),
    limit: int = Query(10, gt=0, le=50, description="每页返回数量，最大 50")
):
    """
    - **shop_id**: 路径参数（动态身份证号，如 `/api/shops/1/items`）
    - **category**: 查询参数（可选筛选条件，默认值为 `"all"`）
    - **limit**: 查询参数（分页限制，默认值为 `10`）
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
        "query_filter": {  # 修正了原代码中的 quer_filter 拼写问题
            "category": category,
            "limit": limit
        }
    }


# ==========================================
# 3. 接口二：用户下单接口（结合 Pydantic Field 约束 + 201 状态码）
# ==========================================
class OrderCreate(BaseModel):
    """
    Pydantic 安检模型：加入了 Field 字段精细化约束
    """
    # 商品名称：必填(...)，长度限制 2 到 30 个字符
    item_name: str = Field(..., min_length=2, max_length=30, description="商品名称")
    
    # 购买数量：默认值 1，必须大于 0 (gt=0 防御负数和零)
    quantity: int = Field(default=1, gt=0, description="购买数量，必须大于 0")
    
    # 是否加急：默认值 False
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