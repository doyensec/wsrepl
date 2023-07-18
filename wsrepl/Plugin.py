import asyncio

from wsrepl.log import log
from wsrepl.WSMessage import WSMessage

class Plugin:
    def __init__(self, message_handler) -> None:
        self.log = log
        self.handler = message_handler
        self.messages = []
        self.ping_0x1_payload = ""
        self.pong_0x1_payload = ""
        self.init()

    def init(self):
        """Called when the plugin is loaded"""
        pass

    async def send(self, message: WSMessage) -> None:
        """Send a message to the server"""
        await self.handler.send(message)

    async def send_str(self, msg: str) -> None:
        """Send a string to the server"""
        message = WSMessage.outgoing(msg)
        await self.send(message)

    async def on_connect(self) -> None:
        """Called when the websocket connection is established"""
        pass

    async def _on_connect(self) -> None:
        """Internal method to send messages from the self.messages list and call the public on_connect hook"""
        await self.on_connect()
        if self.messages:
            self.log.debug(f"Sending initial messages ({len(self.messages)})")
            for msg in self.messages:
                if msg.strip() == "":
                    # Empty message signals 1 second pause
                    self.log.debug("Empty message, sleeping for 1 second")
                    await asyncio.sleep(1)
                else:
                    self.log.debug(f"Sending initial message: {msg}")
                    await self.send_str(msg)
        await self.after_connect()

    async def after_connect(self) -> None:
        pass

    async def on_disconnect(self) -> None:
        """Called when the websocket connection is lost"""
        pass

    # Message frame
    async def on_message_received(self, message: WSMessage) -> None:
        """Called when a (text) message is received from the server. Can modify the message before it is pushed to the history.

        - message.msg contains the original message received from the server (should not be modified)
        - message.short contains a shortened version of the message that will be displayed in the history (can be overwritten)
        - message.long contains a long version of the message that will be displayed upon selection (can be overwritten)

        - message.is_hidden - if True, the message will not be displayed in the history

        ! Do not use this hook to send responses to the server. Use the after_message_received hook instead !
        """
        pass

    async def after_message_received(self, message: WSMessage) -> None:
        """Called after a message is received from the server. Use this hook to send responses to the server."""
        pass

    # Data frame
    async def on_data_received(self, message: WSMessage) -> None:
        """Called before on_message_received is fired, and also on binary messages and continuation frames."""
        pass

    async def after_data_received(self, message: WSMessage) -> None:
        """Called after on_message_received is fired, and also on binary messages and continuation frames."""
        pass

    # Continuation frame
    async def on_continuation_received(self, message: WSMessage) -> None:
        """Called when a continuation frame is received from the server."""
        pass

    async def after_continuation_received(self, message: WSMessage) -> None:
        """Called after a continuation frame is received from the server."""
        pass

    # Ping frame (received)
    async def on_ping_received(self, message: WSMessage) -> None:
        """Called when a ping frame is received from the server."""
        pass

    async def after_ping_received(self, message: WSMessage) -> None:
        """Called after a ping frame is received from the server."""
        pass

    # Pong frame (received)
    async def on_pong_received(self, message: WSMessage) -> None:
        """Called when a pong frame is received from the server."""
        pass

    async def after_pong_received(self, message: WSMessage) -> None:
        """Called after a pong frame is received from the server."""
        pass

    # Sending messages to the server
    async def on_message_sent(self, message: WSMessage) -> bool | None:
        """Called when a message is sent to the server. Can modify the message before it is sent and pushed to history.

        See on_message_received for more information on the message object.

        Similary to on_message_received, setting message.is_hidden to True will prevent the message from being displayed in the history.

        Returning False from this hook will prevent the message from being sent to the server.

        ! Do not use this hook to send more messages to the server. Use the after_message_sent hook instead !
        """
        pass

    async def after_message_sent(self, message: WSMessage) -> None:
        """Called after a message is sent to the server. Use this hook to send responses to the server."""
        pass

    async def on_error(self, exception: Exception) -> None:
        """Called when an error message is received from the server"""
        pass
