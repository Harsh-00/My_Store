from fastapi import FastAPI 
from fastapi.middleware.cors import CORSMiddleware 
from models import ProductOrder,Order 
import requests 
from dotenv import load_dotenv
import os
from fastapi.background import BackgroundTasks
from database import redis
import time  
from datetime import datetime

app=FastAPI() 
load_dotenv()
warehouse_url=os.getenv("WAREHOUSE_URL")

origins = [f'{os.getenv("FRONT_URL")}'] 
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

    order=Order(
        product_id=productOrder.product_id,
        price=product['price'],
        fee=round(product['price']*productOrder.quantity *0.1, 2),
        total=round(product['price']*productOrder.quantity*1.1, 2),
        quantity=productOrder.quantity,
        status="pending",
        created_at= datetime.utcnow().isoformat()
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

@app.delete("/orders/delete")
def delete_orders():
    for pk in Order.all_pks():
        Order.delete(pk)
    return {"message":"All orders deleted"}







