from Board import Board
from Physics import Physics


class PhysicsFactory:      # very light for now
    def __init__(self, board: Board): 
        """Initialize physics factory with board."""
        self.board = board
        
        
    def create(self, start_cell, cfg) -> Physics:
        """Create a physics object with the given configuration."""
            # יצירת מופע Physics עם המידע הדרוש
        physics_obj = Physics(start_cell=start_cell, config=cfg, board=self.board)
        return physics_obj
         