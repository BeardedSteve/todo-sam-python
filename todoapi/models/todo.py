import datetime
from uuid import uuid4

from bloop import (
    BaseModel, Boolean, Column, DateTime, String, UUID
)


class TodoItem(BaseModel):
    uuid = Column(UUID, hash_key=True, default=lambda: uuid4())
    created_on = Column(DateTime,
                        default=lambda: datetime.datetime.now(tz=datetime.timezone.utc))
    task = Column(String, range_key=True)
    completed = Column(Boolean, default=False)

    @property
    def as_dict(self):
        """returns TodoItem as a json-serializable dict

        :return: dict
        """
        return {
            "uuid": str(self.uuid),
            "created_on": str(self.created_on),
            "task": self.task,
            "completed": self.completed
        }
