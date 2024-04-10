from typing import List, Optional
from grpc import Channel
import grpc
from .rpc import models_pb2_grpc, models_pb2, inference_pb2, inference_pb2_grpc
from .models import Model
from .inference import InferenceParams



DEFAULT_LOCAL_HOST = "localhost:50051"

class Client():
    channel: Channel
    def __init__(self, channel: Optional[str] = None):
        channel = DEFAULT_LOCAL_HOST if channel == None else channel
        self.channel = grpc.insecure_channel(channel)

    def get_models(self) -> List[Model]:
        stub = models_pb2_grpc.ModelsServiceStub(self.channel)
        request = models_pb2.ListRequest()
        list: models_pb2.ListResponse = stub.List(request)

        
        return [Model(id=model.id, model_size=model.model_size, tokenizer_size=model.tokenizer_size, client=self) for model in list.models]

    def infer(self, model_id: str, prompt: str, params: Optional[InferenceParams] = None):
        stub = inference_pb2_grpc.InferenceServiceStub(self.channel)
        params_request = None if params == None else params.__into_request()

        inference_request = inference_pb2.InferRequest(model_id=model_id, prompt=prompt, params=params_request)

        response = stub.Infer(inference_request)



        for chunk in response:
            chunk: inference_pb2.InferResponse = chunk
            if chunk.chunk:
                yield chunk.chunk.token
