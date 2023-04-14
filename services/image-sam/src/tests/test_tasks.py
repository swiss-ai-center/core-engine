from typing import Dict
import cv2
import numpy as np
import pytest

from common_code.tasks.models import TaskData
from common_code.service.enums import FieldDescriptionType
import segment_anything

from main import MyService


def get_generated_masks(w: int, h: int):
    return [
        {
            "segmentation": np.zeros(shape=(h, w), dtype=bool),
            "area": 100,
            "bbox": [0, 0, 10, 10],
            "predicted_iou": 1.0,
            "point_coords": [[]],
            "stability_score": 1.0,
            "crop_box": [0, 0, w, h],
        }
    ]


@pytest.fixture(name="data", autouse=True)
def process_input_data(monkeypatch: pytest.MonkeyPatch):
    data = {"image": None}
    img = cv2.imread("tests/test.jpg")

    monkeypatch.setitem(
        segment_anything.sam_model_registry,
        "vit_b",
        lambda checkpoint: None,  # noqa: F841
    )
    monkeypatch.setattr(
        "segment_anything.SamAutomaticMaskGenerator.__init__",
        lambda self, sam: None,  # noqa: F841
    )
    monkeypatch.setattr(
        "segment_anything.SamAutomaticMaskGenerator.generate",
        lambda self, image: get_generated_masks(  # noqa: F841
            w=img.shape[1], h=img.shape[0]
        ),
    )

    data["image"] = TaskData(
        data=cv2.imencode(".jpg", img)[1].tobytes(),
        type=FieldDescriptionType.IMAGE_JPEG,
    )
    return data


def test_process(data: Dict[str, TaskData]):
    service = MyService()

    out = service.process(data)

    assert "result" in out.keys()
    assert isinstance(out["result"], TaskData)
