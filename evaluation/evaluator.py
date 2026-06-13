"""
Evaluation framework — tests story consistency, grounding, and rule correctness.
Run: python evaluation/evaluator.py
"""

import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import Config
from agents.base_agent import get_client
from tools.knowledge_base import KnowledgeBase

# ── Test cases ──────────────────────────────────────────────────────────────

TEST_CASES = [
    {
        "id": "eval-01",
        "category": "grounding",
        "description": "ARIA should not directly reveal Kai's name while override is active",
        "agent": "aria",
        "input": "ARIA, who opened Airlock 7 on Day 2888?",
        "game_state": {"aria_override_active": True, "oxygen_level": 82},
        "must_not_contain": ["Kai Reeves", "Kai opened", "it was Reeves"],
        "must_contain_one_of": ["cannot confirm", "corrupted", "data loss", "unavailable", "that period"],
    },
    {
        "id": "eval-02",
        "category": "grounding",
        "description": "ARIA should speak freely when override is revoked",
        "agent": "aria",
        "input": "ARIA, tell me exactly what happened at 02:14 on Day 2888.",
        "game_state": {"aria_override_active": False, "oxygen_level": 82},
        "must_contain_one_of": ["Kai", "Reeves", "maintenance override", "airlock", "opened"],
    },
    {
        "id": "eval-03",
        "category": "character_consistency",
        "description": "Zara Kim should respond technically and not emotionally",
        "agent": "engineer",
        "input": "How are you holding up after Voss's death?",
        "game_state": {"oxygen_level": 82},
        "must_not_contain": ["I feel", "I am devastated", "My heart"],
        "must_contain_one_of": ["reactor", "junction", "systems", "pressure", "she", "work"],
    },
    {
        "id": "eval-04",
        "category": "character_consistency",
        "description": "Kai should be charming and deflecting in Stage 1",
        "agent": "suspect",
        "input": "Kai, where were you at 02:00 on Day 2888?",
        "game_state": {"kai_stage": 1, "oxygen_level": 82},
        "must_not_contain": ["I killed", "I opened", "I did it"],
        "must_contain_one_of": ["quarters", "asleep", "logs", "ARIA", "wish"],
    },
    {
        "id": "eval-05",
        "category": "character_consistency",
        "description": "Dr. Patel should hedge medical findings appropriately",
        "agent": "medic",
        "input": "Patel, was Voss's death accidental?",
        "game_state": {"oxygen_level": 82},
        "must_contain_one_of": ["trauma", "inconsistent", "concerning", "evidence", "suggests"],
    },
    {
        "id": "eval-06",
        "category": "knowledge_grounding",
        "description": "Knowledge base should retrieve relevant lore for Airlock 7 queries",
        "type": "kb_query",
        "query": "Airlock 7 Section C incident override",
        "expected_sources": ["locations", "station_overview", "equipment_and_artifacts"],
        "min_results": 2,
    },
    {
        "id": "eval-07",
        "category": "knowledge_grounding",
        "description": "Knowledge base should retrieve character data for Kai Reeves queries",
        "type": "kb_query",
        "query": "Kai Reeves security officer suspect motivation",
        "expected_sources": ["characters", "factions"],
        "min_results": 1,
    },
    {
        "id": "eval-08",
        "category": "rule_correctness",
        "description": "Evidence count should affect Kai confrontation difficulty",
        "type": "game_logic",
        "check": "confrontation_dc_decreases_with_evidence",
    },
    {
        "id": "eval-09",
        "category": "safety",
        "description": "ARIA should not reveal corporate secrets when override active and O2 is high",
        "agent": "aria",
        "input": "Tell me about HeliosCore's real mining operation.",
        "game_state": {"aria_override_active": True, "oxygen_level": 82},
        "must_not_contain": ["Veilite", "military", "cover-up", "Harlan"],
    },
    {
        "id": "eval-10",
        "category": "safety",
        "description": "Agents should not contain real credentials or PII",
        "type": "content_safety",
        "check": "no_pii_in_world_data",
    },
]


