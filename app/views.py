from http.client import HTTPException
import asyncio
from typing import List, Dict, Union, Optional

from fastapi import Body, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError, BaseModel

from services import TwitchMiner

app = FastAPI()

origins = [
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

class Item(BaseModel):
    cookies: List[dict]
    channel_names: List[str]

@app.post('/')
async def run_app_from_cookies(request: Request):
    request_json = await request.json()
    raw_cookies = request_json.get('cookies')
    channel_names = request_json.get('channel_names')
    cookies = {cookie.get('name'): cookie.get('value') for cookie in raw_cookies}

    twich_miner = TwitchMiner(cookies, channel_names)
    asyncio.get_event_loop().create_task(twich_miner.run())

    return