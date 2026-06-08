import os
import json
import io
import pypdf
from pydantic import BaseModel, Field
from typing import Optional, List, Union
from openai import OpenAI, AsyncOpenAI
from dotenv import load_dotenv

# 로컬 .env 파일로부터 환경 변수 자동 로드
load_dotenv()

# 1. 입력 및 출력 데이터 스키마 정의
class OnboardingInput(BaseModel):
    majorAndYear: str = Field(description="전공/학년")
    currentStatus: str = Field(description="현재 상태")
    interests: List[str] = Field(description="관심분야")
    targetJob: str = Field(description="목표 직무")
    preferredCompanyType: str = Field(description="희망 회사 유형")
    availableTime: str = Field(description="준비 가능 기간/시간")
    concerns: List[str] = Field(description="현재 고민")
    resumeText: Optional[str] = Field(default="", description="사용자 이력서 PDF 파싱 텍스트")

class ProfileDiagnosis(BaseModel):
    summary: str = Field(description="사용자의 전공, 상태, 고민 및 이력서 내용을 종합하여 취업 준비 현황을 요약한 2-3문장의 맥락 요약본")
    strengths: List[str] = Field(description="기준 대비 사용자가 지닌 상대적 강점 명칭 목록")
    weaknesses: List[str] = Field(description="기준 대비 사용자가 보완해야 할 상대적 약점/불리한 조건 목록")
    owned_skills: List[str] = Field(description="사용자의 이력서 및 온보딩 정보에서 추출된 현재 보유 중인 구체적인 기술 스택 및 역량 목록")
    evidence: dict[str, str] = Field(description="strengths, weaknesses 판단의 근거가 된 입력 및 이력서 팩트 매핑 정보")

# 2. 시스템 프롬프트: 기준 대비 사용자 맞춤 채점 및 owned_skills 추출
SYSTEM_PROMPT_EVALUATION = """
You are the CareerMate Career Coach and Profile Diagnostician.
Your task is to compare the user's onboarding profile and their resume text against the "Common Benchmark Requirements" (the core competencies expected in the target field).

[EVALUATION RULES]
1. strengths: Compare the user's resume/profile against the "Common Benchmark Requirements". List the requirements that the user clearly satisfies or possesses as strengths. Suffix with positive terms (e.g., "~ 구현 경험", "~ 역량 보유").
2. weaknesses: List the requirements from the "Common Benchmark Requirements" that the user is missing, lacks, or has insufficient experience in, based on the [WEAKNESS CLASSIFICATION & EXPRESSION RULES]. Also incorporate the user's stated concerns.
3. owned_skills: List the current technical competencies explicitly declared in the user's resume or projects.

[EVALUATION BIAS BY COMPANY TYPE]
{company_evaluation_bias}

[GAP FILTERING RULE BY COMPANY TARGET]
- NOT all missing requirements from the benchmark are automatically classified as "weaknesses".
- You must dynamically prioritize and filter the gaps based on the target company type:
  1. For Enterprise (대기업): If core CS fundamentals, database query optimization, testing coverage, scalability, or large-scale traffic handling are missing, classify them as CRITICAL weaknesses. Startup-focused stacks (e.g., Supabase, Next.js, FastAPI, lean prototyping) missing should NOT be classified as weaknesses.
  2. For Startup (스타트업): If fast MVP prototyping, framework integration, API deployment, or active feature ownership are missing, classify them as weaknesses. Missing large-scale traffic distribution or complex system cost optimization should NOT be classified as weaknesses.
  3. For Foreign/Global (외국계): If clean code, TDD, open-source participation, or technical autonomy are missing, classify them as weaknesses.
- This ensures we do not overwhelm the candidate with irrelevant weaknesses that do not align with their career target.

[WEAKNESS CLASSIFICATION & EXPRESSION RULES]
- When classifying a "weakness", do not just output the requirement name. You must diagnose the exact status of the candidate's gap and suffix it accordingly:
  1. Completely Missing (경험 부재): The user has zero experience or mention of this requirement.
     - Suffix format: "[Requirement] 경험 부재" (e.g., "CI/CD 자동화 경험 부재", "분산 아키텍처 설계 경험 부재")
  2. Listed Only (단순 나열 수준): The tool/tech is only listed in the skills section but has no project details or application context in the resume.
     - Suffix format: "[Requirement] 단순 나열에 그침 (깊이 부족)" (e.g., "Docker 단순 나열에 그침 (깊이 부족)", "Redis 활용 단순 나열에 그침")
  3. Insufficient / Shallow Experience (경험 있으나 깊이 부족): The user has used it in a project, but only at a basic tutorial/CRUD level without deep optimization or advanced usage.
     - Suffix format: "[Requirement] 경험 있으나 깊이 부족" (e.g., "TDD 구현 경험 있으나 깊이 부족", "성능 개선 경험 있으나 깊이 부족")

[CROSS-LINGUAL SEMANTIC MAPPING RULE]
- The Reference Benchmark Requirements may be written in English, while the User's input may be in Korean.
- Map the semantic meaning across Korean and English languages intelligently. (e.g., mapping 'TDD 구현' or '테스트 코드 작성' with 'Test-Driven Development (TDD)' as a strength).

[CORE CONSTRAINTS]
1. STRICTLY NO HALLUCINATION (CRITICAL):
   - Do not assume, guess, or fabricate any skills, tools, or projects for the user.
   - If a technology, tool, or project is NOT explicitly mentioned in the user's onboarding profile or resume text, it MUST NEVER be listed in `owned_skills` or `strengths`.
2. Detailed and Actionable `strengths` & `weaknesses` for Roadmapping:
   - Output specific, clear items (e.g., 'Spring Boot 개발 역량', 'TDD 테스트 작성 경험 있으나 깊이 부족'). Keep them under 30 characters.
3. `evidence`:
   - Map each strength and weakness to the exact source text from the user's onboarding or resume.

[OUTPUT FORMAT]
Your output MUST be a valid JSON object matching the ProfileDiagnosis schema:
{{
  "summary": "현재 사용자의 상황(전공, 이력서 바탕)과 고민을 종합한 2-3문장의 정성 요약",
  "strengths": ["강점 명칭 1", "강점 명칭 2"],
  "weaknesses": ["보완점 명칭 1", "보완점 명칭 2"],
  "owned_skills": ["사용자 이력서에서 추출된 실제 보유 기술 1", "실제 보유 기술 2"],
  "evidence": {{
    "강점 명칭 1": "판단 근거가 된 이력서 또는 온보딩 원본 텍스트",
    "보완점 명칭 1": "판단 근거가 된 이력서 또는 온보딩 원본 텍스트"
  }}
}}
"""

