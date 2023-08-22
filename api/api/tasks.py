import logging
import os
import queue
import threading
import uuid

import torch
import fastapi.logger

from api.models.model import Model
from api.schemas import (
    ModelsEnum,
    PredictTaskState,
    PredictTask,
    PredictTaskStage,
)
from api.utils.image import ImageUtilsMixin

logger = fastapi.logger.logger
logger.setLevel(os.getenv("LOG_LEVEL", logging.WARNING))


class _PredictTaskQueue(ImageUtilsMixin):
    def __init__(self, max_size: int = 10):
        self._queue: queue.Queue[PredictTask] = queue.Queue(maxsize=max_size)

        self._states_lock = threading.Lock()
        self._states: dict[uuid.UUID, PredictTaskState] = {}
        self._current_task: uuid.UUID

        threading.Thread(target=self._worker).start()

    def submit(self, predict_task: PredictTask) -> uuid.UUID:
        logger.info(f"Submitting {predict_task.task_id}")
        self._queue.put_nowait(predict_task)
        try:
            task_info = PredictTaskState(
                predict_task=predict_task, stage=PredictTaskStage.PENDING
            )
            with self._states_lock:
                self._states[predict_task.task_id] = task_info
        except queue.Full:
            raise queue.Full("At max capacity. Try again later")
        return predict_task.task_id

    def status(
        self, submission_id: uuid.UUID
    ) -> PredictTaskState | os.PathLike[str]:
        try:
            with self._states_lock:
                state = self._states[submission_id]
                position = list(self._states.keys()).index(submission_id)
                state.position = position
        except KeyError as exc:
            image_path = self.image_path(image_id=submission_id)
            if os.path.exists(path=image_path):
                return image_path
            else:
                raise exc

        return PredictTaskState(
            position=position,
            predict_task=state.predict_task,
            stage=state.stage,
            percent_complete=state.percent_complete,
        )

    def _predict(self, predict_task: PredictTask):
        model = predict_task.model
        model_instance: Model = _get_model_class(requested_model=model)
        model_instance.load()

        state = self._states[self._current_task]

        def _callback(step: int, timestep: int, latents: torch.FloatTensor):
            with self._states_lock:
                state.percent_complete = (
                    step / state.predict_task.num_inference_steps * 100
                )
                self._states[self._current_task] = state

                logger.warning(f"states: {self._states}")

        image = model_instance.predict(
            prompt=predict_task.prompt,
            width=predict_task.width,
            height=predict_task.height,
            num_inference_steps=predict_task.num_inference_steps,
            callback=_callback,
        )
        self.saveImage(image=image, image_id=predict_task.task_id)

    def _worker(self):
        while True:
            predict_task = self._queue.get()

            logger.info(f"Starting {predict_task}")
            with self._states_lock:
                state = self._states[predict_task.task_id]
                state.stage = PredictTaskStage.PROCESSING
                state.position = 0
            self._current_task = state.predict_task.task_id

            self._predict(predict_task=predict_task)

            logger.info(f"Completed {predict_task.task_id}")
            self._queue.task_done()

            with self._states_lock:
                del self._states[predict_task.task_id]


def _get_model_class(requested_model: ModelsEnum) -> Model:
    model_class = next(
        cls
        for cls in Model.__subclasses__()
        if cls.__name__.lower() == requested_model
    )
    model: Model = model_class()
    return model


PredictTaskQueue = _PredictTaskQueue()
