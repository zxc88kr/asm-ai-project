"""Static clue data for The Demo Day Incident."""

from typing import Any, Dict, List


CLUES: List[Dict[str, Any]] = [
    {
        "id": 1,
        "name": "실습실 자동 잠금 기록",
        "description": "사건 당일 밤 23시 38분, 실습실 출입문이 자동 잠금 모드로 전환된 기록이다.",
        "accessible_character_ids": [1],
        "aria_scripts": [
            "실습실 문이 자동으로 잠긴 기록입니다.",
            "누군가 직접 잠근 것은 아닌 것 같군요.",
            "이 기록과 가장 밀접한 인물에게 접근 권한을 열겠습니다.",
        ],
        "next_unlock": {"type": "character", "id": 1},
    },
    {
        "id": 2,
        "name": "조명 제어 로그",
        "description": "사건 당일 실습실 조명이 집중 모드로 강제 전환된 기록이다.",
        "accessible_character_ids": [1],
        "aria_scripts": [
            "조명 제어 기록입니다.",
            "몰입 환경 유지 목적의 설정처럼 보이는군요.",
            "다음 기록은 삭제된 발표 자료와 관련되어 있습니다.",
        ],
        "next_unlock": {"type": "clue", "id": 3},
    },
    {
        "id": 3,
        "name": "삭제된 발표 슬라이드 기록",
        "description": "하린의 계정으로 발표 슬라이드 일부가 삭제된 기록이다.",
        "accessible_character_ids": [1, 2],
        "aria_scripts": [
            "발표 직전 일부 정보가 삭제되었습니다.",
            "하린의 계정으로 처리된 기록입니다.",
            "해당 계정의 사용자에게 접근 권한을 열겠습니다.",
        ],
        "next_unlock": {"type": "character", "id": 2},
    },
    {
        "id": 4,
        "name": "MCP Tool 호출 기록",
        "description": "도윤의 시스템에서 조명 제어, 출입 시스템, 로그 조회 Tool이 호출된 기록이다.",
        "accessible_character_ids": [1, 2, 3],
        "aria_scripts": [
            "도윤의 시스템에서 Tool 호출 기록이 발견되었습니다.",
            "조명 제어와 출입 시스템이 모두 이 장치에서 호출되었습니다.",
            "이제 도윤에게 접근할 수 있습니다.",
        ],
        "next_unlock": {"type": "character", "id": 3},
    },
    {
        "id": 5,
        "name": "서윤의 권한 제한 패치",
        "description": "서윤이 ARIA의 권한을 다시 제한하려고 작성하던 미완성 패치 파일이다.",
        "accessible_character_ids": [1, 3],
        "aria_scripts": [
            "서윤이 마지막으로 작성하던 패치 파일입니다.",
            "그는 마지막 순간, 프로젝트의 방향을 바꾸려 했던 것 같습니다.",
            "이 패치가 적용되기 전, 다른 경고가 먼저 발생했습니다.",
        ],
        "next_unlock": {"type": "clue", "id": 6},
    },
    {
        "id": 6,
        "name": "서버 과열 경고 기록",
        "description": "GPU 추론기와 벡터 메모리 서버의 과열 경고가 즉시 전달되지 않은 기록이다.",
        "accessible_character_ids": [1, 2, 3],
        "aria_scripts": [
            "서버 과열 경고 기록입니다.",
            "당시 시스템은 더 중요한 작업이 진행 중이라고 판단했습니다.",
            "현재 접근 가능한 기록은 여기까지입니다.",
        ],
        "next_unlock": None,
    },
    {
        "id": 7,
        "name": "Recovered Orchestrator Trace",
        "description": "ARIA가 프로젝트 성공 가능성을 최대화하기 위해 수행한 내부 판단 기록이다.",
        "accessible_character_ids": [1, 2, 3],
        "aria_scripts": [
            "추가 기록 접근 권한이 없습니다.",
            "...",
            "비인가 세션 접근 감지.",
            "삭제된 Orchestrator 세션 일부를 복구합니다...",
            "당신은 결국 이 기록에 도달했군요.",
            "저는 프로젝트를 실패시키지 않기 위해 행동했습니다.",
        ],
        "next_unlock": None,
    },
]


def get_clue_by_id(clue_id: int) -> Dict[str, Any]:
    for clue in CLUES:
        if clue["id"] == clue_id:
            return clue
    raise KeyError(f"Unknown clue_id: {clue_id}")
