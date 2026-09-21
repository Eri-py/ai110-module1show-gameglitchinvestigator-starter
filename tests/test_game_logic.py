from logic_utils import OUTCOME_MESSAGES, check_guess, parse_guess, update_score

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

# --- Edge-case tests (Challenge 1: Advanced Edge-Case Testing) ---

def test_negative_number_guess_is_handled_gracefully():
    # Edge case: a negative guess (e.g. "-5") should parse cleanly and
    # compare correctly instead of crashing or being rejected outright --
    # nothing in parse_guess/check_guess assumes the guess is non-negative.
    ok, guess, err = parse_guess("-5")
    assert ok is True
    assert guess == -5
    assert err is None
    assert check_guess(-5, 50) == "Too Low"

def test_decimal_guess_truncates_toward_zero():
    # Edge case: a decimal guess is accepted via int(float(raw)), so "50.9"
    # truncates to 50 (not rounded, not rejected as invalid input).
    ok, guess, err = parse_guess("50.9")
    assert ok is True
    assert guess == 50
    assert err is None

def test_extremely_large_guess_does_not_crash():
    # Edge case: Python ints are arbitrary precision, so a guess far larger
    # than any normal secret should still parse and compare correctly
    # instead of overflowing, raising, or silently misbehaving.
    huge_guess = "9" * 30  # 999...9, 30 digits
    ok, guess, err = parse_guess(huge_guess)
    assert ok is True
    assert guess == int(huge_guess)
    assert err is None
    assert check_guess(guess, 50) == "Too High"
