import { useRef, useState } from 'react';
import {
  GraduationCap,
  Activity,
  Tag,
  Target,
  Building2,
  Clock,
  FileText,
  Sparkles,
  Plus,
  Check,
  X,
} from 'lucide-react';
import Sidebar from '../components/Sidebar';
import Stepper from '../components/Stepper';
import { toRoadmapViewResponse } from '../data/mockData';
import { roadmapApi, ApiError } from '../api/client';
import type { RoadmapCreateRequest, RoadmapViewResponse } from '../types/api';
import styles from './Onboarding.module.css';

const MAJOR_OPTIONS = ['컴퓨터공학과', '소프트웨어학과', '전자공학과', '산업공학과', '경영학과', '기타'];
const YEAR_OPTIONS = ['3학년', '4학년', '졸업예정', '졸업'];
const STATUS_OPTIONS = ['학생 (취업 준비 중)', '학생 (재학 중)', '취업준비생', '인턴', '신입 (사회초년생)'];
const INTEREST_OPTIONS = ['AI/ML', 'Backend', 'Frontend', 'Data', 'DevOps', 'Mobile', 'Security'];
const JOB_OPTIONS = ['AI Product Engineer', 'Backend Engineer', 'Frontend Engineer', 'Data Engineer', 'ML Engineer', 'DevOps Engineer'];
const COMPANY_OPTIONS = ['테크 스타트업', '대기업', '중견기업', '외국계', '공공기관'];
const TIME_OPTIONS = ['5시간 미만', '5-10시간', '10-15시간', '15-20시간', '20시간 이상'];

const CONCERN_OPTIONS = [
  '무엇을 준비해야 할지 모르겠어요',
  'AI/백엔드 중 고민',
  '포트폴리오 방향 설정',
  '면접이 너무 막막해요',
  '나에게 맞는 회사가 궁금해요',
  '기타',
];

interface OnboardingProps {
  /** 로드맵 생성 완료 후 대시보드로 이동 */
  onComplete: (data?: RoadmapViewResponse) => void;
}

