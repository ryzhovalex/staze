from staze import Sock, log


class ChatSock(Sock):
    NAMESPACE: str = '/chat' 

    def on_connect(self):
        pass
    
    def on_send(self, data):
        data = {'number': 4321}
        self.socket.send(data, namespace=self.namespace)
        return data
