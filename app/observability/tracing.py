from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from app.core.settings import settings


def init_tracing() -> None:
    provider = TracerProvider()
    processor = BatchSpanProcessor(
    OTLPSpanExporter(endpoint=settings.metrix.otlp_endpoint, insecure=True)
    )
    provider.add_span_processor(processor)
    trace.set_tracer_provider(provider)