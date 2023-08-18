import logging
from abc import ABC

import torch
from diffusers import DiffusionPipeline
from PIL.Image import Image

from api.utils.image import ImageUtilsMixin

logger = logging.getLogger(__name__)


class Model(ABC, ImageUtilsMixin):
    def __init__(self):
        pass

    def load(self):
        raise NotImplementedError()

    def predict(
        self, prompt: str, width: int, height: int, num_inference_steps: int
    ) -> Image:
        raise NotImplementedError()

    def _speedup(self, pipe: DiffusionPipeline):
        # see https://huggingface.co/docs/diffusers/v0.20.0/en/stable_diffusion#speed
        if torch.cuda.is_available():
            # see https://huggingface.co/docs/diffusers/optimization/fp16#use-tf32-instead-of-fp32-on-ampere-and-later-cuda-devices
            torch.backends.cuda.matmul.allow_tf32 = True
            logger.debug("using gpu")
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
