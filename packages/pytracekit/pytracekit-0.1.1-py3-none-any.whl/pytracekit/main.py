
from opentelemetry.sdk.resources import Resource
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.redis import RedisInstrumentor
from opentelemetry.instrumentation.pymongo import PymongoInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor

from pytracekit.config.TraceConfig import TraceConfig
from pytracekit.utils.detect_framework import detect_framework
from pytracekit.instrumentors.utils import initialize_instrumentor



# Initialize tracing function
def instrument(app=None):
    """
       Main action that enables auto instrumentation
       params : 
       app : the instance of the fastapi, flask ,falcon application
       framework: the name of the framework which needs to be instrumented 
    """
    config = TraceConfig()
    if not config.enable_tracing:
        print("Tracing is disabled.")
        return
    if not config.tracing_endpoint:
        raise Exception("Tracing endpoint not provided.")

    if not config.trace_service_name:
        raise Exception("Trace service name not provided.")

  
    provider = TracerProvider(resource=Resource.create(attributes={
        "service.name": config.trace_service_name
    }))
    # span processor
    processor = BatchSpanProcessor(OTLPSpanExporter(endpoint=config.tracing_endpoint))
    provider.add_span_processor(processor)
    trace.set_tracer_provider(provider)
    
    framework = detect_framework(app)
    initialize_instrumentor(framework, app)
    RequestsInstrumentor().instrument()
    RedisInstrumentor().instrument()
    PymongoInstrumentor().instrument()
    print("Tracing is enabled ")





