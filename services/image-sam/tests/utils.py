import segment_anything
import pytest


def default_setup(monkeypatch: pytest.MonkeyPatch):
    """Default setup for tests."""
    monkeypatch.setitem(
        segment_anything.sam_model_registry,
        "vit_b",
        lambda checkpoint: None,  # noqa: F841
    )
    monkeypatch.setattr(
        "segment_anything.SamAutomaticMaskGenerator.__init__",
        lambda self, sam: None,  # noqa: F841
    )
