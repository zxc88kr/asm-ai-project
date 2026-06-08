from fastapi import FastAPI, File, Form, UploadFile
from pydantic import BaseModel
from typing import List
import json

# 태민님 agent
from agents.ProfileDiagnosisAgent.ProfileDiagnosisAgent import Agent1

# 태환님 agent
from agents.agent2.Agent2 import Agent2

# 보라님 agent
from agents.agent3.Agent3 import Agent3

app = FastAPI()

# 테스트 url
@app.get("/api/test")
def home():
    return {"message": "fastapi 테스트"}

# 로드맵 생성 api
class RoadmapRequest(BaseModel): # 로드맵 생성 request 모델
    majorAndYear: str              # 전공/학년
    currentStatus: str             # 현재 상태
    interests: List[str]           # 관심 분야
    ownedSkills: List[str] = []    # 보유 스킬 (Agent3 갭 계산용, 선택)
    targetJob: str                 # 목표 직무
    preferredCompanyType: str      # 희망 회사 유형
    availableTime: str             # 준비 가능 시간
    concerns: List[str]            # 현재 고민

class Roadmap(BaseModel): # 로드맵 모델
    week1To2: List[str]
    week3To4: List[str]
    week5To6: List[str]
    week7To8: List[str]


class RoadmapResponse(BaseModel): # 로드맵 response 모델
    recommendedPath: str
    skillGaps: List[str]
    roadmap: Roadmap
    companies : List[str]

@app.post(
        "/api/users/roadmap",
        response_model=RoadmapResponse
        )
async def makeRoadMap(
        pdfFile: UploadFile = File(...),
        requestDatas: str = Form(...)
    ):
    # request 테스트용 코드
    # print("전공 학년: ", request.majorAndYear) 
    # print("현재 상태: ", request.currentStatus)
    # print("관심 분야: ", request.interests)
    # print("목표 직무: ", request.targetJob)
    # print("희망 회사 유형: ", request.preferredCompanyType)
    # print("준비 가능 시간: ", request.availableTime)
    # print("현재 고민: ", request.concerns)

    # 데이터 파싱
    request = RoadmapRequest(**json.loads(requestDatas)); # JSON 데이터

    pdfBytes = await pdfFile.read(); # pdf byte 데이터

    # agent1 사용
    agent1 = Agent1();
    agent1Result = await agent1.default(
        request.majorAndYear,
        request.currentStatus, 
        request.interests, 
        request.targetJob,
        request.preferredCompanyType,
        request.availableTime,
        request.concerns,
        pdfBytes # 추가 부분
      )
    # print("agent1 결과: ", agent1Result)

    # agent2 사용
    agent2 = Agent2();
    agent2Result = await agent2.default(
        request.targetJob, 
        request.preferredCompanyType, 
        4
      )
    # print("agent2 결과: ", agent2Result)

    # agent3 사용 (갭 분석 + 주차별 로드맵 생성)
    agent3 = Agent3();
    agent3Result = await agent3.default(request, agent1Result, agent2Result)

    return RoadmapResponse(
        recommendedPath=agent3Result["recommendedPath"],
        skillGaps=agent3Result["skillGaps"],
        roadmap=Roadmap(**agent3Result["roadmap"]),
        companies=agent2Result["companies"], # 회사 부분 추가
    )
