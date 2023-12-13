# Report: Chess-DB - A Python-based chess explorer

## Overiew
This document is the report for the project. The more exploratory code we wrote can be found in the [1-prove-of-concept.ipynb](1-prove-of-concept.ipynb) notebook. The more structured code can be found in the notebooks in which we also tried to add comments explaining our thought process. The dataset as well as the index generated by PyLucene were not uploaded to this repo due to the size constraints of GitHub. However all the code that is needed to generate the dataset and index can be found in this repo together with the instructions below on how to do so.

## Getting the data
### Introduction
We started by examining the ['Lichees Elite Database'](https://database.nikonoel.fr) which contains only games of players with a 2400+ [elo rating](https://en.wikipedia.org/wiki/Elo_rating_system). Since this dataset was however intended to be used with [SCID](https://scid.sourceforge.net) the games were scrapped of much of the interesting meta-data since SCID itself does only support a limited amount of meta data per game.

Most of the removed meta-data was not necessarily relevant to use except for the game link. This can namely be used to look up the game on the Lichees website and view it in their editor. This sadly meant that we could not use the 'Elite Database'. Lucky this was not a big issue as we figured we could generate our own 'Elite' subset of the database by filtering out games with players with a rating below 1500 (removing the bottom 50% of players on Lichess). We also filtered out [Bullet games](https://en.wikipedia.org/wiki/Fast_chess#:~:text=from%20move%201.-,Bullet,per%2Dplayer%20games%2C%20respectively.) as we deemed the positions that arise in these games to be of lower quality, due to the heavy time constraint on the players.

It is worth noting here that this cutoff for the elo rating is arbitrary and games from lower rated players could still contain interesting positions. However with our idea in mind to maybe use the lookup feature to solve chess puzzles, by checking similar positions to the puzzle and see how the games paned out. We figured that lower rated players might still make blunders from a very strong position which would make the lookup less useful.

### Making our own 'Elite' dataset
We started by downloading the the complete set of games for September 2023 from the [Lichees website](https://database.lichess.org) since this was the most recent data available at the time of writing. This is a compressed dataset of 30GB containing 93 million games. The website also warned that the compressed file would be about 7x larger. The dataset it self contained the games in [PGN notation](https://en.wikipedia.org/wiki/Portable_Game_Notation). A sample record from the dataset can be seen below:

```pgn
[Event "Rated Bullet game"]
[Site "https://lichess.org/kLKqVm2U"]
[Date "2023.09.01"]
[Round "-"]
[White "slammayjammay"]
[Black "Zedward"]
[Result "0-1"]
[UTCDate "2023.09.01"]
[UTCTime "00:00:27"]
[WhiteElo "1982"]
[BlackElo "1979"]
[WhiteRatingDiff "-5"]
[BlackRatingDiff "+6"]
[ECO "B30"]
[Opening "Sicilian Defense: Old Sicilian"]
[TimeControl "60+0"]
[Termination "Normal"]

1. e4 { [%clk 0:01:00] } 1... c5 { [%clk 0:01:00] } 2. Nf3 { [%clk 0:00:59] } 2... Nc6 { [%clk 0:01:00] } 3. c3 { [%clk 0:00:58] } 3... e5 { [%clk 0:00:59] } 4. d4 { [%clk 0:00:58] } 4... cxd4 { [%clk 0:00:59] } 5. cxd4 { [%clk 0:00:58] } 5... exd4 { [%clk 0:00:59] } 6. Nxd4 { [%clk 0:00:57] } 6... Nf6 { [%clk 0:00:59] } 7. Nxc6 { [%clk 0:00:56] } 7... bxc6 { [%clk 0:00:59] } 8. Nc3 { [%clk 0:00:56] } 8... Bb4 { [%clk 0:00:58] } 9. f3 { [%clk 0:00:54] } 9... O-O { [%clk 0:00:57] } 10. Bd2 { [%clk 0:00:53] } 10... a5 { [%clk 0:00:57] } 11. a3 { [%clk 0:00:52] } 11... Be7 { [%clk 0:00:56] } 12. Bc4 { [%clk 0:00:51] } 12... Ba6 { [%clk 0:00:56] } 13. Qe2 { [%clk 0:00:50] } 13... Bxc4 { [%clk 0:00:54] } 14. Qxc4 { [%clk 0:00:50] } 14... Qc7 { [%clk 0:00:54] } 15. O-O { [%clk 0:00:49] } 15... Rac8 { [%clk 0:00:53] } 16. Qd3 { [%clk 0:00:48] } 16... Rfd8 { [%clk 0:00:52] } 17. Bg5 { [%clk 0:00:45] } 17... h6 { [%clk 0:00:51] } 18. Bxf6 { [%clk 0:00:44] } 18... Bxf6 { [%clk 0:00:51] } 19. Rad1 { [%clk 0:00:43] } 19... Qb6+ { [%clk 0:00:49] } 20. Kh1 { [%clk 0:00:37] } 20... Qxb2 { [%clk 0:00:48] } 21. Ne2 { [%clk 0:00:37] } 21... c5 { [%clk 0:00:45] } 22. Rd2 { [%clk 0:00:37] } 22... Qe5 { [%clk 0:00:43] } 23. Nc1 { [%clk 0:00:34] } 23... c4 { [%clk 0:00:42] } 24. Qe2 { [%clk 0:00:34] } 24... c3 { [%clk 0:00:41] } 25. Na2 { [%clk 0:00:34] } 25... cxd2 { [%clk 0:00:40] } 26. Nc3 { [%clk 0:00:33] } 26... Qxc3 { [%clk 0:00:39] } 27. Qf2 { [%clk 0:00:32] } 27... Qc1 { [%clk 0:00:37] } 28. Qg3 { [%clk 0:00:32] } 28... Qxf1# { [%clk 0:00:36] } 0-1
```

This representation is remarkably efficient since it encodes the board position after every move implicitly by only storing the moves. This makes it ideal for exploring games with a specific opening since we can simply look at the first few moves of the game to determine the opening. The downside of this encoding is that it is not possible to look at the board position at a specific point in the game without replaying the game up to that point. Doing this ad-hoc for a query is obviously not feasible.

To overcome this issue we decided to convert the PGN representation of a game into a series of [Forsyth–Edwards Notation (FEN)](https://en.wikipedia.org/wiki/Forsyth%E2%80%93Edwards_Notation) representations of the board position after every move. This is a representation that takes up much more space, but it allows us to look at the board position at any point in the game without having to replay the game up to that point.

_An interesting side note is that the FEN notation itself already uses compression to reduce the size of the representation. It does this by only storing the number of empty squares between pieces instead of storing all the empty squares explicitly. This of course is a form of [run-length encoding](https://en.wikipedia.org/wiki/Run-length_encoding). Which is very similar to the Front coding compression that we have seen during the lesson._

Armed with the information that our representation would be less efficient that the PGN and that the raw PGN was already 7x larger than the compressed 30GB file we decided to only use a subset of the data. More specifically we limited us to the most recent 2 million games between players with elo of at least 1500 for all formats except Bullet.

We achieved this by first un-compressing 50GB of games using the follwoing command, this was possible since zst can partially be decompressed:
```bash 
pzstd -d lichess_db_standard_rated_2023-09.pgn.zst
```
Next up we ran the following python script to filter out the games that we wanted:
```python
import chess.pgn

pgn = open("lichess_db_standard_rated_2023-09.pgn")
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
            file = open("filtered.pgn", "a")
            file.write(f"{str(game)}\n\n")
            
            if(counter%100 == 0):
                print(counter)
            if(counter == 250000):
                break
```

### Generating the FEN representation
Now that we had our filtered dataset we could start generating the FEN representation. We did this by using the [python-chess](https://python-chess.readthedocs.io/en/latest/) library. This library allows us to easily convert a PGN representation of a game into a series of FEN representations of the board position after every move. We used the following python script to generate the FEN representation. This generates a txt file per game with each row containing the FEN representation of the board position after a move and the first row containing the meta-data of the game.
```python
import chess.pgn

pgn = open("filtered.pgn")
games = []

counter = 0

while True:
    game = chess.pgn.read_game(pgn)
    if game is None:
        break
    
    counter += 1
    name = game.headers['Site'].split("/")[-1]
    new_content = str(game.headers)+"\n"
    
    while game.next():
        game=game.next()
        new_content += f"{game.board().fen()}\n"
    
    if counter%1000 == 0:
        print(counter)
        
    file = open(f"good_games/{name}.txt", "w")
    file.write(new_content)
```

### Our Dataset
The above steps thus yielded a directory containing files with unique names (the game identifier used by Lichess). Each file containing the board position after every move of the game. This has the added benefit that if a file is a match for our query we can check which row resulted in a match to not only know the game that matched but also the move that matched. A subset of such a file can be seen below:

```FEN
...
rnbqkbnr/pp2pppp/2p5/8/4p3/2N2N2/PPPP1PPP/R1BQKB1R w KQkq - 0 4
rnbqkbnr/pp2pppp/2p5/8/4N3/5N2/PPPP1PPP/R1BQKB1R b KQkq - 0 4
rn1qkbnr/pp2pppp/2p5/5b2/4N3/5N2/PPPP1PPP/R1BQKB1R w KQkq - 1 5
rn1qkbnr/pp2pppp/2p5/5b2/8/5NN1/PPPP1PPP/R1BQKB1R b KQkq - 2 5
rn1qkbnr/pp2pppp/2p3b1/8/8/5NN1/PPPP1PPP/R1BQKB1R w KQkq - 3 6
rn1qkbnr/pp2pppp/2p3b1/8/7P/5NN1/PPPP1PP1/R1BQKB1R b KQkq - 0 6
...
```

## Querying the data
### Setting up PyLucene
As mentioned in our proposal we wanted to use [PyLucene](https://lucene.apache.org/pylucene/) the reason for that was twofold, on the one hand we wanted to use an existing library since we understood that the implementation of a library would be much better than anything that we could come up with in the time that we had. For that [Lucene](https://lucene.apache.org) seemed like a good choice since it is a very mature library with a lot of features. On the other hand we wanted to use Python since both of use are not very familiar with Java. On top of that using Python would allow us to use Jupiter notebook which lends itself to a more exploratory approach to the problem. It is worth noting here that PyLucene turned out to be quite tricky to set up on Windows, however we eventually got it working in the [Linux subsystem for Windows](https://learn.microsoft.com/en-us/windows/wsl/install). In geneal we would recommend using a Linux or Unix based systems.

... 