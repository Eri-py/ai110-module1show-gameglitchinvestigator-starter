import random

import streamlit as st

from logic_utils import (
    OUTCOME_MESSAGES,
    check_guess,
    get_proximity_label,
    get_range_for_difficulty,
    load_high_scores,
    parse_guess,
    save_high_score,
    update_score,
)

st.set_page_config(page_title="Glitchy Guesser", page_icon="🎮")

st.title("🎮 Game Glitch Investigator")
st.caption("An AI-generated guessing game. Something is off.")

st.sidebar.header("Settings")

difficulty = st.sidebar.selectbox(
    "Difficulty",
    ["Easy", "Normal", "Hard"],
    index=1,
)

attempt_limit_map = {
    "Easy": 6,
    "Normal": 8,
    "Hard": 5,
}
attempt_limit = attempt_limit_map[difficulty]

low, high = get_range_for_difficulty(difficulty)

st.sidebar.caption(f"Range: {low} to {high}")
st.sidebar.caption(f"Attempts allowed: {attempt_limit}")

# Feature: High Score tracker (Challenge 2) -- best score per difficulty,
# persisted to high_scores.json so it survives across app restarts.
high_scores = load_high_scores()
best_for_difficulty = high_scores.get(difficulty)
st.sidebar.caption(
    f"🏆 High Score ({difficulty}): "
    f"{best_for_difficulty if best_for_difficulty is not None else '—'}"
)

if "secret" not in st.session_state:
    st.session_state.secret = random.randint(low, high)

# FIX: Was initialized to 1 instead of 0, so the increment in the submit
# handler below made players lose one real guess off the top of attempt_limit.
if "attempts" not in st.session_state:
    st.session_state.attempts = 0

if "score" not in st.session_state:
    st.session_state.score = 0

if "status" not in st.session_state:
    st.session_state.status = "playing"

if "history" not in st.session_state:
    st.session_state.history = []

# Feature: Guess History summary table (Challenge 4) -- one row per valid
# guess with its outcome and hot/cold proximity, separate from `history`
# (which the Debug panel above uses and keeps raw, including invalid input).
if "guess_log" not in st.session_state:
    st.session_state.guess_log = []

st.subheader("Make a guess")

# FIX: Was hardcoded to "1 and 100" regardless of difficulty; now uses the
# actual low/high for the selected difficulty.
st.info(
    f"Guess a number between {low} and {high}. "
    f"Attempts left: {attempt_limit - st.session_state.attempts}"
)

with st.expander("Developer Debug Info"):
    st.write("Secret:", st.session_state.secret)
    st.write("Attempts:", st.session_state.attempts)
    st.write("Score:", st.session_state.score)
    st.write("Difficulty:", difficulty)
    st.write("History:", st.session_state.history)

raw_guess = st.text_input(
    "Enter your guess:",
    key=f"guess_input_{difficulty}"
)

col1, col2, col3 = st.columns(3)
with col1:
    submit = st.button("Submit Guess 🚀")
with col2:
    new_game = st.button("New Game 🔁")
with col3:
    show_hint = st.checkbox("Show hint", value=True)

# FIX: This used to only reset attempts/secret (and reseeded from a hardcoded
# random.randint(1, 100) instead of the difficulty's low/high). It never reset
# `status`, so the very next block below would immediately re-trigger the
# "already won"/"game over" screen and st.stop() the game permanently.
# (Found by tracing session_state through a rerun with AI assistance, then
# verified live: clicking New Game after a win now actually returns to play.)
if new_game:
    st.session_state.attempts = 0
    st.session_state.score = 0
    st.session_state.status = "playing"
    st.session_state.history = []
    st.session_state.guess_log = []
    st.session_state.secret = random.randint(low, high)
    st.success("New game started.")
    st.rerun()

if st.session_state.status != "playing":
    if st.session_state.status == "won":
        st.success("You already won. Start a new game to play again.")
    else:
        st.error("Game over. Start a new game to try again.")
    st.stop()

if submit:
    st.session_state.attempts += 1

    ok, guess_int, err = parse_guess(raw_guess)

    if not ok:
        st.session_state.history.append(raw_guess)
        st.error(err)
    else:
        st.session_state.history.append(guess_int)

        # FIX: This used to branch on `st.session_state.attempts % 2` and cast
        # the secret to str before comparing, which is what caused the
        # backwards hints. Now always compares guess vs. secret as ints — see
        # the FIX note in logic_utils.check_guess().
        outcome = check_guess(guess_int, st.session_state.secret)
        proximity = get_proximity_label(guess_int, st.session_state.secret, low, high)

        # Feature: color-coded hints + hot/cold proximity (Challenge 4).
        # Direction (too high/low) is color-coded red/blue; proximity is a
        # separate, purely presentational readout -- neither affects
        # check_guess()'s outcome or update_score()'s scoring.
        if show_hint:
            if outcome == "Too High":
                st.error(OUTCOME_MESSAGES[outcome])
            elif outcome == "Too Low":
                st.info(OUTCOME_MESSAGES[outcome])
            if outcome != "Win":
                st.caption(f"Proximity: {proximity}")

        st.session_state.guess_log.append(
            {
                "Attempt": st.session_state.attempts,
                "Guess": guess_int,
                "Outcome": outcome,
                "Proximity": proximity,
            }
        )

        st.session_state.score = update_score(
            current_score=st.session_state.score,
            outcome=outcome,
            attempt_number=st.session_state.attempts,
        )

        if outcome == "Win":
            st.balloons()
            st.session_state.status = "won"
            st.success(
                f"You won! The secret was {st.session_state.secret}. "
                f"Final score: {st.session_state.score}"
            )
            if save_high_score(difficulty, st.session_state.score):
                st.success(f"🏆 New high score for {difficulty}!")
        else:
            if st.session_state.attempts >= attempt_limit:
                st.session_state.status = "lost"
                st.error(
                    f"Out of attempts! "
                    f"The secret was {st.session_state.secret}. "
                    f"Score: {st.session_state.score}"
                )

# Feature: session summary table (Challenge 4) -- every valid guess this
# round, with its outcome and hot/cold proximity, newest first.
if st.session_state.guess_log:
    st.subheader("📊 This Session's Guesses")
    st.dataframe(
        list(reversed(st.session_state.guess_log)),
        hide_index=True,
        width="stretch",
    )

st.divider()
st.caption("Built by an AI that claims this code is production-ready.")
