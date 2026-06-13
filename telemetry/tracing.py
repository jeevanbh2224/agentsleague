from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.resources import Resource

_tracer: trace.Tracer | None = None


def setup_telemetry(connection_string: str) -> None:
    """Initialise OpenTelemetry with Azure Monitor exporter."""
    global _tracer
    try:
        from azure.monitor.opentelemetry.exporter import AzureMonitorTraceExporter

        resource = Resource.create({"service.name": "fractured-orbit-game"})
        provider = TracerProvider(resource=resource)
        exporter = AzureMonitorTraceExporter(connection_string=connection_string)
        provider.add_span_processor(BatchSpanProcessor(exporter))
        trace.set_tracer_provider(provider)
        _tracer = trace.get_tracer("fractured-orbit")
    except Exception:
        # Telemetry is optional — game continues without it
        _tracer = trace.get_tracer("fractured-orbit")


def get_tracer() -> trace.Tracer:
    global _tracer
    if _tracer is None:
        _tracer = trace.get_tracer("fractured-orbit")
    return _tracer
