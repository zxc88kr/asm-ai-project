import { useGameStore } from '../store/useGameStore';
import SceneBackground from '../components/game/SceneBackground';
import CharacterSprite from '../components/game/CharacterSprite';
import AffinityGauge from '../components/game/AffinityGauge';
import SelectionMenu from '../components/game/SelectionMenu';
import DialogueBox from '../components/chat/DialogueBox';
import ChatInput from '../components/chat/ChatInput';

export default function GameScreen() {
  const currentChapter = useGameStore((s) => s.currentChapter);
  const emotion = useGameStore((s) => s.emotion);
  const affinity = useGameStore((s) => s.affinity);

  return (
    <div className="relative h-full w-full overflow-hidden">
      <SceneBackground chapter={currentChapter} />
      <CharacterSprite emotion={emotion} />
      <div className="absolute inset-x-0 top-0 p-4">
        <AffinityGauge affinity={affinity} />
      </div>
      <div className="absolute inset-x-0 bottom-0 flex flex-col gap-2 p-4">
        <DialogueBox />
        <SelectionMenu />
        <ChatInput />
      </div>
    </div>
  );
}
