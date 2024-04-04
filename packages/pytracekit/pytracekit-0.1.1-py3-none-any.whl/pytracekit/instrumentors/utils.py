from pytracekit.constants.common import FASTAPI, FLASK, FALCON
from .fastapi import FastAPIInstrumentor
from .flask import FlaskInstrumentor
from .falcon import FalconInstrumentor

def initialize_instrumentor(framework, app):
    instrumentor = None
    if framework == FASTAPI:
        instrumentor = FastAPIInstrumentor()
    elif framework == FLASK:
        instrumentor = FlaskInstrumentor()
    elif framework == FALCON:
        instrumentor = FalconInstrumentor()
    else:
        raise ValueError(f"Unsupported framework {framework}")

    if instrumentor:
        instrumentor.instrument_framework(app)
