from dataclasses import dataclass
from typing import Tuple, List

from img import Img

@dataclass
class Board:
    cell_H_pix: int
    cell_W_pix: int
    cell_H_m: int
    cell_W_m: int
    W_cells: int
    H_cells: int
    img: Img

    def __init__(self,
                 W_cells: int,
                 H_cells: int,
                 cell_W_pix: int,
                 cell_H_pix: int,
                 cell_W_m: float,
                 cell_H_m: float,
                 img: Img):
        self.W_cells = W_cells
        self.H_cells = H_cells
        self.cell_W_pix = cell_W_pix
        self.cell_H_pix = cell_H_pix
        self.cell_W_m = cell_W_m
        self.cell_H_m = cell_H_m
        self.img = img

    @staticmethod


    def read_board_and_pieces(path: str,
                            img: Img,
                            cell_size_m: Tuple[float, float]) -> Tuple["Board", List[Tuple[str, Tuple[int, int]]]]:
        pieces = []

        with open(path, 'r') as f:
            lines = [line.strip() for line in f if line.strip()]

        H_cells = len(lines)
        W_cells = max(len(line.split(',')) for line in lines)

        for row_idx, line in enumerate(lines):
            cells = line.split(',')
            for col_idx, piece_id in enumerate(cells):
                piece_id = piece_id.strip()
                if piece_id:
                    pieces.append((piece_id, (row_idx, col_idx)))

        # גישה לגודל התמונה מתוך אובייקט Img
        cell_W_pix = img.img.shape[1] // W_cells  # רוחב בפיקסלים
        cell_H_pix = img.img.shape[0] // H_cells  # גובה בפיקסלים
        cell_H_m, cell_W_m = cell_size_m

        board = Board(
            W_cells=W_cells,
            H_cells=H_cells,
            cell_W_pix=cell_W_pix,
            cell_H_pix=cell_H_pix,
            cell_W_m=cell_W_m,
            cell_H_m=cell_H_m,
            img=img
        )

        return board, pieces

    # convenience, not required by dataclass
    def clone(self) -> "Board":
        """Clone the board with a copy of the image."""
        board =Board(
            cell_H_pix=self.cell_H_pix,
            cell_W_pix=self.cell_W_pix,
            cell_H_m=self.cell_H_m,
            cell_W_m=self.cell_W_m,
            W_cells=self.W_cells,
            H_cells=self.H_cells,
            img=self.img.copy()
        )
        # print("cell_W_pix:", board.cell_W_pix)
        # print("cell_H_pix:", board.cell_H_pix)
        # print("board image size:", board.img.img.shape)
        return board
    def cell_to_px(self, cell: Tuple[int, int]) -> Tuple[int, int]:
        row, col = cell
        return (col * self.cell_W_pix, row * self.cell_H_pix)

    def px_to_cell(self, pos: Tuple[int, int]) -> Tuple[int, int]:
        """ממיר קואורדינטת פיקסל (x, y) למיקום תא (שורה, עמודה)"""
        x, y = pos
        col = x // self.cell_W_pix
        row = y // self.cell_H_pix
        return (int(row), int(col))

    def meters_to_pixels(self, dx_m: float, dy_m: float) -> Tuple[int, int]:
        """ממיר מרחק במטרים למרחק בפיקסלים"""
        dx_px = dx_m / self.cell_W_m * self.cell_W_pix
        dy_px = dy_m / self.cell_H_m * self.cell_H_pix
        return (int(dx_px), int(dy_px))

    @property
    def pixels_per_meter(self) -> float:
        """המרת מטרים לפיקסלים (ממוצע לצורך תנועה)"""
        px_per_m_x = self.cell_W_pix / self.cell_W_m
        px_per_m_y = self.cell_H_pix / self.cell_H_m
        return (px_per_m_x + px_per_m_y) / 2

