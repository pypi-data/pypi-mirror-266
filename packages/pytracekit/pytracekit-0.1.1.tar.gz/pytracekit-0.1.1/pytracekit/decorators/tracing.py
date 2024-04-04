from functools import wraps
import asyncio
from opentelemetry.trace import Status, StatusCode
from opentelemetry import trace
from pytracekit.config.TraceConfig import TraceConfig

def instrument_with_tracing(operation_name=None, span_attrs=None):
    """
    decorator for applying instrumentation on function (supports both async and sync functions)
    params:
    operation_name(optional) : name you want to give to the function(if not provided default function name will be used)
    span_attrs(optional) : custom attributes you want to give to the function
    """
    def decorator(func):
        if asyncio.iscoroutinefunction(func):
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                if not TraceConfig().enable_tracing:
                    return await func(*args, **kwargs)

                tracer = trace.get_tracer(__name__)
                with tracer.start_as_current_span(operation_name or func.__name__, attributes=span_attrs) as span:
                    try:
                        return await func(*args, **kwargs)
                    except Exception as e:
                        span.record_exception(e)
                        span.set_status(Status(StatusCode.ERROR, str(e)))
                        raise
            return async_wrapper
        else:
            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                if not TraceConfig().enable_tracing:
                    return func(*args, **kwargs)

                tracer = trace.get_tracer(__name__)
                with tracer.start_as_current_span(operation_name or func.__name__, attributes=span_attrs) as span:
                    try:
                        return func(*args, **kwargs)
                    except Exception as e:
                        span.record_exception(e)
                        span.set_status(Status(StatusCode.ERROR, str(e)))
                        raise
            return sync_wrapper
    return decorator