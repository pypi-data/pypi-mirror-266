from dataclasses import dataclass
from typing import Optional
from .rpc import inference_pb2



@dataclass
class InferenceParams:
    temperature: float
    top_p: float
    seed: int
    sample_len: int
    repeat_penalty: float
    repeat_last_n: int


    def __into_request(self):
        params_request = inference_pb2.Params(temperature=self.temperature,top_p=self.top_p,seed=self.seed, sample_len=self.sample_len, repeat_penalty=self.repeat_penalty,repeat_last_n=self.repeat_last_n)
