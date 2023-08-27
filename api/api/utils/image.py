import os
import uuid

from PIL.Image import Image

from api.constants import OUTPUTS_DIR


class ImageUtilsMixin:
    @staticmethod
    def saveImage(image: Image, image_id: uuid.UUID) -> uuid.UUID:
        path = ImageUtilsMixin.image_path(image_id=image_id)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "wb") as fp:
            image.save(fp=fp)

    @staticmethod
    def image_path(image_id: uuid.UUID) -> os.PathLike[str]:
        image_path = os.path.join(OUTPUTS_DIR, f"{str(image_id)}.png")
        return image_path
