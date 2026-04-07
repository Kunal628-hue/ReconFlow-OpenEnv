
def sanitize_score(score):
    """
    Ensures that all score values are strictly between 0 and 1.
    Handles booleans and non-numeric types.
    """
    try:
        if isinstance(score, bool):
            score = 1.0 if score else 0.0
        else:
            score = float(score)
    except (ValueError, TypeError):
        score = 0.01

    if score <= 0.0:
        return 0.01
    if score >= 1.0:
        return 0.99
    return score
