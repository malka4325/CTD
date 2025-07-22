import pathlib
from typing import Dict, Tuple
from Graphics import Graphics
from Board import Board


class GraphicsFactory:
    def __init__(self, board: Board):
        """Factory initialized with board reference (for size, scaling, etc.)."""
        self.board = board

    def load(self,
             sprites_dir: pathlib.Path,
             cfg: Dict,
             ) -> Graphics:
        """
        Load graphics based on configuration.

        cfg = {
            "fps": 6.0,
            "loop": True
        }
        """
        fps: float = cfg.get("fps", 6.0)
        loop: bool = cfg.get("loop", True)

        return Graphics(
            sprites_folder=sprites_dir,
            board=self.board,
            fps=fps,
            loop=loop
        )
