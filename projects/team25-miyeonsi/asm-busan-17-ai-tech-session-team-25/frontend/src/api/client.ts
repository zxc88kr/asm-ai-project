import axios from 'axios';
import type { ChatRequest, TurnResult } from '../types';
import { mockChat } from './mock';

const API_BASE = import.meta.env.VITE_API_BASE ?? '/api';
// 기본값: 목업 ON. 실제 백엔드 연결 시 .env에 VITE_USE_MOCK=false 설정.
const USE_MOCK = import.meta.env.VITE_USE_MOCK !== 'false';
const MOCK_DELAY_MS = 400; // 로딩 연출 확인용 인위적 지연

export async function postChat(req: ChatRequest): Promise<TurnResult> {
  if (USE_MOCK) {
    await new Promise((resolve) => setTimeout(resolve, MOCK_DELAY_MS));
    return mockChat(req);
  }
  const { data } = await axios.post<TurnResult>(`${API_BASE}/chat`, req);
  return data;
}
