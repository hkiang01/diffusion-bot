import enum
import uuid

import pydantic

# `import *` necessary to dynamically populate names of subclasses of Model
from api.models import *  # noqa: F401,F403
from api.models.model import Model

model_subclasses = [cls.__name__ for cls in Model.__subclasses__()]
ModelsEnum = enum.StrEnum(Model.__name__, model_subclasses)
default_model = list(vars(ModelsEnum).items())[0]


class ImageToImageRequest(pydantic.BaseModel):
    model: ModelsEnum = default_model
    prompt: str

    num_inference_steps: pydantic.PositiveInt = 20


class TextToImageRequest(ImageToImageRequest):
    # can change defaults if your GPU has the allowed memory
    width: pydantic.conint(ge=8, le=2560) = 1024
    height: pydantic.conint(ge=8, le=1440) = 1024

    @pydantic.field_validator("width", "height")
    @classmethod
    def dimensions_divisible_by_8(
        cls, v: int, info: pydantic.FieldValidationInfo
    ) -> str:
        field_name = info.field_name
        if v % 8 != 0:
            raise ValueError(f"{field_name} must be divisible by 8")
        return v


class TextToImageTask(TextToImageRequest):
    task_id: pydantic.UUID4 = pydantic.Field(default_factory=uuid.uuid4)


class ImageToImageTask(ImageToImageRequest):
    task_id: pydantic.UUID4 = pydantic.Field(default_factory=uuid.uuid4)
    image_path: pydantic.FilePath = None


class TaskStage(enum.StrEnum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETE = "COMPLETE"
    NOT_FOUND = "NOT FOUND"


class TaskState(pydantic.BaseModel):
    task: TextToImageTask | ImageToImageTask
    stage: TaskStage = TaskStage.NOT_FOUND
    percent_complete: pydantic.confloat(ge=0, le=100) = 0
    position: int = -1
