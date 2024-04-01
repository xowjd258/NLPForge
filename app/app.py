from fastapi import FastAPI, Request, APIRouter
from starlette.concurrency import run_in_threadpool, iterate_in_threadpool
from sse_starlette.sse import EventSourceResponse
from functools import partial
from pydantic import Field
import os
import anyio
import time
from typing import (List,Iterator)
from anyio.streams.memory import MemoryObjectSendStream
import json
from type import WaybillItem, EventItem, MarketReportRequest, ChatbotMessage
from dotenv import load_dotenv
from module import models

from fastapi.middleware.cors import CORSMiddleware

load_dotenv()


app = FastAPI(   title="NLPForge",
    version="0.0.1",
    description="An all-in-one NLP suite for enhancing language tasks, from data analysis to chatbot creation.",
    contact={
    "name": "T.J. KIM",
    "email": "xowjd258@hanyang.ac.kr",
    },
    license_info={
    "name": "Apache 2.0",
    "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
    },
    openapi_url="/api/v1/openapi.json")
# 모델 정의
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# 라우터 정의
waybill_router = APIRouter(prefix="/waybills", tags=["Waybills"])
event_router = APIRouter(prefix="/events", tags=["Events"])
market_router = APIRouter(prefix="/market-reports", tags=["Market Reports"])
chatbot_router = APIRouter(prefix="/chatbot", tags=["Chatbot"])

# 라우터에 엔드포인트 추가
@waybill_router.post("/classify")
async def classify_waybill(item: WaybillItem):
    return item

@event_router.post("/analyze")
async def analyze_event(item: EventItem):
    return item

@market_router.post("/generate")
async def generate_market_report(request: MarketReportRequest):
    return request

@chatbot_router.post("/interact")
async def interact_with_chatbot(message: ChatbotMessage):
    target_model = models.ChatModelInvoker()
    question = message.message
    answer = target_model.generate_response(question=question)
    return answer

@chatbot_router.post("/interact/gpt3")
async def interact_with_chatbot(message: ChatbotMessage):
    target_model = models.ChatGPTAPIResponder()
    question = message.message
    answer = target_model.get_response(question=question)
    return answer

@chatbot_router.post("/interact/phi")
async def interact_with_chatbot(message: ChatbotMessage):
    target_model = models.phi_instance
    question = message.message
    answer = target_model.get_response(question=question)
    return answer

# 라우터 등록
app.include_router(waybill_router)
app.include_router(event_router)
app.include_router(market_router)
app.include_router(chatbot_router)

if __name__ == '__main__':
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=5050, log_level="debug")
