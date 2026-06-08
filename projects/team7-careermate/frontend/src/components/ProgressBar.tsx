interface ProgressBarProps {
  /** 0~100 */
  percent: number;
  variant?: 'success' | 'primary';
}

export default function ProgressBar({ percent, variant = 'success' }: ProgressBarProps) {
  const clamped = Math.max(0, Math.min(100, percent));
  return (
    <div className="progress-track" role="progressbar" aria-valuenow={clamped} aria-valuemin={0} aria-valuemax={100}>
      <div
        className={`progress-fill ${variant === 'primary' ? 'is-primary' : ''}`}
        style={{ width: `${clamped}%` }}
      />
    </div>
  );
}
