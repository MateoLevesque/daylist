from datetime import date

from textual.app import App, ComposeResult
from textual.widgets import Footer, Header
from textual.binding import Binding
from textual.containers import Horizontal
from textual.message import Message

# import widgets
from widgets.calendar_widget import Calendar
from widgets.todolist_widget import Todolist


class TaskAdded(Message):
    def __init__(self, date, task):
        self.date = date
        self.task = task
        super().__init__()


class CalendarApp(App):
    """Calendar App"""

    CSS_PATH = "style/styles.tcss"
    TITLE = date.today().strftime("%A")
    SUB_TITLE = date.today().strftime("%d %B %y")

    BINDINGS = [
        Binding("q", "quit"),
        Binding("v", "change_focus", "change focus"),
        Binding("a", "add_task", "add task"),
    ]

    tasks: dict = {
        date(2026, 3, 10): ["test"],
        date(2026, 4, 15): ["test"],
    }

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        yield Horizontal(
            Calendar(id="calendar"),
            Todolist(id="todolist"),
        )
        yield Footer()

    def on_mount(self):
        self.calendar_id = self.query_one("#calendar")
        self.todolist_id = self.query_one("#todolist")
        self.calendar_id.focus()

        self.theme = "flexoki"

    def action_change_focus(self):
        if self.calendar_id.has_focus:
            self.todolist_id.focus()
        else:
            self.calendar_id.focus()

    def action_add_task(self):
        self.query_one(Todolist).action_focus_input()

    def on_task_added(self, message: TaskAdded):
        self.tasks.setdefault(message.date, []).append(message.task)
        self.query_one(Calendar).render_calendars()


if __name__ == "__main__":
    CalendarApp().run()
