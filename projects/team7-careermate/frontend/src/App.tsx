import { useState } from 'react';
import Onboarding from './pages/Onboarding';
import Dashboard from './pages/Dashboard';
import type { RoadmapViewResponse } from './types/api';

type View = 'onboarding' | 'dashboard';

// 데모용 간단한 화면 전환입니다.
// 실제 라우팅이 필요하면 react-router-dom 으로 /onboarding, /dashboard 를 분리하세요.
export default function App() {
  const [view, setView] = useState<View>('onboarding');
  const [roadmap, setRoadmap] = useState<RoadmapViewResponse | null>(null);

  if (view === 'onboarding') {
    return (
      <Onboarding
        onComplete={(data) => {
          if (data) setRoadmap(data);
          setView('dashboard');
        }}
      />
    );
  }
  return <Dashboard initialData={roadmap} onRestart={() => setView('onboarding')} />;
}
