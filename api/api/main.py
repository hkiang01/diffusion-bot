import http
import os
import queue
import typing
import uuid

import fastapi
import uvicorn

import api.constants
import api.schemas
import api.tasks

app = fastapi.FastAPI(
    title="diffusion-bot",
)


@app.get("/ping")
async def ping():
    return "pong"


@app.post("/predict", status_code=http.HTTPStatus.ACCEPTED)
async def predict(
    predict_task_request: api.schemas.PredictTaskRequest,
    image: typing.Annotated[
        fastapi.UploadFile,
        fastapi.File(
            description="Image to blend into a diffusion model",
            media_type="image",
        ),
    ]
    | None = None,
) -> uuid.UUID:
    predict_task = api.schemas.PredictTask(
        model=predict_task_request.model,
        prompt=predict_task_request.prompt,
        width=predict_task_request.width,
        height=predict_task_request.height,
        num_inference_steps=predict_task_request.num_inference_steps,
    )
    if image:
        image_path = f"{api.constants.INPUTS_DIR}/{predict_task.task_id}"
        with open(image_path, "xb") as f:
            image_bytes = await image.read()
            f.write(image_bytes)
        predict_task.image = image_path

    try:
        task_id = api.tasks.PredictTaskQueue.submit(predict_task=predict_task)
    except queue.Full as exc:
        raise fastapi.exceptions.HTTPException(
            detail=str(exc),
            status_code=http.HTTPStatus.TOO_MANY_REQUESTS,
            headers={"Retry-After": "60"},
        )
    return fastapi.responses.PlainTextResponse(
        content=str(task_id),
        status_code=http.HTTPStatus.ACCEPTED,
    )


# status
@app.get("/status")
async def status(
    task_id: uuid.UUID,
) -> api.schemas.PredictTaskState:
    try:
        task_info = api.tasks.PredictTaskQueue.status(task_id=task_id)
    except KeyError:
        raise fastapi.exceptions.HTTPException(
            status_code=http.HTTPStatus.NOT_FOUND,
            detail=api.schemas.PredictTaskStage.NOT_FOUND,
        )

    if isinstance(task_info, str):
        return fastapi.responses.RedirectResponse(
            url=f"/result?task_id={task_id}",
            status_code=http.HTTPStatus.SEE_OTHER,
        )

    return task_info


@app.get("/result")
async def result(task_id: uuid.UUID) -> fastapi.responses.FileResponse:
    image_path = api.tasks.PredictTaskQueue.image_path(image_id=task_id)
    if not os.path.exists(path=image_path):
        return fastapi.responses.PlainTextResponse(
            f"Image {task_id} does not exist",
            status_code=404,
        )
    return fastapi.responses.FileResponse(image_path)


@app.delete("/result")
async def delete_result(task_id: uuid.UUID) -> str:
    image_path = api.tasks.PredictTaskQueue.image_path(image_id=task_id)
    if os.path.exists(image_path):
        os.unlink(image_path)
    return "deleted"


if __name__ == "__main__":
    uvicorn.run(app, port=8000)
