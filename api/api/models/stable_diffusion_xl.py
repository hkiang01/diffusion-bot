import logging
import typing

import torch
import diffusers
import PIL.Image

from api.models.model import Model

logger = logging.getLogger(__name__)

# see https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0/blob/ffd13a1d2ed00b2bbcf5d78c2a347313a3b556c8/README.md#sd-xl-10-base-model-card
MODEL = "stabilityai/stable-diffusion-xl-base-1.0"


class StableDiffusionXL(Model):
    def __init__(self):
        self.pipe: diffusers.DiffusionPipeline

    def load(self):
        ##############
        # load model #
        ##############
        # see https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0/blob/ffd13a1d2ed00b2bbcf5d78c2a347313a3b556c8/README.md#sd-xl-10-base-model-card  # noqa: E501
        pipe = diffusers.DiffusionPipeline.from_pretrained(
            MODEL,
            # speedup
            # see https://huggingface.co/docs/diffusers/optimization/fp16#half-precision-weights
            torch_dtype=torch.float16 if torch.cuda.is_available() else None,
            safety_checker=None,
            requires_safety_checker=False,
            use_safetensors=True,
            variant="fp16",
        )

        #####################
        # some speedup code #
        #####################
        self.speedup(pipe=pipe)
        self.pipe = pipe

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
        ##########################
        # actually use the model #
        ##########################
        image: PIL.Image.Image = self.pipe(
            prompt=prompt,
            num_inference_steps=num_inference_steps,
            width=width,
            height=height,
            callback=callback,
        ).images[0]
        return image
