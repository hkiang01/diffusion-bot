import enum
import logging
import typing

import diffusers
import PIL.Image
import torch

import api.models.model

logger = logging.getLogger(__name__)


class Task(enum.Enum):
    TEXT_TO_IMAGE = 1
    IMAGE_TO_IMAGE = 2


class SDXLTurbo(
    api.models.model.TextToImageModel, api.models.model.ImageToImageModel
):
    def __init__(self):
        self.pipe: diffusers.DiffusionPipeline

    def predict_text_to_image(
        self,
        prompt: str,
        width: int,
        height: int,
        callback_steps: int,
        num_inference_steps: int | None = None,
        callback: typing.Optional[
            typing.Callable[[int, int, torch.FloatTensor], None]
        ] = None,
    ) -> PIL.Image.Image:
        kwargs = {
            "prompt": prompt,
            "callback": callback,
            "width": width,
            "height": height,
            "callback_steps": callback_steps
        }
        if num_inference_steps:
            kwargs["num_inference_steps"] = num_inference_steps
        ##########################
        # actually use the model #
        ##########################
        self._load(task=Task.TEXT_TO_IMAGE)

        with torch.inference_mode():
            result: PIL.Image.Image = self.pipe(**kwargs).images[0]
        return result

    def predict_image_to_image(
        self,
        prompt: str,
        image_url: str,
        callback_steps: int,
        num_inference_steps: int | None = None,
        strength: float | None = None,
        guidance_scale: float | None = None,
        callback: typing.Optional[
            typing.Callable[[int, int, torch.FloatTensor], None]
        ] = None,
    ) -> PIL.Image.Image:
        image = diffusers.utils.load_image(image=image_url)

        ##########################
        # actually use the model #
        ##########################
        self._load(task=Task.IMAGE_TO_IMAGE)
        kwargs = {
            "prompt": prompt,
            "callback": callback,
            "image": image,
            "callback_steps": callback_steps

        }
        if strength:
            kwargs["strength"] = strength
        if guidance_scale:
            kwargs["guidance_scale"] = guidance_scale
        if num_inference_steps:
            kwargs["num_inference_steps"] = num_inference_steps

        with torch.inference_mode():
            result: PIL.Image.Image = self.pipe(**kwargs).images[0]
        return result

    def _load(self, task: Task):
        pipe: diffusers.DiffusionPipeline
        ##############
        # load model #
        ##############
        if task == Task.TEXT_TO_IMAGE:
            # see https://huggingface.co/stabilityai/sdxl-turbo/blob/8fce7b5546bfdbc5aa3562eafa1de9ee129e3b3c/README.md#diffusers  # noqa: E501
            pipe = diffusers.AutoPipelineForText2Image.from_pretrained(
                # see https://huggingface.co/stabilityai/sdxl-turbo/blob/8fce7b5546bfdbc5aa3562eafa1de9ee129e3b3c/README.md#diffusers
                "stabilityai/sdxl-turbo",
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

        elif task == Task.IMAGE_TO_IMAGE:
            # see https://huggingface.co/stabilityai/sdxl-turbo/blob/8fce7b5546bfdbc5aa3562eafa1de9ee129e3b3c/README.md#diffusers
            pipe = diffusers.AutoPipelineForImage2Image.from_pretrained(
                # see https://huggingface.co/stabilityai/sdxl-turbo/blob/8fce7b5546bfdbc5aa3562eafa1de9ee129e3b3c/README.md#diffusers
                "stabilityai/sdxl-turbo",
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

    def _speedup(self, pipe: diffusers.DiffusionPipeline):
        # see https://huggingface.co/docs/diffusers/v0.20.0/en/stable_diffusion#speed
        if torch.cuda.is_available():
            logger.debug("using gpu")

            # see https://huggingface.co/docs/diffusers/optimization/fp16#use-tf32-instead-of-fp32-on-ampere-and-later-cuda-devices
            torch.backends.cuda.matmul.allow_tf32 = True

            # # see https://huggingface.co/docs/diffusers/optimization/fp16#offloading-to-cpu-with-accelerate-for-memory-savings
            # pipe.enable_sequential_cpu_offload()

            # see https://huggingface.co/docs/diffusers/optimization/fp16#model-offloading-for-fast-inference-and-memory-savings
            pipe.enable_model_cpu_offload()

            # pipe.to("cuda")

            # # see https://huggingface.co/docs/diffusers/optimization/fp16#memory-efficient-attention
            # pipe.enable_xformers_memory_efficient_attention()
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
