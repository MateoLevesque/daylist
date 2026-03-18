from textual.app import ComposeResult
from textual.widget import Widget
from textual.message import Message
from textual.binding import Binding
from textual.widgets import Label

from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
import calendar


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
        Binding("J", "next_month", "next month"),
        Binding("K", "prev_month", "prev month"),
        Binding("t", "go_today", "return to today"),
    ]

    def compose(self) -> ComposeResult:
        self.prev_month_label = Label(classes="hint_cal")
        self.main_calendar = Label(id="calendar_label")
        self.next_month_label = Label(classes="hint_cal")

        yield self.prev_month_label
        yield self.main_calendar
        yield self.next_month_label

    def on_mount(self):
        self.cursor = date.today()
        self.cal = calendar.Calendar()

    def build_month(self, year: int, month: int, tasks, highlight_cursor=False):
        temporary_calendar = self.cal.monthdayscalendar(year, month)

        header = f"{calendar.month_name[month]} {year}\nMo Tu We Th Fr Sa Su\n"

        lines = []

        for week in temporary_calendar:
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

                line.append(self.build_day(is_cursor, has_tasks, day))

            lines.append(" ".join(line))

        return header + "\n".join(lines)

    def build_day(self, is_cursor: bool, has_tasks: bool, day) -> str:
        if is_cursor:
            if has_tasks:
                return f"[reverse orange italic]{day:2}[/]"
            else:
                return f"[reverse orange]{day:2}[/]"
        else:
            if has_tasks:
                return f"[italic orange]{day:2}[/]"
            else:
                return f"{day:2}"

    def render_all(self, tasks):
        self.main_calendar.update(
            self.build_month(self.cursor.year, self.cursor.month, tasks, True)
        )

        prev_date = self.cursor - relativedelta(months=1)
        next_date = self.cursor + relativedelta(months=1)

        self.prev_month_label.update(
            self.build_month(prev_date.year, prev_date.month, tasks)
        )

        self.next_month_label.update(
            self.build_month(next_date.year, next_date.month, tasks)
        )

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
        self.move_cursor(relativedelta(months=-1))

    def action_next_month(self):
        self.move_cursor(relativedelta(months=1))

    def action_go_today(self):
        self.cursor = date.today()
        self.post_message(self.CursorMoved(self.cursor))
