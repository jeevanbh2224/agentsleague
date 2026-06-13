# Equipment and Artifacts: ISS Tartarus
tags: [items, equipment, artifacts, tools, evidence]
related_entities: [Kai Reeves, ARIA, Voss, HeliosCore, Axiom Industries]

---

# Item: Commander's Sealed Orders
id: item-sealed-orders
type: document — classified
location: Command Deck — Commander's biometric safe
access: Commander biometrics only

Description: A HeliosCore corporate directive transmitted encrypted 48 hours before the incident. The seal is intact — it has not been opened. Opening it requires a conscious choice by the Commander.

Contents (revealed on opening):
"CONFIDENTIAL — HELIOSCORE EXECUTIVE DIRECTIVE 9-T. Commander, you are instructed to classify the Section C incident as an accidental airlock failure resulting from equipment malfunction. File standard Form 7-A. Do not conduct crew interviews. Do not retain physical evidence. A corporate review team will arrive within 21 days. Compliance is mandatory under your contract. Non-compliance will be treated as breach of corporate security protocol. — HeliosCore Station Operations, Director V. Harlan."

Game effect: Reading the orders adds the "Corporate Pressure" status to the session — Kai becomes aware the Commander has opened them (ARIA reports it to him automatically under the override). Kai's trust meter drops 15 points as he realises the Commander may not comply.

---

# Item: Encrypted Comms Device
id: item-comms-device
type: evidence — critical
location: Cargo Hold — hidden panel, Section E

Description: A non-standard personal comms device. Not registered to any crew member. Military-grade encryption. About the size of a thick deck of cards. Warm to the touch — it has been transmitting recently.

Contents (after decryption, requires Lyra + DC 16):
Axiom Industries contact: "R — samples received. Payment confirmed. Final step: silence the botanist. Confirmation required within 48 hours. Deny all contact."

Kai's reply (sent 3 days ago): "Confirmed. Understood. It's done."

Game effect: This is the decisive piece of evidence. Confronting Kai with this device triggers the final confrontation scene regardless of other evidence gathered.

---

# Item: Dr. Voss's Lab Terminal Data
id: item-voss-terminal
type: evidence — key
location: Section C Lab — requires EVA suit to retrieve
access: Standard crew login (Patel has her credentials)

Description: Voss's personal research terminal. Still powered. Her mineral analysis files, personal journal, and one unsent message are intact.

Key entries:
- Research log: "Sample V-047 is not deuterium. The crystalline lattice interferes with my sensor array — I've had to recalibrate three times. HeliosCore is lying about what we're extracting."
- Journal entry (2 days before death): "I showed Kai the analysis. He went pale. He said he'd help me get the data out. He said he knew someone. I believe him. I probably shouldn't."
- Unsent message: Addressed to an Axiom Industries public comms channel — Voss was trying to contact them independently, unaware Kai already had.

Game effect: Provides strong narrative evidence and unlocks the Veilite mission thread.

---

# Item: EVA Suit (x2 operational)
id: item-eva-suit
type: equipment
location: Section B equipment locker

Description: Standard deep-space EVA suits. 4-hour oxygen supply. Magnetic boots. Integrated comms. Required to access Section C.

Game effect: Enables Section C investigation. Engineering check DC 10 to safely traverse the breach zone.

---

# Item: Station Master Override Key
id: item-master-override
type: tool — critical
location: Command Deck — Commander's direct access

Description: The physical and digital key that gives the Commander master access to all station systems — including ARIA's override management.

Game effect: Required to revoke the corporate override code on ARIA. Cannot be used until the override code is identified (Mission side-02 step 3). Using it is an irreversible action — requires human-in-the-loop confirmation.

---

# Item: Security Station 2 Access Log
id: item-access-log
type: evidence — medium
location: Section A — accessible via Commander console

Description: Station security logs showing which crew member's badge accessed which terminal at which time. Normally routine. For the incident window, it shows the override query to Airlock 7 at 01:57 originated from Security Station 2 — Kai Reeves's assigned workstation.

Game effect: Directly places Kai at the relevant terminal. Combined with other evidence, builds the case for confrontation.

---

# Item: Veilite Sample (Secured)
id: item-veilite-sample
type: artifact — critical
location: Section C lab — EVA required, then secured by Commander

Description: A thumb-sized crystalline fragment, deep violet with an internal luminescence. Does not match any catalogued mineral. When brought near standard sensor arrays, readings become unstable. Beautiful and deeply unsettling.

Properties: Interferes with sensor arrays within 2 metres. May interfere with ARIA's subsystems if brought near the server room (Game Master discretion — can be used creatively).

Game effect: The physical proof of HeliosCore's secret operation. Central to the Veilite Question mission. Holding it triggers commentary from all character agents.

---

# Item: Kai's Maintenance Badge Duplicate
id: item-badge-duplicate
type: evidence — supporting
location: Kai's quarters — requires search with DC 14 persuasion to gain access or DC 16 stealth to enter without consent

Description: A duplicate maintenance badge programmed with Dr. Voss's access credentials. Kai created it to access Junction B-7 without using his own credentials.

Game effect: Connects Kai to the B-7 sabotage. Combined with the power drain device (Engineering check DC 13 to identify), proves pre-meditated sabotage.
