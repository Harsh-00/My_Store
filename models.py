from redis_om import HashModel
from database import redis
from typing import Optional

class ProductOrder(HashModel):
    product_id: str
    quantity: int   
    class Meta:
        database= redis

class Order(HashModel):
    product_id: str
    price: float
    fee: float
    total: float
    quantity: int
    status: str
    created_at: Optional[str]=None
    class Meta:
        database= redis
 