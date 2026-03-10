from textual.app import ComposeResult
from textual.widget import Widget
from textual.message import Message
from textual.binding import Binding
from textual.widgets import Label

from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
import calendar as c


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

    def action_prev_monta(self):
        self.cursor -= relativedelta(months=1)
        self.post_message(self.CursorMoved(self.cursor))

    def action_next_month(self):
        self.cursor += relativedelta(months=1)
        self.post_message(self.CursorMoved(self.cursor))

    def action_go_today(self):
        self.cursor = date.today()
        self.post_message(self.CursorMoved(self.cursor))
