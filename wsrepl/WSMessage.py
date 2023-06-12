import json
from enum import Enum
from base64 import b64decode, b64encode

from rich.syntax import Syntax
from rich.markup import escape

from wsrepl.constants import ACCENT_COLOR


class Direction(Enum):
    """Direction of a websocket message."""
    INCOMING   = '<'  # Received message
    OUTGOING   = '>' # Sent message
    DEBUG      = '.' # Debug message
    INFO       = '?' # Information message
    WARNING    = '#' # Warning message
    ERROR      = '!' # Error message

class Opcode(Enum):
    """Opcode of a websocket message."""
    CONTINUATION = 0x0
    TEXT         = 0x1
    BINARY       = 0x2
    CLOSE        = 0x8
    PING         = 0x9
    PONG         = 0xA

class WSMessage:
    """A websocket message.

    The original message is stored in `msg`, and optionally two more versions can be provided:

    - `short` is a shortened version of the message, that is displayed in the history widget
    - `long` is a formatted version of the message, that is displayed in the message details widget

    If these are not provided, the original message is used for `short` and JSON formatted version is used for `long`.
    """
    _short_value = None
    _long_value  = None
    is_fake_ping_pong = False

    def __init__(self, msg: str, direction: Direction, hidden = False, is_binary: bool = False, is_ping: bool = False,
                 is_pong: bool = False, is_continuation: bool = False, opcode: int | Opcode = Opcode.TEXT, fin: bool = True) -> None:
        self.msg: str = msg
        self.direction: Direction = direction

        # Hide the message from the history
        self.is_hidden: bool = hidden

        # Set the opcode and fin flags
        self.opcode: Opcode = opcode if isinstance(opcode, Opcode) else Opcode(opcode)
        if is_binary:
            self.is_binary = True
        if is_ping:
            self.is_ping = True
        if is_pong:
            self.is_pong = True
        if is_continuation:
            self.is_continuation = True

        # FIN flag means this is the last frame in a message
        self.fin : bool = fin

    @property
    def is_binary(self) -> bool:
        return self.opcode == Opcode.BINARY

    @is_binary.setter
    def is_binary(self, value: bool) -> None:
        self.opcode = Opcode.BINARY if value else Opcode.TEXT

    @property
    def is_ping(self) -> bool:
        return self.opcode == Opcode.PING

    @is_ping.setter
    def is_ping(self, value: bool) -> None:
        self.opcode = Opcode.PING if value else Opcode.TEXT

    @property
    def is_pong(self) -> bool:
        return self.opcode == Opcode.PONG

    @is_pong.setter
    def is_pong(self, value: bool) -> None:
        self.opcode = Opcode.PONG if value else Opcode.TEXT

    @property
    def is_continuation(self) -> bool:
        return self.opcode == Opcode.CONTINUATION

    @is_continuation.setter
    def is_continuation(self, value: bool) -> None:
        self.opcode = Opcode.CONTINUATION if value else Opcode.TEXT

    @property
    def short(self) -> str:
        return escape(self._short)

    @short.setter
    def short(self, value: str) -> None:
        self._short_value = value

    @property
    def _short(self) -> str:
        """Not escaped version of the short message, for internal consumption."""
        if self._short_value:
            return self._short_value

        if isinstance(self.msg, bytes):
            try:
                decoded = self.msg.decode('utf-8')
                return decoded
            except:
                return 'b64:' + b64encode(self.msg).decode('utf-8')
        elif isinstance(self.msg, str):
            return self.msg
        else:
            raise ValueError('Message is not a string or bytes')

    @property
    def long(self) -> str:
        msg = self._long

        # Try to format the message as JSON, if it fails, just return the original message
        try:
            parsed = json.loads(msg)
            pretty = json.dumps(parsed, indent=4)
            return Syntax(pretty, lexer="json", theme='native', background_color=ACCENT_COLOR)
        except:
            return escape(msg)

    @long.setter
    def long(self, value: str) -> None:
        self._long_value = value

    @property
    def _long(self) -> str:
        """Not escaped version of the long message, for internal consumption."""
        return self._long_value if self._long_value else self._short

    @property
    def binary(self) -> bytes:
        """Return the binary message as bytes (check self.is_binary flag first)."""
        if self.is_binary:
            # Validate that the message is a base64 string by checking 'b64:' prefix
            if not self.msg.startswith('b64:'):
                raise ValueError('Binary message does not start with "b64:" prefix')
            return b64decode(self.msg[4:])
        return self.msg.encode()

    # Convenient methods for creating messages
    @classmethod
    def incoming(cls, msg: str, *args, **kwargs) -> 'WSMessage':
        return cls(msg, Direction.INCOMING, *args, **kwargs)

    @classmethod
    def outgoing(cls, msg: str, *args, **kwargs) -> 'WSMessage':
        return cls(msg, Direction.OUTGOING, *args, **kwargs)

    @classmethod
    def ping_out(cls, msg: str = "") -> 'WSMessage':
        return cls(msg, Direction.OUTGOING, is_ping=True)

    @classmethod
    def ping_in(cls, msg: str = "") -> 'WSMessage':
        return cls(msg, Direction.INCOMING, is_ping=True)

    @classmethod
    def pong_out(cls, msg: str = "") -> 'WSMessage':
        return cls(msg, Direction.OUTGOING, is_pong=True)

    @classmethod
    def pong_in(cls, msg: str = "") -> 'WSMessage':
        return cls(msg, Direction.INCOMING, is_pong=True)

    @classmethod
    def debug(cls, msg: str) -> 'WSMessage':
        return cls(msg, Direction.DEBUG)

    @classmethod
    def info(cls, msg: str) -> 'WSMessage':
        return cls(msg, Direction.INFO)

    @classmethod
    def warning(cls, msg: str) -> 'WSMessage':
        return cls(msg, Direction.WARNING)

    @classmethod
    def error(cls, msg: str) -> 'WSMessage':
        return cls(msg, Direction.ERROR)

    @property
    def is_traffic(self) -> bool:
        """Return True if this message is a websocket traffic message."""
        return self.direction in (Direction.INCOMING, Direction.OUTGOING)

    @property
    def opcode_hex(self) -> str:
        """Return the opcode as a hex string."""
        if not self.is_traffic:
            return "-"

        opcode = self.opcode.value
        return f"0x{opcode:X}"
