import asyncio
import websocket
import time

## websocket-client does not support async, so we need to use threads.
## At the same type Textual isn't thread-safe, so we need to take care
## to only communicate with it through post_message:
## https://textual.textualize.io/guide/workers/#posting-messages


class WebsocketConnection:
    def __init__(self, async_handler, **init_args) -> None:
        # Async MessageHandler that will actually handle all messages
        self.async_handler = async_handler
        # Main asyncio event loop where the async handlers runs (set during init())
        self.event_loop = None

        self._ws = websocket.WebSocketApp(
            on_open=self.on_open,
            on_message=self.on_message,
            on_data=self.on_data,
            on_error=self.on_error,
            on_close=self.on_close,
            on_ping=self.on_ping,
            on_pong=self.on_pong,
            on_cont_message=self.on_cont_message,
            **init_args)
        self.init_args = init_args

    def run_forever(self) -> None:
        """Connect to the websocket and reconnect if disconnected."""
        self.log(f"Websocket init arguments: {self.init_args}")
        self.log(f"run_forever arguments: {self.connect_args}")

        timeout = self.connect_args['reconnect']
        while True:
            try:
                # Blocking call, will return when the websocket is closed
                # It returns False if the self._ws.close() was called or KeyboardInterrupt was raised
                there_were_errors = self._ws.run_forever(**self.connect_args) == False
            except:
                there_were_errors = True
            # TODO: Should we exit on there_were_errors or any other condition?

            self.log(f"Lost connection, reconnecting in {timeout} seconds")
            time.sleep(timeout)

    def _async_proxy(self, func_name, *args, **kwargs):
        """Run the given function in the asyncio event loop."""
        func = getattr(self.async_handler, func_name)
        return asyncio.run_coroutine_threadsafe(func(*args, **kwargs), self.event_loop)

    # Blocks the websocket thread until the async handler is done, use sparingly
    def _async_proxy_block(self, func_name, *args, **kwargs):
        """Run the given function in the asyncio event loop and block until it's done."""
        future = self._async_proxy(func_name, *args, **kwargs)
        future.result()

    def on_open(self, _) -> None:
        """Executed when the websocket is opened (also after reconnect)."""
        self.log("Connected to websocket")
        self._async_proxy('on_connect')

    def on_message(self, _, message: str) -> None:
        """Executed when a message is received. Gets fired *on text messages only*."""
        self.log(f"Message: {message}")
        self._async_proxy('on_message_received', message)

    def on_data(self, _, data: str | bytes, opcode: int, fin: bool) -> None:
        """Executed when a message is received. Gets fired *on text, binary and continuation messages*.

        Execution order:
          - text and continuation messages: this callback will be called *before* on_message and on_cont_message
          - binary messages: this callback is the only one that will be called

        Type of data:
          - text messages: decoded automatically (from utf-8), so you get a string
          - binary messages: not decoded, so you get a bytes object

        The other parameters are the same as the ones of the websocket-client callback:
          - opcode: the websocket opcode of the message: 0x1 for text, 0x2 for binary, 0x0 for continuation
          - fin: True if the message is the last one of the frame, False otherwise.
        """
        self.log(f"Data: {data}")
        self._async_proxy('on_data_received', data, opcode, fin)

    def on_error(self, _, exception: Exception) -> None:
        self.log(f"Error: {exception}")
        self._async_proxy('on_error', exception)

    def on_close(self, _, status_code, reason) -> None:
        """Executed *AFTER* the websocket is closed."""
        self.log(f"Closed: {status_code} {reason}")
        self._async_proxy('on_disconnect', status_code, reason)

    def on_ping(self, _, data) -> None:
        self.log(f"Ping: {data}")
        self._async_proxy('on_ping_received', data)

    def on_pong(self, _, data) -> None:
        self.log(f"Pong: {data}")
        self._async_proxy('on_pong_received', data)

    def on_cont_message(self, _, data, fin) -> None:
        self.log(f"Continuation message: {data}")
        self._async_proxy('on_cont_message', data, fin)

    # NOTE: This is the only function that will be called from the main thread (that runs async UI code), everything
    # else works in the dedicated websocket thread, but all handlers proxy requests to the async handlers in the main thread.
    def send(self, data: str | bytes, opcode: int = 0x1) -> None:
        """Send a message to the websocket. Default opcode is 0x1 (text) and expects utf-8 string."""
        self.log(f"Sending message: {data}")
        self._ws.send(data, opcode)

    def log(self, msg: str) -> None:
        """Log the given message."""
        self._async_proxy('log', msg)
