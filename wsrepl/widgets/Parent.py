from textual.widget import Widget
from textual.app import ComposeResult

class Parent(Widget):
    """A parent class for all app widgets, to make them easier to style via CSS"""
    def __init__(self, classes: list[str]):
        class_string = " ".join(classes)
        super().__init__(classes=class_string)

    def compose(self) -> ComposeResult:
        yield self.app.history
        yield self.app.input_widget
