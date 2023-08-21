import logging
import threading
import uuid
from queue import Queue

from api.models.model import Model
from api.schemas import (
    ModelsEnum,
    PredictTaskSubmission,
    PredictTask,
    PredictTaskStatus,
)
from api.utils.image import ImageUtilsMixin

logger = logging.getLogger(__name__)


class _PredictTaskQueue(ImageUtilsMixin):
    def __init__(self, num_worker_threads: int = 1):
        self.queue: Queue[PredictTask] = Queue()
        self.submission_stats: dict[uuid.UUID, PredictTaskStatus] = {}

        for _ in range(0, num_worker_threads):
            threading.Thread(target=self._worker).start()

    def submit(self, predict_request: PredictTaskSubmission) -> uuid.UUID:
        predict_task = PredictTask(
            model=predict_request.model,
            prompt=predict_request.prompt,
            width=predict_request.width,
            height=predict_request.height,
            num_inference_steps=predict_request.num_inference_steps,
        )

        logger.info(f"Submitting {predict_task.task_id}")
        self.submission_stats[predict_task.task_id] = PredictTaskStatus.PENDING
        self.queue.put_nowait(predict_task)
        return predict_task.task_id

    def status(self, submission_id: uuid.UUID) -> PredictTaskStatus:
        try:
            status = self.submission_stats[submission_id]
        except KeyError:
            return PredictTaskStatus.NOT_FOUND
        return status

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
            self.submission_stats[
                predict_task.task_id
            ] = PredictTaskStatus.COMPLETE


def _get_model_class(requested_model: ModelsEnum) -> Model:
    model_class = next(
        cls
        for cls in Model.__subclasses__()
        if cls.__name__.lower() == requested_model
    )
    model: Model = model_class()
    return model


PredictTaskQueue = _PredictTaskQueue()
