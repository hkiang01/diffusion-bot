import logging
import abc
import torch
import diffusers
import PIL.Image
import typing
import api.utils.image

logger = logging.getLogger(__name__)


class Model(abc.ABC, api.utils.image.ImageUtilsMixin):
    def __init__(self):
        self.pipe: diffusers.DiffusionPipeline

    def load(self):
        raise NotImplementedError()

    def predict(
        self,
        prompt: str,
        width: int,
        height: int,
        num_inference_steps: int,
        callback: typing.Optional[
            typing.Callable[[int, int, torch.FloatTensor], None]
        ] = None,
    ) -> PIL.Image.Image:
        raise NotImplementedError()

    def speedup(self, pipe: diffusers.DiffusionPipeline):
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
