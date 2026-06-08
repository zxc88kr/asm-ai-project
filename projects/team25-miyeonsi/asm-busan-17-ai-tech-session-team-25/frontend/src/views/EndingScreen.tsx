import { useGameStore } from '../store/useGameStore';
import { getEndingBackground } from '../config/scenes';

export default function EndingScreen() {
  const affinity = useGameStore((s) => s.affinity);
  const reset = useGameStore((s) => s.reset);

  return (
    <div className="relative flex h-full w-full flex-col items-center justify-center gap-6">
      <img
        src={getEndingBackground(affinity)}
        alt=""
        className="absolute inset-0 h-full w-full object-cover"
        onError={(e) => {
          (e.currentTarget as HTMLImageElement).style.visibility = 'hidden';
        }}
      />
      <div className="relative z-10 flex flex-col items-center gap-6 rounded-2xl bg-game-navy/80 p-10">
        <h2 className="text-3xl font-bold text-game-pink">🎬 여행 끝!</h2>
        <p className="text-white/90">최종 호감도: ♥ {affinity}</p>
        <button
          onClick={reset}
          className="rounded-full bg-game-pink px-8 py-3 font-semibold text-white transition-colors hover:bg-game-pink-dark"
        >
          다시 하기
        </button>
      </div>
    </div>
  );
}
