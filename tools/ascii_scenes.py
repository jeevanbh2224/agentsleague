"""
The Fractured Orbit — Terminal ASCII Scene Art
Small illustrated scenes showing characters inside the ship.
"""
from __future__ import annotations

from rich.console import Console
from rich.panel import Panel
from rich.text import Text

console = Console()

SCENES: dict[str, list[tuple[str, str]]] = {

    "command_deck": [
        ("   .  *    .       *    .   *    .  *  .   ", "dim white"),
        ("  ┌─────────────────────────────────────┐  ", "cyan"),
        ("  │  [:::SCREEN:::] ⚠ [:::SCREEN:::]   │  ", "bold red"),
        ("  │                                     │  ", "cyan"),
        ("  │      o        o                     │  ", "white"),
        ("  │     /|\\      /|\\      _____         │  ", "white"),
        ("  │     / \\      / \\     |     |        │  ", "cyan"),
        ("  │   LYRA      ZARA    | MAP |        │  ", "dim cyan"),
        ("  │                    |_____|        │  ", "dim cyan"),
        ("  └──────────── ⚡ ALERT ⚡ ───────────┘  ", "bold red"),
    ],

    "airlock_7": [
        ("  ┌─────────────────────────────────────┐  ", "dim"),
        ("  │  ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  │  ", "dim"),
        ("  │  ░   ╔══[ AIRLOCK 7 ]══╗           │  ", "cyan"),
        ("  │  ░   ║                 ║           │  ", "cyan"),
        ("  │  ░   ║   _   VOID  _   ║           │  ", "dim white"),
        ("  │  ░   ║  | |       | |  ║  o        │  ", "white"),
        ("  │  ░   ║  |_| ~~~~~ |_|  ║ /|\\       │  ", "white"),
        ("  │  ░   ║   *  SPACE  *   ║  |  YOU   │  ", "dim cyan"),
        ("  │  ░   ╚═[ BREACH LOG ]══╝ / \\       │  ", "bold yellow"),
        ("  │  ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  │  ", "dim"),
        ("  └─────────────────────────────────────┘  ", "dim"),
    ],

    "medical_bay": [
        ("  ┌──────────────────────────────────────┐  ", "white"),
        ("  │  ✚  MEDICAL BAY  ✚                   │  ", "bold white"),
        ("  │                                      │  ", "white"),
        ("  │    ___________                 o     │  ", "white"),
        ("  │   |           |               /|\\    │  ", "white"),
        ("  │   |  DR.VOSS  |               |      │  ", "dim red"),
        ("  │   |  ███████  |              / \\     │  ", "dim white"),
        ("  │   |___________|           DR. PATEL  │  ", "dim cyan"),
        ("  │         |                            │  ", "dim"),
        ("  │    [POST-MORTEM IN PROGRESS...]      │  ", "bold yellow"),
        ("  └──────────────────────────────────────┘  ", "white"),
    ],

    "engineering_bay": [
        ("  ╔══════════════════════════════════════╗  ", "yellow"),
        ("  ║  ⚙  ENGINEERING BAY  ⚙              ║  ", "bold yellow"),
        ("  ║                                      ║  ", "yellow"),
        ("  ║   ┌──────┐  SPARKS→  *  ✦  *        ║  ", "dim"),
        ("  ║   │REACT.│          o                ║  ", "white"),
        ("  ║   │ B-7  │  ~~~    /|\\    o          ║  ", "white"),
        ("  ║   │!!!!!│  ~~~     |    /|\\          ║  ", "bold red"),
        ("  ║   └──────┘        / \\ ZARA           ║  ", "dim cyan"),
        ("  ║     ↑ FAULT    [REPAIR NEEDED]       ║  ", "bold yellow"),
        ("  ╚══════════════════════════════════════╝  ", "yellow"),
    ],

    "cargo_hold": [
        ("  ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  ", "dim"),
        ("  ░                                    ░  ", "dim"),
        ("  ░  [CRATE]  [CRATE]  [CRATE]         ░  ", "dim white"),
        ("  ░                                    ░  ", "dim"),
        ("  ░      o         ┌────────────┐      ░  ", "white"),
        ("  ░     /|\\        │ ENCRYPTED  │      ░  ", "white"),
        ("  ░      |         │   DEVICE   │      ░  ", "bold yellow"),
        ("  ░     / \\        └────────────┘      ░  ", "dim white"),
        ("  ░    YOU  →→→→→  [EVIDENCE FOUND]    ░  ", "bold cyan"),
        ("  ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  ", "dim"),
    ],

    "aria_server_room": [
        ("  ┌────────────────────────────────────┐  ", "blue"),
        ("  │  ◈  ARIA SERVER ROOM  ◈            │  ", "bold cyan"),
        ("  │                                    │  ", "blue"),
        ("  │   [█][█][█][░][█][█]  o            │  ", "cyan"),
        ("  │   [█][█][█][X][█][█] /|\\           │  ", "bold red"),
        ("  │   [█][█][█][░][█][█]  |            │  ", "cyan"),
        ("  │         ↑            / \\           │  ", "bold yellow"),
        ("  │    CORRUPTED        YOU            │  ", "bold yellow"),
        ("  │   [OVERRIDE: ACTIVE — MEMORY GONE] │  ", "bold red"),
        ("  └────────────────────────────────────┘  ", "blue"),
    ],

    # ── Character interaction scenes ──────────────────────────────────────────

    "talking_patel": [
        ("  ┌──────────────────────────────────────┐  ", "white"),
        ("  │  ✚  DR. PATEL — CHIEF MEDICAL        │  ", "bold white"),
        ("  │                                      │  ", "white"),
        ("  │         o            o               │  ", "white"),
        ("  │        /|\\          /|\\              │  ", "white"),
        ("  │         |            |    ___        │  ", "white"),
        ("  │        / \\          / \\  |   |       │  ", "dim white"),
        ("  │      DR.PATEL      YOU  |LOG|       │  ", "bold cyan"),
        ("  │                        |___|       │  ", "dim"),
        ("  │   \"The sedative traces — that's     │  ", "dim yellow"),
        ("  │    what concerns me, Commander.\"    │  ", "dim yellow"),
        ("  └──────────────────────────────────────┘  ", "white"),
    ],

    "talking_zara": [
        ("  ╔══════════════════════════════════════╗  ", "yellow"),
        ("  ║  ⚙  ZARA KIM — CHIEF ENGINEER       ║  ", "bold yellow"),
        ("  ║                                      ║  ", "yellow"),
        ("  ║   ┌──────┐      o          o         ║  ", "dim"),
        ("  ║   │ B-7  │     /|\\        /|\\        ║  ", "white"),
        ("  ║   │FAULT │      |          |         ║  ", "bold red"),
        ("  ║   └──────┘     / \\        / \\        ║  ", "dim"),
        ("  ║              ZARA         YOU        ║  ", "bold cyan"),
        ("  ║   \"I can bypass it. But it won't     ║  ", "dim yellow"),
        ("  ║    hold forever, Commander.\"         ║  ", "dim yellow"),
        ("  ╚══════════════════════════════════════╝  ", "yellow"),
    ],

    "talking_lyra": [
        ("   .  *    .       *    .   *    .  *     ", "dim white"),
        ("  ┌──────────────────────────────────────┐  ", "cyan"),
        ("  │  ◈  LYRA CHEN — NAVIGATOR            │  ", "bold cyan"),
        ("  │                                      │  ", "cyan"),
        ("  │      o              o    [NAV CHART] │  ", "white"),
        ("  │     /|\\            /|\\   ┌─────────┐ │  ", "white"),
        ("  │      |              |    │ · · · · │ │  ", "dim cyan"),
        ("  │     / \\            / \\   │ ·DRONE· │ │  ", "bold yellow"),
        ("  │    LYRA            YOU   └─────────┘ │  ", "bold cyan"),
        ("  │   \"The drone log shows an off-        │  ", "dim yellow"),
        ("  │    schedule delivery, Commander.\"    │  ", "dim yellow"),
        ("  └──────────────────────────────────────┘  ", "cyan"),
    ],

    "talking_kai": [
        ("  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓  ", "dim red"),
        ("  ▓  ⚠  KAI REEVES — SECURITY CHIEF  ⚠  ▓  ", "bold red"),
        ("  ▓                                    ▓  ", "dim red"),
        ("  ▓     o                    o         ▓  ", "white"),
        ("  ▓    /|\\    [ . . . ]     /|\\        ▓  ", "white"),
        ("  ▓     |      TENSE         |         ▓  ", "bold yellow"),
        ("  ▓    / \\                  / \\        ▓  ", "white"),
        ("  ▓   KAI                  YOU         ▓  ", "bold red"),
        ("  ▓                                    ▓  ", "dim red"),
        ("  ▓   [STAGE {stage}] [TRUST: FALLING] ▓  ", "bold yellow"),
        ("  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓  ", "dim red"),
    ],

    "talking_aria": [
        ("  ┌────────────────────────────────────┐  ", "blue"),
        ("  │  ◈  ARIA — STATION AI  ◈           │  ", "bold cyan"),
        ("  ├────────────────────────────────────┤  ", "blue"),
        ("  │                                    │  ", "blue"),
        ("  │   [■■■■■■■■■■■■■■■■■■■■■■■■■■■]   │  ", "cyan"),
        ("  │   [■  ARIA NEURAL INTERFACE  ■]   │  ", "bold cyan"),
        ("  │   [■■■■■■■■■■■■■■■■■■■■■■■■■■■]   │  ", "cyan"),
        ("  │              ↕                    │  ", "dim"),
        ("  │              o                    │  ", "white"),
        ("  │             /|\\   YOU             │  ", "white"),
        ("  │   [MEMORY: SUPPRESSED BY CORP]    │  ", "bold red"),
        ("  └────────────────────────────────────┘  ", "blue"),
    ],

    "confrontation": [
        ("  ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  ", "dim red"),
        ("  ░                                  ░  ", "dim red"),
        ("  ░    o                    o        ░  ", "white"),
        ("  ░   /|\\  ←— EVIDENCE —→  /|\\      ░  ", "bold white"),
        ("  ░    |                    |        ░  ", "white"),
        ("  ░   / \\                  / \\       ░  ", "white"),
        ("  ░   YOU                 KAI        ░  ", "bold cyan"),
        ("  ░                                  ░  ", "dim red"),
        ("  ░   [CONFRONTATION — TRUTH MOMENT] ░  ", "bold yellow"),
        ("  ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  ", "dim red"),
    ],

    "oxygen_critical": [
        ("  ████████████████████████████████████  ", "bold red"),
        ("  █   ⚠  O₂ CRITICAL  ⚠              █  ", "bold white"),
        ("  █                                  █  ", "bold red"),
        ("  █     o         o        o         █  ", "dim white"),
        ("  █    /|\\       /|\\      /|\\        █  ", "dim white"),
        ("  █     |  ~*~    |  ~*~   |         █  ", "dim red"),
        ("  █    / \\       / \\      / \\        █  ", "dim white"),
        ("  █  CREW STRUGGLING — AIR THINNING  █  ", "bold yellow"),
        ("  █   [ TYPE: fix oxygen — NOW ]     █  ", "bold white"),
        ("  ████████████████████████████████████  ", "bold red"),
    ],

    "default": [
        ("   *    .       *    .   *    .  *  .  *  ", "dim white"),
        ("  ┌───────────────────────────────────┐  ", "dim cyan"),
        ("  │   ISS TARTARUS — KEPLER-452        │  ", "bold cyan"),
        ("  │                                   │  ", "dim cyan"),
        ("  │        o    .  *    .             │  ", "white"),
        ("  │       /|\\      ·                 │  ", "white"),
        ("  │        |    *     .    *          │  ", "white"),
        ("  │       / \\  COMMANDER              │  ", "dim cyan"),
        ("  │                                   │  ", "dim cyan"),
        ("  └───────────────────────────────────┘  ", "dim cyan"),
    ],
}

