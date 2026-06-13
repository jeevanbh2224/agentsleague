"""
The Fractured Orbit — Main Game Loop
ISS Tartarus Deep-Space Mystery | Microsoft Agents League Challenge B
"""

import os
import sys
import time
import random

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.rule import Rule
from rich.live import Live
from rich.align import Align
from rich import box

from config import Config
from telemetry.tracing import setup_telemetry
from tools.state_manager import StateManager
from tools.knowledge_base import KnowledgeBase
from agents.commander import CommanderAgent
from tools.ascii_scenes import print_scene_art, location_to_scene_key, player_input_to_scene_key

console = Console()

BOOT_LINES = [
    "[dim]INITIALISING TARTARUS COMMAND INTERFACE...[/dim]",
    "[dim]LIFE SUPPORT: ONLINE[/dim]",
    "[dim]NAVIGATION: ONLINE[/dim]",
    "[dim]ARIA SUBSYSTEM: [yellow]DEGRADED — OVERRIDE ACTIVE[/yellow][/dim]",
    "[dim]REACTOR: [yellow]WARNING — JUNCTION B-7 FAULT[/dim]",
    "[dim]CREW STATUS: 5 ACTIVE · 1 DECEASED[/dim]",
    "[dim]SECTION C: [red]VACUUM BREACH — DO NOT ENTER WITHOUT EVA[/red][/dim]",
    "[bold red]⚠  STATION EMERGENCY PROTOCOL ACTIVE[/bold red]",
]

ASCII_LOGO = """
[bold cyan]
  ████████╗██╗  ██╗███████╗    ███████╗██████╗  █████╗  ██████╗████████╗██╗   ██╗██████╗ ███████╗██████╗
     ██╔══╝██║  ██║██╔════╝    ██╔════╝██╔══██╗██╔══██╗██╔════╝╚══██╔══╝██║   ██║██╔══██╗██╔════╝██╔══██╗
     ██║   ███████║█████╗      █████╗  ██████╔╝███████║██║        ██║   ██║   ██║██████╔╝█████╗  ██║  ██║
     ██║   ██╔══██║██╔══╝      ██╔══╝  ██╔══██╗██╔══██║██║        ██║   ██║   ██║██╔══██╗██╔══╝  ██║  ██║
     ██║   ██║  ██║███████╗    ██║     ██║  ██║██║  ██║╚██████╗   ██║   ╚██████╔╝██║  ██║███████╗██████╔╝
     ╚═╝   ╚═╝  ╚═╝╚══════╝    ╚═╝     ╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝   ╚═╝    ╚═════╝ ╚═╝  ╚═╝╚══════╝╚═════╝
[/bold cyan]
[bold white]  ██████╗ ██████╗ ██████╗ ██╗████████╗[/bold white]
[bold white]  ██╔══██╗██╔══██╗██╔══██╗██║╚══██╔══╝[/bold white]
[bold white]  ██║  ██║██████╔╝██████╔╝██║   ██║   [/bold white]
[bold white]  ██║  ██║██╔══██╗██╔══██╗██║   ██║   [/bold white]
[bold white]  ██████╔╝██║  ██║██████╔╝██║   ██║   [/bold white]
[bold white]  ╚═════╝ ╚═╝  ╚═╝╚═════╝ ╚═╝   ╚═╝   [/bold white]
[dim]                          ISS Tartarus · Kepler-452 · 1,400 ly from Earth[/dim]
"""

