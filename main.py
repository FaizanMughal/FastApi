from fastapi import FastAPI, Form, Request, HTTPException
from fastapi.responses import JSONResponse
from datetime import datetime
import redis
import json

# Initialize the FastAPI app
app = FastAPI()

# Initialize Redis client
redis_client = redis.StrictRedis(host="redis", port=6379, decode_responses=True)

# Middleware for skipping authentication (for testing)
@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    # Skip authentication for development/testing
    return await call_next(request)

# Root Endpoint
@app.get("/")
async def read_root():
    """
    Root endpoint: Provides a welcome message.
    """
    return {"message": "Welcome to the FastAPI Task Manager!"}

# Create Task Endpoint
@app.post("/create-task/")
async def create_task(task_name: str = Form(...)):
    """
    POST endpoint to create a task.
    """
    try:
        current_time = datetime.now().isoformat()
        redis_client.set(task_name, current_time)
        return {"task_name": task_name, "created_at": current_time}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Redis error: {str(e)}")

# Get All Tasks Endpoint
@app.get("/tasks/")
async def get_tasks():
    """
    GET endpoint to retrieve all created tasks.
    """
    try:
        keys = redis_client.keys("*")
        tasks = {key: redis_client.get(key) for key in keys}
        return {"tasks": tasks}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Redis error: {str(e)}")

# Test Redis Connection Endpoint
@app.get("/test-redis/")
async def test_redis():
    """
    Test Redis connection.
    """
    try:
        redis_client.ping()
        return {"message": "Redis is working!"}
    except Exception as e:
        return {"error": f"Redis connection error: {str(e)}"}

# Get Template JSON Endpoint
@app.get("/get-template/")
async def get_template():
    """
    GET endpoint to retrieve the template.json content.
    """
    try:
        with open("template.json", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Template file not found.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading template: {str(e)}")

# Update Template JSON Endpoint
@app.post("/fill-template/")
async def fill_template(template_data: dict):
    """
    POST endpoint to update the template.json content.
    """
    try:
        with open("template.json", "w") as file:
            json.dump(template_data, file)
        return {"message": "Template updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating template: {str(e)}")
