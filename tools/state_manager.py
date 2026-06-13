import uuid
import json
from datetime import datetime, timezone
from typing import Any

from config import Config


DEFAULT_STATE: dict[str, Any] = {
    "station_day": 2891,
    "in_game_hour": 6,
    "oxygen_level": 82,
    "reactor_status": "degraded",
    "location": "Command Deck",
    "player_name": "Commander",
    "missions": {
        "main_01": "active",
        "side_01": "active",
        "side_02": "not_started",
        "side_03": "locked",
        "climax_01": "locked",
    },
    "evidence": [],
    "crew_trust": {
        "zara_kim": 75,
        "dr_patel": 80,
        "lyra_chen": 70,
        "aria": 25,
        "kai_reeves": 50,
    },
    "kai_stage": 1,
    "inventory": ["station_keycard_level_2", "commander_biometric_chip"],
    "conditions": [],
    "decisions": [],
    "story_log": [],
    "aria_override_active": True,
    "sealed_orders_opened": False,
    "veilite_discovered": False,
    "distress_signal_sent": False,
    "kai_confronted": False,
    "oxygen_repaired": False,
}


class StateManager:
    """
    Manages persistent game state in Azure Cosmos DB.
    Falls back to in-memory state if Cosmos is unavailable.
    """

    def __init__(self) -> None:
        self._client = None
        self._container = None
        self._memory_store: dict[str, dict] = {}
        self._cosmos_available = False

        if Config.has_cosmos():
            self._init_cosmos()

    def _init_cosmos(self) -> None:
        try:
            from azure.cosmos import CosmosClient, PartitionKey, exceptions

            self._cosmos_exceptions = exceptions
            client = CosmosClient(Config.COSMOS_ENDPOINT, Config.COSMOS_KEY)
            db = client.create_database_if_not_exists(Config.COSMOS_DATABASE)
            self._container = db.create_container_if_not_exists(
                id=Config.COSMOS_CONTAINER,
                partition_key=PartitionKey(path="/id"),
            )
            self._cosmos_available = True
        except Exception:
            self._cosmos_available = False

    def create_session(self, player_name: str) -> dict:
        """Create a new game session and return the initial state."""
        session_id = str(uuid.uuid4())
        state = DEFAULT_STATE.copy()
        state = json.loads(json.dumps(state))  # deep copy via serialisation
        state["id"] = session_id
        state["player_name"] = player_name
        state["created_at"] = datetime.now(timezone.utc).isoformat()
        state["updated_at"] = datetime.now(timezone.utc).isoformat()

        self._save(session_id, state)
        return state

    def load_session(self, session_id: str) -> dict | None:
        """Load a session by ID. Returns None if not found."""
        if self._cosmos_available:
            try:
                item = self._container.read_item(session_id, partition_key=session_id)
                return dict(item)
            except Exception:
                pass
        return self._memory_store.get(session_id)

    def save_session(self, state: dict) -> None:
        """Persist the current state."""
        state["updated_at"] = datetime.now(timezone.utc).isoformat()
        self._save(state["id"], state)

    def _save(self, session_id: str, state: dict) -> None:
        self._memory_store[session_id] = state
        if self._cosmos_available:
            try:
                self._container.upsert_item(state)
            except Exception:
                pass

    def list_sessions(self) -> list[dict]:
        """Return a summary of all available sessions."""
        if self._cosmos_available:
            try:
                items = list(
                    self._container.query_items(
                        "SELECT c.id, c.player_name, c.station_day, c.updated_at FROM c",
                        enable_cross_partition_query=True,
                    )
                )
                return items
            except Exception:
                pass
        return [
            {
                "id": s["id"],
                "player_name": s.get("player_name", "Unknown"),
                "station_day": s.get("station_day", 0),
                "updated_at": s.get("updated_at", ""),
            }
            for s in self._memory_store.values()
        ]

    # ── State mutation helpers ──────────────────────────────────────────────

    def advance_time(self, state: dict, hours: int = 4) -> dict:
        state["in_game_hour"] = (state["in_game_hour"] + hours) % 24
        if state["in_game_hour"] < hours:
            state["station_day"] += 1
        # Oxygen decay — only when not yet repaired
        if state.get("oxygen_repaired", False):
            # Hard pin: once repaired, oxygen never drops
            state["oxygen_level"] = max(state["oxygen_level"], 100)
        else:
            if state["reactor_status"] == "degraded":
                state["oxygen_level"] = max(0, state["oxygen_level"] - 7)
            elif state["reactor_status"] == "critical":
                state["oxygen_level"] = max(0, state["oxygen_level"] - 10)
        return state

    def add_evidence(self, state: dict, evidence_id: str) -> dict:
        if evidence_id not in state["evidence"]:
            state["evidence"].append(evidence_id)
        return state

    def update_trust(self, state: dict, agent: str, delta: int) -> dict:
        if agent in state["crew_trust"]:
            state["crew_trust"][agent] = max(
                0, min(100, state["crew_trust"][agent] + delta)
            )
        self._update_kai_stage(state)
        return state

    def _update_kai_stage(self, state: dict) -> None:
        kai_trust = state["crew_trust"].get("kai_reeves", 50)
        if kai_trust > 20:
            state["kai_stage"] = 1
        elif kai_trust > 10:
            state["kai_stage"] = 2
        else:
            state["kai_stage"] = 3

    def log_event(self, state: dict, event: str) -> dict:
        state["story_log"].append(
            {
                "day": state["station_day"],
                "hour": state["in_game_hour"],
                "event": event,
            }
        )
        return state

    def log_decision(self, state: dict, decision: str) -> dict:
        state["decisions"].append(
            {
                "day": state["station_day"],
                "hour": state["in_game_hour"],
                "decision": decision,
            }
        )
        return state

    def add_inventory(self, state: dict, item: str) -> dict:
        if item not in state["inventory"] and len(state["inventory"]) < 6:
            state["inventory"].append(item)
        return state

    def remove_inventory(self, state: dict, item: str) -> dict:
        if item in state["inventory"]:
            state["inventory"].remove(item)
        return state

    def complete_mission(self, state: dict, mission_id: str) -> dict:
        if mission_id in state["missions"]:
            state["missions"][mission_id] = "completed"
        return state

    def unlock_mission(self, state: dict, mission_id: str) -> dict:
        if mission_id in state["missions"] and state["missions"][mission_id] == "locked":
            state["missions"][mission_id] = "active"
        return state
