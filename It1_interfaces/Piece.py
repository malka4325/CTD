from Board import Board
from Command import Command
from State import State
from typing import Tuple, Optional
import cv2


class Piece:
    def __init__(self, piece_id: str, init_state: State):
        """Initialize a piece with ID and initial state."""
        self.piece_id = piece_id
        self._state = init_state
        self._current_cell = None
        self._last_update_time = None
    def set_current_cell(self, cell: Tuple[int, int], now_ms: int):
        """Set the current cell of the piece and update its state."""
        self._current_cell = cell
        self._state.reset(Command(
            timestamp=now_ms,
            piece_id=self.piece_id,
            type="reset",
            params=[cell]
        ))
        self._last_update_time = now_ms 
    def get_current_cell(self) -> Optional[Tuple[int, int]]:
        """Return the current cell of the piece."""
        return self._current_cell
    
    def clone(self) -> "Piece":
        """Return a deep copy of this piece."""
        cloned_piece = Piece(
            piece_id=self.piece_id,
            init_state=self._state.clone()
        )
        cloned_piece._current_cell = self._current_cell
        cloned_piece._last_update_time = self._last_update_time
        return cloned_piece

    def on_command(self, cmd: Command, now_ms: int):
        """Handle a command for this piece."""
        if self.is_command_possible(cmd):
            # Update the command with this piece's ID
            cmd.piece_id = self.piece_id
            
            # Transition to new state
            new_state = self._state.process_command(cmd, now_ms)
            if new_state != self._state:
                self._state = new_state
                self._state.update(now_ms)

    def is_command_possible(self, cmd: Command) -> bool:
        """Check if a command is possible for this piece in its current state."""
        # Basic validation
        if cmd.type == "Move" and len(cmd.params) >= 2:
            from_cell, to_cell = cmd.params[0], cmd.params[1]
            
            # Check if the move is valid according to piece rules
            moves = self._state.get_moves()
            if moves:
                valid_moves = moves.get_moves(from_cell[0], from_cell[1])
                return to_cell in valid_moves
            
            # If no move rules, allow any adjacent move as default
            row_diff = abs(to_cell[0] - from_cell[0])
            col_diff = abs(to_cell[1] - from_cell[1])
            return row_diff <= 1 and col_diff <= 1 and (row_diff + col_diff) > 0
        
        # Check if current state can handle this command type
        return self._state.can_transition(cmd.type)

    def reset(self, start_ms: int):
        """Reset the piece to idle state."""
        reset_cmd = Command(
            timestamp=start_ms,
            piece_id=self.piece_id,
            type="reset",
            params=[]
        )
        self._state.reset(reset_cmd)
        self._last_update_time = start_ms

    def update(self, now_ms: int):
        """Update the piece state based on current time."""
        self._state = self._state.update(now_ms)
        self._last_update_time = now_ms

    def draw_on_board(self, board: Board, now_ms: int):
        """Draw the piece on the board with cooldown overlay."""
        graphics = self._state.get_graphics()
        physics = self._state.get_physics()
        
        if graphics and physics:
            draw_pos = physics.get_draw_position(now_ms)
           # cooldown_ratio = self._state.get_cooldown_ratio(now_ms)

            graphics.draw(board.img, draw_pos)

            # אופציונלי: הוספת צל קירור אם יש remaining_cooldown
            # cooldown_ratio = self._state.get_cooldown_ratio(now_ms)
            # if cooldown_ratio > 0:
            #     overlay = graphics.get_cooldown_overlay(cooldown_ratio)
            #     x, y = draw_pos
            #     h, w = overlay.shape[:2]
            #     board.img.frame[y:y+h, x:x+w] = cv2.addWeighted(
            #         board.img.frame[y:y+h, x:x+w], 0.5,
            #         overlay, 0.5, 0
            #     )
