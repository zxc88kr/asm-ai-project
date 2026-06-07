import tempfile
import unittest
from pathlib import Path

from backend.app.config import get_settings
from backend.app.db import Repository
from backend.app.models import BriefingProfileInput, BriefingRequest
from backend.app.news_client import NewsClient
from backend.app.service import BriefingService, ValidationError
from backend.app.summarizer import Summarizer


def build_service(tmp_dir: Path) -> BriefingService:
    repository = Repository(tmp_dir / "test.db")
    repository.init()
    return BriefingService(
        news_client=NewsClient(api_key=None, use_rss=False),
        summarizer=Summarizer(
            api_key=None,
            model=get_settings().upstage_model,
            base_url=get_settings().upstage_base_url,
        ),
        repository=repository,
    )


class BriefingServiceTest(unittest.TestCase):
    def test_create_briefing_with_sample_data(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            service = build_service(Path(temp_dir))
            briefing = service.create_briefing(
                BriefingRequest(
                    sources=["yonhap", "mk", "hankyung"],
                    topics=["ai", "economy"],
                    date_range="7d",
                    limit=5,
                )
            )

        self.assertTrue(briefing.articles)
        self.assertTrue(briefing.used_sample_data)
        self.assertTrue(briefing.articles[0].summary)
        self.assertGreaterEqual(briefing.articles[0].priority_score, 0)
        self.assertTrue(briefing.articles[0].priority_label)

    def test_lists_and_loads_briefing_history(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            service = build_service(Path(temp_dir))
            created = service.create_briefing(
                BriefingRequest(
                    sources=["yonhap", "mk", "hankyung"],
                    topics=["ai", "economy"],
                    date_range="7d",
                    limit=5,
                )
            )
            history = service.list_history()
            loaded = service.get_briefing(history[0].id)

        self.assertEqual(len(history), 1)
        self.assertEqual(history[0].title, created.title)
        self.assertEqual(history[0].article_count, len(created.articles))
        self.assertEqual(history[0].custom_keywords, created.custom_keywords)
        self.assertIsNotNone(loaded)
        self.assertEqual(loaded.title, created.title)

    def test_requires_source_selection(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            service = build_service(Path(temp_dir))
            with self.assertRaises(ValidationError) as context:
                service.create_briefing(BriefingRequest(sources=[], topics=["ai"]))

        self.assertIn("언론사", str(context.exception))

    def test_custom_keywords_can_drive_briefing_without_topic(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            service = build_service(Path(temp_dir))
            briefing = service.create_briefing(
                BriefingRequest(
                    sources=["chosun"],
                    topics=[],
                    custom_keywords=["유통"],
                    date_range="7d",
                    limit=1,
                )
            )

        self.assertEqual(briefing.custom_keywords, ["유통"])
        self.assertIn("유통", briefing.title)
        self.assertEqual(len(briefing.articles), 1)
        self.assertIn("유통", briefing.articles[0].priority_reason or "")

    def test_exclude_keywords_remove_matching_articles(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            service = build_service(Path(temp_dir))
            briefing = service.create_briefing(
                BriefingRequest(
                    sources=["chosun"],
                    topics=[],
                    custom_keywords=["유통"],
                    exclude_keywords=["유통"],
                    date_range="7d",
                    limit=3,
                )
            )

        self.assertEqual(briefing.articles, [])
        self.assertEqual(briefing.exclude_keywords, ["유통"])
        self.assertEqual(briefing.stats.selected_count, 0)

    def test_saves_lists_and_deletes_profiles(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repository = Repository(Path(temp_dir) / "test.db")
            repository.init()
            created = repository.save_profile(
                BriefingProfileInput(
                    name="반도체 모니터링",
                    sources=["yonhap"],
                    topics=["ai"],
                    custom_keywords=["반도체"],
                    exclude_keywords=["스포츠"],
                    date_range="7d",
                    limit=5,
                )
            )
            profiles = repository.list_profiles()
            deleted = repository.delete_profile(created.id)

        self.assertEqual(len(profiles), 1)
        self.assertEqual(profiles[0].custom_keywords, ["반도체"])
        self.assertEqual(profiles[0].exclude_keywords, ["스포츠"])
        self.assertTrue(deleted)


if __name__ == "__main__":
    unittest.main()
