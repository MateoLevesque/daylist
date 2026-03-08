import calendar as c
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta

from textual.app import ComposeResult
from textual.widget import Widget
from textual.widgets import Label
from textual.binding import Binding


class Calendar(Widget):
    """Calendar widget"""

    can_focus = True

    BINDINGS = [
        Binding("h", "prev_day"),
        Binding("j", "next_week"),
        Binding("k", "prev_week"),
        Binding("l", "next_day"),
        Binding("hjkl", "", "move through days"),
        Binding("J", "next_month", "next month"),
        Binding("K", "prev_month", "prev month"),
        Binding("t", "go_today", "today"),
    ]

    def compose(self) -> ComposeResult:
        self.prev_month_cal = Label(classes="hint_cal")
        self.calendar_label = Label(id="calendar_label")
        self.next_month_cal = Label(classes="hint_cal")

        yield self.prev_month_cal
        yield self.calendar_label
        yield self.next_month_cal

    def on_mount(self):
        self.cursor = date.today()
        self.cal = c.Calendar()
        self.render_calendars()

    def build_month(self, year: int, month: int, show_cursor=False) -> str:
        cal = self.cal.monthdayscalendar(year, month)

        # build header
        if show_cursor:
            header = f"[bold orange]{c.month_name[month]} {year}[/bold orange]\nMo Tu We Th Fr Sa Su\n"
        else:
            header = f"{c.month_name[month]} {year}\nMo Tu We Th Fr Sa Su\n"
        lines = []
        tasks = self.app.tasks

        # build month
        for week in cal:
            line = []
            for day in week:
                if day == 0:
                    line.append("  ")
                else:
                    current_day = date(year, month, day)
                    has_tasks = bool(tasks.get(current_day))

                    if show_cursor and day == self.cursor.day:
                        style = "reverse orange"
                        if has_tasks:
                            style += " italic bold orange"
                        line.append(f"[{style}]{day:2}[/{style}]")
                    else:
                        if has_tasks:
                            line.append(
                                f"[italic bold orange]{day:2}[/italic bold orange]"
                            )
                        else:
                            line.append(f"{day:2}")
            lines.append(" ".join(line))

        return header + "\n".join(lines)

    def render_calendars(self):
        # Add tasks logic !!! TO VERIFY
        self.calendar_label.update(
            self.build_month(self.cursor.year, self.cursor.month, True)
        )
        self.render_hint_cals()

    def render_hint_cals(self):
        prev_date = self.cursor - relativedelta(months=1)
        next_date = self.cursor + relativedelta(months=1)

        self.prev_month_cal.update(self.build_month(prev_date.year, prev_date.month))

        self.next_month_cal.update(self.build_month(next_date.year, next_date.month))

    def action_prev_day(self):
        self.cursor -= timedelta(days=1)
        self.render_calendars()

    def action_next_day(self):
        self.cursor += timedelta(days=1)
        self.render_calendars()

    def action_prev_week(self):
        self.cursor -= timedelta(days=7)
        self.render_calendars()

    def action_next_week(self):
        self.cursor += timedelta(days=7)
        self.render_calendars()

    def action_prev_month(self):
        self.cursor -= relativedelta(months=1)
        self.render_calendars()

    def action_next_month(self):
        self.cursor += relativedelta(months=1)
        self.render_calendars()

    def action_go_today(self):
        self.cursor = date.today()
        self.render_calendars()
