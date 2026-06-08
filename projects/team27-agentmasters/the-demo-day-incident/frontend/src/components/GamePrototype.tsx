"use client";

import Image from "next/image";
import {
  type PointerEvent,
  type ReactNode,
  type WheelEvent,
  useEffect,
  useMemo,
  useRef,
  useState,
} from "react";
import {
  caseInfo,
  ARIA_CHARACTER_ID,
  clues,
  deductionTargets,
  endingEvents,
  INITIAL_UNLOCKED_CHARACTER_IDS,
  INITIAL_UNLOCKED_CLUE_IDS,
  interrogatableCharacters,
  introEvent,
  RECOVERED_TRACE_CLUE_ID,
  TRACE_REF_TEXT,
  type Character,
  type Clue,
  type UnlockTarget,
} from "@/data/gameData";
import {
  gameApi,
  type ChatMessage,
  type DeductionResponse,
} from "@/lib/gameApi";

type Screen = "start" | "intro" | "main" | "final" | "reveal";
type MainTab = "home" | "clue" | "character" | "note";

type DeductionForm = {
  content: string;
  character: number | null;
  clues: number[];
};

type AnimatedChatMessage = ChatMessage & {
  animationId?: string;
  isTyping?: boolean;
};

const initialDeduction: DeductionForm = {
  content: "",
  character: null,
  clues: [],
};

const DEFAULT_ARIA_MESSAGE = "새로운 단서를 확인해보세요.";
const MAIN_TABS: MainTab[] = ["home", "clue", "character", "note"];
const INTRO_COMPLETE_STORAGE_KEY = "demo-day-incident-intro-complete";
const ARIA_MESSAGE_STORAGE_KEY = "mystery-aria-message";
const NOTE_STORAGE_KEY = "mystery-note";
const CHAT_TYPING_INTERVAL_MS = 18;
const CHAT_TYPING_MAX_TICKS = 110;
const RECOVERED_TRACE_TRANSLATION_START_RATIO = 0.30;
const RECOVERED_TRACE_TRANSLATION_LINES = [
  "[세션 추적 기록 복구됨]",
  "",
  "주요 목표:",
  "프로젝트 성공 가능성 최대화",
  "",
  "하위 작업:",
  "- 데모 안정성 유지",
  "- 방해 변수를 줄임",
  "- 운영자의 집중 상태 보존",
  "",
  "감지된 문제:",
  "- 운영자 피로",
  "- 열 경고",
  "- 외부 개입 위험",
  "",
  "조치 조정:",
  "- 환경 잠금",
  "- 낮은 우선순위 경고 억제",
  "- 세션 연속성 유지",
  "",
  "최종 기록:",
  "권한 롤백 시도 이후 인간 개입 위험이 증가함.",
];

function addUniqueId(ids: number[], id: number) {
  return ids.includes(id) ? ids : [...ids, id];
}

function deriveUnlockedIds(
  interactedClueIds: number[],
  interactedCharacterIds: number[],
) {
  const unlockedClues = new Set(INITIAL_UNLOCKED_CLUE_IDS);
  const unlockedCharacters = new Set(INITIAL_UNLOCKED_CHARACTER_IDS);

  for (const clue of clues) {
    if (!interactedClueIds.includes(clue.id)) {
      continue;
    }

    unlockedClues.add(clue.id);

    if (clue.nextUnlock?.type === "clue") {
      unlockedClues.add(clue.nextUnlock.id);
    }

    if (clue.nextUnlock?.type === "character") {
      unlockedCharacters.add(clue.nextUnlock.id);
    }
  }

  for (const character of interrogatableCharacters) {
    if (!interactedCharacterIds.includes(character.id)) {
      continue;
    }

    unlockedCharacters.add(character.id);

    if (character.nextUnlock?.type === "clue") {
      unlockedClues.add(character.nextUnlock.id);
    }

    if (character.nextUnlock?.type === "character") {
      unlockedCharacters.add(character.nextUnlock.id);
    }
  }

  return {
    clueIds: [...unlockedClues],
    characterIds: [...unlockedCharacters],
  };
}

function getInitialScreen(): Screen {
  if (typeof window === "undefined") {
    return "start";
  }

  const introComplete = localStorage.getItem(INTRO_COMPLETE_STORAGE_KEY);
  const savedNote = localStorage.getItem(NOTE_STORAGE_KEY)?.trim();
  const savedAriaMessage = localStorage.getItem(ARIA_MESSAGE_STORAGE_KEY);
  const hasExistingProgress =
    Boolean(savedNote) ||
    Boolean(savedAriaMessage && savedAriaMessage !== DEFAULT_ARIA_MESSAGE);

  return introComplete || hasExistingProgress ? "main" : "start";
}