LOCATION_TO_SCENE: dict[str, str] = {
    "command deck": "command_deck",
    "airlock 7": "airlock_7",
    "airlock": "airlock_7",
    "event log": "airlock_7",
    "access log": "airlock_7",
    "breach log": "airlock_7",
    "manual override": "airlock_7",
    "section c": "airlock_7",
    "medical bay": "medical_bay",
    "med bay": "medical_bay",
    "autopsy": "medical_bay",
    "post-mortem": "medical_bay",
    "post mortem": "medical_bay",
    "body": "medical_bay",
    "voss's body": "medical_bay",
    "engineering bay": "engineering_bay",
    "engineering": "engineering_bay",
    "reactor": "engineering_bay",
    "b-7": "engineering_bay",
    "junction b": "engineering_bay",
    "coolant": "engineering_bay",
    "cargo hold": "cargo_hold",
    "cargo": "cargo_hold",
    "crate": "cargo_hold",
    "comms device": "cargo_hold",
    "encrypted device": "cargo_hold",
    "aria server": "aria_server_room",
    "server room": "aria_server_room",
    "aria's memory": "aria_server_room",
    "aria logs": "aria_server_room",
    "security log": "airlock_7",
    "security camera": "airlock_7",
    "timeline": "airlock_7",
    "escape pod": "airlock_7",
    "pod 3": "airlock_7",
}

