from dotenv import load_dotenv
load_dotenv()
import os, chess
import numpy as np

import keras
opener_model = None
mider_model = None
ender_model = None
loaded = False
def loader():
    global opener_model, mider_model, ender_model, loaded
    loaded = True
    opener_model = keras.models.load_model("open_model.keras")
    mider_model = keras.models.load_model("mid_model.keras")
    ender_model = keras.models.load_model("end_model.keras")
loop = 0
pre_bestmove = ""

def one_hot_encoding(piece):
    pieces = list('rnbqkpRNBQKP.')
    array = np.zeros(len(pieces))
    piece_to_index = {p: i for i, p in enumerate(pieces)}
    index = piece_to_index[piece]
    array[index] = 1
    return array

square_index = {'a': 0, 'b': 1, 'c': 2, 'd': 3, 'e': 4, 'f': 5, 'g': 6, 'h': 7}

def square_to_idx(square):
    letter = chess.square_name(square)
    return 8 - int(letter[1]), square_index[letter[0]]

def encode_board(board):
    board_str = str(board)
    board_str = board_str.replace(' ','')
    board_list = []

    for row in board_str.split('\n'):
        row_list = []
        for piece in row:
              row_list.append(one_hot_encoding(piece))
        board_list.append(row_list)

    board_list = np.array(board_list)
    # Attack by black piece / white piêc:
    attack_listB = np.zeros((8,13))
    attack_listW = np.zeros((8,13))

    aux = board.turn
    board.turn = chess.WHITE
    for move in board.legal_moves:
      i, j = square_to_idx(move.to_square)
      attack_listB[i][j] = 1
    attack_listB = np.expand_dims(attack_listB, axis=0)

    # board.turn = chess.BLACK
    # for move in board.legal_moves:
    #   i, j = square_to_idx(move.to_square)
    #   attack_listW[i][j] = 1
    # attack_listW = np.expand_dims(attack_listW, axis=0)

    board.turn = aux
    board_list = np.append(board_list, attack_listB, axis=0)
    # board_list = np.append(board_list, attack_listW, axis=0)

    knight_scores = np.array([[0.0, 0.1, 0.2, 0.2, 0.2, 0.2, 0.1, 0.0],
                          [0.1, 0.3, 0.5, 0.5, 0.5, 0.5, 0.3, 0.1],
                          [0.2, 0.5, 0.6, 0.65, 0.65, 0.6, 0.5, 0.2],
                          [0.2, 0.55, 0.65, 0.7, 0.7, 0.65, 0.55, 0.2],
                          [0.2, 0.5, 0.65, 0.7, 0.7, 0.65, 0.5, 0.2],
                          [0.2, 0.55, 0.6, 0.65, 0.65, 0.6, 0.55, 0.2],
                          [0.1, 0.3, 0.5, 0.55, 0.55, 0.5, 0.3, 0.1],
                          [0.0, 0.1, 0.2, 0.2, 0.2, 0.2, 0.1, 0.0]])

# Mở rộng ma trận thành kích thước (8, 13) bằng cách thêm các cột chứa giá trị 0
    knight_scores = knight_scores[::-1, :]
    knight_scores_extended = np.pad(knight_scores, ((0, 0), (0, 5)), 'constant')

# Lật ngược bảng bằng cách đảo ngược thứ tự của các cột


    bishop_scores = np.array([[0.0, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.0],
                              [0.2, 0.4, 0.4, 0.4, 0.4, 0.4, 0.4, 0.2],
                              [0.2, 0.4, 0.5, 0.6, 0.6, 0.5, 0.4, 0.2],
                              [0.2, 0.5, 0.5, 0.6, 0.6, 0.5, 0.5, 0.2],
                              [0.2, 0.4, 0.6, 0.6, 0.6, 0.6, 0.4, 0.2],
                              [0.2, 0.6, 0.6, 0.6, 0.6, 0.6, 0.6, 0.2],
                              [0.2, 0.5, 0.4, 0.4, 0.4, 0.4, 0.5, 0.2],
                              [0.0, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.0]])

    # Mở rộng ma trận thành kích thước (8, 13) bằng cách thêm các cột chứa giá trị 0
    bishop_scores = bishop_scores[::-1, :]
    bishop_scores_extended = np.pad(bishop_scores, ((0, 0), (2, 3)), 'constant')
    
    rook_scores = np.array([[0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25],
                        [0.5, 0.75, 0.75, 0.75, 0.75, 0.75, 0.75, 0.5],
                        [0.0, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.0],
                        [0.0, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.0],
                        [0.0, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.0],
                        [0.0, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.0],
                        [0.0, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.0],
                        [0.25, 0.25, 0.25, 0.5, 0.5, 0.25, 0.25, 0.25]])

