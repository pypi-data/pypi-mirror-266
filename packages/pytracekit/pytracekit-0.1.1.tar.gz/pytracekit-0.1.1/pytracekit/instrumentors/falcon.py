from .base import InstrumentorInterface


class FalconInstrumentor(InstrumentorInterface):
    def instrument_framework(self, app):
        from opentelemetry.instrumentation.falcon import FalconInstrumentor as OTFalconInstrumentor
        OTFalconInstrumentor().instrument()
