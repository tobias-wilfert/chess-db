import chess.pgn

# The root file
pgn = open("lichess_db_standard_rated_2023-09.pgn")


file = open("/Users/tobiaswilfert/Documents/University/IR/chess-db/filter_more.pgn", "w")

counter = 0
while True:
    game = chess.pgn.read_game(pgn)
    if game is None:
        break
    
    # Filter bullet games
    if game.headers["Event"] != "Rated Bullet game":
        # Filter the games with players with less than 1200 elo
        if int(game.headers["WhiteElo"]) >= 1500 and int(game.headers["BlackElo"]) >= 1500:
            counter += 1
            if counter > 250000 :

                file.write(f"{str(game)}\n\n")
            
            if(counter%1000 == 0):
                print(counter)
                
print(counter)