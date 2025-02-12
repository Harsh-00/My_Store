
FROM python:3.12.8
WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 8001

# Define environment variables
ENV REDIS_ENDPOINT="redis-14982.c301.ap-south-1-1.ec2.redns.redis-cloud.com"
ENV REDIS_PORT="14982"
ENV REDIS_PASSWORD="QcwPbszKlwtfThOCDKEK3NvJljlDOQd8"
ENV FRONT_URL="https://general-inventory.vercel.app"
ENV WAREHOUSE_URL="http://product_service:8000"

# Use a process manager to run multiple processes
RUN apt-get update && apt-get install -y --no-install-recommends supervisor && \
    rm -rf /var/lib/apt/lists/*

# Copy the supervisor configuration file
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Run the application and Redis listener using supervisor
CMD ["supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]