import chess.pgn

pgn = open("filter_more.pgn")
games = []

counter = 0

while True:
    game = chess.pgn.read_game(pgn)
    if game is None:
        break
    
    counter += 1
    name = game.headers['Site'].split("/")[-1]
    new_content = str(game.headers) + "\n"
    
    while game.next():
        game=game.next()
        new_content += f"{game.board().fen()}\n"
    
    if counter%1000 == 0:
        print(counter)
        
    file = open(f"/Users/tobiaswilfert/Documents/University/IR/chess-db/filter_more/{name}.txt", "w")
    file.write(new_content)