from logic_utils import OUTCOME_MESSAGES, check_guess, update_score

def test_winning_guess():
    # If the secret is 50 and guess is 50, it should be a win
    result = check_guess(50, 50)
    assert result == "Win"

def test_guess_too_high():
    # If secret is 50 and guess is 60, hint should be "Too High"
    result = check_guess(60, 50)
    assert result == "Too High"

def test_guess_too_low():
    # If secret is 50 and guess is 40, hint should be "Too Low"
    result = check_guess(40, 50)
    assert result == "Too Low"

def test_guess_too_low_regression_backwards_hint_bug():
    # Regression test for the "backwards hints" bug: app.py used to cast the
    # secret to str on even-numbered attempts, so guess=9 vs secret=10 got
    # compared lexicographically ("9" > "10" is True) and returned "Too High".
    # Numerically 9 < 10, so this must be "Too Low".
    result = check_guess(9, 10)
    assert result == "Too Low"

def test_update_score_win_awards_full_points_on_first_attempt():
    # Regression test for the scoring bug: the win formula used to be
    # 100 - 10 * (attempt_number + 1), which under-scored a first-attempt
    # win as 70 instead of the intended 90.
    score = update_score(0, "Win", 1)
    assert score == 90

def test_update_score_too_high_always_costs_points():
    # Regression test: "Too High" used to award +5 instead of -5 on even
    # attempt numbers, rewarding a wrong guess. It must always cost 5 points.
    score = update_score(100, "Too High", 2)
    assert score == 95

def test_hint_messages_match_their_outcome_direction():
    # Regression test: the "Too High"/"Too Low" hint text used to be
    # swapped -- a guess that was too high told the player to go HIGHER
    # (and vice versa), which is backwards advice on every single guess.
    assert "LOWER" in OUTCOME_MESSAGES["Too High"]
    assert "HIGHER" in OUTCOME_MESSAGES["Too Low"]
