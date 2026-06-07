const state = {
  sources: [],
  topics: [],
  profiles: [],
  lastPayload: null,
  sourceStatusLoaded: false,
};

const elements = {
  sourceOptions: document.querySelector("#sourceOptions"),
  topicOptions: document.querySelector("#topicOptions"),
  form: document.querySelector("#briefingForm"),
  dateRange: document.querySelector("#dateRange"),
  limit: document.querySelector("#limit"),
  customKeywords: document.querySelector("#customKeywords"),
  excludeKeywords: document.querySelector("#excludeKeywords"),
  customKeywordPreview: document.querySelector("#customKeywordPreview"),
  excludeKeywordPreview: document.querySelector("#excludeKeywordPreview"),
  sourceSearch: document.querySelector("#sourceSearch"),
  sourceSelectionSummary: document.querySelector("#sourceSelectionSummary"),
  topicSelectionSummary: document.querySelector("#topicSelectionSummary"),
  selectAllSourcesButton: document.querySelector("#selectAllSourcesButton"),
  clearSourcesButton: document.querySelector("#clearSourcesButton"),
  defaultTopicsButton: document.querySelector("#defaultTopicsButton"),
  clearTopicsButton: document.querySelector("#clearTopicsButton"),
  resetButton: document.querySelector("#resetButton"),
  profileName: document.querySelector("#profileName"),
  saveProfileButton: document.querySelector("#saveProfileButton"),
  profileRefreshButton: document.querySelector("#profileRefreshButton"),
  profileList: document.querySelector("#profileList"),
  systemStatus: document.querySelector("#systemStatus"),
  resultMeta: document.querySelector("#resultMeta"),
  briefingTitle: document.querySelector("#briefingTitle"),
  noticeStack: document.querySelector("#noticeStack"),
  statsGrid: document.querySelector("#statsGrid"),
  commonTopics: document.querySelector("#commonTopics"),
  commonTopicList: document.querySelector("#commonTopicList"),
  emptyState: document.querySelector("#emptyState"),
  articleList: document.querySelector("#articleList"),
  refreshButton: document.querySelector("#refreshButton"),
  historyList: document.querySelector("#historyList"),
  historyRefreshButton: document.querySelector("#historyRefreshButton"),
  presetList: document.querySelector("#presetList"),
  sourceStatusList: document.querySelector("#sourceStatusList"),
  sourceStatusRefreshButton: document.querySelector("#sourceStatusRefreshButton"),
};

async function fetchJson(url, options) {
  const response = await fetch(url, options);
  if (!response.ok) {
    const payload = await response.json().catch(() => ({}));
    throw new Error(payload.detail || "요청을 처리하지 못했습니다.");
  }
  return response.status === 204 ? null : response.json();
}

function optionChip(option, name, checked = false) {
  const label = document.createElement("label");
  label.className = "option-chip";
  label.title = option.label;

  const input = document.createElement("input");
  input.type = "checkbox";
  input.name = name;
  input.value = option.id;
  input.checked = checked;
  input.addEventListener("change", updateSelectionSummary);

  const text = document.createElement("span");
  text.textContent = option.label;

  label.append(input, text);
  return label;
}

async function loadOptions() {
  const [sources, topics] = await Promise.all([
    fetchJson("/api/sources"),
    fetchJson("/api/topics"),
  ]);

  state.sources = sources;
  state.topics = topics;

  elements.sourceOptions.innerHTML = "";
  elements.topicOptions.innerHTML = "";
  sources.forEach((source) => {
    elements.sourceOptions.append(optionChip(source, "sources", true));
  });
  topics.forEach((topic, index) => {
    elements.topicOptions.append(optionChip(topic, "topics", index < 3));
  });
  updateSelectionSummary();
}

async function loadHealth() {
  try {
    const health = await fetchJson("/health");
    const summarizer = health.upstage_configured ? `Upstage ${health.upstage_model}` : "로컬 요약";
    elements.systemStatus.textContent = health.rss_enabled ? `RSS + ${summarizer}` : summarizer;
  } catch {
    elements.systemStatus.textContent = "연결 실패";
  }
}

async function loadPresets() {
  try {
    renderPresets(await fetchJson("/api/presets"));
  } catch {
    renderPresets([]);
  }
}