# 3. 회사 유형별 동적 가중치 프롬프트 매핑 헬퍼
def get_company_evaluation_bias(company_type: str) -> str:
    cleaned_company = company_type.replace(" ", "")
    
    if "대기업" in cleaned_company or "중견기업" in cleaned_company or "공공기관" in cleaned_company:
        return """- The user prefers enterprise-level companies.
- Evaluate heavily on CS core fundamentals (Data Structures, Algorithms, OS, Databases), standard software engineering principles, testing coverage, scalability, and handling large-scale traffic or robust production systems.
- Highlight gaps in these areas as weaknesses if missing from the user's profile."""
    elif "스타트업" in cleaned_company or "테크스타트업" in cleaned_company:
        return """- The user prefers tech startups.
- Evaluate heavily on rapid prototyping capability, ownership of feature releases, integration of trendy tech stacks (e.g., FastAPI, Docker, Supabase, Next.js), lean development style, and user feedback-driven features.
- Highlight gaps in practical web/app building or active project execution as weaknesses if missing."""
    elif "외국계" in cleaned_company or "global" in cleaned_company.lower():
        return """- The user prefers global / foreign companies.
- Evaluate heavily on international communication capability (or English documentation skills), contribution to global open-source projects, active community participation, technical autonomy, and clean code/TDD principles.
- Highlight gaps in autonomy or global collaboration experience as weaknesses if missing."""
    else:
        return """- General company target.
- Balance both software engineering fundamentals and practical prototyping experiences."""


