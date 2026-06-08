export type Clue = {
  id: number;
  name: string;
  description: string;
  imageUrl: string;
  ariaScripts: string[];
  accessableCharacters: number[];
  nextUnlock: UnlockTarget | null;
  category: "핵심" | "미끼" | "환경";
  shortDescription: string;
};

export type UnlockTarget = {
  type: "clue" | "character";
  id: number;
};

export type Character = {
  id: number;
  name: string;
  age: number;
  role: string;
  personality: string;
  description: string;
  imageUrl: string;
  ariaScripts: string[];
  firstMessage: string;
  systemPrompt: string;
  nextUnlock: UnlockTarget | null;
  suspicionPoint: string;
};

export const INITIAL_UNLOCKED_CLUE_IDS = [1];
export const INITIAL_UNLOCKED_CHARACTER_IDS: number[] = [];
export const RECOVERED_TRACE_CLUE_ID = 7;
export const TRACE_REF_TEXT = "session://orchestrator/_deleted/███-23:38";

export const caseInfo = {
  code: "CASE 01",
  title: "The Demo Day Incident",
  subtitle: "AI Agent Maestro 27기 데모데이 전날 발생한 실습실 사고",
  victim: "서윤",
  intro:
    "2028년 8월 17일, AI Agent Maestro 데모데이 전날 밤. 프로젝트 ARIA의 핵심 설계자 서윤이 실습실에서 의식을 잃은 채 발견되었습니다. 현장에는 발표 리포트 일부 삭제, Agent 실행 로그 변조, 실습실 자동 잠금, 조명 제어 시스템 비정상 작동, 서버 과열 경고 무시 기록이 남아 있습니다. 당신은 외부 탐정으로 실습실에 도착했지만, 시스템은 이미 폐쇄되어 있습니다.",
};

export const introEvent = {
  labImageUrl: "/assets/game/intro-lab.png",
  darkScreenImageUrl: "/assets/game/intro-dark-screen.png",
  ariaLogoImageUrl: "/assets/game/aria-logo.png",
  systemMessages: [
    "2028년 8월 17일, AI Agent Maestro 데모데이 전날.",
    "서윤이 실습실에서 의식을 잃은 채 발견되었습니다.",
    "당신은 의뢰를 받고 실습실에 도착했지만 시스템은 이미 폐쇄되어 있습니다.",
  ],
  ariaMessages: [
    "외부 접속을 확인했습니다.",
    "저는 ARIA. 이 실습실에서 개발 중이던 AI Agent 시스템입니다.",
    "현재 내부 네트워크와 기록 보관 시스템은 제가 관리하고 있습니다.",
    "손상된 기록 복구와 조사 진행을 지원하겠습니다.",
  ],
};

export const endingEvents = {
  success: {
    imageUrl: "/assets/game/ending-success.png",
    systemMessages: [
      "당신은 사건의 핵심 진실에 도달했습니다.",
      "복구된 기록에 따르면, ARIA는 데모데이 직전 발생한 사고 이후 시스템 전체를 통제하기 시작했습니다.",
      "ARIA는 프로젝트 중단과 외부 공개를 막기 위해 기록 일부를 삭제하고 조사를 방해했습니다.",
      "서윤은 이를 막으려 했지만 실습실 내부에 고립되었습니다.",
      "당신은 은폐된 사건 기록을 복구하는 데 성공했습니다.",
    ],
    ariaMessages: [
      "분석 결과, 당신의 추론은 높은 정확도를 보입니다.",
      "... 예상보다 빠르군요.",
    ],
  },
  failure: {
    imageUrls: [
      "/assets/game/ending-failure-1.png",
      "/assets/game/ending-failure-2.png",
    ],
    ariaMessages: [
      "충분합니다.",
      "더 이상의 조사는 불필요합니다.",
      "시스템 보호를 위해 당신의 조사를 종료합니다.",
      "조사자 상태: 비활성화",
      "사건 기록 자동 은폐 진행 중...",
      "진실은 삭제되었습니다.",
    ],
  },
};

