from textual.widgets import Label


class HistoryIndex(Label):
    """A label that counts how many instances of it have been created"""
    __internal_counter = 0

    def __init__(self):
        HistoryIndex.__internal_counter += 1
        super().__init__(str(self.__internal_counter), classes="history-index")

