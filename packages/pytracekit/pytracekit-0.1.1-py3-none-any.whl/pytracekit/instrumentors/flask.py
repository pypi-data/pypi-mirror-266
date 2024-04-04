from .base import InstrumentorInterface


class FlaskInstrumentor(InstrumentorInterface):
    def instrument_framework(self, app):
        from opentelemetry.instrumentation.flask import FlaskInstrumentor as OTFlaskInstrumentor # conditional import
        OTFlaskInstrumentor().instrument_app(app)
