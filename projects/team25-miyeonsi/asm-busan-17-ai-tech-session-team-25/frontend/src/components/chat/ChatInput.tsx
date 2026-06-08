import { useState } from 'react';
import { useGameStore } from '../../store/useGameStore';

export default function ChatInput() {
  const [text, setText] = useState('');
  const inputLocked = useGameStore((s) => s.inputLocked);
  const isLoading = useGameStore((s) => s.isLoading);
  const sendMessage = useGameStore((s) => s.sendMessage);

  const disabled = inputLocked || isLoading;

  const handleSend = () => {
    if (disabled || !text.trim()) return;
    void sendMessage(text);
    setText('');
  };

  return (
    <div className="flex gap-2">
      <input
        value={text}
        onChange={(e) => setText(e.target.value)}
        onKeyDown={(e) => {
          if (e.key === 'Enter') handleSend();
        }}
        disabled={disabled}
        placeholder={isLoading ? '응답을 기다리는 중…' : inputLocked ? '대사를 클릭해 진행하세요…' : '메시지를 입력하세요…'}
        className="flex-1 rounded-full px-4 py-2 text-game-navy disabled:opacity-50"
      />
      <button
        onClick={handleSend}
        disabled={disabled}
        className="rounded-full bg-game-pink px-6 py-2 font-semibold text-white transition-colors hover:bg-game-pink-dark disabled:opacity-40"
      >
        전송
      </button>
    </div>
  );
}
