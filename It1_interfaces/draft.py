# Graphics = get curr images
# Physics  = get curr pos
# State    = Graphics + Physics + Transitions to other states
# Piece    = ID + Moves + Wrapper for State (to hide state transitions)
# Board    = background + pix / world dimensions
# Game     = Pieces + Board + run() # game logic.

# run()
#     in = listen to keyboard
#     process_input(in)
    
#design patterns:
# Factory, Command, Tempalte, State Machine

import time
from Board import Board
from PieceFactory import PieceFactory
from State import State
from Moves import Moves
from Piece import Piece
from Game import Game
from img import Img


def create_game(board_path, root_folder):
    pieces_templates = {} # { piece_id : piece }
    game_pieces = []

    background =r"C:\Users\m0583\Desktop\bc\CTD25\board.png"
    board,p = Board.read_board_and_pieces(board_path,Img().read(background) , [0,0])
    factory = PieceFactory(board, root_folder)
    # print("Board loaded with dimensions:", board.W_cells, "x", board.H_cells)
    # print("Found pieces:", len(p), "at locations:", p)
    for piece_id, location in p:
        if piece_id not in pieces_templates:
            pieces_templates[piece_id] = factory.create_piece(piece_id)
        
        p = pieces_templates[piece_id].clone()
        
        row, col = location
        if not (0 <= row < board.H_cells and 0 <= col < board.W_cells):
            print(f"Warning: piece {piece_id} has invalid location {location} "
                f"for board size {board.H_cells}x{board.W_cells}")
        
        now_ms = int(time.time() * 1000)
        px = board.cell_to_px(location)
        print(f"Creating piece {piece_id} at cell {location}, pixel pos: {px}")

        p.set_current_cell(location, now_ms)
        game_pieces.append(p)
        # game_pieces.append(create_piece(piece_id, root_folder))


    game = Game(game_pieces, board)
    
    game._draw()
    game._show()
    
    return game
      



def main():
    game = create_game(r"C:\Users\m0583\Desktop\bc\CTD25\pieces\board.csv", r"C:\Users\m0583\Desktop\bc\CTD25\pieces")
    game.run()
    
if __name__ == "__main__":
    main()
    
