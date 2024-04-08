from websockets.sync.client import connect as create_connection
import json

class RawWs:

    def __init__(self, protocol):
        self.__uri = "wss://ppynet.darkodaaa.one"
        self.__protocol = protocol
        self.__ws = create_connection(self.__uri)

    def reConnect(self):
        try:
            self.__ws = create_connection(self.__uri)
            return True
        except:
            raise ConnectionError("Can't connect to the server, is still it running?")
            
    def send(self, protocol, data):
        data["protocol"] = self.__protocol
        data["subProtocol"] = protocol
        try:
            return self.__ws.send(json.dumps(data))
        except:
            raise ConnectionError("Sending failed. Is the server down?")
        
    def receive(self):
        try:
            return json.loads(self.__ws.recv())
        except:
            raise ConnectionError("Receive failed, is the server down?")