def boot_sequence() -> None:
    """Animated boot sequence with glitch effect."""
    console.clear()
    time.sleep(0.2)

    # Flicker effect
    for _ in range(3):
        console.clear()
        time.sleep(0.05)
        console.print("[bold cyan]█[/bold cyan]")
        time.sleep(0.05)

    console.clear()
    console.print(ASCII_LOGO)
    time.sleep(0.4)

    console.print()
    for line in BOOT_LINES:
        console.print(f"  {line}")
        time.sleep(0.18)

    time.sleep(0.3)
    console.print()
    console.print(Rule("[bold red]  INCIDENT REPORT — STATION DAY 2888  [/bold red]", style="red"))
    time.sleep(0.2)

    incident_lines = [
        ("02:14", "[red]AIRLOCK 7 — MANUAL OVERRIDE DETECTED[/red]"),
        ("02:14", "[red]SECTION C — ATMOSPHERIC BREACH[/red]"),
        ("02:15", "[red]CREW MEMBER C-07 — UNRESPONSIVE[/red]"),
        ("02:31", "[yellow]ARIA TELEMETRY — CORRUPTED (02:00–02:30)[/yellow]"),
        ("06:00", "[yellow]HELIOSCORE HQ — ENCRYPTED DIRECTIVE RECEIVED[/yellow]"),
    ]
    for ts, event in incident_lines:
        console.print(f"  [dim]{ts}[/dim]  {event}")
        time.sleep(0.2)

    console.print()
    console.print(Rule(style="red"))
    time.sleep(0.3)
    console.print()
    console.print(Align.center(
        Text.from_markup(
            "[bold yellow]HeliosCore wants you to call it an accident.[/bold yellow]\n"
            "[bold white]You don't believe it was.[/bold white]"
        )
    ))
    console.print()
    time.sleep(0.5)


def print_intro() -> None:
    boot_sequence()


def print_status(state: dict) -> None:
    table = Table(box=box.SIMPLE, show_header=False, pad_edge=False)
    table.add_column(style="dim", width=22)
    table.add_column(style="white")

    o2 = state.get("oxygen_level", 0)
    days_left = 2909 - state.get("station_day", 2891)
    hour = state.get("in_game_hour", 0)

    # Pulse effect — alternates on each render using system time
    pulse = int(time.time() * 2) % 2 == 0

    # Oxygen
    if o2 <= 50:
        o2_display = f"[bold white on red]  {o2}%  ⚠ CRITICAL  [/bold white on red]" if pulse else f"[bold red]  !! {o2}%  ⚠ CRITICAL !!  [/bold red]"
    elif o2 <= 70:
        o2_display = f"[bold black on yellow]  {o2}%  ⚠ LOW  [/bold black on yellow]" if pulse else f"[bold yellow]  >> {o2}%  ⚠ LOW <<  [/bold yellow]"
    else:
        o2_display = f"[bold green]{o2}%  ✓ NOMINAL[/bold green]"

    # Time
    period = "NIGHT CYCLE 🌑" if 0 <= hour < 6 else ("MORNING 🌅" if hour < 12 else ("AFTERNOON ☀" if hour < 18 else "NIGHT CYCLE 🌑"))
    time_display = f"[bold cyan]{hour:02d}:00[/bold cyan]  [dim]{period}[/dim]"

    # Reactor
    reactor = state.get("reactor_status", "unknown")
    if reactor == "critical":
        reactor_display = f"[bold white on red]  ██ FAILURE IMMINENT ██  [/bold white on red]" if pulse else f"[bold red]  !! FAILURE IMMINENT !!  [/bold red]"
    elif reactor == "degraded":
        reactor_display = f"[bold black on yellow]  ⚠ DEGRADED — B-7 FAULT  [/bold black on yellow]" if pulse else f"[bold yellow]  >> DEGRADED — B-7 FAULT <<  [/bold yellow]"
    else:
        reactor_display = "[bold green]■■■■■ OPERATIONAL[/bold green]"

    # Resolution team
    if days_left <= 7:
        team_display = f"[bold white on red]  T-{days_left} DAYS — CORP TEAM INCOMING  [/bold white on red]" if pulse else f"[bold red]  !! T-{days_left} DAYS !!  [/bold red]"
    elif days_left <= 14:
        team_display = f"[bold black on yellow]  T-{days_left} days  [/bold black on yellow]"
    else:
        team_display = f"[dim]T-{days_left} days[/dim]"

    # ARIA
    aria_override = state.get("aria_override_active", True)
    if aria_override:
        aria_display = f"[bold black on yellow]  ⚠ OVERRIDE ACTIVE  [/bold black on yellow]" if pulse else f"[bold yellow]  >> MEMORY SUPPRESSED <<  [/bold yellow]"
    else:
        aria_display = "[bold green]  ✓ UNLOCKED — FULL ACCESS  [/bold green]"

    # Evidence bar
    ev_count = len(state.get("evidence", []))
    ev_bar = "[cyan]" + "▰" * ev_count + "[/cyan][dim]" + "▱" * max(0, 10 - ev_count) + "[/dim]"
    ev_display = f"{ev_bar} [bold]{ev_count}[/bold]/10"

    table.add_row("◈ STATION DAY", f"[bold cyan]{state.get('station_day', '?')}[/bold cyan]")
    table.add_row("◈ TIME", time_display)
    table.add_row("◈ LOCATION", f"[bold white]{state.get('location', '?')}[/bold white]")
    table.add_row("◈ OXYGEN", o2_display)
    table.add_row("◈ EVIDENCE", ev_display)
    table.add_row("◈ REACTOR", reactor_display)
    table.add_row("◈ ARIA", aria_display)
    table.add_row("◈ RESOLUTION TEAM", team_display)

    if state.get("conditions"):
        cond = ", ".join(state["conditions"])
        cond_display = f"[bold white on red]  {cond}  [/bold white on red]" if pulse else f"[bold red]  !! {cond} !!  [/bold red]"
        table.add_row("◈ CONDITIONS", cond_display)

    console.print(Panel(
        table,
        title="[bold dim]━━  TARTARUS COMMAND INTERFACE  ━━[/bold dim]",
        border_style="dim cyan",
        padding=(0, 1),
    ))


