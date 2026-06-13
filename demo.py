"""
Demo mode — auto-plays 6 key scenes with narration pauses.
Run: python demo.py
Press ENTER to advance each scene. Takes ~3 minutes.
"""

import sys
import time
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.rule import Rule

from config import Config
from telemetry.tracing import setup_telemetry
from tools.state_manager import StateManager
from tools.knowledge_base import KnowledgeBase
from agents.commander import CommanderAgent

console = Console()

DEMO_SCRIPT = [
    {
        "label": "SCENE 1 — Investigation Begins",
        "narrate": "Commander begins investigating Dr. Voss's death. First stop: the medical bay.",
        "input": "talk to Patel about post-mortem findings on Dr. Voss",
    },
    {
        "label": "SCENE 2 — Navigation Anomaly",
        "narrate": "Lyra flags an off-schedule cargo drone and a suspicious transmission.",
        "input": "ask Lyra about unusual log entries around the time of the incident",
    },
    {
        "label": "SCENE 3 — Airlock Evidence",
        "narrate": "The security log places someone at Airlock 7's override terminal at 01:57.",
        "input": "inspect the security station access log for airlock 7 and escape pod bay",
    },
    {
        "label": "SCENE 4 — ARIA Interrogation",
        "narrate": "ARIA knows something — but a corporate override is suppressing its memory.",
        "input": "query ARIA about what happened between 02:00 and 02:30 on day 2888",
    },
    {
        "label": "SCENE 5 — The Smoking Gun",
        "narrate": "A hidden comms device in the cargo hold links the murder to Axiom Industries.",
        "input": "search the cargo hold for hidden devices and ask Lyra to decrypt the comms device",
    },
    {
        "label": "SCENE 6 — Confrontation & Truth",
        "narrate": "With 5 pieces of evidence, the Commander confronts Kai Reeves.",
        "input": "confront kai reeves with all evidence __confirmed",
    },
]


def pause(label: str, narrate: str) -> None:
    console.print()
    console.print(Rule(f"[bold yellow]{label}[/bold yellow]", style="yellow"))
    console.print(Panel(
        f"[dim italic]{narrate}[/dim italic]\n\n[yellow]Press ENTER to run this scene...[/yellow]",
        border_style="dim",
        padding=(0, 2),
    ))
    input()


def print_scene(narration: str) -> None:
    import re
    pattern = r'---\s*(SCENE|STATUS|CHOICES)\s*---(.*?)(?=---\s*(?:SCENE|STATUS|CHOICES)\s*---|$)'
    matches = re.findall(pattern, narration, re.DOTALL)

    if not matches:
        console.print(Panel(narration.strip(), title="[bold cyan]▶ SCENE[/bold cyan]", border_style="cyan", padding=(1, 2)))
        return

    for section_name, content in matches:
        content = content.strip()
        if not content:
            continue
        if section_name == "SCENE":
            console.print(Panel(content, title="[bold cyan]▶ SCENE[/bold cyan]", border_style="cyan", padding=(1, 2)))
        elif section_name == "STATUS":
            console.print(Panel(f"[dim]{content}[/dim]", title="[dim]STATUS UPDATE[/dim]", border_style="dim", padding=(0, 2)))
        elif section_name == "CHOICES":
            console.print(Panel(content, title="[bold yellow]◈ YOUR OPTIONS[/bold yellow]", border_style="yellow", padding=(1, 2)))


def main() -> None:
    if Config.has_telemetry():
        setup_telemetry(Config.APPLICATIONINSIGHTS_CONNECTION_STRING)

    console.clear()
    console.print(Panel(
        Text.from_markup(
            "[bold cyan]T H E   F R A C T U R E D   O R B I T[/bold cyan]\n\n"
            "[dim]DEMO MODE — 6 scenes — ~3 minutes[/dim]\n\n"
            "[yellow]ISS Tartarus · Deep Space · Station Day 2891[/yellow]\n"
            "[red]Dr. Mira Voss is dead. Airlock 7 opened from the inside.\nHeliosCore wants it classified as an accident.[/red]"
        ),
        title="[bold white]● DEMO START[/bold white]",
        border_style="cyan",
        padding=(1, 4),
    ))

    state_manager = StateManager()
    knowledge_base = KnowledgeBase()
    commander = CommanderAgent(state_manager, knowledge_base)

    state = state_manager.create_session("Commander [DEMO]")

    # Seed evidence so final confrontation is dramatic
    state["evidence"] = [
        "patel_blunt_force_trauma",
        "nav_log_off_schedule_drone",
        "security_station_2_override_query",
        "escape_pod_3_manual_lock",
        "cargo_hold_encrypted_comms_device",
    ]
    state["crew_trust"]["kai_reeves"] = 10
    state["kai_stage"] = 3

    for scene in DEMO_SCRIPT:
        pause(scene["label"], scene["narrate"])
        console.print(f"\n[dim]Commander: {scene['input']}[/dim]\n")
        console.print("[dim]Agents processing...[/dim]", end="\r")

        try:
            narration, state = commander.process_turn(scene["input"], state)
            state_manager.save_session(state)
        except Exception as exc:
            console.print(f"[red]Error: {exc}[/red]")
            continue

        print_scene(narration)

        # Show evidence count after each scene
        ev_count = len(state.get("evidence", []))
        console.print(f"\n[dim]Evidence collected: {ev_count} items | Oxygen: {state.get('oxygen_level')}% | Day: {state.get('station_day')}[/dim]")

    console.print()
    console.print(Panel(
        "[bold green]DEMO COMPLETE[/bold green]\n\n"
        "The Fractured Orbit demonstrates:\n"
        "  ✓ Multi-agent orchestration (Commander + 5 crew agents)\n"
        "  ✓ Foundry IQ grounded knowledge retrieval (Azure AI Search)\n"
        "  ✓ Unreliable AI agent mechanic (ARIA override)\n"
        "  ✓ Persistent game state (Cosmos DB)\n"
        "  ✓ Dice-based skill checks and consequences\n"
        "  ✓ Human-in-the-loop for irreversible actions\n"
        "  ✓ Full telemetry in Application Insights",
        border_style="green",
        padding=(1, 2),
    ))


if __name__ == "__main__":
    main()
