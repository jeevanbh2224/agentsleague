import random
from dataclasses import dataclass
from enum import Enum


class Outcome(str, Enum):
    CRITICAL_FAILURE = "critical_failure"
    FAILURE = "failure"
    PARTIAL_SUCCESS = "partial_success"
    SUCCESS = "success"
    CRITICAL_SUCCESS = "critical_success"


@dataclass
class RollResult:
    actor: str
    skill: str
    raw_roll: int
    modifier: int
    total: int
    difficulty: int
    outcome: Outcome
    consequence: str
    advantage: bool = False
    disadvantage: bool = False

    def to_dict(self) -> dict:
        return {
            "actor": self.actor,
            "check": self.skill,
            "roll": self.raw_roll,
            "modifier": self.modifier,
            "total": self.total,
            "difficulty": self.difficulty,
            "result": self.outcome.value,
            "consequence": self.consequence,
        }


# Skill modifiers per agent — mirrors game_rules.md
AGENT_SKILL_MODIFIERS: dict[str, dict[str, int]] = {
    "commander": {
        "engineering": 1, "medicine": 1, "navigation": 1, "hacking": 0,
        "persuasion": 2, "deception": 2, "stealth": 1, "investigation": 2,
        "athletics": 1, "intimidation": 1, "insight": 1,
    },
    "engineer": {
        "engineering": 4, "hacking": 2, "athletics": 2,
        "investigation": 1, "stealth": 0,
    },
    "medic": {
        "medicine": 4, "insight": 3, "persuasion": 2, "investigation": 2,
    },
    "navigator": {
        "navigation": 4, "investigation": 3, "hacking": 1, "persuasion": 1,
    },
}


def _roll_d20() -> int:
    return random.randint(1, 20)


def _classify(total: int, dc: int) -> Outcome:
    if total <= 5:
        return Outcome.CRITICAL_FAILURE
    if total < dc - 5:
        return Outcome.FAILURE
    if total < dc:
        return Outcome.PARTIAL_SUCCESS
    if total < dc + 5:
        return Outcome.SUCCESS
    return Outcome.CRITICAL_SUCCESS


def skill_check(
    actor: str,
    skill: str,
    difficulty: int,
    consequence_map: dict[str, str],
    advantage: bool = False,
    disadvantage: bool = False,
) -> RollResult:
    """
    Roll a d20 skill check.

    consequence_map keys: "critical_failure", "failure", "partial_success",
                          "success", "critical_success"
    Missing keys fall back to the nearest lower tier.
    """
    modifiers = AGENT_SKILL_MODIFIERS.get(actor.lower(), {})
    modifier = modifiers.get(skill.lower(), 0)

    if advantage and not disadvantage:
        raw = max(_roll_d20(), _roll_d20())
    elif disadvantage and not advantage:
        raw = min(_roll_d20(), _roll_d20())
    else:
        raw = _roll_d20()

    total = raw + modifier
    outcome = _classify(total, difficulty)

    # Fallback chain for consequence
    fallback_order = [
        Outcome.CRITICAL_SUCCESS,
        Outcome.SUCCESS,
        Outcome.PARTIAL_SUCCESS,
        Outcome.FAILURE,
        Outcome.CRITICAL_FAILURE,
    ]
    consequence = ""
    idx = fallback_order.index(outcome)
    while idx < len(fallback_order):
        consequence = consequence_map.get(fallback_order[idx].value, "")
        if consequence:
            break
        idx += 1

    return RollResult(
        actor=actor,
        skill=skill,
        raw_roll=raw,
        modifier=modifier,
        total=total,
        difficulty=difficulty,
        outcome=outcome,
        consequence=consequence,
        advantage=advantage,
        disadvantage=disadvantage,
    )


def roll_dice(sides: int, count: int = 1) -> list[int]:
    """Roll `count` dice with `sides` faces."""
    return [random.randint(1, sides) for _ in range(count)]


def roll_encounter_table(table_size: int = 6) -> int:
    """Roll on an encounter/event table."""
    return random.randint(1, table_size)
