import { Check } from 'lucide-react';

const STEPS = ['진단', '목표 설정', '로드맵', '실행'];

interface StepperProps {
  /** 현재 단계 (1부터 시작) */
  current: number;
}

export default function Stepper({ current }: StepperProps) {
  return (
    <div
      style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        gap: 0,
      }}
    >
      {STEPS.map((label, i) => {
        const step = i + 1;
        const isDone = step < current;
        const isActive = step === current;
        const isLast = i === STEPS.length - 1;
        return (
          <div key={label} style={{ display: 'flex', alignItems: 'center' }}>
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 8 }}>
              <span
                style={{
                  width: 30,
                  height: 30,
                  borderRadius: '50%',
                  display: 'grid',
                  placeItems: 'center',
                  fontSize: 13,
                  fontWeight: 600,
                  background: isActive || isDone ? 'var(--primary)' : '#eef1f6',
                  color: isActive || isDone ? '#fff' : 'var(--text-faint)',
                  transition: 'background 0.2s ease',
                }}
              >
                {isDone ? <Check size={15} strokeWidth={3} /> : step}
              </span>
              <span
                style={{
                  fontSize: 13,
                  fontWeight: isActive ? 600 : 500,
                  color: isActive ? 'var(--text)' : 'var(--text-faint)',
                }}
              >
                {label}
              </span>
            </div>
            {!isLast && (
              <span
                style={{
                  width: 64,
                  height: 2,
                  margin: '0 8px',
                  marginBottom: 26,
                  background: step < current ? 'var(--primary)' : '#e6e9f0',
                }}
              />
            )}
          </div>
        );
      })}
    </div>
  );
}
