from wsrepl import Plugin
from wsrepl.WSMessage import WSMessage

import json
import requests

class Demo(Plugin):

    def init(self):
        """Initialization method that is called when the plugin is loaded.

        In this example, we are dynamically populating self.messages list by getting a session token from a HTTP endpoint.
        This is a typical scenario when interacting with APIs that require user authentication before the WebSocket connection is established.
        """

        # Here we simulate an API request to get a session token by supplying a username and password.
        # For the demo, we're using a dummy endpoint "https://hb.cran.dev/uuid" that returns a UUID.
        # In a real-life scenario, replace this with your own authentication endpoint and provide necessary credentials.
        token = requests.get("https://hb.cran.dev/uuid").json()["uuid"]

        # The acquired session token is then used to populate self.messages with an authentication message.
        # The exact format of this message will depend on your WebSocket server requirements.
        self.messages = [
            json.dumps({
                "auth": "session",
                "sessionId": token
            })
        ]

    async def on_connect(self) -> None:
        """Called when the websocket connection is established.

        In this demo, we're simply logging the successful connection event.
        """
        self.log.info("Successfully connected to the server with the session token!")

    async def on_message_received(self, message: WSMessage) -> None:
        """Called when a (text) message is received from the server.

        In this demo, we're logging the original message received from the server.
        """
        self.log.info(f"Received message from server: {message.msg}")
        # Further processing of the message can go here

    async def on_error(self, exception: Exception) -> None:
        """Called when an error message is received from the server

        In this demo, we're logging the error.
        """
        self.log.error(f"An error occurred: {exception}")
        # Additional error handling can go here