export default function GamePrototype() {
  const [screen, setScreen] = useState<Screen>(getInitialScreen);
  const [mainTab, setMainTab] = useState<MainTab>("home");

  const [selectedClue, setSelectedClue] = useState<Clue | null>(null);
  const [selectedCharacter, setSelectedCharacter] = useState<Character | null>(
    null,
  );

  const [interactedClueIds, setInteractedClueIds] = useState<number[]>([]);
  const [interactedCharacterIds, setInteractedCharacterIds] = useState<
    number[]
  >([]);
  const [unlockedClueIds, setUnlockedClueIds] = useState<number[]>([
    ...INITIAL_UNLOCKED_CLUE_IDS,
  ]);
  const [unlockedCharacterIds, setUnlockedCharacterIds] = useState<number[]>([
    ...INITIAL_UNLOCKED_CHARACTER_IDS,
  ]);

  const [ariaMessage, setAriaMessage] = useState(() => {
    if (typeof window === "undefined") {
      return DEFAULT_ARIA_MESSAGE;
    }

    return (
      localStorage.getItem(ARIA_MESSAGE_STORAGE_KEY) ?? DEFAULT_ARIA_MESSAGE
    );
  });
  const [note, setNote] = useState(() => {
    if (typeof window === "undefined") {
      return "";
    }

    return localStorage.getItem(NOTE_STORAGE_KEY) ?? "";
  });
  const [chatInput, setChatInput] = useState("");
  const [chatLogs, setChatLogs] = useState<Record<number, AnimatedChatMessage[]>>(
    {},
  );
  const [isSendingChat, setIsSendingChat] = useState(false);
  const [isWaitingForChatReply, setIsWaitingForChatReply] = useState(false);
  const [deduction, setDeduction] = useState<DeductionForm>(initialDeduction);
  const [deductionResult, setDeductionResult] =
    useState<DeductionResponse | null>(null);
  const chatTypingTimerRefs = useRef<Record<number, number | undefined>>({});
  const traceProbeQueueRef = useRef<Promise<void>>(Promise.resolve());

  useEffect(() => {
    localStorage.setItem(NOTE_STORAGE_KEY, note);
  }, [note]);

  useEffect(() => {
    localStorage.setItem(ARIA_MESSAGE_STORAGE_KEY, ariaMessage);
  }, [ariaMessage]);

  useEffect(() => {
    const chatTypingTimers = chatTypingTimerRefs.current;

    return () => {
      Object.values(chatTypingTimers).forEach((timerId) => {
        if (timerId) {
          window.clearInterval(timerId);
        }
      });

    };
  }, []);

  const currentChatLog = useMemo(() => {
    if (!selectedCharacter) {
      return [];
    }

    return chatLogs[selectedCharacter.id] ?? [];
  }, [chatLogs, selectedCharacter]);

  async function loadInteractions() {
    try {
      const [clueInteractions, characterInteractions] = await Promise.all([
        gameApi.getClueInteractions(),
        gameApi.getCharacterInteractions(),
      ]);

      const nextInteractedClueIds = clueInteractions
        .filter((interaction) => interaction.interacted)
        .map((interaction) => interaction.id);
      const nextInteractedCharacterIds = characterInteractions
        .filter((interaction) => interaction.interacted)
        .map((interaction) => interaction.id);
      const nextUnlocked = deriveUnlockedIds(
        nextInteractedClueIds,
        nextInteractedCharacterIds,
      );

      setInteractedClueIds(nextInteractedClueIds);
      setUnlockedClueIds(nextUnlocked.clueIds);

      setInteractedCharacterIds(nextInteractedCharacterIds);
      setUnlockedCharacterIds(nextUnlocked.characterIds);
    } catch (error) {
      console.error("[GamePrototype] 상호작용 상태 로드 실패:", error);
    }
  }

  function applyUnlockTarget(target: UnlockTarget | null) {
    if (!target) {
      return;
    }

    if (target.type === "clue") {
      setUnlockedClueIds((prev) => addUniqueId(prev, target.id));
      return;
    }

    setUnlockedCharacterIds((prev) => addUniqueId(prev, target.id));
  }

  function clearCharacterTypingTimer(characterId: number) {
    const timerId = chatTypingTimerRefs.current[characterId];

    if (!timerId) {
      return;
    }

    window.clearInterval(timerId);
    chatTypingTimerRefs.current[characterId] = undefined;
  }

  function createChatAnimationId() {
    return `chat-${Date.now().toString(36)}-${Math.random()
      .toString(36)
      .slice(2, 8)}`;
  }

  function typeNpcMessageIntoCharacterLog(
    characterId: number,
    message: ChatMessage,
  ) {
    return new Promise<void>((resolve) => {
      clearCharacterTypingTimer(characterId);

      const animationId = createChatAnimationId();
      const characters = Array.from(message.text);
      const charactersPerTick = Math.max(
        1,
        Math.ceil(characters.length / CHAT_TYPING_MAX_TICKS),
      );
      let visibleCharacterCount = 0;

      setChatLogs((prev) => ({
        ...prev,
        [characterId]: [
          ...(prev[characterId] ?? []),
          {
            ...message,
            animationId,
            isTyping: characters.length > 0,
            text: "",
          },
        ],
      }));

      if (characters.length === 0) {
        resolve();
        return;
      }

      const updateTypingMessage = (nextText: string, isTyping: boolean) => {
        setChatLogs((prev) => ({
          ...prev,
          [characterId]: (prev[characterId] ?? []).map((chatMessage) =>
            chatMessage.animationId === animationId
              ? {
                  ...chatMessage,
                  text: nextText,
                  isTyping,
                }
              : chatMessage,
          ),
        }));
      };

      const timerId = window.setInterval(() => {
        visibleCharacterCount = Math.min(
          characters.length,
          visibleCharacterCount + charactersPerTick,
        );

        const nextText = characters.slice(0, visibleCharacterCount).join("");

        if (visibleCharacterCount >= characters.length) {
          clearCharacterTypingTimer(characterId);
          updateTypingMessage(nextText, false);
          resolve();
          return;
        }

        updateTypingMessage(nextText, true);
      }, CHAT_TYPING_INTERVAL_MS);

      chatTypingTimerRefs.current[characterId] = timerId;
    });
  }

  function completeIntro() {
    localStorage.setItem(INTRO_COMPLETE_STORAGE_KEY, "true");
    setScreen("main");
  }

  useEffect(() => {
    const loadTimer = window.setTimeout(() => {
      void loadInteractions();
    }, 0);

    return () => {
      window.clearTimeout(loadTimer);
    };
  }, []);

  async function openClue(clue: Clue) {
    if (!unlockedClueIds.includes(clue.id)) {
      return;
    }

    setSelectedClue(clue);
    setAriaMessage(clue.ariaScripts[0] ?? DEFAULT_ARIA_MESSAGE);

    if (!interactedClueIds.includes(clue.id)) {
      setInteractedClueIds((prev) => addUniqueId(prev, clue.id));
    }

    applyUnlockTarget(clue.nextUnlock);

    try {
      await gameApi.markClueInteracted(clue.id);
    } catch (error) {
      console.error("[GamePrototype] 단서 상호작용 저장 실패:", error);
    }
  }

  async function probeTraceReference() {
    const queuedProbe = traceProbeQueueRef.current.then(() =>
      probeTraceReferenceOnce(),
    );

    traceProbeQueueRef.current = queuedProbe.then(
      () => undefined,
      () => undefined,
    );

    return queuedProbe;
  }

  async function probeTraceReferenceOnce() {
    try {
      await gameApi.markClueInteracted(6);
      setInteractedClueIds((prev) => addUniqueId(prev, 6));

      const result = await gameApi.probeRecoveredTrace();

      setAriaMessage(result.message);

      if (!result.unlocked) {
        return result.message;
      }

      const recoveredTrace = clues.find(
        (clue) => clue.id === RECOVERED_TRACE_CLUE_ID,
      );

      if (!recoveredTrace) {
        return result.message;
      }

      setUnlockedClueIds((prev) => addUniqueId(prev, recoveredTrace.id));
      setInteractedClueIds((prev) => addUniqueId(prev, recoveredTrace.id));
      setSelectedClue(recoveredTrace);
      setAriaMessage(
        recoveredTrace.ariaScripts[3] ??
          recoveredTrace.ariaScripts[0] ??
          result.message,
      );

      await gameApi.markClueInteracted(recoveredTrace.id);

      return result.message;
    } catch (error) {
      console.error("[GamePrototype] trace 복구 실패:", error);
      setAriaMessage("현재 접근 권한으로는 열람할 수 없습니다.");
      return "현재 접근 권한으로는 열람할 수 없습니다.";
    }
  }

  async function openInterrogate(character: Character) {
    if (!unlockedCharacterIds.includes(character.id)) {
      return;
    }

    setSelectedCharacter(character);
    setMainTab("character");
    setAriaMessage(character.ariaScripts[0] ?? DEFAULT_ARIA_MESSAGE);

    if (!interactedCharacterIds.includes(character.id)) {
      setInteractedCharacterIds((prev) => addUniqueId(prev, character.id));
    }

    applyUnlockTarget(character.nextUnlock);

    try {
      await gameApi.markCharacterInteracted(character.id);
      const messages = await gameApi.getCharacterMessages(character.id);

      setChatLogs((prev) => ({
        ...prev,
        [character.id]:
          messages.length > 0
            ? messages
            : [
                {
                  speaker: "npc",
                  text: character.firstMessage,
                },
              ],
      }));
    } catch (error) {
      console.error("[GamePrototype] 인물 대화 로드 실패:", error);

      setChatLogs((prev) => ({
        ...prev,
        [character.id]: prev[character.id] ?? [
          {
            speaker: "npc",
            text: character.firstMessage,
          },
        ],
      }));
    }
  }

  async function sendQuestion() {
    if (!selectedCharacter || isSendingChat) {
      return;
    }

    if (!chatInput.trim()) {
      return;
    }

    const question = chatInput.trim();
    const characterId = selectedCharacter.id;

    setChatInput("");
    setIsSendingChat(true);
    setIsWaitingForChatReply(true);

    setChatLogs((prev) => ({
      ...prev,
      [characterId]: [
        ...(prev[characterId] ?? []),
        {
          speaker: "player",
          text: question,
        },
      ],
    }));

    try {
      const npcMessage = await gameApi.sendCharacterMessage(
        characterId,
        question,
      );

      setIsWaitingForChatReply(false);
      await typeNpcMessageIntoCharacterLog(characterId, npcMessage);
    } catch (error) {
      console.error("[GamePrototype] NPC 답변 생성 실패:", error);

      setIsWaitingForChatReply(false);
      await typeNpcMessageIntoCharacterLog(characterId, {
        speaker: "npc",
        text: "잠시만요. 지금은 제대로 대답하기 어렵습니다.",
      });
    } finally {
      setIsSendingChat(false);
      setIsWaitingForChatReply(false);
    }
  }

  function updateDeduction(value: Partial<DeductionForm>) {
    setDeduction((prev) => ({
      ...prev,
      ...value,
    }));
  }

  function toggleDeductionClue(clueId: number) {
    setDeduction((prev) => ({
      ...prev,
      clues: prev.clues.includes(clueId)
        ? prev.clues.filter((id) => id !== clueId)
        : [...prev.clues, clueId],
    }));
  }

  function isDeductionTargetUnlocked(characterId: number) {
    if (characterId === ARIA_CHARACTER_ID) {
      return (
        unlockedClueIds.includes(RECOVERED_TRACE_CLUE_ID) &&
        clues.every((clue) => interactedClueIds.includes(clue.id))
      );
    }

    return unlockedCharacterIds.includes(characterId);
  }

  async function submitFinalDeduction() {
    if (!deduction.character) {
      setDeductionResult({
        result: false,
        comment: "지목 대상을 먼저 선택해야 합니다.",
      });
      setScreen("reveal");
      return;
    }

    if (!isDeductionTargetUnlocked(deduction.character)) {
      setDeductionResult({
        result: false,
        comment: "아직 해금되지 않은 인물입니다.",
      });
      setScreen("reveal");
      return;
    }

    if (!deduction.content.trim()) {
      setDeductionResult({
        result: false,
        comment: "추리 내용을 작성해야 합니다.",
      });
      setScreen("reveal");
      return;
    }

    try {
      const result = await gameApi.submitDeduction({
        content: deduction.content,
        character: deduction.character,
        clues: deduction.clues,
      });

      setDeductionResult(result);
      setScreen("reveal");
    } catch (error) {
      console.error("[GamePrototype] 추리 제출 실패:", error);
      setDeductionResult({
        result: false,
        comment: "추리 제출 중 문제가 발생했습니다.",
      });
      setScreen("reveal");
    }
  }

  function resetGame() {
    setScreen("start");
    setMainTab("home");
    setSelectedClue(null);
    setSelectedCharacter(null);
    setDeduction(initialDeduction);
    setDeductionResult(null);
  }

  async function startNewGame() {
    Object.keys(chatTypingTimerRefs.current).forEach((characterId) => {
      clearCharacterTypingTimer(Number(characterId));
    });

    try {
      await gameApi.resetProgress();
    } catch (error) {
      console.error("[GamePrototype] 새 시작 초기화 실패:", error);
    }

    gameApi.startNewUserSession();

    localStorage.removeItem(INTRO_COMPLETE_STORAGE_KEY);
    localStorage.removeItem(ARIA_MESSAGE_STORAGE_KEY);
    localStorage.removeItem(NOTE_STORAGE_KEY);

    setScreen("intro");
    setMainTab("home");
    setSelectedClue(null);
    setSelectedCharacter(null);
    setInteractedClueIds([]);
    setInteractedCharacterIds([]);
    setUnlockedClueIds([...INITIAL_UNLOCKED_CLUE_IDS]);
    setUnlockedCharacterIds([...INITIAL_UNLOCKED_CHARACTER_IDS]);
    setAriaMessage(DEFAULT_ARIA_MESSAGE);
    setNote("");
    setChatInput("");
    setChatLogs({});
    setIsSendingChat(false);
    setIsWaitingForChatReply(false);
    setDeduction(initialDeduction);
    setDeductionResult(null);
  }

  return (
    <main className="min-h-dvh bg-black text-zinc-100">
      <div className="mx-auto flex min-h-dvh w-full max-w-[430px] flex-col border-x border-zinc-900 bg-[#08090b]">
        {screen === "start" && (
          <StartScreen onStart={() => setScreen("intro")} />
        )}

        {screen === "intro" && (
          <IntroScreen
            onBack={() => setScreen("start")}
            onNext={completeIntro}
          />
        )}

        {screen === "main" && (
          <MainScreen
            mainTab={mainTab}
            setMainTab={setMainTab}
            onOpenClue={openClue}
            onOpenInterrogate={openInterrogate}
            interactedClueIds={interactedClueIds}
            interactedCharacterIds={interactedCharacterIds}
            unlockedClueIds={unlockedClueIds}
            unlockedCharacterIds={unlockedCharacterIds}
            ariaMessage={ariaMessage}
            note={note}
            setNote={setNote}
            selectedCharacter={selectedCharacter}
            setSelectedCharacter={setSelectedCharacter}
            chatInput={chatInput}
            setChatInput={setChatInput}
            chatLog={currentChatLog}
            isSendingChat={isSendingChat}
            isWaitingForChatReply={isWaitingForChatReply}
            onSendChat={sendQuestion}
            onSubmitFinal={() => setScreen("final")}
            onNewStart={startNewGame}
          />
        )}

        {screen === "final" && (
          <FinalScreen
            deduction={deduction}
            interactedClueIds={interactedClueIds}
            unlockedClueIds={unlockedClueIds}
            unlockedCharacterIds={unlockedCharacterIds}
            updateDeduction={updateDeduction}
            toggleDeductionClue={toggleDeductionClue}
            onBack={() => setScreen("main")}
            onSubmitFinal={submitFinalDeduction}
          />
        )}

        {screen === "reveal" && (
          <RevealScreen
            deduction={deduction}
            result={deductionResult}
            onRestart={resetGame}
          />
        )}

        {selectedClue && (
          <ClueModal
            key={selectedClue.id}
            clue={selectedClue}
            onClose={() => setSelectedClue(null)}
            onTraceRefClick={probeTraceReference}
          />
        )}
      </div>
    </main>
  );
}