function renderPresets(presets) {
  elements.presetList.innerHTML = "";
  presets.forEach((preset) => {
    const button = document.createElement("button");
    button.className = "preset-button";
    button.type = "button";
    button.title = preset.description;
    button.addEventListener("click", () => {
      const payload = {
        sources: preset.sources,
        topics: preset.topics,
        custom_keywords: preset.custom_keywords || [],
        exclude_keywords: preset.exclude_keywords || [],
        date_range: preset.date_range,
        limit: preset.limit,
      };
      applyPayloadToControls(payload);
      createBriefing(payload);
    });

    const title = document.createElement("span");
    title.className = "preset-title";
    title.textContent = preset.label;

    const meta = document.createElement("span");
    meta.className = "preset-meta";
    const focus = [...preset.topics.map(topicLabel), ...(preset.custom_keywords || [])].join(", ");
    meta.textContent = `${dateRangeLabel(preset.date_range)} · 기사 ${preset.limit}건 · ${focus}`;

    button.append(title, meta);
    elements.presetList.append(button);
  });
}

async function loadProfiles() {
  try {
    state.profiles = await fetchJson("/api/profiles");
    renderProfiles(state.profiles);
  } catch {
    renderProfiles([]);
  }
}

function renderProfiles(profiles) {
  elements.profileList.innerHTML = "";
  if (!profiles.length) {
    const empty = document.createElement("p");
    empty.className = "history-empty";
    empty.textContent = "저장된 프로필이 없습니다.";
    elements.profileList.append(empty);
    return;
  }

  profiles.forEach((profile) => {
    const item = document.createElement("div");
    item.className = "profile-item";

    const main = document.createElement("button");
    main.className = "profile-load";
    main.type = "button";
    main.addEventListener("click", () => applyPayloadToControls(profile));

    const title = document.createElement("span");
    title.className = "history-title";
    title.textContent = profile.name;

    const meta = document.createElement("span");
    meta.className = "history-meta";
    const focus = [
      ...profile.topics.map(topicLabel),
      ...(profile.custom_keywords || []),
      ...(profile.exclude_keywords || []).map((keyword) => `제외 ${keyword}`),
    ].join(", ");
    meta.textContent = `${dateRangeLabel(profile.date_range)} · 기사 ${profile.limit}건${focus ? ` · ${focus}` : ""}`;

    const remove = document.createElement("button");
    remove.className = "profile-delete";
    remove.type = "button";
    remove.title = "프로필 삭제";
    remove.textContent = "삭제";
    remove.addEventListener("click", () => deleteProfile(profile.id));

    main.append(title, meta);
    item.append(main, remove);
    elements.profileList.append(item);
  });
}

