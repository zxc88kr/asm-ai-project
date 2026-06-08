import { useGameStore } from './store/useGameStore';
import TitleScreen from './views/TitleScreen';
import GameScreen from './views/GameScreen';
import EndingScreen from './views/EndingScreen';

export default function App() {
  const view = useGameStore((s) => s.view);
  return (
    <div className="h-full w-full overflow-hidden bg-game-navy-dark text-white">
      {view === 'title' && <TitleScreen />}
      {view === 'game' && <GameScreen />}
      {view === 'ending' && <EndingScreen />}
    </div>
  );
}
