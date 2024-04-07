from typing import List, Dict
from types import FunctionType


class NstreamLLM(object):
    def __init__(self) -> None:
        pass
    @staticmethod
    def feret_v1():
        return "FERET_V1"
    @staticmethod
    def llama2_7b():
        return "LLAMA2_7B"
    @staticmethod
    def mistral_7b():
        return "MISTRAL_7B"

class NsSocket(object):
    def __init__(self, grpc_endpoint) -> None:
        self.grpc_endpoint = grpc_endpoint
        self.status = False
        pass

    def call_grpc_endpoint(self, method: FunctionType):
        self.status = True
        return self.status

class NsNeuron(object):
    def __init__(self, llm:str) -> None:
        pass

class NsInit(object):
    def __init__(self, api_key="") -> None:
        pass
    
    def connect()->NsSocket:
        socket = NsSocket(grpc_endpoint="api.cloud.nstream.ai:50031")
        return socket

class Nstream(object):
    def __init__(self) -> None:
        pass

class NsLink(Nstream):
    def __init__(self) -> None:
        return super().__init__()

class NsNodeOutput(Nstream):
    def __init__(self) -> None:
        return super().__init__()
        
class NsNode(object):
    def __init__(self, prompt:NsLink|NsNodeOutput, context: NsLink|NsNodeOutput, neuron: NsNeuron) -> None:
        self.prompt = prompt
        self.context = context
        self.neuron = neuron
        pass

    def output(self):
        out = NsNodeOutput()
        return out

class NsGraph(object):
    def __init__(self, socket:NsSocket) -> None:
        self.graph = list(dict())
        self.socket = socket
        self.current_node = None
        self.last_node = None
        pass

    def start(self, node:NsNode):
        self.current_node = node
        return self
    
    def next_node(self,node:NsNode):
        self.last_node = self.current_node
        self.current_node = node
        self.graph.append(self.node_to_dict(self.current_node))
        return self
    
    def end(self, node:NsNode):
        self.last_node = self.current_node
        self.current_node = node
        self.graph.append(self.node_to_dict(self.current_node))
        return self
    
    
    def submit(self, sink:NsLink):
        self.graph.append({"sink": sink})
        self.socket.call_grpc_endpoint(method=(lambda x: x))
        return self

    def terminate(self):
        self.socket.call_grpc_endpoint(method=(lambda x : x))
        return self

    
    @staticmethod
    def node_to_dict(node:NsNode)->Dict:
        return dict()
    


# if __name__ == "__main__":

#     conn = NsInit(api_key="JISHDDSJDKSNDNJ").connect()
    
#     ns_node_1 = NsNode(prompt=NsLink(), context=NsLink(), neuron=NsNeuron(NstreamLLM.mistral_7b()))
#     ns_node_2 = NsNode(prompt=NsLink(), context=ns_node_1.output(), neuron=NsNeuron(NstreamLLM.mistral_7b()))
#     ns_node_3 = NsNode(prompt=ns_node_2.output(), context=NsLink(), neuron=NsNeuron(NstreamLLM.mistral_7b()))

#     ns_graph_sink = NsLink()

#     ns_graph = NsGraph(conn).start(ns_node_1).next_node(ns_node_2).end(ns_node_3).submit(ns_graph_sink)

#     ns_graph.terminate()
