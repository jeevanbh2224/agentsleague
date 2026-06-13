"""
Image generation for The Fractured Orbit.
Uses Pollinations.ai — free, no API key required.
Saves output to generated/latest.png for the browser scene panel.
"""
from __future__ import annotations

import threading
import urllib.parse
import urllib.request
from pathlib import Path

# Where generated images are saved
GENERATED_DIR = Path(__file__).parent.parent / "generated"
LATEST_PATH = GENERATED_DIR / "latest.png"
HISTORY_DIR = GENERATED_DIR / "history"

SCENE_PROMPTS: dict[str, str] = {
    "default": (
        "interior of a dark deteriorating deep-space station corridor, "
        "flickering emergency lighting, exposed conduits, floating debris, "
        "cinematic sci-fi concept art, ultra-detailed"
    ),
    "command_deck": (
        "ISS Tartarus command bridge, holographic displays showing red alerts, "
        "cracked viewport revealing stars, emergency lighting, abandoned coffee cup floating, "
        "cinematic sci-fi concept art, moody atmosphere"
    ),
    "airlock_7": (
        "deep-space station airlock chamber, blast marks on the door, "
        "cold blue emergency lighting, crime scene tape floating in zero-g, "
        "cinematic sci-fi noir, photorealistic"
    ),
    "medical_bay": (
        "futuristic space station medical bay, sterile white surfaces stained red, "
        "holographic autopsy display, dim lighting, unsettling silence, "
        "cinematic sci-fi concept art"
    ),
    "engineering_bay": (
        "deep-space station engineering core, damaged reactor junction B-7, "
        "sparking conduits, toxic coolant leak glowing green, "
        "technician tools floating abandoned, cinematic sci-fi"
    ),
    "cargo_hold": (
        "space station cargo hold, crates stamped HeliosCore, "
        "hidden smuggling compartment pried open, encrypted comms device on crate, "
        "shadowy cinematic lighting, sci-fi thriller"
    ),
    "aria_server_room": (
        "space station AI server room, glowing blue neural network racks, "
        "one rack visibly corrupted and dark, warning lights flashing, "
        "sinister atmosphere, cinematic sci-fi"
    ),
    "confrontation": (
        "tense confrontation scene inside a dark space station corridor, "
        "two silhouettes facing each other, red emergency lighting, "
        "dramatic shadows, cinematic sci-fi thriller"
    ),
    "oxygen_critical": (
        "space station interior, red emergency lights pulsing, "
        "oxygen warning displays everywhere, crew member in distress, "
        "atmosphere of imminent danger, cinematic sci-fi"
    ),
    "ending_truth": (
        "space station commander holding encrypted evidence device, "
        "stars visible through viewport, justice achieved, "
        "hopeful blue lighting, cinematic sci-fi"
    ),
    "ending_failure": (
        "space station commander alone in dark corridor, "
        "corporate shuttle departing through viewport, "
        "defeated atmosphere, cold blue-grey lighting, cinematic sci-fi noir"
    ),
}

LOCATION_TO_SCENE: dict[str, str] = {
    "command deck": "command_deck",
    "airlock 7": "airlock_7",
    "airlock": "airlock_7",
    "medical bay": "medical_bay",
    "engineering bay": "engineering_bay",
    "cargo hold": "cargo_hold",
    "aria server room": "aria_server_room",
    "server room": "aria_server_room",
}


def _build_url(scene_key: str) -> str:
    prompt = (
        f"cinematic sci-fi illustration, {SCENE_PROMPTS.get(scene_key, SCENE_PROMPTS['default'])}, "
        "no text, no watermarks, dark dramatic lighting, widescreen 16:9, digital painting"
    )
    encoded = urllib.parse.quote(prompt)
    return f"https://image.pollinations.ai/prompt/{encoded}?width=1792&height=1024&nologo=true&seed=42"


def _generate_and_save(scene_key: str) -> None:
    """Blocking call — run in a thread."""
    try:
        GENERATED_DIR.mkdir(exist_ok=True)
        HISTORY_DIR.mkdir(exist_ok=True)

        url = _build_url(scene_key)
        req = urllib.request.Request(url, headers={"User-Agent": "FracturedOrbit/1.0"})
        with urllib.request.urlopen(req, timeout=30) as response:
            image_data = response.read()

        LATEST_PATH.write_bytes(image_data)

        import shutil, time as _time
        ts = int(_time.time())
        shutil.copy(str(LATEST_PATH), str(HISTORY_DIR / f"{ts}_{scene_key}.png"))

    except Exception:
        pass


def generate_scene_image(scene_key: str) -> None:
    """Trigger image generation in a background thread. Non-blocking."""
    t = threading.Thread(target=_generate_and_save, args=(scene_key,), daemon=True)
    t.start()


def location_to_scene_key(location: str) -> str:
    loc = location.lower()
    for key, scene in LOCATION_TO_SCENE.items():
        if key in loc:
            return scene
    return "default"


# Where generated images are saved
GENERATED_DIR = Path(__file__).parent.parent / "generated"
LATEST_PATH = GENERATED_DIR / "latest.png"
HISTORY_DIR = GENERATED_DIR / "history"