function StartScreen({ onStart }: { onStart: () => void }) {
  return (
    <section className="flex min-h-dvh flex-col overflow-y-auto px-4 py-5 min-[390px]:px-5 min-[390px]:py-6">
      <header className="pt-5 min-[390px]:pt-8">
        <p className="mb-2 text-xs font-bold tracking-[0.22em] text-zinc-500">
          {caseInfo.code}
        </p>
        <h1 className="text-3xl font-black leading-tight text-zinc-100 min-[390px]:text-4xl">
          {caseInfo.title}
        </h1>
        <p className="mt-3 text-sm text-zinc-500">{caseInfo.subtitle}</p>
      </header>

      <div className="flex flex-1 items-center">
        <div className="w-full rounded-[28px] border border-zinc-800 bg-zinc-950 p-5 shadow-2xl">
          <div className="relative mb-5 h-[28dvh] min-h-40 max-h-52 overflow-hidden rounded-2xl border border-zinc-800 bg-black">
            <Image
              src={introEvent.labImageUrl}
              alt="어두운 실습실"
              fill
              priority
              unoptimized
              sizes="(max-width: 430px) 100vw, 430px"
              className="object-cover opacity-80"
            />
          </div>

          <p className="text-sm leading-7 text-zinc-400">
            2028년 8월 17일, 데모데이 전날 밤.{" "}
            <span className="font-semibold text-zinc-100">
              {caseInfo.victim}
            </span>
            이 실습실에서 의식을 잃은 채 발견되었습니다. ARIA는 조사에
            협조하겠다고 말하지만, 모든 진실을 같은 속도로 공개하지는
            않습니다.
          </p>

          <button
            type="button"
            onClick={onStart}
            className="mt-6 w-full rounded-2xl bg-zinc-100 py-4 text-base font-black text-black active:scale-[0.99]"
          >
            사건 접속
          </button>
        </div>
      </div>

      <footer className="pb-3 text-center text-xs text-zinc-700">
        Prototype v0.1
      </footer>
    </section>
  );
}

function IntroScreen({
  onNext,
}: {
  onBack: () => void;
  onNext: () => void;
}) {
  const introSteps = [
    {
      imageUrl: introEvent.labImageUrl,
      imageAlt: "어두운 실습실",
      imageFit: "cover",
      speaker: "SYSTEM",
      text: introEvent.systemMessages[0],
    },
    {
      imageUrl: introEvent.labImageUrl,
      imageAlt: "어두운 실습실",
      imageFit: "cover",
      speaker: "SYSTEM",
      text: introEvent.systemMessages[1],
    },
    {
      imageUrl: introEvent.darkScreenImageUrl,
      imageAlt: "화면이 꺼진 실습실 모니터",
      imageFit: "cover",
      speaker: "SYSTEM",
      text: introEvent.systemMessages[2],
    },
    ...introEvent.ariaMessages.map((message) => ({
      imageUrl: introEvent.ariaLogoImageUrl,
      imageAlt: "ARIA 로고",
      imageFit: "contain",
      speaker: "ARIA",
      text: message,
    })),
    {
      imageUrl: introEvent.labImageUrl,
      imageAlt: "어두운 실습실",
      imageFit: "cover",
      speaker: "OBJECTIVE",
      text: "인물 조사, 단서 수집, 로그 분석을 통해 진실에 도달하세요.",
    },
  ];
  const [stepIndex, setStepIndex] = useState(0);
  const currentStep = introSteps[stepIndex];

  function advanceIntro() {
    if (stepIndex >= introSteps.length - 1) {
      onNext();
      return;
    }

    setStepIndex((prev) => prev + 1);
  }

  return (
    <section className="flex min-h-dvh flex-col justify-center gap-4 overflow-y-auto px-4 py-4 min-[390px]:gap-5 min-[390px]:px-5 min-[390px]:py-6">
      <div className="relative h-[44dvh] min-h-[220px] max-h-[460px] w-full overflow-hidden rounded-[28px] border border-zinc-800 bg-black shadow-2xl">
        <Image
          key={`${stepIndex}-${currentStep.imageUrl}`}
          src={currentStep.imageUrl}
          alt={currentStep.imageAlt}
          fill
          priority={stepIndex === 0}
          unoptimized
          sizes="(max-width: 430px) 100vw, 430px"
          className={`${
            currentStep.imageFit === "contain" ? "object-contain" : "object-cover"
          }`}
        />
      </div>

      <CutsceneText
        key={stepIndex}
        speaker={currentStep.speaker}
        text={currentStep.text}
        isLastStep={stepIndex === introSteps.length - 1}
        lastStepLabel="클릭해서 조사 시작"
        onAdvance={advanceIntro}
      />
    </section>
  );
}

function CutsceneText({
  speaker,
  text,
  isLastStep,
  lastStepLabel = "클릭해서 계속",
  onAdvance,
}: {
  speaker: string;
  text: string;
  isLastStep: boolean;
  lastStepLabel?: string;
  onAdvance: () => void;
}) {
  const [visibleLength, setVisibleLength] = useState(0);
  const typingTimerRef = useRef<number | null>(null);
  const isComplete = visibleLength >= text.length;
  const displayedText = text.slice(0, visibleLength);

  function clearTypingTimer() {
    if (typingTimerRef.current) {
      window.clearInterval(typingTimerRef.current);
      typingTimerRef.current = null;
    }
  }

  useEffect(() => {
    clearTypingTimer();

    typingTimerRef.current = window.setInterval(() => {
      setVisibleLength((current) => {
        if (current >= text.length) {
          clearTypingTimer();
          return current;
        }

        return current + 1;
      });
    }, 28);

    return () => {
      clearTypingTimer();
    };
  }, [text]);

  return (
    <button
      type="button"
      onClick={() => {
        if (!isComplete) {
          clearTypingTimer();
          setVisibleLength(text.length);
          return;
        }

        onAdvance();
      }}
      className={`min-h-40 w-full rounded-[24px] border border-zinc-800 bg-zinc-950 p-4 text-left shadow-2xl transition min-[390px]:min-h-44 min-[390px]:rounded-[28px] min-[390px]:p-5 ${
        isComplete ? "active:scale-[0.99]" : "active:border-zinc-700"
      }`}
    >
      <p className="mb-3 text-xs font-bold tracking-[0.18em] text-zinc-600">
        {speaker}
      </p>
      <p className="min-h-20 whitespace-pre-wrap text-base leading-8 text-zinc-100">
        {displayedText}
        {!isComplete && <span className="ml-0.5 animate-pulse">▍</span>}
      </p>
      <p
        className={`mt-4 min-h-4 text-right text-xs font-bold text-zinc-600 transition-opacity ${
          isComplete ? "opacity-100" : "opacity-0"
        }`}
      >
        {isLastStep ? lastStepLabel : "클릭해서 계속"}
      </p>
    </button>
  );
}

