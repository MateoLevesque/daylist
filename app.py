from textual.app import App, ComposeResult
from textual.widgets import Header, Footer
from textual.containers import Horizontal
from textual.binding import Binding

import calendar as c
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta

from textual.message import Message
from textual.widget import Widget
from textual.widgets import Label

from textual.widgets import Input, ListView, ListItem


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


class Calendar(Widget):
    """Calendar widget"""

    class CursorMoved(Message):
        def __init__(self, cursor: date):
            self.cursor = cursor
            super().__init__()

    can_focus = True

    BINDINGS = [
        Binding("h", "prev_day"),
        Binding("j", "next_week"),
        Binding("k", "prev_week"),
        Binding("l", "next_day"),
        Binding("J", "next_month"),
        Binding("K", "prev_month"),
        Binding("t", "go_today"),
    ]

    def compose(self) -> ComposeResult:
        self.prev_month = Label(classes="hint_cal")
        self.main_calendar = Label(id="calendar_label")
        self.next_month = Label(classes="hint_cal")

        yield self.prev_month
        yield self.main_calendar
        yield self.next_month

    def on_mount(self):
        self.cursor = date.today()
        self.cal = c.Calendar()

    def build_month(self, year: int, month: int, tasks, highlight_cursor=False):

        cal = self.cal.monthdayscalendar(year, month)

        header = f"{c.month_name[month]} {year}\nMo Tu We Th Fr Sa Su\n"

        lines = []

        for week in cal:
            line = []
            for day in week:
                if day == 0:
                    line.append("  ")
                    continue

                current_day = date(year, month, day)
                has_tasks = current_day in tasks and tasks[current_day]

                is_cursor = (
                    highlight_cursor
                    and year == self.cursor.year
                    and month == self.cursor.month
                    and day == self.cursor.day
                )

                if is_cursor:
                    if has_tasks:
                        line.append(f"[reverse orange italic]{day:2}[/]")
                    else:
                        line.append(f"[reverse orange]{day:2}[/]")
                else:
                    if has_tasks:
                        line.append(f"[italic orange]{day:2}[/]")
                    else:
                        line.append(f"{day:2}")

            lines.append(" ".join(line))

        return header + "\n".join(lines)

    def render_all(self, tasks):

        self.main_calendar.update(
            self.build_month(self.cursor.year, self.cursor.month, tasks, True)
        )

        prev_date = self.cursor - relativedelta(months=1)
        next_date = self.cursor + relativedelta(months=1)

        self.prev_month.update(self.build_month(prev_date.year, prev_date.month, tasks))

        self.next_month.update(self.build_month(next_date.year, next_date.month, tasks))

    def move_cursor(self, delta):
        self.cursor += delta
        self.post_message(self.CursorMoved(self.cursor))

    def action_prev_day(self):
        self.move_cursor(timedelta(days=-1))

    def action_next_day(self):
        self.move_cursor(timedelta(days=1))

    def action_prev_week(self):
        self.move_cursor(timedelta(days=-7))

    def action_next_week(self):
        self.move_cursor(timedelta(days=7))

    def action_prev_month(self):
        self.cursor -= relativedelta(months=1)
        self.post_message(self.CursorMoved(self.cursor))

    def action_next_month(self):
        self.cursor += relativedelta(months=1)
        self.post_message(self.CursorMoved(self.cursor))

    def action_go_today(self):
        self.cursor = date.today()
        self.post_message(self.CursorMoved(self.cursor))


class CalendarApp(App):
    """Calendar App"""

    CSS_PATH = "style/styles.tcss"
    TITLE = date.today().strftime("%A")
    SUB_TITLE = date.today().strftime("%d %B %y")

    BINDINGS = [
        Binding("q", "quit"),
        Binding("v", "change_focus", "change focus"),
        Binding("a", "focus_input", "add task"),
    ]

    def __init__(self):
        super().__init__()

        self.tasks: dict[date, list[str]] = {
            date(2026, 3, 13): ["test", "chenille"],
            date(2026, 4, 15): ["test"],
        }

        self.current_day = date.today()

    def compose(self) -> ComposeResult:
        self.todolist = Todolist(id="todolist")
        self.calendar = Calendar(id="calendar")
        yield Header()
        yield Horizontal(self.calendar, self.todolist)
        yield Footer()

    def on_mount(self):
        self.calendar.focus()
        self.theme = "flexoki"

        tasks = self.tasks.get(self.current_day, [])
        self.update_tasks(self.current_day, tasks)

    def update_tasks(self, date, tasks):

        self.todolist.cursor = date
        self.todolist.render_tasks(tasks)
        self.calendar.render_all(self.tasks)

    def action_change_focus(self):
        if self.calendar.has_focus:
            self.todolist.focus()
        else:
            self.calendar.focus()

    def action_focus_input(self):
        self.todolist.focus_input()

    def on_calendar_cursor_moved(self, message: Calendar.CursorMoved):
        self.current_day = message.cursor
        tasks = self.tasks.get(self.current_day, [])
        self.update_tasks(self.current_day, tasks)

    def on_todolist_task_added(self, message: Todolist.TaskAdded):
        self.tasks.setdefault(message.date, []).append(message.task)

        tasks = self.tasks[message.date]

        self.update_tasks(message.date, tasks)
        self.calendar.focus()


if __name__ == "__main__":
    CalendarApp().run()
