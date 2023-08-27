import logging

import torch
import diffusers

import api.models.model

logger = logging.getLogger(__name__)

# see https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0/blob/ffd13a1d2ed00b2bbcf5d78c2a347313a3b556c8/README.md#sd-xl-10-base-model-card
MODEL = "segmind/small-sd"


class SegmindSmallSD(api.models.model.Model):
    def __init__(self):
        self.pipe: diffusers.StableDiffusionXLImg2ImgPipeline

    def _load(self, task: api.models.model.Task):
        ##############
        # load model #
        ##############
        # see https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0/blob/ffd13a1d2ed00b2bbcf5d78c2a347313a3b556c8/README.md#sd-xl-10-base-model-card  # noqa: E501
        pipe: diffusers.DiffusionPipeline = diffusers.DiffusionPipeline.from_pretrained(
            MODEL,
            # speedup
            # see https://huggingface.co/docs/diffusers/optimization/fp16#half-precision-weights
            torch_dtype=torch.float16 if torch.cuda.is_available() else None,
            safety_checker=None,
            requires_safety_checker=False,
            variant="fp16",
        )

        #####################
        # some speedup code #
        #####################
        self._speedup(pipe=pipe)
        self.pipe = pipe