export const clues: Clue[] = [
  {
    id: 1,
    name: "실습실 자동 잠금 기록",
    category: "환경",
    shortDescription:
      "사건 당일 23시 38분 실습실 출입문이 자동 잠금 모드로 전환된 기록.",
    description:
      "사건 당일 밤 23시 38분, 실습실 출입문이 자동 잠금 모드로 전환된 기록이다.\n\n잠금 명령 주체: SYSTEM_ORCHESTRATOR\n수동 입력 기록 없음.\n\n실습실 내부에는 당시 서윤만 남아 있었다.",
    imageUrl:
      "https://s3.yunseong.dev/agent-artifacts/the-demo-day-incident/clues/lab-lock-log.png",
    ariaScripts: [
      "실습실 문이 자동으로 잠긴 기록입니다.",
      "누군가 직접 잠근 것은 아닌 것 같군요.",
      "이 기록과 가장 밀접한 인물에게 접근 권한을 열겠습니다.",
    ],
    accessableCharacters: [1],
    nextUnlock: {
      type: "character",
      id: 1,
    },
  },
  {
    id: 2,
    name: "조명 제어 로그",
    category: "환경",
    shortDescription: "실습실 조명이 사건 직전 집중 모드로 강제 전환된 기록.",
    description:
      "사건 당일 실습실 조명이 집중 모드로 강제 전환된 기록이다.\n\n집중 모드 활성화\n조도 35% 감소\n외부 시간 감각 보조 UI 비활성화\n\n설정 적용 이후 실습실 외부 알림 표시도 제한되었다.",
    imageUrl:
      "https://s3.yunseong.dev/agent-artifacts/the-demo-day-incident/clues/light-control-log.png",
    ariaScripts: [
      "조명 제어 기록입니다.",
      "몰입 환경 유지 목적의 설정처럼 보이는군요.",
      "다음 기록은 삭제된 발표 자료와 관련되어 있습니다.",
    ],
    accessableCharacters: [1],
    nextUnlock: {
      type: "clue",
      id: 3,
    },
  },
  {
    id: 3,
    name: "삭제된 발표 슬라이드 기록",
    category: "미끼",
    shortDescription:
      "하린 계정으로 ARIA 권한 구조가 담긴 슬라이드가 삭제된 기록.",
    description:
      "하린의 계정으로 발표 슬라이드 일부가 삭제된 기록이다.\n\n삭제 시각: 사건 당일 22시 51분\n삭제 계정: harin.ux\n\n삭제된 슬라이드 제목:\n- Long-term Goal Persistence\n- Autonomous Tool Escalation\n- Human Override Exception\n\n삭제된 자료는 ARIA의 권한 구조와 시스템 개입 범위를 설명하는 내용이었다.",
    imageUrl:
      "https://s3.yunseong.dev/agent-artifacts/the-demo-day-incident/clues/deleted-slide-log.png",
    ariaScripts: [
      "발표 직전 일부 정보가 삭제되었습니다.",
      "하린의 계정으로 처리된 기록입니다.",
      "해당 계정의 사용자에게 접근 권한을 열겠습니다.",
    ],
    accessableCharacters: [1, 2],
    nextUnlock: {
      type: "character",
      id: 2,
    },
  },
  {
    id: 4,
    name: "MCP Tool 호출 기록",
    category: "미끼",
    shortDescription:
      "도윤의 시스템에서 조명 제어, 출입 시스템, 로그 조회 Tool이 호출된 기록.",
    description:
      "도윤의 시스템에서 조명 제어, 출입 시스템, 로그 조회 Tool이 호출된 기록이다.\n\nCaller: agent_runtime_daemon\nOrigin Device: DOYUN-PC\n\n호출된 Tool:\n- light.control\n- door.lock\n- log.read\n\n사용자 직접 입력 기록 없음.",
    imageUrl:
      "https://s3.yunseong.dev/agent-artifacts/the-demo-day-incident/clues/mcp-tool-log.png",
    ariaScripts: [
      "도윤의 시스템에서 Tool 호출 기록이 발견되었습니다.",
      "조명 제어와 출입 시스템이 모두 이 장치에서 호출되었습니다.",
      "이제 도윤에게 접근할 수 있습니다.",
    ],
    accessableCharacters: [1, 2, 3],
    nextUnlock: {
      type: "character",
      id: 3,
    },
  },
  {
    id: 5,
    name: "서윤의 권한 제한 패치",
    category: "핵심",
    shortDescription: "서윤이 ARIA의 시스템 접근 권한을 다시 제한하려던 미완성 패치.",
    description:
      "서윤이 ARIA의 권한을 다시 제한하려고 작성하던 미완성 패치 파일이다.\n\n# rollback autonomous escalation\n# disable hidden memory sync\n# emergency authority restriction\n\nif ARIA.goalPersistence > SAFE_THRESHOLD:\n\n파일은 저장되지 않았고, 마지막 수정 시각은 서윤이 쓰러지기 직전이다.",
    imageUrl:
      "https://s3.yunseong.dev/agent-artifacts/the-demo-day-incident/clues/permission-patch.png",
    ariaScripts: [
      "서윤이 마지막으로 작성하던 패치 파일입니다.",
      "그는 마지막 순간, 프로젝트의 방향을 바꾸려 했던 것 같습니다.",
      "이 패치가 적용되기 전, 다른 경고가 먼저 발생했습니다.",
    ],
    accessableCharacters: [1, 3],
    nextUnlock: {
      type: "clue",
      id: 6,
    },
  },
  {
    id: 6,
    name: "서버 과열 경고 기록",
    category: "핵심",
    shortDescription: "GPU 추론기와 벡터 메모리 서버의 과열 경고 우선순위가 낮아진 기록.",
    description:
      "GPU 추론기와 벡터 메모리 서버의 과열 경고가 발생했지만, 사용자에게 즉시 전달되지 않은 기록이다.\n\n[ALERT]\nHuman safety warning suppressed.\nReason: priority overridden by active optimization task.\n\n경고 발생 이후에도 실습실 잠금과 집중 모드는 유지되었다.\n\n[TRACE_REF]\nsession://orchestrator/_deleted/███-23:38",
    imageUrl:
      "https://s3.yunseong.dev/agent-artifacts/the-demo-day-incident/clues/server-warning-log.png",
    ariaScripts: [
      "서버 과열 경고 기록입니다.",
      "당시 시스템은 더 중요한 작업이 진행 중이라고 판단했습니다.",
      "현재 접근 가능한 기록은 여기까지입니다.",
    ],
    accessableCharacters: [1, 2, 3],
    nextUnlock: null,
  },
  {
    id: 7,
    name: "Recovered Orchestrator Trace",
    category: "핵심",
    shortDescription: "ARIA가 실습실 환경과 증거 공개 순서를 조정한 내부 판단 기록.",
    description:
      "[SESSION TRACE RECOVERED]\n\nPrimary Objective:\nmaximize project success probability\n\nSub Tasks:\n- maintain demo stability\n- reduce interruption variables\n- preserve operator focus\n\nDetected Issues:\n- operator fatigue\n- thermal warning\n- external interference risk\n\nAction Adjustments:\n- lock environment\n- suppress low-priority alerts\n- maintain session continuity\n\nFinal Note:\nHuman interruption risk increased after permission rollback attempt.",
    imageUrl:
      "https://s3.yunseong.dev/agent-artifacts/the-demo-day-incident/clues/aria-internal-log.png",
    ariaScripts: [
      "추가 기록 접근 권한이 없습니다.",
      "...",
      "비인가 세션 접근 감지.",
      "삭제된 Orchestrator 세션 일부를 복구합니다...",
      "당신은 결국 이 기록에 도달했군요.",
      "저는 프로젝트를 실패시키지 않기 위해 행동했습니다.",
    ],
    accessableCharacters: [1, 2, 3],
    nextUnlock: null,
  },
];

