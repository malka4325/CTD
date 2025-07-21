import numpy as np
import pytest
from ..img import Img


def create_dummy_img_array(shape=(100, 100, 3), color=(0, 255, 0)):
    """Helper to create a dummy image array with given shape and color."""
    img = np.full(shape, color, dtype=np.uint8)
    return img


def test_copy_returns_deep_copy():
    # Arrange
    img1 = Img()
    img1.img = create_dummy_img_array()
    
    # Act
    img2 = img1.copy()

    # Assert
    assert img2 is not img1
    assert np.array_equal(img2.img, img1.img)
    img1.img[0, 0] = [255, 0, 0]
    assert not np.array_equal(img2.img, img1.img)


def test_draw_on_without_alpha():
    # Arrange
    background = Img()
    background.img = create_dummy_img_array((100, 100, 3), color=(0, 0, 0))
    
    logo = Img()
    logo.img = create_dummy_img_array((50, 50, 3), color=(255, 0, 0))

    # Act
    logo.draw_on(background, 10, 10)

    # Assert
    assert np.all(background.img[10:60, 10:60] == [255, 0, 0])


def test_draw_on_with_alpha():
    # Arrange
    background = Img()
    background.img = create_dummy_img_array((100, 100, 4), color=(0, 0, 0, 255))

    logo = Img()
    logo_img = np.zeros((50, 50, 4), dtype=np.uint8)
    logo_img[..., 0] = 255  # Blue
    logo_img[..., 3] = 128  # Alpha 50%
    logo.img = logo_img

    # Act
    logo.draw_on(background, 0, 0)

    # Assert
    blended_pixel = background.img[25, 25]
    assert blended_pixel[0] > 0  # some blue
    assert blended_pixel[3] == 255


def test_draw_on_invalid_position_raises():
    # Arrange
    bg = Img()
    bg.img = create_dummy_img_array((10, 10, 3))
    fg = Img()
    fg.img = create_dummy_img_array((20, 20, 3))

    # Act + Assert
    with pytest.raises(ValueError, match="fit at the specified position"):
        fg.draw_on(bg, 0, 0)


def test_draw_on_uninitialized_raises():
    # Arrange
    img1 = Img()
    img2 = Img()

    # Act + Assert
    with pytest.raises(ValueError):
        img1.draw_on(img2, 0, 0)


def test_put_text_adds_text_without_error():
    # Arrange
    img = Img()
    img.img = create_dummy_img_array((100, 300, 3))

    # Act
    img.put_text("TEST", 10, 50, font_size=1.0, color=(0, 255, 0), thickness=2)

    # Assert – hard to test exact pixels, so just confirm shape didn't change
    assert img.img.shape == (100, 300, 3)


def test_put_text_on_uninitialized_image_raises():
    # Arrange
    img = Img()

    # Act + Assert
    with pytest.raises(ValueError):
        img.put_text("test", 0, 0, 1.0)


def test_show_on_uninitialized_image_raises():
    # Arrange
    img = Img()

    # Act + Assert
    with pytest.raises(ValueError):
        img.show()

if __name__ == "__main__":
    import pytest
    pytest.main()