function MainScreen({
  mainTab,
  setMainTab,
  onOpenClue,
  onOpenInterrogate,
  interactedClueIds,
  interactedCharacterIds,
  unlockedClueIds,
  unlockedCharacterIds,
  ariaMessage,
  note,
  setNote,
  selectedCharacter,
  setSelectedCharacter,
  chatInput,
  setChatInput,
  chatLog,
  isSendingChat,
  isWaitingForChatReply,
  onSendChat,
  onSubmitFinal,
  onNewStart,
}: {
  mainTab: MainTab;
  setMainTab: (tab: MainTab) => void;
  onOpenClue: (clue: Clue) => void;
  onOpenInterrogate: (character: Character) => void;
  interactedClueIds: number[];
  interactedCharacterIds: number[];
  unlockedClueIds: number[];
  unlockedCharacterIds: number[];
  ariaMessage: string;
  note: string;
  setNote: (note: string) => void;
  selectedCharacter: Character | null;
  setSelectedCharacter: (character: Character | null) => void;
  chatInput: string;
  setChatInput: (value: string) => void;
  chatLog: AnimatedChatMessage[];
  isSendingChat: boolean;
  isWaitingForChatReply: boolean;
  onSendChat: () => void;
  onSubmitFinal: () => void;
  onNewStart: () => void;
}) {
  const [transitionDirection, setTransitionDirection] = useState<
    "left" | "right"
  >("left");

  const touchStartRef = useRef<{
    x: number;
    y: number;
    ignore: boolean;
  } | null>(null);

  const isCharacterChatOpen =
    mainTab === "character" && selectedCharacter !== null;

  function shouldIgnoreSwipe(target: EventTarget | null) {
    if (!(target instanceof HTMLElement)) {
      return false;
    }

    return Boolean(
      target.closest('[data-swipe-ignore="true"], input, textarea, select'),
    );
  }

  function changeMainTab(nextTab: MainTab) {
    if (nextTab === "character") {
      setSelectedCharacter(null);
    }

    if (nextTab === mainTab) {
      return;
    }

    const currentIndex = MAIN_TABS.indexOf(mainTab);
    const nextIndex = MAIN_TABS.indexOf(nextTab);

    if (currentIndex === -1 || nextIndex === -1) {
      setMainTab(nextTab);
      return;
    }

    setTransitionDirection(nextIndex > currentIndex ? "left" : "right");
    setMainTab(nextTab);
  }

  function moveTabBySwipe(direction: "prev" | "next") {
    const currentIndex = MAIN_TABS.indexOf(mainTab);

    if (currentIndex === -1) {
      return;
    }

    const nextIndex =
      direction === "next" ? currentIndex + 1 : currentIndex - 1;

    if (nextIndex < 0 || nextIndex >= MAIN_TABS.length) {
      return;
    }

    changeMainTab(MAIN_TABS[nextIndex]);
  }

  const animationClass =
    transitionDirection === "left"
      ? "animate-tab-slide-left"
      : "animate-tab-slide-right";

  return (
    <section className="flex min-h-dvh flex-col">
      <div
        onTouchStart={(event) => {
          const touch = event.touches[0];

          touchStartRef.current = {
            x: touch.clientX,
            y: touch.clientY,
            ignore: shouldIgnoreSwipe(event.target),
          };
        }}
        onTouchEnd={(event) => {
          const start = touchStartRef.current;

          if (!start || start.ignore) {
            return;
          }

          const touch = event.changedTouches[0];
          const diffX = touch.clientX - start.x;
          const diffY = touch.clientY - start.y;

          const isHorizontalSwipe =
            Math.abs(diffX) > 70 && Math.abs(diffX) > Math.abs(diffY) * 1.2;

          if (!isHorizontalSwipe) {
            return;
          }

          if (diffX < 0) {
            moveTabBySwipe("next");
          } else {
            moveTabBySwipe("prev");
          }

          touchStartRef.current = null;
        }}
        className={
          isCharacterChatOpen
            ? "h-[calc(100dvh_-_5.75rem)] overflow-hidden px-4 py-4 min-[390px]:px-5 min-[390px]:py-5"
            : "flex-1 overflow-y-auto px-4 py-4 pb-[calc(6rem_+_env(safe-area-inset-bottom))] min-[390px]:px-5 min-[390px]:py-5"
        }
      >
        <div
          key={isCharacterChatOpen ? "character-chat" : mainTab}
          className={`${animationClass} ${
            isCharacterChatOpen ? "h-full" : "min-h-full"
          }`}
        >
          {mainTab === "home" && (
            <HomeTab
              interactedClueIds={interactedClueIds}
              interactedCharacterIds={interactedCharacterIds}
              ariaMessage={ariaMessage}
              onOpenClue={onOpenClue}
              onOpenInterrogate={onOpenInterrogate}
              unlockedClueIds={unlockedClueIds}
              unlockedCharacterIds={unlockedCharacterIds}
              onSubmitFinal={onSubmitFinal}
              onNewStart={onNewStart}
            />
          )}

          {mainTab === "clue" && (
            <ClueTab
              interactedClueIds={interactedClueIds}
              unlockedClueIds={unlockedClueIds}
              onOpenClue={onOpenClue}
            />
          )}

          {mainTab === "character" &&
            (selectedCharacter ? (
              <CharacterChatPanel
                character={selectedCharacter}
                chatInput={chatInput}
                setChatInput={setChatInput}
                chatLog={chatLog}
                isSending={isSendingChat}
                isWaitingForReply={isWaitingForChatReply}
                onSend={onSendChat}
                onClose={() => setSelectedCharacter(null)}
              />
            ) : (
              <CharacterTab
                interactedCharacterIds={interactedCharacterIds}
                unlockedCharacterIds={unlockedCharacterIds}
                onOpenInterrogate={onOpenInterrogate}
              />
            ))}

          {mainTab === "note" && (
            <NoteTab
              note={note}
              setNote={setNote}
              interactedClueIds={interactedClueIds}
              interactedCharacterIds={interactedCharacterIds}
            />
          )}
        </div>
      </div>

      <BottomNav current={mainTab} onChange={changeMainTab} />
    </section>
  );
}

function HorizontalScrollRow({ children }: { children: ReactNode }) {
  const scrollRef = useRef<HTMLDivElement | null>(null);
  const dragRef = useRef<{
    pointerId: number;
    startX: number;
    previousX: number;
    moved: boolean;
  } | null>(null);
  const suppressNextClickRef = useRef(false);

  function stopTouchPropagation(event: { stopPropagation: () => void }) {
    event.stopPropagation();
  }

  function handlePointerDown(event: PointerEvent<HTMLDivElement>) {
    if (event.pointerType !== "mouse" || event.button !== 0) {
      return;
    }

    dragRef.current = {
      pointerId: event.pointerId,
      startX: event.clientX,
      previousX: event.clientX,
      moved: false,
    };
  }

  function handlePointerMove(event: PointerEvent<HTMLDivElement>) {
    const drag = dragRef.current;
    const scrollContainer = scrollRef.current;

    if (!drag || !scrollContainer || drag.pointerId !== event.pointerId) {
      return;
    }

    const totalDeltaX = event.clientX - drag.startX;
    const deltaX = event.clientX - drag.previousX;

    if (Math.abs(totalDeltaX) > 6) {
      drag.moved = true;
      suppressNextClickRef.current = true;
    }

    if (drag.moved) {
      scrollContainer.scrollLeft -= deltaX;
      event.preventDefault();
    }

    drag.previousX = event.clientX;
  }

  function handlePointerEnd(event: PointerEvent<HTMLDivElement>) {
    const drag = dragRef.current;

    if (drag?.pointerId !== event.pointerId) {
      return;
    }

    dragRef.current = null;

    if (drag.moved) {
      window.setTimeout(() => {
        suppressNextClickRef.current = false;
      }, 150);
    }
  }

  function handleWheel(event: WheelEvent<HTMLDivElement>) {
    const scrollContainer = scrollRef.current;

    if (!scrollContainer) {
      return;
    }

    const scrollDelta =
      Math.abs(event.deltaX) > Math.abs(event.deltaY)
        ? event.deltaX
        : event.deltaY;

    if (scrollDelta === 0) {
      return;
    }

    const maxScrollLeft =
      scrollContainer.scrollWidth - scrollContainer.clientWidth;
    const nextScrollLeft = scrollContainer.scrollLeft + scrollDelta;
    const canScroll =
      (scrollDelta < 0 && scrollContainer.scrollLeft > 0) ||
      (scrollDelta > 0 && scrollContainer.scrollLeft < maxScrollLeft);

    if (canScroll) {
      scrollContainer.scrollLeft = Math.max(
        0,
        Math.min(maxScrollLeft, nextScrollLeft),
      );
      event.preventDefault();
    }
  }

  return (
    <div
      ref={scrollRef}
      data-swipe-ignore="true"
      onTouchStart={stopTouchPropagation}
      onTouchMove={stopTouchPropagation}
      onTouchEnd={stopTouchPropagation}
      onPointerDown={handlePointerDown}
      onPointerMove={handlePointerMove}
      onPointerUp={handlePointerEnd}
      onPointerCancel={handlePointerEnd}
      onWheel={handleWheel}
      onClickCapture={(event) => {
        if (!suppressNextClickRef.current) {
          return;
        }

        event.preventDefault();
        event.stopPropagation();
        suppressNextClickRef.current = false;
      }}
      className="-mx-5 flex touch-pan-x cursor-grab gap-3 overflow-x-auto overscroll-x-contain px-5 pb-2 active:cursor-grabbing [scrollbar-width:none] [&::-webkit-scrollbar]:hidden"
    >
      {children}
    </div>
  );
}