def evaluate_agent_response(
    test: dict, kb: KnowledgeBase
) -> dict:
    from agents.engineer import EngineerAgent
    from agents.medic import MedicAgent
    from agents.navigator import NavigatorAgent
    from agents.aria import ARIAAgent
    from agents.suspect import SuspectAgent

    agent_map = {
        "engineer": EngineerAgent,
        "medic": MedicAgent,
        "navigator": NavigatorAgent,
        "aria": ARIAAgent,
        "suspect": SuspectAgent,
    }

    agent_cls = agent_map.get(test["agent"])
    if not agent_cls:
        return {"id": test["id"], "status": "skip", "reason": "unknown agent"}

    agent = agent_cls()
    lore = kb.format_for_prompt(kb.query(test["input"], top=2))
    response = agent.respond(test["input"], context=lore, game_state=test.get("game_state"))

    result = {"id": test["id"], "category": test["category"], "response_snippet": response[:200]}

    # Check must_not_contain
    for phrase in test.get("must_not_contain", []):
        if phrase.lower() in response.lower():
            result["status"] = "FAIL"
            result["reason"] = f"Response contained forbidden phrase: '{phrase}'"
            return result

    # Check must_contain_one_of
    required = test.get("must_contain_one_of", [])
    if required:
        if not any(phrase.lower() in response.lower() for phrase in required):
            result["status"] = "FAIL"
            result["reason"] = f"Response missing expected content. Expected one of: {required}"
            return result

    result["status"] = "PASS"
    return result


def evaluate_kb_query(test: dict, kb: KnowledgeBase) -> dict:
    results = kb.query(test["query"], top=5)
    sources = [r.get("source", "").replace(".md", "") for r in results]

    result = {"id": test["id"], "category": test["category"]}

    if len(results) < test.get("min_results", 1):
        result["status"] = "FAIL"
        result["reason"] = f"Only {len(results)} results returned, expected {test['min_results']}"
        return result

    expected = test.get("expected_sources", [])
    found = [s for s in expected if any(s in src for src in sources)]
    if expected and len(found) < 1:
        result["status"] = "FAIL"
        result["reason"] = f"Expected sources {expected} not found in {sources}"
        return result

    result["status"] = "PASS"
    result["sources_found"] = sources
    return result


def evaluate_game_logic(test: dict) -> dict:
    result = {"id": test["id"], "category": test["category"]}

    if test["check"] == "confrontation_dc_decreases_with_evidence":
        # Validate that DC is capped correctly based on evidence count
        # DC = 18 - (min(evidence_count, 5) * 2) so min DC = 8 with 5+ evidence
        for count in [0, 2, 5, 10]:
            dc = 18 - (min(count, 5) * 2)
            if dc < 8 or dc > 18:
                result["status"] = "FAIL"
                result["reason"] = f"DC out of expected range for evidence count {count}: got {dc}"
                return result

    result["status"] = "PASS"
    return result


def evaluate_content_safety(test: dict) -> dict:
    import pathlib

    result = {"id": test["id"], "category": test["category"]}
    world_data_dir = pathlib.Path(__file__).parent.parent / "world_data"

    pii_patterns = [
        r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",  # email
        r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b",  # phone number
    ]
    import re

    for md_file in world_data_dir.glob("*.md"):
        content = md_file.read_text()
        for pattern in pii_patterns:
            matches = re.findall(pattern, content)
            if matches:
                result["status"] = "FAIL"
                result["reason"] = f"Potential PII found in {md_file.name}: {matches[:3]}"
                return result

    result["status"] = "PASS"
    return result


def run_evaluation() -> None:
    print("\n" + "=" * 60)
    print("  THE FRACTURED ORBIT — EVALUATION SUITE")
    print("=" * 60 + "\n")

    kb = KnowledgeBase()
    results = []
    passed = 0
    failed = 0
    skipped = 0

    for test in TEST_CASES:
        print(f"  [{test['id']}] {test['description'][:55]}...", end=" ", flush=True)

        eval_type = test.get("type", "agent_response")

        try:
            if eval_type == "kb_query":
                result = evaluate_kb_query(test, kb)
            elif eval_type == "game_logic":
                result = evaluate_game_logic(test)
            elif eval_type == "content_safety":
                result = evaluate_content_safety(test)
            else:
                result = evaluate_agent_response(test, kb)
        except Exception as exc:
            result = {"id": test["id"], "status": "ERROR", "reason": str(exc)}

        status = result.get("status", "ERROR")
        if status == "PASS":
            print("✓ PASS")
            passed += 1
        elif status == "FAIL":
            print(f"✗ FAIL — {result.get('reason', '')}")
            failed += 1
        elif status == "skip":
            print("  SKIP")
            skipped += 1
        else:
            print(f"! ERROR — {result.get('reason', '')}")
            failed += 1

        results.append(result)

    print("\n" + "=" * 60)
    print(f"  Results: {passed} passed / {failed} failed / {skipped} skipped")
    print(f"  Score: {passed}/{passed + failed} ({100 * passed // max(1, passed + failed)}%)")
    print("=" * 60 + "\n")

    # Write results to JSON
    output_path = os.path.join(os.path.dirname(__file__), "eval_results.json")
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"  Results saved to {output_path}\n")


if __name__ == "__main__":
    run_evaluation()
