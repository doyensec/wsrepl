from textual.widgets import Label

from wsrepl.WSMessage import Direction


class DirectionSign(Label):
    """A label that displays a direction sign"""
    def __init__(self, sign: Direction) -> None:
        super().__init__(sign.value, classes=f"history-sign {sign.name}")
