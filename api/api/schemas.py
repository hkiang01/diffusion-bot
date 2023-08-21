import enum
import uuid

import pydantic

# necessary to dynamically populate names of subclasses of Model
from api.models import *  # noqa: F401,F403
from api.models.model import Model

model_subclasses = [cls.__name__ for cls in Model.__subclasses__()]
ModelsEnum = enum.StrEnum(Model.__name__, model_subclasses)


class PredictTaskSubmission(pydantic.BaseModel):
    model: ModelsEnum
    prompt: str
    width: pydantic.PositiveInt = 1024
    height: pydantic.PositiveInt = 1024
    num_inference_steps: pydantic.PositiveInt = 20


class PredictTask(PredictTaskSubmission):
    task_id: pydantic.UUID4 = pydantic.Field(default_factory=uuid.uuid4)


class PredictTaskStatus(enum.StrEnum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETE = "COMPLETE"
    NOT_FOUND = "NOT FOUND"