export default function Onboarding({ onComplete }: OnboardingProps) {
  const [major, setMajor] = useState('컴퓨터공학과');
  const [year, setYear] = useState('3학년');
  const [currentStatus, setCurrentStatus] = useState('학생 (취업 준비 중)');
  const [interests, setInterests] = useState<string[]>(['AI/ML', 'Backend']);
  const [targetJob, setTargetJob] = useState('AI Product Engineer');
  const [preferredCompanyType, setPreferredCompanyType] = useState('테크 스타트업');
  const [availableTime, setAvailableTime] = useState('10-15시간');
  const [pdfFile, setPdfFile] = useState<File | null>(null);
  const [concerns, setConcerns] = useState<string[]>([
    '무엇을 준비해야 할지 모르겠어요',
    'AI/백엔드 중 고민',
    '포트폴리오 방향 설정',
  ]);

  const [interestPickerOpen, setInterestPickerOpen] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const pdfInputRef = useRef<HTMLInputElement>(null);

  const toggleInterest = (value: string) =>
    setInterests((prev) => (prev.includes(value) ? prev.filter((v) => v !== value) : [...prev, value]));

  const toggleConcern = (value: string) =>
    setConcerns((prev) => (prev.includes(value) ? prev.filter((v) => v !== value) : [...prev, value]));

  const clearPdfFile = () => {
    setPdfFile(null);
    if (pdfInputRef.current) pdfInputRef.current.value = '';
  };

  const handleSubmit = async () => {
    setError(null);

    if (!pdfFile) {
      setError('자기소개서 PDF 파일을 업로드해주세요.');
      return;
    }

    setSubmitting(true);

    const payload: RoadmapCreateRequest = {
      majorAndYear: `${major}/${year}`,
      currentStatus,
      interests,
      targetJob,
      preferredCompanyType,
      availableTime,
      concerns,
    };

    try {
      const response = await roadmapApi.create({ requestDatas: payload, pdfFile });
      onComplete(toRoadmapViewResponse(response));
    } catch (err) {
      // 백엔드 미연동 상태에서도 데모를 이어갈 수 있도록 대시보드로 진행합니다.
      // 실제 배포 시에는 아래 분기를 에러 처리(토스트/안내)로 바꾸세요.
      const message = err instanceof ApiError ? `(${err.status}) ${err.message}` : '서버에 연결할 수 없습니다.';
      console.warn('로드맵 생성 실패 — 데모 데이터로 진행합니다:', message);
      onComplete();
    } finally {
      setSubmitting(false);
    }
  };

  const availableInterests = INTEREST_OPTIONS.filter((opt) => !interests.includes(opt));

  return (
    <div className="app-shell">
      <Sidebar active="home" />

      <main className="app-main">
        <div className={styles.stepperWrap}>
          <Stepper current={1} />
        </div>

        <div className={styles.headerRow}>
          <div>
            <h1 className={styles.title}>
              <span className={styles.wave}>👋</span> 환영합니다, 민지님!
            </h1>
            <p className={styles.subtitle}>정확한 로드맵 생성을 위해 몇 가지 정보를 알려주세요.</p>
          </div>
          <div className={styles.hintCard}>
            <Sparkles size={16} />
            <span>
              진단이 완료되면
              <br />
              맞춤 로드맵을 생성해드려요!
            </span>
          </div>
        </div>

        <div className={styles.grid}>
          <Field icon={<FileText size={16} />} label="자기소개서 PDF 파일 업로드" className={styles.fileField} required>
            <label className={styles.fileInputWrap}>
              <input
                ref={pdfInputRef}
                type="file"
                accept="application/pdf,.pdf"
                required
                className={styles.fileInput}
                onChange={(e) => setPdfFile(e.target.files?.[0] ?? null)}
              />
              <span className={styles.fileButton}>파일 선택</span>
              <span className={styles.fileName}>{pdfFile ? pdfFile.name : '선택된 파일 없음'}</span>
            </label>
            {pdfFile && (
              <button type="button" className={styles.fileClear} onClick={clearPdfFile}>
                파일 제거
              </button>
            )}
          </Field>

          <Field icon={<GraduationCap size={16} />} label="전공 / 학년">
            <div className={styles.inlineSelects}>
              <Select value={major} options={MAJOR_OPTIONS} onChange={setMajor} />
              <Select value={year} options={YEAR_OPTIONS} onChange={setYear} />
            </div>
          </Field>

          <Field icon={<Activity size={16} />} label="현재 상태">
            <Select value={currentStatus} options={STATUS_OPTIONS} onChange={setCurrentStatus} />
          </Field>

          <Field icon={<Tag size={16} />} label="관심 분야 (복수 선택)">
            <div className={styles.tagRow}>
              {interests.map((item) => (
                <span key={item} className="pill">
                  {item}
                  <button type="button" className={styles.tagRemove} onClick={() => toggleInterest(item)} aria-label={`${item} 제거`}>
                    <X size={13} />
                  </button>
                </span>
              ))}
              <div className={styles.tagAddWrap}>
                <button
                  type="button"
                  className={styles.tagAdd}
                  onClick={() => setInterestPickerOpen((o) => !o)}
                  disabled={availableInterests.length === 0}
                >
                  <Plus size={15} />
                </button>
                {interestPickerOpen && availableInterests.length > 0 && (
                  <div className={styles.picker}>
                    {availableInterests.map((opt) => (
                      <button
                        key={opt}
                        type="button"
                        className={styles.pickerItem}
                        onClick={() => {
                          toggleInterest(opt);
                          setInterestPickerOpen(false);
                        }}
                      >
                        {opt}
                      </button>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </Field>

          <Field icon={<Target size={16} />} label="목표 직무">
            <Select value={targetJob} options={JOB_OPTIONS} onChange={setTargetJob} />
          </Field>

          <Field icon={<Building2 size={16} />} label="희망 회사 유형">
            <Select value={preferredCompanyType} options={COMPANY_OPTIONS} onChange={setPreferredCompanyType} />
          </Field>

          <Field icon={<Clock size={16} />} label="준비 가능 시간">
            <Select value={availableTime} options={TIME_OPTIONS} onChange={setAvailableTime} />
          </Field>
        </div>

        <section className={styles.concernSection}>
          <h2 className={styles.concernTitle}>현재 고민 (복수 선택 가능)</h2>
          <div className={styles.concernGrid}>
            {CONCERN_OPTIONS.map((concern) => {
              const checked = concerns.includes(concern);
              return (
                <button
                  key={concern}
                  type="button"
                  className={`${styles.concernChip} ${checked ? styles.concernChipOn : ''}`}
                  onClick={() => toggleConcern(concern)}
                >
                  {checked && (
                    <span className={styles.concernCheck}>
                      <Check size={12} strokeWidth={3} />
                    </span>
                  )}
                  {concern}
                </button>
              );
            })}
          </div>
        </section>

        {error && <p className={styles.error}>{error}</p>}

        <div className={styles.submitRow}>
          <button type="button" className="btn-primary" onClick={handleSubmit} disabled={submitting}>
            {submitting ? '생성 중…' : '로드맵 생성하기 →'}
          </button>
        </div>
      </main>
    </div>
  );
}

/* ───────── 보조 컴포넌트 ───────── */

function Field({
  icon,
  label,
  children,
  className = '',
  required = false,
}: {
  icon: React.ReactNode;
  label: string;
  children: React.ReactNode;
  className?: string;
  required?: boolean;
}) {
  return (
    <div className={`card ${styles.field} ${className}`}>
      <div className={styles.fieldLabel}>
        <span className={styles.fieldIcon}>{icon}</span>
        {label}
        {required && <span className={styles.requiredBadge}>필수</span>}
      </div>
      {children}
    </div>
  );
}

function Select({ value, options, onChange }: { value: string; options: string[]; onChange: (v: string) => void }) {
  return (
    <select className={styles.select} value={value} onChange={(e) => onChange(e.target.value)}>
      {options.map((opt) => (
        <option key={opt} value={opt}>
          {opt}
        </option>
      ))}
    </select>
  );
}
