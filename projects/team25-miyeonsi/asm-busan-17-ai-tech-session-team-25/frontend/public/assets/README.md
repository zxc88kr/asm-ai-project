# 에셋 파일 가이드 (나슬님)

아래 경로/파일명 그대로 이미지를 넣으면 코드 수정 없이 자동 반영됩니다.
(파일이 아직 없어도 앱은 깨지지 않고 해당 이미지만 숨김 처리됩니다.)

## 캐릭터 표정 (characters/)
`emotion_code`에 1:1로 매핑됩니다.
- `idle.png`     기본
- `smile.png`    웃음
- `sad.png`      슬픔
- `surprise.png` 놀람

## 배경 (backgrounds/)
챕터 번호에 매핑됩니다.
- `ch1.png`, `ch2.png`, `ch3.png` ... 챕터별 배경
- `ending.png`   엔딩 배경 (next_chapter >= 900)
- `default.png`  매핑되지 않은 챕터용 기본 배경 (fallback)

## 권장 사항
- 배경: 가로형(16:9), PNG 또는 WebP.
- 캐릭터: 배경 투명 PNG. 4종 표정의 크기/위치(눈높이)를 통일하면 표정 교체가 자연스럽습니다.
- 챕터가 늘어나면 `frontend/src/config/scenes.ts`의 `BACKGROUNDS` 맵에 한 줄씩 추가하면 됩니다.
