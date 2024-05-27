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
logger.setLevel(os.getenv("LOG_LEVEL", logging.WARNING))


class _PredictTaskQueue(ImageUtilsMixin):
    def __init__(self, max_size: int = 10):
        self._queue: queue.Queue[
            api.schemas.ImageToImageTask | api.schemas.TextToImageTask | api.schemas.TextToVideoTask
        ] = queue.Queue(maxsize=max_size)

        self._states_lock = threading.Lock()
        self._states: dict[uuid.UUID, api.schemas.TaskState] = {}
        self._current_task: uuid.UUID

        threading.Thread(target=self._worker).start()

    def submit(
        self, task: api.schemas.ImageToImageTask | api.schemas.TextToImageTask |  api.schemas.TextToVideoTask
    ) -> uuid.UUID:
        logger.info(f"Submitting {task.task_id}")
        self._queue.put_nowait(task)
        try:
            task_info = api.schemas.TaskState(
                task=task, stage=api.schemas.TaskStage.PENDING
            )
            with self._states_lock:
                self._states[task.task_id] = task_info
        except queue.Full:
            raise queue.Full("At max capacity. Try again later")
        return task.task_id

    def status(
        self, task_id: uuid.UUID
    ) -> api.schemas.TaskState | os.PathLike[str]:
        try:
            with self._states_lock:
                state = self._states[task_id]
                position = list(self._states.keys()).index(task_id)
                state.position = position
        except KeyError as exc:
            if self.image_exists(task_id=task_id):
                return self.image_path(task_id=task_id)
            elif self.gif_exists(task_id=task_id):
                return self.gif_path(task_id=task_id)
            else:
                raise exc

        return api.schemas.TaskState(
            position=position,
            task=state.task,
            stage=state.stage,
            steps_completed=state.steps_completed,
        )

    def _predict(
        self, task: api.schemas.ImageToImageTask | api.schemas.TextToImageTask |  api.schemas.TextToVideoTask
    ):
        model = task.model
        model_instance: api.models.model.Model = _get_model_instance(requested_model=model)

        state = self._states[self._current_task]

        def _callback(step: int, timestep: int, latents: torch.FloatTensor):
            with self._states_lock:
                state.steps_completed = step + 1
                self._states[self._current_task] = state

        if isinstance(task, api.schemas.TextToImageTask):
            model_instance: api.models.model.TextToImageModel
            image = model_instance.predict_text_to_image(
                prompt=task.prompt,
                num_inference_steps=task.num_inference_steps,
                width=task.width,
                height=task.height,
                callback_steps=task.callback_steps,
                callback=_callback,
            )
            self.save_image(image=image, task_id=task.task_id)
        elif isinstance(task, api.schemas.TextToVideoTask):
            model_instance: api.models.model.TextToVideoModel
            images = model_instance.predict_text_to_video(
                prompt=task.prompt,
                guidance_scale=task.guidance_scale,
                num_inference_steps=task.num_inference_steps,
                callback_steps=task.callback_steps,
                callback=_callback
            )
            self.save_gif(images=images, task_id=task.task_id)
        elif isinstance(task, api.schemas.ImageToImageTask):
            model_instance: api.models.model.ImageToImageModel
            image = model_instance.predict_image_to_image(
                prompt=task.prompt,
                num_inference_steps=task.num_inference_steps,
                image_url=str(task.image_url),
                callback_steps=task.callback_steps,
                callback=_callback,
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
            with self._states_lock:
                state = self._states[task.task_id]
                state.stage = api.schemas.TaskStage.PROCESSING
                state.position = 0
            self._current_task = state.task.task_id

            try:
                self._predict(task=task)
            except Exception as exc:
                logger.exception(
                    msg=f"Error while processing PredictTask {task}",
                    exc_info=exc,
                )

            logger.info(f"Completed {task.task_id}")
            self._queue.task_done()

            with self._states_lock:
                del self._states[task.task_id]


def _get_model_instance(requested_model: api.schemas.TextToImageModelsEnum | api.schemas.ImageToImageModelsEnum | api.schemas.TextToVideoModelsEnum) -> api.models.model.Model:
    model_class = next(
        cls
        for cls in api.models.model.TextToImageModel.__subclasses__() + api.models.model.ImageToImageModel.__subclasses__() + api.models.model.TextToVideoModel.__subclasses__()
        if cls.__name__.lower() == requested_model
    )
    model: api.models.model.Model = model_class()
    return model


PredictTaskQueue = _PredictTaskQueue()
