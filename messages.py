from datetime import date
from textual.message import Message


class TasksUpdated(Message):
    def __init__(self, date: date, tasks: list[str]):
        self.date = date
        self.tasks = tasks
        super().__init__()
