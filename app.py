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
        Binding("j", "cursor_down"),
        Binding("k", "cursor_up"),
    ]

    def compose(self) -> ComposeResult:
        self.task_list = ListView()
        self.task_input = Input(placeholder="Add task and press Enter")
        self.task_list.styles.height = "71%"
        yield self.task_list
        yield self.task_input

    def clear(self):
        self.task_list.clear()

    def add_items(self, items):
        self.task_list.mount(*items)


class Calendar(Widget):
    """A widget to display a calendar"""

    can_focus = True

    BINDINGS = [
        Binding("h", "left"),
        Binding("j", "down"),
        Binding("k", "up"),
        Binding("l", "right"),
        Binding("J", "down_month", "prev month"),
        Binding("K", "up_month", "next month"),
        Binding("t", "return_today", "today"),
        Binding("a", "add_task", "Add a task"),
        Binding("q", "quit", show=False),
    ]

    def __init__(self):
        super().__init__()
        self.cursor = date.today()
        self.todos = {}  # {date: [tasks]}

    def compose(self) -> ComposeResult:
        self.label = Label()
        self.task_list = TodoList()
        yield self.label
        yield self.task_list

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
                else:
                    current_day = date(self.cursor.year, self.cursor.month, day)
                    has_tasks = current_day in self.todos and self.todos[current_day]

                    if day == self.cursor.day:
                        style = "reverse"
                        if has_tasks:
                            style += " bold orange"  # current day with tasks
                        line.append(f"[{style}]{day:2}[/{style}]")
                    else:
                        if has_tasks:
                            line.append(f"[bold orange]{day:2}[/bold orange]")
                        else:
                            line.append(f"{day:2}")
            lines.append(" ".join(line))

        tasks = self.todos.get(self.cursor, [])
        task_items = [ListItem(Label(f"O {task}")) for task in tasks]
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
        self.task_list.task_input.focus()

    def on_input_submitted(self, event: Input.Submitted):
        task = event.value.strip()
        if task:
            self.todos.setdefault(self.cursor, []).append(task)
        self.task_list.task_input.value = ""
        self.focus()
        self.render_calendar()


class CalendarApp(App):
    """A simple and easy to use cool calendar TUI with vim motions"""

    CSS_PATH = "main.tcss"
    TITLE = date.today().strftime("%A")
    SUB_TITLE = date.today().strftime("%d %B %y")

    BINDINGS = [
        Binding("q", "quit", "Quit"),
    ]

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        yield Footer()
        yield Calendar()


if __name__ == "__main__":
    app = CalendarApp()
    app.run()
