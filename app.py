from datetime import date, timedelta
import calendar as c

from dateutil.relativedelta import relativedelta

from textual.app import App, ComposeResult
from textual.widget import Widget
from textual.widgets import Footer, Header, Label, Input, ListView, ListItem
from textual.containers import Container
from textual.binding import Binding


class TodoList(Widget):
    """Test"""

    can_focus = True

    BINDINGS = [
        Binding("h", "left"),
        Binding("j", "down"),
        Binding("k", "up"),
        Binding("l", "right"),
        Binding("space", "watch_calendar", "Calendar"),
    ]

    def compose(self) -> ComposeResult:
        self.task_list = ListView()
        yield self.task_list

    def action_left(self):
        pass
        # self.cursor -= timedelta(days=1)
        # self.render_calendar()

    def action_right(self):
        pass
        # self.cursor += timedelta(days=1)
        # self.render_calendar()

    def action_up(self):
        pass
        # self.cursor -= timedelta(days=7)
        # self.render_calendar()

    def action_down(self):
        pass
        # self.cursor += timedelta(days=7)
        # self.render_calendar()

    def clear(self):
        self.task_list.clear()

    def add_items(self, items):
        self.task_list.mount(*items)


class Calendar(Widget):
    """A widget to display a calendar"""

    can_focus = True

    CSS = """
    Lavel {
        dock: bottom;
    }
    """
    BINDINGS = [
        Binding("h", "left"),
        Binding("j", "down"),
        Binding("k", "up"),
        Binding("l", "right"),
        Binding("J", "down_month", "prev month"),
        Binding("K", "up_month", "next month"),
        Binding("t", "return_today", "today"),
        Binding("a", "add_task", "Add a task"),
        Binding("space", "watch_todolist", "Todo list"),
        Binding("q", "quit", show=False),
    ]

    def __init__(self):
        super().__init__()
        self.cursor = date.today()
        self.todos = {}  # {date: [tasks]}

    def compose(self) -> ComposeResult:
        self.label = Label()
        self.task_list = TodoList()
        self.task_input = Input(placeholder="Add task and press Enter")
        yield self.label
        yield self.task_list
        yield self.task_input

    def on_mount(self):
        self.render_calendar()

    def render_calendar(self):
        calendar = c.Calendar().monthdayscalendar(self.cursor.year, self.cursor.month)

        header = f"{c.month_name[self.cursor.month]} {self.cursor.year}\nMo Tu We Th Fr Sa Su\n"
        lines = []

        for week in calendar:
            line = []
            for day in week:
                if day == 0:
                    line.append("  ")
                elif day == self.cursor.day:
                    line.append(f"[reverse]{day:2}[/]")
                else:
                    line.append(f"{day:2}")
            lines.append(" ".join(line))

        tasks = self.todos.get(self.cursor, [])
        task_items = [ListItem(Label(f"- {task}")) for task in tasks]
        if not tasks:
            task_items = [ListItem(Label("[italic]No tasks for this day.[/]"))]

        self.task_list.clear()
        self.task_list.add_items(task_items)

        self.label.update(header + "\n".join(lines))

    def action_left(self):
        self.cursor -= timedelta(days=1)
        self.render_calendar()

    def action_right(self):
        self.cursor += timedelta(days=1)
        self.render_calendar()

    def action_up(self):
        self.cursor -= timedelta(days=7)
        self.render_calendar()

    def action_down(self):
        self.cursor += timedelta(days=7)
        self.render_calendar()

    def action_down_month(self):
        self.cursor += relativedelta(months=1)
        self.render_calendar()

    def action_up_month(self):
        self.cursor -= relativedelta(months=1)
        self.render_calendar()

    def action_return_today(self):
        today = date.today()
        self.cursor = self.cursor.replace(
            year=today.year, month=today.month, day=today.day
        )
        self.render_calendar()

    def action_add_task(self):
        self.task_input.focus()

    def on_input_submitted(self, event: Input.Submitted):
        task = event.value.strip()
        if task:
            self.todos.setdefault(self.cursor, []).append(task)
        self.task_input.value = ""
        self.focus()
        self.render_calendar()

    def action_watch_todo(self):
        self.task_list.focus()


class CalendarApp(App):
    """A simple and easy to use cool calendar TUI with vim motions"""

    CSS_PATH = "main.tcss"
    TITLE = date.today().strftime("%A")
    SUB_TITLE = date.today().strftime("%d %B %y")

    BINDINGS = [
        Binding("q", "quit", "Quit", show=False),
    ]

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        yield Footer()
        yield Calendar()


if __name__ == "__main__":
    app = CalendarApp()
    app.run()
