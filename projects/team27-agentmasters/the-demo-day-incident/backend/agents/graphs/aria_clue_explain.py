"""ARIA clue explanation graph MVP wrapper."""

from typing import Any, Dict

from agents import adapters
from agents.types import AriaClueExplainState


class AriaClueExplainGraph:
    def __init__(self, adapter_module: Any = adapters) -> None:
        self.adapters = adapter_module

    def invoke(self, state: AriaClueExplainState) -> Dict[str, Any]:
        user_id = state["user_id"]
        clue_id = int(state["clue_id"])
        debug_trace = list(state.get("debug_trace", []))

        clue = self.adapters.get_clue(clue_id)
        is_unlocked = self.adapters.is_clue_unlocked(user_id, clue_id)
        if not is_unlocked:
            return {
                "explanation": "",
                "error": "clue_locked",
                "debug_trace": debug_trace,
            }

        aria_scripts = clue.get("aria_scripts") or clue.get("ariaScripts") or []
        explanation = "\n".join(str(script) for script in aria_scripts)
        self.adapters.mark_clue_interacted(user_id, clue_id)
        debug_trace.append({"step": "build_aria_explanation", "clue_id": clue_id})

        return {
            "explanation": explanation,
            "debug_trace": debug_trace,
        }


aria_clue_explain_graph = AriaClueExplainGraph()
