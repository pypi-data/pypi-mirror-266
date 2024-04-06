from dataclasses import dataclass

@dataclass
class Model:
    id: str
    model_size: int
    tokenizer_size: int
