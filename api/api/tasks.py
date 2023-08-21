import logging
import os
import queue
import threading
import uuid

from api.models.model import Model
from api.schemas import (
    ModelsEnum,
    PredictTaskInfo,
    PredictTask,
    PredictTaskStatus,
)
from api.utils.image import ImageUtilsMixin

logger = logging.getLogger(__name__)


class _PredictTaskQueue(ImageUtilsMixin):
    def __init__(self, num_worker_threads: int = 1, max_size: int = 10):
        self.queue: queue.Queue[PredictTask] = queue.Queue(maxsize=max_size)

        self.submission_stats: dict[uuid.UUID, PredictTaskStatus] = {}

        for _ in range(0, num_worker_threads):
            threading.Thread(target=self._worker).start()

    def submit(self, predict_task: PredictTask) -> uuid.UUID:
        logger.info(f"Submitting {predict_task.task_id}")
        self.queue.put_nowait(predict_task)
        try:
            self.submission_stats[
                predict_task.task_id
            ] = PredictTaskStatus.PENDING
        except queue.Full:
            raise queue.Full("At max capacity. Try again later")
        return predict_task.task_id

    def status(self, submission_id: uuid.UUID) -> PredictTaskInfo:
        try:
            status = self.submission_stats[submission_id]
            position = list(self.submission_stats.keys()).index(submission_id)
        except KeyError:
            image_path = self.image_path(image_id=submission_id)
            if os.path.exists(path=image_path):
                return PredictTaskInfo(
                    position=0, status=PredictTaskStatus.COMPLETE
                )
            else:
                return PredictTaskInfo()

        return PredictTaskInfo(position=position, status=status)

    def _predict(self, predict_task: PredictTask):
        model = predict_task.model
        model_instance = _get_model_class(requested_model=model)
        model_instance.load()
        image = model_instance.predict(
            prompt=predict_task.prompt,
            width=predict_task.width,
            height=predict_task.height,
            num_inference_steps=predict_task.num_inference_steps,
        )
        self.saveImage(image=image, image_id=predict_task.task_id)

    def _worker(self):
        while True:
            predict_task = self.queue.get()
            logger.info(f"Starting {predict_task}")
            self.submission_stats[
                predict_task.task_id
            ] = PredictTaskStatus.PROCESSING
            self._predict(predict_task=predict_task)
            logger.info(f"Completed {predict_task.task_id}")
            self.queue.task_done()
            del self.submission_stats[predict_task.task_id]


def _get_model_class(requested_model: ModelsEnum) -> Model:
    model_class = next(
        cls
        for cls in Model.__subclasses__()
        if cls.__name__.lower() == requested_model
    )
    model: Model = model_class()
    return model


PredictTaskQueue = _PredictTaskQueue()
