"""Photo editing operations: pure-function tests, no models needed."""

import cv2
import numpy as np
import pytest

from app.services import edit_service


@pytest.fixture()
def img():
    rng = np.random.default_rng(4)
    return rng.integers(0, 255, (120, 200, 3), dtype=np.uint8)


def test_rotate_swaps_dimensions(img):
    assert edit_service.rotate90(img, True).shape[:2] == (200, 120)
    # Four rotations return to the original.
    out = img
    for _ in range(4):
        out = edit_service.rotate90(out, True)
    assert np.array_equal(out, img)


def test_flip_is_involution(img):
    assert np.array_equal(
        edit_service.flip_horizontal(edit_service.flip_horizontal(img)), img
    )


def test_crop_bounds(img):
    assert edit_service.crop(img, 10, 20, 50, 40).shape[:2] == (40, 50)
    # Out-of-range crops are clamped to the image.
    assert edit_service.crop(img, 150, 100, 500, 500).shape[:2] == (20, 50)
    # Degenerate crops are refused.
    assert edit_service.crop(img, 0, 0, 2, 2).shape[:2] == (120, 200)


def test_adjust_brightness_and_identity(img):
    assert np.array_equal(edit_service.adjust(img), img)  # all-zero = no-op
    brighter = edit_service.adjust(img, brightness=50)
    assert brighter.mean() > img.mean()
    darker = edit_service.adjust(img, brightness=-50)
    assert darker.mean() < img.mean()


def test_adjust_saturation(img):
    gray = cv2.cvtColor(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY), cv2.COLOR_GRAY2BGR)
    saturated = edit_service.adjust(img, saturation=80)
    def sat(i):
        return cv2.cvtColor(i, cv2.COLOR_BGR2HSV)[..., 1].mean()
    assert sat(saturated) > sat(img) > sat(gray)


def test_auto_enhance_shape_preserved(img):
    assert edit_service.auto_enhance(img).shape == img.shape


def test_save_copy_never_overwrites(tmp_path, img):
    original = tmp_path / "photo.jpg"
    cv2.imwrite(str(original), img)
    first = edit_service.save_copy(original, img)
    second = edit_service.save_copy(original, img)
    assert first.name == "photo_edited.jpg"
    assert second.name == "photo_edited_2.jpg"
    assert original.read_bytes()  # original untouched
    assert first.is_file() and second.is_file()
