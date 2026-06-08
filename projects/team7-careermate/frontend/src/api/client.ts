// CareerMate API 클라이언트
// 백엔드 주소는 .env 의 VITE_API_BASE_URL 로 설정합니다. (없으면 "/api" 사용 → 개발 중 프록시 권장)

import type {
  AuthRequest,
  MessageResponse,
  RoadmapCreatePayload,
  RoadmapCreateResponse,
  RoadmapViewResponse,
  RoadmapProgressUpdateRequest,
} from '../types/api';

const BASE_URL = import.meta.env.VITE_API_BASE_URL ?? '/api';

export class ApiError extends Error {
  public status: number;

  constructor(status: number, message: string) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
  }
}

interface RequestOptions {
  method?: 'GET' | 'POST' | 'PATCH' | 'PUT' | 'DELETE';
  body?: unknown;
}

function isFormData(body: unknown): body is FormData {
  return typeof FormData !== 'undefined' && body instanceof FormData;
}

async function request<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const { method = 'GET', body } = options;
  const formData = isFormData(body);

  const res = await fetch(`${BASE_URL}${path}`, {
    method,
    headers: formData ? undefined : { 'Content-Type': 'application/json' },
    // 로그인 시 발급되는 token 쿠키를 주고받기 위해 필요
    credentials: 'include',
    body: body !== undefined ? (formData ? body : JSON.stringify(body)) : undefined,
  });

  if (!res.ok) {
    let message = res.statusText;
    try {
      const data = await res.json();
      if (data?.message) message = data.message;
    } catch {
      /* 응답 본문이 JSON이 아닐 수 있음 */
    }
    throw new ApiError(res.status, message);
  }

  if (res.status === 204) return undefined as T;
  return (await res.json()) as T;
}

export const authApi = {
  /** 회원가입 — POST /api/users/signup */
  signup: (body: AuthRequest) =>
    request<MessageResponse>('/users/signup', { method: 'POST', body }),

  /** 로그인 — POST /api/users/login (성공 시 token 쿠키 발급) */
  login: (body: AuthRequest) =>
    request<MessageResponse>('/users/login', { method: 'POST', body }),
};

function createRoadmapFormData({ requestDatas, pdfFile }: RoadmapCreatePayload): FormData {
  const formData = new FormData();
  formData.append('requestDatas', JSON.stringify(requestDatas));
  formData.append('pdfFile', pdfFile);
  return formData;
}

export const roadmapApi = {
  /** 로드맵 생성 — POST /api/users/roadmap */
  create: (body: RoadmapCreatePayload) =>
    request<RoadmapCreateResponse>('/users/roadmap', {
      method: 'POST',
      body: createRoadmapFormData(body),
    }),

  /** 로드맵 + 진행 현황 조회 — GET /api/users/roadmap */
  get: () => request<RoadmapViewResponse>('/users/roadmap'),

  /** 할일 체크 (진행 상황 업데이트) — PATCH /api/users/roadmap */
  updateProgress: (body: RoadmapProgressUpdateRequest) =>
    request<MessageResponse>('/users/roadmap', { method: 'PATCH', body }),
};
