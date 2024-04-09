from dataclasses import dataclass
from typing import Any, Optional

from .inference import InferenceParams

@dataclass
class Model:
    id: str
    model_size: int
    tokenizer_size: int
    client: Any

    def infer(self, prompt: str, params: Optional[InferenceParams] = None, streaming=True):
        return self.client.infer(model_id=self.id, prompt=prompt, params=params, streaming=streaming)
