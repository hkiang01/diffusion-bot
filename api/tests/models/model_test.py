import pytest

# necessary to dynamically populate names of subclasses of Model
from api.models import *  # noqa: F401,F403
from api.models.model import Model


@pytest.mark.parametrize(
    "model_class", [cls for cls in Model.__subclasses__()]
)
def test_predict(model_class):
    model: Model = model_class()
    model.load()
    image = model.predict(
        prompt="handsome",
        width=1920,
        height=1080,
        num_inference_steps=20,
    )
    model.saveImage(image=image)
