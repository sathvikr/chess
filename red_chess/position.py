# Chess v3.2.0 Position
# --------------------------------------------------------------
# Data structure used to encapsulate the board and generate various pieces of information about a state.
# --------------------------------------------------------------

from contextlib import suppress

# Library used for move generation
import chess

import numpy as np
import random


def piece_index(piece):
    return list(Position.piece_values.keys()).index(piece) if piece in Position.piece_values else -1


# Returns rectangular coordinates for a square in range [0, 64]
def get_square_coordinates(square):
    squares = np.flip(np.array(chess.SQUARES).reshape(8, 8), 0)

    return np.argwhere(squares == square)[0]


class Position:
    squares = np.flip(np.array(chess.SQUARES).reshape(8, 8), 0)
    phases = {
        "endgame": 110
    }
    pieces = {
        chess.PAWN: 100,
        chess.KNIGHT: 320,
        chess.BISHOP: 330,
        chess.ROOK: 500,
        chess.QUEEN: 900,
        chess.KING: 20000
    }
    piece_phases = {
        chess.PAWN: [0, 16],
        chess.KNIGHT: [1, 4],
        chess.BISHOP: [1, 4],
        chess.ROOK: [2, 4],
        chess.QUEEN: [4, 2]
    }
    piece_symbols = {
        chess.PAWN: "P",
        chess.KNIGHT: "N",
        chess.BISHOP: "B",
        chess.ROOK: "R",
        chess.QUEEN: "Q",
        chess.KING: "K"
    }
    attack_weights = {
        "N": 20,
        "B": 20,
        "R": 40,
        "Q": 80
    }
    piece_values = {
        "P": 100,
        "N": 320,
        "B": 330,
        "R": 500,
        "Q": 900,
        "K": 20000,
        "p": 100,
        "n": 320,
        "b": 330,
        "r": 500,
        "q": 900,
        "k": 20000
    }
    piece_square_tables = {
        chess.PAWN:
            [
                0, 0, 0, 0, 0, 0, 0, 0,
                5, 10, 10, -20, -20, 10, 10, 5,
                5, -5, -10, 0, 0, -10, -5, 5,
                0, 0, 0, 20, 20, 0, 0, 0,
                5, 5, 10, 25, 25, 10, 5, 5,
                10, 10, 20, 30, 30, 20, 10, 10,
                50, 50, 50, 50, 50, 50, 50, 50,
                0, 0, 0, 0, 0, 0, 0, 0
            ],

        chess.KNIGHT:
            [
                -50, -40, -30, -30, -30, -30, -40, -50,
                -40, -20, 0, 5, 5, 0, -20, -40,
                -30, 5, 10, 15, 15, 10, 5, -30,
                -30, 0, 15, 20, 20, 15, 0, -30,
                -30, 5, 15, 20, 20, 15, 5, -30,
                -30, 0, 10, 15, 15, 10, 0, -30,
                -40, -20, 0, 0, 0, 0, -20, -40,
                -50, -40, -30, -30, -30, -30, -40, -50
            ],

        chess.BISHOP:
            [
                -20, -10, -10, -10, -10, -10, -10, -20,
                -10, 5, 0, 0, 0, 0, 5, -10,
                -10, 10, 10, 10, 10, 10, 10, -10,
                -10, 0, 10, 10, 10, 10, 0, -10,
                -10, 5, 5, 10, 10, 5, 5, -10,
                -10, 0, 5, 10, 10, 5, 0, -10,
                -10, 0, 0, 0, 0, 0, 0, -10,
                -20, -10, -10, -10, -10, -10, -10, -20
            ],

        chess.ROOK:
            [
                0, 0, 0, 5, 5, 0, 0, 0,
                -5, 0, 0, 0, 0, 0, 0, -5,
                -5, 0, 0, 0, 0, 0, 0, -5,
                -5, 0, 0, 0, 0, 0, 0, -5,
                -5, 0, 0, 0, 0, 0, 0, -5,
                -5, 0, 0, 0, 0, 0, 0, -5,
                5, 10, 10, 10, 10, 10, 10, 5,
                0, 0, 0, 0, 0, 0, 0, 0
            ],
        chess.QUEEN:
            [
                -20, -10, -10, -5, -5, -10, -10, -20,
                -10, 0, 0, 0, 0, 0, 0, -10,
                -10, 5, 5, 5, 5, 5, 0, -10,
                0, 0, 5, 5, 5, 5, 0, -5,
                -5, 0, 5, 5, 5, 5, 0, -5,
                -10, 0, 5, 5, 5, 5, 0, -10,
                -10, 0, 0, 0, 0, 0, 0, -10,
                -20, -10, -10, -5, -5, -10, -10, -20
            ],

        chess.KING:
            [
                20, 30, 10, 0, 0, 10, 30, 20,
                20, 20, 0, 0, 0, 0, 20, 20,
                -10, -20, -20, -20, -20, -20, -20, -10,
                -20, -30, -30, -40, -40, -30, -30, -20,
                -30, -40, -40, -50, -50, -40, -40, -30,
                -30, -40, -40, -50, -50, -40, -40, -30,
                -30, -40, -40, -50, -50, -40, -40, -30,
                -30, -40, -40, -50, -50, -40, -40, -30
            ]

    }

    endgame_piece_square_table = {
        chess.PAWN:
            [
                0, 0, 0, 0, 0, 0, 0, 0,
                5, 10, 10, -20, -20, 10, 10, 5,
                5, 5, 10, 20, 20, 10, 5, 5,
                10, 10, 15, 30, 30, 15, 10, 10,
                15, 15, 20, 35, 35, 20, 15, 15,
                20, 20, 30, 40, 40, 30, 20, 20,
                60, 60, 60, 60, 60, 60, 60, 60,
                0, 0, 0, 0, 0, 0, 0, 0
            ],

        chess.KING:
            [
                -50, -40, -30, -20, -20, -30, -40, -50,
                -30, -20, -10, 0, 0, -10, -20, -30,
                -30, -10, 20, 30, 30, 20, -10, -30,
                -30, -10, 30, 40, 40, 30, -10, -30,
                -30, -10, 30, 40, 40, 30, -10, -30,
                -30, -10, 20, 30, 30, 20, -10, -30,
                -30, -30, 0, 0, 0, 0, -30, -30,
                -50, -30, -30, -30, -30, -30, -30, -50
            ]
    }

    # Predefined king safety table retrieved from Stockfish
    safety_table = [
        0, 0, 1, 2, 3, 5, 7, 9, 12, 15,
        18, 22, 26, 30, 35, 39, 44, 50, 56, 62,
        68, 75, 82, 85, 89, 97, 105, 113, 122, 131,
        140, 150, 169, 180, 191, 202, 213, 225, 237, 248,
        260, 272, 283, 295, 307, 319, 330, 342, 354, 366,
        377, 389, 401, 412, 424, 436, 448, 459, 471, 483,
        494, 500, 500, 500, 500, 500, 500, 500, 500, 500,
        500, 500, 500, 500, 500, 500, 500, 500, 500, 500,
        500, 500, 500, 500, 500, 500, 500, 500, 500, 500,
        500, 500, 500, 500, 500, 500, 500, 500, 500, 500
    ]

    attack_table = [0, 0, 50, 75, 88, 94, 97, 99]

    center_squares = [chess.D4, chess.E4, chess.D5, chess.E5]
    ztable = [[[random.randint(1, 2 ** 64 - 1) for i in range(12)] for j in range(8)] for k in range(8)]

    def __init__(self, state=chess.Board()):
        self.state = state

    def __str__(self):
        return self.state.unicode()

    # Getters
    def get_state(self):
        return self.state

    def get_actions(self):
        return sorted(list(self.state.legal_moves), key=self.sort_actions)
        # return list(self.state.legal_moves)

    def get_player(self):
        return self.state.turn

    def get_result(self, action):
        self.state.push(action)
        result = self.state.copy()
        self.state.pop()

        return Position(result)

    def get_captures(self):
        return sorted(list(self.state.generate_legal_captures()), key=self.sort_captures)
        # return list(self.state.generate_legal_captures())

    def get_checks_and_captures(self):
        checks_and_captures = self.get_captures()

        for action in self.get_actions():
            if self.state.gives_check(action):
                checks_and_captures.append(action)

        return checks_and_captures

    def get_king_location(self, side):
        return get_square_coordinates(self.state.king(side))

    def get_phase(self):
        total_phase = 0
        subtract = 0

        for piece in Position.piece_phases:
            total_phase += Position.piece_phases[piece][0] * Position.piece_phases[piece][1]
            white_pieces = len(self.state.pieces(piece, chess.WHITE))
            black_pieces = len(self.state.pieces(piece, chess.BLACK))
            subtract += white_pieces + black_pieces

        phase = total_phase - subtract

        return (phase * 256 + (total_phase / 2)) / total_phase

    def get_zobrist_hash(self):
        board = self.to_array()
        h = 0

        for i in range(8):
            for j in range(8):
                if board[i][j] != '.':
                    piece = piece_index(board[i][j])
                    h ^= Position.ztable[i][j][piece]

        return h

    def is_terminal(self):
        return self.state.is_game_over()

    # Utility methods
    def to_array(self):
        board_array = np.array(str(self.state).split("\n"))
        final_board_array = []

        for row in board_array:
            final_board_array.append(row.split(" "))

        return np.array(final_board_array)

    # Evaluation methods
    # Checkmate
    def get_winner(self):
        if self.state.is_checkmate():
            return -1 if self.get_player() == chess.WHITE else 1
        else:
            return 0

    # Material
    def get_material(self):
        white_material = 0
        black_material = 0

        for piece in Position.pieces:
            white_pieces = len(self.state.pieces(piece, chess.WHITE))
            black_pieces = len(self.state.pieces(piece, chess.BLACK))
            white_material += white_pieces * Position.pieces[piece]
            black_material += black_pieces * Position.pieces[piece]

        return white_material, black_material

    def get_white_material(self):
        return self.get_material()[0]

    def get_black_material(self):
        return self.get_material()[1]

    def get_relative_material(self):
        points = 0

        for piece in Position.pieces:
            points += self.get_psq_value(piece)

        # print(self, points)

        return points

    def get_material_difference(self):
        material = self.get_material()

        return material[0] - material[1]

    # Center control
    def get_center_control(self):
        white_control = 0
        black_control = 0

        for square in Position.center_squares:
            if self.state.is_attacked_by(chess.WHITE, square):
                white_control += 1
            if self.state.is_attacked_by(chess.BLACK, square):
                black_control += 1

        return white_control, black_control

    def get_white_center_control(self):
        return self.get_center_control()[0]

    def get_black_center_control(self):
        return self.get_center_control()[1]

    def get_center_control_difference(self):
        center_control = self.get_center_control()

        return center_control[0] - center_control[1]

    # Central pawn occupancy
    def get_central_pawn_occupancy(self):
        white_occupancy = 0
        black_occupancy = 0

        for square in Position.center_squares:
            if str(self.state.piece_at(square)) == "p":
                black_occupancy += 1
            if str(self.state.piece_at(square)) == "P":
                white_occupancy += 1

        return white_occupancy, black_occupancy

    def get_white_central_pawn_occupancy(self):
        return self.get_central_pawn_occupancy()[0]

    def get_black_central_pawn_occupancy(self):
        return self.get_central_pawn_occupancy()[1]

    def get_central_pawn_occupancy_difference(self):
        central_pawn_occupancy = self.get_central_pawn_occupancy()

        return central_pawn_occupancy[0] - central_pawn_occupancy[1]

    # Piece mobility
    def get_white_mobility(self):
        if not self.get_player():
            self.state.push(chess.Move.null())

        count = len(list(self.state.legal_moves))
        self.state.pop()

        return count

    def get_black_mobility(self):
        if self.get_player():
            self.state.push(chess.Move.null())

        count = len(list(self.state.legal_moves))
        self.state.pop()

        return count

    def get_mobility_difference(self):
        return self.get_white_mobility() - self.get_black_mobility()

    # Space
    def get_space(self):
        white_space = 0
        black_space = 0

        for square in chess.SQUARES:
            if len(list(self.state.attackers(chess.WHITE, square))) > 0:
                white_space += 1
            if len(list(self.state.attackers(chess.BLACK, square))) > 0:
                black_space += 1

        return white_space, black_space

    def get_white_space(self):
        return self.get_space()[0]

    def get_black_space(self):
        return self.get_space()[1]

    def get_space_difference(self):
        space = self.get_space()

        return space[0] - space[1]

    # King safety
    def get_king_safety(self):
        attacking_piece_count = 0
        value_of_attacks = 0
        king_zone = self.get_king_zone(not self.get_player())
        piece_attacks = {"N": 0, "B": 0, "R": 0, "Q": 0}

        for action in self.state.pseudo_legal_moves:
            piece = str(self.state.piece_at(action.from_square)).upper()

            if piece in self.attack_weights:
                if action.to_square in king_zone:
                    if piece_attacks[piece] == 0:
                        attacking_piece_count += 1

                    piece_attacks[piece] += 1

        for attack in piece_attacks:
            value_of_attacks += piece_attacks[attack] * self.attack_weights[attack]

        if attacking_piece_count >= len(self.attack_table):
            king_attack_score = value_of_attacks * 99
        else:
            king_attack_score = value_of_attacks * self.attack_table[attacking_piece_count]

        return king_attack_score

    # Tempo
    def get_tempo(self, square=None):
        if square is not None:
            return 0

        return 28 if self.get_player() else -28

    # Helper methods
    # Sorts moves using MVV/LVA move ordering
    def sort_actions(self, action):
        score = 0

        if self.state.is_capture(action):
            victim = str(self.state.piece_at(action.to_square))
            attacker = str(self.state.piece_at(action.from_square))

            if victim != "None" and attacker != "None":
                score -= Position.piece_values[victim] - Position.piece_values[attacker]

        self.state.push(action)

        if self.is_terminal():
            score -= 999

        self.state.pop()

        return score

    # Sorts captures using MVV/LVA move ordering
    def sort_captures(self, capture):
        victim = str(self.state.piece_at(capture.to_square))
        attacker = str(self.state.piece_at(capture.from_square))

        if victim == "None" or attacker == "None":
            return 999

        return -(Position.piece_values[victim] - Position.piece_values[attacker])

    # Gets the relative value of a piece based on its position on the board
    def get_psq_value(self, piece):
        phase = self.get_phase()
        if phase >= Position.phases["endgame"] and (piece == chess.KING or piece == chess.PAWN):
            table = Position.endgame_piece_square_table[piece]

            if piece == chess.KING:
                pawntable = Position.endgame_piece_square_table[chess.PAWN]
        else:
            table = Position.piece_square_tables[piece]

        psq = sum([table[i] for i in self.state.pieces(piece, chess.WHITE)])
        psq += sum([-table[chess.square_mirror(i)] for i in self.state.pieces(piece, chess.BLACK)])

        if phase >= Position.phases["endgame"] and piece == chess.KING:
            white_pawn_locations = self.state.pieces(chess.PAWN, chess.WHITE)
            black_pawn_locations = self.state.pieces(chess.PAWN, chess.BLACK)
            white_king_distance = 0
            black_king_distance = 0
            white_weights = 0
            black_weights = 0

            if len(white_pawn_locations) > 0:
                for i in white_pawn_locations:
                    white_king_distance += chess.square_distance(self.state.king(chess.WHITE), i) * \
                                           pawntable[i]

                    white_weights += pawntable[i]

            if len(black_pawn_locations) > 0:
                for i in black_pawn_locations:
                    black_king_distance += chess.square_distance(self.state.king(chess.BLACK), i) * \
                                           -pawntable[chess.square_mirror(i)]

                    black_weights -= pawntable[chess.square_mirror(i)]

            white_pawn_tropism = white_king_distance / white_weights if white_weights != 0 else 0
            black_pawn_tropism = black_king_distance / black_weights if black_weights != 0 else 0

            psq += white_pawn_tropism + black_pawn_tropism

        return psq

    # Gets the number of pawns protecting the kings (out of 3)
    def get_king_shields(self):
        white_score = 0
        black_score = 0
        white_king_location = self.get_king_location(chess.WHITE)
        w_r, w_c = white_king_location
        black_king_location = self.get_king_location(chess.BLACK)
        b_r, b_c = black_king_location
        board = self.to_array()
        directions = [1, 0, -1]

        for direction in directions:
            with suppress(IndexError):
                if board[w_r - 1][w_c + direction] != "P":
                    white_score -= 1

            with suppress(IndexError):
                if board[b_r + 1][b_c + direction] != "p":
                    black_score -= 1

        return white_score, black_score

    # Gets the area near a specific king
    def get_king_zone(self, color):
        same = self.state.king(color)
        opposite = self.state.king(not color)
        square_set = []

        if self.get_player() != color:
            self.state.push(chess.Move.null())

        for action in self.state.pseudo_legal_moves:
            # print(action)
            if action.from_square == same:
                square_set.append(action.to_square)

                if opposite < same:
                    with suppress(IndexError):
                        square_set.append(action.to_square - 8)
                    with suppress(IndexError):
                        square_set.append(action.to_square - 16)
                else:
                    with suppress(IndexError):
                        square_set.append(action.to_square + 8)
                    with suppress(IndexError):
                        square_set.append(action.to_square + 16)

        self.state.pop()

        return list(chess.SquareSet(square_set))
