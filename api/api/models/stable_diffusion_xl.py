import logging

import torch
import diffusers

import api.models.model

logger = logging.getLogger(__name__)


class StableDiffusionXL(api.models.model.Model):
    def __init__(self):
        self.pipe: diffusers.DiffusionPipeline

    def _load(self, task: api.models.model.Task):
        pipe: diffusers.DiffusionPipeline
        ##############
        # load model #
        ##############
        if task == api.models.model.Task.TEXT_TO_IMAGE:
            # see https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0/blob/ffd13a1d2ed00b2bbcf5d78c2a347313a3b556c8/README.md#sd-xl-10-base-model-card  # noqa: E501
            pipe = diffusers.DiffusionPipeline.from_pretrained(
                # see https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0/blob/ffd13a1d2ed00b2bbcf5d78c2a347313a3b556c8/README.md#sd-xl-10-base-model-card
                "stabilityai/stable-diffusion-xl-base-1.0",
                # speedup
                # see https://huggingface.co/docs/diffusers/optimization/fp16#half-precision-weights
                torch_dtype=torch.float16
                if torch.cuda.is_available()
                else None,
                safety_checker=None,
                requires_safety_checker=False,
                use_safetensors=True,
                variant="fp16",
            )

        elif task == api.models.model.Task.IMAGE_TO_IMAGE:
            # see https://huggingface.co/docs/diffusers/v0.20.0/en/api/pipelines/stable_diffusion/stable_diffusion_xl#imagetoimage
            pipe = diffusers.StableDiffusionXLImg2ImgPipeline.from_pretrained(
                # see https://huggingface.co/stabilityai/stable-diffusion-xl-refiner-1.0/tree/93b080bbdc8efbeb862e29e15316cff53f9bef86
                "stabilityai/stable-diffusion-xl-refiner-1.0",
                # speedup
                # see https://huggingface.co/docs/diffusers/optimization/fp16#half-precision-weights
                torch_dtype=torch.float16
                if torch.cuda.is_available()
                else None,
                safety_checker=None,
                requires_safety_checker=False,
                use_safetensors=True,
                variant="fp16",
            )

        #####################
        # some speedup code #
        #####################
        self._speedup(pipe=pipe)
        self.pipe = pipe
