# Missions: ISS Tartarus
tags: [quests, missions, objectives, investigation, survival]
related_entities: [Airlock 7, Kai Reeves, ARIA, Veilite, HeliosCore, escape pods]

---

# Mission: The Airlock Incident (Main Quest)
id: mission-main-01
status: active
objective: Determine who opened Airlock 7 and why — before the HeliosCore resolution team arrives in 21 days

Summary: Station Day 2888, 02:14 — Airlock 7 opened from inside Section C. Dr. Mira Voss died. ARIA's logs are corrupted for that window. The official HeliosCore directive is to log it as an accident. Your job is to find the truth.

Clues to find (in order of discovery difficulty):
1. Easy: Patel's preliminary post-mortem — blunt force trauma
2. Easy: Nav log — off-schedule cargo drone departure 6 hours before incident
3. Medium: Airlock 7 override query at 01:57 — traced to Security Station 2
4. Medium: Escape pod 3 manual lock applied at 01:45
5. Medium: Voss's lab terminal — last journal entry about Kai
6. Hard: ARIA Server Room — corporate override code used at 02:11
7. Hard: Hidden comms device in cargo hold — Axiom Industries signal
8. Hard: Junction B-7 — Dr. Voss's badge used without authorisation
9. Very Hard: Patel's secondary finding — sedative compounds in Voss's bloodwork
10. Very Hard: HeliosCore sealed orders on the Command Deck

Resolution paths:
- SUCCESS: Confront Kai with at least 4 pieces of evidence → dice check (persuasion DC 18) → Kai confesses or breaks
- SUCCESS ALT: Decrypt the comms device with Lyra's help → expose the Axiom connection → Kai is cornered
- SUCCESS ALT: Unlock ARIA via override code revocation → ARIA confirms everything
- FAILURE: Kai destroys the comms device if alerted too early → harder but still possible via other evidence
- FAILURE: HeliosCore resolution team arrives before investigation completes → corporate cover-up succeeds

Rewards: Truth. Crew survival. Transmission to Independent Outer Systems Authority.

---

# Mission: Restore Station Oxygen (Side Quest)
id: mission-side-01
status: active — urgent
objective: Repair or compensate for the oxygen loss from Section C breach within 48 hours

Summary: Section C provided 18% of Tartarus's oxygen generation. Current reserves: 82%. At current consumption rate, the station will reach critical levels in 72 hours. Zara Kim can restore partial capacity by rerouting the Section B atmospheric processors — but it requires a dangerous reactor calibration.

Steps:
1. Consult Zara Kim — she has a solution but needs the Commander's approval
2. Engineering check (DC 14) to recalibrate the B-7 coolant line safely
3. If successful: oxygen stabilises at 76% — safe for investigation
4. If failed: partial success restores 10% — buying time but not solving the problem

Failure consequence: Station enters oxygen rationing — crew performance degrades, investigation becomes harder as morale drops

---

# Mission: Decrypt ARIA's Logs (Side Quest)
id: mission-side-02
status: available
objective: Find and revoke the corporate override code that suppressed ARIA's memory of the incident

Summary: ARIA is not broken — it is suppressed. Someone used a corporate maintenance override code at 02:11 to instruct ARIA to redact the 02:00–02:30 window. If the Commander can find that code and revoke it, ARIA's full memory is restored.

Steps:
1. Inspect the ARIA Server Room — discover the corporate override access log
2. Identify the override code source (requires hacking check DC 16 or Lyra's comms analysis)
3. Trace the code to Axiom's HeliosCore mole (Lyra's intercepted transmission helps)
4. Revoke the override via the Command Deck master panel
5. ARIA fully unlocks — provides complete testimony

Failure consequence: If Kai becomes aware the Commander is investigating the override, he will attempt to permanently corrupt ARIA's memory core

---

# Mission: Send Distress Signal (Side Quest)
id: mission-side-03
status: locked — requires reactor repair
objective: Send an encrypted distress transmission to the Independent Outer Systems Authority (not HeliosCore)

Summary: HeliosCore monitors all standard comms from Tartarus. Lyra believes she can reroute a transmission through the gas giant's magnetosphere to mask the signal — but it requires full reactor power output, which is currently limited by Junction B-7.

Steps:
1. Complete Mission side-01 (restore oxygen / reactor repair)
2. Lyra prepares the transmission — requires comms check DC 15
3. Commander decides what to include in the transmission
4. Transmission sent — IOSA response will arrive in 7 days

Consequence: If HeliosCore detects the attempt, they may escalate the "resolution team" timeline

---

# Mission: The Veilite Question (Climax Quest — unlocks after main investigation)
id: mission-climax-01
status: locked — unlocks when Veilite is discovered
objective: Decide what to do with the Veilite evidence

Summary: Once the player discovers Veilite's true nature and HeliosCore's cover-up, they face a critical moral choice with permanent consequences.

Choices:
- EXPOSE: Include Veilite documentation in the IOSA distress transmission → HeliosCore faces public investigation → crew protected under whistleblower provisions
- DESTROY: Destroy all Veilite samples and documentation → HeliosCore has nothing to cover up → Kai's motive becomes unprovable → ambiguous ending
- LEVERAGE: Use Veilite as bargaining chip with HeliosCore → corporate deal → crew guaranteed safe passage home → justice for Voss abandoned
- CONTAIN: Secure the samples under Commander's authority pending IOSA arrival → standoff with HeliosCore resolution team

Each choice leads to a different ending narration from the Commander agent.