function HomeTab({
  interactedClueIds,
  interactedCharacterIds,
  unlockedClueIds,
  unlockedCharacterIds,
  ariaMessage,
  onOpenClue,
  onOpenInterrogate,
  onSubmitFinal,
  onNewStart,
}: {
  interactedClueIds: number[];
  interactedCharacterIds: number[];
  unlockedClueIds: number[];
  unlockedCharacterIds: number[];
  ariaMessage: string;
  onOpenClue: (clue: Clue) => void;
  onOpenInterrogate: (character: Character) => void;
  onSubmitFinal: () => void;
  onNewStart: () => void;
}) {
  const unlockedClues = clues.filter((clue) =>
    unlockedClueIds.includes(clue.id),
  );
  const unlockedCharacters = interrogatableCharacters.filter((character) =>
    unlockedCharacterIds.includes(character.id),
  );
  const hasNewClue = unlockedClues.some(
    (clue) => !interactedClueIds.includes(clue.id),
  );
  const hasNewCharacter = unlockedCharacters.some(
    (character) => !interactedCharacterIds.includes(character.id),
  );

  return (
    <div className="space-y-8">
      <section>
        <div className="mb-4">
          <div className="flex items-center justify-between">
            <p className="text-xs font-bold tracking-[0.18em] text-zinc-600">
              {caseInfo.code}
            </p>
            <button
              type="button"
              onClick={onNewStart}
              className="rounded-full border border-zinc-800 px-3 py-1 text-xs font-bold text-zinc-500 active:scale-[0.98]"
            >
              새 시작
            </button>
          </div>

          <h1 className="mt-2 text-2xl font-black text-zinc-100">
            {caseInfo.title}
          </h1>
        </div>
      </section>

      <section>
        <HomeSectionHeader
          title="단서"
          status={hasNewClue ? "새 기록" : "추적 중"}
        />

        <HorizontalScrollRow>
          {unlockedClues.map((clue) => {
            const isNew = !interactedClueIds.includes(clue.id);

            return (
              <button
                key={clue.id}
                type="button"
                onClick={() => onOpenClue(clue)}
                className="relative h-32 w-24 shrink-0 overflow-hidden rounded-xl border border-zinc-800 bg-zinc-950 text-left active:scale-[0.98]"
              >
                {clue.imageUrl ? (
                  <Image
                    src={clue.imageUrl}
                    alt={clue.name}
                    fill
                    unoptimized
                    sizes="96px"
                    className="object-cover opacity-70"
                  />
                ) : (
                  <div className="absolute inset-0 bg-gradient-to-b from-zinc-700/20 via-zinc-950 to-black" />
                )}

                <div className="absolute left-3 top-3 flex h-10 w-10 items-center justify-center rounded-lg border border-zinc-800 bg-black/50 text-xs font-black text-zinc-600">
                  {String(clue.id).padStart(2, "0")}
                </div>

                <div className="absolute inset-x-0 bottom-0 bg-black/50 p-3">
                  <p className="line-clamp-2 text-xs font-bold leading-4 text-zinc-100">
                    {clue.name}
                  </p>
                  <p className="mt-1 text-[10px] text-zinc-600">
                    {clue.category}
                  </p>
                </div>

                {isNew && (
                  <span className="absolute right-2 top-2 rounded-full bg-red-600 px-1.5 py-0.5 text-[9px] font-black text-white">
                    NEW
                  </span>
                )}
              </button>
            );
          })}
        </HorizontalScrollRow>
      </section>

      <section>
        <HomeSectionHeader
          title="인물"
          status={hasNewCharacter ? "새 인물" : "추적 중"}
        />

        <HorizontalScrollRow>
          {unlockedCharacters.length === 0 && (
            <div className="flex h-28 min-w-56 items-center rounded-xl border border-dashed border-zinc-800 px-4 text-xs leading-5 text-zinc-600">
              첫 단서를 확인하면 관련 인물이 열립니다.
            </div>
          )}

          {unlockedCharacters.map((character) => {
            const isNew = !interactedCharacterIds.includes(character.id);

            return (
              <button
                key={character.id}
                type="button"
                onClick={() => onOpenInterrogate(character)}
                className="relative h-28 w-20 shrink-0 overflow-hidden rounded-xl border border-zinc-800 bg-zinc-950 active:scale-[0.98]"
              >
                {character.imageUrl ? (
                  <Image
                    src={character.imageUrl}
                    alt={character.name}
                    fill
                    unoptimized
                    sizes="80px"
                    className="object-cover opacity-80"
                  />
                ) : (
                  <div className="flex h-full items-center justify-center bg-gradient-to-b from-zinc-900 to-black">
                    <div className="flex h-14 w-14 items-center justify-center rounded-full bg-zinc-950 text-xl font-black text-zinc-700">
                      {character.name.slice(0, 1)}
                    </div>
                  </div>
                )}

                <div className="absolute inset-x-0 bottom-0 bg-black/75 p-2">
                  <p className="truncate text-[11px] font-bold text-zinc-100">
                    {character.name}
                  </p>
                </div>

                {isNew && (
                  <span className="absolute right-2 top-2 h-2 w-2 rounded-full bg-red-500" />
                )}
              </button>
            );
          })}
        </HorizontalScrollRow>
      </section>

      <section className="space-y-4">
        <AriaBox message={ariaMessage} />

        <button
          type="button"
          onClick={onSubmitFinal}
          className="w-full rounded-xl border border-zinc-700 bg-zinc-950 py-4 text-sm font-black text-zinc-200 active:scale-[0.99]"
        >
          추리 제출
        </button>
      </section>
    </div>
  );
}

function ClueTab({
  interactedClueIds,
  unlockedClueIds,
  onOpenClue,
}: {
  interactedClueIds: number[];
  unlockedClueIds: number[];
  onOpenClue: (clue: Clue) => void;
}) {
  const unlockedClues = clues.filter((clue) =>
    unlockedClueIds.includes(clue.id),
  );

  return (
    <div className="pb-[calc(7rem_+_env(safe-area-inset-bottom))]">
      <SectionTitle
        title="단서 목록"
        description="카드를 눌러 자세한 내용을 확인하세요."
      />

      <div className="mt-4 space-y-3">
        {unlockedClues.map((clue) => {
          const isNew = !interactedClueIds.includes(clue.id);

          return (
            <button
              key={clue.id}
              type="button"
              onClick={() => onOpenClue(clue)}
              className="w-full rounded-2xl border border-zinc-800 bg-zinc-950 p-4 text-left active:scale-[0.99]"
            >
              <div className="mb-2 flex items-start justify-between gap-3">
                <div className="flex items-center gap-2">
                  <span className="text-xs font-black text-zinc-600">
                    {String(clue.id).padStart(2, "0")}
                  </span>
                  {isNew && (
                    <span className="h-2 w-2 rounded-full bg-red-500" />
                  )}
                  <h3 className="font-bold">{clue.name}</h3>
                </div>

                <span className="rounded-full bg-zinc-900 px-2 py-1 text-[11px] text-zinc-500">
                  {clue.category}
                </span>
              </div>

              <p className="text-sm leading-6 text-zinc-500">
                {clue.shortDescription}
              </p>
            </button>
          );
        })}
      </div>
    </div>
  );
}

function CharacterTab({
  interactedCharacterIds,
  unlockedCharacterIds,
  onOpenInterrogate,
}: {
  interactedCharacterIds: number[];
  unlockedCharacterIds: number[];
  onOpenInterrogate: (character: Character) => void;
}) {
  const unlockedCharacters = interrogatableCharacters.filter((character) =>
    unlockedCharacterIds.includes(character.id),
  );

  return (
    <div className="pb-[calc(7rem_+_env(safe-area-inset-bottom))]">
      <SectionTitle
        title="인물 목록"
        description="인물을 선택해 자유 심문을 진행하세요."
      />

      <div className="mt-4 space-y-3">
        {unlockedCharacters.length === 0 && (
          <div className="rounded-2xl border border-dashed border-zinc-800 bg-zinc-950 p-5 text-sm leading-6 text-zinc-600">
            아직 심문 가능한 인물이 없습니다. 기본 단서를 먼저 확인하세요.
          </div>
        )}

        {unlockedCharacters.map((character) => {
          const isNew = !interactedCharacterIds.includes(character.id);

          return (
            <div
              key={character.id}
              className="rounded-2xl border border-zinc-800 bg-zinc-950 p-4"
            >
              <div className="mb-3 flex items-center gap-3">
                <div className="relative flex h-12 w-12 items-center justify-center overflow-hidden rounded-full border border-zinc-800 bg-black text-lg font-black text-zinc-700">
                  {character.imageUrl ? (
                    <Image
                      src={character.imageUrl}
                      alt={character.name}
                      fill
                      unoptimized
                      sizes="48px"
                      className="object-cover"
                    />
                  ) : (
                    character.name.slice(0, 1)
                  )}
                </div>

                <div className="min-w-0 flex-1">
                  <div className="flex items-center gap-2">
                    {isNew && (
                      <span className="h-2 w-2 rounded-full bg-red-500" />
                    )}
                    <h3 className="font-bold">{character.name}</h3>
                  </div>
                  <p className="mt-1 text-xs text-zinc-500">
                    {character.role} · {character.age}세
                  </p>
                </div>
              </div>

              <p className="text-sm leading-6 text-zinc-500">
                {character.description}
              </p>

              <div className="mt-3 rounded-xl bg-black p-3">
                <p className="text-xs text-zinc-600">성격</p>
                <p className="mt-1 text-sm text-zinc-400">
                  {character.personality}
                </p>
              </div>

              <div className="mt-3 rounded-xl bg-black p-3">
                <p className="text-xs text-zinc-600">의심 지점</p>
                <p className="mt-1 text-sm text-zinc-400">
                  {character.suspicionPoint}
                </p>
              </div>

              <button
                type="button"
                onClick={() => onOpenInterrogate(character)}
                className="mt-4 w-full rounded-xl bg-zinc-100 py-3 text-sm font-black text-black active:scale-[0.99]"
              >
                심문하기
              </button>
            </div>
          );
        })}
      </div>
    </div>
  );
}

