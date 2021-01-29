# Chess v3.2.0 Search
# --------------------------------------------------------------
# Contains the search algorithms used by the engine
# --------------------------------------------------------------

import math
import chess

from red_chess import data
from red_chess.evaluation import evaluate

TT = data.TranspositionTable()


# Recursively explores each state in the game tree until the max depth is reached
# and finds the best score for a given position
def negamax(position, alpha, beta, max_depth, depth=0, searching=True):
    if not searching:
        return evaluate(position)

    zhash = position.get_zobrist_hash()
    a = alpha

    transposition = TT.get(zhash)

    if transposition.get_flag() != data.Transposition.NOT_PRESENT and transposition.get_depth() >= depth:
        if transposition.get_flag() == data.Transposition.EXACT:
            return transposition.get_entry().get_score()
        elif transposition.get_flag() == data.Transposition.LOWER_BOUND:
            alpha = max(alpha, transposition.get_entry().get_score())
        elif transposition.get_flag() == data.Transposition.UPPER_BOUND:
            beta = min(beta, transposition.get_entry().get_score())

        if alpha >= beta:
            return transposition.get_entry().get_score()

    entry = data.Entry(chess.Move.null(), -math.inf)

    if position.is_terminal():
        if not position.get_player():
            return -position.get_winner() * 10000
        else:
            return position.get_winner() * 10000

    if depth >= max_depth:
        return qsearch(position, alpha, beta)

    for move in position.get_actions():
        position.get_state().push(move)
        score = -negamax(position, -beta, -alpha, max_depth, depth=depth + 1)
        position.get_state().pop()

        if score >= beta:
            return score
        if score > entry.get_score():
            entry.set_move(move)
            entry.set_score(score)
        if score > alpha:
            alpha = score

    if entry.get_score() > -math.inf:
        new_transposition = data.Transposition(data.Transposition.EXACT, entry, depth)

        if entry.get_score() <= a:
            new_transposition.set_flag(data.Transposition.UPPER_BOUND)
        elif entry.get_score() >= beta:
            new_transposition.set_flag(data.Transposition.LOWER_BOUND)

        TT.store(zhash, new_transposition)

    return entry.get_score()


# Searches all possible captures after negamax is done to prevent the horizon effect
def qsearch(position, alpha, beta, depth=0, searching=True):
    if position.is_terminal():
        if not position.get_player():
            return -position.get_winner() * 10000
        else:
            return position.get_winner() * 10000

    evaluation = evaluate(position)

    if not searching:
        return evaluation

    zhash = position.get_zobrist_hash()
    a = alpha

    transposition = TT.get(zhash)

    if transposition.get_flag() != data.Transposition.NOT_PRESENT and transposition.get_depth() >= depth:
        if transposition.get_flag() == data.Transposition.EXACT:
            return transposition.get_entry().get_score()
        elif transposition.get_flag() == data.Transposition.LOWER_BOUND:
            alpha = max(alpha, transposition.get_entry().get_score())
        elif transposition.get_flag() == data.Transposition.UPPER_BOUND:
            beta = min(beta, transposition.get_entry().get_score())

        if alpha >= beta:
            return transposition.get_entry().get_score()

    if evaluation >= beta:
        return beta

    if alpha < evaluation:
        alpha = evaluation

    entry = data.Entry(chess.Move.null(), -math.inf)

    for action in position.get_captures():
        position.get_state().push(action)
        score = -qsearch(position, -beta, -alpha, depth + 1)
        position.get_state().pop()

        if score >= beta:
            return beta
        if alpha < score:
            alpha = score
            entry.set_move(action)
            entry.set_score(alpha)

    if entry.get_score() not in (-math.inf, math.inf):
        new_transposition = data.Transposition(data.Transposition.EXACT, entry, depth)

        if entry.get_score() <= a:
            new_transposition.set_flag(data.Transposition.UPPER_BOUND)
        elif entry.get_score() >= beta:
            new_transposition.set_flag(data.Transposition.LOWER_BOUND)

        TT.store(zhash, new_transposition)

    return alpha
