from .rawws import RawWs

class Connection:

    def __init__(self, id, username):
        self.__conn = RawWs("connection")
        self.__id = str(id)
        self.__username = username

        self.__conn.send("register",{
            "from": self.__id,
            "username": self.__username,
        })
        
        authPacket = self.__conn.receive()
        self.__token = authPacket['token']

    def __reLogin(self):
        try:
            self.__conn.reConnect()
        except:
            raise ConnectionError("Did you change the address? If not the server is probably down.")
        self.__conn.send("login", {
            "id" : self.__id,
            "token" : self.__token
        })
        loginPacket = self.__conn.receive()
        if loginPacket["isSuccess"] == False:
            raise ConnectionError("Failed to relogin. Did you edit your token or id?")

    def deleteUser(self):
        packet = {
            "from" : self.__id,
            "token": self.__token
        }
        try:
            self.__conn.send("deleteUser", packet)
        except:
            self.__reLogin()
            self.deleteUser()

    def changeUserName(self, username):
        self.__conn.send("changeUsername", {
            "id" : self.__id,
            "token" : self.__token,
            "username" : username
        })
        self.__username = username
    
    def send(self, message, to):
        packet = {
            "from" : self.__id,
            "to" : to,
            "message" : message
        }
        try:
            self.__conn.send("message", packet)
        except:
            self.__reLogin()
            self.send(message, to)

    def receive(self):
        try:
            return self.__conn.receive()
        except:
            self.__reLogin()
            return self.receive()

'''
from websocket import create_connection
import json

class Connection_old:

    def __init__(self, id, username):
        self.__uri = "wss://darkodaaa.one:25500"
        self.__id = str(id)
        self.__username = username

        self.__ws = create_connection(self.__uri)

        self.__ws.send(json.dumps({
            "protocol": "register",
            "from": self.__id,
            "username": self.__username,
        }))
        
        authPacket = json.loads(self.__ws.recv())
        self.__token = authPacket['token']

    def __reLogin(self):
        try:
            self.__ws = create_connection(self.__uri)
        except:
            ConnectionError("Server down.")
        self.__ws.send(json.dumps({
            "protocol": "login",
            "id" : self.__id,
            "token" : self.__token
        }))
        loginPacket = json.loads(self.__ws.recv())
        if loginPacket["isSuccess"] == False:
            ConnectionError("Failed to relogin. Did you edit your token or id?")

    def deleteUser(self):
        packet = json.dumps({
            "protocol": "deleteUser",
            "from" : self.__id,
            "token": self.__token
        })
        try:
            self.__ws.send(packet)
        except:
            self.__reLogin()
            self.deleteUser()

    def changeUserName(self, username):
        self.__ws.send(json.dumps({
            "protocol": "changeUsername",
            "id" : self.__id,
            "token" : self.__token,
            "username" : username
        }))
    
    def send(self, message, to):
        packet = json.dumps({
            "protocol": "message",
            "from" : self.__id,
            "to" : to,
            "message" : message
        })
        try:
            self.__ws.send(packet)
        except:
            self.__reLogin()
            self.send(message, to)

    def receive(self):
        try:
            return json.loads(self.__ws.recv())
        except:
            self.__reLogin()
            self.receive()

'''