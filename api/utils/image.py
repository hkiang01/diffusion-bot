import os
import uuid

from PIL.Image import Image

from api.constants import OUTPUT_DIR


class ImageUtilsMixin:
    @classmethod
    def saveImage(cls, image: Image) -> uuid.UUID:
        image_id = uuid.uuid4()
        path = cls.image_path(image_id=image_id)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "wb") as fp:
            image.save(fp=fp)
        return image_id

    @classmethod
    def image_path(cls, image_id: uuid.UUID) -> os.PathLike:
        image_path = os.path.join(
            OUTPUT_DIR, cls.__name__, f"{str(image_id)}.png"
        )
        return image_path
