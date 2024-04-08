from .rawws import RawWs

class Connection:

    def __init__(self, id: int, username: str) -> None:
        self.__conn = RawWs("connection")
        self.__id = str(id)
        self.__username = username

        self.__conn.send("register",{
            "from": self.__id,
            "username": self.__username,
        })
        
        authPacket = self.__conn.receive()
        self.__token = authPacket['token']

    def __reLogin(self) -> None:
        """
            Relogs session whenever its called.
            This usually happens when a sending or recieving of a message fails.

            Raises:
                ConnectionError: When it can't reconnect to the server as its probably down.
                ConnectionError: When the login failed probably because the id or token is invalid. (This usually happens if the user changes the session's properties.)

            Returns: None
        """

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
            raise ConnectionError("Failed to relogin. Did you edit your token or id? \nIf not maybe someone else logged on with the same id because your session was expired.")

    def deleteUser(self):
        """
            Deletes the user. \n
            Not needed since the server cleans up unused users.

            Returns: Boolean if the server was reachable.If its false it was probably deleted already or the server shut down.
        """
        packet = {
            "from" : self.__id,
            "token": self.__token
        }
        try:
            self.__conn.send("deleteUser", packet)
            return True
        except:
            return False

    def changeUsername(self, username: str):
        """
            Changes the user name of the user. \n
            The happens on the server side and the client side.

            Params:
                username: The username to change to.
            
            Raises:
                ConnectionError: When the server isn't available.

            Returns: None
        """
        self.__conn.send("changeUsername", {
            "id" : self.__id,
            "token" : self.__token,
            "username" : username
        })
        self.__username = username

    def getUsername(self) -> str:
        """
            Returns the username (str) stored in the current session.

            Returns: String the current username of the client. 
        """
        return self.__username
    
    def send(self, message: str, to: int, retry = True) -> None:
        """
            Sends a message to the client with the given id.

            Params:
                message: String the message to send to the specified user.
                to: Int the id of the user to send the message to.
                retry: Boolean if the sending of the message should be retried after a connection failure.
                    Leave this on as this tries to relogin whenever your connection times out. Default is True.

            Raises:
                ConnectionError: When retry is false and the it can't send the message.

            Returns: None
        """
        packet = {
            "from" : self.__id,
            "to" : to,
            "message" : message
        }

        if not retry:
            self.__conn.send("message", packet)
            return None

        try:
            self.__conn.send("message", packet)
        except:
            self.__reLogin()
            self.send(message, to)

    def receive(self, retry=True) -> dict:
        """
            Receive a message if someone sent this client one.

            Params:
                retry: Boolean if the receiving of a message should be retried after a connection failure.
                    Leave this on as this tries to relogin whenever your connection times out. Default is True.

            Raises:
                ConnectionError: When retry is false and the connection is closed.
                RecursionError: When retry is true and relogin succeeds but it can't receive a message. Happens very rarely.

            Returns: Dict a dictionary parsed from a json containing the senders username, id and message.
        """

        if not retry:
            return self.__conn.receive()
        
        try:
            return self.__conn.receive()
        except:
            self.__reLogin()
            return self.receive()