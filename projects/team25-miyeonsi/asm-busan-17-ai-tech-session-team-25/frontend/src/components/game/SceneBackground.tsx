import { getBackground } from '../../config/scenes';

interface Props {
  chapter: number;
}

export default function SceneBackground({ chapter }: Props) {
  return (
    <img
      key={chapter}
      src={getBackground(chapter)}
      alt=""
      className="absolute inset-0 h-full w-full object-cover animate-fade-in"
      onError={(e) => {
        (e.currentTarget as HTMLImageElement).style.visibility = 'hidden';
      }}
    />
  );
}
