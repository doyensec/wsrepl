from datetime import datetime

from textual.containers import Horizontal
from textual.widgets import ListItem, Label
from textual.app import ComposeResult

from wsrepl.WSMessage import WSMessage
from wsrepl.widgets import CopyButton, DirectionSign, FormattedMessage, HistoryIndex


class HistoryRow(ListItem):
    """A row in the history widget"""

    def __init__(self, message: WSMessage, message_width: int = 20, small: bool = False) -> None:
        # Just an auto-incremental counter
        self.index = HistoryIndex()

        # Label with current time
        current_time = datetime.now().strftime("%H:%M:%S")
        self.time = Label(current_time, classes="history-time")

        # Label with the opcode
        self.opcode = Label(message.opcode_hex, classes="history-opcode")

        # The direction sign (> and < for sent and received messages, respectively, ! for errors)
        self.sign = DirectionSign(message.direction)

        # The message itself, pretty printed and syntax highlighted
        self.text = FormattedMessage(message, message_width)

        # A button that copies the message to the clipboard when pressed
        self.button = CopyButton(message, small)

        self.row = Horizontal(self.index, self.time, self.opcode, self.sign, self.text, self.button,
                              classes=message.direction.name)

        super().__init__(self.row)

    def compose(self) -> ComposeResult:
        yield self.row
