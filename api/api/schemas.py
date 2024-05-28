import enum
import uuid

import pydantic

# `import *` necessary to dynamically populate names of subclasses of Model
from api.models import *  # noqa: F401,F403
import api.models.model

text_to_image_subclasses = [
    cls.__name__ for cls in api.models.model.TextToImageModel.__subclasses__()
]
text_to_image_subclasses.sort()
TextToImageModelsEnum = enum.StrEnum(
    api.models.model.TextToImageModel.__name__, text_to_image_subclasses
)
default_text_to_image_model = list(vars(TextToImageModelsEnum).items())[0]

text_to_video_subclasses = [
    cls.__name__ for cls in api.models.model.TextToVideoModel.__subclasses__()
]
text_to_video_subclasses.sort()
TextToVideoModelsEnum = enum.StrEnum(
    api.models.model.TextToVideoModel.__name__, text_to_video_subclasses
)
default_text_to_video_model = list(vars(TextToVideoModelsEnum).items())[0]

image_to_image_subclasses = [
    cls.__name__ for cls in api.models.model.ImageToImageModel.__subclasses__()
]
image_to_image_subclasses.sort()
ImageToImageModelsEnum = enum.StrEnum(
    api.models.model.ImageToImageModel.__name__, image_to_image_subclasses
)
default_image_to_image_model = list(vars(ImageToImageModelsEnum).items())[0]


class BaseRequest(pydantic.BaseModel):
    prompt: str
    num_inference_steps: pydantic.PositiveInt | None = None


class TextToImageRequest(BaseRequest):
    model: TextToImageModelsEnum = default_text_to_image_model
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

class TextToVideoNumInferenceSteps(enum.IntEnum):
    # see https://huggingface.co/ByteDance/AnimateDiff-Lightning/blob/a9938907943a08e0f3dec0802c7515b13514552b/README.md#animatediff-lightning  # noqa: E501
    One = 1
    Two = 2
    Four = 4
    Eight = 8
class TextToVideoRequest(BaseRequest):
    model: TextToVideoModelsEnum = default_text_to_video_model
    guidance_scale: float | None = 1.0
    num_inference_steps: TextToVideoNumInferenceSteps


class ImageToImageRequest(BaseRequest):
    model: ImageToImageModelsEnum = default_image_to_image_model
    image_url: pydantic.HttpUrl
    strength: pydantic.confloat(ge=0, le=1) | None = None
    guidance_scale: float | None = None


class TextToImageTask(TextToImageRequest):
    task_id: pydantic.UUID4 = pydantic.Field(default_factory=uuid.uuid4)
    steps_completed: int = 0

class TextToVideoTask(TextToVideoRequest):
    task_id: pydantic.UUID4 = pydantic.Field(default_factory=uuid.uuid4)
    steps_completed: int = 0

class ImageToImageTask(ImageToImageRequest):
    task_id: pydantic.UUID4 = pydantic.Field(default_factory=uuid.uuid4)
    steps_completed: int = 0
