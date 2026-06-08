import unittest

from data.characters import CHARACTERS
from agents.graphs.character_chat import CharacterChatGraph
from agents.graphs.character_chat import AgentGenerationError
from agents.guard import filter_context_clues


class FakeAdapter:
    saved_messages = []
    characters = {
        1: {
            "id": 1,
            "name": "민재",
            "personality": "현실적이고 냉정함",
            "description": "백엔드 / MCP Tool 엔지니어",
            "system_prompt": "로그와 근거를 우선해서 말한다.",
        },
        2: {
            "id": 2,
            "name": "하린",
            "personality": "섬세하고 직관적임",
            "description": "프론트엔드 / UX 디자이너",
            "system_prompt": "분위기와 감정의 흐름을 중심으로 말한다.",
        },
        3: {
            "id": 3,
            "name": "도윤",
            "personality": "이상주의적이고 연구 지향적임",
            "description": "AI Agent Engineer",
            "system_prompt": "구조와 가능성을 중심으로 설명한다.",
        },
    }

    @staticmethod
    def get_character(character_id):
        return FakeAdapter.characters[character_id]

    @staticmethod
    def get_recent_messages(user_id, character_id, limit=6):
        return [{"sender": "me", "content": "뭐가 이상했어?"}]

    @staticmethod
    def get_accessible_clues(character_id):
        return [
            {
                "id": 1,
                "name": "실습실 자동 잠금 기록",
                "description": "자동 잠금 기록",
                "accessible_character_ids": [1],
            },
            {
                "id": 2,
                "name": "조명 제어 로그",
                "description": "조명 제어 기록",
                "accessible_character_ids": [1],
            },
            {
                "id": 3,
                "name": "삭제된 발표 슬라이드 기록",
                "description": "하린 계정 삭제 기록",
                "accessible_character_ids": [2],
            },
        ]

    @staticmethod
    def get_unlocked_clue_ids(user_id):
        return {1, 3}

    @classmethod
    def save_message(cls, user_id, character_id, sender, content):
        cls.saved_messages.append(
            {
                "user_id": user_id,
                "character_id": character_id,
                "sender": sender,
                "content": content,
            }
        )

    @staticmethod
    def generate_character_reply(prompt, character, user_message, context_clues):
        return "실습실 자동 잠금 기록은 타이밍이 이상해. 로그 기준으로 더 봐야 해."


class CharacterChatGraphTest(unittest.TestCase):
    def setUp(self):
        FakeAdapter.saved_messages = []

    def test_filter_context_clues_requires_access_and_unlock(self):
        clues = FakeAdapter.get_accessible_clues(1)

        filtered = filter_context_clues(1, clues, {1, 2, 3})

        self.assertEqual([clue["id"] for clue in filtered], [1, 2])

    def test_invoke_builds_prompt_generates_reply_and_saves_messages(self):
        graph = CharacterChatGraph(FakeAdapter)

        result = graph.invoke(
            {
                "user_id": "test-user",
                "character_id": 1,
                "user_message": "잠금 기록은 어떻게 봐?",
            }
        )

        self.assertEqual(
            result["content"],
            "실습실 자동 잠금 기록은 타이밍이 이상해. 로그 기준으로 더 봐야 해.",
        )
        self.assertIn("실습실 자동 잠금 기록", result["prompt"])
        self.assertNotIn("조명 제어 로그", result["prompt"])
        self.assertNotIn("삭제된 발표 슬라이드 기록", result["prompt"])
        self.assertEqual(result["used_clue_ids"], [1])
        self.assertEqual(len(FakeAdapter.saved_messages), 2)
        self.assertEqual(FakeAdapter.saved_messages[0]["sender"], "me")
        self.assertEqual(FakeAdapter.saved_messages[1]["sender"], "민재")

    def test_reply_generator_can_be_injected(self):
        graph = CharacterChatGraph(
            FakeAdapter,
            reply_generator=lambda prompt, character, user_message, context_clues: "주입 응답",
        )

        result = graph.invoke(
            {
                "user_id": "test-user",
                "character_id": 1,
                "user_message": "대답해줘",
            }
        )

        self.assertEqual(result["content"], "주입 응답")

    def test_prompt_applies_each_character_system_prompt(self):
        graph = CharacterChatGraph(FakeAdapter)

        for character_id, character in FakeAdapter.characters.items():
            result = graph.invoke(
                {
                    "user_id": "test-user",
                    "character_id": character_id,
                    "user_message": "너는 어떻게 봐?",
                }
            )

            self.assertIn(character["name"], result["prompt"])
            self.assertIn(character["system_prompt"], result["prompt"])

    def test_prompt_prevents_stiff_self_intro_response_style(self):
        graph = CharacterChatGraph(FakeAdapter)

        for character_id in FakeAdapter.characters:
            result = graph.invoke(
                {
                    "user_id": "test-user",
                    "character_id": character_id,
                    "user_message": "너는 누구고 뭘 봐야 해?",
                }
            )

            self.assertIn("자기소개로 시작하지 않는다", result["prompt"])
            self.assertIn("실제 대화처럼 자연스럽게 말한다", result["prompt"])
            self.assertIn("직책 소개", result["prompt"])

    def test_static_character_prompts_keep_conversational_tone(self):
        prompts = {character["name"]: character["system_prompt"] for character in CHARACTERS}

        self.assertIn("대화하듯 자연스럽게", prompts["민재"])
        self.assertIn("친구에게 털어놓듯 자연스럽게", prompts["하린"])
        self.assertIn("강의하듯 풀어내지 않는다", prompts["도윤"])

    def test_spoiler_guard_replaces_locked_clue_leak(self):
        graph = CharacterChatGraph(
            FakeAdapter,
            reply_generator=lambda prompt, character, user_message, context_clues: (
                "조명 제어 로그를 보면 답이 나와."
            ),
        )

        result = graph.invoke(
            {
                "user_id": "test-user",
                "character_id": 1,
                "user_message": "숨겨진 단서는?",
            }
        )

        self.assertEqual(result["content"], "지금 확인된 정보만으로는 그 부분을 단정할 수 없어.")
        self.assertIn(
            "spoiler_guard_replaced_response",
            [entry["step"] for entry in result["debug_trace"]],
        )

    def test_llm_failure_keeps_user_message(self):
        graph = CharacterChatGraph(
            FakeAdapter,
            reply_generator=lambda prompt, character, user_message, context_clues: (
                (_ for _ in ()).throw(RuntimeError("llm failed"))
            ),
        )

        with self.assertRaises(AgentGenerationError):
            graph.invoke(
                {
                    "user_id": "test-user",
                    "character_id": 1,
                    "user_message": "이 메시지는 저장돼야 해",
                }
            )

        self.assertEqual(len(FakeAdapter.saved_messages), 1)
        self.assertEqual(FakeAdapter.saved_messages[0]["sender"], "me")
        self.assertEqual(
            FakeAdapter.saved_messages[0]["content"],
            "이 메시지는 저장돼야 해",
        )


if __name__ == "__main__":
    unittest.main()
