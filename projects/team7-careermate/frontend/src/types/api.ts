// CareerMate API 타입 정의
// API 명세서 3차 기준 타입 정의입니다.

/** 회원가입 / 로그인 공용 요청 바디 */
export interface AuthRequest {
  email: string;
  password: string;
}

/** 단순 메시지 응답 (회원가입 / 로그인 / 할일 체크) */
export interface MessageResponse {
  message: string;
}

/** 로드맵 생성 요청 (온보딩 입력값) — POST /api/users/roadmap */
export interface RoadmapCreateRequest {
  /** 전공/학년 (예: "컴퓨터공학과/3학년") */
  majorAndYear: string;
  /** 현재 상태 (예: "학생 (취업 준비 중)") */
  currentStatus: string;
  /** 관심 분야 (복수) */
  interests: string[];
  /** 목표 직무 */
  targetJob: string;
  /** 희망 회사 유형 */
  preferredCompanyType: string;
  /** 준비 가능 시간 (예: "10-15시간") */
  availableTime: string;
  /** 현재 고민 (복수) */
  concerns: string[];
  /** 보유 역량 (선택, PDF 분석 결과와 함께 백엔드에서 활용) */
  ownedSkills?: string[];
}

/** 로드맵 생성 요청 파일 필드 */
export interface RoadmapCreatePayload {
  requestDatas: RoadmapCreateRequest;
  pdfFile: File;
}

/** 주차별 로드맵 항목 */
export interface Roadmap {
  week1To2: string[];
  week3To4: string[];
  week5To6: string[];
  week7To8: string[];
}

/** 로드맵 생성 응답 — POST /api/users/roadmap */
export interface RoadmapCreateResponse {
  recommendedPath: string;
  skillGaps: string[];
  roadmap: Roadmap;
  /** Agent2 결과 기반 적합 회사 */
  companies: string[];
}

/** 주차별 완료 개수 */
export interface RoadmapProgress {
  week1To2: number;
  week3To4: number;
  week5To6: number;
  week7To8: number;
}

/** 로드맵 조회 응답 — GET /api/users/roadmap */
export interface RoadmapViewResponse extends RoadmapCreateResponse {
  progress: RoadmapProgress;
  /** 현재 진행 중인 주차 단계 (1~4) */
  currentWeek: number;
}

/** 할일 체크 요청 — PATCH /api/users/roadmap */
export interface RoadmapProgressUpdateRequest {
  /** 완료한 항목들의 전역 인덱스 배열 */
  completedItems: number[];
}
