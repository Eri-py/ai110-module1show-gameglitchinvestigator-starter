def get_range_for_difficulty(difficulty: str):
    """Return (low, high) inclusive range for a given difficulty."""
    if difficulty == "Easy":
        return 1, 20
    if difficulty == "Normal":
        return 1, 100
    if difficulty == "Hard":
        return 1, 50
    return 1, 100


def parse_guess(raw: str):
    """
    Parse user input into an int guess.

    Returns: (ok: bool, guess_int: int | None, error_message: str | None)
    """
    if raw is None or raw == "":
        return False, None, "Enter a guess."

    try:
        if "." in raw:
            value = int(float(raw))
        else:
            value = int(raw)
    except Exception:
        return False, None, "That is not a number."

    return True, value, None


def check_guess(guess, secret):
    """
    Compare guess to secret and return the outcome.

    Returns one of: "Win", "Too High", "Too Low"
    """
    # FIX: Refactored out of app.py and dropped the str(secret) cast that
    # made this fall into a lexicographic string comparison (AI-assisted
    # root-cause diagnosis; agent mode applied the refactor + fix together).
    if guess == secret:
        return "Win"
    if guess > secret:
        return "Too High"
    return "Too Low"


# FIX: These were inverted relative to their outcome labels — "Too High"
# (guess overshot the secret) was paired with "Go HIGHER!" and "Too Low" with
# "Go LOWER!", telling the player the opposite of the correct direction on
# every single guess. Swapped so the advice matches the outcome.
OUTCOME_MESSAGES = {
    "Win": "🎉 Correct!",
    "Too High": "📉 Go LOWER!",
    "Too Low": "📈 Go HIGHER!",
}


def update_score(current_score: int, outcome: str, attempt_number: int):
    """Update score based on outcome and attempt number."""
    # FIX: Win formula no longer double-counts the attempt (was `attempt_number + 1`,
    # which under-scored every win by 10), and "Too High" no longer rewards a wrong
    # guess with +5 on even attempts — both always cost 5 points now.
    if outcome == "Win":
        points = 100 - 10 * attempt_number
        if points < 10:
            points = 10
        return current_score + points

    if outcome == "Too High" or outcome == "Too Low":
        return current_score - 5

    return current_score
