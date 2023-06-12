import pyperclip

from textual.widgets import Button

from wsrepl.WSMessage import WSMessage


class CopyButton(Button):
    """A button that copies its data to the clipboard when pressed"""
    def __init__(self, message: WSMessage, small) -> None:
        if small:
            name = "[Click to copy]"
        else:
            name = "Click to copy"

        super().__init__(name, classes="history-btn")
        self.message = message

    def on_button_pressed(self, event: Button.Pressed) -> None:
        pyperclip.copy(self.message.msg)
        self.blur()
