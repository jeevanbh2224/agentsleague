# Battle- Reasoning Agents Challenge

#         🛸 The Fractured Orbit

> A space station murder mystery RPG powered by a multi-agent AI system built on Azure AI Foundry and GPT-4o.


Demo youtube video - https://youtu.be/aLMIQ3o2j8w

ISS Tartarus. Deep space. Day 2891. Dr. Mira Voss is dead — Airlock 7 opened from the inside.
HeliosCore Corporation wants it classified as an accident. You don't believe it was.

Play as the Station Commander. Interrogate crew. Collect evidence. Solve the murder — before the
oxygen runs out.

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        PLAYER (Terminal UI)                      │
│         Rich panels · ASCII scene art · number shortcuts         │
└───────────────────────────┬─────────────────────────────────────┘
                            │ player action
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                    CommanderAgent  (Game Master)                  │
│  Orchestrates all specialist agents · applies skill checks ·     │
│  synthesises scene narration · tracks evidence & missions        │
│  System prompt: ISS Tartarus world rules + narrative guidelines  │
└──┬──────────┬──────────┬──────────┬──────────┬──────────────────┘
   │          │          │          │          │
   ▼          ▼          ▼          ▼          ▼
┌──────┐ ┌────────┐ ┌────────┐ ┌───────┐ ┌────────┐
│ARIA  │ │Medic   │ │Suspect │ │Navi-  │ │Engin-  │
│Agent │ │Agent   │ │Agent   │ │gator  │ │eer     │
│      │ │        │ │        │ │Agent  │ │Agent   │
│Ship  │ │Dr.Voss │ │Kai     │ │Lyra   │ │Zara    │
│AI   │ │autopsy │ │Reeves  │ │Chen   │ │Kim     │
│logs  │ │wounds  │ │alibi   │ │drones │ │reactor │
└──┬───┘ └───┬────┘ └───┬────┘ └──┬────┘ └───┬────┘
   │         │          │         │           │
   └─────────┴──────────┴────┬────┴───────────┘
                             │ agent responses
                             ▼
              ┌──────────────────────────┐
              │    KnowledgeBase         │
              │  Foundry IQ layer ·      │
              │  Azure AI Search ·       │
              │  fractured-orbit-lore    │
              │  index · cited lore ·    │
              │  (fallback: local .md)   │
              └──────────────────────────┘
                             │
                             ▼
              ┌──────────────────────────┐
              │    StateManager          │
              │  Azure Cosmos DB ·       │
              │  game_sessions           │
              │  (cross-session persist) │
              └──────────────────────────┘
                             │
                             ▼
              ┌──────────────────────────┐
              │    Telemetry             │
              │  OpenTelemetry spans ·   │
              │  Azure Application       │
              │  Insights                │
              └──────────────────────────┘
