import os
import chess.pgn

# TODO: THis is the simple one for now can become more complex later
def board_position(board):
    output = ""
    
    for square, piece in board.piece_map().items():
        output += " " + piece.symbol()+chess.square_name(square)
    
    return output

num_games = 0
# Open the PGN file
with open("test_subset.pgn") as pgn_file:
    game = chess.pgn.read_game(pgn_file)
    
    while game:
        num_games += 1
        game = chess.pgn.read_game(pgn_file)
        if game is None:
            break
        
        # Create the directory
        path = game.headers["Site"]
        id = path[path.rfind("/")+1:]
        dir_path = "./z_converter/" + id
        # print(dir_path)
        os.makedirs(dir_path, exist_ok=True)
        
        
        # Loop over the game and generate the files in the directory
        move_counter = 0
        board = game.board()
        for move in game.mainline_moves():
            move_counter += 1
            board.push(move)
            
            with open(dir_path + "/" + str(move_counter) + ".txt", "w") as f:
                f.write(board_position(board))
                
# Print the number of games
print(f"The number of games in 'test_subset.pgn' is: {num_games}")
