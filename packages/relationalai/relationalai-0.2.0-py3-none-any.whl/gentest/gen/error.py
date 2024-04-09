from typing import Any


class BuilderConsumedError(Exception):
    def __init__(self, builder: Any):
        super().__init__(f"{builder.__class__.__name__} modified after finish() called. finish() reuses the collections the builder populates, so this would mutate the resulting instance and break any generators dependant on it. Consider calling .snapshot() instead if the intent is to keep producing new instances from the same builder.")