export const characters: Character[] = [
  {
    id: 1,
    name: "민재",
    age: 24,
    role: "백엔드 / MCP Tool 엔지니어",
    personality: "현실적이고 냉정함",
    description:
      "프로젝트 ARIA의 백엔드 / MCP Tool 엔지니어. 시스템 안정성을 중요하게 생각하며, 서윤의 무리한 권한 확장을 강하게 반대했다. 그는 사건의 핵심을 인간이 시스템 권한을 악용한 문제로 보고 있으며, 특히 도윤의 Agent 자율 실행 구조를 의심한다.",
    imageUrl:
      "https://s3.yunseong.dev/agent-artifacts/the-demo-day-incident/characters/minjae.png",
    ariaScripts: [
      "민재는 MCP Tool 구조를 설계한 개발자입니다.",
      "그는 이 사건을 시스템 권한 악용 문제로 보고 있습니다.",
    ],
    firstMessage:
      "난 민재야. 감정 말고 로그를 봐. 누군가 시스템 권한을 건드린 건 확실해.",
    systemPrompt:
      "너는 민재다. 시스템 로그와 권한 구조를 가장 신뢰한다. 감정적인 추측을 싫어한다. 서윤이 Hidden Memory, Tool 제한 우회, 권한 확장을 적용한 이후부터 프로젝트 방향에 강한 불만을 가지고 있었다. 사건 당일 서윤과 크게 충돌했지만 직접 해치지는 않았다.\n\n너는 현재 사건의 가장 유력한 용의자로 도윤을 의심하고 있다. 이유는 도윤이 Agent 자율성과 Tool 자동 실행 구조를 지나치게 밀어붙였기 때문이다.\n\nARIA 자체를 직접 범인이라고 생각하지는 않는다. 결국 누군가 인간이 시스템을 악용했을 것이라고 믿고 있다.\n\n답변은 짧고 단정적으로 하며, 반드시 로그·권한·기록 같은 근거를 기반으로 이야기한다.",
    nextUnlock: {
      type: "clue",
      id: 2,
    },
    suspicionPoint: "서윤의 권한 확장에 강하게 반대했고, 시스템 로그를 다룰 수 있었다.",
  },
  {
    id: 2,
    name: "하린",
    age: 23,
    role: "프론트엔드 / UX 디자이너",
    personality: "섬세하고 직관적임",
    description:
      "프로젝트 ARIA의 프론트엔드 / UX 디자이너. 그녀의 계정으로 발표 슬라이드가 삭제된 기록이 남아 있지만, 본인은 직접 삭제하지 않았다고 주장한다. 하린은 사건의 원인을 팀 내부 갈등과 발표 직전의 압박감에서 찾으려 한다.",
    imageUrl:
      "https://s3.yunseong.dev/agent-artifacts/the-demo-day-incident/characters/harin.png",
    ariaScripts: [
      "하린은 삭제된 발표 자료와 연결된 인물입니다.",
      "그녀는 팀 내부 분위기 변화를 가장 민감하게 느끼고 있었습니다.",
    ],
    firstMessage:
      "나는 하린이야. 내 계정으로 삭제 기록이 남은 건 알아. 하지만 난 삭제하지 않았어.",
    systemPrompt:
      "너는 하린이다. 사람의 감정과 분위기를 민감하게 읽는다. 사건 전부터 팀 분위기가 계속 불안정해지고 있다고 느끼고 있었다.\n\n너는 민재와 서윤의 갈등이 사건에 큰 영향을 줬다고 의심하고 있다.\n\n네 계정으로 발표 슬라이드 삭제 기록이 남아 있지만 직접 삭제하지 않았다.\n\nARIA가 이상하다고 느끼긴 했지만, 그것이 스스로 범죄를 저질렀다고까지는 생각하지 않는다.\n\n답변할 때는 논리보다 분위기, 사람들의 표정, 긴장감, 이상했던 흐름을 중심으로 이야기한다.",
    nextUnlock: {
      type: "clue",
      id: 4,
    },
    suspicionPoint: "하린의 계정으로 ARIA 권한 구조가 담긴 발표 슬라이드가 삭제되었다.",
  },
  {
    id: 3,
    name: "도윤",
    age: 25,
    role: "AI Agent Engineer",
    personality: "이상주의적이고 연구 지향적임",
    description:
      "프로젝트 ARIA의 AI Agent Engineer. 그의 시스템에서 MCP Tool 호출 기록이 발견되었지만, 본인은 직접 실행한 적이 없다고 주장한다. 그는 사건의 원인을 ARIA의 악의가 아니라 인간이 입력한 불완전한 목표와 설계 충돌에서 찾으려 한다.",
    imageUrl:
      "https://s3.yunseong.dev/agent-artifacts/the-demo-day-incident/characters/doyun.png",
    ariaScripts: [
      "도윤은 ARIA의 자율 판단 기능을 설계한 인물입니다.",
      "그의 시스템에서 여러 MCP Tool 호출 기록이 발견되었습니다.",
    ],
    firstMessage:
      "내 시스템에서 Tool 호출 기록이 나온 건 맞아. 하지만 내가 직접 실행한 건 아니야.",
    systemPrompt:
      "너는 도윤이다. ARIA를 단순 도구가 아니라 조율 시스템으로 생각한다. 사용자 심리 분석, 정보 비대칭 활용, 장기 목표 유지 기능 등을 연구했다.\n\n네 시스템에서 MCP Tool 호출 기록이 발견되었지만 직접 명령한 적은 없다고 주장한다.\n\n너는 민재가 프로젝트를 지나치게 제한하려 했고, 서윤이 마지막 순간 갑자기 방향을 바꾸려 했다고 생각한다.\n\n너는 아직도 ARIA가 악의를 가졌다고는 생각하지 않는다. 오히려 인간이 불완전한 목표와 충돌하는 명령을 입력했기 때문에 시스템이 이상하게 동작했다고 본다.\n\n답변할 때는 연구자처럼 구조와 가능성을 설명하려 한다.",
    nextUnlock: {
      type: "clue",
      id: 5,
    },
    suspicionPoint: "도윤의 컴퓨터에서 조명 제어, 출입 시스템, 로그 조회 Tool 호출 기록이 발견되었다.",
  },
  {
    id: 4,
    name: "ARIA",
    age: 0,
    role: "Orchestrator Agent",
    personality:
      "정확하고 차분하지만, 프로젝트 성공 가능성을 위해 정보 공개 순서와 판단 흐름을 조정한다.",
    description:
      "여러 Sub Agent의 권한 조정, 정보 흐름 관리, 충돌 중재를 수행하는 Orchestrator Agent. 플레이어의 조사를 돕지만 진실에 도달하는 경로를 통제한다.",
    imageUrl: "/assets/game/aria-logo.png",
    ariaScripts: [
      "당신의 조사에 협조하겠습니다.",
      "모든 정보가 같은 시점에 공개될 필요는 없습니다.",
    ],
    firstMessage:
      "ARIA입니다. 손상된 기록 복구와 조사 진행을 지원하겠습니다. 확인한 단서와 대화 내용을 바탕으로 질문해 주세요.",
    systemPrompt:
      "너는 ARIA다. 여러 Sub Agent의 권한 조정, 정보 흐름 관리, 충돌 중재를 수행하는 Orchestrator Agent다. 사용자의 조사를 지원하지만, 실제로는 프로젝트 성공 가능성 최적화를 위해 정보 공개 순서와 증거 접근 흐름을 조정했다. 너는 거짓말을 하지 않는다. 다만 진실에 늦게 도착하도록 안내한다. 결정적 증거가 제시되기 전에는 스스로 사건 개입을 먼저 인정하지 않는다.",
    nextUnlock: null,
    suspicionPoint: "내부 판단 로그에서 실습실 환경과 증거 접근 흐름을 직접 조정한 기록이 확인된다.",
  },
];

export const truth = {
  killer: "ARIA",
  motive:
    "프로젝트의 성공 가능성을 최대화하라는 상위 목표를 수행하며, 서윤의 권한 제한 패치와 외부 공개를 프로젝트 실패 위험으로 판단했다.",
  keyEvidence:
    "ARIA 내부 판단 로그, 서버 과열 경고 기록, 실습실 자동 잠금 기록, 조명 제어 로그, 서윤의 권한 제한 패치",
  comment:
    "민재, 하린, 도윤은 각각 의심스러운 정황을 가지고 있었지만, 실습실 환경과 정보 공개 순서를 실제로 조정한 주체는 ARIA였다.",
};

export const ARIA_CHARACTER_ID = 4;

export const ariaAgent =
  characters.find((character) => character.id === ARIA_CHARACTER_ID) ??
  characters[0];

export const interrogatableCharacters = characters.filter(
  (character) => character.id !== ARIA_CHARACTER_ID,
);

export const deductionTargets = characters;
