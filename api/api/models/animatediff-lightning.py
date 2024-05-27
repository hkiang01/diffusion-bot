import logging
import typing

import diffusers
import PIL.Image
import huggingface_hub
import safetensors.torch
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
        guidance_scale: float,
        callback_steps: int,
        num_inference_steps: int,
        callback: typing.Optional[
            typing.Callable[[int, int, torch.FloatTensor], None]
        ] = None,
    ) -> typing.List[PIL.Image.Image]:
        kwargs = {
            "prompt": prompt,
            "guidance_scale": guidance_scale,
            "callback": callback,
            "callback_steps": callback_steps,
            "num_inference_steps": num_inference_steps
        }
        ##########################
        # actually use the model #
        ##########################
        self._load(num_inference_steps=num_inference_steps)

        with torch.inference_mode():
            result: typing.List[PIL.Image.Image] = self.pipe(**kwargs).frames[0]
        return result


    def _load(self, num_inference_steps: int):
        pipe: diffusers.AnimateDiffPipeline
        ##############
        # load model #
        ##############
        device: torch.device=None
        torch_dtype: torch.dtype=None
        if torch.cuda.is_available():
            logger.debug("using gpu")
            device="cuda"
            torch_dtype=torch.float16
        elif (
            torch.backends.mps.is_available() and torch.backends.mps.is_built()
        ):
            logger.debug("using mps")
            device="mps"
        else:
            logger.debug("using cpu")
            device="cpu"

        # configure adapter
        adapter = diffusers.MotionAdapter().to(device=device, dtype=torch_dtype)
        repo = "ByteDance/AnimateDiff-Lightning"
        ckpt = f"animatediff_lightning_{num_inference_steps}step_diffusers.safetensors"
        adapter.load_state_dict(safetensors.torch.load_file(huggingface_hub.hf_hub_download(repo ,ckpt), device=device))

        pipe = diffusers.AnimateDiffPipeline.from_pretrained(
            # see https://huggingface.co/ByteDance/AnimateDiff-Lightning/blob/a9938907943a08e0f3dec0802c7515b13514552b/README.md#diffusers-usage
            "emilianJR/epiCRealism",
            # speedup
            # see https://huggingface.co/docs/diffusers/optimization/fp16#half-precision-weights
            torch_dtype=torch_dtype,
            safety_checker=None,
            requires_safety_checker=False,
            use_safetensors=True,
            motion_adapter=adapter
        )
        pipe.scheduler = diffusers.EulerDiscreteScheduler.from_config(pipe.scheduler.config, timestep_spacing="trailing", beta_schedule="linear")

        #####################
        # some speedup code #
        #####################
        self._speedup(pipe=pipe, device=device, torch_dtype=torch_dtype)
        self.pipe = pipe

    def _speedup(self, pipe: diffusers.AnimateDiffPipeline, device: torch.device, torch_dtype: torch.dtype):
        pipe.to(device)
