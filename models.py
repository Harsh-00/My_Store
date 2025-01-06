from redis_om import HashModel
from database import redis
from typing import Optional
from pydantic import Field

class ProductOrder(HashModel):
    product_id: str
    quantity: int   
    class Meta:
        database= redis

class Order(HashModel):
    product_id: str
    price: float=Field(...,ge=0)
    fee: float = Field(...,ge=0)
    total: float = Field(...,ge=0)
    quantity: int = Field(...,gt=0)
    status: str
    created_at: Optional[str]=None
    class Meta:
        database= redis
 