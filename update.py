import time
from database import redis
from models import Order

key="refund-order"
group="payment-group"

# Create a group
try:
    redis.xgroup_create(name=key,groupname=group,mkstream=True)
    print(f"Created group {group}")
except Exception as e:
    print(str(e))
    print(f"Group {group} already exists")

# Listen for new messages
# key:">" means listen for all messages
while True:
    try:
        result=redis.xreadgroup(groupname=group,consumername=key,streams={key:">"} )
        print(result)
        if result:
            for res in result:
                obj=res[1][0][1] 
                order=Order.get(obj["pk"])
                order.status="refunded"
                    
                order.save()
                print(order.dict())
    except Exception as e:
        print(str(e))
    time.sleep(3)
