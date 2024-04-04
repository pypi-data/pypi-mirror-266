from abc import ABC, abstractmethod

class InstrumentorInterface(ABC):
    @abstractmethod
    def instrument_framework(self, app):
        """Instruments the given app/framework with tracing capabilities."""
        
        raise NotImplementedError("Subclasses must implement this method.")


