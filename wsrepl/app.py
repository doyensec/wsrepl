import asyncio
import inspect
import logging

from textual import events, on
from textual.app import App, ComposeResult
from textual.logging import TextualHandler
from textual.widgets import Input

from wsrepl.log import log, register_log_handler
from wsrepl.widgets import History, Parent
from wsrepl.MessageHandler import MessageHandler


logging.basicConfig(
    level="DEBUG",
    # https://textual.textualize.io/guide/devtools/
    handlers=[TextualHandler()],
)


class WSRepl(App):
    CSS_PATH = "app.css"

    def __init__(self,
                 # URL is the only required argument
                 url: str,
                 # UI settings
                 small: bool                        = False,
                 # Websocket settings
                 user_agent: str | None             = None,
                 origin: str | None                 = None,
                 cookies: list[str] | None          = None,
                 headers: list[str] | None          = None,
                 headers_file: str | None           = None,
                 ping_interval: int | float         = 24, # 0 -> disable auto ping
                 hide_ping_pong: bool               = False,
                 ping_0x1_interval: int | float     = 24, # 0 -> disable fake ping
                 ping_0x1_payload: str | None       = None,
                 pong_0x1_payload: str | None       = None,
                 hide_0x1_ping_pong: bool           = False,
                 reconnect_interval: int            =    0,
                 proxy: str | None                  = None,
                 verify_tls: bool                   = True,
                 # Other
                 initial_msgs_file: str | None      = None,
                 plugin_path: str | None            = None,
                 plugin_provided_url: bool | None   = None,
                 verbosity: int                     = 3) -> None:
        super().__init__()

        # Small UI
        self.small = small

        # Verbosity for logging level
        self.verbosity = verbosity

        # Message handler, spawns a thread to handle the websocket connection
        self.message_handler = MessageHandler(
            app=self,
            url=url, user_agent=user_agent, origin=origin, cookies=cookies, headers=headers, headers_file=headers_file,
            ping_interval=ping_interval, hide_ping_pong=hide_ping_pong,
            ping_0x1_interval=ping_0x1_interval, ping_0x1_payload=ping_0x1_payload, pong_0x1_payload=pong_0x1_payload,
            hide_0x1_ping_pong=hide_0x1_ping_pong,
            reconnect_interval=reconnect_interval, proxy=proxy, verify_tls=verify_tls,
            initial_msgs_file=initial_msgs_file, plugin_path=plugin_path, plugin_provided_url=plugin_provided_url
        )

        # These are set in compose()
        self.history = None
        self.input_widget = None

    @on(History.Ready)
    async def _history_mount(self, event: events.Mount) -> None:
        """Called when the history widget is mounted and we're ready to connect to the websocket."""
        # Set up logging, allows adding messages to UI by logging them
        register_log_handler(self, self.verbosity)
        # Pass asyncio event loop to the message handler so that it can schedule tasks on main thread
        await self.message_handler.init(asyncio.get_running_loop())

    def compose(self) -> ComposeResult:
        """Compose the Textual app layout."""
        self.history = History(self.small)
        self.input_widget = Input(placeholder="Enter websocket message", disabled=True)

        classes = ["app"]
        if self.small:
            classes.append("small")

        yield Parent(classes=classes)

    async def on_input_submitted(self, event) -> None:
        await self.message_handler.send_str(event.value)
        self.input_widget.value = ''

    def disable_input(self) -> None:
        """Disable the input widget."""
        self.input_widget.disabled = True

    def enable_input(self) -> None:
        """Enable the input widget."""
        self.input_widget.disabled = False
        self.input_widget.focus()

