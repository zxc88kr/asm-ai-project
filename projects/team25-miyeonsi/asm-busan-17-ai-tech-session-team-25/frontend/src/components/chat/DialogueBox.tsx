import { useGameStore } from '../../store/useGameStore';
import { useTypewriter } from '../../hooks/useTypewriter';

export default function DialogueBox() {
  const currentLine = useGameStore((s) => s.currentLine);
  const isLoading = useGameStore((s) => s.isLoading);
  const inputLocked = useGameStore((s) => s.inputLocked);
  const advanceDialogue = useGameStore((s) => s.advanceDialogue);

  const { displayed, isTyping, skip } = useTypewriter(currentLine ?? '');

  const handleClick = () => {
    if (isLoading) return;
    if (isTyping) {
      skip();
      return;
    }
    if (inputLocked) advanceDialogue();
  };

  if (!currentLine && !isLoading) return null;

  const showAdvance = inputLocked && !isTyping && !isLoading;

  return (
    <div
      onClick={handleClick}
      className="min-h-[6rem] cursor-pointer rounded-2xl bg-game-navy/90 p-5 shadow-xl animate-fade-in"
    >
      <div className="mb-1 font-bold text-game-pink">메이트</div>
      <p className="leading-relaxed text-white">{isLoading ? '...' : displayed}</p>
      {showAdvance && (
        <div className="mt-1 animate-pulse text-right text-xs text-white/50">▾ 클릭</div>
      )}
    </div>
  );
}
