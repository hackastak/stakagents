"""Tracing wrapper — instruments LangChain/LangGraph once, exports OTLP to Langfuse.

The one anti-lock-in rule: agents never import Langfuse. They call setup_tracing()
and everything they do through LangChain becomes OpenInference spans, shipped over
OTLP to whatever OTEL_EXPORTER_OTLP_ENDPOINT names — Langfuse today, Phoenix tomorrow,
a one-line .env change. Never wire a vendor callback into agent code.
"""

import base64

from openinference.instrumentation.langchain import LangChainInstrumentor
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from stakagents.core.config import settings

_provider: TracerProvider | None = None


def setup_tracing(service_name: str = "stakagents") -> None:
    """Initialize OTLP tracing to Langfuse and instrument LangChain. Idempotent."""
    global _provider
    if _provider is not None:
        return

    # Langfuse authenticates OTLP ingestion with Basic auth: base64(public:secret).
    auth = base64.b64encode(
        f"{settings.langfuse_public_key}:{settings.langfuse_secret_key}".encode()
    ).decode()

    exporter = OTLPSpanExporter(
        endpoint=f"{settings.otel_exporter_otlp_endpoint}/v1/traces",
        headers={"Authorization": f"Basic {auth}"},
    )

    provider = TracerProvider(resource=Resource.create({"service.name": service_name}))
    provider.add_span_processor(BatchSpanProcessor(exporter))
    trace.set_tracer_provider(provider)

    LangChainInstrumentor().instrument(tracer_provider=provider)
    _provider = provider


def flush_tracing() -> None:
    """Force-export buffered spans. Call before a short-lived process exits."""
    if _provider is not None:
        _provider.force_flush()
