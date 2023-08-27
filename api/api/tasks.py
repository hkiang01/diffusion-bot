import logging
import os
import queue
import threading
import uuid

import fastapi.logger
import torch

from api.models.model import Model
import api.schemas
from api.utils.image import ImageUtilsMixin

logger = fastapi.logger.logger
logger.setLevel(os.getenv("LOG_LEVEL", logging.WARNING))


class _PredictTaskQueue(ImageUtilsMixin):
    def __init__(self, max_size: int = 10):
        self._queue: queue.Queue[
            api.schemas.ImageToImageTask | api.schemas.TextToImageTask
        ] = queue.Queue(maxsize=max_size)

        self._states_lock = threading.Lock()
        self._states: dict[uuid.UUID, api.schemas.TaskState] = {}
        self._current_task: uuid.UUID

        threading.Thread(target=self._worker).start()

    def submit(
        self, task: api.schemas.ImageToImageTask | api.schemas.TextToImageTask
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
            image_path = self.image_path(image_id=task_id)
            if os.path.exists(path=image_path):
                return image_path
            else:
                raise exc

        return api.schemas.TaskState(
            position=position,
            task=state.task,
            stage=state.stage,
            percent_complete=state.percent_complete,
        )

    def _predict(
        self, task: api.schemas.ImageToImageTask | api.schemas.TextToImageTask
    ):
        model = task.model
        model_instance: Model = _get_model_instance(requested_model=model)

        state = self._states[self._current_task]

        def _callback(step: int, timestep: int, latents: torch.FloatTensor):
            with self._states_lock:
                state.percent_complete = (
                    step / state.task.num_inference_steps * 100
                )
                self._states[self._current_task] = state

        if isinstance(task, api.schemas.TextToImageTask):
            image = model_instance.predict_text_to_image(
                prompt=task.prompt,
                num_inference_steps=task.num_inference_steps,
                width=task.width,
                height=task.height,
                callback=_callback,
            )
        elif isinstance(task, api.schemas.ImageToImageTask):
            image = model_instance.predict_image_to_image(
                prompt=task.prompt,
                num_inference_steps=task.num_inference_steps,
                image_url=task.image_url,
                callback=_callback,
            )
        else:
            raise RuntimeError(f"Unexpected Task type {type(task)}")

        self.saveImage(image=image, image_id=task.task_id)

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


def _get_model_instance(requested_model: api.schemas.ModelsEnum) -> Model:
    model_class = next(
        cls
        for cls in Model.__subclasses__()
        if cls.__name__.lower() == requested_model
    )
    model: Model = model_class()
    return model


PredictTaskQueue = _PredictTaskQueue()