def oxygen_alert(state: dict) -> None:
    """Print a big urgent oxygen warning when O2 drops below 60%."""
    o2 = state.get("oxygen_level", 100)
    if o2 > 60:
        return

    console.print()
    if o2 <= 30:
        banner = (
            "[bold white on red]                                                               [/bold white on red]\n"
            "[bold white on red]   ██████ CRITICAL: OXYGEN LEVELS DANGEROUSLY LOW █████████   [/bold white on red]\n"
            "[bold white on red]   ██  Station-wide CO₂ scrubbers at minimum capacity.  ████   [/bold white on red]\n"
            f"[bold white on red]   ██  Current O₂: {o2:>3}% — CREW INCAPACITATION IMMINENT   ████   [/bold white on red]\n"
            "[bold white on red]                                                               [/bold white on red]"
        )
        hint = (
            "[bold red]▶ URGENT MISSION:[/bold red] Restore oxygen immediately or lose the crew.\n"
            "[yellow]  → Go to Engineering Bay and restart the O₂ recycler\n"
            "  → Ask Zara Kim (Engineer) to bypass the B-7 reactor fault\n"
            "  → Use the Emergency O₂ Canister in Medical Bay (one-time use)[/yellow]\n\n"
            "[bold white on red]  TYPE: fix oxygen  [/bold white on red][dim]  ← instant repair command available now[/dim]"
        )
    elif o2 <= 50:
        banner = (
            "[bold black on yellow]                                                          [/bold black on yellow]\n"
            "[bold black on yellow]   ⚠⚠  WARNING: STATION OXYGEN CRITICALLY LOW  ⚠⚠         [/bold black on yellow]\n"
            "[bold black on yellow]   ⚠⚠  Scrubber efficiency at minimum threshold.  ⚠⚠       [/bold black on yellow]\n"
            f"[bold black on yellow]   ⚠⚠  Current O₂: {o2:>3}% — ACT NOW                  ⚠⚠       [/bold black on yellow]\n"
            "[bold black on yellow]                                                          [/bold black on yellow]"
        )
        hint = (
            "[bold yellow]▶ PRIORITY MISSION:[/bold yellow] Oxygen supply is failing.\n"
            "[dim]  → Investigate the Engineering Bay — reactor fault is bleeding O₂\n"
            "  → Ask Zara Kim to assess the B-7 recycler bypass\n"
            "  → Check Medical Bay for emergency O₂ canisters[/dim]\n\n"
            "[bold black on yellow]  TYPE: fix oxygen  [/bold black on yellow][dim]  ← repair command available now[/dim]"
        )
    else:  # 50 < o2 <= 60
        banner = (
            "[bold yellow]  ⚠  STATION OXYGEN LOW — O₂ reserves falling  ⚠  [/bold yellow]\n"
            f"[bold yellow]  ⚠  Current O₂: {o2}% — Degraded reactor is venting atmosphere  ⚠  [/bold yellow]"
        )
        hint = (
            "[dim yellow]▶ SIDE MISSION:[/dim yellow] [yellow]The reactor B-7 fault is draining oxygen.\n"
            "  → Speak to Zara Kim about the reactor — she may know a fix\n"
            "  → Check Engineering Bay for repair options[/yellow]\n\n"
            "[yellow]  TYPE: [bold]fix oxygen[/bold] — Zara bypasses the scrubber (+30% O₂, one-time)[/yellow]"
        )

    console.print(Panel(banner, border_style="red" if o2 <= 50 else "yellow", padding=(0, 1)))
    console.print(Panel(hint, border_style="dim", padding=(0, 2)))
    console.print()


