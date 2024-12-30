from fastapi import FastAPI 
from fastapi.middleware.cors import CORSMiddleware 
from models import ProductOrder,Order 
import requests 
from dotenv import load_dotenv
import os
from fastapi.background import BackgroundTasks
from database import redis
import time  

app=FastAPI() 
load_dotenv()
warehouse_url=os.getenv("WAREHOUSE_URL")


origins = ["http://localhost:3000"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"My": "Store"}

@app.post("/orders")
def create_order(productOrder: ProductOrder,background_tasks: BackgroundTasks):
    req=requests.get(f'{warehouse_url}/product/{productOrder.product_id}')
    product=req.json()
    fee=product['price']*0.2

    order=Order(
        product_id=productOrder.product_id,
        price=product['price'],
        fee=fee,
        total=product['price']+fee,
        quantity=productOrder.quantity,
        status="pending"
    )

    order.save()
    background_tasks.add_task(update_order_status,order) 
    return order

def update_order_status(order: Order):
    time.sleep(4)
    order.status="completed"
    order.save() 
    redis.xadd(name="order-completed",fields=order.dict())
    


@app.get("/orders/all")
def get_orders():
    return [detailed_order(pk) for pk in Order.all_pks()]
def detailed_order(pk):
    order= Order.get(pk)
    return order.dict()


@app.get("/orders/{pk}")
def get_order(pk: str): 
    return Order.get(pk)







