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


app = FastAPI(
    title="NLPForge",
    version="0.0.1",
    description="데이터 분석부터 챗봇 생성까지 언어 작업을 향상시키기 위한 NLP 통합 솔루션을 제공합니다.",
    contact={
        "name": "T.J. KIM",
        "email": "xowjd258@hanyang.ac.kr",
    },
    license_info={
        "name": "Apache 2.0",
        "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
    },
    openapi_url="/api/v1/openapi.json"
)
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
    """
    운송장 아이템을 분류하는 엔드포인트입니다. 운송장 데이터를 받아서 분류 작업을 수행하고, 그 결과를 반환합니다.
    Args:
        item (WaybillItem): 분류할 운송장 아이템.
    Returns:
        WaybillItem: 분류된 운송장 아이템.
    """
    return item

@event_router.post("/analyze")
async def analyze_event(item: EventItem):
    """
    이벤트 아이템을 분석하는 엔드포인트입니다. 이벤트 데이터를 받아서 분석 작업을 수행하고, 그 결과를 반환합니다.
    Args:
        item (EventItem): 분석할 이벤트 아이템.
    Returns:
        EventItem: 분석된 이벤트 아이템.
    """ 
    return item

@market_router.post("/generate")
async def generate_market_report(request: MarketReportRequest):
    """
    시장 보고서를 생성하는 엔드포인트입니다. 시장 보고서 생성에 필요한 데이터를 받아서 보고서를 생성하고, 그 결과를 반환합니다.
    Args:
        request (MarketReportRequest): 시장 보고서 생성 요청 데이터.
    Returns:
        MarketReportRequest: 생성된 시장 보고서 데이터.
    """
    return request

@chatbot_router.post("/interact")
async def interact_with_chatbot(message: ChatbotMessage):
    """
    챗봇과의 기본 상호작용을 처리하는 엔드포인트입니다. 사용자의 메시지를 받아 챗봇 모델로부터 응답을 생성하고 반환합니다.
    Args:
        message (ChatbotMessage): 사용자로부터의 챗봇 메시지.
    Returns:
        dict: 챗봇의 응답 메시지.
    """ 
    target_model = models.ChatModelInvoker()
    question = message.message
    answer = target_model.generate_response(question=question)
    return answer

@chatbot_router.post("/interact/gpt3")
async def interact_with_chatbot(message: ChatbotMessage):
    """
    GPT-3 모델을 사용하여 챗봇과 상호작용하는 엔드포인트입니다. 사용자의 메시지를 받아 GPT-3 모델로부터 응답을 생성하고 반환합니다.
    Args:
        message (ChatbotMessage): 사용자로부터의 챗봇 메시지.
    Returns:
        dict: 챗봇의 응답 메시지.
    """    
    target_model = models.ChatGPTAPIResponder()
    question = message.message
    answer = target_model.get_response(question=question)
    return answer

@chatbot_router.post("/interact/phi")
async def interact_with_chatbot(message: ChatbotMessage):
    """
    phi 모델을 사용하여 챗봇과 상호작용하는 엔드포인트입니다. 사용자의 메시지를 받아 phi 모델로부터 응답을 생성하고 반환합니다.
    Args:
        message (ChatbotMessage): 사용자로부터의 챗봇 메시지.
    Returns:
        dict: 챗봇의 응답 메시지.
    """
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