def _typewriter(text: str, delay: float = 0.012) -> None:
    """Print text with a typewriter effect."""
    for char in text:
        console.print(char, end="", highlight=False)
        time.sleep(delay)
    console.print()


def _processing_animation() -> None:
    frames = ["▰▱▱▱▱", "▰▰▱▱▱", "▰▰▰▱▱", "▰▰▰▰▱", "▰▰▰▰▰"]
    for frame in frames:
        console.print(f"  [cyan]{frame}[/cyan] [dim]Agents processing...[/dim]", end="\r")
        time.sleep(0.12)
    console.print(" " * 40, end="\r")


def print_scene(narration: str, state: dict | None = None) -> None:
    import re
    o2 = state.get("oxygen_level", 100) if state else 100
    kai_stage = state.get("kai_stage", 1) if state else 1

    # Scene border flashes red if oxygen critical or Kai is desperate
    scene_border = "red" if (o2 < 60 or kai_stage == 3) else "cyan"
    scene_title = "[bold red]▶ SCENE — CRITICAL[/bold red]" if scene_border == "red" else "[bold cyan]▶ SCENE[/bold cyan]"

    pattern = r'---\s*(SCENE|STATUS|CHOICES)\s*---(.*?)(?=---\s*(?:SCENE|STATUS|CHOICES)\s*---|$)'
    matches = re.findall(pattern, narration, re.DOTALL)

    if not matches:
        console.print()
        console.print(Panel(narration.strip(), title=scene_title, border_style=scene_border, padding=(1, 2)))
        return

    for section_name, content in matches:
        content = content.strip()
        if not content:
            continue
        if section_name == "SCENE":
            console.print()
            console.print(Panel(
                content,
                title=scene_title,
                border_style=scene_border,
                padding=(1, 2),
            ))
        elif section_name == "STATUS":
            console.print(Panel(
                f"[dim]{content}[/dim]",
                title="[dim]STATUS UPDATE[/dim]",
                border_style="dim",
                padding=(0, 2),
            ))
        elif section_name == "CHOICES":
            # Inject oxygen repair option when O2 is low
            oxygen_repaired = state.get("oxygen_repaired", False) if state else False
            if o2 <= 60 and not oxygen_repaired:
                o2_option = f"\n[bold yellow]  ⚠ fix oxygen[/bold yellow] [dim]— Zara bypasses the B-7 scrubber (+30% O₂)[/dim]"
            else:
                o2_option = ""
            console.print(Panel(
                content + o2_option,
                title="[bold yellow]◈ YOUR OPTIONS[/bold yellow]",
                border_style="yellow",
                padding=(1, 2),
            ))


def print_dice_roll(result) -> None:
    """Animate and display a dice roll."""
    if not result:
        return
    console.print()
    console.print(Rule("[dim]SKILL CHECK[/dim]", style="dim"))
    time.sleep(0.3)
    for _ in range(3):
        console.print(f"  [dim]Rolling d20...[/dim]", end="\r")
        time.sleep(0.2)

    outcome_colors = {
        "critical_failure": "bold red",
        "failure": "red",
        "partial_success": "yellow",
        "success": "green",
        "critical_success": "bold green",
    }
    color = outcome_colors.get(result.outcome.value, "white")

    console.print(
        f"  [dim]Skill:[/dim] {result.skill.title()} | "
        f"[dim]Roll:[/dim] {result.raw_roll} + {result.modifier} = "
        f"[bold]{result.total}[/bold] [dim]vs DC[/dim] {result.difficulty} → "
        f"[{color}]{result.outcome.value.replace('_', ' ').upper()}[/{color}]"
    )
    console.print(Rule(style="dim"))
    console.print()


