# Game Rules: ISS Tartarus
tags: [rules, mechanics, dice, checks, combat, inventory, status]
related_entities: [Commander, crew, skill checks, dice]

---

## Core Principle
The Commander resolves uncertainty through skill checks. Every check has:
- A **difficulty class (DC)** — the minimum total needed to succeed
- A **relevant skill** — determines which modifier applies
- A **consequence** — success, partial success, or failure each produce meaningful outcomes (never dead ends)

---

## Dice System

All checks use a **d20** (twenty-sided die) plus a relevant skill modifier.

| Outcome | Total Roll |
|---|---|
| Critical Failure | 1–5 |
| Failure | 6–9 |
| Partial Success | 10–14 |
| Success | 15–19 |
| Critical Success | 20+ |

**Advantage**: Roll twice, take the higher result. Granted when the player has strong preparation, crew assistance, or relevant items.
**Disadvantage**: Roll twice, take the lower result. Applied under time pressure, injury, or poor preparation.

---

## Crew Skill Modifiers

| Skill | Commander Base | Relevant Agent Bonus |
|---|---|---|
| Engineering | +1 | +3 (Zara Kim) |
| Medicine / Insight | +1 | +3 (Dr. Patel) |
| Navigation / Comms | +1 | +3 (Lyra Chen) |
| Hacking / Systems | +0 | +2 (Zara Kim) |
| Persuasion / Deception | +2 | — |
| Stealth | +1 | — |
| Investigation | +2 | — |
| Athletics / EVA | +1 | — |
| Intimidation | +1 | — |

When a crew agent assists on a check, add their bonus to the roll. The Commander must request their help first (costs a turn action).

---

## Difficulty Classes Reference

| Task | DC |
|---|---|
| Routine station access | 8 |
| EVA debris navigation | 12 |
| Read Kai Reeves's stress level | 12 |
| Reactor coolant repair | 14 |
| Reroute atmospheric processors | 14 |
| Search Kai's quarters (with consent) | 14 |
| Decrypt cargo hold comms device | 16 |
| Hack ARIA subsystems | 16 |
| Search Kai's quarters (without consent) | 16 |
| Identify override code source | 16 |
| Final confrontation with Kai (1-2 evidence) | 20 |
| Final confrontation with Kai (3-4 evidence) | 18 |
| Final confrontation with Kai (5+ evidence) | 15 |
| Revoke ARIA corporate override | 12 (once code found) |
| Comms signal through magnetosphere | 15 |

---

## Turn Structure

Each player turn consists of:
1. **Action**: One primary action (investigate location, consult crew member, use item, make check)
2. **Reaction**: One optional reaction (ARIA query, status check, review evidence)
3. **Consequence**: Commander narrates result, updates game state

Time passes: Each full turn advances the game clock by 4 in-game hours.
Oxygen declines: -3% every 8 in-game hours (roughly every 2 turns) until repaired.

---

## Trust System

Each crew member has a trust level (0–100). Starting values:
- Zara Kim: 75
- Dr. Patel: 80
- Lyra Chen: 70
- ARIA: 25 (suppressed — starts low)
- Kai Reeves: 50 (facade — starts deceptively high)

**Increasing trust**: Sharing information, acting with integrity, completing missions that benefit the crew, protecting crew safety.
**Decreasing trust**: Withholding information, following HeliosCore orders blindly, failing checks that harm crew, being caught in deception.

Kai's trust meter works inversely: as the Commander gathers evidence, Kai's facade trust drops toward his real antagonist state.

---

## Inventory

The Commander carries a personal inventory of up to 6 items. Items can be shared with or received from crew members. Key items include:
- Station keycard (Level 2 — standard access)
- Commander's biometric chip (always equipped — grants Level 5 access)
- EVA suit (bulky — counts as 2 inventory slots when carried)
- Evidence items collected during investigation

---

## Health and Conditions

The Commander does not have traditional hit points — this is an investigation game, not combat. Instead, the Commander has a **Condition Track**:

| Condition | Effect |
|---|---|
| Healthy | No penalties |
| Stressed | -1 to all social checks |
| Exhausted | Disadvantage on physical checks |
| Oxygen Deprived | Disadvantage on all checks |
| Injured (EVA accident) | -2 to all checks until treated by Patel |

Patel can remove any condition with a Medical check DC 10.

---

## Irreversible Actions — Human-in-the-Loop Required

The following actions require explicit player confirmation before execution:
- Opening the Commander's Sealed Orders (cannot be resealed)
- Revoking ARIA's corporate override (permanent — ARIA's testimony becomes active)
- Sending the IOSA distress signal (HeliosCore will detect attempt)
- Confronting Kai formally (triggers Stage 3 — Kai becomes desperate)
- EVA into Section C (physical risk — suit integrity check required)
- Destroying Veilite samples (irreversible — affects ending)

The game will present a clear warning and ask for confirmation before each of these actions.

---

## Endings

| Ending | Condition | Description |
|---|---|---|
| TRUTH | Main quest complete + IOSA signal sent | Full justice — Kai arrested, Veilite exposed, crew safe |
| SURVIVAL | Main quest complete, no signal sent | Kai confined, crew safe, HeliosCore covers it up |
| CORPORATE | Followed HeliosCore orders | Cover-up succeeds, crew goes home, no justice |
| COMPROMISE | Veilite used as leverage | Deal made, crew safe, Voss's death legally "accidental" |
| FAILURE | Resolution team arrives first | HeliosCore takes control, Commander removed from command |
