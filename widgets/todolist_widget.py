from textual.app import ComposeResult
from textual.widget import Widget
from textual.widgets import Input
from textual.binding import Binding


class Todolist(Widget):
    """Todolist widget"""

    can_focus = True

    BINDINGS = []

    def compose(self) -> ComposeResult:
        self.task_input = Input(
            id="task_input", placeholder="Add a task then press Enter..."
        )
        yield self.task_input

    def on_mount(self):
        pass

    def action_focus_input(self):
        self.task_input.focus()

    def on_input_submitted(self, event: Input.Submitted):
        task = event.value
        calendar = self.app.query_one(Calendar)
        date = calendar.cursor

        if not task.strip():
            event.input.value = ""
            calendar.focus()
            return

        self.post_message(TaskAdded(date, task))
        event.input.value = ""
        calendar.render_calendars()
        calendar.focus()