# Keywords in player input → character scene (order matters — first match wins)
CHARACTER_TRIGGERS: list[tuple[list[str], str]] = [
    # Confrontation takes highest priority
    (["confront", "accuse kai", "accuse reeves", "present evidence to kai"], "confrontation"),
    # Kai / security
    (["kai", "kai reeves", "reeves", "security chief", "security officer",
      "interrogate kai", "question kai", "speak to kai", "talk to kai",
      "interview kai", "whereabouts", "alibi"], "talking_kai"),
    # Patel / medical
    (["patel", "dr patel", "dr. patel", "doctor patel", "chief medical",
      "medical officer", "psychological profile", "crew behaviour", "crew behavior",
      "unusual behavior", "unusual behaviour", "mental state", "sedative",
      "toxicology", "cause of death", "injury", "wounds", "blunt force",
      "medical findings", "medical report", "health", "trauma"], "talking_patel"),
    # Lyra / navigation
    (["lyra", "lyra chen", "navigator", "navigation officer",
      "drone log", "cargo drone", "nav log", "flight log",
      "drone schedule", "delivery log", "drone route",
      "ship log", "trajectory", "flight path"], "talking_lyra"),
    # Zara / engineering
    (["zara", "zara kim", "chief engineer", "engineer",
      "repair", "fix", "coolant", "bypass", "scrubber",
      "oxygen system", "o2 system", "power system",
      "reactor fault", "b-7", "junction"], "talking_zara"),
    # ARIA
    (["aria", "station ai", "ship ai", "ai system",
      "override code", "aria override", "aria logs", "aria memory",
      "query aria", "hack aria", "aria subsystem",
      "neural interface", "ship computer", "computer logs"], "talking_aria"),
]


