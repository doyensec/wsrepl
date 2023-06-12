import asyncio
import time
import threading
from datetime import datetime
from wsrepl.WSMessage import WSMessage


class PingThread(threading.Thread):
    def __init__(self,
                 message_handler: 'MessageHandler',
                 ping_interval: int | float,
                 is_stopped: threading.Event) -> None:
        super().__init__(daemon=True)

        self.ping_interval = ping_interval
        self.message_handler = message_handler
        self.is_stopped = is_stopped
        self.update_last_ping()

    def update_last_ping(self) -> None:
        """Updates last ping time"""
        self.last_ping = datetime.now()

    def seconds_since_last_ping(self) -> int:
        """Returns number of seconds since last ping"""
        return (datetime.now() - self.last_ping).seconds

    def run(self) -> None:
        self.log(f"Starting ping thread with interval of {self.ping_interval} seconds")
        while True:
            seconds_passed = self.seconds_since_last_ping()
            self.log(f"Seconds passed since last ping: {seconds_passed}")
            if seconds_passed < self.ping_interval:
                # Wait for ping interval using time.sleep
                seconds_to_sleep = max(1, self.ping_interval - seconds_passed)
                time.sleep(seconds_to_sleep)
                continue

            # Check if thread is stopped
            if self.is_stopped.is_set():
                self.log(f"Ping thread is stopped, sleeping for {self.ping_interval} seconds")
                self.update_last_ping()
                continue

            # Send ping packet
            self.send_ping()

    def log(self, msg: str) -> None:
        """Log a message"""
        asyncio.run_coroutine_threadsafe(
            self.message_handler.log(msg),
            self.event_loop)

    def send(self, *args, **kwargs) -> None:
        """Send a message to the server"""
        return asyncio.run_coroutine_threadsafe(
            self.message_handler.send(*args, **kwargs),
            self.event_loop)

    def send_ping(self) -> None:
        """Send a ping packet to the server"""
        ping_message = WSMessage.ping_out()
        self.send(ping_message)
        self.update_last_ping()
