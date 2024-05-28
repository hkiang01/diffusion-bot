import logging
import os
import queue
import threading
import uuid

import fastapi.logger
import torch

import api.models.model
import api.schemas
from api.utils.image import ImageUtilsMixin

logger = fastapi.logger.logger
logger.setLevel(os.getenv("LOG_LEVEL", logging.DEBUG))


class _PredictTaskQueue(ImageUtilsMixin):
    def __init__(self, max_size: int = 10):
        self._queue: queue.Queue[
            api.schemas.ImageToImageTask | api.schemas.TextToImageTask | api.schemas.TextToVideoTask
        ] = queue.Queue(maxsize=max_size)

        threading.Thread(target=self._worker).start()

    def submit(
        self, task: api.schemas.ImageToImageTask | api.schemas.TextToImageTask |  api.schemas.TextToVideoTask
    ):
        logger.info(f"Submitting {task.task_id}")
        try:
            self._queue.put_nowait(task)
        except queue.Full:
            raise queue.Full("At max capacity. Try again later")
        return task.task_id

    def status(
        self, task_id: uuid.UUID
    ) -> os.PathLike[str]| None:
        task: api.schemas.ImageToImageTask | api.schemas.TextToImageTask | api.schemas.TextToVideoTask = None
        if self.image_exists(task_id=task_id):
            return self.image_path(task_id=task_id)
        elif self.gif_exists(task_id=task_id):
            return self.gif_path(task_id=task_id)
        else:
            return None

    def _predict(
        self, task: api.schemas.ImageToImageTask | api.schemas.TextToImageTask |  api.schemas.TextToVideoTask
    ):
        model = task.model
        model_instance: api.models.model.Model = _get_model_instance(requested_model=model)

        if isinstance(task, api.schemas.TextToImageTask):
            model_instance: api.models.model.TextToImageModel
            image = model_instance.predict_text_to_image(
                prompt=task.prompt,
                num_inference_steps=task.num_inference_steps,
                width=task.width,
                height=task.height,
            )
            self.save_image(image=image, task_id=task.task_id)
        elif isinstance(task, api.schemas.TextToVideoTask):
            model_instance: api.models.model.TextToVideoModel
            images = model_instance.predict_text_to_video(
                prompt=task.prompt,
                guidance_scale=task.guidance_scale,
                num_inference_steps=task.num_inference_steps,
            )
            self.save_gif(images=images, task_id=task.task_id)
        elif isinstance(task, api.schemas.ImageToImageTask):
            model_instance: api.models.model.ImageToImageModel
            image = model_instance.predict_image_to_image(
                prompt=task.prompt,
                num_inference_steps=task.num_inference_steps,
                image_url=str(task.image_url),
                strength=task.strength,
                guidance_scale=task.guidance_scale,
            )
            self.save_image(image=image, task_id=task.task_id)
        else:
            raise RuntimeError(f"Unexpected Task type {type(task)}")

        

    def _worker(self):
        while True:
            task = self._queue.get()
            logger.info(f"Starting {task}")
            try:
                self._predict(task=task)
            except Exception as exc:
                logger.exception(
                    msg=f"Error while processing PredictTask {task}",
                    exc_info=exc,
                )

            logger.info(f"Completed {task.task_id}")
            self._queue.task_done()

def _get_model_instance(requested_model: api.schemas.TextToImageModelsEnum | api.schemas.ImageToImageModelsEnum | api.schemas.TextToVideoModelsEnum) -> api.models.model.Model:
    model_class = next(
        cls
        for cls in api.models.model.TextToImageModel.__subclasses__() + api.models.model.ImageToImageModel.__subclasses__() + api.models.model.TextToVideoModel.__subclasses__()
        if cls.__name__.lower() == requested_model
    )
    model: api.models.model.Model = model_class()
    return model


PredictTaskQueue = _PredictTaskQueue()