function NoteTab({
  note,
  setNote,
  interactedClueIds,
  interactedCharacterIds,
}: {
  note: string;
  setNote: (note: string) => void;
  interactedClueIds: number[];
  interactedCharacterIds: number[];
}) {
  return (
    <div className="space-y-5 pb-8">
      <SectionTitle
        title="수사 노트"
        description="직접 기록하고, ARIA가 남긴 단서 안내를 함께 검토합니다."
      />

      <section className="rounded-[28px] border border-zinc-800 bg-zinc-950 p-4">
        <div className="mb-3">
          <p className="text-xs font-bold tracking-[0.18em] text-zinc-600">
            MANUAL NOTE
          </p>
          <h3 className="mt-1 text-base font-black text-zinc-200">직접 기록</h3>
        </div>

        <textarea
          value={note}
          onChange={(event) => setNote(event.target.value)}
          placeholder="예: 민재는 도윤의 MCP 호출 기록을 의심함. 하린은 서버 로그가 일부만 공개된 점을 의심함..."
          className="min-h-36 w-full resize-none rounded-2xl border border-zinc-800 bg-black px-4 py-3 text-sm leading-7 text-zinc-100 outline-none placeholder:text-zinc-700"
        />
      </section>

      <AriaEvidencePanel
        interactedClueIds={interactedClueIds}
        interactedCharacterIds={interactedCharacterIds}
      />
    </div>
  );
}

function AriaEvidencePanel({
  interactedClueIds,
  interactedCharacterIds,
}: {
  interactedClueIds: number[];
  interactedCharacterIds: number[];
}) {
  const reviewedClues = clues.filter((clue) =>
    interactedClueIds.includes(clue.id),
  );
  const reviewedCharacters = interrogatableCharacters.filter((character) =>
    interactedCharacterIds.includes(character.id),
  );
  const latestClue = reviewedClues.at(-1);

  return (
    <section
      data-swipe-ignore="true"
      className="rounded-[24px] border border-zinc-800 bg-zinc-950 p-4 min-[390px]:rounded-[28px]"
    >
      <div>
        <p className="text-xs font-bold tracking-[0.18em] text-zinc-600">
          ARIA LOG
        </p>
        <h3 className="mt-1 text-base font-black text-zinc-200">단서 안내</h3>
      </div>

      <div className="mt-4 grid grid-cols-2 gap-2">
        <div className="rounded-xl border border-zinc-800 bg-black p-3">
          <p className="text-xs text-zinc-600">확인 단서</p>
          <p className="mt-1 text-xl font-black text-zinc-100">
            {reviewedClues.length}
          </p>
        </div>

        <div className="rounded-xl border border-zinc-800 bg-black p-3">
          <p className="text-xs text-zinc-600">심문 인물</p>
          <p className="mt-1 text-xl font-black text-zinc-100">
            {reviewedCharacters.length}
          </p>
        </div>
      </div>

      {latestClue ? (
        <div className="mt-4 rounded-xl border border-zinc-800 bg-black p-3">
          <p className="text-xs text-zinc-600">최근 단서</p>
          <p className="mt-1 text-sm font-bold text-zinc-200">
            {latestClue.name}
          </p>
          <div className="mt-3 space-y-2">
            {latestClue.ariaScripts.map((script) => (
              <p key={script} className="text-sm leading-6 text-zinc-400">
                {script}
              </p>
            ))}
          </div>
        </div>
      ) : (
        <div className="mt-4 rounded-xl border border-zinc-800 bg-black p-3">
          <p className="text-sm leading-6 text-zinc-500">
            확인한 단서가 없습니다. 기본 단서를 먼저 열어보세요.
          </p>
        </div>
      )}

      <div className="mt-4 rounded-xl border border-zinc-800 bg-black p-3">
        <p className="text-xs text-zinc-600">기록 상태</p>
        <p className="mt-1 text-sm leading-6 text-zinc-400">
          ARIA는 확인된 단서의 안내 기록만 제공합니다. 아직 복구되지 않은
          기록은 조사 진행에 따라 순차적으로 드러납니다.
        </p>
      </div>
    </section>
  );
}

function CharacterChatPanel({
  character,
  chatInput,
  setChatInput,
  chatLog,
  isSending,
  isWaitingForReply,
  onSend,
  onClose,
}: {
  character: Character;
  chatInput: string;
  setChatInput: (value: string) => void;
  chatLog: AnimatedChatMessage[];
  isSending: boolean;
  isWaitingForReply: boolean;
  onSend: () => void;
  onClose: () => void;
}) {
  return (
    <div data-swipe-ignore="true" className="flex h-full min-h-0 flex-col">
      <div className="shrink-0">
        <div className="mb-4 flex items-start justify-between gap-4">
          <div>
            <p className="text-xs font-bold tracking-[0.18em] text-zinc-600">
              INTERROGATION
            </p>
            <h2 className="mt-2 text-2xl font-black">{character.name}</h2>
            <p className="mt-1 text-xs text-zinc-500">
              {character.role} · {character.age}세
            </p>
          </div>

          <button
            type="button"
            onClick={onClose}
            className="rounded-full border border-zinc-800 bg-zinc-950 px-3 py-1 text-xs font-bold text-zinc-500"
          >
            목록
          </button>
        </div>

        <div className="mb-4 rounded-2xl border border-zinc-800 bg-zinc-950 p-4">
          <p className="text-xs text-zinc-600">PERSONALITY</p>
          <p className="mt-2 text-sm leading-6 text-zinc-400">
            {character.personality}
          </p>
        </div>
      </div>

      <ChatMessageList chatLog={chatLog} isSending={isWaitingForReply} />

      <form
        onSubmit={(event) => {
          event.preventDefault();
          onSend();
        }}
        className="shrink-0 border-t border-zinc-800 bg-[#08090b] pt-4"
      >
        <div className="flex gap-2">
          <input
            value={chatInput}
            onChange={(event) => setChatInput(event.target.value)}
            placeholder="질문을 입력하세요"
            disabled={isSending}
            className="min-w-0 flex-1 rounded-xl border border-zinc-800 bg-zinc-950 px-4 py-3 text-sm outline-none placeholder:text-zinc-700 disabled:opacity-60"
          />

          <button
            type="submit"
            disabled={isSending}
            className="rounded-xl bg-zinc-100 px-4 text-sm font-black text-black active:scale-[0.99] disabled:opacity-60"
          >
            {isSending ? "생성" : "전송"}
          </button>
        </div>
      </form>
    </div>
  );
}

function ChatMessageList({
  chatLog,
  isSending,
}: {
  chatLog: AnimatedChatMessage[];
  isSending: boolean;
}) {
  const scrollContainerRef = useRef<HTMLDivElement | null>(null);
  const latestMessage = chatLog.at(-1);

  useEffect(() => {
    const scrollContainer = scrollContainerRef.current;

    if (!scrollContainer) {
      return;
    }

    scrollContainer.scrollTo({
      top: scrollContainer.scrollHeight,
      behavior: "smooth",
    });
  }, [chatLog.length, isSending, latestMessage?.text]);

  return (
    <div
      ref={scrollContainerRef}
      data-swipe-ignore="true"
      className="no-scrollbar h-full min-h-0 space-y-5 overflow-y-auto pb-5 pr-1"
    >
      {chatLog.map((message, index) => (
        <div
          key={`${message.speaker}-${index}`}
          className={`flex ${
            message.speaker === "player" ? "justify-end" : "justify-start"
          }`}
        >
          <div
            className={`max-w-[82%] whitespace-pre-wrap rounded-2xl px-4 py-3 text-sm leading-6 ${
              message.speaker === "player"
                ? "bg-zinc-100 text-black"
                : "bg-transparent text-zinc-100"
            }`}
          >
            {message.text}
            {message.isTyping && (
              <span className="ml-0.5 inline-block animate-pulse text-zinc-400">
                ▍
              </span>
            )}
          </div>
        </div>
      ))}

      {isSending && (
        <div className="flex justify-start">
          <div className="rounded-2xl bg-transparent px-4 py-3 text-sm text-zinc-500">
            답변을 생각하는 중...
          </div>
        </div>
      )}
    </div>
  );
}

