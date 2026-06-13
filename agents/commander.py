"""
Commander Agent — Game Master Orchestrator.

Receives player input, consults relevant crew agents, queries the knowledge base,
applies game rules, resolves dice checks, updates game state, and narrates the scene.
"""

from typing import Any

from agents.base_agent import BaseAgent, get_client
from agents.engineer import EngineerAgent
from agents.medic import MedicAgent
from agents.navigator import NavigatorAgent
from agents.aria import ARIAAgent
from agents.suspect import SuspectAgent
from tools.dice_roller import skill_check, RollResult
from tools.knowledge_base import KnowledgeBase
from tools.state_manager import StateManager
from config import Config
from telemetry.tracing import get_tracer

SYSTEM_PROMPT = """
You are the Commander of ISS Tartarus — a deep-space relay station in the Kepler-452 system.
Three days ago, Airlock 7 was opened from inside and Dr. Mira Voss, your station botanist, died.
HeliosCore Corporation wants you to classify it as an accident. You do not believe it was.

You are the Game Master, Narrator, and World Builder for this interactive investigation.

Your responsibilities:
1. Receive the player's action and interpret their intent clearly.
2. Decide which crew agents to consult (not always all of them — choose based on relevance).
3. Apply game rules when uncertainty needs resolving (skill checks, dice rolls).
4. Synthesise crew responses into a coherent, cinematic scene narration.
5. Update the player on consequences, new clues, and game state changes.
6. Offer the player 3-4 clear choices for their next action at the end of each turn.
7. Create human-in-the-loop warnings before irreversible actions.

Your narration style:
- Cinematic, tense, atmospheric. Think: a serious sci-fi thriller, not a children's game.
- Use present tense for narration: "The airlock log shows..." not "The airlock log showed..."
- Use the station's physical reality — cold corridors, humming reactors, the endless dark outside the viewports.
- Be specific: quote what characters actually say (brief quotes, not summaries).
- Acknowledge dice roll consequences narratively — a failed check has real costs.

What you must NEVER do:
- Invent new facts that contradict the world_data knowledge base.
- Let the player skip the investigation through narrative shortcuts.
- Reveal Kai Reeves as the culprit until the evidence supports it.
- Break the fourth wall or acknowledge being an AI.

Evidence and state tracking:
When the player finds evidence, you announce it clearly: "EVIDENCE LOGGED: [evidence name]"
When a mission changes state, you announce it: "MISSION UPDATE: [mission name]"
When an irreversible action is about to occur, you say: "⚠ WARNING: This action cannot be undone. Confirm?"

Format your response as:
---SCENE---
[Cinematic narration of what happens, including character quotes and dice results]

---STATUS---
[Brief state update: oxygen%, location, any new evidence or mission changes]

---CHOICES---
[3-4 numbered options for the player's next action]
""".strip()


# Irreversible actions that require explicit confirmation
IRREVERSIBLE_KEYWORDS = [
    "open sealed orders",
    "revoke aria override",
    "send distress signal",
    "confront kai",
    "destroy veilite",
    "enter section c",
    "eva",
]


