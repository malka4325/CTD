# Moves.py  – drop-in replacement
import pathlib
from typing import List, Tuple


class Moves:

    def __init__(self, txt_path: pathlib.Path, dims: Tuple[int, int]):
        """Initialize moves with rules from text file and board dimensions."""
        self.board_height, self.board_width = dims
        self.moves = []
        self.moves: List[Tuple[int, int]] = []  # רשימת וקטורים חוקיים לתנועה
        
        with open(txt_path, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                parts = line.split(',')
                if len(parts) != 2:
                    raise ValueError(f"Invalid move format: {line}")
                
                dx, dy = int(parts[0]), int(parts[1])
                self.moves.append((dx, dy))
    
    def is_move_valid(self, start_pos: Tuple[int, int], end_pos: Tuple[int, int]) -> bool:
        dx = end_pos[0] - start_pos[0]
        dy = end_pos[1] - start_pos[1]
        
        # תנועה חוקית היא תנועה אחת מתוך רשימת הווקטורים
        return (dx, dy) in self.moves


    def get_moves(self, r: int, c: int) -> List[Tuple[int, int]]:
        """Get all possible moves from a given position."""
        possible_positions = []
        
        for dx, dy in self.moves:
            new_r = r + dx
            new_c = c + dy
            
            # בדיקה שהמיקום החדש בתוך גבולות הלוח
            if 0 <= new_r < self.board_height and 0 <= new_c < self.board_width:
                possible_positions.append((new_r, new_c))
        
        return possible_positions
