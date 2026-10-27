
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..db import db


class Goal(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str]

    tasks: Mapped[list["Task"]] = relationship(
        "Task", back_populates="goal"
    )

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title
        }

    @classmethod
    def from_dict(cls, goal_data):
        return cls(title=goal_data["title"])

    def to_dict_with_tasks(self):
        response_body = self.to_dict()

        response_body["tasks"] = [
            task.to_dict() for task in self.tasks
        ]

        return response_body
