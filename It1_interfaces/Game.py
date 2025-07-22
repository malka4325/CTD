import inspect
import pathlib
import queue, threading, time, cv2, math
from typing import List, Dict, Tuple, Optional
from Board   import Board
from Command import Command
from Piece   import Piece
from img     import Img


class InvalidBoard(Exception): ...
# ────────────────────────────────────────────────────────────────────
class Game:
    def __init__(self, pieces: List[Piece], board: Board):
        """Initialize the game with pieces, board, and optional event bus."""
        self.pieces = { p.piece_id : p for p in pieces}
        self.board = board
        self.start_time = None
        self.user_input_queue = queue.Queue()
        self.mouse_callback_active = False

    # ─── helpers ─────────────────────────────────────────────────────────────
    def game_time_ms(self) -> int:
        """Return the current game time in milliseconds."""
        if self.start_time is None:
            self.start_time = time.perf_counter()
        return int((time.perf_counter() - self.start_time) * 1000)

    def clone_board(self) -> Board:
        """
        Return a **brand-new** Board wrapping a copy of the background pixels
        so we can paint sprites without touching the pristine board.
        """
        return self.board.clone()

    def start_user_input_thread(self):
        """Start the user input thread for mouse handling."""
        def mouse_callback(event, x, y, flags, param):
            if not self.mouse_callback_active:
                return
                
            if event == cv2.EVENT_LBUTTONDOWN:
                # Convert pixel coordinates to cell coordinates
                cell_c = x // self.board.cell_W_pix
                cell_r = y // self.board.cell_H_pix
                
                # Find piece at this location
                for piece_id, piece in self.pieces.items():
                    piece_pos = piece.get_current_cell()
                    if piece_pos and piece_pos == (cell_r, cell_c):
                        # Create a move command (simplified - just move one cell right as example)
                        target_cell = (cell_r, cell_c + 1)
                        if target_cell[1] < self.board.W_cells:  # Valid move
                            cmd = Command(
                                timestamp=self.game_time_ms(),
                                piece_id=piece_id,
                                type="Move",
                                params=[piece_pos, target_cell]
                            )
                            self.user_input_queue.put(cmd)
                        break
        
        cv2.namedWindow("Game Window")
        cv2.setMouseCallback("Game Window", mouse_callback)
        self.mouse_callback_active = True

    # ─── main public entrypoint ──────────────────────────────────────────────
    def run(self):
        """Main game loop."""
        self.start_user_input_thread() # QWe2e5

        start_ms = self.game_time_ms()
        for piece_id, p in self.pieces.items():
            p.reset(start_ms)

        # ─────── main loop ──────────────────────────────────────────────────
        while not self._is_win():
            now = self.game_time_ms() # monotonic time ! not computer time.

            # (1) update physics & animations
            for piece_id, p in self.pieces.items():
                p.update(now)

            # (2) handle queued Commands from mouse thread
            while not self.user_input_queue.empty(): # QWe2e5
                cmd: Command = self.user_input_queue.get()
                self._process_input(cmd)

            # (3) draw current position
            self._draw()
            if not self._show():           # returns False if user closed window
                break

            # (4) detect captures
            self._resolve_collisions()

            # Small sleep to prevent excessive CPU usage
            time.sleep(0.016)  # ~60 FPS

        self._announce_win()
        cv2.destroyAllWindows()

    # ─── drawing helpers ────────────────────────────────────────────────────
    def _process_input(self, cmd : Command):
        if cmd.piece_id in self.pieces:
            self.pieces[cmd.piece_id].on_command(cmd, cmd.timestamp)

    def _draw(self):
        """Draw the current game state."""
        # Start with a fresh board copy
        current_board = self.clone_board()
        
        # Draw all pieces on the board
        now = self.game_time_ms()
        for piece_id, piece in self.pieces.items():
            piece.draw_on_board(current_board, now)
        
        # Store the drawn board for showing
        self.current_frame = current_board

    def _show(self) -> bool:
        """Show the current frame and handle window events."""
        if hasattr(self, 'current_frame') and self.current_frame.img.img is not None:
            cv2.imshow("Game Window", self.current_frame.img.img)
            
            # Check for window close or ESC key
            key = cv2.waitKey(1) & 0xFF
            if key == 27 or cv2.getWindowProperty("Game Window", cv2.WND_PROP_VISIBLE) < 1:
                return False
        return True

    # ─── capture resolution ────────────────────────────────────────────────
    def _resolve_collisions(self):
        """Resolve piece collisions and captures."""
        pieces_list = list(self.pieces.values())
        
        for i in range(len(pieces_list)):
            for j in range(i + 1, len(pieces_list)):
                piece1, piece2 = pieces_list[i], pieces_list[j]
                
                # Get current positions
                pos1 = piece1.get_current_cell()
                pos2 = piece2.get_current_cell()
                
                # Check if pieces are in the same cell
                if pos1 and pos2 and pos1 == pos2:
                    # Determine capture based on piece capabilities
                    if piece1.can_capture() and piece2.can_be_captured():
                        self._capture_piece(piece2)
                    elif piece2.can_capture() and piece1.can_be_captured():
                        self._capture_piece(piece1)

    def _capture_piece(self, piece: Piece):
        """Remove a captured piece from the game."""
        if piece.piece_id in self.pieces:
            del self.pieces[piece.piece_id]

    # ─── board validation & win detection ───────────────────────────────────
    def _is_win(self) -> bool:
        """Check if the game has ended."""
        # Simple win condition: only one piece type remaining
        piece_types = set()
        for piece in self.pieces.values():
            piece_type = piece.piece_id[0]  # First character as type
            piece_types.add(piece_type)
        
        return len(piece_types) <= 1

    def _announce_win(self):
        """Announce the winner."""
        if self.pieces:
            remaining_piece = next(iter(self.pieces.values()))
            winner_type = remaining_piece.piece_id[0]
            print(f"Game Over! Winner: {winner_type}")
        else:
            print("Game Over! No winner (all pieces captured)")
        
        # Show final message on screen
        if hasattr(self, 'current_frame'):
            self.current_frame.img.put_text(
                "GAME OVER", 
                50, 50, 
                2.0, 
                (0, 255, 0), 
                3
            )
            cv2.imshow("Game Window", self.current_frame.img.img)
            cv2.waitKey(3000)  # Show for 3 seconds