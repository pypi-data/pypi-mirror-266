from typing import List
from grpc import Channel
import grpc
from rpc import models_pb2_grpc, models_pb2
from .models import Model


class Client():
    channel: Channel
    def __init__(self, channel: str):
        self.channel = grpc.insecure_channel(channel)

    def get_models(self) -> List[Model]:
        stub = models_pb2_grpc.ModelsServiceStub(self.channel)
        request = models_pb2.ListRequest()
        list: models_pb2.ListResponse = stub.List(request)

        
        return [Model(id=model.id, model_size=model.model_size, tokenizer_size=model.tokenizer_size) for model in list.models]
        
        
        
        
        
        
