from redis_om import HashModel
from database import redis

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
    class Meta:
        database= redis
 