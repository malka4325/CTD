import pathlib
from typing import Dict, Tuple
import json
from Board import Board
from GraphicsFactory import GraphicsFactory
from Moves import Moves
from PhysicsFactory import PhysicsFactory
from Piece import Piece
from State import State


class PieceFactory:
    def __init__(self, board: Board, pieces_root: pathlib.Path):
        """Initialize piece factory with board and 
        generates the library of piece templates from the pieces directory.."""
        self.board = board
        self.pieces_root = pieces_root # root folder containing all piece folders
        self.piece_templates: Dict[str, Piece] = {}  # piece_id -> Piece
        self._load_piece_templates()
    
    def _load_piece_templates(self):
        """Load all piece templates from the pieces directory."""
        for piece_dir in self.pieces_root.iterdir():
            if not piece_dir.is_dir():
                continue
            piece_id = piece_dir.name  # לדוגמה: "knight", "bishop"
            # בנה את המצב ההתחלתי של הפיס
            initial_state = self._build_state_machine(piece_dir)
            # יצירת פיס חדש עם המצב ההתחלתי
            piece = Piece(piece_id, initial_state)
            # הוספת הפיס למילון של תבניות פיסים
            self.piece_templates[piece_id] = piece
          
            


    def _build_state_machine(self, piece_dir: pathlib.Path) -> State:
        """Build the state machine for a piece from its directory."""
        # קריאת הגדרות הפיס מהקובץ config.json
        config_path = piece_dir / "config.json"
        if not config_path.exists():
            raise FileNotFoundError(f"Config file not found for piece {piece_dir.name}")
        with open(config_path, "r") as f:
            cfg = json.load(f)
        # יצירת גרפיקה מהספרייה
        sprites_dir = piece_dir / "sprites"
        if not sprites_dir.exists():
            raise FileNotFoundError(f"Sprites directory not found for piece {piece_dir.name}")
        graphics = self._load_graphics(sprites_dir, cfg)
        # יצירת פיזיקה מההגדרות
        physics = self._load_physics(cfg)
        # יצירת אובייקט מצב התחלתי
        initial_state = State(graphics, physics)
        # קריאת מהלכים מהקובץ moves.txt
        moves_path = piece_dir / "moves.txt"
        if not moves_path.exists():
            raise FileNotFoundError(f"Moves file not found for piece {piece_dir.name}")
        moves = self._load_moves(moves_path)
        # הגדרת המצב ההתחלתי עם המהלכים
        initial_state.set_moves(moves)
        # הגדרת המעברים בין המצבים
        states_dir = piece_dir / "states"
        if not states_dir.exists():
            raise FileNotFoundError(f"States directory not found for piece {piece_dir.name}")
        states: Dict[str, State] = {}  # שם מצב -> אובייקט מצב
        for state_folder in states_dir.iterdir():
            if not state_folder.is_dir():
                continue
            state_name = state_folder.name
            config_path = state_folder / "config.json"
            if not config_path.exists():
                raise FileNotFoundError(f"Config file not found for state {state_name} in piece {piece_dir.name}")
            with open(config_path, "r") as f:
                state_cfg = json.load(f)
            sprites_dir = state_folder / "sprites"
            if not sprites_dir.exists():
                raise FileNotFoundError(f"Sprites directory not found for state {state_name} in piece {piece_dir.name}")
            graphics = self._load_graphics(sprites_dir, state_cfg)
            physics = self._load_physics(state_cfg)
            # יצירת אובייקט מצב
            state = State(graphics, physics)
            # הגדרת המהלכים למצב זה
            state.set_moves(moves)
            # הוספת המצב למילון
            states[state_name] = state
        # הגדרת המעברים בין המצבים
        for from_name, from_state in states.items():
            for to_name, to_state in states.items():
                if from_name != to_name:
                    from_state.set_transition(to_name, to_state)
        # נחזיר את המצב ההתחלתי (נניח "idle")
        return states.get("idle", initial_state)  # אם אין מצב "idle", נחזיר את המצב ההתחלתי

                


    def _load_moves(self, moves_path: pathlib.Path) -> Moves:
        """Load moves from a text file."""
        return Moves(moves_path, (self.board.H_cells, self.board.W_cells))  
    def _load_graphics(self, sprites_dir: pathlib.Path, cfg: Dict) -> Graphics:
        """Load graphics from a directory and configuration."""
        return GraphicsFactory.create_graphics(sprites_dir, cfg["graphics"])
    def _load_physics(self, cfg: Dict) -> Physics:
        """Load physics configuration."""
        return PhysicsFactory.create(cfg["physics"], self.board)



    # PieceFactory.py  – replace create_piece(...)
    def create_piece(self, p_type: str, cell: Tuple[int, int]) -> Piece:
        """Create a piece of the specified type at the given cell."""
        piece_dir = self.pieces_root / p_type
        if not piece_dir.exists():
            raise ValueError(f"Piece type {p_type} not found in {self.pieces_root}")

        # בנה את ה־State Machine עבור הכלי
        initial_state = self._build_state_machine(piece_dir)

        # צור את הפיס
        piece = Piece(p_type, initial_state)
        piece.cell = cell  # הגדר את התא ההתחלתי

        return piece