# Scene-specific prompt fragments — used to build the full DALL-E prompt
SCENE_PROMPTS: dict[str, str] = {
    "default": (
        "interior of a dark, deteriorating deep-space station corridor, "
        "flickering emergency lighting, exposed conduits, floating debris, "
        "cinematic sci-fi concept art, ultra-detailed"
    ),
    "command_deck": (
        "ISS Tartarus command bridge, holographic displays showing red alerts, "
        "cracked viewport revealing stars, emergency lighting, abandoned coffee cup floating, "
        "cinematic sci-fi concept art, moody atmosphere"
    ),
    "airlock_7": (
        "deep-space station airlock chamber, blast marks on the door, "
        "cold blue emergency lighting, crime scene tape floating in zero-g, "
        "cinematic sci-fi noir, photorealistic"
    ),
    "medical_bay": (
        "futuristic space station medical bay, sterile white surfaces stained red, "
        "holographic autopsy display, dim lighting, unsettling silence, "
        "cinematic sci-fi concept art"
    ),
    "engineering_bay": (
        "deep-space station engineering core, damaged reactor junction B-7, "
        "sparking conduits, toxic coolant leak glowing green, "
        "technician tools floating abandoned, cinematic sci-fi"
    ),
    "cargo_hold": (
        "space station cargo hold, crates stamped HeliosCore, "
        "hidden smuggling compartment pried open, encrypted comms device on crate, "
        "shadowy cinematic lighting, sci-fi thriller"
    ),
    "aria_server_room": (
        "space station AI server room, glowing blue neural network racks, "
        "one rack visibly corrupted and dark, warning lights flashing, "
        "sinister atmosphere, cinematic sci-fi"
    ),
    "evidence": (
        "close-up of a crucial piece of evidence aboard a dark space station, "
        "dramatic spotlight, forensic detail, cinematic sci-fi noir"
    ),
    "confrontation": (
        "tense confrontation scene inside a dark space station corridor, "
        "two silhouettes facing each other, red emergency lighting, "
        "dramatic shadows, cinematic sci-fi thriller"
    ),
    "oxygen_critical": (
        "space station interior, red emergency lights pulsing, "
        "oxygen warning displays everywhere, crew member in distress, "
        "atmosphere of imminent danger, cinematic sci-fi"
    ),
    "ending_truth": (
        "space station commander holding encrypted evidence device, "
        "stars visible through viewport, justice achieved, "
        "hopeful blue lighting, cinematic sci-fi"
    ),
    "ending_failure": (
        "space station commander alone in dark corridor, "
        "corporate shuttle departing through viewport, "
        "defeated atmosphere, cold blue-grey lighting, cinematic sci-fi noir"
    ),
}

# Location name → scene key mapping
LOCATION_TO_SCENE: dict[str, str] = {
    "command deck": "command_deck",
    "airlock 7": "airlock_7",
    "airlock": "airlock_7",
    "medical bay": "medical_bay",
    "engineering bay": "engineering_bay",
    "cargo hold": "cargo_hold",
    "aria server room": "aria_server_room",
    "server room": "aria_server_room",
}


def _build_prompt(scene_key: str) -> str:
    fragment = SCENE_PROMPTS.get(scene_key, SCENE_PROMPTS["default"])
    return (
        f"Cinematic sci-fi illustration: {fragment}. "
        "No text, no watermarks. Dark dramatic lighting. "
        "Style: detailed digital painting, widescreen 16:9."
    )


def _get_client() -> AzureOpenAI:
    return AzureOpenAI(
        azure_endpoint=Config.AZURE_OPENAI_ENDPOINT,
        api_key=Config.AZURE_OPENAI_API_KEY,
        api_version="2024-02-01",  # DALL-E 3 requires this version
    )


def _generate_and_save(scene_key: str) -> None:
    """Blocking call — run in a thread."""
    try:
        GENERATED_DIR.mkdir(exist_ok=True)
        HISTORY_DIR.mkdir(exist_ok=True)

        client = _get_client()
        deployment = os.getenv("AZURE_IMAGE_DEPLOYMENT", "dall-e-3")

        response = client.images.generate(
            model=deployment,
            prompt=_build_prompt(scene_key),
            size="1792x1024",
            quality="standard",
            n=1,
        )

        image_url = response.data[0].url
        # Download and save
        urllib.request.urlretrieve(image_url, str(LATEST_PATH))

        # Also save to history with scene name
        import shutil, time as _time
        ts = int(_time.time())
        shutil.copy(str(LATEST_PATH), str(HISTORY_DIR / f"{ts}_{scene_key}.png"))

    except Exception:
        # Image generation is non-critical — silently fail
        pass


def generate_scene_image(scene_key: str) -> None:
    """
    Trigger DALL-E 3 image generation in a background thread.
    Non-blocking — game continues immediately.
    """
    t = threading.Thread(target=_generate_and_save, args=(scene_key,), daemon=True)
    t.start()


def location_to_scene_key(location: str) -> str:
    """Map a game location string to a SCENE_PROMPTS key."""
    loc = location.lower()
    for key, scene in LOCATION_TO_SCENE.items():
        if key in loc:
            return scene
    return "default"
