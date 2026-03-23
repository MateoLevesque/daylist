from textual.app import App, ComposeResult
from textual.widgets import Header, Footer
from textual.containers import Horizontal
from textual.binding import Binding

from platformdirs import user_data_dir
from pathlib import Path
import json

from datetime import date

from widgets.calendar_widget import Calendar
from widgets.todolist_widget import TaskList, Todolist


class CalendarApp(App):
    """Calendar App"""

    CSS_PATH = "style/styles.tcss"

    APP_NAME = "daylist"
    TITLE = date.today().strftime("%A")
    SUB_TITLE = date.today().strftime("%d %B %y")

    BINDINGS = [
        Binding("q", "save_quit"),
        Binding("space", "change_focus", "change focus"),
        Binding("a", "focus_input", "add task"),
    ]

    def __init__(self):
        super().__init__()

        self.tasks: dict[date, list[str]] = self.load_data()
        self.cursor = date.today()  # represent the current day

    def compose(self) -> ComposeResult:
        self.todolist = Todolist(id="todolist")
        self.calendar = Calendar(id="calendar")

        yield Header()
        yield Horizontal(self.calendar, self.todolist)
        yield Footer()

    def on_mount(self):
        # force flexoki theme by default
        self.theme = "flexoki"

        tasks_for_widgets = self.tasks.get(self.cursor, [])
        self.update_tasks(self.cursor, tasks_for_widgets)

        self.calendar.focus()

    def get_data_dir(self) -> Path:
        data_dir = Path(user_data_dir("koolkal"))
        data_dir.mkdir(parents=True, exist_ok=True)

        save_file = "tasks.json"

        return data_dir / save_file

    def load_data(self):
        file_path = self.get_data_dir()

        if not file_path.exists():
            return {}

        with open(file_path, "r") as f:
            raw = json.load(f)

        return {date.fromisoformat(d): tasks for d, tasks in raw.items()}

    def write_data(self, data):
        file_path = self.get_data_dir()

        serializable = {d.isoformat(): tasks for d, tasks in data.items()}

        with open(file_path, "w") as f:
            json.dump(serializable, f, indent=2)

    def update_tasks(self, date, tasks):
        self.todolist.cursor = date

        self.todolist.render_tasks(tasks)

        self.calendar.render_all(self.tasks)

    def action_change_focus(self):
        if self.calendar.has_focus:
            self.todolist.focus()
        else:
            self.calendar.focus()

    def action_save_quit(self):
        self.write_data(self.tasks)

        self.exit()

    def action_focus_input(self):
        self.todolist.focus_input()

    def on_calendar_cursor_moved(self, message: Calendar.CursorMoved):
        self.cursor = message.cursor

        tasks_for_widgets = self.tasks.get(self.cursor, [])
        self.update_tasks(self.cursor, tasks_for_widgets)

    def on_todolist_task_added(self, message: Todolist.TaskAdded):
        if not message.task:
            self.calendar.focus()
            return

        self.tasks.setdefault(message.date, []).append(message.task)

        tasks_for_widgets = self.tasks[message.date]
        self.update_tasks(message.date, tasks_for_widgets)

        self.calendar.focus()

    def on_task_list_task_deleted(self, message: TaskList.TaskDeleted):
        index = message.index
        tasks = self.tasks.get(self.cursor, [])

        self.remove_task(tasks, index)

    def on_task_list_editing_task(self, message: TaskList.EditingTask):
        index = message.index
        tasks = self.tasks.get(self.cursor, [])
        task = tasks[index]
        self.remove_task(tasks, index)
        self.todolist.focus_input(task)

    def remove_task(self, tasks, index):
        if len(tasks) <= 0:
            self.update_tasks(self.cursor, tasks)
            self.calendar.focus()
            return

        tasks.pop(index)
        self.update_tasks(self.cursor, tasks)
        if len(tasks) <= 0:
            self.calendar.focus()


if __name__ == "__main__":
    CalendarApp().run()
