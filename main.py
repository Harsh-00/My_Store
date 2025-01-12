from fastapi import FastAPI,HTTPException 
from fastapi.middleware.cors import CORSMiddleware 
from models import ProductOrder,Order 
from redis_om.model.model import NotFoundError
import requests 
from dotenv import load_dotenv
import os
from fastapi.background import BackgroundTasks
from database import redis
import time  
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()
warehouse_url=os.getenv("WAREHOUSE_URL")

app=FastAPI() 

origins = [f'{os.getenv("FRONT_URL")}',"http://localhost:5173"] 
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
    logger.info(f"Received order request: {productOrder}")
    try:
        req=requests.get(f'{warehouse_url}/product/{productOrder.product_id}')
        if req.status_code!=200:
            raise HTTPException(status_code=404, detail="Product not found")
        
        product=req.json() 

        order=Order(
            product_id=productOrder.product_id,
            product_name=product['name'],
            price=product['price'],
            fee=round(product['price']*productOrder.quantity *0.1, 2),
            total=round(product['price']*productOrder.quantity*1.1, 2),
            quantity=productOrder.quantity,
            status="pending",
            created_at= datetime.utcnow().isoformat()
        )

        order.save()
        logger.info(f"Order created: {order.pk}")

        background_tasks.add_task(update_order_status,order) 
        return order
    except Exception as e:
        logger.error(f"Failed to create order: {e}")
        raise HTTPException(status_code=500, detail=str(e))

def update_order_status(order: Order):
    try:
        time.sleep(4)
        order.status="completed"
        order.save() 
        logger.info(f"Order status updated: {order.pk}")
        redis.xadd(name="order-completed",fields=order.dict())
    except Exception as e:
        logger.error(f"Failed to process order: {e}")
         

@app.get("/orders/all")
def get_orders():
    logger.info("Fetching all orders")
    try:
        orders = [detailed_order(pk) for pk in Order.all_pks()]
        logger.info(f"Fetched {len(orders)} orders")
        return orders
    except Exception as e:
        logger.error(f"Failed to fetch orders: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    
def detailed_order(pk):
    try:
        order = Order.get(pk)
        return order.dict()
    except NotFoundError:
        logger.error(f"Order not found: {pk}")
        raise HTTPException(status_code=404, detail="Order not found")
    except Exception as e:
        logger.error(f"Failed to fetch order {pk}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/orders/{pk}")
def get_order(pk: str):
    logger.info(f"Fetching order: {pk}")
    try:
        order = Order.get(pk)
        return order
    except NotFoundError:
        logger.error(f"Order not found: {pk}")
        raise HTTPException(status_code=404, detail="Order not found")
    except Exception as e:
        logger.error(f"Failed to fetch order {pk}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    
@app.delete("/orders/delete")
def delete_orders():
    logger.info("Deleting all orders")
    try:
        for pk in Order.all_pks():
            Order.delete(pk)
        logger.info("All orders deleted")
        return {"message": "All orders deleted"}
    except Exception as e:
        logger.error(f"Failed to delete orders: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/orders/{pk}")
def delete_order(pk: str):
    logger.info(f"Deleting order: {pk}")
    try:
        Order.delete(pk)
        logger.info(f"Order deleted: {pk}")
        return {"message": "Order deleted"}
    except NotFoundError:
        logger.error(f"Order not found: {pk}")
        raise HTTPException(status_code=404, detail="Order not found")
    except Exception as e:
        logger.error(f"Failed to delete order {pk}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))    