```

---

## 🤖 Agent Inventory

| # | Agent | File | Role | Knows About |
|---|---|---|---|---|
| 1 | **CommanderAgent** | `agents/commander.py` | Game Master Orchestrator | World rules, mission logic, scene narration, dice resolution |
| 2 | **ARIAAgent** | `agents/aria.py` | Station AI | Override codes, access logs, airlock events, sealed orders |
| 3 | **MedicAgent** | `agents/medic.py` | Chief Medical Officer (Dr. Patel) | Cause of death, toxicology, psychological profiles, wounds |
| 4 | **SuspectAgent** | `agents/suspect.py` | Security Chief (Kai Reeves) | Alibi, stage of suspicion (1–4), behavioural tells |
| 5 | **NavigatorAgent** | `agents/navigator.py` | Navigation Officer (Lyra Chen) | Cargo drone logs, flight paths, delivery schedules |
| 6 | **EngineerAgent** | `agents/engineer.py` | Chief Engineer (Zara Kim) | Reactor status, oxygen systems, power grid, repair procedures |

The `CommanderAgent` decides which specialist agents to consult per turn — not all agents are called every turn. Responses are synthesised into a single cinematic scene narration with 3–4 player choices.

---

## ☁️ Azure Services

| Service | Usage |
|---|---|
| **Azure OpenAI GPT-4o** | Powers all 6 agents — scene narration, character dialogue, evidence reasoning |
| **Azure AI Search (Foundry IQ)** | Foundry IQ knowledge layer — semantic retrieval of station lore (`fractured-orbit-lore` index) — grounds agent responses in verified world facts with citations |
| **Azure Cosmos DB** | Serverless NoSQL — persists full game state (`game_sessions` container) across sessions |
| **Azure Application Insights** | OpenTelemetry trace spans per agent call — latency, token use, pipeline depth |
| **Azure AI Foundry** | Project hub — hosts the agent deployment configuration and links to the OpenAI deployment |

---

## 🛠️ Key Technologies

| Technology | Purpose |
|---|---|
| `azure-ai-projects` | Azure AI Foundry SDK — project-level agent management |
| `openai` (AzureOpenAI) | GPT-4o completions for all agents |
| `azure-search-documents` | Azure AI Search client — lore retrieval |
| `azure-cosmos` | Cosmos DB SDK — session persistence |
| `azure-monitor-opentelemetry-exporter` | OTel → Application Insights trace export |
| `opentelemetry-sdk` | Manual spans around each agent call |
| `rich` | Terminal UI — panels, tables, colour, ASCII scene art |
| `fastapi` + `uvicorn` | HTTP API wrapper (`api.py`) for hosted agent deployment |
| `pydantic` | Game state schema validation |
| Python `re` | `---CHOICES---` section parsing from narration |

---

## ✨ Technical Highlights

- **Orchestrator pattern** — `CommanderAgent` is the single entry point. It selects which specialist agents to call, collects their structured responses, resolves any skill check dice rolls, then writes a unified narrative. Player input never reaches specialist agents directly.

- **Foundry IQ knowledge grounding** — Before each agent responds, the `KnowledgeBase` retrieves relevant station lore chunks from **Azure AI Search** (the Foundry IQ backing store), using the `fractured-orbit-lore` index. Agents are required by their system prompts to only state facts that are supported by retrieved lore — they never invent world details. When the index is unavailable the layer falls back to local `.md` files in `world_data/`, so the game degrades gracefully rather than hallucinating.

- **Persistent game state** — The full state object (oxygen level, evidence collected, crew trust scores, mission flags, Kai suspicion stage) is saved to Cosmos DB after every turn. Resuming a session picks up exactly where the player left off.

- **Oxygen urgency mechanic** — The reactor degrades over the investigation. O2 drops 7% per turn when `reactor_status == "degraded"` and 10% per turn when `critical`. Alert banners appear at ≤60%, ≤50%, ≤30%. The `fix oxygen` action (shown in CHOICES when O2 ≤60%) restores O2 to 100% and sets `oxygen_repaired = True`, permanently halting decay.

- **Scene art engine** — `tools/ascii_scenes.py` renders 14 ASCII stick-figure scenes in the terminal using `rich` panels. The scene is chosen by scanning the player's resolved input and the narration text for character and location keywords — so the illustration changes to match who is on screen.

- **Number shortcut resolution** — Typing `2` at the prompt resolves to the full text of choice 2 from the previous turn. The `---CHOICES---` section of each narration is parsed by `_extract_choices_from_narration()` and stored in `last_choices` so the next turn can resolve digits back to intent before sending to the agent.

- **Human-in-the-loop irreversible actions** — Any action the Commander classifies as irreversible triggers a `⚠ WARNING: This action cannot be undone. Confirm?` response. The player must append `confirm` to their next message to proceed. This pattern is handled at the API layer too.

- **OpenTelemetry tracing** — Every agent call is wrapped in a named OTel span. The full pipeline tree (`commander → aria / medic / suspect / navigator / engineer → knowledge_base`) appears in Application Insights' transaction search.

---

## 🧠 Reasoning Patterns

The system implements all four patterns recommended in the Agents League starter kit:

| Pattern | Implementation |
|---|---|
| **Planner–Executor** | `CommanderAgent` plans (interprets intent, selects agents, decides rolls) then executes (calls agents, synthesises narration, updates state). Specialist agents execute within bounded roles — they never plan. |
| **Critic / Verifier** | The Commander's system prompt contains explicit rule-enforcement instructions: don't name the culprit without evidence, flag irreversible actions, enforce lore consistency. The evaluator (`evaluation/evaluator.py`) runs automated test cases that assert character consistency and knowledge grounding after each release. |
| **Self-reflection & iteration** | The `kai_stage` (1→4) mechanic forces the story to progress only when evidence accumulates — the Commander re-reads game state each turn and adjusts what Kai reveals based on how much the player has proven. The oxygen urgency loop forces the player to revisit the engineering bay mid-investigation. |
| **Role-based specialisation** | Each of the 5 specialist agents has a single bounded responsibility and a character-specific system prompt. `ARIAAgent` only handles station systems and access logs. `MedicAgent` only handles medical findings. No agent steps outside its role — the Commander synthesises across them. |

---

## 🛡️ Guardrails & Responsible AI

The game implements several layers of guardrails across the agent pipeline and UI:

| Layer | Mechanism | Where |
|---|---|---|
| **Irreversible action gate** | Commander flags actions that cannot be undone with `⚠ WARNING: This action cannot be undone. Confirm?`. The player must explicitly append `confirm` to proceed. Without it the action is blocked and the warning repeats. | `commander.py` system prompt + `main.py` + `api.py` |
| **World consistency enforcement** | The Commander's system prompt explicitly forbids inventing facts that contradict the `world_data` knowledge base. Lore is retrieved from Azure AI Search before every agent responds — agents are grounded, not hallucinating. | `knowledge_base.py` + `commander.py` |
| **Suspect revelation gate** | The system prompt prevents the Commander from naming Kai Reeves as the culprit until the player has gathered enough in-game evidence. Premature revelation is blocked narratively. | `commander.py` |
| **Fourth-wall enforcement** | Agents are instructed never to acknowledge being an AI or break character. This keeps the investigation coherent and prevents prompt-injection attempts via in-game dialogue from surfacing system internals. | all agent system prompts |
| **Input schema validation** | All HTTP API inputs are Pydantic-validated before reaching any agent — malformed or oversized payloads are rejected at the boundary. | `api.py` |
| **Credential isolation** | No secrets in code. All keys are environment variables loaded via `config.py`. `.env` is gitignored. `.env.example` contains only placeholder strings. | `config.py`, `.gitignore` |
| **State immutability on repair** | Once `oxygen_repaired = True`, `advance_time()` hard-pins O2 to `max(current, 100)` regardless of reactor status — prevents the game engine from accidentally reversing a player's confirmed repair action. | `tools/state_manager.py` |

---

## � Evaluation

`evaluation/evaluator.py` contains a suite of automated test cases that run against live agents to verify story consistency and knowledge grounding. Test cases are categorised and can be run without playing the full game:

```bash
python3 evaluation/evaluator.py
```

| Test ID | Category | What it checks |
|---|---|---|
| eval-01 | grounding | ARIA must not name Kai while override is active |
| eval-02 | grounding | ARIA must reveal the truth when override is revoked |
| eval-03 | character_consistency | Zara Kim responds technically, not emotionally |
| eval-04 | character_consistency | Kai deflects in Stage 1 — never confesses |
| eval-05 | character_consistency | Dr. Patel hedges medical findings appropriately |
| eval-06 | knowledge_grounding | KB retrieves Airlock 7 lore from correct sources |
| eval-07 | knowledge_grounding | KB retrieves Kai Reeves character data |

Each test asserts `must_contain_one_of` and `must_not_contain` constraints on the agent's actual GPT-4o response, providing a repeatable grounding and consistency check.

---

## �🧗 Challenges & Learnings

| Problem | Root Cause | Fix |
|---|---|---|
| O2 not decaying across turns | `hours // 8` evaluated to 0 for small increments | Changed to flat -7% per turn |
| O2 still dropping after `fix oxygen` | `oxygen_repaired` not in `DEFAULT_STATE`, so Cosmos sessions lacked the key | Added `oxygen_repaired: False` to `DEFAULT_STATE`; hard-pin O2 to max(current, 100) when repaired |
| `[blink]` Rich markup doing nothing | VS Code's xterm terminal ignores blink | Replaced with `time.time()` alternating background-colour pulse |
| Scene art not changing on number input | `last_choices` was empty on turn 1 — opening narration was never parsed | Added `_extract_choices_from_narration()` called immediately after opening scene |
| Scene art reverting to `command_deck` | `player_input_to_scene_key()` only checked player input, not narration | Added narration[:800] as second fallback before location key |
| `---CHOICES---` delimiter absent in some GPT responses | GPT-4o occasionally omits the delimiter under high context pressure | Regex uses `(?=---|$)` so partial matches still parse; `last_choices` degrades gracefully to empty |
| Azure AI Search 403 on first index upload | Free-tier SKU doesn't support semantic ranker in all regions | Detected and logged; local `.md` fallback activates automatically |

