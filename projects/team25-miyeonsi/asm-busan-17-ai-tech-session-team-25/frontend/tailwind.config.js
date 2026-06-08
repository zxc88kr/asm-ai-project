/** @type {import('tailwindcss').Config} */
export default {
    content: [
      "./index.html",
      "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
      extend: {
        // 미연시/비주얼 노벨 특유의 화사하고 몰입감 있는 UI에 어울리는 가상 테마 컬러 정의
        colors: {
          game: {
            pink: {
              light: "#FFF0F5",  // 말풍선 이나 배경용 연한 핑크
              DEFAULT: "#FF69B4",// 호감도 게이지 및 포인트 컬러 (HotPink)
              dark: "#C71585",   // 중요 텍스트 및 강조용
            },
            navy: {
              DEFAULT: "#1E293B", // 가독성 높은 텍스트 및 메인 UI 프레임용
              dark: "#0F172A",
            }
          },
        },
        // 대사창 타이핑 효과나 UI 페이드인을 위한 애니메이션 확장 여지 제공
        animation: {
          'fade-in': 'fadeIn 0.5s ease-out forwards',
        },
        keyframes: {
          fadeIn: {
            '0%': { opacity: '0', transform: 'translateY(10px)' },
            '100%': { opacity: '1', transform: 'translateY(0)' },
          },
        },
      },
    },
    plugins: [],
  }