import enum

import pydantic

# necessary to dynamically populate names of subclasses of Model
from api.models import *  # noqa: F401,F403
from api.models.model import Model

model_subclasses = [cls.__name__ for cls in Model.__subclasses__()]
ModelsEnum = enum.StrEnum(Model.__name__, model_subclasses)


class PredictRequest(pydantic.BaseModel):
    model: ModelsEnum
    prompt: str
    width: pydantic.PositiveInt = 1024
    height: pydantic.PositiveInt = 1024
    num_inference_steps: pydantic.PositiveInt = 20