# Mở rộng ma trận thành kích thước (8, 13) bằng cách thêm các cột chứa giá trị 0
    rook_scores = rook_scores[::-1, :]
    rook_scores_extended = np.pad(rook_scores, ((0, 0), (2, 3)), 'constant')
    queen_scores = np.array([[0.0, 0.2, 0.2, 0.3, 0.3, 0.2, 0.2, 0.0],
                         [0.2, 0.4, 0.4, 0.4, 0.4, 0.4, 0.4, 0.2],
                         [0.2, 0.4, 0.5, 0.5, 0.5, 0.5, 0.4, 0.2],
                         [0.3, 0.4, 0.5, 0.5, 0.5, 0.5, 0.4, 0.3],
                         [0.4, 0.4, 0.5, 0.5, 0.5, 0.5, 0.4, 0.3],
                         [0.2, 0.5, 0.5, 0.5, 0.5, 0.5, 0.4, 0.2],
                         [0.2, 0.4, 0.5, 0.4, 0.4, 0.4, 0.4, 0.2],
                         [0.0, 0.2, 0.2, 0.3, 0.3, 0.2, 0.2, 0.0]])

# Mở rộng ma trận thành kích thước (8, 13) bằng cách thêm các cột chứa giá trị 0
    queen_scores = queen_scores[::-1, :]
    queen_scores_extended = np.pad(queen_scores, ((0, 0), (2, 3)), 'constant')

    pawn_scores = np.array([[0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8],
               [0.7, 0.7, 0.7, 0.7, 0.7, 0.7, 0.7, 0.7],
               [0.3, 0.3, 0.4, 0.5, 0.5, 0.4, 0.3, 0.3],
               [0.25, 0.25, 0.3, 0.45, 0.45, 0.3, 0.25, 0.25],
               [0.2, 0.2, 0.2, 0.4, 0.4, 0.2, 0.2, 0.2],
               [0.25, 0.15, 0.1, 0.2, 0.2, 0.1, 0.15, 0.25],
               [0.25, 0.3, 0.3, 0.0, 0.0, 0.3, 0.3, 0.25],
               [0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2]])
    pawn_scores = pawn_scores[::-1, :]
    pawn_scores_extended = np.pad(pawn_scores, ((0, 0), (2, 3)), 'constant')

    rook_scores_extended = np.expand_dims(rook_scores_extended, axis=0)
    knight_scores_extended = np.expand_dims(knight_scores_extended, axis=0)
    bishop_scores_extended = np.expand_dims(bishop_scores_extended, axis=0)
    queen_scores_extended = np.expand_dims(queen_scores_extended, axis=0)
    pawn_scores_extended = np.expand_dims(pawn_scores_extended, axis=0)

    board_list = np.append(board_list, rook_scores_extended, axis=0)
    board_list = np.append(board_list, knight_scores_extended, axis=0)
    board_list = np.append(board_list, bishop_scores_extended, axis=0)
    board_list = np.append(board_list, queen_scores_extended, axis=0)
    board_list = np.append(board_list, pawn_scores_extended, axis=0)
    return board_list

# Đếm tổng điểm của quân trên bàn cờ để xác định đầu hay trung cuộc
def count_material(fen):
    material_dict = {
        'p': 1, 'b': 3, 'n': 3, 'r': 5, 'q': 9
    }

    count = 0
    for char in fen.lower():
        if char in material_dict.keys():
            count += material_dict[char]
    return count

# play với nơ non network
def play_nn(fen, show_move_evaluations=False):
    if not loaded:
        loader()
    board = chess.Board(fen)

    total_material = count_material(fen)

    if total_material > 60:
        model = opener_model
    elif total_material < 30:
        model = ender_model
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
    input_vector = input_vector.reshape((n_moves, 14, 8, 13))

    scores = model.predict(input_vector, verbose=0)
    # print(scores)

    if board.turn == chess.BLACK:
        index_of_bestmove = np.argmax(scores)
    else:
        index_of_bestmove = np.argmax(-scores)

    if show_move_evaluations:
        print(zip(scores, moves))

    best_move = moves[index_of_bestmove]
    global loop, pre_bestmove
    if loop == 0:
        pre_bestmove = str(best_move)
    loop += 1
    if loop == 3 and pre_bestmove == str(best_move):
        pass
    elif loop == 5 and pre_bestmove == str(best_move):
        pass
    elif loop == 7 and pre_bestmove == str(best_move):
        scores[index_of_bestmove] = -1000
        index_of_bestmove = np.argmax(scores)
        best_move = moves[index_of_bestmove]
        print("lppp")
        loop = 0
    elif loop == 3:
        loop = 0
        
    print("Best move: ", str(best_move))
    return str(best_move)

###########################################################
###########################################################
###########################################################
# board = [['bR', 'bN', 'bB', 'bQ', 'bK', 'bB', 'bN', 'bR'], 
#          ['bp', 'bp', 'bp', 'bp', 'bp', 'bp', 'bp', 'bp'], 
#          ['--', '--', '--', '--', '--', '--', '--', '--'], 
#          ['--', '--', '--', '--', '--', '--', '--', '--'], 
#          ['--', '--', '--', '--', '--', '--', '--', '--'], 
#          ['--', '--', '--', '--', '--', '--', '--', '--'], 
#          ['wp', 'wp', 'wp', 'wp', 'wp', 'wp', 'wp', 'wp'], 
#          ['wR', 'wN', 'wB', 'wQ', 'wK', 'wB', 'wN', 'wR']]

# print('Fen đúng: ', chess.Board().fen())
# play_nn(board_to_fen(board))
