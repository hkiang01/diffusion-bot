import os
import uuid
from http import HTTPStatus

from fastapi import FastAPI
from fastapi.responses import FileResponse, PlainTextResponse, RedirectResponse

from api.schemas import Model, ModelsEnum, PredictRequest

app = FastAPI(
    title="Text to Image Server",
)


@app.get("/ping")
async def ping():
    return "pong"


@app.post("/predict")
async def predict(predict_request: PredictRequest) -> RedirectResponse:
    model = predict_request.model
    model_instance = _get_model_class(requested_model=model)
    model_instance.load()
    image = model_instance.predict(
        prompt=predict_request.prompt,
        width=predict_request.width,
        height=predict_request.height,
        num_inference_steps=predict_request.num_inference_steps,
    )
    image_id = model_instance.saveImage(image=image)
    return RedirectResponse(
        url=f"/image/{model}/{image_id}", status_code=HTTPStatus.FOUND
    )


@app.get("/image/{model}/{image_id}")
async def image(model: ModelsEnum, image_id: uuid.UUID) -> FileResponse:
    model_instance = _get_model_class(requested_model=model)
    image_path = model_instance.image_path(image_id=image_id)
    if not os.path.exists(path=image_path):
        return PlainTextResponse(
            f"Image {image_id} for model {model} does not exist",
            status_code=404,
        )
    return FileResponse(image_path)


def _get_model_class(requested_model: ModelsEnum) -> Model:
    model_class = next(
        cls
        for cls in Model.__subclasses__()
        if cls.__name__.lower() == requested_model
    )
    model: Model = model_class()
    return model
