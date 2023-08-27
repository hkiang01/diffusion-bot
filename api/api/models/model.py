import abc
import enum
import logging
import pathlib
import typing

import diffusers
import PIL.Image
import torch

import api.utils.image

logger = logging.getLogger(__name__)


class Task(enum.Enum):
    TEXT_TO_IMAGE = 1
    IMAGE_TO_IMAGE = 2


class Model(abc.ABC, api.utils.image.ImageUtilsMixin):
    def __init__(self):
        self.pipe: diffusers.DiffusionPipeline

    def predict_text_to_image(
        self,
        prompt: str,
        num_inference_steps: int,
        width: int,
        height: int,
        callback: typing.Optional[
            typing.Callable[[int, int, torch.FloatTensor], None]
        ] = None,
    ) -> PIL.Image.Image:
        ##########################
        # actually use the model #
        ##########################
        self._load(task=Task.TEXT_TO_IMAGE)
        result: PIL.Image.Image = self.pipe(
            prompt=prompt,
            num_inference_steps=num_inference_steps,
            callback=callback,
            width=width,
            height=height,
        ).images[0]
        return result

    def predict_image_to_image(
        self,
        prompt: str,
        num_inference_steps: int,
        image_path: pathlib.Path,
        callback: typing.Optional[
            typing.Callable[[int, int, torch.FloatTensor], None]
        ] = None,
    ) -> PIL.Image.Image:
        image = diffusers.utils.load_image(image=image_path)

        ##########################
        # actually use the model #
        ##########################
        self._load(task=Task.IMAGE_TO_IMAGE)
        result: PIL.Image.Image = self.pipe(
            prompt=prompt,
            num_inference_steps=num_inference_steps,
            callback=callback,
            image=image,
        ).images[0]
        return result

    def _load(self, task: Task):
        raise NotImplementedError

    def _speedup(self, pipe: diffusers.DiffusionPipeline):
        # see https://huggingface.co/docs/diffusers/v0.20.0/en/stable_diffusion#speed
        if torch.cuda.is_available():
            logger.debug("using gpu")

            # see https://huggingface.co/docs/diffusers/optimization/fp16#use-tf32-instead-of-fp32-on-ampere-and-later-cuda-devices
            torch.backends.cuda.matmul.allow_tf32 = True
            pipe.to("cuda")

            # see https://huggingface.co/docs/diffusers/optimization/fp16#offloading-to-cpu-with-accelerate-for-memory-savings
            pipe.enable_sequential_cpu_offload()

        elif (
            torch.backends.mps.is_available() and torch.backends.mps.is_built()
        ):
            logger.debug("using mps")

            # see https://huggingface.co/docs/diffusers/optimization/mps#inference-pipeline
            pipe.to("mps")
            # Recommended if your computer has < 64 GB of RAM
            pipe.enable_attention_slicing()
        else:
            logger.debug("using cpu")
