from Board import Board
from Physics import Physics, IdlePhysics, MovePhysics, JumpPhysics
from typing import Tuple, Dict


class PhysicsFactory:
    def __init__(self, board: Board):
        """Initialize physics factory with reference to the board."""
        self.board = board

    def create(self, start_cell: Tuple[int, int], cfg: Dict) -> Physics:
        physics_type = cfg.get("type", "idle").lower()
        speed = cfg.get("speed", 1.0)

        if physics_type == "idle":
            return IdlePhysics(start_cell, self.board, speed)
        elif physics_type == "move":
            return MovePhysics(start_cell, self.board, speed)
        elif physics_type == "jump":
            return JumpPhysics(start_cell, self.board, speed)
        else:
            raise ValueError(f"Unsupported physics type: {physics_type}")

      