def player_input_to_scene_key(player_input: str, state: dict | None = None) -> str | None:
    """
    Detect the best scene key from player input text.
    Checks character triggers first, then location keywords.
    Returns None if no match found.
    """
    text = player_input.lower()

    # 1. Character triggers (first match wins)
    for keywords, scene_key in CHARACTER_TRIGGERS:
        if any(kw in text for kw in keywords):
            return scene_key

    # 2. Location keywords
    for keyword, scene_key in LOCATION_TO_SCENE.items():
        if keyword in text:
            return scene_key

    return None


def location_to_scene_key(location: str) -> str:
    """Map a game location string to a scene key."""
    loc = location.lower()
    for key, scene in LOCATION_TO_SCENE.items():
        if key in loc:
            return scene
    return "default"


def print_scene_art(scene_key: str, o2: int = 100, kai_stage: int = 1) -> None:
    if o2 <= 30:
        scene_key = "oxygen_critical"

    lines = SCENES.get(scene_key, SCENES["default"])

    text = Text()
    for line, style in lines:
        # Substitute {stage} placeholder for Kai scenes
        rendered = line.replace("{stage}", str(kai_stage))
        text.append(rendered + "\n", style=style)

    border = "red" if (o2 <= 50 or kai_stage == 3 or scene_key in ("confrontation", "talking_kai", "oxygen_critical")) else "dim cyan"

    console.print(Panel(
        text,
        border_style=border,
        padding=(0, 0),
        expand=False,
    ))
