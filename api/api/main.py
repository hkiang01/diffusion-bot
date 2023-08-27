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


@app.post("/text-to-image", status_code=http.HTTPStatus.ACCEPTED)
async def text_to_image(
    text_to_image_request: api.schemas.TextToImageRequest,
) -> uuid.UUID:
    task = api.schemas.TextToImageTask(
        model=text_to_image_request.model,
        prompt=text_to_image_request.prompt,
        width=text_to_image_request.width,
        height=text_to_image_request.height,
        num_inference_steps=text_to_image_request.num_inference_steps,
    )

    try:
        task_id = api.tasks.PredictTaskQueue.submit(task=task)
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


@app.post("/image-to-image", status_code=http.HTTPStatus.ACCEPTED)
async def image_to_image(
    image_to_image_request: api.schemas.ImageToImageRequest,
) -> uuid.UUID:
    task = api.schemas.ImageToImageTask(
        model=image_to_image_request.model,
        prompt=image_to_image_request.prompt,
        num_inference_steps=image_to_image_request.num_inference_steps,
        image_url=image_to_image_request.image_url,
        strength=image_to_image_request.strength,
        guidance_scale=image_to_image_request.guidance_scale,
    )

    try:
        task_id = api.tasks.PredictTaskQueue.submit(task=task)
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
) -> api.schemas.TaskState:
    try:
        task_info = api.tasks.PredictTaskQueue.status(task_id=task_id)
    except KeyError:
        raise fastapi.exceptions.HTTPException(
            status_code=http.HTTPStatus.NOT_FOUND,
            detail=api.schemas.TaskStage.NOT_FOUND,
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
