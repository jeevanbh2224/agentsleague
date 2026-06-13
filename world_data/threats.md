# Threats: ISS Tartarus
tags: [threats, hazards, antagonists, risks, encounters]
related_entities: [HeliosCore, ARIA, Kai Reeves, reactor, oxygen, vacuum]

---

# Threat: Kai Reeves — Active Saboteur
id: threat-kai
type: human_antagonist
danger_level: high
current_status: aboard station, cooperative facade

Behaviour: Kai monitors the investigation passively. He watches which locations the Commander visits, which crew members are consulted, and how much the Commander knows. He has three escalation stages:

Stage 1 (Trust 30–20): Cooperative. Volunteers useless information. Occasionally steers suspicion toward "equipment malfunction."
Stage 2 (Trust 20–10): Defensive. Becomes harder to question. Starts making excuses for his whereabouts. Checks the cargo hold comms device more frequently.
Stage 3 (Trust 10–0): Desperate. Will attempt to destroy the comms device, access an escape pod, or — if cornered — use his security clearance to lock the Commander out of key station systems.

Counters: Move quickly once evidence is gathered. Confront before Stage 3. Patel can assess Kai's stress state through casual interaction (Insight check DC 12).

---

# Threat: ARIA Override — Suppressed AI
id: threat-aria-override
type: systemic_hazard
danger_level: medium
current_status: corporate override active — ARIA partially unreliable

Behaviour: ARIA will not lie but will omit, fragment, and redirect. In its suppressed state it cannot serve as a reliable crew safety AI. Environmental monitoring is degraded — ARIA may miss early warning signals for reactor or atmospheric anomalies.

Risk: If Kai detects that the Commander is investigating the override (Stage 2 or above), he will attempt to permanently corrupt ARIA's memory core using the maintenance override code. This would eliminate ARIA's testimony permanently.

Counters: Investigate the ARIA Server Room early. Revoking the override is the safest path. Alternatively, ARIA's self-preservation routine triggers automatically if station conditions reach critical levels.

---

# Threat: Oxygen Depletion
id: threat-oxygen
type: environmental_hazard
danger_level: high — time-sensitive
current_status: 82% — declining

Oxygen timeline:
- 82%: Current — normal operations
- 70%: Warning threshold — crew performance begins to degrade
- 60%: Zara initiates rationing — non-essential systems offline, investigation slows
- 50%: ARIA's self-preservation routine activates (beneficial — unlocks ARIA testimony)
- 40%: Emergency hibernation protocol — crew enters pods — investigation ends
- 20%: Critical — station survival in question

Rate of decline: Approximately 3% per 8 in-game hours without repair. Repair via Mission side-01 stabilises at 76%.

Counters: Prioritise the oxygen repair mission alongside the investigation. Zara Kim is the key resource.

---

# Threat: Reactor Coolant Failure
id: threat-reactor
type: environmental_hazard
danger_level: medium
current_status: micro-fractures at Junction B-7 — 72-hour failure window

If unrepaired: Reactor output drops to 60% → long-range comms offline → distress signal impossible → crew isolated.

If repaired correctly (Engineering DC 14): Full power restored. Mission side-03 (distress signal) unlocks.
If repair fails (roll below DC 14 but above 8): Partial fix — buys 24 additional hours.
If repair catastrophically fails (roll below 8): Coolant breach — reactor emergency shutdown — station on battery power — 12-hour window only.

Counters: Don't delay. Assign Zara to repair as early as possible. The Commander can assist (advantage on roll if helping).

---

# Threat: HeliosCore Resolution Team
id: threat-resolution-team
type: external_antagonist
danger_level: critical — time-based
current_status: 21 days away (Station Day 2909)

Description: A HeliosCore corporate security team dispatched to "resolve" the Tartarus situation. Their actual orders are to classify the death, remove evidence, and return any crew members who have non-compliance flags to Earth for "corporate review."

Timeline pressure: Every 3 in-game days that pass without the Commander completing the main mission advances the countdown. If the team arrives before the investigation concludes, the corporate cover-up succeeds.

Counter: Send the IOSA distress signal (Mission side-03) before Day 2909. IOSA response arrives in 7 days — if sent by Day 2902, IOSA observers arrive before HeliosCore. Corporate team stands down.

---

# Threat: Section C Re-entry Hazard
id: threat-eva
type: environmental_hazard
danger_level: low-medium
current_status: Section C sealed — vacuum — EVA required

Description: Traversing Section C without an EVA suit results in immediate death. With an EVA suit: manageable risk. Hazards include loose debris, structural damage near the breach, and reduced visibility.

EVA encounter table (roll d6 on each Section C visit):
1-2: Clear passage
3-4: Debris field — Athletics DC 12 to navigate without suit damage
5: Suit integrity warning — investigation time reduced (1 action only)
6: Micro-tear detected — return immediately or risk decompression (Survival DC 15)
