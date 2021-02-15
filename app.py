# Chess v3.2.0 Main
# ------------------------------------------------------------------------
# Driver file used to run the application on a GUI (PyGame framework)
# ------------------------------------------------------------------------


import chess
import numpy as np
import pygame as pg

from flask import Flask
from red_chess import engine
from red_chess.position import Position

WIDTH = HEIGHT = 600
ROWS = COLS = 8
SQ_SIZE = WIDTH // ROWS
MAX_FPS = 15
IMAGES = {}
SQUARES = np.flip(np.array(chess.SQUARES).reshape(8, 8), 0)
NOTATED_FILES = ["a", "b", "c", "d", "e", "f", "g", "h"]
NOTATED_RANKS = ["8", "7", "6", "5", "4", "3", "2", "1"]

# GAME SETTINGS
VS_COMPUTER = True
PLAY_AS_WHITE = True
ENGINE_DEPTH = 3
BOOK = True
FEN = ""

app = Flask(__name__)


# Creates the GUI and runs the game
@app.route("/")
def main():
    pg.init()
    pg.display.set_caption("Chess")

    screen = pg.display.set_mode((WIDTH, HEIGHT))
    clock = pg.time.Clock()
    if FEN != "":
        position = Position(chess.Board(FEN))
    else:
        position = Position()

    load_images()

    running = True
    move_made = False
    selected = ()
    clicks = []

    if VS_COMPUTER and not PLAY_AS_WHITE:
        engine.move(position, ENGINE_DEPTH, BOOK)

    while running:
        board = position.to_array()

        if move_made:
            if VS_COMPUTER:
                engine.move(position, ENGINE_DEPTH, BOOK)

        move_made = False

        for e in pg.event.get():
            if e.type == pg.QUIT:
                running = False
            elif position.is_terminal():
                print("Game over")
            elif e.type == pg.MOUSEBUTTONDOWN:
                # Take the mouse location, convert it into square coordinates, and move there

                location = pg.mouse.get_pos()
                col = location[0] // SQ_SIZE
                row = location[1] // SQ_SIZE

                if not PLAY_AS_WHITE:
                    col = 7 - col
                    row = 7 - row

                if board[row][col] == "." and len(clicks) == 0:
                    selected = ()
                    clicks = []
                else:
                    selected = (row, col)
                    clicks.append(selected)

                if len(clicks) == 2:
                    # If the move is valid, make the move

                    piece_moved = board[clicks[0][0]][clicks[0][1]]

                    if piece_moved != ".":
                        start = NOTATED_FILES[clicks[0][1]] + NOTATED_RANKS[clicks[0][0]]
                        end = NOTATED_FILES[clicks[1][1]] + NOTATED_RANKS[clicks[1][0]]
                        move = start + end
                        if piece_moved.lower() == "p":
                            if NOTATED_RANKS[clicks[1][0]] == "8" or NOTATED_RANKS[clicks[1][0]] == "1":
                                move += "q"

                        try:
                            position.get_state().parse_uci(move)

                            if len(move) == 5:
                                move = move[:-1] + input("Enter promotion piece: ").lower()

                            position.get_state().push_uci(move)

                            move_made = True
                        except:
                            pass

                    selected = ()
                    clicks = []

            elif e.type == pg.KEYDOWN:
                # Undo the move

                if e.key == pg.K_LEFT:
                    try:
                        position.get_state().pop()

                        if VS_COMPUTER:
                            position.get_state().pop()
                            position.get_state().pop()

                        move_made = True
                    except:
                        print("Empty stack")

        try:
            last_move = position.get_state().peek()
        except:
            last_move = None

        draw_state(screen, position, selected, last_move)

        if not PLAY_AS_WHITE:
            screen.blit(pg.transform.rotate(screen, 180), (0, 0))

        clock.tick(MAX_FPS)
        pg.display.flip()


# Loads the piece images found in the images directory (replace filepath for custom images)
def load_images():
    white_pieces = ["P", "R", "N", "B", "Q", "K"]
    black_pieces = ["p", "r", "n", "b", "q", "k"]

    for piece in white_pieces:
        image = pg.image.load("images/pieces/w" + piece + ".png")
        IMAGES[piece] = pg.transform.smoothscale(image.convert_alpha(), (SQ_SIZE, SQ_SIZE))

    for piece in black_pieces:
        image = pg.image.load("images/pieces/c" + piece + ".png")
        IMAGES[piece] = pg.transform.smoothscale(image.convert_alpha(), (SQ_SIZE, SQ_SIZE))


