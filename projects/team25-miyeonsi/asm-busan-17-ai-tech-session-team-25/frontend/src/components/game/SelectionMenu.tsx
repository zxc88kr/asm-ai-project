import { useGameStore } from '../../store/useGameStore';

export default function SelectionMenu() {
  const selections  = useGameStore((s) => s.selections);
  const inputLocked = useGameStore((s) => s.inputLocked);
  const isLoading   = useGameStore((s) => s.isLoading);
  const sendMessage = useGameStore((s) => s.sendMessage);

  if (!inputLocked || isLoading || selections.length === 0) return null;

  return (
    <div className="flex flex-col gap-2 animate-fade-in">
      {selections.map((option) => (
        <button
          key={option}
          onClick={() => void sendMessage(option)}
          className="rounded-2xl bg-game-navy/90 px-5 py-3 text-left text-white
                     transition-colors hover:bg-game-pink/80 shadow-md"
        >
          {option}
        </button>
      ))}
    </div>
  );
}