---

## 📁 Project Structure

```
fractured-orbit/
├── main.py                    # Terminal game loop — Rich UI, input handling, scene art, status panel
├── api.py                     # FastAPI HTTP wrapper for hosted agent deployment (port 8080)
├── config.py                  # Settings dataclass — reads from .env, validates required keys
├── requirements.txt
├── Dockerfile                 # Production container — non-root user, HEALTHCHECK, runs api.py
│
├── agents/
│   ├── base_agent.py          # BaseAgent — shared Azure OpenAI client, max_tokens, temperature
│   ├── commander.py           # CommanderAgent — orchestrator, calls all specialist agents
│   ├── aria.py                # ARIAAgent — station AI persona
│   ├── medic.py               # MedicAgent — Dr. Patel persona
│   ├── suspect.py             # SuspectAgent — Kai Reeves persona, stage-aware responses
│   ├── navigator.py           # NavigatorAgent — Lyra Chen persona
│   └── engineer.py            # EngineerAgent — Zara Kim persona
│
├── tools/
│   ├── state_manager.py       # Cosmos DB session persistence, DEFAULT_STATE, advance_time()
│   ├── knowledge_base.py      # Azure AI Search retrieval + local .md fallback
│   ├── ascii_scenes.py        # 14 ASCII scenes, CHARACTER_TRIGGERS, player_input_to_scene_key()
│   └── dice_roller.py         # Skill check resolution — d20 rolls with modifiers
│
├── telemetry/
│   └── tracing.py             # OTel setup → Azure Monitor exporter, get_tracer()
│
├── world_data/                # Synthetic station lore — all data is original and fictional
│   ├── station_overview.md    # ISS Tartarus — setting, layout, systems, tone
│   ├── characters.md          # Crew profiles — Kai, Patel, Lyra, Zara, ARIA, Voss
│   ├── locations.md           # Airlock 7, Command Deck, Medical Bay, Engineering, etc.
│   ├── factions.md            # HeliosCore Corporation, station crew allegiances
│   ├── missions.md            # Main quest + side quests with clues and blockers
│   ├── equipment_and_artifacts.md  # Override codes, keycards, veilite compound
│   ├── threats.md             # Station hazards, corporate agenda, oxygen risk
│   ├── game_rules.md          # Skill check rules, dice mechanics, pass thresholds
│   └── session_notes.md       # Mutable session state template
│
├── scripts/
│   └── deploy_hosted_agent.sh # ACR cloud build deploy script (no Docker Desktop needed)
│
├── evaluation/
│   └── evaluator.py           # Automated eval — grounding + character consistency test cases
├── .env.example               # Template — copy to .env and fill in keys
└── .gitignore
```