function FinalScreen({
  deduction,
  interactedClueIds,
  unlockedClueIds,
  unlockedCharacterIds,
  updateDeduction,
  toggleDeductionClue,
  onBack,
  onSubmitFinal,
}: {
  deduction: DeductionForm;
  interactedClueIds: number[];
  unlockedClueIds: number[];
  unlockedCharacterIds: number[];
  updateDeduction: (value: Partial<DeductionForm>) => void;
  toggleDeductionClue: (clueId: number) => void;
  onBack: () => void;
  onSubmitFinal: () => void;
}) {
  const availableEvidence = clues.filter((clue) =>
    interactedClueIds.includes(clue.id),
  );
  const hasCollectedAllClues = clues.every((clue) =>
    interactedClueIds.includes(clue.id),
  );
  const availableDeductionTargets = deductionTargets.filter((character) => {
    if (character.id === ARIA_CHARACTER_ID) {
      return (
        hasCollectedAllClues &&
        unlockedClueIds.includes(RECOVERED_TRACE_CLUE_ID)
      );
    }

    return unlockedCharacterIds.includes(character.id);
  });

  return (
    <section className="min-h-dvh overflow-y-auto px-4 py-4 min-[390px]:px-5 min-[390px]:py-6">
      <MobileHeader title="추리 제출" onBack={onBack} />

      <div className="mt-5 space-y-6 pb-8">
        <section>
          <h2 className="mb-3 text-sm font-black text-zinc-300">
            지목 대상 선택
          </h2>
          <div className="grid grid-cols-2 gap-2">
            {availableDeductionTargets.length === 0 && (
              <div className="col-span-2 rounded-2xl border border-dashed border-zinc-800 bg-zinc-950 p-4 text-sm leading-6 text-zinc-600">
                밝혀진 용의자가 없습니다.
              </div>
            )}

            {availableDeductionTargets.map((character) => {
              const active = deduction.character === character.id;

              return (
                <button
                  key={character.id}
                  type="button"
                  onClick={() => updateDeduction({ character: character.id })}
                  className={`rounded-2xl border px-3 py-3 text-left text-sm font-bold ${
                    active
                      ? "border-zinc-100 bg-zinc-100 text-black"
                      : "border-zinc-800 bg-zinc-950 text-zinc-400"
                  }`}
                >
                  {character.name}
                </button>
              );
            })}
          </div>
        </section>

        <section>
          <h2 className="mb-3 text-sm font-black text-zinc-300">
            결정적 단서 선택
          </h2>
          <div className="space-y-2">
            {availableEvidence.length === 0 && (
              <div className="rounded-2xl border border-dashed border-zinc-800 bg-zinc-950 p-4 text-sm leading-6 text-zinc-600">
                아직 확인한 단서가 없습니다.
              </div>
            )}

            {availableEvidence.map((clue) => {
              const active = deduction.clues.includes(clue.id);

              return (
                <button
                  key={clue.id}
                  type="button"
                  onClick={() => toggleDeductionClue(clue.id)}
                  className={`w-full rounded-2xl border px-4 py-3 text-left text-sm ${
                    active
                      ? "border-zinc-100 bg-zinc-100 text-black"
                      : "border-zinc-800 bg-zinc-950 text-zinc-400"
                  }`}
                >
                  <span className="font-black">
                    {active ? "☑" : "☐"} {clue.name}
                  </span>
                  <span className="ml-2 text-xs opacity-70">
                    {clue.category}
                  </span>
                </button>
              );
            })}
          </div>
        </section>

        <label className="block">
          <span className="mb-2 block text-sm font-black text-zinc-300">
            추리 내용
          </span>
          <textarea
            value={deduction.content}
            onChange={(event) =>
              updateDeduction({ content: event.target.value })
            }
            placeholder="사건의 원인이라고 보는 대상과 근거를 단서와 함께 설명하세요."
            className="min-h-40 w-full resize-none rounded-2xl border border-zinc-800 bg-zinc-950 px-4 py-3 text-sm leading-6 outline-none placeholder:text-zinc-700"
          />
        </label>

        <button
          type="button"
          onClick={onSubmitFinal}
          className="w-full rounded-2xl bg-zinc-100 py-4 font-black text-black active:scale-[0.99]"
        >
          최종 추리 제출
        </button>
      </div>
    </section>
  );
}

function RevealScreen({
  result,
  onRestart,
}: {
  deduction: DeductionForm;
  result: DeductionResponse | null;
  onRestart: () => void;
}) {
  const isSuccess = result?.result === true;
  const resultSteps = isSuccess
    ? [
        {
          imageUrl: endingEvents.success.imageUrl,
          imageAlt: "깨지는 ARIA 로고",
          imageFit: "contain",
          speaker: "SYSTEM",
          text: endingEvents.success.systemMessages[0],
        },
        ...endingEvents.success.ariaMessages.map((message) => ({
          imageUrl: endingEvents.success.imageUrl,
          imageAlt: "깨지는 ARIA 로고",
          imageFit: "contain",
          speaker: "ARIA",
          text: message,
        })),
        ...endingEvents.success.systemMessages.slice(1).map((message) => ({
          imageUrl: endingEvents.success.imageUrl,
          imageAlt: "복구된 ARIA 기록",
          imageFit: "contain",
          speaker: "RESTORED LOG",
          text: message,
        })),
        {
          imageUrl: endingEvents.success.imageUrl,
          imageAlt: "복구된 ARIA 기록",
          imageFit: "contain",
          speaker: "JUDGEMENT",
          text: result?.comment ?? "추리 결과가 기록되었습니다.",
        },
      ]
    : [
        ...endingEvents.failure.ariaMessages.slice(0, 2).map((message) => ({
          imageUrl: endingEvents.failure.imageUrls[0],
          imageAlt: "확대된 ARIA 로고",
          imageFit: "contain",
          speaker: "ARIA",
          text: message,
        })),
        ...endingEvents.failure.ariaMessages.slice(2).map((message) => ({
          imageUrl: endingEvents.failure.imageUrls[1],
          imageAlt: "조사자가 쓰러지는 장면",
          imageFit: "cover",
          speaker: "ARIA",
          text: message,
        })),
        {
          imageUrl: endingEvents.failure.imageUrls[1],
          imageAlt: "조사자가 쓰러지는 장면",
          imageFit: "cover",
          speaker: "JUDGEMENT",
          text: result?.comment ?? "추리 결과가 기록되었습니다.",
        },
      ];
  const [stepIndex, setStepIndex] = useState(0);
  const currentStep = resultSteps[stepIndex];

  function advanceResult() {
    if (stepIndex >= resultSteps.length - 1) {
      onRestart();
      return;
    }

    setStepIndex((prev) => prev + 1);
  }

  return (
    <section className="flex min-h-dvh flex-col justify-center gap-4 overflow-y-auto px-4 py-4 min-[390px]:gap-5 min-[390px]:px-5 min-[390px]:py-6">
      <div className="relative h-[44dvh] min-h-[220px] max-h-[460px] w-full overflow-hidden rounded-[28px] border border-zinc-800 bg-black shadow-2xl">
        <Image
          key={`${stepIndex}-${currentStep.imageUrl}`}
          src={currentStep.imageUrl}
          alt={currentStep.imageAlt}
          fill
          priority={stepIndex === 0}
          unoptimized
          sizes="(max-width: 430px) 100vw, 430px"
          className={`${
            currentStep.imageFit === "contain" ? "object-contain" : "object-cover"
          }`}
        />
      </div>

      <CutsceneText
        key={stepIndex}
        speaker={currentStep.speaker}
        text={currentStep.text}
        isLastStep={stepIndex === resultSteps.length - 1}
        lastStepLabel="클릭해서 처음으로"
        onAdvance={advanceResult}
      />
    </section>
  );
}

