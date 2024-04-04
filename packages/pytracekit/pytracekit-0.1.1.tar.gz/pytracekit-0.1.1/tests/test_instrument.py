
from unittest.mock import patch, MagicMock
import pytest
from pytracekit.main import instrument


def test_tracing_disbaled():
    with patch('pytracekit.main.TraceConfig') as MockTraceConfig:
        MockTraceConfig.return_value.enable_tracing = False
        with patch('builtins.print') as mock_print:
            instrument()
            mock_print.assert_called_once_with("Tracing is disabled.")


def test_missing_tracing_endpoint():
    with patch('pytracekit.main.TraceConfig') as MockTraceConfig:
        MockTraceConfig.return_value.enable_tracing = True
        MockTraceConfig.return_value.tracing_endpoint = None 
        MockTraceConfig.return_value.trace_service_name = "some_service"  
       
        with pytest.raises(Exception) as exp:
            instrument()  
        assert "Tracing endpoint not provided." in str(exp.value)


def test_missing_trace_service_name():
    with patch('pytracekit.main.TraceConfig') as MockTraceConfig:
        MockTraceConfig.return_value.enable_tracing = True
        MockTraceConfig.return_value.tracing_endpoint = "https://23455333" 
        MockTraceConfig.return_value.trace_service_name = None  

        with pytest.raises(Exception) as exp:
            instrument()
        assert  "Trace service name not provided." in str(exp.value)



def test_dummy():
    assert 2+3 == 5


def test_successful_instrumentation():
    with patch('pytracekit.main.TraceConfig') as MockTraceConfig, \
         patch('pytracekit.main.TracerProvider') as MockTracerProvider, \
         patch('pytracekit.main.BatchSpanProcessor') as MockBatchSpanProcessor, \
         patch('pytracekit.main.OTLPSpanExporter') as MockOTLPSpanExporter, \
         patch('pytracekit.main.RequestsInstrumentor') as MockRequestsInstrumentor, \
         patch('pytracekit.main.RedisInstrumentor') as MockRedisInstrumentor, \
         patch('pytracekit.main.PymongoInstrumentor') as MockPymongoInstrumentor, \
         patch('pytracekit.main.initialize_instrumentor') as MockInitializeInstrumentor, \
         patch('builtins.print') as mock_print:

        # Configure TraceConfig mock
        MockTraceConfig.return_value.enable_tracing = True
        MockTraceConfig.return_value.tracing_endpoint = 'some_endpoint'
        MockTraceConfig.return_value.trace_service_name = 'some_service_name'
        
        # Simulate the behavior as if the correct framework has been detected and instrumented
        MockInitializeInstrumentor.side_effect = lambda framework, app: None

        # Call the instrument function
        instrument()
        
        # Assert initialize_instrumentor was called, this implies framework detection was attempted
        MockInitializeInstrumentor.assert_called()
        
        # Assert the TracerProvider and span processor setup
        MockTracerProvider.assert_called_once()
        MockBatchSpanProcessor.assert_called_once_with(MockOTLPSpanExporter.return_value)
        MockTracerProvider.return_value.add_span_processor.assert_called_once_with(
            MockBatchSpanProcessor.return_value
        )
        
        # Assert that global tracer provider was set (this requires patching 'pytracekit.main.trace' if it's imported that way)
        
        # Assert the instrumentation for Requests, Redis, and Pymongo
        MockRequestsInstrumentor.return_value.instrument.assert_called_once()
        MockRedisInstrumentor.return_value.instrument.assert_called_once()
        MockPymongoInstrumentor.return_value.instrument.assert_called_once()
        
        # Check that the final print statement was executed, indicating successful completion
        mock_print.assert_called_with("Tracing is enabled ")