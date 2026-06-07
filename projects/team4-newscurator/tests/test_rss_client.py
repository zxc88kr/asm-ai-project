import unittest
import xml.etree.ElementTree as ET

from backend.app.catalog import SOURCE_BY_ID
from backend.app.news_client import NewsClient


class RssClientTest(unittest.TestCase):
    def test_parse_rss_feed_items(self) -> None:
        client = NewsClient(api_key=None, use_rss=False)
        source = SOURCE_BY_ID["yonhap"]
        xml = """<?xml version="1.0" encoding="UTF-8"?>
        <rss version="2.0">
          <channel>
            <item>
              <title><![CDATA[AI 반도체 투자 확대]]></title>
              <link>https://example.com/a</link>
              <description><![CDATA[기업들이 AI 데이터센터 투자를 늘리고 있다.]]></description>
              <pubDate>Sun, 07 Jun 2026 09:00:00 +0900</pubDate>
            </item>
          </channel>
        </rss>
        """.encode("utf-8")
        root = ET.fromstring(xml)
        item = root.find(".//item")

        title = client._text(item, ("title",))
        link = client._rss_link(item)
        published_at = client._normalize_date(client._text(item, ("pubDate",)))

        self.assertEqual(source.label, "연합뉴스")
        self.assertEqual(title, "AI 반도체 투자 확대")
        self.assertEqual(link, "https://example.com/a")
        self.assertTrue(published_at.startswith("2026-06-07T00:00:00"))


if __name__ == "__main__":
    unittest.main()