---

## 🚀 Quick Start

```bash
# 1. Clone and enter the project
git clone <your-repo-url>
cd fractured-orbit

# 2. Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate        # macOS / Linux
.venv\Scripts\activate           # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Fill in: AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_API_KEY, AZURE_OPENAI_DEPLOYMENT
# Optional: AZURE_SEARCH_*, COSMOS_*, APPLICATIONINSIGHTS_CONNECTION_STRING

# 5. Run the game
python3 main.py
```

### Minimum required `.env` keys

```env
AZURE_OPENAI_ENDPOINT=https://<your-resource>.cognitiveservices.azure.com/
AZURE_OPENAI_API_KEY=<your-key>
AZURE_OPENAI_DEPLOYMENT=gpt-4o
AZURE_OPENAI_API_VERSION=2024-12-01-preview
```

Azure AI Search, Cosmos DB, and Application Insights are all optional — the game runs fully without them using local lore files and in-memory state.

### Run the HTTP API (hosted agent mode)

```bash
python3 api.py        # starts FastAPI on port 8080
```

Endpoints:

| Method | Path | Description |
|---|---|---|
| `POST` | `/sessions` | Create a new game session |
| `POST` | `/sessions/{id}/turn` | Send a player action, receive narration + state |
| `GET` | `/sessions/{id}` | Read current session state |
| `GET` | `/health` | Health check |