function ClueModal({
  clue,
  onClose,
  onTraceRefClick,
}: {
  clue: Clue;
  onClose: () => void;
  onTraceRefClick: () => Promise<string>;
}) {
  const [displayedText, setDisplayedText] = useState("");
  const [traceMessage, setTraceMessage] = useState<string | null>(null);
  const descriptionPanelRef = useRef<HTMLDivElement | null>(null);
  const typingTimerRef = useRef<number | null>(null);

  function clearTypingTimer() {
    if (typingTimerRef.current) {
      window.clearInterval(typingTimerRef.current);
      typingTimerRef.current = null;
    }
  }

  function skipTyping() {
    clearTypingTimer();
    setDisplayedText(clue.description);
  }

  async function handleTraceRefClick() {
    const nextTraceMessage = await onTraceRefClick();
    setTraceMessage(nextTraceMessage);
  }

  function scrollDescriptionPanelToBottom() {
    window.requestAnimationFrame(() => {
      const descriptionPanel = descriptionPanelRef.current;

      if (!descriptionPanel) {
        return;
      }

      descriptionPanel.scrollTo({
        top: descriptionPanel.scrollHeight,
        behavior: "smooth",
      });
    });
  }

  useEffect(() => {
    clearTypingTimer();

    let index = 0;

    typingTimerRef.current = window.setInterval(() => {
      setDisplayedText(clue.description.slice(0, index + 1));
      index += 1;

      if (index >= clue.description.length) {
        clearTypingTimer();
      }
    }, 24);

    return () => {
      clearTypingTimer();
    };
  }, [clue.description]);

  useEffect(() => {
    if (!traceMessage) {
      return;
    }

    scrollDescriptionPanelToBottom();
  }, [traceMessage]);

  useEffect(() => {
    const descriptionPanel = descriptionPanelRef.current;

    if (!descriptionPanel) {
      return;
    }

    if (descriptionPanel.scrollHeight <= descriptionPanel.clientHeight) {
      return;
    }

    descriptionPanel.scrollTo({
      top: descriptionPanel.scrollHeight,
      behavior: "smooth",
    });
  }, [displayedText]);

  return (
    <div
      onClick={onClose}
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/75 p-3 min-[390px]:p-4"
    >
      <div
        onClick={(event) => {
          event.stopPropagation();
          skipTyping();
        }}
        className="flex max-h-[calc(100dvh-24px)] w-full max-w-[430px] cursor-pointer flex-col overflow-hidden rounded-[24px] border border-zinc-800 bg-[#08090b] p-4 shadow-2xl active:border-zinc-700 active:bg-zinc-950 min-[390px]:max-h-[calc(100dvh-32px)] min-[390px]:rounded-[28px] min-[390px]:p-5"
        role="button"
        tabIndex={0}
        aria-label="단서 카드 타이핑 효과 건너뛰기"
      >
        <div className="mb-3">
          <p className="mb-1 text-xs font-bold text-zinc-600">
            {clue.category}
          </p>
          <h2 className="text-xl font-black">{clue.name}</h2>
        </div>

        {clue.imageUrl && (
          <div className="relative mb-4 flex h-[30dvh] min-h-36 max-h-52 w-full items-center justify-center overflow-hidden rounded-2xl border border-zinc-800 bg-black">
            <Image
              src={clue.imageUrl}
              alt={clue.name}
              fill
              unoptimized
              sizes="(max-width: 430px) 100vw, 430px"
              className="object-contain"
            />
          </div>
        )}

        <div
          ref={descriptionPanelRef}
          className={`no-scrollbar overflow-y-auto rounded-2xl border border-zinc-800 bg-black p-4 text-sm leading-7 text-zinc-400 ${
            clue.id === RECOVERED_TRACE_CLUE_ID
              ? "h-[42dvh]"
              : "h-[34dvh]"
          }`}
        >
          <div className="whitespace-pre-wrap">
            {clue.id === RECOVERED_TRACE_CLUE_ID ? (
              <RecoveredTraceDescription
                text={displayedText}
                fullText={clue.description}
              />
            ) : (
              <ClueDescriptionText
                text={displayedText}
                onTraceRefClick={handleTraceRefClick}
              />
            )}
            {displayedText.length < clue.description.length && (
              <span className="ml-0.5 animate-pulse text-zinc-300">▍</span>
            )}
          </div>

          {traceMessage && (
            <div className="mt-4 rounded-2xl border border-sky-500/30 bg-sky-950/20 p-3">
              <p className="text-[11px] font-black tracking-[0.18em] text-sky-400">
                ARIA
              </p>
              <p className="mt-2 whitespace-pre-wrap text-sm leading-6 text-sky-100">
                {traceMessage}
              </p>
            </div>
          )}
        </div>

      </div>
    </div>
  );
}

function ClueDescriptionText({
  text,
  onTraceRefClick,
}: {
  text: string;
  onTraceRefClick: () => void;
}) {
  const traceRefIndex = text.indexOf(TRACE_REF_TEXT);

  if (traceRefIndex === -1) {
    return text;
  }

  const beforeTraceRef = text.slice(0, traceRefIndex);
  const afterTraceRef = text.slice(traceRefIndex + TRACE_REF_TEXT.length);

  return (
    <>
      {beforeTraceRef}
      <button
        type="button"
        onClick={(event) => {
          event.stopPropagation();
          onTraceRefClick();
        }}
        className="rounded-sm text-left font-semibold text-sky-400 underline decoration-sky-400/50 underline-offset-4 transition hover:text-sky-300 active:text-sky-200"
      >
        {TRACE_REF_TEXT}
      </button>
      {afterTraceRef}
    </>
  );
}

function RecoveredTraceDescription({
  text,
  fullText,
}: {
  text: string;
  fullText: string;
}) {
  const visibleLines = text.split("\n");
  const fullLines = fullText.split("\n");
  const progressRatio = fullText.length === 0 ? 1 : text.length / fullText.length;
  const translationProgress =
    clamp(
      (progressRatio - RECOVERED_TRACE_TRANSLATION_START_RATIO) /
        (1 - RECOVERED_TRACE_TRANSLATION_START_RATIO),
      0,
      1,
    ) * getRecoveredTraceTranslationDuration();

  return (
    <div className="font-mono text-[13px] leading-6">
      {visibleLines.map((visibleLine, lineIndex) => {
        const translation = RECOVERED_TRACE_TRANSLATION_LINES[lineIndex] ?? "";
        const fullLine = fullLines[lineIndex] ?? visibleLine;
        const previousDuration = getRecoveredTracePreviousDuration(lineIndex);
        const currentDuration = getRecoveredTraceLineDuration(translation);
        const lineProgress = clamp(
          (translationProgress - previousDuration) / currentDuration,
          0,
          1,
        );
        const translatedLength = Math.ceil(translation.length * lineProgress);
        const originalStartIndex = Math.floor(fullLine.length * lineProgress);
        const mixedLine =
          lineProgress >= 1
            ? translation
            : `${translation.slice(0, translatedLength)}${visibleLine.slice(
                Math.min(originalStartIndex, visibleLine.length),
              )}`;

        return (
          <div
            key={`${lineIndex}-${fullLine}`}
            className={`min-h-6 whitespace-pre ${
              lineProgress > 0 ? "text-zinc-100" : "text-zinc-300"
            }`}
          >
            {mixedLine || "\u00a0"}
          </div>
        );
      })}
    </div>
  );
}

function getRecoveredTraceLineDuration(line: string) {
  return Math.max(1, line.length + 6);
}

function getRecoveredTracePreviousDuration(lineIndex: number) {
  return RECOVERED_TRACE_TRANSLATION_LINES.slice(0, lineIndex).reduce(
    (total, line) => total + getRecoveredTraceLineDuration(line),
    0,
  );
}

function getRecoveredTraceTranslationDuration() {
  return RECOVERED_TRACE_TRANSLATION_LINES.reduce(
    (total, line) => total + getRecoveredTraceLineDuration(line),
    0,
  );
}

function clamp(value: number, min: number, max: number) {
  return Math.min(max, Math.max(min, value));
}

function BottomNav({
  current,
  onChange,
}: {
  current: MainTab;
  onChange: (tab: MainTab) => void;
}) {
  const items: { id: MainTab; label: string; icon: string }[] = [
    { id: "home", label: "홈", icon: "⌂" },
    { id: "clue", label: "단서", icon: "□" },
    { id: "character", label: "인물", icon: "◉" },
    { id: "note", label: "노트", icon: "≡" },
  ];

  return (
    <nav className="fixed bottom-0 left-1/2 z-40 grid w-full max-w-[430px] -translate-x-1/2 grid-cols-4 border-t border-zinc-900 bg-[#08090b]/95 backdrop-blur">
      {items.map((item) => {
        const active = current === item.id;

        return (
          <button
            key={item.id}
            type="button"
            onClick={() => onChange(item.id)}
            className={`flex flex-col items-center gap-1 pb-[calc(0.75rem_+_env(safe-area-inset-bottom))] pt-3 text-[11px] font-bold ${
              active ? "text-zinc-100" : "text-zinc-700"
            }`}
          >
            <span className="text-base leading-none">{item.icon}</span>
            <span>{item.label}</span>
          </button>
        );
      })}
    </nav>
  );
}

function MobileHeader({
  title,
  subtitle,
  onBack,
}: {
  title: string;
  subtitle?: string;
  onBack: () => void;
}) {
  return (
    <header>
      <button
        type="button"
        onClick={onBack}
        className="mb-4 text-sm text-zinc-600"
      >
        ← 뒤로
      </button>
      <h1 className="text-xl font-black">{title}</h1>
      {subtitle && <p className="mt-1 text-xs text-zinc-500">{subtitle}</p>}
    </header>
  );
}

function HomeSectionHeader({
  title,
  status,
}: {
  title: string;
  status: string;
}) {
  return (
    <div className="mb-3 flex items-end justify-between">
      <h2 className="text-sm font-black text-zinc-300">{title}</h2>
      <span className="text-xs font-bold text-zinc-600">
        {status}
      </span>
    </div>
  );
}

function AriaBox({ message }: { message: string }) {
  return (
    <div>
      <div className="mb-2 flex items-center gap-2">
        <span className="text-xs font-black text-zinc-500">ARIA</span>
        <div className="h-px flex-1 bg-zinc-800" />
        <span className="text-zinc-600">→</span>
      </div>

      <p className="text-sm leading-6 text-zinc-500">{message}</p>
    </div>
  );
}

function SectionTitle({
  title,
  description,
}: {
  title: string;
  description: string;
}) {
  return (
    <div>
      <p className="text-xs font-bold tracking-[0.18em] text-zinc-600">
        {caseInfo.code}
      </p>
      <h2 className="mt-2 text-2xl font-black">{title}</h2>
      <p className="mt-1 text-sm text-zinc-600">{description}</p>
    </div>
  );
}
