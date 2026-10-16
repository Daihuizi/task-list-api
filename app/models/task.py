from datetime import datetime

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..db import db


class Task(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    goal_id: Mapped[int | None] = mapped_column(
        ForeignKey("goal.id"), nullable=True
    )

    goal: Mapped["Goal | None"] = relationship(
        "Goal", back_populates="tasks"
    )

    title: Mapped[str] = mapped_column()
    description: Mapped[str] = mapped_column()

    completed_at: Mapped[datetime | None] = mapped_column(
        nullable=True, default=None
    )

    def to_dict(self):
        return {
            "id": self.id,
            "goal_id": self.goal_id,
            "title": self.title,
            "description": self.description,
            "is_complete": self.completed_at is not None
        }

    @classmethod
    def from_dict(cls, task_data):
        return cls(
            title=task_data["title"],
            description=task_data["description"]
        )