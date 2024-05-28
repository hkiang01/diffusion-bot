import abc
import logging
import typing

import PIL.Image
import torch

import api.utils.image

logger = logging.getLogger(__name__)

class Model(abc.ABC):
    pass

class TextToImageModel(Model, api.utils.image.ImageUtilsMixin):
    def predict_text_to_image(
        self,
        prompt: str,
        width: int,
        height: int,
        num_inference_steps: int | None = None,
    ) -> PIL.Image.Image:
        raise NotImplementedError()

class TextToVideoModel(Model, api.utils.image.ImageUtilsMixin):
    def predict_text_to_video(
        self,
        prompt: str,
        num_inference_steps: int | None = None,
    ) -> typing.List[PIL.Image.Image]:
        raise NotImplementedError()

class ImageToImageModel(Model, api.utils.image.ImageUtilsMixin):
    def predict_image_to_image(
        self,
        prompt: str,
        image_url: str,
        num_inference_steps: int | None = None,
        strength: float | None = None,
        guidance_scale: float | None = None
    ) -> PIL.Image.Image:
        raise NotImplementedError()

