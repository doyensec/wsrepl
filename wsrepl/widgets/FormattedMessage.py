from textual.widgets import Label

from wsrepl.WSMessage import WSMessage


class FormattedMessage(Label):
    """A label that formats its data and displays it"""

    def __init__(self, message: WSMessage, message_width: int = 20) -> None:
        self.message = message
        super().__init__(message.short, classes="history-text")

        # History widget has a handler that gets triggered on resize, iterates over all messages and fixes their width
        self.styles.width = message_width

    def show_short(self) -> str:
        self.remove_class('selected')
        return self.update(self.message.short)

    def show_long(self) -> str:
        self.add_class('selected')
        return self.update(self.message.long)

