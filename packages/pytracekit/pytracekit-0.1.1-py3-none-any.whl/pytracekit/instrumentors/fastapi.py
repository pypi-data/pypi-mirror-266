from .base import InstrumentorInterface


class FastAPIInstrumentor(InstrumentorInterface):
    def instrument_framework(self, app):
        from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor as OTFastAPIInstrumentor
        OTFastAPIInstrumentor.instrument_app(app)
