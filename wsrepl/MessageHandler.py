import asyncio
import textual
import threading
import ssl
from collections import OrderedDict
from urllib.parse import urlparse

from wsrepl.log import log
from wsrepl.utils import load_plugin
from wsrepl.WSMessage import WSMessage, Direction
from wsrepl.WebsocketConnection import WebsocketConnection
from wsrepl.PingThread import PingThread
from wsrepl.Ping0x1Thread import Ping0x1Thread


class MessageHandler:
    def __init__(self,
                 app: textual.app.App,
                 url: str,
                 user_agent: str | None             = None,
                 origin: str | None                 = None,
                 cookies: list[str] | None          = None,
                 headers: list[str] | None          = None,
                 headers_file: str | None           = None,
                 ping_interval: int | float         = 24,
                 hide_ping_pong: bool               = False,
                 ping_0x1_interval: int | float     = 24,
                 ping_0x1_payload: str | None       = None,
                 pong_0x1_payload: str | None       = None,
                 hide_0x1_ping_pong: bool           = False,
                 reconnect_interval: int            = 0,
                 proxy: str | None                  = None,
                 verify_tls: bool                   = True,
                 initial_msgs_file: str | None      = None,
                 plugin_path: str | None            = None,
                 plugin_provided_url: bool | None   = None) -> None:

        self.app = app
        self.plugin = load_plugin(plugin_path)(message_handler=self)
        if(plugin_provided_url):
            try:
                url = self.plugin.url
                print("URL from plugin = " + url)
            except:
                print("Failed to get URL path from plugin. Exiting...")
                exit()

        self.initial_messages: list[WSMessage] = self._load_initial_messages(initial_msgs_file)
        processed_headers: OrderedDict = self._process_headers(headers, headers_file, user_agent, origin, cookies)

        self._ws = WebsocketConnection(
            # Stuff WebsocketConnection needs to call back to us
            async_handler=self,
            # WebSocketApp args
            url=url,
            header=processed_headers
        )

        # Args passed to websocket.WebSocketApp.run_forever()
        if isinstance(proxy, str):
            proxy = 'http://' + proxy if '://' not in proxy else proxy

        self._ws.connect_args = {
            'suppress_origin': 'Origin' in processed_headers,
            'sslopt': {'cert_reqs': ssl.CERT_NONE} if not verify_tls else {},
            'ping_interval': 0, # Disable websocket-client's autoping because it doesn't provide feedback
            'http_proxy_host': urlparse(proxy).hostname if proxy else None,
            'http_proxy_port': urlparse(proxy).port if proxy else None,
            'proxy_type': 'http' if proxy else None,
            'reconnect': reconnect_interval
        }

        self.is_stopped = threading.Event()

        # Regular ping thread, conforming to RFC 6455 (ping uses opcode 0x9, pong uses 0xA, data is arbitrary but must be the same)
        if ping_interval:
            self.ping_thread = PingThread(self, ping_interval, self.is_stopped)
        else:
            self.ping_thread = None

        # Fake ping thread, using opcode 0x (TEXT) and arbitrary ping / pong messages
        self.ping_0x1_interval = ping_0x1_payload and pong_0x1_payload and ping_0x1_interval
        self.ping_0x1_data = ping_0x1_payload or self.plugin.ping_0x1_payload
        self.pong_0x1_data = pong_0x1_payload or self.plugin.pong_0x1_payload
        if self.ping_0x1_interval:
            self.ping_0x1_thread = Ping0x1Thread(self, ping_0x1_interval, ping_0x1_payload, self.is_stopped)
        else:
            self.ping_0x1_thread = None

        # Whether to show ping / pong messages in the history
        self.hide_ping_pong = hide_ping_pong
        self.hide_0x1_ping_pong = hide_0x1_ping_pong

    def _process_headers(self, headers: list[str] | None, headers_file: str | None,
                         user_agent: str | None, origin: str | None, cookies: list[str]) -> OrderedDict:
        """Process headers and return an OrderedDict of headers."""
        result = OrderedDict()
        cookie_headers = []

        # Blacklisted headers that should be removed to avoid duplication
        blacklisted_headers = [
            "Host",
            "Upgrade",
            "Connection"
        ]

        # Headers from command line take precedence
        if headers:
            for header in headers:
                name, value = map(str.strip, header.split(":", 1))
                if name in blacklisted_headers:
                    continue

                if name.lower().strip() == "cookie":
                    cookie_headers.append(value.strip())
                else:
                    result[name] = value

        # Headers from file are next
        if headers_file:
            with open(headers_file, "r") as f:
                for header in f.read().splitlines():
                    name, value = map(str.strip, header.split(":", 1))
                    if name in blacklisted_headers:
                        continue

                    if name.lower().strip() == "cookie":
                        cookie_headers.append(value.strip())
                    elif name not in result:
                        result[name] = value

        # Add User-Agent if not already present
        if user_agent and "User-Agent" not in result:
            result["User-Agent"] = user_agent

        # Add Origin if not already present
        if origin and "Origin" not in result:
            result["Origin"] = origin

        # Merge and add Cookies
        if cookies:
            cookie_value = "; ".join(cookies)
            if cookie_headers:
                result['Cookie'] = cookie_value + "; " + "; ".join(cookie_headers)
            else:
                result['Cookie'] = cookie_value

        return result

    def _load_initial_messages(self, initial_msgs_file: str | None) -> list[WSMessage]:
        messages = []
        if initial_msgs_file:
            with open(initial_msgs_file, "r") as f:
                for msg in f.readlines():
                    messages.append(WSMessage.outgoing(msg.strip()))
        return messages

    async def init(self, event_loop) -> None:
        """Start the websocket thread."""
        # Run self._ws.run_forever in a separate thread
        self._ws.event_loop = event_loop
        threading.Thread(target=self._ws.run_forever, daemon=True).start()

        # Start the ping thread
        if self.ping_thread:
            self.ping_thread.event_loop = asyncio.get_running_loop()
            self.ping_thread.start()

        if self.ping_0x1_thread:
            self.ping_0x1_thread.event_loop = asyncio.get_running_loop()
            self.ping_0x1_thread.start()

    async def on_connect(self) -> None:
        """Called when the websocket connects."""
        log.info("Websocket connected")
        self.is_stopped.clear()

        await self._send_initial_messages()
        await self.plugin._on_connect()

        # Enable the input widget and focus it
        self.app.enable_input()

    async def _send_initial_messages(self):
        """Send the initial messages to the server"""
        for message in self.initial_messages:
            await self.send(message)

    async def on_disconnect(self, status_code, reason) -> None:
        """Called when the websocket disconnects."""
        log.error(f"Websocket disconnected with status code {status_code} and reason {reason}")

        self.is_stopped.set()
        await self.plugin.on_disconnect()

    async def on_error(self, exception: Exception) -> None:
        """Called when the websocket encounters an error."""
        log.error(f"Websocket error: {exception}")
        await self.plugin.on_error(exception)

    async def on_message_received(self, msg: str) -> bool:
        """Called when the websocket receives a text message."""
        message = WSMessage.incoming(message)

        await self.plugin.on_message_received(message)
        await self.plugin.after_message_received(message)

    # NOTE: This is what sends received messages to the history for 1) text; 2) binary and 3) continuation frames
    async def on_data_received(self, data: str | bytes, opcode: int, fin: bool) -> None:
        log.debug(f"Received data: {data}, opcode: {opcode}, fin: {fin}")

        message = WSMessage.incoming(data, opcode=opcode, fin=fin)
        if opcode == 0x1 and data in (self.ping_0x1_data, self.pong_0x1_data):
            message.is_fake_ping_pong = True
            if self.hide_0x1_ping_pong:
                message.is_hidden = True

        await self.plugin.on_message_received(message)
        if not message.is_hidden:
            self.app.history.add_message(message)
        await self.plugin.after_message_received(message)

        # Auto respond with a fake pong if the received message is a fake ping
        if self.ping_0x1_data and self.pong_0x1_data and opcode == 0x1 and data == self.ping_0x1_data:
            log.debug("Received fake ping - responding with fake pong")
            pong_message = WSMessage.outgoing(self.pong_0x1_data, opcode=0x1)
            pong_message.is_fake_ping_pong = True
            if self.hide_0x1_ping_pong:
                pong_message.is_hidden = True
            await self.send(pong_message)

    async def on_ping_received(self, data: str | bytes) -> None:
        """Called when the websocket receives a ping."""
        log.debug("Received ping")
        message = WSMessage.ping_in(data)
        await self.plugin.on_ping_received(data)
        if not message.is_hidden and not self.hide_ping_pong:
            self.app.history.add_message(message)
        await self.plugin.after_ping_received(data)

        # Auto respond with a pong
        log.debug("Responding with pong")
        pong_message = WSMessage.pong_out(data)
        await self.send(pong_message)

    async def on_pong_received(self, data: str | bytes) -> None:
        """Called when the websocket receives a pong."""
        message = WSMessage.pong_in(data)
        await self.plugin.on_pong_received(data)
        if not message.is_hidden and not self.hide_ping_pong:
            self.app.history.add_message(message)
        await self.plugin.after_pong_received(data)

    async def on_continuation_received(self, data: str | bytes, fin: bool) -> None:
        """Called when the websocket receives a continuation frame."""
        message = WSMessage.incoming(data, is_continuation=True, fin=fin)
        await self.plugin.on_continuation_received(data)
        if not message.is_hidden:
            self.app.history.add_message(message)
        await self.plugin.after_continuation_received(data)

    async def send(self, message: WSMessage) -> None:
        """Send a message to the server and push it to the history."""
        log.debug(f"Sending message: {message.msg}")
        skip_msg_if_false = await self.plugin.on_message_sent(message)
        if skip_msg_if_false == False:
            message.direction = Direction.INFO
            message.short = f"Message skipped: {message.short}"
        else:
            # NOTE: This should be the only place where we send messages!
            self._ws.send(message.msg, opcode=message.opcode.value)

        # Decide whether to hide the message or not
        if (message.is_ping or message.is_pong) and self.hide_ping_pong:
            message.is_hidden = True

        if message.is_fake_ping_pong and self.hide_0x1_ping_pong:
            message.is_hidden = True

        if not message.is_hidden:
            self.app.history.add_message(message)

        # TODO: Spawn this without await maybe?
        await self.plugin.after_message_sent(message)

    async def send_str(self, msg: str) -> None:
        """Send a string message to the server."""
        await self.send(WSMessage.outgoing(msg))

    async def log(self, msg: str) -> None:
        """Log a message to the history."""
        log.debug(msg)