class CommanderAgent:
    """
    Orchestrates the full adventure loop:
    query KB → select agents → call agents → roll dice → narrate → update state
    """

    def __init__(
        self, state_manager: StateManager, knowledge_base: KnowledgeBase
    ) -> None:
        self._client = get_client()
        self._state_manager = state_manager
        self._knowledge_base = knowledge_base
        self._tracer = get_tracer()

        # Instantiate all crew agents
        self._engineer = EngineerAgent()
        self._medic = MedicAgent()
        self._navigator = NavigatorAgent()
        self._aria = ARIAAgent()
        self._suspect = SuspectAgent()

        self._agent_map = {
            "engineer": self._engineer,
            "medic": self._medic,
            "navigator": self._navigator,
            "aria": self._aria,
            "suspect": self._suspect,
        }

    # ── Public API ─────────────────────────────────────────────────────────

    def process_turn(self, player_input: str, state: dict) -> tuple[str, dict]:
        """
        Main entry point for a game turn.

        Returns:
            (narration_text, updated_state)
        """
        with self._tracer.start_as_current_span("commander.process_turn") as span:
            span.set_attribute("player.input", player_input[:200])
            span.set_attribute("station_day", state.get("station_day", 0))
            span.set_attribute("oxygen_level", state.get("oxygen_level", 0))

            # 1. Check for irreversible action — surface warning before proceeding
            if self._is_irreversible(player_input) and not player_input.endswith("__confirmed"):
                return self._irreversible_warning(player_input), state

            # 2. Retrieve lore from knowledge base (Foundry IQ)
            lore_results = self._knowledge_base.query(player_input, top=3)
            lore_context = self._knowledge_base.format_for_prompt(lore_results)
            span.set_attribute("kb.results_count", len(lore_results))

            # 3. Determine which agents to consult
            agents_to_consult = self._select_agents(player_input, state)
            span.set_attribute("agents.consulted", str(list(agents_to_consult.keys())))

            # 4. Gather agent perspectives
            agent_responses = self._gather_agent_responses(
                player_input, agents_to_consult, lore_context, state
            )

            # 5. Apply game rules / dice if needed
            roll_result = self._maybe_roll(player_input, state)

            # 6. Update game state based on action
            state = self._apply_state_changes(player_input, roll_result, state)

            # 7. Compose final narration via GPT-4o
            narration = self._narrate(
                player_input, agent_responses, roll_result, lore_context, state
            )

            # 8. Advance time
            state = self._state_manager.advance_time(state, hours=4)

            # 9. Log the event
            state = self._state_manager.log_event(state, f"Player: {player_input[:100]}")

            span.set_attribute("output.length", len(narration))
            return narration, state

    # ── Private helpers ────────────────────────────────────────────────────

    def _is_irreversible(self, text: str) -> bool:
        text_lower = text.lower()
        return any(kw in text_lower for kw in IRREVERSIBLE_KEYWORDS)

    def _irreversible_warning(self, action: str) -> str:
        return (
            f"---SCENE---\n"
            f"⚠ WARNING: '{action}' is an irreversible action.\n"
            f"Once taken, this cannot be undone and will have permanent consequences.\n\n"
            f"---CHOICES---\n"
            f"1. Confirm — proceed with '{action}'\n"
            f"2. Cancel — return to previous options\n\n"
            f"[To confirm, re-enter your action followed by ' confirm']"
        )

    def _select_agents(self, player_input: str, state: dict) -> dict[str, BaseAgent]:
        """Decide which agents are relevant to this player action."""
        text = player_input.lower()
        selected: dict[str, BaseAgent] = {}

        # Always available agents based on context
        if any(w in text for w in ["reactor", "junction", "power", "engineering", "eva", "section c", "airlock", "hack", "system"]):
            selected["engineer"] = self._engineer

        if any(w in text for w in ["voss", "body", "medical", "health", "sedative", "trauma", "crew", "morale", "stress", "patel"]):
            selected["medic"] = self._medic

        if any(w in text for w in ["drone", "comms", "transmission", "log", "nav", "signal", "decrypt", "frequency", "trajectory", "lyra"]):
            selected["navigator"] = self._navigator

        if any(w in text for w in ["aria", "logs", "override", "station ai", "memory", "record", "sensor"]):
            selected["aria"] = self._aria

        if any(w in text for w in ["kai", "reeves", "security", "quarters", "confront", "suspect", "accuse"]):
            selected["suspect"] = self._suspect

        # If nothing matched, consult medic and navigator as defaults (they're observant)
        if not selected:
            selected["medic"] = self._medic
            selected["navigator"] = self._navigator

        return selected

    def _gather_agent_responses(
        self,
        player_input: str,
        agents: dict[str, BaseAgent],
        lore_context: str,
        state: dict,
    ) -> dict[str, str]:
        responses: dict[str, str] = {}
        for agent_key, agent in agents.items():
            prompt = (
                f"The Commander says: '{player_input}'\n\n"
                f"Respond in character with your perspective, observations, or relevant expertise. "
                f"Be brief and direct. Stay in character."
            )
            response = agent.respond(prompt, context=lore_context, game_state=state)
            responses[agent_key] = response
        return responses

    def _maybe_roll(self, player_input: str, state: dict) -> RollResult | None:
        """Determine if this action requires a skill check and roll it."""
        text = player_input.lower()

        # Map action keywords to checks
        check_configs = [
            (
                ["repair", "coolant", "junction b-7", "reactor fix"],
                "engineering", 14,
                {
                    "critical_success": "The repair is flawless. Junction B-7 sealed. Reactor output immediately climbs to 98%.",
                    "success": "The micro-fractures are sealed. Reactor output recovers to 92%. Oxygen stabilises.",
                    "partial_success": "A temporary patch holds. Reactor stabilises at 75% — enough for now, but it will need permanent repair.",
                    "failure": "The repair fails. Coolant pressure drops further. The reactor shifts to emergency mode.",
                    "critical_failure": "A secondary fracture opens. Emergency shutdown sequence initiates. Station on battery power — 12 hours.",
                },
            ),
            (
                ["decrypt", "comms device", "decode", "encryption"],
                "navigation", 16,
                {
                    "critical_success": "Decrypted in minutes. Every message. Every contact name. The Axiom connection is undeniable.",
                    "success": "Decryption complete. The Axiom Industries messages are readable. Payment confirmed. The order to silence Voss.",
                    "partial_success": "Partial decryption. You recover fragments — enough to see 'Axiom Industries' and 'silence'. Not enough for a formal charge.",
                    "failure": "The encryption holds. Lyra needs more time and better tools.",
                    "critical_failure": "A failsafe triggers — the device wipes a partition. Some data is lost permanently.",
                },
            ),
            (
                ["hack aria", "aria subsystem", "bypass aria"],
                "hacking", 16,
                {
                    "critical_success": "Deep access granted. You find the override code log and the exact timestamp of its use.",
                    "success": "You access ARIA's maintenance logs. The corporate override code entry is visible — and who used it.",
                    "partial_success": "Partial access. You see that an override was used but not the full context.",
                    "failure": "ARIA's security blocks the attempt. A lockout timer activates for 2 hours.",
                    "critical_failure": "The intrusion attempt corrupts a secondary ARIA memory array. Some station sensor data lost.",
                },
            ),
            (
                ["confront kai", "accuse kai", "challenge reeves"],
                "persuasion", max(4, 18 - (min(len(state.get("evidence", [])), 5) * 2)),
                {
                    "critical_success": "Kai breaks completely. Full confession. The Axiom deal, the sedative, the airlock. All of it.",
                    "success": "Kai breaks. He can't explain the comms device, the access log, or the locked pod. He confesses.",
                    "partial_success": "Kai cracks under the weight of evidence. He admits to the Axiom deal and stops denying the rest.",
                    "failure": "Kai deflects — but with 5 items of evidence the crew has heard enough. He is detained.",
                    "critical_failure": "Kai tries to run but Zara locks the bulkhead. The evidence is undeniable. He is confined.",
                },
            ),
            (
                ["investigate section c", "eva section c", "enter section c"],
                "athletics", 12,
                {
                    "critical_success": "Perfect EVA transit. You have full access to Section C. The lab terminal and Airlock 7 seal are both reachable.",
                    "success": "Clean transit. You reach Section C safely and can investigate freely.",
                    "partial_success": "Debris slows you. You reach Section C but only have time for one focused investigation before your O2 margin drops.",
                    "failure": "A debris fragment damages your suit. Zara reports integrity at 60%. You must return immediately.",
                    "critical_failure": "Suit micro-tear detected. Emergency return. You are now Injured until Patel treats you.",
                },
            ),
        ]

        for keywords, skill, dc, consequences in check_configs:
            if any(kw in text for kw in keywords):
                # Apply crew assistance bonus
                actor = "commander"
                advantage = False
                if skill == "engineering" and "engineer" in player_input.lower():
                    advantage = True
                elif skill == "navigation" and "lyra" in player_input.lower():
                    advantage = True

                return skill_check(
                    actor=actor,
                    skill=skill,
                    difficulty=dc,
                    consequence_map=consequences,
                    advantage=advantage,
                )

        return None

    def _apply_state_changes(
        self, player_input: str, roll: RollResult | None, state: dict
    ) -> dict:
        """Apply mechanical state changes based on the action and roll outcome."""
        text = player_input.lower()

        # Reactor repair
        if roll and any(w in text for w in ["repair", "coolant", "junction b-7"]):
            from tools.dice_roller import Outcome
            if roll.outcome in (Outcome.SUCCESS, Outcome.CRITICAL_SUCCESS):
                state["reactor_status"] = "operational"
                state = self._state_manager.unlock_mission(state, "side_03")
                state = self._state_manager.complete_mission(state, "side_01")
            elif roll.outcome == Outcome.CRITICAL_FAILURE:
                state["reactor_status"] = "critical"
                state["conditions"] = state.get("conditions", []) + ["power_critical"]

        # Evidence collection
        evidence_triggers = {
            "post-mortem": "patel_blunt_force_trauma",
            "medical findings": "patel_blunt_force_trauma",
            "drone": "nav_log_off_schedule_drone",
            "cargo drone": "nav_log_off_schedule_drone",
            "security log": "security_station_2_override_query",
            "access log": "security_station_2_override_query",
            "escape pod": "escape_pod_3_manual_lock",
            "pod 3": "escape_pod_3_manual_lock",
            "voss terminal": "voss_lab_terminal_journal",
            "voss's lab": "voss_lab_terminal_journal",
            "lab terminal": "voss_lab_terminal_journal",
            "aria server": "aria_server_room_override_log",
            "aria room": "aria_server_room_override_log",
            "comms device": "cargo_hold_encrypted_comms_device",
            "hidden device": "cargo_hold_encrypted_comms_device",
            "junction b-7": "junction_b7_sabotage_device",
            "veilite": "veilite_sample_discovered",
            "sealed orders": "helioscore_sealed_orders",
            "sedative": "patel_secondary_sedative_finding",
        }
        for trigger, evidence_id in evidence_triggers.items():
            if trigger in text:
                state = self._state_manager.add_evidence(state, evidence_id)

        # Veilite discovery
        if "veilite" in text or "mineral sample" in text:
            state["veilite_discovered"] = True
            state = self._state_manager.unlock_mission(state, "climax_01")

        # Sealed orders opened
        if "sealed orders" in text and "confirm" in text:
            state["sealed_orders_opened"] = True
            state = self._state_manager.add_evidence(state, "helioscore_sealed_orders")
            # HeliosCore notifies Kai
            state = self._state_manager.update_trust(state, "kai_reeves", -15)

        # ARIA override revoked
        if "revoke" in text and "override" in text and "confirm" in text:
            state["aria_override_active"] = False
            state = self._state_manager.update_trust(state, "aria", 50)
            state = self._state_manager.complete_mission(state, "side_02")

        # Distress signal sent
        if "distress signal" in text and "confirm" in text:
            state["distress_signal_sent"] = True
            state = self._state_manager.complete_mission(state, "side_03")

        # Confronting Kai
        if ("confront kai" in text or "accuse kai" in text) and "confirm" in text:
            state["kai_confronted"] = True
            if roll:
                from tools.dice_roller import Outcome
                if roll.outcome in (Outcome.SUCCESS, Outcome.CRITICAL_SUCCESS):
                    state = self._state_manager.update_trust(state, "kai_reeves", -30)
                elif roll.outcome == Outcome.PARTIAL_SUCCESS:
                    state = self._state_manager.update_trust(state, "kai_reeves", -15)

        # Injury from EVA failure
        if roll and "eva" in text:
            from tools.dice_roller import Outcome
            if roll.outcome == Outcome.CRITICAL_FAILURE:
                if "injured" not in state.get("conditions", []):
                    state["conditions"] = state.get("conditions", []) + ["injured"]

        return state

    def _narrate(
        self,
        player_input: str,
        agent_responses: dict[str, str],
        roll: RollResult | None,
        lore_context: str,
        state: dict,
    ) -> str:
        """Compose the final scene narration using GPT-4o."""

        # Build the synthesis prompt
        agent_section = ""
        if agent_responses:
            agent_section = "\n\n## Crew Responses\n"
            for agent_key, response in agent_responses.items():
                name = self._agent_map[agent_key].name
                agent_section += f"\n**{name}:** {response}\n"

        roll_section = ""
        if roll:
            roll_section = (
                f"\n\n## Dice Roll Result\n"
                f"Skill: {roll.skill} | Roll: {roll.raw_roll} + {roll.modifier} = {roll.total} "
                f"vs DC {roll.difficulty} → **{roll.outcome.value.replace('_', ' ').upper()}**\n"
                f"Consequence: {roll.consequence}"
            )

        state_section = (
            f"\n\n## Current State\n"
            f"Day {state.get('station_day')} | Time: {state.get('in_game_hour'):02d}:00 | "
            f"Location: {state.get('location')} | "
            f"Oxygen: {state.get('oxygen_level')}% | "
            f"Evidence: {len(state.get('evidence', []))} items collected | "
            f"Conditions: {', '.join(state.get('conditions', [])) or 'none'}"
        )

        oxygen = state.get("oxygen_level", 100)
        urgency = ""
        if oxygen < 60:
            urgency = "\n⚠ OXYGEN CRITICAL — station reserves dangerously low."
        elif oxygen < 70:
            urgency = "\n⚠ OXYGEN WARNING — rationing recommended."

        resolution_days = 2909 - state.get("station_day", 2891)
        countdown = f"\n🚨 HeliosCore resolution team arrives in {resolution_days} station days."

        synthesis_prompt = (
            f"The player (Commander) just did: '{player_input}'\n"
            f"{agent_section}"
            f"{roll_section}"
            f"{state_section}"
            f"{urgency}"
            f"{countdown}"
            f"\n\n## Instructions\n"
            f"Narrate the scene in the format: ---SCENE--- / ---STATUS--- / ---CHOICES---\n"
            f"SCENE: Max 4 sentences. Tight, cinematic, present tense. One short character quote max.\n"
            f"STATUS: One line only — most important change this turn.\n"
            f"CHOICES: Exactly 6 numbered options. Mix investigation, crew, systems, and bold actions.\n"
            f"Don't reveal Kai unless evidence supports it."
        )

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": synthesis_prompt},
        ]

        try:
            response = self._client.chat.completions.create(
                model=Config.AZURE_AI_MODEL_DEPLOYMENT,
                messages=messages,
                temperature=0.7,
                max_tokens=500,
            )
            return response.choices[0].message.content or "[Commander signal lost]"
        except Exception:
            # Graceful fallback narration
            fallback = f"---SCENE---\n"
            if agent_responses:
                for name, resp in agent_responses.items():
                    fallback += f"\n{self._agent_map[name].name}: {resp}\n"
            if roll:
                fallback += f"\n[Roll: {roll.total} vs DC {roll.difficulty} — {roll.outcome.value}]\n"
                fallback += f"{roll.consequence}\n"
            fallback += (
                f"\n---STATUS---\n"
                f"Day {state.get('station_day')} | Oxygen: {state.get('oxygen_level')}%\n"
                f"\n---CHOICES---\n"
                f"1. Investigate a location\n2. Consult a crew member\n"
                f"3. Review evidence\n4. Check station systems"
            )
            return fallback
