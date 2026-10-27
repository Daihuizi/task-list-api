from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..db import db

if TYPE_CHECKING:
    from .goal import Goal


class Task(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    goal_id: Mapped[int | None] = mapped_column(
        ForeignKey("goal.id")
    )

    goal: Mapped[Goal | None] = relationship(
        "Goal", back_populates="tasks"
    )

    title: Mapped[str]
    description: Mapped[str]

    completed_at: Mapped[datetime | None]

    def to_dict(self):
        task_dict = {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "is_complete": self.completed_at is not None
        }

        if self.goal_id is not None:
            task_dict["goal_id"] = self.goal_id

        return task_dict

    @classmethod
    def from_dict(cls, task_data):
        completed_at = task_data.get("completed_at")

        if completed_at is not None:
            completed_at = datetime.fromisoformat(completed_at)

        return cls(
            title=task_data["title"],
            description=task_data["description"],
            completed_at=completed_at
        )

    def mark_complete(self):
        self.completed_at = datetime.now()