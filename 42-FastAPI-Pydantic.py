from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

# 1. Initialize the Server
app = FastAPI(title="Enterprise Swarm API", version="1.0")


# 2. Define the strict Data Contracts (The Request and the Response)
class UserRequest(BaseModel):
    user_id: str
    prompt: str


class SwarmResponse(BaseModel):
    manager_routing: str
    final_answer: str


