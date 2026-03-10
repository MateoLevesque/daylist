from textual.widget import Widget
from textual.message import Message
from textual.binding import Binding
from textual.app import ComposeResult
from textual.widgets import Input, ListView, ListItem, Label

from datetime import date


class Todolist(Widget):
    """Todolist widget"""

    class TaskAdded(Message):
        def __init__(self, date: date, task: str):
            self.date = date
            self.task = task
            super().__init__()

    can_focus = True

    BINDINGS = [
        Binding("j", "next_task"),
        Binding("k", "prev_task"),
    ]

    def compose(self) -> ComposeResult:
        self.task_input = Input(
            placeholder="Add a task then press Enter...",
            id="task_input",
        )

        self.task_list = ListView(id="task_list")

        yield self.task_input
        yield self.task_list

    def on_mount(self):
        self.cursor = date.today()

    def focus_input(self):
        self.task_input.focus()

    def render_tasks(self, tasks):
        self.task_list.clear()

        if tasks:
            items = [ListItem(Label(task)) for task in tasks]
        else:
            items = [ListItem(Label("[italic]No tasks for this day[/italic]"))]

        for item in items:
            self.task_list.mount(item)

    def on_input_submitted(self, event: Input.Submitted):

        task = event.value.strip()

        if not task:
            event.input.value = ""
            return

        self.post_message(self.TaskAdded(self.cursor, task))

        event.input.value = ""
