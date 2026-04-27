from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

# 1. Initialize the Server
app = FastAPI(title="Enterprise Swarm API", version="1.0")


