# Chess v3.2.0 Engine
# --------------------------------------------------------------
# Attempts to find the best move in any inputted position
# --------------------------------------------------------------

import math
import chess
from chess import polyglot, gaviota
from red_chess import data
from red_chess.position import Position
from red_chess.search import negamax

# Used for the opening book (change filepath for custom opening book )
BOOKS = ["gm2600", "Elo2400", "DCbook_large", "final-book", "komodo", "KomodoVariety", "Performance", "codekiddy"]

# Used for the endgame tablebase (change filepath for custom tablebase)
TABLEBASE = gaviota.open_tablebase("endgames/gaviota_3/gtb")


# Finds the best move in a given position at specified depth
def move(position, depth, book):
    if position.is_terminal():
        return None

    action = None

    if book:
        action = book_action(position)

    if action == chess.Move.null() or action is None:
        action = mate_n(position)

        if action is None:
            action = get_best_action(position, depth).get_move()
        else:
            action = action.get_move()
    elif book:
        print("Book")

    position.get_state().push(action)

    return action


# If there is a book move, return it
def book_action(position):
    action = chess.Move.null()
    i = 0

    while action == chess.Move.null() and i < len(BOOKS):
        book = chess.polyglot.MemoryMappedReader("openings/" + BOOKS[i] + ".bin")

        try:
            action = book.weighted_choice(position.get_state()).move
        except Exception:
            action = chess.Move.null()

        book.close()
        i += 1

    return action


# If the move is present in the endgame tablebase, return it.
def mate_n(position):
    try:
        TABLEBASE.probe_dtm(position.get_state())
    except Exception:
        return None

    wdl = TABLEBASE.probe_wdl(position.get_state())

    best = None
    best_score = math.inf if wdl > 0 else -math.inf

    for action in position.get_actions():
        is_mate = False
        position.get_state().push(action)
        dtm = TABLEBASE.probe_dtm(position.get_state())

        if dtm == 0 and position.get_winner() != 0:
            is_mate = True

        position.get_state().pop()

        if abs(dtm) < best_score and wdl > 0 or abs(dtm) > best_score and wdl < 0 or dtm == 0 and wdl == 0:

            if dtm != 0 or is_mate or dtm == 0 and wdl == 0:
                position.get_state().push(action)

                if TABLEBASE.probe_wdl(position.get_state()) == -wdl:
                    best_score = abs(dtm)
                    best = action

                position.get_state().pop()

    print("M" + str(best_score))

    return data.Entry(best, best_score)


# Returns the best move given the position sing a negamax search with a handcrafted heuristic
def get_best_action(position, depth):
    best_move = chess.Move.null()
    best_score = -math.inf
    alpha = -math.inf
    beta = math.inf
    actions = position.get_actions()

    for action in actions:
        position.get_state().push(action)
        score = -negamax(position, -beta, -alpha, depth - 1)

        if score > best_score:
            best_score = score
            best_move = action

        if score > alpha:
            alpha = score

        position.get_state().pop()

    if best_move == chess.Move.null():
        best_move = actions[0]

    return data.Entry(best_move, best_score)
