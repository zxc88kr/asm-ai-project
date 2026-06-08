import { useEffect, useRef, useState } from 'react';

const SPEED_MS = 30;

export function useTypewriter(text: string) {
  const [displayed, setDisplayed] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null);

  useEffect(() => {
    let i = 0;
    setDisplayed('');
    if (!text) {
      setIsTyping(false);
      return;
    }
    setIsTyping(true);
    timerRef.current = setInterval(() => {
      i += 1;
      setDisplayed(text.slice(0, i));
      if (i >= text.length) {
        if (timerRef.current) clearInterval(timerRef.current);
        timerRef.current = null;
        setIsTyping(false);
      }
    }, SPEED_MS);
    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
    };
  }, [text]);

  const skip = () => {
    if (timerRef.current) {
      clearInterval(timerRef.current);
      timerRef.current = null;
    }
    setDisplayed(text);
    setIsTyping(false);
  };

  return { displayed, isTyping, skip };
}
