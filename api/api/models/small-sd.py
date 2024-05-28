import enum
import logging
import typing

import diffusers
import PIL.Image
import torch

import api.models.model

logger = logging.getLogger(__name__)



class SmallSD(api.models.model.TextToImageModel):
    def __init__(self):
        self.pipe: diffusers.DiffusionPipeline

    def predict_text_to_image(
        self,
        prompt: str,
        width: int,
        height: int,
        num_inference_steps: int | None = None
    ) -> PIL.Image.Image:
        kwargs = {
            "prompt": prompt,
            "width": width,
            "height": height,
        }
        if num_inference_steps:
            kwargs["num_inference_steps"] = num_inference_steps
        ##########################
        # actually use the model #
        ##########################
        self._load()
        result: PIL.Image.Image = self.pipe(**kwargs).images[0]
        return result


    def _load(self):
        pipe: diffusers.DiffusionPipeline
        ##############
        # load model #
        ##############
        # see https://huggingface.co/segmind/small-sd/blob/f8b087e68071a29bbe85a4b07e6e1e8998d59aa7/README.md#pipeline-usage
        pipe = diffusers.DiffusionPipeline.from_pretrained(
            "segmind/small-sd",
            # speedup
            # see https://huggingface.co/docs/diffusers/optimization/fp16#half-precision-weights
            torch_dtype=torch.float16
            if torch.cuda.is_available()
            else None,
            safety_checker=None,
            requires_safety_checker=False,
        )

        #####################
        # some speedup code #
        #####################
        self._speedup(pipe=pipe)
        self.pipe = pipe

    def _speedup(self, pipe: diffusers.DiffusionPipeline):
        # see https://huggingface.co/docs/diffusers/v0.20.0/en/stable_diffusion#speed
        if torch.cuda.is_available():
            logger.debug("using gpu")

            # see https://huggingface.co/docs/diffusers/optimization/fp16#use-tf32-instead-of-fp32-on-ampere-and-later-cuda-devices
            torch.backends.cuda.matmul.allow_tf32 = True

            # see https://huggingface.co/docs/diffusers/optimization/fp16#offloading-to-cpu-with-accelerate-for-memory-savings
            pipe.to("cuda")
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
