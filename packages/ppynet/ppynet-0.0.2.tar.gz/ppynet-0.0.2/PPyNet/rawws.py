from websockets.sync.client import connect as create_connection
import json

class RawWs:

    def __init__(self, protocol: str) -> None:
        """
            Makes a websocket connection to the server.
            Takes a protocol that is assigned to the instance.

            Params:
                protocol: String the protocol the instance uses for sending the server data.

            Raises:
                ConnectionError: When it can't create a new connection to the server.

            Returns: None
        """

        self.__uri = "wss://ppynet.darkodaaa.one"
        self.__protocol = protocol
        try:
            self.__ws = create_connection(self.__uri)
        except:
            ConnectionError("Couldn't create to server. Is the server down?")

    def reConnect(self) -> None:
        """
            Reconnect the websocket mostly when it times out.
            Creates a new connection to the server.

            Raises:
                ConnectionError: Whenever it can't create a new connection to the server.

            Returns: None
        """

        try:
            self.__ws = create_connection(self.__uri)
            return True
        except:
            raise ConnectionError("Can't connect to the server, is still it running?")
            
    def send(self, protocol: str, data: dict) -> None:
        """
            Sends a raw json message to the server with the protocol of the current instance and the subprotocol specified.

            Params:
                protocol: String the subprotocol to use for the server to handle.
                data: Dict a dictionary containing all data that is needed for the server to process the given protocol and subprotocol.
            
            Raises:
                ConnectionError: When the connection to the server is closed.

            Returns: None
        """

        data["protocol"] = self.__protocol
        data["subProtocol"] = protocol
        try:
            return self.__ws.send(json.dumps(data))
        except:
            raise ConnectionError("Sending failed. Is the server down?")
        
    def receive(self):
        """
            Receive a raw json message from the server and converts it into a dictionary.

            Raises:
                ConnectionError: When the connection to the server is closed.

            Returns: Dict the dictionary containing the data sent by the server.
        """

        try:
            return json.loads(self.__ws.recv())
        except:
            raise ConnectionError("Receive failed, is the server down?")