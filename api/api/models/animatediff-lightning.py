import logging
import typing

import diffusers
import PIL.Image
import torch

import api.models.model

logger = logging.getLogger(__name__)




class AnimateDiffLightning(
    api.models.model.TextToVideoModel, 
):
    def __init__(self):
        self.pipe: diffusers.AnimateDiffPipeline

    def predict_text_to_video(
        self,
        prompt: str,
        width: int,
        height: int,
        callback_steps: int,
        num_inference_steps: int | None = None,
        callback: typing.Optional[
            typing.Callable[[int, int, torch.FloatTensor], None]
        ] = None,
    ) -> typing.List[PIL.Image.Image]:
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
        self._load()

        with torch.inference_mode():
            result: typing.List[PIL.Image.Image] = self.pipe(**kwargs).frames[0]
        return result


    def _load(self):
        pipe: diffusers.AnimateDiffPipeline
        ##############
        # load model #
        ##############


        pipe = diffusers.AnimateDiffPipeline.from_pretrained(
            # see https://huggingface.co/ByteDance/AnimateDiff-Lightning/blob/a9938907943a08e0f3dec0802c7515b13514552b/README.md#diffusers-usage
            "emilianJR/epiCRealism",
            # speedup
            # see https://huggingface.co/docs/diffusers/optimization/fp16#half-precision-weights
            torch_dtype=torch.float16
            if torch.cuda.is_available()
            else None,
            safety_checker=None,
            requires_safety_checker=False,
            use_safetensors=True,
            variant="fp16",
            adapter = diffusers.MotionAdapter()
        )


        #####################
        # some speedup code #
        #####################
        self._speedup(pipe=pipe)
        self.pipe = pipe

    def _speedup(self, pipe: diffusers.AnimateDiffPipeline):
        # see https://huggingface.co/ByteDance/AnimateDiff-Lightning/blob/a9938907943a08e0f3dec0802c7515b13514552b/README.md#diffusers-usage  # noqa: E501
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
