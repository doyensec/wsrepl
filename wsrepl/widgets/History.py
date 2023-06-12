import shutil

import textual
from textual import events
from textual import on
from textual.widgets import ListView
from textual.message import Message

from wsrepl.WSMessage import WSMessage, Direction
from wsrepl.widgets import HistoryRow


class History(ListView):
    message_width = 20
    last_highlighted = None

    def __init__(self, small: bool = False) -> None:
        self.small = small
        super().__init__()

        self.id = "history"

    def on_list_view_highlighted(self, event) -> None:

        if self.last_highlighted is not None:
            # Update the last highlighted message with its original text before the update
            self.last_highlighted.show_short()

        # Update the new highlighted message with a "changed" text
        if event.item is None:
            return

        self.last_highlighted = event.item.text
        self.last_highlighted.show_long()

    class Ready(Message):
        """Sent when the history is ready to receive messages"""
        pass

    def on_mount(self) -> None:
        self.post_message(self.Ready())

    def add_message(self, message: WSMessage) -> None:
        assert(isinstance(message, WSMessage))

        on_last_element = (self.index is None) or (self.index == len(self.children) - 1)
        self.append(HistoryRow(message, self.message_width, self.small))

        if on_last_element:
            # Scroll to the bottom if the user is already there
            self.index = len(self.children) - 1
            self.scroll_end(animate=False)

    def on_key(self, event: events.Key) -> None:
        """Vim style keybindings for scrolling through the history"""
        if event.key == 'j':
            self.action_cursor_down()
        if event.key == 'k':
            self.action_cursor_up()
        if event.key == 'g':
            self.index = 0
        if event.key == 'G':
            self.index = len(self.children) - 1

    @on(events.Resize)
    def handle_resize(self, event: events.Resize) -> None:
        """Handle terminal resize events by adjusting the width of the history message column"""
        self.message_width = self.calculate_message_width()

        # FIXME: This is ugly af, but I don't know how to update CSS styles dynamically
        for child in self.children:
            child.text.styles.width = self.message_width

    def calculate_message_width(self):
        # Get the new terminal width
        terminal_width = shutil.get_terminal_size().columns

        # Calculate the new width of the history message column
        return (terminal_width
            - 5  # The index column
            - 10 # The time column
            - 3 # The opcode column
            - 3  # The direction sign column
            - 17 # The copy button column
            - 2  # Padding on the right of the copy button
            - 1  # An additional padding for some breathing space
        )

