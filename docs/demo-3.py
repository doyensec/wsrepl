from wsrepl import Plugin

import json
from wsrepl.WSMessage import WSMessage

class Demo(Plugin):

    async def on_message_sent(self, message: WSMessage) -> None:
        """This method is called on every message that the user enters into the REPL.
        It modifies the message before it's sent to the server by wrapping it into a specific JSON format.

        Here we're demonstrating how to wrap user messages into a more complex structure that some websocket servers might require.
        """

        # Grab the original message entered by the user
        original = message.msg

        # Prepare a more complex message structure that our server requires.
        # The exact structure here will depend on your websocket server's requirements.
        message.msg = json.dumps({
            "type": "message",
            "data": {
                "text": original
            }
        })

        # Short and long versions of the message are used for display purposes in REPL UI.
        # By default they are the same as 'message.msg', but here we modify them for better UX.
        message.short = original
        message.long = message.msg


    async def on_message_received(self, message: WSMessage) -> None:
        """This method is called every time a message is received from the server.
        It extracts the core message out of the JSON object received from the server.

        Here we're demonstrating how to unwrap the received messages and display more user-friendly information.
        """

        # Get the original message received from the server
        original = message.msg

        try:
            # Try to parse the received message and extract meaningful data.
            # The exact structure here will depend on your websocket server's responses.
            message.short = json.loads(original)["data"]["text"]
        except:
            # In case of a parsing error, let's inform the user about it in the history view.
            message.short = "Error: could not parse message"

        # Show the original message when the user focuses on it in the UI.
        message.long = original
