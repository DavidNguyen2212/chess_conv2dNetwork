import numpy as np
import random, chess, chess.svg
# from IPython.display import SVG
import IPython

def play_game(ai_function):
    board = chess.Board()

    while board.outcome() is None:

        if board.turn == chess.WHITE:
            usermove = input("User move: ")
            if usermove == 'quit':
                break
            # else check whether valid move
            valid_moves = [str(move) for move in board.legal_moves]
            while usermove not in valid_moves:
                print("This is not a valid move, try again!")
                usermove = input("User move: ")
            print("Usermove: ", usermove)
            board.push_san(usermove)
            html_code = chess.svg.board(board=board)
            display(IPython.display.HTML(html_code))
            print("------------")
            print("------------")
            print("------------")
        else: # Ai turn
            aimove = ai_function(board.fen())
            print("AI moves: ", aimove)
            board.push_san(aimove)
            html_code = chess.svg.board(board=board)
            display(IPython.display.HTML(html_code))
            print("------------")
            print("------------")
            print("------------")


    print(board.outcome())

def one_hot_encoding(piece):
    pieces = list('rnbqkpRNBQKP.')
    array = np.zeros(len(pieces))
    piece_to_index = {p: i for i, p in enumerate(pieces)}
    index = piece_to_index[piece]
    array[index] = 1
    return array

def encode_board(board):
    board_str = str(board)
    board_str = board_str.replace(' ','')
    board_list = []

    for row in board_str.split('\n'):
        row_list = []
        for piece in row:
            row_list.append(one_hot_encoding(piece))
        board_list.append(row_list)

    return np.array(board_list)
def count_material(fen):
    material_dict = {
        'p': 1, 'b': 3, 'n': 3, 'r': 5, 'q': 9
    }

    count = 0
    for char in fen.lower():
        if char in material_dict.keys():
            count += material_dict[char]
    return count
from keras.models import load_model

opener_model = load_model("open_model.keras")
mider_model = load_model("mid_model.keras")
ender_model = load_model("end_model.keras")

def play_nn(fen, show_move_evaluations=False):
    board = chess.Board(fen)

    total_material = count_material(fen)

    if total_material < 30:
        model = ender_model
    elif total_material > 60:
        model = opener_model
    else:
        model = mider_model

    # Evaluate all legal moves
    moves = []
    input_vectors = []

    for legal_move in board.legal_moves:
        candidate_board = board.copy()
        candidate_board.push(legal_move)
        moves.append(legal_move)
        input_vectors.append(encode_board(candidate_board).astype(np.int32).flatten())

    input_vector = np.stack(input_vectors)
    # Run fail shape input vector if load from keras model
    # To fix, reshape it
    n_moves = input_vector.shape[0]
    input_vector = input_vector.reshape((n_moves, 8, 8, 13))

    scores = model.predict(input_vector, verbose=0) 
    # print(scores)

    if board.turn == chess.BLACK:
        index_of_bestmove = np.argmax(scores)
    else:
        index_of_bestmove = np.argmax(-scores)

    if show_move_evaluations:
        print(zip(scores, moves))

    best_move = moves[index_of_bestmove]
    return str(best_move)
play_game(play_nn)