# Draws a given position with highlighting
def draw_state(screen, position, selected, move):
    draw_board(screen, position)
    highlight_possible_moves(screen, position, position.get_actions(), selected)

    if move is not None:
        highlight_last_move(screen, move)

    highlight_check(screen, position)


# Draws a static board (without highlighting)
def draw_board(screen, board):
    board_array = board.to_array()
    bg = pg.transform.smoothscale(pg.image.load("images/other/board.png"), (WIDTH, HEIGHT)).convert()
    screen.blit(bg, (0, 0))

    for i in range(ROWS):
        for j in range(COLS):
            piece = board_array[i][j]
            if piece != "." and piece != "None":
                if not PLAY_AS_WHITE:
                    img = pg.transform.rotate(IMAGES[piece], 180)
                else:
                    img = IMAGES[piece]

                screen.blit(img, pg.Rect(j * SQ_SIZE, i * SQ_SIZE, SQ_SIZE, SQ_SIZE))


# Highlights the possible moves
def highlight_possible_moves(screen, position, valid_moves, selected):
    if len(selected) > 0:
        r, c = selected
        board_array = position.to_array()

        if board_array[r][c] == ".":
            return

        s = pg.Surface((SQ_SIZE, SQ_SIZE))

        s.set_alpha(100)
        s.fill(pg.Color("yellow"))
        screen.blit(s, (c * SQ_SIZE, r * SQ_SIZE))

        dot = pg.image.load("images/other/highlight_green.png")
        dot = pg.transform.smoothscale(dot, (SQ_SIZE, SQ_SIZE))
        capture_dot = pg.image.load("images/other/capture_highlight.png")
        capture_dot = pg.transform.smoothscale(capture_dot, (SQ_SIZE, SQ_SIZE))

        for move in valid_moves:
            move_start_coordinates = np.argwhere(SQUARES == move.from_square)[0]
            move_end_coordinates = np.argwhere(SQUARES == move.to_square)[0]

            move_start_coordinates = [move_start_coordinates[0], move_start_coordinates[1]]
            move_end_coordinates = [move_end_coordinates[1], move_end_coordinates[0]]

            if [r, c] == move_start_coordinates:
                if board_array[move_end_coordinates[1]][move_end_coordinates[0]] == ".":
                    screen.blit(dot, (SQ_SIZE * move_end_coordinates[0], SQ_SIZE * move_end_coordinates[1]))
                else:
                    screen.blit(capture_dot, (SQ_SIZE * move_end_coordinates[0], SQ_SIZE * move_end_coordinates[1]))


# Highlights the last move made
def highlight_last_move(screen, move):
    s = pg.Surface((SQ_SIZE, SQ_SIZE))
    s.set_alpha(100)
    s.fill(pg.Color("green"))

    move_start_coordinates = np.argwhere(SQUARES == move.from_square)[0]
    move_end_coordinates = np.argwhere(SQUARES == move.to_square)[0]

    move_start_coordinates = [move_start_coordinates[0], move_start_coordinates[1]]
    move_end_coordinates = [move_end_coordinates[1], move_end_coordinates[0]]

    screen.blit(s, (move_start_coordinates[1] * SQ_SIZE, move_start_coordinates[0] * SQ_SIZE))
    screen.blit(s, (move_end_coordinates[0] * SQ_SIZE, move_end_coordinates[1] * SQ_SIZE))


# Highlights a check
def highlight_check(screen, position):
    side = position.get_player()

    if position.get_state().is_check():
        s = pg.Surface((SQ_SIZE, SQ_SIZE))
        s.set_alpha(100)
        s.fill(pg.Color("red"))

        image = pg.transform.smoothscale(pg.image.load("images/other/highlight_red.png"), (SQ_SIZE, SQ_SIZE))
        king_location = position.get_king_location(side)

        screen.blit(image, (king_location[1] * SQ_SIZE, king_location[0] * SQ_SIZE))


if __name__ == '__main__':
    app.debug = True
    app.run(host="localhost", port=8080)
