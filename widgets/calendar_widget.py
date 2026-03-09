import calendar as c
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta

from textual.app import ComposeResult
from textual.message import Message
from textual.widget import Widget
from textual.widgets import Label
from textual.binding import Binding


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
        self.render_all()

    def build_month(self, year: int, month: int, highlight_cursor=False):

        cal = self.cal.monthdayscalendar(year, month)

        header = f"{c.month_name[month]} {year}\nMo Tu We Th Fr Sa Su\n"

        lines = []

        for week in cal:
            line = []

            for day in week:
                if day == 0:
                    line.append("  ")
                    continue

                if highlight_cursor and day == self.cursor.day:
                    line.append(f"[reverse orange]{day:2}[/reverse orange]")
                else:
                    line.append(f"{day:2}")

            lines.append(" ".join(line))

        return header + "\n".join(lines)

    def render_all(self):

        self.main_calendar.update(
            self.build_month(self.cursor.year, self.cursor.month, True)
        )

        prev_date = self.cursor - relativedelta(months=1)
        next_date = self.cursor + relativedelta(months=1)

        self.prev_month.update(self.build_month(prev_date.year, prev_date.month))

        self.next_month.update(self.build_month(next_date.year, next_date.month))

        self.post_message(self.CursorMoved(self.cursor))

    def move_cursor(self, delta):
        self.cursor += delta
        self.render_all()

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
        self.render_all()

    def action_next_month(self):
        self.cursor += relativedelta(months=1)
        self.render_all()

    def action_go_today(self):
        self.cursor = date.today()
        self.render_all()
