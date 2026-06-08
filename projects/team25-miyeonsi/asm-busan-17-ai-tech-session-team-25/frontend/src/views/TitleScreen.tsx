import { useGameStore } from '../store/useGameStore';

export default function TitleScreen() {
  const startGame = useGameStore((s) => s.startGame);
  return (
    <div className="relative flex h-full w-full flex-col items-center justify-center gap-8">
      <img
        src="/assets/backgrounds/main.png"
        alt=""
        className="absolute inset-0 h-full w-full object-cover"
        onError={(e) => {
          (e.currentTarget as HTMLImageElement).style.visibility = 'hidden';
        }}
      />
      <div className="relative z-10 flex flex-col items-center gap-8 rounded-2xl bg-white/60 px-12 py-10 shadow-xl backdrop-blur-sm">
        <h1 className="text-4xl font-bold text-game-pink-dark drop-shadow">✈️ 나만의 여행 메이트</h1>
        <p className="text-game-navy font-medium">메이트와 대화하며 함께 여행을 떠나보세요</p>
        <button
          onClick={startGame}
          className="rounded-full bg-game-pink px-8 py-3 text-lg font-semibold text-white shadow-lg transition-colors hover:bg-game-pink-dark"
        >
          시작하기
        </button>
      </div>
    </div>
  );
}
