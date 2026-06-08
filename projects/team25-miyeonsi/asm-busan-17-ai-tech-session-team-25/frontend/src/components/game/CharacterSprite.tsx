import { getSprite } from '../../config/scenes';
import type { EmotionCode } from '../../types';

interface Props {
  emotion: EmotionCode;
}

export default function CharacterSprite({ emotion }: Props) {
  return (
    <img
      key={emotion}
      src={getSprite(emotion)}
      alt={emotion}
      className="absolute bottom-40 left-1/2 h-2/3 -translate-x-1/2 object-contain animate-fade-in pointer-events-none"
      onError={(e) => {
        (e.currentTarget as HTMLImageElement).style.visibility = 'hidden';
      }}
    />
  );
}
