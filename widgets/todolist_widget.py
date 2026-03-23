from textual.widget import Widget
from textual.message import Message
from textual.binding import Binding
from textual.app import ComposeResult
from textual.widgets import Input, ListView, ListItem, Label

from datetime import date


class TaskList(ListView):
    class TaskDeleted(Message):
        def __init__(self, index: int) -> None:
            self.index = index
            super().__init__()

    class EditingTask(Message):
        def __init__(self, index: int) -> None:
            self.index = index
            super().__init__()

    BINDINGS = [
        Binding("j", "cursor_down", "Next task"),
        Binding("k", "cursor_up", "Previous task"),
        Binding("r", "remove_task", "Remove task"),
        Binding("e", "edit_task", "Edit task"),
    ]

    def action_remove_task(self):
        if not self.highlighted_child:
            return

        self.post_message(self.TaskDeleted(self.index))

    def action_edit_task(self):
        self.post_message(self.EditingTask(self.index))


class Todolist(Widget):
    """Todolist widget"""

    class TaskAdded(Message):
        def __init__(self, date: date, task: str):
            self.date = date
            self.task = task
            super().__init__()

    can_focus = True

    def compose(self) -> ComposeResult:
        self.task_input = Input(
            placeholder="Add a task then press Enter...",
            id="task_input",
        )

        self.task_list = TaskList(id="task_list")

        yield self.task_input
        yield self.task_list

    def on_mount(self):
        self.cursor = date.today()

    def focus_input(self, content: str = ""):
        self.task_input.focus()
        self.task_input.value = content

    def render_tasks(self, tasks):
        index = self.task_list.index
        self.task_list.clear()

        if tasks:
            items = [ListItem(Label(task)) for task in tasks]
        else:
            items = [ListItem(Label("[italic]No tasks for this day[/italic]"))]

        for item in items:
            self.task_list.mount(item)

        self.task_list.index = index

    def on_focus(self):
        self.task_list.focus()
        self.task_list.index = 0

    def on_input_submitted(self, event: Input.Submitted):
        task = event.value.strip()

        self.post_message(self.TaskAdded(self.cursor, task))

        event.input.value = ""
