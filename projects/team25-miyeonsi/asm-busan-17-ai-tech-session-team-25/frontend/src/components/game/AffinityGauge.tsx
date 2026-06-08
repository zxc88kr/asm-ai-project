import { AFFINITY_MAX } from '../../config/scenes';

interface Props {
  affinity: number;
  max?: number;
}

export default function AffinityGauge({ affinity, max = AFFINITY_MAX }: Props) {
  const pct = Math.max(0, Math.min(100, (affinity / max) * 100));
  return (
    <div className="flex items-center gap-2 rounded-full bg-game-navy/60 px-3 py-1">
      <span className="font-bold text-game-pink">♥</span>
      <div className="h-3 flex-1 overflow-hidden rounded-full bg-white/70">
        <div
          className="h-full bg-game-pink transition-all duration-500 ease-out"
          style={{ width: `${pct}%` }}
        />
      </div>
      <span className="w-8 text-right text-sm text-white/90">{affinity}</span>
    </div>
  );
}
