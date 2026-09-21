import json
import os

HIGH_SCORE_FILE = "high_scores.json"


def get_range_for_difficulty(difficulty: str):
    """Return the inclusive guessing range for a difficulty level.

    Args:
        difficulty: One of "Easy", "Normal", or "Hard". Any other value
            (including unrecognized strings) falls back to the Normal range.

    Returns:
        A ``(low, high)`` tuple of ints giving the inclusive bounds the
        secret number is drawn from.
    """
    if difficulty == "Easy":
        return 1, 20
    if difficulty == "Normal":
        return 1, 100
    if difficulty == "Hard":
        return 1, 50
    return 1, 100


def parse_guess(raw: str):
    """Parse a player's raw text input into an integer guess.

    Decimal input is accepted and truncated toward zero (e.g. ``"50.9"``
    becomes ``50``), matching Python's own ``int(float(...))`` behavior.
    Negative numbers and arbitrarily large integers are accepted as-is;
    nothing here enforces that the guess falls within the game's range.

    Args:
        raw: The raw string from the guess text input. ``None`` or an
            empty string is treated as "no guess entered".

    Returns:
        A ``(ok, guess_int, error_message)`` tuple:
            - ``ok``: ``True`` if parsing succeeded, ``False`` otherwise.
            - ``guess_int``: the parsed integer, or ``None`` if ``ok`` is
              ``False``.
            - ``error_message``: a user-facing error string when ``ok`` is
              ``False``, otherwise ``None``.
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
    """Compare a guess to the secret number and classify the outcome.

    Args:
        guess: The player's parsed guess (an int; see :func:`parse_guess`).
        secret: The secret number to compare against (an int).

    Returns:
        ``"Win"`` if the guess equals the secret, ``"Too High"`` if the
        guess overshot it, or ``"Too Low"`` if it undershot it. Pair the
        result with :data:`OUTCOME_MESSAGES` to get player-facing hint text.
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
    """Compute the player's new score after one guess.

    A win awards ``100 - 10 * attempt_number`` points (minimum 10), so
    guessing correctly earlier scores more. Any wrong guess ("Too High"
    or "Too Low") costs a flat 5 points; any other outcome leaves the
    score unchanged.

    Args:
        current_score: The score before this guess.
        outcome: The result of :func:`check_guess` -- ``"Win"``,
            ``"Too High"``, or ``"Too Low"``.
        attempt_number: The 1-based count of guesses made so far,
            including this one.

    Returns:
        The updated score as an int.
    """
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


def get_proximity_label(guess: int, secret: int, low: int, high: int) -> str:
    """Classify how close a guess is to the secret as a "hot/cold" label.

    Distance is measured as a fraction of the full guessing range
    (``high - low``), so "hot" means proportionally close for the current
    difficulty rather than close in absolute terms -- a miss by 2 is
    scorching on Easy (range 1-20) but merely warm on Normal (1-100).
    Purely presentational: it has no effect on scoring or win/loss and
    does not replace :func:`check_guess`.

    Args:
        guess: The player's guess.
        secret: The secret number.
        low: The inclusive lower bound of the current difficulty's range.
        high: The inclusive upper bound of the current difficulty's range.

    Returns:
        An emoji + label string, from ``"🔥 Blazing Hot!"`` (very close)
        down to ``"🥶 Ice Cold"`` (far away). A guess equal to the secret
        returns ``"🎯 Bullseye!"``.
    """
    if guess == secret:
        return "🎯 Bullseye!"

    span = high - low
    ratio = abs(guess - secret) / span if span > 0 else 1.0

    if ratio <= 0.02:
        return "🔥 Blazing Hot!"
    if ratio <= 0.05:
        return "🥵 Hot"
    if ratio <= 0.15:
        return "😐 Warm"
    if ratio <= 0.30:
        return "🧊 Cool"
    return "🥶 Ice Cold"


def load_high_scores(file_path: str = HIGH_SCORE_FILE) -> dict:
    """Load per-difficulty high scores from a JSON file.

    A missing or corrupted file is treated as "no scores yet" rather than
    an error, so a fresh install or a damaged save file never crashes the
    game.

    Args:
        file_path: Path to the JSON save file. Defaults to
            :data:`HIGH_SCORE_FILE`; tests pass a temp path here to avoid
            touching the real save file.

    Returns:
        A dict mapping difficulty name to best score, e.g.
        ``{"Normal": 85}``. Empty if the file is missing, unreadable, not
        valid JSON, or its top-level value isn't an object.
    """
    if not os.path.exists(file_path):
        return {}
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}
    return data if isinstance(data, dict) else {}


def save_high_score(
    difficulty: str, score: int, file_path: str = HIGH_SCORE_FILE
) -> bool:
    """Save a score as the new high score for a difficulty, if it's better.

    Args:
        difficulty: The difficulty this score was earned on, e.g. "Normal".
        score: The score to record.
        file_path: Path to the JSON save file. Defaults to
            :data:`HIGH_SCORE_FILE`; tests pass a temp path here to avoid
            touching the real save file.

    Returns:
        ``True`` if ``score`` beat the previous best (or none existed yet)
        and the file was updated; ``False`` if the existing high score was
        kept because it was already greater than or equal to ``score``.
    """
    scores = load_high_scores(file_path)
    current_best = scores.get(difficulty)
    if current_best is not None and score <= current_best:
        return False

    scores[difficulty] = score
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(scores, f, indent=2)
    return True