def get_player_input(session_id: str) -> str:
    console.print()
    try:
        action = console.input("[bold yellow]> What do you do? [/bold yellow]").strip()
        return action
    except (KeyboardInterrupt, EOFError):
        return "quit"


def select_or_create_session(sm: StateManager) -> dict:
    """Show session menu and return a game state dict."""
    sessions = sm.list_sessions()

    console.print(Panel(
        "[bold]Start a new investigation or continue an existing one.[/bold]",
        border_style="dim",
    ))

    if sessions:
        console.print("\n[dim]Existing sessions:[/dim]")
        for i, s in enumerate(sessions, 1):
            console.print(
                f"  {i}. [cyan]{s['player_name']}[/cyan] — "
                f"Day {s.get('station_day', '?')} — "
                f"[dim]{s.get('updated_at', '')[:10]}[/dim]"
            )
        console.print()

    choice = console.input(
        "[yellow]Enter session number to continue, or press Enter for a new game: [/yellow]"
    ).strip()

    if choice.isdigit() and 1 <= int(choice) <= len(sessions):
        sid = sessions[int(choice) - 1]["id"]
        state = sm.load_session(sid)
        if state:
            console.print(f"\n[green]Resuming session — Day {state['station_day']}[/green]")
            return state

    # New session
    name = console.input("[yellow]Enter your name, Commander: [/yellow]").strip()
    if not name:
        name = "Commander"
    state = sm.create_session(name)
    console.print(f"\n[green]Session created. Welcome aboard, {name}.[/green]")
    return state


def check_game_end(state: dict, turns_this_session: int) -> str | None:
    """
    Return an ending string if the game has concluded, else None.
    Only checks after at least 2 turns played in current session.
    Endings: TRUTH, SURVIVAL, CORPORATE, COMPROMISE, FAILURE
    """
    if turns_this_session < 2:
        return None

    days_left = 2909 - state.get("station_day", 2891)

    if days_left <= 0:
        if not state.get("kai_confronted") and not state.get("distress_signal_sent"):
            return "FAILURE"

    evidence_count = len(state.get("evidence", []))

    if state.get("kai_confronted") and evidence_count >= 4:
        if state.get("distress_signal_sent"):
            return "TRUTH"
        return "SURVIVAL"

    if state.get("decisions") and any(
        "follow helioscore orders" in d.get("decision", "").lower()
        for d in state["decisions"]
    ):
        return "CORPORATE"

    return None


def print_ending(ending: str, state: dict) -> None:
    endings = {
        "TRUTH": (
            "cyan",
            "ENDING: TRUTH",
            "Kai Reeves confesses. The encrypted comms device ties Axiom Industries to the murder.\n"
            "You transmit everything to the Independent Outer Systems Authority.\n"
            "Seven days later, an IOSA ship arrives before HeliosCore's resolution team.\n"
            "HeliosCore's Veilite operation is suspended pending investigation.\n"
            "Dr. Mira Voss's name is cleared. Justice, if not comfort, is served.\n\n"
            "[dim]The station is quiet for the first time in three days.[/dim]",
        ),
        "SURVIVAL": (
            "yellow",
            "ENDING: SURVIVAL",
            "Kai Reeves is confined to quarters. The evidence is secured.\n"
            "HeliosCore's resolution team arrives on schedule.\n"
            "They classify the incident as 'under internal review' — corporate language for buried.\n"
            "Kai is quietly transferred. You never learn what became of him.\n"
            "The crew makes it home. The truth stays aboard Tartarus.\n\n"
            "[dim]Some questions don't get answers. Some answers don't get justice.[/dim]",
        ),
        "CORPORATE": (
            "red",
            "ENDING: CORPORATE",
            "You filed Form 7-A. Accidental airlock failure.\n"
            "HeliosCore's resolution team arrives and commends your professionalism.\n"
            "Kai Reeves is promoted to senior security consultant on another station.\n"
            "Dr. Voss's family receives a standard bereavement payment.\n\n"
            "[dim]You tell yourself you had no choice. The stars outside don't disagree.[/dim]",
        ),
        "COMPROMISE": (
            "yellow",
            "ENDING: COMPROMISE",
            "You used the Veilite as leverage. HeliosCore agreed to your terms.\n"
            "Safe passage home. No 'review.' Voss's death sealed under a non-disclosure agreement.\n"
            "Axiom Industries never got their data. Kai walks free under the terms.\n\n"
            "[dim]You saved the crew. You also let a murderer go.\n"
            "Whether that was the right call is something only you have to live with.[/dim]",
        ),
        "FAILURE": (
            "bold red",
            "ENDING: FAILURE",
            "The resolution team arrived before the investigation concluded.\n"
            "HeliosCore security took control of the station.\n"
            "You were relieved of command under Corporate Security Protocol 7.\n"
            "The Airlock 7 incident was classified as equipment failure.\n"
            "Kai Reeves flew home on the corporate shuttle.\n\n"
            "[dim]Dr. Voss deserved better. You tried.[/dim]",
        ),
    }

    color, title, text = endings.get(ending, ("white", "ENDING", "The story concludes."))
    console.print()
    console.print(Panel(
        Text.from_markup(text),
        title=f"[bold {color}]{title}[/bold {color}]",
        border_style=color,
        padding=(2, 4),
    ))
    console.print()


