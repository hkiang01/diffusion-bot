import os
import uuid
from http import HTTPStatus

from fastapi import FastAPI
from fastapi.responses import FileResponse, PlainTextResponse

from api.tasks import PredictTaskQueue
from api.schemas import (
    PredictTaskInfo,
    PredictTaskSubmission,
)
import uvicorn

app = FastAPI(
    title="Text to Image Server",
)


@app.get("/ping")
async def ping():
    return "pong"


@app.post("/predict", status_code=HTTPStatus.ACCEPTED)
async def predict(
    predict_request: PredictTaskSubmission,
) -> uuid.UUID:
    submission_id = PredictTaskQueue.submit(predict_request=predict_request)
    return PlainTextResponse(
        content=str(submission_id),
        status_code=HTTPStatus.ACCEPTED,
    )


# status
@app.get("/status")
async def status(submission_id: uuid.UUID) -> PredictTaskInfo:
    return PredictTaskQueue.status(submission_id=submission_id)


@app.get("/result/{model}/{image_id}")
async def result(submission_id: uuid.UUID) -> FileResponse:
    image_path = PredictTaskQueue.image_path(image_id=submission_id)
    if not os.path.exists(path=image_path):
        return PlainTextResponse(
            f"Image {submission_id} for does not exist",
            status_code=404,
        )
    return FileResponse(image_path)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