async function saveProfile() {
  const name = elements.profileName.value.trim();
  if (!name) {
    renderNotices(["프로필 이름을 입력해주세요."], "error");
    return;
  }
  const payload = { name, ...readPayload() };
  try {
    await fetchJson("/api/profiles", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    elements.profileName.value = "";
    await loadProfiles();
    renderNotices([`프로필 "${name}"을 저장했습니다.`]);
  } catch (error) {
    renderNotices([error.message], "error");
  }
}

async function deleteProfile(profileId) {
  try {
    await fetchJson(`/api/profiles/${profileId}`, { method: "DELETE" });
    await loadProfiles();
  } catch (error) {
    renderNotices([error.message], "error");
  }
}

async function loadHistory() {
  try {
    renderHistory(await fetchJson("/api/briefings/history"));
  } catch {
    renderHistory([]);
  }
}

function renderHistory(items) {
  elements.historyList.innerHTML = "";
  if (!items.length) {
    const empty = document.createElement("p");
    empty.className = "history-empty";
    empty.textContent = "아직 저장된 브리핑이 없습니다.";
    elements.historyList.append(empty);
    return;
  }

  items.forEach((item) => {
    const button = document.createElement("button");
    button.className = "history-item";
    button.type = "button";
    button.title = item.title;
    button.addEventListener("click", () => {
      switchTab("briefing");
      loadBriefing(item.id);
    });

    const title = document.createElement("span");
    title.className = "history-title";
    title.textContent = item.title;

    const meta = document.createElement("span");
    meta.className = "history-meta";
    const focus = [
      ...item.topic_labels,
      ...(item.custom_keywords || []),
      ...(item.exclude_keywords || []).map((keyword) => `제외 ${keyword}`),
    ].join(", ");
    meta.textContent = `${formatDate(item.generated_at)} · 기사 ${item.article_count}건${focus ? ` · ${focus}` : ""}`;

    button.append(title, meta);
    elements.historyList.append(button);
  });
}

async function loadBriefing(id) {
  try {
    const response = await fetchJson(`/api/briefings/${id}`);
    renderBriefing(response.briefing);
  } catch (error) {
    renderNotices([error.message], "error");
  }
}

function readPayload() {
  return {
    sources: [...document.querySelectorAll("input[name='sources']:checked")].map((input) => input.value),
    topics: [...document.querySelectorAll("input[name='topics']:checked")].map((input) => input.value),
    custom_keywords: parseKeywords(elements.customKeywords.value),
    exclude_keywords: parseKeywords(elements.excludeKeywords.value),
    date_range: elements.dateRange.value,
    limit: Math.min(10, Math.max(1, Number(elements.limit.value || 5))),
  };
}

function applyPayloadToControls(payload) {
  elements.sourceSearch.value = "";
  filterSources();
  document.querySelectorAll("input[name='sources']").forEach((input) => {
    input.checked = payload.sources.includes(input.value);
  });
  document.querySelectorAll("input[name='topics']").forEach((input) => {
    input.checked = payload.topics.includes(input.value);
  });
  elements.customKeywords.value = (payload.custom_keywords || []).join(", ");
  elements.excludeKeywords.value = (payload.exclude_keywords || []).join(", ");
  elements.dateRange.value = payload.date_range;
  elements.limit.value = payload.limit;
  updateKeywordPreviews();
  updateSelectionSummary();
}

function parseKeywords(value) {
  return [...new Set(
    value
      .split(/[\n,]+/)
      .map((keyword) => keyword.trim())
      .filter(Boolean)
  )].slice(0, 20);
}

function topicLabel(topicId) {
  return state.topics.find((topic) => topic.id === topicId)?.label || topicId;
}

function updateKeywordPreviews() {
  renderKeywordPreview(elements.customKeywordPreview, parseKeywords(elements.customKeywords.value));
  renderKeywordPreview(elements.excludeKeywordPreview, parseKeywords(elements.excludeKeywords.value));
}

function renderKeywordPreview(container, keywords) {
  container.innerHTML = "";
  keywords.forEach((keyword) => {
    const item = document.createElement("span");
    item.textContent = keyword;
    container.append(item);
  });
}

function updateSelectionSummary() {
  const selectedSources = document.querySelectorAll("input[name='sources']:checked").length;
  const selectedTopics = document.querySelectorAll("input[name='topics']:checked").length;
  elements.sourceSelectionSummary.textContent = `${selectedSources}개 언론사 선택`;
  elements.topicSelectionSummary.textContent = `${selectedTopics}개 분야 선택`;
}

function filterSources() {
  const query = elements.sourceSearch.value.trim().toLowerCase();
  document.querySelectorAll("#sourceOptions .option-chip").forEach((chip) => {
    const label = chip.textContent.trim().toLowerCase();
    chip.hidden = query && !label.includes(query);
  });
}

function setSources(checked) {
  document.querySelectorAll("input[name='sources']").forEach((input) => {
    if (!input.closest(".option-chip").hidden) {
      input.checked = checked;
    }
  });
  updateSelectionSummary();
}

function resetControls() {
  elements.sourceSearch.value = "";
  filterSources();
  document.querySelectorAll("input[name='sources']").forEach((input) => {
    input.checked = true;
  });
  document.querySelectorAll("input[name='topics']").forEach((input, index) => {
    input.checked = index < 3;
  });
  elements.customKeywords.value = "";
  elements.excludeKeywords.value = "";
  elements.dateRange.value = "1d";
  elements.limit.value = "5";
  updateKeywordPreviews();
  updateSelectionSummary();
}

function setLoading(isLoading) {
  const button = elements.form.querySelector("button[type='submit']");
  button.disabled = isLoading;
  if (isLoading) {
    button.textContent = "생성 중...";
    return;
  }
  button.innerHTML = `
    <svg aria-hidden="true" viewBox="0 0 24 24">
      <path d="M4 4h16v4H4zM4 10h10v10H4zM16 10h4v10h-4z"></path>
    </svg>
    브리핑 생성
  `;
}

function renderNotices(notices, type = "info") {
  elements.noticeStack.innerHTML = "";
  notices.forEach((notice) => {
    const item = document.createElement("div");
    item.className = `notice ${type === "error" ? "error" : ""}`;
    item.textContent = notice;
    elements.noticeStack.append(item);
  });
}

function renderStats(stats) {
  elements.statsGrid.innerHTML = "";
  if (!stats) {
    elements.statsGrid.hidden = true;
    return;
  }
  const items = [
    ["수집", stats.collected_count],
    ["매칭", stats.matched_count],
    ["중복 제거 후", stats.deduped_count],
    ["요약", stats.selected_count],
    ["언론사", stats.source_count],
    ["실패 RSS", stats.failed_feed_count],
  ];
  items.forEach(([label, value]) => {
    const item = document.createElement("div");
    item.className = "stat-card";
    item.innerHTML = `<span>${label}</span><strong>${value}</strong>`;
    elements.statsGrid.append(item);
  });
  elements.statsGrid.hidden = false;
}

function renderCommonTopics(commonTopics) {
  elements.commonTopicList.innerHTML = "";
  elements.commonTopics.hidden = commonTopics.length === 0;
  commonTopics.forEach((topic) => {
    const item = document.createElement("li");
    item.textContent = topic;
    elements.commonTopicList.append(item);
  });
}

function formatDate(value) {
  if (!value) return "";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return new Intl.DateTimeFormat("ko-KR", {
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  }).format(date);
}

function dateRangeLabel(value) {
  return value === "1d" ? "오늘" : "최근 7일";
}

function articleCard(article) {
  const card = document.createElement("article");
  card.className = "article-card refined";

  const topline = document.createElement("div");
  topline.className = "article-topline";

  const source = document.createElement("span");
  source.className = "article-source";
  source.textContent = article.source;

  const dot = document.createElement("span");
  dot.setAttribute("aria-hidden", "true");
  dot.textContent = "·";

  const date = document.createElement("span");
  date.className = "article-date";
  date.textContent = formatDate(article.published_at);

  const priority = document.createElement("span");
  priority.className = `priority-pill priority-${article.priority_label || "참고"}`;
  priority.textContent = `${article.priority_label || "참고"} ${article.priority_score || 0}`;

  topline.append(source, dot, date, priority);

  const title = document.createElement("h3");
  title.className = "article-title";
  title.textContent = article.title;

  const keywords = document.createElement("div");
  keywords.className = "article-keywords";
  (article.matched_keywords || []).forEach((keyword) => {
    const badge = document.createElement("span");
    badge.textContent = keyword;
    keywords.append(badge);
  });

  const summary = document.createElement("p");
  summary.className = "article-summary";
  summary.textContent = article.summary || article.description || "";

  const why = document.createElement("details");
  why.className = "article-detail";
  const whySummary = document.createElement("summary");
  whySummary.textContent = "왜 중요한가";
  const whyText = document.createElement("p");
  whyText.textContent = article.why_it_matters || "선택한 관심 조건과 관련된 최신 흐름을 파악하는 데 도움이 됩니다.";
  why.append(whySummary, whyText);

  const reason = document.createElement("details");
  reason.className = "article-detail";
  const reasonSummary = document.createElement("summary");
  reasonSummary.textContent = "선정 기준";
  const reasonText = document.createElement("p");
  reasonText.textContent = article.priority_reason || "선택 조건과 최신성을 기준으로 선정했습니다.";
  reason.append(reasonSummary, reasonText);

  const link = document.createElement("a");
  link.className = "article-link";
  link.target = "_blank";
  link.rel = "noreferrer";
  link.href = article.url;
  link.innerHTML = `
    원문 보기
    <svg aria-hidden="true" viewBox="0 0 24 24">
      <path d="M14 3h7v7h-2V6.41l-9.29 9.3-1.42-1.42 9.3-9.29H14z"></path>
      <path d="M5 5h6v2H7v10h10v-4h2v6H5z"></path>
    </svg>
  `;

  card.append(topline, title);
  if (keywords.children.length) card.append(keywords);
  card.append(summary, why, reason, link);
  return card;
}

function renderBriefing(briefing) {
  switchTab("briefing");
  const focusLabels = [
    ...briefing.topic_labels,
    ...(briefing.custom_keywords || []),
    ...(briefing.exclude_keywords || []).map((keyword) => `제외 ${keyword}`),
  ];
  elements.resultMeta.textContent = `${dateRangeLabel(briefing.date_range)} · ${briefing.source_labels.join(", ")} · ${focusLabels.join(", ")}`;
  elements.briefingTitle.textContent = briefing.title;
  renderNotices(briefing.notices || []);
  renderStats(briefing.stats);
  renderCommonTopics(briefing.common_topics || []);

  elements.articleList.innerHTML = "";
  elements.emptyState.hidden = briefing.articles.length > 0;
  briefing.articles.forEach((article) => {
    elements.articleList.append(articleCard(article));
  });
}

async function createBriefing(payload) {
  state.lastPayload = payload;
  if (!payload.sources.length) {
    renderNotices(["언론사를 하나 이상 선택해주세요."], "error");
    switchTab("briefing");
    return;
  }
  if (!payload.topics.length && !payload.custom_keywords.length) {
    renderNotices(["관심 분야나 포함 키워드를 하나 이상 선택해주세요."], "error");
    switchTab("briefing");
    return;
  }
  setLoading(true);
  renderNotices([]);
  try {
    const response = await fetchJson("/api/briefings", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    renderBriefing(response.briefing);
    await loadHistory();
  } catch (error) {
    renderNotices([error.message], "error");
    switchTab("briefing");
  } finally {
    setLoading(false);
  }
}

async function loadSourceStatus(force = false) {
  if (state.sourceStatusLoaded && !force) return;
  elements.sourceStatusList.innerHTML = "<p class=\"history-empty\">RSS 상태를 확인하고 있습니다.</p>";
  try {
    const statuses = await fetchJson("/api/sources/status");
    renderSourceStatuses(statuses);
    state.sourceStatusLoaded = true;
  } catch (error) {
    elements.sourceStatusList.innerHTML = "";
    const item = document.createElement("p");
    item.className = "notice error";
    item.textContent = error.message;
    elements.sourceStatusList.append(item);
  }
}

function renderSourceStatuses(statuses) {
  elements.sourceStatusList.innerHTML = "";
  statuses.forEach((status) => {
    const card = document.createElement("article");
    card.className = `source-status-card status-${status.status}`;
    const statusLabel = status.status === "ok" ? "정상" : status.status === "partial" ? "부분" : "오류";
    card.innerHTML = `
      <div>
        <strong>${status.label}</strong>
        <span>${status.domain}</span>
      </div>
      <p>${status.message}</p>
      <dl>
        <dt>RSS</dt><dd>${status.ok_feed_count}/${status.feed_count}</dd>
        <dt>기사</dt><dd>${status.article_count}</dd>
        <dt>상태</dt><dd>${statusLabel}</dd>
      </dl>
    `;
    elements.sourceStatusList.append(card);
  });
}

function switchTab(tabName) {
  document.querySelectorAll(".tab-button").forEach((button) => {
    button.classList.toggle("active", button.dataset.tab === tabName);
  });
  const panels = {
    briefing: document.querySelector("#briefingPanel"),
    sources: document.querySelector("#sourcesPanel"),
    history: document.querySelector("#historyPanel"),
  };
  Object.entries(panels).forEach(([name, panel]) => {
    const active = name === tabName;
    panel.hidden = !active;
    panel.classList.toggle("active", active);
  });
  if (tabName === "sources") loadSourceStatus();
  if (tabName === "history") loadHistory();
}

elements.form.addEventListener("submit", (event) => {
  event.preventDefault();
  createBriefing(readPayload());
});
elements.refreshButton.addEventListener("click", () => createBriefing(state.lastPayload || readPayload()));
elements.historyRefreshButton.addEventListener("click", loadHistory);
elements.sourceStatusRefreshButton.addEventListener("click", () => loadSourceStatus(true));
elements.profileRefreshButton.addEventListener("click", loadProfiles);
elements.saveProfileButton.addEventListener("click", saveProfile);
elements.sourceSearch.addEventListener("input", filterSources);
elements.customKeywords.addEventListener("input", updateKeywordPreviews);
elements.excludeKeywords.addEventListener("input", updateKeywordPreviews);
elements.selectAllSourcesButton.addEventListener("click", () => setSources(true));
elements.clearSourcesButton.addEventListener("click", () => setSources(false));
elements.defaultTopicsButton.addEventListener("click", () => {
  document.querySelectorAll("input[name='topics']").forEach((input, index) => {
    input.checked = index < 3;
  });
  updateSelectionSummary();
});
elements.clearTopicsButton.addEventListener("click", () => {
  document.querySelectorAll("input[name='topics']").forEach((input) => {
    input.checked = false;
  });
  updateSelectionSummary();
});
elements.resetButton.addEventListener("click", resetControls);
document.querySelectorAll(".tab-button").forEach((button) => {
  button.addEventListener("click", () => switchTab(button.dataset.tab));
});

async function init() {
  try {
    await loadOptions();
    updateKeywordPreviews();
    await Promise.all([loadHealth(), loadHistory(), loadPresets(), loadProfiles()]);
  } catch (error) {
    renderNotices([error.message], "error");
  }
}

init();
