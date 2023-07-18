from wsrepl import Plugin

MESSAGES = [
    "hello",
    "world"
]

class Demo(Plugin):

    def init(self):
        """Initialization method that is called when the plugin is loaded.

        In this demo, we're simply populating the self.messages list with predefined messages.
        These messages will be sent to the server once a websocket connection is established.
        """
        self.messages = MESSAGES
