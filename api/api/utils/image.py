import os
import typing
import uuid

import diffusers
from PIL.Image import Image

from api.constants import OUTPUTS_DIR


class ImageUtilsMixin:
    @staticmethod
    def save_image(image: Image, image_id: uuid.UUID) -> uuid.UUID:
        path = ImageUtilsMixin.output_path(image_id=image_id, extension=".png")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "wb") as fp:
            image.save(fp=fp)


    @staticmethod
    def save_gif(images: typing.List[Image], image_id: uuid.UUID) -> uuid.UUID:
        path = ImageUtilsMixin.output_path(image_id=image_id, extension=".gif")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        diffusers.utils.export_to_gif(images, path)

    @staticmethod
    def output_path(image_id: uuid.UUID, extension: str) -> os.PathLike[str]:
        output_path = os.path.join(OUTPUTS_DIR, f"{str(image_id)}{extension}")
        return output_path
