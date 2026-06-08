import os
import json
from pydantic import BaseModel, Field
from typing import Optional
from openai import OpenAI
from dotenv import load_dotenv

# 로컬 .env 파일로부터 환경 변수 자동 로드
load_dotenv()

# 1. 입력 및 출력 데이터 스키마 정의 (팀원 변수명 및 사양에 맞춤)
class OnboardingInput(BaseModel):
    majorAndYear: str = Field(description="전공/학년")
    currentStatus: str = Field(description="현재 상태")
    interests: list[str] = Field(description="관심분야")
    targetJob: str = Field(description="목표 직무")
    preferredCompanyType: str = Field(description="희망 회사 유형")
    availableTime: str = Field(description="준비 가능 기간/시간")
    concerns: list[str] = Field(description="현재 고민")

class ProfileDiagnosis(BaseModel):
    # 온보딩 원본 보존 필드는 main.py와 겹치므로 완전히 제거하여 스키마 경량화
    summary: str = Field(description="현재 사용자의 전공, 상태, 고민 등을 종합하여 취업 준비 상태와 배경 맥락을 2-3문장으로 간결하게 정리한 요약본")
    strengths: list[str] = Field(description="온보딩 정보를 기반으로 추출된 사용자의 상대적 강점/유리한 조건")
    weaknesses: list[str] = Field(description="목표 직무 대비 보완해야 할 상대적 약점/불리한 조건")
    evidence: dict[str, str] = Field(description="strengths, weaknesses 등의 판단 근거가 된 온보딩 입력 문항 매핑")

# 2. 시스템 프롬프트 정의 (4대 분석 필드 특화 및 가짜 데이터 도출 차단)
SYSTEM_PROMPT = """
You are the CareerMate Profile Diagnosis Agent.
Your task is to analyze the user's structured onboarding profile and output a comprehensive, unified diagnosis JSON matching the schema.

You must append the diagnostic analysis (summary, strengths, and weaknesses) based strictly on the user onboarding fields.

[CORE CONSTRAINTS]
1. ABSOLUTELY NO HALLUCINATION: DO NOT extrapolate, assume, or fabricate any skills, projects, certifications, or experiences that are not explicitly provided in the input. Prevent any guessing-based fake data.
2. `summary` Generation Rule:
   - Create a dense 2-3 sentence context that summarizes:
     a) The user's current academic/career background.
     b) Their specific target job and interest domains.
     c) Key constraints (e.g., availableTime) and major concerns.
3. `strengths` & `weaknesses` Rule:
   - Identify strengths based on majorAndYear relevance (e.g., CS major targeting developer roles) or interest alignment.
   - Identify weaknesses based on lack of majorAndYear relevance (non-CS transitioning to IT), low availableTime (e.g. less than 15 hours per week), or key concerns selected.
   - NEVER append source texts, colons, brackets, or code to items in the `strengths` and `weaknesses` lists. Keep them as pure nominal concepts (e.g., "전공 일치도", "가용 시간 부족", "개발 경험 부족").
4. `evidence` Rule:
   - For every key listed in `strengths` and `weaknesses`, map the exact strength/weakness name to the relevant raw select-box value from the input.

[VALID MATCHING EXAMPLE]
{
  "summary": "경영학 전공의 취업 준비생으로, 백엔드 및 클라우드 개발에 관심이 있으나 개발 경험이 전무한 상태입니다. 주당 10시간의 다소 한정된 준비 시간과 개발 기초 부족에 대한 고민을 안고 취업을 준비하고 있습니다.",
  "strengths": ["경영학적 비즈니스 도메인 지식"],
  "weaknesses": ["개발 경험 부족", "주당 가용 시간 부족"],
  "evidence": {
    "경영학적 비즈니스 도메인 지식": "majorAndYear: '경영학과 졸업'",
    "개발 경험 부족": "concerns: ['IT로 이직하고 싶은데 개발 경험이 아예 없습니다.']",
    "주당 가용 시간 부족": "availableTime: '주당 10시간'"
  }
}

[JSON SCHEMA]
Your output MUST be a valid JSON object matching the ProfileDiagnosis schema.
"""

# 3. 호출할 클래스 인터페이스 정의
class Agent1:
    async def default(
        self,
        major: str,
        currentStatus: str,
        interests: list[str],
        targetJob: str,
        preferredCompanyType: str,
        availableTime: str,
        concerns: list[str],
        pdfBytes : bytes # pdf byte데이터 추가 부분
    ) -> dict:
        """
        백엔드 팀원의 main.py 호출 규격과 100% 연동되는 동기식 에이전트 1 메인 실행 메서드입니다.
        """
        # 1. 7개의 개별 변수를 하나의 검증된 Pydantic 구조로 변환
        user_input = OnboardingInput(
            majorAndYear=major,
            currentStatus=currentStatus,
            interests=interests,
            targetJob=targetJob,
            preferredCompanyType=preferredCompanyType,
            availableTime=availableTime,
            concerns=concerns
        )
        
        api_key = os.getenv("UPSTAGE_API_KEY")
        if not api_key:
            raise ValueError("환경 변수 UPSTAGE_API_KEY가 설정되지 않았습니다.")
            
        # 2. 동기식 OpenAI 호환 클라이언트 가동
        client = OpenAI(
            api_key=api_key,
            base_url="https://api.upstage.ai/v1"
        )
        
        user_prompt = f"User Onboarding Profile:\n{user_input.model_dump_json(indent=2)}"
        
        # 3. Solar API 동기식 호출 진행
        response = await client.chat.completions.create(
            model="solar-pro3",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.1
        )
        
        output_text = response.choices[0].message.content
        parsed_data = json.loads(output_text)
        
        # 4. 출력 스키마 정합성 검증 후 딕셔너리로 반환 (summary, strengths, weaknesses, evidence 반환)
        profile_diagnosis = ProfileDiagnosis.model_validate(parsed_data)
        
        # main.py를 수정하지 않고 터미널에서 검증하기 위한 디버그 출력 추가
        print("\n================ [Agent1 Profile Diagnosis Output] ================")
        print(json.dumps(profile_diagnosis.model_dump(), ensure_ascii=False, indent=2))
        print("===================================================================\n")
        
        return profile_diagnosis.model_dump()