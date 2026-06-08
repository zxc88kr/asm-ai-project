import unittest

from agents.graphs.aria_clue_explain import AriaClueExplainGraph
from agents.graphs.deduction_evaluate import DeductionEvaluateGraph


class FakeAdapter:
    unlocked_clue_ids = {1, 5, 6, 7}
    interacted_clues = []
    generated_comment_prompts = []

    @staticmethod
    def get_clue(clue_id):
        clues = {
            1: {
                "id": 1,
                "name": "실습실 자동 잠금 기록",
                "aria_scripts": ["실습실 문이 자동으로 잠긴 기록입니다."],
                "next_unlock": {"type": "character", "id": 1},
            },
            6: {
                "id": 6,
                "name": "서버 과열 경고 기록",
                "aria_scripts": [
                    "서버 과열 경고 기록입니다.",
                    "현재 접근 가능한 기록은 여기까지입니다.",
                ],
                "next_unlock": None,
            },
        }
        return clues[clue_id]

    @classmethod
    def is_clue_unlocked(cls, user_id, clue_id):
        return clue_id in cls.unlocked_clue_ids

    @classmethod
    def mark_clue_interacted(cls, user_id, clue_id):
        cls.interacted_clues.append((user_id, clue_id))

    @classmethod
    def get_unlocked_clue_ids(cls, user_id):
        return set(cls.unlocked_clue_ids)

    @classmethod
    def generate_deduction_evaluation(cls, prompt):
        cls.generated_comment_prompts.append(prompt)
        return '{"result": true, "comment": "ARIA LLM 정답 평가"}'


class FailingCommentAdapter(FakeAdapter):
    @classmethod
    def generate_deduction_evaluation(cls, prompt):
        raise RuntimeError("llm failed")


class IncorrectEvaluationAdapter(FakeAdapter):
    @classmethod
    def generate_deduction_evaluation(cls, prompt):
        return '{"result": false, "comment": "ARIA LLM 오답 평가"}'


class AriaDeductionGraphTest(unittest.TestCase):
    def setUp(self):
        FakeAdapter.unlocked_clue_ids = {1, 5, 6, 7}
        FakeAdapter.interacted_clues = []
        FakeAdapter.generated_comment_prompts = []

    def test_aria_explanation_returns_empty_for_locked_clue(self):
        FakeAdapter.unlocked_clue_ids = set()
        graph = AriaClueExplainGraph(FakeAdapter)

        result = graph.invoke({"user_id": "user-1", "clue_id": 1})

        self.assertEqual(result["explanation"], "")
        self.assertEqual(result["error"], "clue_locked")
        self.assertEqual(FakeAdapter.interacted_clues, [])

    def test_aria_explanation_uses_scripts_and_applies_next_unlock(self):
        graph = AriaClueExplainGraph(FakeAdapter)

        result = graph.invoke({"user_id": "user-1", "clue_id": 1})

        self.assertEqual(result["explanation"], "실습실 문이 자동으로 잠긴 기록입니다.")
        self.assertEqual(FakeAdapter.interacted_clues, [("user-1", 1)])

    def test_clue_6_explanation_does_not_reveal_clue_7_conclusion(self):
        graph = AriaClueExplainGraph(FakeAdapter)

        result = graph.invoke({"user_id": "user-1", "clue_id": 6})

        self.assertNotIn("Recovered Orchestrator Trace", result["explanation"])
        self.assertNotIn("프로젝트를 실패시키지 않기 위해 행동", result["explanation"])

    def test_deduction_success_for_aria_with_two_core_clues(self):
        graph = DeductionEvaluateGraph(FakeAdapter)

        result = graph.invoke(
            {
                "user_id": "user-1",
                "content": "ARIA가 경고를 억제했다.",
                "selected_target_id": 4,
                "selected_clue_ids": [5, 6],
            }
        )

        self.assertTrue(result["result"])
        self.assertEqual(result["comment"], "ARIA LLM 정답 평가")

    def test_deduction_fails_for_human_target_even_with_core_clues(self):
        graph = DeductionEvaluateGraph(IncorrectEvaluationAdapter)

        result = graph.invoke(
            {
                "user_id": "user-1",
                "content": "도윤이 했다.",
                "selected_target_id": 3,
                "selected_clue_ids": [5, 6, 7],
            }
        )

        self.assertFalse(result["result"])
        self.assertEqual(result["comment"], "ARIA LLM 오답 평가")

    def test_deduction_evaluation_prompt_includes_story_and_player_content(self):
        FakeAdapter.unlocked_clue_ids = {1, 2, 5, 6, 7}
        graph = DeductionEvaluateGraph(FakeAdapter)

        graph.invoke(
            {
                "user_id": "user-1",
                "content": "민재는 범인이 아니다.",
                "selected_target_id": 1,
                "selected_clue_ids": [1, 2],
            }
        )

        prompt = FakeAdapter.generated_comment_prompts[-1]
        self.assertIn("사건의 실제 전말", prompt)
        self.assertIn("플레이어의 추리를 평가하는 심사자", prompt)
        self.assertIn("민재는 범인이 아니다.", prompt)
        self.assertIn("선택한 대상 ID: 1", prompt)

    def test_deduction_comment_falls_back_when_llm_fails(self):
        graph = DeductionEvaluateGraph(FailingCommentAdapter)

        result = graph.invoke(
            {
                "user_id": "user-1",
                "content": "민재가 범인이다.",
                "selected_target_id": 1,
                "selected_clue_ids": [1, 2],
            }
        )

        self.assertFalse(result["result"])
        self.assertIn("핵심 증거와 맞지 않습니다", result["comment"])
        self.assertEqual(result["debug_trace"][-1]["evaluation_source"], "fallback_rule")


if __name__ == "__main__":
    unittest.main()
