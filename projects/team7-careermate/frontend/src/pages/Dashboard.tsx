import { useEffect, useMemo, useState } from 'react';
import {
  Bell,
  ChevronDown,
  Route,
  Layers,
  CircleCheck,
  TrendingUp,
  Rocket,
  Building2,
} from 'lucide-react';
import Sidebar from '../components/Sidebar';
import ProgressBar from '../components/ProgressBar';
import { roadmapApi } from '../api/client';
import type { RoadmapViewResponse } from '../types/api';
import {
  PHASES,
  toRoadmapViewResponse,
  mockRoadmap,
  mockInitialCompletedItems,
} from '../data/mockData';
import styles from './Dashboard.module.css';

interface DashboardProps {
  initialData?: RoadmapViewResponse | null;
  onRestart?: () => void;
}

export default function Dashboard({ initialData, onRestart }: DashboardProps) {
  const [data, setData] = useState<RoadmapViewResponse>(initialData ?? mockRoadmap);
  const [completed, setCompleted] = useState<Set<number>>(new Set(mockInitialCompletedItems));
  const [skillModalOpen, setSkillModalOpen] = useState(false);

  // 진입 시 실제 로드맵을 조회. 실패하면(미연동) 목 데이터를 그대로 사용합니다.
  useEffect(() => {
    if (initialData) return;

    let alive = true;
    roadmapApi
      .get()
      .then((res) => {
        if (!alive) return;
        setData(toRoadmapViewResponse(res));
      })
      .catch((err) => {
        console.warn('로드맵 조회 실패 — 데모 데이터를 사용합니다:', err?.message ?? err);
      });
    return () => {
      alive = false;
    };
  }, []);

  // 주차별 항목을 전역 인덱스와 함께 평탄화
  const flatItems = useMemo(() => {
    const result: { phaseIndex: number; localIndex: number; globalIndex: number; label: string }[] = [];
    let g = 0;
    PHASES.forEach((phase, phaseIndex) => {
      const items = data.roadmap[phase.key];
      items.forEach((label, localIndex) => {
        result.push({ phaseIndex, localIndex, globalIndex: g, label });
        g += 1;
      });
    });
    return result;
  }, [data]);

  const itemsByPhase = useMemo(
    () => PHASES.map((_, i) => flatItems.filter((it) => it.phaseIndex === i)),
    [flatItems]
  );

  const phaseStats = itemsByPhase.map((items) => {
    const total = items.length;
    const done = items.filter((it) => completed.has(it.globalIndex)).length;
    return { total, done, percent: total === 0 ? 0 : Math.round((done / total) * 100) };
  });

  const totalItems = flatItems.length;
  const totalDone = flatItems.filter((it) => completed.has(it.globalIndex)).length;
  const overallPercent = totalItems === 0 ? 0 : Math.round((totalDone / totalItems) * 100);

  const currentPhaseIndex = Math.max(0, Math.min(PHASES.length - 1, data.currentWeek - 1));
  const currentStat = phaseStats[currentPhaseIndex] ?? { total: 0, done: 0, percent: 0 };

  const toggleItem = (globalIndex: number) => {
    setCompleted((prev) => {
      const next = new Set(prev);
      if (next.has(globalIndex)) next.delete(globalIndex);
      else next.add(globalIndex);

      // TODO: PATCH /api/users/roadmap 구현 후 진행 상황 저장을 다시 연결합니다.
      // roadmapApi
      //   .updateProgress({ completedItems: Array.from(next).sort((a, b) => a - b) })
      //   .catch((err) => console.warn('진행 상황 저장 실패:', err?.message ?? err));

      return next;
    });
  };

  return (
    <div className="app-shell">
      <Sidebar active="roadmap" onNavigate={(key) => key === 'home' && onRestart?.()} />

      <main className="app-main">
        {/* 상단 바 */}
        <div className={styles.topbar}>
          <div className={styles.greetingBlock}>
            <h1 className={styles.greeting}>
              민지님, 오늘도 성장하는 하루 되세요! <Rocket size={20} className={styles.rocket} />
            </h1>
            <p className={styles.greetingSub}>{data.recommendedPath}를 향한 여정을 응원해요.</p>
          </div>
          <div className={styles.topbarRight}>
            <button type="button" className={styles.iconButton} aria-label="알림">
              <Bell size={18} />
            </button>
            <button type="button" className={styles.userChip}>
              <span className={styles.avatar}>김</span>
              <span>김민지</span>
              <ChevronDown size={15} />
            </button>
          </div>
        </div>

        {/* 요약 카드 4개 */}
        <div className={styles.statGrid}>
          <StatCard
            icon={<Route size={18} />}
            label="추천 경로"
            value={data.recommendedPath}
            valueAccent
          />
          <StatCard
            icon={<Layers size={18} />}
            label="필요 역량"
            value={`${data.skillGaps.length}개 필요 역량`}
            action="상세 보기"
            onAction={() => setSkillModalOpen(true)}
          />
          <StatCard
            icon={<CircleCheck size={18} />}
            label="이번 주 목표"
            value={`${currentStat.done} / ${currentStat.total} 완료`}
          />
          <StatCard
            icon={<TrendingUp size={18} />}
            label="전체 진행률"
            value={`${overallPercent}%`}
            footer={<ProgressBar percent={overallPercent} variant="primary" />}
          />
        </div>

        <section className={`card ${styles.companyCard}`}>
          <div className={styles.companyHead}>
            <span className={styles.companyIcon}>
              <Building2 size={18} />
            </span>
            <div>
              <h2 className={styles.companyTitle}>적합 회사</h2>
              <p className={styles.companySub}>채용공고 기반</p>
            </div>
          </div>
          <div className={styles.companyList}>
            {data.companies.length > 0 ? (
              data.companies.map((company) => (
                <span key={company} className={styles.companyChip}>
                  {company}
                </span>
              ))
            ) : (
              <span className={styles.companyEmpty}>추천 회사 정보가 없습니다.</span>
            )}
          </div>
        </section>

        {/* 8주 로드맵 */}
        <section className={`card ${styles.roadmapCard}`}>
          <div className={styles.cardHead}>
            <h2 className={styles.cardTitle}>8주 커리어 로드맵</h2>
          </div>
          <div className={styles.roadmapGrid}>
            {PHASES.map((phase, i) => {
              const stat = phaseStats[i];
              const items = itemsByPhase[i];
              return (
                <div key={phase.key} className={styles.phaseCol}>
                  <div className={styles.phaseRange}>{phase.range}</div>
                  <div className={styles.phaseTitle}>{phase.title}</div>
                  <ul className={styles.taskList}>
                    {items.map((it) => {
                      const done = completed.has(it.globalIndex);
                      return (
                        <li key={it.globalIndex}>
                          <button
                            type="button"
                            className={`${styles.task} ${done ? styles.taskDone : ''}`}
                            onClick={() => toggleItem(it.globalIndex)}
                          >
                            <span className={`${styles.checkbox} ${done ? styles.checkboxOn : ''}`} />
                            <span>{it.label}</span>
                          </button>
                        </li>
                      );
                    })}
                  </ul>
                  <div className={styles.phaseProgress}>
                    <span className={styles.phaseProgressLabel}>진행률 {stat.percent}%</span>
                    <ProgressBar percent={stat.percent} />
                  </div>
                </div>
              );
            })}
          </div>
        </section>
      </main>

      {skillModalOpen && (
        <div className={styles.modalBackdrop} role="presentation" onClick={() => setSkillModalOpen(false)}>
          <section
            className={styles.modal}
            role="dialog"
            aria-modal="true"
            aria-labelledby="skill-gap-title"
            onClick={(event) => event.stopPropagation()}
          >
            <div className={styles.modalHead}>
              <h2 id="skill-gap-title" className={styles.modalTitle}>
                필요 역량 상세
              </h2>
              <button
                type="button"
                className={styles.modalClose}
                aria-label="닫기"
                onClick={() => setSkillModalOpen(false)}
              >
                x
              </button>
            </div>
            <ul className={styles.skillList}>
              {data.skillGaps.map((skillGap) => (
                <li key={skillGap} className={styles.skillItem}>
                  {skillGap}
                </li>
              ))}
            </ul>
          </section>
        </div>
      )}
    </div>
  );
}

/* ───────── 보조 컴포넌트 ───────── */

function StatCard({
  icon,
  label,
  value,
  action,
  onAction,
  valueAccent,
  footer,
}: {
  icon: React.ReactNode;
  label: string;
  value: string;
  action?: string;
  onAction?: () => void;
  valueAccent?: boolean;
  footer?: React.ReactNode;
}) {
  return (
    <div className={`card ${styles.statCard}`}>
      <div className={styles.statTop}>
        <span className={styles.statIcon}>{icon}</span>
        <span className={styles.statLabel}>{label}</span>
      </div>
      <div className={`${styles.statValue} ${valueAccent ? styles.statValueAccent : ''}`}>{value}</div>
      {footer}
      {action && (
        <button type="button" className="link-action" onClick={onAction}>
          {action}
        </button>
      )}
    </div>
  );
}