# ── Helpers ────────────────────────────────────────────────────────────────────

import re as _re

def _extract_choices_from_narration(narration: str, state: dict) -> list[str]:
    """Parse the CHOICES section of narration into a plain list."""
    choices: list[str] = []
    match = _re.search(r'---\s*CHOICES\s*---(.*?)(?=---|$)', narration, _re.DOTALL)
    if match:
        raw = match.group(1).strip()
        for line in raw.splitlines():
            line = line.strip()
            line = _re.sub(r'\*\*([^*]+)\*\*', r'\1', line)
            line = _re.sub(r'^\d+\.\s*', '', line).strip()
            if line:
                choices.append(line)
    if state.get("oxygen_level", 100) <= 60 and not state.get("oxygen_repaired"):
        choices.append("fix oxygen — Zara bypasses the scrubber")
    return choices


# ── Main ───────────────────────────────────────────────────────────────────────

def main() -> None:
    # Setup telemetry
    if Config.has_telemetry():
        setup_telemetry(Config.APPLICATIONINSIGHTS_CONNECTION_STRING)

    # Validate credentials
    missing = Config.validate()
    if missing:
        console.print(Panel(
            f"[yellow]Missing environment variables:[/yellow]\n"
            + "\n".join(f"  • {m}" for m in missing)
            + "\n\n[dim]Copy .env.example to .env and fill in your Azure credentials.[/dim]",
            title="[red]⚠ CONFIGURATION REQUIRED[/red]",
            border_style="red",
        ))
        sys.exit(1)

    # Initialise services
    state_manager = StateManager()
    knowledge_base = KnowledgeBase()
    commander = CommanderAgent(state_manager, knowledge_base)

    # Intro and session selection
    print_intro()
    state = select_or_create_session(state_manager)

    console.print()
    console.print(Rule("[bold cyan]MISSION BEGINS[/bold cyan]", style="cyan"))
    console.print()

    # Opening scene
    opening_input = "begin investigation — I need to understand what happened to Dr. Voss"
    narration, state = commander.process_turn(opening_input, state)
    state_manager.save_session(state)
    last_choices = _extract_choices_from_narration(narration, state)
    print_scene_art(location_to_scene_key(state.get("location", "command_deck")), o2=state.get("oxygen_level", 82), kai_stage=state.get("kai_stage", 1))
    print_status(state)
    oxygen_alert(state)
    print_scene(narration, state)

    turns_this_session = 0
    last_choices: list[str] = []  # track last shown choices for number resolution

    # ── Main game loop ────────────────────────────────────────────────────────
    while True:
        player_input = get_player_input(state["id"])

        if player_input.lower() in ("quit", "exit", "q"):
            console.print("\n[dim]Saving session...[/dim]")
            state_manager.save_session(state)
            console.print("[cyan]Session saved. Tartarus awaits your return.[/cyan]")
            break

        if player_input.lower() in ("status", "state", "info"):
            print_status(state)
            continue

        # Oxygen repair command — available when O2 < 60%
        if player_input.lower() in ("fix oxygen", "repair oxygen", "repair scrubber", "fix scrubber", "restore oxygen"):
            o2_now = state.get("oxygen_level", 100)
            if o2_now >= 60:
                console.print("[dim]O\u2082 levels are within acceptable range. No repair needed.[/dim]")
            elif state.get("oxygen_repaired"):
                console.print(Panel(
                    "[yellow]The O\u2082 recycler has already been bypassed.\n"
                    "Emergency canisters are depleted.\n"
                    "[dim]You cannot stabilise oxygen a second time.[/dim][/yellow]",
                    border_style="yellow",
                ))
            else:
                frames = ["Pressurising line B-7...", "Bypassing faulty valve...", "Recycler online...", "O\u2082 stabilising..."]
                for f in frames:
                    console.print(f"  [cyan]{f}[/cyan]", end="\r")
                    time.sleep(0.5)
                console.print(" " * 50, end="\r")
                restored = 100
                state["oxygen_level"] = restored
                state["oxygen_repaired"] = True
                state["reactor_status"] = "degraded"  # reactor still faulty but scrubber bypassed
                state_manager.save_session(state)
                console.print(Panel(
                    f"[bold green]  ✓ O\u2082 RECYCLER FULLY STABILISED  [/bold green]\n\n"
                    f"  Zara Kim reroutes coolant through the emergency scrubber line.\n"
                    f"  Oxygen restored from [red]{o2_now}%[/red] → [bold green]{restored}%[/bold green].\n\n"
                    f"  [dim]O\u2082 is now stable and will not degrade further.\n"
                    f"  The crew is safe — focus on finding Dr. Voss's killer.[/dim]",
                    title="[bold green]REPAIR COMPLETE[/bold green]",
                    border_style="green",
                    padding=(1, 2),
                ))
            continue

        if player_input.lower() in ("evidence", "clues"):
            ev = state.get("evidence", [])
            if ev:
                console.print(Panel(
                    "\n".join(f"  • {e.replace('_', ' ').title()}" for e in ev),
                    title="[yellow]EVIDENCE LOG[/yellow]",
                    border_style="yellow",
                ))
            else:
                console.print("[dim]No evidence collected yet.[/dim]")
            continue

        if player_input.lower() == "help":
            console.print(Panel(
                "• Type any action naturally — explore, investigate, talk to crew\n"
                "• 'status' — view station status\n"
                "• 'evidence' — view collected evidence\n"
                "• 'fix oxygen' — repair O\u2082 scrubber when oxygen is below 60%\n"
                "• 'quit' — save and exit\n\n"
                "[dim]Examples:[/dim]\n"
                "  inspect the airlock 7 access log\n"
                "  talk to Patel about the post-mortem\n"
                "  investigate section C via EVA\n"
                "  confront Kai about his whereabouts\n"
                "  query ARIA about the incident window",
                title="[cyan]HELP[/cyan]",
                border_style="cyan",
            ))
            continue

        if not player_input:
            continue

        # Resolve number shortcut → full choice text
        resolved_input = player_input
        if player_input.strip().isdigit():
            idx = int(player_input.strip()) - 1
            if 0 <= idx < len(last_choices):
                resolved_input = last_choices[idx]
                console.print(f"[dim]  → {resolved_input}[/dim]")

        # Process confirmed irreversible action
        if resolved_input.lower().endswith(" confirm"):
            resolved_input = resolved_input[:-8].strip() + " __confirmed"

        # Process the turn
        try:
            _processing_animation()
            narration, state = commander.process_turn(resolved_input, state)
            state_manager.save_session(state)
            turns_this_session += 1
        except Exception as exc:
            console.print(f"[red]System error: {exc}[/red]")
            continue

        # Extract choices from narration for next turn number resolution
        last_choices = _extract_choices_from_narration(narration, state)

        # Character scene: check player input, then narration, then location
        art_key = (
            player_input_to_scene_key(resolved_input, state)
            or player_input_to_scene_key(narration[:800], state)
            or location_to_scene_key(state.get("location", "default"))
        )
        print_scene_art(art_key, o2=state.get("oxygen_level", 100), kai_stage=state.get("kai_stage", 1))
        print_status(state)
        oxygen_alert(state)
        print_scene(narration, state)

        # Check for game-ending conditions
        ending = check_game_end(state, turns_this_session)
        if ending:
            print_ending(ending, state)
            break

    console.print("\n[dim]Thank you for playing The Fractured Orbit.[/dim]\n")


if __name__ == "__main__":
    main()
