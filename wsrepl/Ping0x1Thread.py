from wsrepl.WSMessage import WSMessage, Opcode
from wsrepl.PingThread import PingThread
import threading

class Ping0x1Thread(PingThread):
    def __init__(self,
                 message_handler: 'MessageHandler',
                 ping_interval: int,
                 ping_data: str,
                 is_stopped: threading.Event) -> None:
        super().__init__(message_handler, ping_interval, is_stopped)
        self.data = ping_data

    def send_ping(self) -> None:
        """Send a ping packet to the server"""
        ping_message = WSMessage.outgoing(self.data, opcode=Opcode.TEXT)
        self.send(ping_message)
        self.update_last_ping()
