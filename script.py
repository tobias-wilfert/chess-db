import chess.pgn

# The root file
pgn = open("test.pgn")
games = []

while True:
    game = chess.pgn.read_game(pgn)
    if game is None:
        break
    games.append(game)
    

for game in games:
        print(game.headers['Site'])
        name = game.headers['Site'].split("/")[-1]
        new_content = str(game.headers)
        while game.next():
            game=game.next()
            new_content += f"{game.board().fen()}\n"
        # write to the file in the zoutput directory
        file = open(f"/Users/tobiaswilfert/Documents/University/IR/chess-db/zoutput/{name}.txt", "w")
        file.write(new_content)