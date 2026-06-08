# 태환님 agent
import json

from .job_requirement_agent import run_agent2
from .models import Agent2Request


class Agent2:
    async def default(self, targetJob, preferredCompanyType, maxResults):
        request = Agent2Request(
            target_role=targetJob,
            company_type=preferredCompanyType,
            max_results=maxResults,
        )

        result = await run_agent2(request) # 비동기로 처리 하면서 이 부분에 대해서 생각을 해야 할 것 같아요

        output = {
            "companies": [company.name for company in result.companies],
            "required_skills": result.required_skills,
            "preferred_skills": result.preferred_skills,
            "required_experience": result.required_experience,
            "keywords": result.keywords,
        }
        print("\n================ [Agent2 Job Requirement Output] ================")
        print(json.dumps(output, ensure_ascii=False, indent=2))
        print("=================================================================\n")
        return output
