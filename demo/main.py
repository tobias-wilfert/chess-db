from dataclasses import dataclass
from enum import Enum
from flask import Flask, render_template, request, redirect, send_file
from IPython.core.display import HTML
import chess
import chess.pgn
import chess.svg
import lucene
import os
import pandas as pd

# from org.apache.lucene.analysis.standard import StandardAnalyzer
from java.nio.file import Paths
from org.apache.lucene.analysis.core import WhitespaceAnalyzer
from org.apache.lucene.index import DirectoryReader
from org.apache.lucene.queryparser.classic import QueryParser
from org.apache.lucene.search import IndexSearcher
from org.apache.lucene.search.similarities import BM25Similarity
from org.apache.lucene.store import NIOFSDirectory

app = Flask(__name__)
entries = []
PATH = "../games/"
val_map = {i: str(1 - (7 * i / 64)) for i in range(1, 9)}

def r_closure(board):
    t = board.turn
    board.turn = chess.WHITE
    w_none_capture_moves = [move for move in board.legal_moves if not board.is_capture(move)]
    w_r_closure = [board.piece_at(x.from_square).symbol() + chess.square_name(x.to_square) + '^' + val_map[chess.square_distance(x.from_square, x.to_square)] for x in w_none_capture_moves]

    board.turn = chess.BLACK
    b_none_capture_moves = [move for move in board.legal_moves if not board.is_capture(move)]
    b_r_closure = [board.piece_at(x.from_square).symbol() + chess.square_name(x.to_square) + '^' + val_map[chess.square_distance(x.from_square, x.to_square)] for x in b_none_capture_moves]

    board.turn = t
    return w_r_closure + b_r_closure

def a_closure(board):
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

def encode_board_position(board):
    return  " ".join(r_closure(board)) + " " + " ".join(p_closure(board)) +" "+ " ".join(a_closure(board)) +" "+ " ".join(d_closure(board))

def decode_piece_position(pos):
    board = chess.Board()
    board.set_piece_map({chess.parse_square(term[1:]): chess.Piece.from_symbol(term[0]) for term in pos.strip().split(" ")})
    return board

def run_query(searcher, analyzer, command, bound=10):
    """ Runs the actuall lucene query and collects the output. """
    escaped_command = command.replace("/", "\\/")
    query = QueryParser("contents", analyzer).parse(escaped_command)
    scoreDocs = searcher.search(query, bound).scoreDocs
    
    seen_games = set()
    output = []
    for scoreDoc in scoreDocs:
        doc = searcher.doc(scoreDoc.doc)
        link = f"https://lichess.org/{doc.get('game').split('.')[0]}#{int(doc.get('move'))}"
        
        # Skip any double matches for the games.
        if doc.get("game") in seen_games:
            continue
        
        file = open(os.path.join(PATH, doc.get("game")))
        file_content = str(file.read())
        content = file_content.split("\n")[int(doc.get("move"))-10].split("|")[0]
        header = file_content.split("\n")[0]
        file.close()
        
        output.append([doc.get('game'), doc.get('move'), link, scoreDoc.score, content, header])
        seen_games.add(doc.get("game"))
    
    return output

def score_lookup(board, bound):
    """ Wrapper for the lucene query to make it all function. """
    output = []
    directory = NIOFSDirectory(Paths.get("/Users/tobiaswilfert/Documents/University/IR/chess-db/games.index"))
    searcher = IndexSearcher(DirectoryReader.open(directory))
    searcher.setSimilarity(BM25Similarity())
    analyzer = WhitespaceAnalyzer()
    board_position = encode_board_position(board)
    print("Searching for:", board_position)
    output = run_query(searcher, analyzer, command=board_position, bound=bound)
    del searcher  
    return output



# TODO: Not sure why this hack is needed for it to work.
@app.route('/img/chesspieces/wikipedia/<path:filename>', methods=['GET'])
def custom_static(filename):
    print(filename)
    return send_file('static/img/chesspieces/wikipedia/' + filename, mimetype='image/png', as_attachment=True)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        entry = request.form.get('entry')
        query = entry
        entries.append(entry)
        return redirect('/results')
    return render_template('./index.html')

@app.route('/results')
def results():
    # TODO: Find the similar positions and return them so that the user can observe them.
    vm_env = lucene.getVMEnv()
    vm_env.attachCurrentThread()
    query = chess.Board(entries[-1])
    res = score_lookup(query, 50)
    print(f"Found {len(res)} unique games in the first 50 results.")
    filter = [[chess.svg.board(decode_piece_position(x[4])), round(x[3],5), "1-0" if ("1-0" in x[5]) else "1/2-1/2" if ("1/2-1/2" in x[5]) else "0-1", x[2] ] for x in res[:10]]
    # print(res)
    # print(filter)
    
    return render_template('./results.html', results=filter
        # [[chess.svg.board(chess.Board(entries[-1])), 43, 1-0, 'https://lichess.org/7UZcJXGc']]
        , query = chess.svg.board(chess.Board(entries[-1])))

if __name__ == '__main__':
    try:
        print("Initializing VM")
        lucene.initVM(vmargs=['-Djava.awt.headless=true'])  # This needs to be run once to get it all going
    except ValueError as e:
        print("VM already initialized")
    
    app.run()

# Interesting game: 8/p1pk4/1p2pp2/8/3P1P2/2P1KR1r/PP6/8