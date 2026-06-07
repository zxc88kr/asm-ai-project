import tempfile
import unittest
from pathlib import Path

from backend.app.config import get_settings
from backend.app.db import Repository
from backend.app.demo_scenarios import DEMO_SCENARIOS
from backend.app.models import BriefingRequest
from backend.app.news_client import NewsClient
from backend.app.service import BriefingService
from backend.app.summarizer import Summarizer


def build_service(tmp_dir: Path) -> BriefingService:
    repository = Repository(tmp_dir / "test.db")
    repository.init()
    settings = get_settings()
    return BriefingService(
        news_client=NewsClient(api_key=None, use_rss=False),
        summarizer=Summarizer(
            api_key=None,
            model=settings.upstage_model,
            base_url=settings.upstage_base_url,
        ),
        repository=repository,
    )


class DemoScenarioTest(unittest.TestCase):
    def test_briefing_presets_generate_five_articles(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            service = build_service(Path(temp_dir))
            for scenario in DEMO_SCENARIOS:
                with self.subTest(scenario=scenario.id):
                    briefing = service.create_briefing(
                        BriefingRequest(
                            sources=scenario.sources,
                            topics=scenario.topics,
                            custom_keywords=scenario.custom_keywords,
                            date_range=scenario.date_range,
                            limit=scenario.limit,
                        )
                    )

                    self.assertEqual(len(briefing.articles), scenario.limit)
                    self.assertTrue(briefing.articles[0].summary)
                    self.assertTrue(briefing.articles[0].priority_label)


if __name__ == "__main__":
    unittest.main()
