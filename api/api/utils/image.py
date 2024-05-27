import os
import typing
import uuid

import diffusers
from PIL.Image import Image

from api.constants import OUTPUTS_DIR


class ImageUtilsMixin:
    @staticmethod
    def save_image(image: Image, task_id: uuid.UUID) -> uuid.UUID:
        path = ImageUtilsMixin._output_path(task_id=task_id, extension=".png")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "wb") as fp:
            image.save(fp=fp)

    @staticmethod
    def save_gif(images: typing.List[Image], task_id: uuid.UUID) -> uuid.UUID:
        path = ImageUtilsMixin._output_path(task_id=task_id, extension=".gif")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        diffusers.utils.export_to_gif(images, path)

    @staticmethod
    def image_exists(task_id: uuid.UUID) -> bool:
        path = ImageUtilsMixin._output_path(task_id=task_id, extension=".png")
        return os.path.exists(path=path)
    
    @staticmethod
    def gif_exists(task_id: uuid.UUID) -> bool:
        path = ImageUtilsMixin._output_path(task_id=task_id, extension=".gif")
        return os.path.exists(path=path)

    @staticmethod
    def image_path(task_id: uuid.UUID) -> os.PathLike[str]:
        path = ImageUtilsMixin._output_path(task_id=task_id, extension=".png")
        return path
    
    @staticmethod
    def gif_path(task_id: uuid.UUID) -> os.PathLike[str]:
        path = ImageUtilsMixin._output_path(task_id=task_id, extension=".gif")
        return path

    @staticmethod
    def _output_path(task_id: uuid.UUID, extension: str) -> os.PathLike[str]:
        output_path = os.path.join(OUTPUTS_DIR, f"{str(task_id)}{extension}")
        return output_path
