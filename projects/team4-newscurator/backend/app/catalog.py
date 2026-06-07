from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SourceOption:
    id: str
    label: str
    domain: str
    rss_urls: tuple[str, ...]


@dataclass(frozen=True)
class TopicOption:
    id: str
    label: str
    keywords: tuple[str, ...]


SOURCES: tuple[SourceOption, ...] = (
    SourceOption(
        id="yonhap",
        label="연합뉴스",
        domain="yna.co.kr",
        rss_urls=(
            "https://www.yna.co.kr/rss/news.xml",
            "https://www.yna.co.kr/rss/economy.xml",
            "https://www.yna.co.kr/rss/industry.xml",
        ),
    ),
    SourceOption(
        id="mk",
        label="매일경제",
        domain="mk.co.kr",
        rss_urls=(
            "https://www.mk.co.kr/rss/30000001/",
            "https://www.mk.co.kr/rss/40300001/",
            "https://www.mk.co.kr/rss/30100041/",
            "https://www.mk.co.kr/rss/50100032/",
        ),
    ),
    SourceOption(
        id="hankyung",
        label="한국경제",
        domain="hankyung.com",
        rss_urls=(
            "https://www.hankyung.com/feed/all-news",
            "https://www.hankyung.com/feed/economy",
            "https://www.hankyung.com/feed/it",
        ),
    ),
    SourceOption(
        id="newsis",
        label="뉴시스",
        domain="newsis.com",
        rss_urls=(
            "https://newsis.com/RSS/economy.xml",
            "https://newsis.com/RSS/industry.xml",
            "https://newsis.com/RSS/health.xml",
            "https://newsis.com/RSS/bank.xml",
        ),
    ),
    SourceOption(
        id="chosun",
        label="조선일보",
        domain="chosun.com",
        rss_urls=(
            "https://www.chosun.com/arc/outboundfeeds/rss/?outputType=xml",
            "https://www.chosun.com/arc/outboundfeeds/rss/category/economy/?outputType=xml",
        ),
    ),
    SourceOption(
        id="hani",
        label="한겨레",
        domain="hani.co.kr",
        rss_urls=(
            "https://www.hani.co.kr/rss/",
            "https://www.hani.co.kr/rss/economy/",
            "https://www.hani.co.kr/rss/science/",
        ),
    ),
    SourceOption(
        id="khan",
        label="경향신문",
        domain="khan.co.kr",
        rss_urls=(
            "https://www.khan.co.kr/rss/rssdata/total_news.xml",
            "https://www.khan.co.kr/rss/rssdata/economy_news.xml",
            "https://www.khan.co.kr/rss/rssdata/it_news.xml",
        ),
    ),
    SourceOption(
        id="donga",
        label="동아일보",
        domain="donga.com",
        rss_urls=(
            "https://rss.donga.com/total.xml",
            "https://rss.donga.com/economy.xml",
            "https://rss.donga.com/science.xml",
        ),
    ),
    SourceOption(
        id="mediatoday",
        label="미디어오늘",
        domain="mediatoday.co.kr",
        rss_urls=(
            "https://www.mediatoday.co.kr/rss/allArticle.xml",
            "https://www.mediatoday.co.kr/rss/S1N3.xml",
            "https://www.mediatoday.co.kr/rss/S1N7.xml",
        ),
    ),
    SourceOption(
        id="seoul",
        label="서울신문",
        domain="seoul.co.kr",
        rss_urls=("https://www.seoul.co.kr/xml/rss/rss_economy.xml",),
    ),
    SourceOption(
        id="segye",
        label="세계일보",
        domain="segye.com",
        rss_urls=(
            "http://www.segye.com/Articles/RSSList/segye_recent.xml",
            "http://www.segye.com/Articles/RSSList/segye_economy.xml",
        ),
    ),
    SourceOption(
        id="pressian",
        label="프레시안",
        domain="pressian.com",
        rss_urls=(
            "https://www.pressian.com/api/v3/site/rss/news",
            "https://www.pressian.com/api/v3/site/rss/section/67",
        ),
    ),
    SourceOption(
        id="sisain",
        label="시사IN",
        domain="sisain.co.kr",
        rss_urls=(
            "https://www.sisain.co.kr/rss/allArticle.xml",
            "https://www.sisain.co.kr/rss/S1N7.xml",
        ),
    ),
    SourceOption(
        id="sisajournal",
        label="시사저널",
        domain="sisajournal.com",
        rss_urls=(
            "http://www.sisajournal.com/rss/allArticle.xml",
            "http://www.sisajournal.com/rss/S1N54.xml",
        ),
    ),
)


TOPICS: tuple[TopicOption, ...] = (
    TopicOption(
        id="ai",
        label="AI",
        keywords=("AI", "인공지능", "생성형", "LLM", "챗GPT", "오픈AI", "반도체", "데이터센터"),
    ),
    TopicOption(
        id="it",
        label="IT",
        keywords=("IT", "소프트웨어", "플랫폼", "클라우드", "보안", "데이터", "앱", "디지털", "AI", "반도체"),
    ),
    TopicOption(
        id="economy",
        label="경제",
        keywords=("경제", "금리", "물가", "환율", "수출", "산업", "시장", "소비", "기업", "증시", "주가"),
    ),
    TopicOption(
        id="startup",
        label="스타트업",
        keywords=("스타트업", "투자", "벤처", "창업", "시리즈", "유니콘"),
    ),
    TopicOption(
        id="stock",
        label="주식시장",
        keywords=("증시", "주식", "코스피", "코스닥", "나스닥", "상장", "실적", "엔비디아", "삼성전자"),
    ),
)


SOURCE_BY_ID = {source.id: source for source in SOURCES}
TOPIC_BY_ID = {topic.id: topic for topic in TOPICS}


def source_labels(source_ids: list[str]) -> list[str]:
    return [SOURCE_BY_ID[source_id].label for source_id in source_ids if source_id in SOURCE_BY_ID]


def topic_labels(topic_ids: list[str]) -> list[str]:
    return [TOPIC_BY_ID[topic_id].label for topic_id in topic_ids if topic_id in TOPIC_BY_ID]


def topic_keywords(topic_ids: list[str]) -> list[str]:
    keywords: list[str] = []
    for topic_id in topic_ids:
        topic = TOPIC_BY_ID.get(topic_id)
        if topic:
            keywords.extend(topic.keywords)
    return list(dict.fromkeys(keywords))
