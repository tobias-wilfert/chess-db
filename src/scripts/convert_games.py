
import os
import sys
import chess.pgn

NUM_MOVES_SKIP = 10  # Skip the first 12 moves of the games since these are usually theory

def a_closure(board):
    #FIXME: This ignores en passant attacks for now since they are a bit tricky
    t = board.turn
    
    board.turn = chess.WHITE
    w_capture_moves = [move for move in board.legal_moves if board.is_capture(move) and not board.is_en_passant(move)]
    w_a_closure = [board.piece_at(x.from_square).symbol() + ">" + board.piece_at(x.to_square).symbol() + chess.square_name(x.to_square) for x in w_capture_moves]

    board.turn = chess.BLACK
    b_capture_moves = [move for move in board.legal_moves if board.is_capture(move) and not board.is_en_passant(move)]
    b_a_closure = [board.piece_at(x.from_square).symbol() + ">" + board.piece_at(x.to_square).symbol() + chess.square_name(x.to_square) for x in b_capture_moves]

    board.turn = t
    return w_a_closure + b_a_closure

def d_closure(board):
    d_closure = []

    for square, piece in board.piece_map().items():
        if piece.piece_type != chess.KING: # Defending a king doesn't really make sense
            d_closure += [board.piece_at(x).symbol() + '<' + piece.symbol() + chess.square_name(square) for x in board.attackers(piece.color, square)]

    return d_closure

def p_closure(board):
    return [p.symbol()+chess.square_name(s) for s,p in board.piece_map().items()]


def main(pgn_file_path):
    num_games = 0

    # Open the PGN file
    with open(pgn_file_path) as pgn_file:
        game = chess.pgn.read_game(pgn_file)
        
        while game:
            num_games += 1
            
            game = chess.pgn.read_game(pgn_file)
            if game is None:
                break
            
            # Create the directory
            path = game.headers["Site"]
            id = path[path.rfind("/")+1:]
            dir_path = "./games"
            
            # Loop over the game and generate the files in the directory
            move_counter = 0
            board = game.board()
            entries = str(game.headers) + "\n"
            for move in game.mainline_moves():
                move_counter += 1
                board.push(move)
                
                if move_counter > NUM_MOVES_SKIP:
                    entries += " ".join(p_closure(board)) + " | "
                    entries += " ".join(a_closure(board)) + " | "
                    entries += " ".join(d_closure(board))
                    entries += "\n"

            if entries:
                with open(dir_path + f"/{id}.txt", "w") as f:
                    f.write(entries)

            if num_games % 10000 == 0:
                print(f"Processed {num_games} games so far...")
            
    print(f"The number of games in '{pgn_file_path}' is: {num_games}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        pgn_file_path = sys.argv[1]
        main(pgn_file_path)
    else:
        print("Please provide the path to the PGN file as an argument.")
