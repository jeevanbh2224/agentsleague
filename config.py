import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    # ── Azure AI Foundry ──────────────────────────────────────────────────────
    AZURE_AI_PROJECT_CONNECTION_STRING: str = os.getenv(
        "AZURE_AI_PROJECT_CONNECTION_STRING", ""
    )
    AZURE_AI_MODEL_DEPLOYMENT: str = os.getenv("AZURE_AI_MODEL_DEPLOYMENT", "gpt-4o")

    # ── Azure OpenAI (direct fallback) ────────────────────────────────────────
    AZURE_OPENAI_ENDPOINT: str = os.getenv("AZURE_OPENAI_ENDPOINT", "")
    AZURE_OPENAI_API_KEY: str = os.getenv("AZURE_OPENAI_API_KEY", "")
    AZURE_OPENAI_API_VERSION: str = os.getenv(
        "AZURE_OPENAI_API_VERSION", "2024-11-20"
    )

    # ── Azure AI Search — Foundry IQ ──────────────────────────────────────────
    AZURE_SEARCH_ENDPOINT: str = os.getenv("AZURE_SEARCH_ENDPOINT", "")
    AZURE_SEARCH_API_KEY: str = os.getenv("AZURE_SEARCH_API_KEY", "")
    AZURE_SEARCH_INDEX_NAME: str = os.getenv(
        "AZURE_SEARCH_INDEX_NAME", "fractured-orbit-lore"
    )

    # ── Cosmos DB ─────────────────────────────────────────────────────────────
    COSMOS_ENDPOINT: str = os.getenv("COSMOS_ENDPOINT", "")
    COSMOS_KEY: str = os.getenv("COSMOS_KEY", "")
    COSMOS_DATABASE: str = os.getenv("COSMOS_DATABASE", "fractured_orbit")
    COSMOS_CONTAINER: str = os.getenv("COSMOS_CONTAINER", "game_sessions")

    # ── Azure Storage ─────────────────────────────────────────────────────────
    AZURE_STORAGE_CONNECTION_STRING: str = os.getenv(
        "AZURE_STORAGE_CONNECTION_STRING", ""
    )
    AZURE_STORAGE_CONTAINER: str = os.getenv(
        "AZURE_STORAGE_CONTAINER", "world-data"
    )

    # ── DALL-E 3 Image Generation ─────────────────────────────────────────────
    AZURE_IMAGE_DEPLOYMENT: str = os.getenv("AZURE_IMAGE_DEPLOYMENT", "dall-e-3")
    IMAGE_PANEL_ENABLED: bool = os.getenv("IMAGE_PANEL_ENABLED", "true").lower() == "true"

    # ── Application Insights ──────────────────────────────────────────────────
    APPLICATIONINSIGHTS_CONNECTION_STRING: str = os.getenv(
        "APPLICATIONINSIGHTS_CONNECTION_STRING", ""
    )

    @classmethod
    def validate(cls) -> list[str]:
        """Return list of missing required env vars."""
        missing = []
        required = {
            "AZURE_OPENAI_ENDPOINT": cls.AZURE_OPENAI_ENDPOINT,
            "AZURE_OPENAI_API_KEY": cls.AZURE_OPENAI_API_KEY,
            "AZURE_SEARCH_ENDPOINT": cls.AZURE_SEARCH_ENDPOINT,
            "AZURE_SEARCH_API_KEY": cls.AZURE_SEARCH_API_KEY,
            "COSMOS_ENDPOINT": cls.COSMOS_ENDPOINT,
            "COSMOS_KEY": cls.COSMOS_KEY,
        }
        for name, val in required.items():
            if not val:
                missing.append(name)
        return missing

    @classmethod
    def has_telemetry(cls) -> bool:
        return bool(cls.APPLICATIONINSIGHTS_CONNECTION_STRING)

    @classmethod
    def has_search(cls) -> bool:
        return bool(cls.AZURE_SEARCH_ENDPOINT and cls.AZURE_SEARCH_API_KEY)

    @classmethod
    def has_cosmos(cls) -> bool:
        return bool(cls.COSMOS_ENDPOINT and cls.COSMOS_KEY)

    @classmethod
    def has_image_gen(cls) -> bool:
        return cls.IMAGE_PANEL_ENABLED
