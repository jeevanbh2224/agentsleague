"""
The Fractured Orbit — Hosted Agent HTTP API
Wraps the multi-agent game as a REST endpoint for Foundry Agent Service.

Endpoints:
  POST /sessions          — create a new game session
  POST /sessions/{id}/turn — send a player action, get scene back
  GET  /sessions/{id}     — get current session state
  GET  /health            — health check
"""
from __future__ import annotations

import os
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from config import Config
from tools.state_manager import StateManager
from tools.knowledge_base import KnowledgeBase
from agents.commander import CommanderAgent

app = FastAPI(
    title="The Fractured Orbit",
    description="Multi-agent space station murder mystery RPG | Microsoft Agents League Challenge B",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Shared services (initialised once at startup) ──────────────────────────────
_state_manager: StateManager | None = None
_knowledge_base: KnowledgeBase | None = None
_commander: CommanderAgent | None = None


@app.on_event("startup")
async def startup():
    global _state_manager, _knowledge_base, _commander
    _state_manager = StateManager()
    _knowledge_base = KnowledgeBase()
    _commander = CommanderAgent(_state_manager, _knowledge_base)


# ── Request / Response models ──────────────────────────────────────────────────

class NewSessionRequest(BaseModel):
    player_name: str = "Commander"


class NewSessionResponse(BaseModel):
    session_id: str
    player_name: str
    opening_scene: str
    choices: list[str]
    state: dict[str, Any]


class TurnRequest(BaseModel):
    action: str


class TurnResponse(BaseModel):
    session_id: str
    narration: str
    scene: str
    choices: list[str]
    status_update: str
    state: dict[str, Any]
    game_ended: bool
    ending: str | None


class SessionStateResponse(BaseModel):
    session_id: str
    player_name: str
    station_day: int
    oxygen_level: int
    reactor_status: str
    location: str
    evidence_count: int
    evidence: list[str]
    kai_stage: int
    aria_override_active: bool
    oxygen_repaired: bool
    missions: dict
    crew_trust: dict


# ── Helpers ────────────────────────────────────────────────────────────────────

def _parse_narration(raw: str) -> dict[str, str]:
    """Split narration into scene / status / choices sections."""
    import re
    pattern = r'---\s*(SCENE|STATUS|CHOICES)\s*---(.*?)(?=---\s*(?:SCENE|STATUS|CHOICES)\s*---|$)'
    matches = re.findall(pattern, raw, re.DOTALL)
    result = {"scene": raw.strip(), "status": "", "choices": ""}
    if matches:
        result["scene"] = ""
        for section, content in matches:
            result[section.lower()] = content.strip()
    return result


def _extract_choices(choices_text: str) -> list[str]:
    """Parse numbered choice list into a Python list."""
    import re
    lines = choices_text.strip().splitlines()
    choices = []
    for line in lines:
        line = line.strip()
        # Strip markdown bold and leading numbers
        line = re.sub(r'\*\*([^*]+)\*\*', r'\1', line)
        line = re.sub(r'^\d+\.\s*', '', line)
        if line:
            choices.append(line)
    return choices[:6]


def _safe_state(state: dict) -> dict:
    """Return a clean, JSON-serialisable subset of game state."""
    return {
        "session_id": state.get("id", ""),
        "player_name": state.get("player_name", "Commander"),
        "station_day": state.get("station_day", 2891),
        "oxygen_level": state.get("oxygen_level", 82),
        "reactor_status": state.get("reactor_status", "degraded"),
        "location": state.get("location", "Command Deck"),
        "evidence": state.get("evidence", []),
        "evidence_count": len(state.get("evidence", [])),
        "kai_stage": state.get("kai_stage", 1),
        "aria_override_active": state.get("aria_override_active", True),
        "oxygen_repaired": state.get("oxygen_repaired", False),
        "missions": state.get("missions", {}),
        "crew_trust": state.get("crew_trust", {}),
        "conditions": state.get("conditions", []),
        "kai_confronted": state.get("kai_confronted", False),
        "distress_signal_sent": state.get("distress_signal_sent", False),
    }


# ── Endpoints ──────────────────────────────────────────────────────────────────

@app.get("/health")
async def health():
    return {"status": "online", "game": "The Fractured Orbit", "station": "ISS Tartarus"}


@app.post("/sessions", response_model=NewSessionResponse)
async def create_session(req: NewSessionRequest):
    state = _state_manager.create_session(req.player_name)

    # Opening scene
    opening_input = "begin investigation — I need to understand what happened to Dr. Voss"
    narration, state = _commander.process_turn(opening_input, state)
    _state_manager.save_session(state)

    parsed = _parse_narration(narration)
    choices = _extract_choices(parsed["choices"])

    return NewSessionResponse(
        session_id=state["id"],
        player_name=state["player_name"],
        opening_scene=parsed["scene"],
        choices=choices,
        state=_safe_state(state),
    )


@app.post("/sessions/{session_id}/turn", response_model=TurnResponse)
async def take_turn(session_id: str, req: TurnRequest):
    state = _state_manager.load_session(session_id)
    if not state:
        raise HTTPException(status_code=404, detail="Session not found")

    action = req.action.strip()
    if not action:
        raise HTTPException(status_code=400, detail="Action cannot be empty")

    # Handle oxygen fix command
    if action.lower() in ("fix oxygen", "repair oxygen", "repair scrubber", "restore oxygen"):
        o2 = state.get("oxygen_level", 100)
        if o2 >= 60:
            narration = "---SCENE---\nO₂ levels are within acceptable range. No repair needed.\n---CHOICES---\n1. Continue investigating\n2. Check the security logs\n3. Speak to a crew member"
        elif state.get("oxygen_repaired"):
            narration = "---SCENE---\nThe O₂ recycler has already been bypassed. Emergency canisters are depleted.\n---CHOICES---\n1. Continue investigating\n2. Check the security logs\n3. Speak to a crew member"
        else:
            state["oxygen_level"] = 100
            state["oxygen_repaired"] = True
            _state_manager.save_session(state)
            narration = (
                "---SCENE---\n"
                "Zara Kim reroutes coolant through the emergency scrubber line.\n"
                "Oxygen restored to 100%. The crew breathes easier.\n"
                "The reactor fault remains but the immediate danger has passed.\n"
                "---STATUS---\nO₂ recycler bypassed. Oxygen stable at 100%.\n"
                "---CHOICES---\n"
                "1. Return to investigating Dr. Voss's death\n"
                "2. Ask Zara about the reactor fault\n"
                "3. Check the security access log\n"
                "4. Speak to Dr. Patel about post-mortem findings\n"
            )
        parsed = _parse_narration(narration)
        return TurnResponse(
            session_id=session_id,
            narration=narration,
            scene=parsed["scene"],
            choices=_extract_choices(parsed["choices"]),
            status_update=parsed["status"],
            state=_safe_state(state),
            game_ended=False,
            ending=None,
        )

    # Append confirm flag for irreversible actions
    if action.lower().endswith(" confirm"):
        action = action[:-8].strip() + " __confirmed"

    try:
        narration, state = _commander.process_turn(action, state)
        _state_manager.save_session(state)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Agent error: {str(exc)}")

    parsed = _parse_narration(narration)
    choices = _extract_choices(parsed["choices"])

    # Check game end
    ending = _check_game_end(state)

    # Inject fix oxygen option when O2 low and not yet repaired
    o2 = state.get("oxygen_level", 100)
    if o2 <= 60 and not state.get("oxygen_repaired") and "fix oxygen" not in " ".join(choices).lower():
        choices.append("fix oxygen — Zara bypasses the B-7 scrubber (+restore O₂)")

    return TurnResponse(
        session_id=session_id,
        narration=narration,
        scene=parsed["scene"],
        choices=choices,
        status_update=parsed["status"],
        state=_safe_state(state),
        game_ended=ending is not None,
        ending=ending,
    )


@app.get("/sessions/{session_id}", response_model=SessionStateResponse)
async def get_session(session_id: str):
    state = _state_manager.load_session(session_id)
    if not state:
        raise HTTPException(status_code=404, detail="Session not found")
    s = _safe_state(state)
    return SessionStateResponse(**{k: s[k] for k in SessionStateResponse.model_fields})


def _check_game_end(state: dict) -> str | None:
    days_left = 2909 - state.get("station_day", 2891)
    if days_left <= 0 and not state.get("kai_confronted") and not state.get("distress_signal_sent"):
        return "FAILURE"
    evidence_count = len(state.get("evidence", []))
    if state.get("kai_confronted") and evidence_count >= 4:
        return "TRUTH" if state.get("distress_signal_sent") else "SURVIVAL"
    if state.get("decisions") and any(
        "follow helioscore orders" in d.get("decision", "").lower()
        for d in state["decisions"]
    ):
        return "CORPORATE"
    return None


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8080"))
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
