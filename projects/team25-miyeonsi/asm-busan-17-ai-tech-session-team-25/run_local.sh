#!/usr/bin/env bash
# Travel Mate Agent - 로컬 실행 스크립트 (Mac/Linux)
# 실행 순서: 프론트엔드 빌드 → backend/static 복사 → FastAPI 서버 시작

set -euo pipefail

# ── 경로 설정 ─────────────────────────────────────────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FRONTEND_DIR="$SCRIPT_DIR/frontend"
BACKEND_DIR="$SCRIPT_DIR/backend"
STATIC_DIR="$BACKEND_DIR/static"
VENV_DIR="$SCRIPT_DIR/.venv"

# ── .env 체크 ─────────────────────────────────────────────────────────────────
if [ ! -f "$SCRIPT_DIR/.env" ]; then
    echo "[WARNING] .env 파일이 없습니다."
    echo "          .env 템플릿을 참고해 API 키를 설정하세요."
    echo "          키 없이 실행하면 LLM/항공권 API는 더미 모드로 동작합니다."
    echo ""
fi

# .env 에서 PORT 값 추출 (없으면 기본값 8000)
PORT=8000
if [ -f "$SCRIPT_DIR/.env" ]; then
    _PORT=$(grep -E '^PORT=' "$SCRIPT_DIR/.env" | tail -1 | sed 's/^PORT=//' | tr -d ' "')
    [ -n "$_PORT" ] && PORT="$_PORT"
fi

# ── 의존성 체크 ───────────────────────────────────────────────────────────────
if ! command -v node &>/dev/null; then
    echo "[ERROR] Node.js 가 설치되어 있지 않습니다. https://nodejs.org 에서 설치하세요."
    exit 1
fi
if ! command -v npm &>/dev/null; then
    echo "[ERROR] npm 이 설치되어 있지 않습니다."
    exit 1
fi

# ── 1. 프론트엔드 빌드 ────────────────────────────────────────────────────────
echo ""
echo "┌─────────────────────────────────────────┐"
echo "│  [1/3] 프론트엔드 빌드                   │"
echo "└─────────────────────────────────────────┘"
cd "$FRONTEND_DIR"
npm install --silent
VITE_USE_MOCK=false npm run build
echo "✓ 프론트엔드 빌드 완료 → frontend/dist/"

# ── 2. 빌드 결과물 복사 ───────────────────────────────────────────────────────
echo ""
echo "┌─────────────────────────────────────────┐"
echo "│  [2/3] backend/static 으로 복사          │"
echo "└─────────────────────────────────────────┘"
rm -rf "$STATIC_DIR"
cp -r "$FRONTEND_DIR/dist" "$STATIC_DIR"
echo "✓ 복사 완료 → backend/static/"

# ── 3. FastAPI 서버 시작 ──────────────────────────────────────────────────────
echo ""
echo "┌─────────────────────────────────────────┐"
echo "│  [3/3] FastAPI 서버 시작                 │"
echo "└─────────────────────────────────────────┘"

cd "$SCRIPT_DIR"

# 가상환경이 있으면 활성화
if [ -d "$VENV_DIR" ]; then
    # shellcheck source=/dev/null
    source "$VENV_DIR/bin/activate"
    echo "✓ 가상환경 활성화: .venv"
fi

# Python / uvicorn 의존성 확인
if ! python -c "import uvicorn" &>/dev/null; then
    echo "[INFO] uvicorn 이 없어 requirements.txt 를 설치합니다..."
    pip install -r "$BACKEND_DIR/requirements.txt" --quiet
fi

echo ""
echo "  Travel Mate Agent 실행 중..."
echo "  URL: http://localhost:$PORT"
echo "  종료: Ctrl+C"
echo ""

cd "$BACKEND_DIR"
uvicorn app.main:app --host 0.0.0.0 --port "$PORT" --reload
