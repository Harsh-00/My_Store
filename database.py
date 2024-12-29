from redis_om import get_redis_connection
from dotenv import load_dotenv
import os

load_dotenv()

redis=get_redis_connection(
    host=os.getenv("REDIS_ENDPOINT"),
    port=os.getenv("REDIS_PORT"),
    password=os.getenv("REDIS_PASSWORD"),
    decode_responses=True
)
 