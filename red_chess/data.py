# Chess v3.2.0 Data
# --------------------------------------------------------------
# Data structures for use in the transposition table
# --------------------------------------------------------------

# Contains a move and its score
class Entry:

    def __init__(self, move, score):
        self.move = move
        self.score = score
        self.data = {
            "move": self.move,
            "score": self.score
        }

    def __str__(self):
        return str(self.data)

    def get_move(self):
        return self.move

    def get_score(self):
        return self.score

    def get_data(self):
        return self.data

    def set_move(self, move):
        self.move = move
        self.data["move"] = move

    def set_score(self, score):
        self.score = score
        self.data["score"] = score


# Represents a single entry in the transposition table
class Transposition:
    NOT_PRESENT = -1
    EXACT = 0
    LOWER_BOUND = 1
    UPPER_BOUND = 2

    def __init__(self, flag, entry, depth):
        self.flag = flag
        self.entry = entry
        self.depth = depth
        self.data = {
            "flag": self.flag,
            "entry": self.entry,
            "depth": self.depth
        }

    def __str__(self):
        s = ""

        for key, value in self.data.items():
            s += str(key) + ': ' + str(value) + "\n"

        return "\n" + s

    def get_flag(self):
        return self.flag

    def get_entry(self):
        return self.entry

    def get_depth(self):
        return self.depth

    def get_data(self):
        return self.data

    def set_flag(self, flag):
        self.flag = flag
        self.data["flag"] = flag

    def set_entry(self, entry):
        self.entry = entry
        self.data["entry"] = entry

    def set_depth(self, depth):
        self.depth = depth
        self.data["depth"] = depth


# Represents the transposition table
class TranspositionTable:

    def __init__(self, transpositions=None):
        if transpositions is None:
            transpositions = {}

        self.transpositions = transpositions

    def __str__(self):
        s = ""

        for key, value in self.get_transpositions().items():
            s += str(key) + ": " + str(value)

        return s

    def get_transpositions(self):
        return self.transpositions

    def get(self, key):
        try:
            return self.transpositions[key]
        except KeyError:
            return Transposition(Transposition.NOT_PRESENT, None, 0)

    def store(self, key, transposition):
        self.transpositions[key] = transposition
