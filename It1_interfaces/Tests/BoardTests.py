import pytest
from Board import Board
from img import Img

class DummyImg(Img):
    def __init__(self, value):
        self.value = value

    def copy(self):
        return DummyImg(self.value)

    def __eq__(self, other):
        return isinstance(other, DummyImg) and self.value == other.value and id(self) != id(other)


def test_clone_creates_deep_copy_of_img():
    # Arrange
    original_img = DummyImg(value=42)
    board = Board(
        cell_H_pix=10,
        cell_W_pix=20,
        cell_H_m=1,
        cell_W_m=2,
        W_cells=5,
        H_cells=6,
        img=original_img
    )

    # Act
    cloned_board = board.clone()

    # Assert
    assert cloned_board != board
    assert cloned_board.cell_H_pix == board.cell_H_pix
    assert cloned_board.cell_W_pix == board.cell_W_pix
    assert cloned_board.cell_H_m == board.cell_H_m
    assert cloned_board.cell_W_m == board.cell_W_m
    assert cloned_board.W_cells == board.W_cells
    assert cloned_board.H_cells == board.H_cells
    assert cloned_board.img == board.img  # same content
    assert cloned_board.img is not board.img  # different object


def test_clone_on_board_with_empty_img():
    # Arrange
    class EmptyImg(Img):
        def copy(self): return self
    board = Board(
        cell_H_pix=1,
        cell_W_pix=1,
        cell_H_m=1,
        cell_W_m=1,
        W_cells=1,
        H_cells=1,
        img=EmptyImg()
    )

    # Act
    cloned = board.clone()

    # Assert
    assert cloned.img is board.img  # because copy returns same instance


def test_board_with_zero_dimensions():
    # Arrange
    dummy_img = DummyImg(value=0)
    board = Board(
        cell_H_pix=0,
        cell_W_pix=0,
        cell_H_m=0,
        cell_W_m=0,
        W_cells=0,
        H_cells=0,
        img=dummy_img
    )

    # Act
    cloned = board.clone()

    # Assert
    assert cloned.cell_H_pix == 0
    assert cloned.cell_W_pix == 0
    assert cloned.W_cells == 0
    assert cloned.img == board.img
    assert cloned.img is not board.img


def test_invalid_img_copy_raises_exception():
    # Arrange
    class BadImg(Img):
        def copy(self):
            raise RuntimeError("Copy failed")

    board = Board(
        cell_H_pix=1,
        cell_W_pix=1,
        cell_H_m=1,
        cell_W_m=1,
        W_cells=1,
        H_cells=1,
        img=BadImg()
    )

    # Act & Assert
    with pytest.raises(RuntimeError, match="Copy failed"):
        board.clone()
