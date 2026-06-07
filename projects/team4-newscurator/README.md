# 뉴스 요약 큐레이터 에이전트

선호 언론사, 관심 분야, 직접 키워드를 선택하면 최신 뉴스를 수집하고, 중복을 줄인 뒤 핵심 내용을 요약해 보여주는 개인 맞춤형 뉴스 브리핑 서비스입니다.

## 주요 기능

- 공개 RSS가 확인된 언론사 선택 및 검색
- 관심 분야 선택
- 직접 키워드 추가
- 제외 키워드로 불필요한 기사 필터링
- 조건 프로필 저장 및 재사용
- 추천 프리셋으로 빠른 브리핑 생성
- 공개 RSS 피드 기반 실제 뉴스 수집
- 언론사 RSS 상태 확인
- 기사 필터링 및 중복 제거
- Upstage Solar 기반 요약 또는 로컬 fallback 요약
- 기사 우선순위 점수 및 선정 기준 표시
- 브리핑 생성 기준 표시
- 최근 브리핑 기록 저장 및 다시 보기
- 원문 링크 제공
- NewsAPI 키 없이도 동작하는 RSS 수집
- RSS 수집 실패 시 동작하는 샘플 데이터 fallback

## 실행 방법

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
uvicorn backend.app.main:app --reload --port 8000
```

브라우저에서 `http://127.0.0.1:8000`을 열면 됩니다.

## 사용 흐름

1. 서버를 실행하고 `http://127.0.0.1:8000`에 접속합니다.
2. `추천 프리셋`을 선택하거나 언론사, 관심 분야, 추가 키워드를 직접 설정합니다.
3. 기간과 기사 수를 정한 뒤 `브리핑 생성`을 클릭합니다.
4. RSS 수집 결과, 공통 핵심 이슈, 기사별 요약, 선정 기준, 원문 링크를 확인합니다.
5. 좌측 `최근 브리핑`에서 저장된 브리핑을 다시 열 수 있습니다.

## 환경 변수

`.env` 파일에 아래 값을 넣으면 실제 API를 사용합니다.

- `NEWS_API_KEY`: NewsAPI 키
- `UPSTAGE_API_KEY`: Upstage API 키
- `UPSTAGE_MODEL`: 요약에 사용할 Upstage 모델명. 기본값은 `solar-pro3`
- `UPSTAGE_BASE_URL`: Upstage API base URL. 기본값은 `https://api.upstage.ai/v1`

`NEWS_API_KEY`는 선택 사항입니다. 기본 뉴스 수집은 비용 없는 공개 RSS 피드를 먼저 사용하고, RSS 수집이 실패할 때만 내장 샘플 기사로 전환합니다.

`UPSTAGE_API_KEY`를 비워두면 로컬 요약 로직으로 실행됩니다.

## API

- `GET /health`: 서버 상태 확인
- `GET /api/sources`: 지원 언론사 목록
- `GET /api/sources/status`: 언론사 RSS 상태 점검
- `GET /api/topics`: 지원 관심 분야 목록
- `GET /api/presets`: 추천 프리셋 목록
- `GET /api/demo-scenarios`: 기존 호환용 프리셋 목록
- `GET /api/profiles`: 저장 프로필 목록
- `POST /api/profiles`: 현재 조건 프로필 저장
- `DELETE /api/profiles/{profile_id}`: 저장 프로필 삭제
- `POST /api/briefings`: 뉴스 브리핑 생성
- `GET /api/briefings/history`: 최근 브리핑 기록 목록
- `GET /api/briefings/{briefing_id}`: 저장된 브리핑 상세 조회

요청 예시:

```json
{
  "sources": ["yonhap", "mk", "hankyung"],
  "topics": ["ai", "economy"],
  "custom_keywords": ["로봇", "바이오"],
  "exclude_keywords": ["스포츠", "연예"],
  "date_range": "7d",
  "limit": 5
}
```

## 프로젝트 구조

```text
backend/
  app/
    main.py
    catalog.py
    config.py
    db.py
    models.py
    news_client.py
    sample_data.py
    service.py
    summarizer.py
web/
  index.html
  styles.css
  app.js
```