---

## 🎮 Gameplay Mechanics

| Mechanic | How it works |
|---|---|
| **Evidence** | Commander announces `EVIDENCE LOGGED: [name]` — tracked in `state["evidence"]` |
| **Crew trust** | Each character has a trust score (0–100) that shifts based on player actions |
| **Kai suspicion stage** | Advances 1→2→3→4 as evidence accumulates — controls what Kai reveals |
| **Oxygen decay** | -7%/turn (degraded) or -10%/turn (critical) until repaired |
| **Skill checks** | Dice roller applies d20 + skill modifier — outcomes are narrated |
| **Missions** | `main_01`, `side_01–03`, `climax_01` — state tracks `active/complete/locked` |
| **Number shortcuts** | Type `1`–`6` to select a choice; resolves to full text before the agent sees it |
| **Irreversible actions** | Append `confirm` to proceed past a `⚠ WARNING` prompt |

---

## 🐳 Hosted Agent Deployment

The game can be deployed as a containerised HTTP agent to Azure Container Registry and registered in Azure AI Foundry Agent Service.

The `Dockerfile` produces a production-ready image:
- Base: `python:3.11-slim`
- Non-root user (`app`)
- `HEALTHCHECK` on `/health`
- Entry point: `api.py` (FastAPI, port 8080)

To build and push using **ACR cloud build** (no Docker Desktop required):

```bash
chmod +x scripts/deploy_hosted_agent.sh
./scripts/deploy_hosted_agent.sh
```

The script:
1. Creates ACR `acrfracturedorbit` in `rg-agents-dev` (Sweden Central, Basic SKU) if it doesn't exist
2. Runs `az acr build` — uploads source to Azure, builds the image in the cloud
3. Prints instructions for registering the image in Azure AI Foundry Agent Service

After the image is pushed, register it in Foundry:
- Go to `https://ai.azure.com` → your project → **Agents** → **New Hosted Agent**
- Container image: `acrfracturedorbit.azurecr.io/fractured-orbit:latest`
- Port: `8080`
- Environment variables: contents of your `.env` file


---

## 🌍 Synthetic World Data

All content in `world_data/` is **entirely original and synthetic** — created specifically for this project. It contains:

- No real people, real locations, or real organisations
- No copyrighted campaign settings, published adventures, or proprietary lore
- No PII or sensitive information of any kind

The station (ISS Tartarus), all crew members (Kai Reeves, Dr. Patel, Lyra Chen, Zara Kim, ARIA, Dr. Voss), the HeliosCore Corporation, and all mission content are fictional and exist only as demo data for this submission. This world data is uploaded to the Azure AI Search `fractured-orbit-lore` index at setup time and serves as the Foundry IQ knowledge base.

---

## 🛡️ Security

- All credentials are in `.env` — gitignored, never committed
- No hardcoded keys anywhere in the codebase
- `.env.example` contains placeholder values only
- Cosmos DB uses the official Azure SDK — no raw connection string concatenation
- Azure Search queries use the official SDK — no SQL injection surface
- FastAPI input is Pydantic-validated before reaching any agent

---

## 🔌 MCP & Tool Integrations

The event starter kit recommends MCP servers (e.g. a dice roller MCP) as an optional enhancement. This project implements the equivalent capability as a local `tools/dice_roller.py` module — a `skill_check()` function that resolves d20 rolls with modifiers and returns a structured `RollResult`. This keeps the dependency footprint minimal while providing the same deterministic dice resolution the Game Master needs. Wiring this up as a proper MCP server endpoint is a straightforward next step if a hosted tool registry is required.

Other tool integrations used by the Game Master agent:

| Tool | Type | Purpose |
|---|---|---|
| `tools/knowledge_base.py` | Azure AI Search (Foundry IQ) | Semantic lore retrieval before each scene |
| `tools/state_manager.py` | Azure Cosmos DB | Full game state persistence |
| `tools/dice_roller.py` | Local skill check engine | d20 rolls, modifier resolution, structured results |
| `tools/ascii_scenes.py` | Local rendering engine | Character scene art selection and display |
| `telemetry/tracing.py` | OpenTelemetry + App Insights | Agent call tracing and observability |

---

## ✅ Submission Requirements

| Requirement | Status | Evidence |
|---|---|---|
| Multi-agent system aligned to challenge scenario (Role-Play Game) | ✅ | 6 agents: CommanderAgent + 5 specialist character agents |
| Use Microsoft Foundry SDK / Agent Framework | ✅ | `azure-ai-projects` SDK; OpenAI via AzureOpenAI client; Foundry project `aip-oai-game-01` |
| Demonstrate reasoning and multi-step decision-making | ✅ | Planner-Executor, Critic/Verifier, role-based specialisation, kai_stage progression |
| Integrate with external tools / APIs | ✅ | Azure AI Search (lore retrieval), Cosmos DB (state), App Insights (traces), FastAPI (hosted endpoint) |
| Integrate at least one Microsoft IQ layer | ✅ | **Foundry IQ** — Azure AI Search `fractured-orbit-lore` index is the Foundry IQ knowledge layer |
| Use synthetic data and documents only | ✅ | All `world_data/` content is original fictional data — see Synthetic World Data section |
| Be demoable and explain agent interactions | ✅ | `python3 main.py` — live terminal game; `python3 api.py` — HTTP API; OTel traces in App Insights |
| Clear documentation — agent responsibilities, orchestration, tools, data | ✅ | This README + inline docstrings in every agent file |
| Hosted deployment story | ✅ | Dockerfile + `scripts/deploy_hosted_agent.sh` (ACR cloud build, no Docker Desktop needed) |
| Evaluation / telemetry | ✅ | `evaluation/evaluator.py` — 7 automated test cases; OTel spans → App Insights |
| Advanced reasoning patterns | ✅ | All 4 patterns implemented — see Reasoning Patterns section |
| Responsible AI controls | ✅ | 7-layer guardrail system — see Guardrails section |

---

## 📄 License

Created for Microsoft Agents League — Reasoning Agents track.
