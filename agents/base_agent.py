"""Base agent — shared OpenAI client setup and response generation."""

from openai import AzureOpenAI
from config import Config
from telemetry.tracing import get_tracer


def _build_openai_client() -> AzureOpenAI:
    return AzureOpenAI(
        azure_endpoint=Config.AZURE_OPENAI_ENDPOINT,
        api_key=Config.AZURE_OPENAI_API_KEY,
        api_version=Config.AZURE_OPENAI_API_VERSION,
    )


_shared_client: AzureOpenAI | None = None


def get_client() -> AzureOpenAI:
    global _shared_client
    if _shared_client is None:
        _shared_client = _build_openai_client()
    return _shared_client


class BaseAgent:
    """
    Base class for all Fractured Orbit agents.
    Each subclass defines its own system_prompt and name.
    """

    name: str = "Agent"
    system_prompt: str = "You are an AI assistant."

    def __init__(self) -> None:
        self._client = get_client()
        self._tracer = get_tracer()

    def respond(
        self,
        user_message: str,
        context: str = "",
        game_state: dict | None = None,
        temperature: float = 0.75,
    ) -> str:
        """
        Generate an in-character response.

        Args:
            user_message: The prompt directed at this agent.
            context:       Retrieved lore from Foundry IQ / knowledge base.
            game_state:    Current game state snapshot for situational awareness.
            temperature:   Sampling temperature.

        Returns:
            The agent's response string.
        """
        messages = self._build_messages(user_message, context, game_state)

        span_name = f"{self.name.lower().replace(' ', '_')}.respond"
        with self._tracer.start_as_current_span(span_name) as span:
            span.set_attribute("agent.name", self.name)
            span.set_attribute("input.length", len(user_message))

            try:
                response = self._client.chat.completions.create(
                    model=Config.AZURE_AI_MODEL_DEPLOYMENT,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=250,
                )
                text = response.choices[0].message.content or ""
                span.set_attribute("output.length", len(text))
                return text.strip()
            except Exception as exc:
                span.record_exception(exc)
                return f"[{self.name} comms offline — signal lost]"

    def _build_messages(
        self,
        user_message: str,
        context: str,
        game_state: dict | None,
    ) -> list[dict]:
        system = self.system_prompt
        if context:
            system += f"\n\n## Station Knowledge Base\n{context}"
        if game_state:
            system += (
                f"\n\n## Current Situation\n"
                f"Station Day: {game_state.get('station_day', '?')}\n"
                f"Time: {game_state.get('in_game_hour', '?')}:00\n"
                f"Location: {game_state.get('location', '?')}\n"
                f"Oxygen: {game_state.get('oxygen_level', '?')}%\n"
                f"Conditions: {', '.join(game_state.get('conditions', [])) or 'none'}\n"
                f"Evidence gathered: {len(game_state.get('evidence', []))} items"
            )
        return [
            {"role": "system", "content": system},
            {"role": "user", "content": user_message},
        ]