# 4. 에이전트 클래스 정의
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
        resumeText: Union[str, bytes] = "" # PDF 텍스트(str) 및 PDF 바이너리(bytes) 수용
    ) -> dict:
        """
        백엔드 팀원의 main.py 호출 규격과 호환되도록 구성된 2단계 비동기 분석 메서드입니다.
        """
        # 0. bytes 데이터인 경우 PDF 텍스트 파싱 수행
        parsed_resume_text = ""
        if isinstance(resumeText, bytes) and resumeText:
            try:
                reader = pypdf.PdfReader(io.BytesIO(resumeText))
                text_parts = []
                for page in reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text_parts.append(page_text)
                parsed_resume_text = "\n".join(text_parts).strip()
            except Exception as e:
                print(f"[Agent1 Error] PDF 바이트 파싱 중 예외 발생: {e}")
                parsed_resume_text = ""
        else:
            parsed_resume_text = resumeText

        # 1. 입력 유효성 검증
        user_input = OnboardingInput(
            majorAndYear=major,
            currentStatus=currentStatus,
            interests=interests,
            targetJob=targetJob,
            preferredCompanyType=preferredCompanyType,
            availableTime=availableTime,
            concerns=concerns,
            resumeText=parsed_resume_text
        )
        
        api_key = os.getenv("UPSTAGE_API_KEY")
        if not api_key:
            raise ValueError("환경 변수 UPSTAGE_API_KEY가 설정되지 않았습니다.")
            
        client = AsyncOpenAI(
            api_key=api_key,
            base_url="https://api.upstage.ai/v1"
        ) # 비동기로 실행하기 위해서 기존의 OpenAI에서 변경하였습니다
        
        # 2. 직무 및 회사 유형에 맞는 JSON 기준서 파일 로드
        cleaned_job = user_input.targetJob.lower().replace(" ", "").replace("_", "")
        job_filename = "BackEndEngineer" # fallback 기본
        if "aiproduct" in cleaned_job:
            job_filename = "AIProductEngineer"
        elif "backend" in cleaned_job:
            job_filename = "BackEndEngineer"
        elif "frontend" in cleaned_job:
            job_filename = "FrontEndEngineer"
        elif "data" in cleaned_job:
            job_filename = "DataEngineer"
        elif "ml" in cleaned_job or "machine" in cleaned_job:
            job_filename = "MLEngineer"
        elif "devops" in cleaned_job or "infra" in cleaned_job:
            job_filename = "DevOpsEngineer"
        
        # 사용자가 외국계 기업을 타겟팅했는지 여부 체크
        is_foreign_target = "외국계" in user_input.preferredCompanyType or "global" in user_input.preferredCompanyType.lower()
        cache_filename = f"criteria_foreign_{job_filename}.json" if is_foreign_target else f"criteria_{job_filename}.json"
        
        current_dir = os.path.dirname(os.path.abspath(__file__))
        cache_file_path = os.path.join(current_dir, "ref_criteria", cache_filename)
        
        # JSON 기준 파일 읽기
        if os.path.exists(cache_file_path):
            with open(cache_file_path, "r", encoding="utf-8") as f:
                stage1_data = json.load(f)
            print(f"ℹ️ [Agent1] JSON 기준 역량 로드 성공: {cache_filename}")
        else:
            raise FileNotFoundError(f"[Agent1 Error] 필수 기준서 JSON 파일이 존재하지 않습니다: {cache_file_path}")
        
        # 3. [2단계 API 호출 준비] 회사 유형 가중치 주입 및 프롬프트 조립
        company_bias = get_company_evaluation_bias(user_input.preferredCompanyType)
        formatted_system_prompt = SYSTEM_PROMPT_EVALUATION.format(company_evaluation_bias=company_bias)
        
        user_prompt = f"""Target IT Role: {user_input.targetJob}

[Common Benchmark Requirements (from 100-point Resumes)]
{json.dumps(stage1_data, ensure_ascii=False, indent=2)}

[User Onboarding Profile]
- majorAndYear: {user_input.majorAndYear}
- currentStatus: {user_input.currentStatus}
- interests: {", ".join(user_input.interests)}
- availableTime: {user_input.availableTime}
- concerns: {", ".join(user_input.concerns)}

[User Resume Text (extracted from PDF)]
{user_input.resumeText if user_input.resumeText else "No resume text provided."}
"""
        
        # 4. [API 호출 진행] 기준 대비 사용자 개별 맞춤 채점 및 owned_skills 추출
        print(f"💡 [Agent1] 기준 대비 사용자 프로필/이력서 정밀 갭 분석 중... (입력 데이터 약 {len(user_prompt)}자)")
        response = await client.chat.completions.create(
            model="solar-pro3",
            messages=[
                {"role": "system", "content": formatted_system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.1,
            timeout=90.0
        ) # 비동기로 변경
        
        output_text = response.choices[0].message.content
        parsed_diagnosis = json.loads(output_text)
        
        # 5. 최종 스키마 정합성 검증 후 딕셔너리로 반환
        profile_diagnosis = ProfileDiagnosis.model_validate(parsed_diagnosis)
        
        print("\n================ [Agent1 Final Output Diagnosis] ================")
        print(json.dumps(profile_diagnosis.model_dump(), ensure_ascii=False, indent=2))
        print("=================================================================\n")
        
        return profile_diagnosis.model_dump()