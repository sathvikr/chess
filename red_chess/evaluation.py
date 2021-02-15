# Chess v3.2.0 Evaluation
# --------------------------------------------------------------
# Returns a score describing how good a player's position is in that player's perspective
# --------------------------------------------------------------

def evaluate(position):
    position_data = {
        "material": {
            "weight": 1,
            "score": (position.get_material_difference() + position.get_relative_material())
        },
    }

    evaluation = 0

    for value in position_data.values():
        evaluation += value["weight"] * value["score"]

    if not position.get_player():
        evaluation *= -1

    return evaluation / 100
