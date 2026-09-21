# 💭 Reflection: Game Glitch Investigator

Answer each question in 3 to 5 sentences. Be specific and honest about what actually happened while you worked. This is about your process, not trying to sound perfect.

## 1. What was broken when you started?

The first time I ran the app it looked like a normal number-guessing game (title, difficulty picker, a text input, a "Submit Guess" button, and a "Developer Debug Info" panel that conveniently reveals the secret number). But playing it a few rounds exposed several real bugs:

1. **The hint text is backwards on every single guess.** In `app.py`'s `check_guess`, when a guess overshoots the secret the outcome is correctly labeled `"Too High"`, but the message paired with it is `"📈 Go HIGHER!"` — telling the player to guess even higher. Symmetrically, `"Too Low"` is paired with `"📉 Go LOWER!"`. The direction words are just swapped relative to what the outcome means, so every single guess (not just some) gives the player advice that sends them the wrong way.
2. **On top of that, the hints lie on (roughly) every other guess for a second, unrelated reason.** Every time `st.session_state.attempts` is even, the code does `secret = str(st.session_state.secret)` before calling `check_guess(guess_int, secret)`. That makes the comparison `guess > secret` compare an `int` to a `str`, which raises a `TypeError`. `check_guess` silently catches that and falls back to comparing `str(guess) > secret` **lexicographically** instead of numerically — so even the *outcome label itself* (not just the message text) can come out wrong, e.g. a guess of `9` against secret `10` gets classified as `"Too High"` instead of `"Too Low"`. Because `attempts` starts at `1` and is incremented *before* the guess is checked, this string-comparison path actually triggers on the very first guess of every game, not just "sometimes."
3. **"New Game 🔁" doesn't actually let you play again.** After winning or losing, `st.session_state.status` gets set to `"won"` or `"lost"` and is never reset back to `"playing"` anywhere in the "New Game" button handler (it only resets `attempts` and `secret`). Since the very next check in the script is `if st.session_state.status != "playing": ... st.stop()`, clicking New Game after a win/loss just re-shows "You already won" / "Game over" and freezes the form — the game becomes permanently unplayable until you manually clear session state.
4. **You get fewer attempts than advertised.** `st.session_state.attempts` is initialized to `1` (not `0`), and is incremented at the *start* of the submit handler before the guess is scored. The sidebar says "Attempts allowed: 6" on Easy, but the game calls "Out of attempts!" after only 5 real guesses, because the counter is already one ahead of the actual number of guesses made.
5. **The stated guess range is wrong for Hard mode, and "New Game" ignores difficulty entirely.** The instructions text is hardcoded to `"Guess a number between 1 and 100"` no matter which difficulty is selected, even though Hard mode's sidebar caption says "Range: 1 to 50." Worse, the "New Game" button always calls `random.randint(1, 100)` instead of using the difficulty's actual `low`/`high`, so a "Hard" secret can be seeded well outside the range the UI told you to guess in.
6. **The debug panel gives away the answer.** The "Developer Debug Info" expander is visible in the normal player UI and prints `st.session_state.secret` in plain text — though per the assignment's own Mission step 1, this one's actually intentional scaffolding, not a bug (see section 2).

**Bug Reproduction Log**

| Input Used | Expected Behavior | Actual Behavior | Console Error / Output |
|-------|-------------------|-----------------|------------------------|
| Secret = 50, guess = `60` (a plain, non-string-cast comparison — the outcome label itself is correct here) | "Too High" outcome paired with "📉 Go LOWER!" | Outcome correctly says "Too High", but message shown is "📈 Go HIGHER!" — the advice contradicts the outcome | none |
| Secret = 10 (read from Debug panel), first guess = `9` | "Too Low" outcome, since 9 < 10 | Outcome comes back as "Too High" — wrong even before the message-text bug above is applied | None shown to the user; internally `TypeError: '>' not supported between instances of 'int' and 'str'` is raised and silently swallowed by the `except TypeError` block in `check_guess()` |
| Win a round, then click "New Game 🔁" | Board resets, status returns to "playing", new guesses are accepted | App immediately re-shows "You already won. Start a new game to play again." and the guess form is disabled via `st.stop()` — game is stuck | none |
| Difficulty = Easy (attempt_limit = 6), submit 5 incorrect guesses in a row | 6 guesses should be usable before "Out of attempts" (per sidebar: "Attempts allowed: 6") | "Out of attempts!" fires after only 5 submitted guesses | none |
| Difficulty = Hard, click "New Game 🔁" | New secret generated within 1–50 (the range shown in the sidebar for Hard) | Secret regenerated with `random.randint(1, 100)`, so it can fall outside the advertised 1–50 range | none |

---

## 2. How did you use AI as a teammate?

I used Claude Code (Anthropic's CLI coding agent) as my main collaborator for this whole project — it read the starter code, helped me identify the bugs, drafted the reflection write-up, and did the actual refactor into `logic_utils.py`.

**Bug 1 — the str/int comparison bug (correct suggestion).** When I asked it to explain the "backwards hints" glitch, it traced the root cause to `secret = str(st.session_state.secret)` running on every even-numbered attempt, which forces `check_guess` into a `TypeError`-triggered fallback that compares the guess and secret as strings instead of numbers. This suggestion was correct. I verified it myself by running `'9' > '10'` in the Python interpreter — it returns `True` (lexicographic comparison), which matches the wrong outcome the app was actually producing for a guess of 9 against a secret of 10. After the fix, I re-ran that exact case through `check_guess(9, 10)` and got the correct `"Too Low"`, and added `tests/test_game_logic.py::test_guess_too_low_regression_backwards_hint_bug` to lock it in.

**Bug 2 — the inverted hint messages (incorrect/misleading suggestion, and it was mine).** When it refactored `check_guess` out of `app.py` into `logic_utils.py`, it carried the original message text over verbatim — `"Too High"` paired with `"📈 Go HIGHER!"` and `"Too Low"` paired with `"📉 Go LOWER!"` — because the outcome *labels* were already correct and it (I) didn't separately check whether the *message text* matched the label's meaning. This was wrong: a guess that overshoots the secret ("Too High") should tell the player to go lower, not higher, and the code was doing the opposite on every guess. Nothing caught this automatically — no test asserted on the message content, and the app ran without errors either way. I only caught it by manually tracing a concrete example (`check_guess(60, 50)` → outcome `"Too High"` → message `"Go HIGHER!"`) and noticing the contradiction myself before shipping. I fixed the mapping in `logic_utils.OUTCOME_MESSAGES` and added `test_hint_messages_match_their_outcome_direction` so a future regression would actually fail a test instead of silently shipping bad advice again.

---

## 3. Debugging and testing your fixes

I called a bug "fixed" only once three things lined up: the existing `pytest` suite passed, a targeted manual check against the *exact* previously-broken input reproduced the correct output, and the app actually launched and served a page with no runtime errors after the refactor.

The most informative test wasn't even pass/fail — it was what `pytest tests/test_game_logic.py` *demanded* from `check_guess`. The stub in `logic_utils.py` had a docstring claiming it should "return (outcome, message)," but `tests/test_game_logic.py` asserts things like `check_guess(60, 50) == "Too High"`, which only makes sense if the function returns a bare string. Running the tests immediately showed that a tuple-returning implementation (which matched the docstring, and matched what `app.py` originally did) would fail every test. That told me the docstring itself was wrong/misleading, and the test file was the real contract — so I moved message text (`OUTCOME_MESSAGES`) out to its own dict instead.

Beyond the original 3 starter tests, I added 4 regression tests to `tests/test_game_logic.py`, each targeting one specific bug from the reproduction log rather than being a generic smoke test: `test_guess_too_low_regression_backwards_hint_bug` (the str/int comparison bug — `check_guess(9, 10)` must be `"Too Low"`), `test_update_score_win_awards_full_points_on_first_attempt` (`update_score(0, "Win", 1)` must be `90`, not the old buggy `70`), `test_update_score_too_high_always_costs_points` (a wrong guess must never gain points), and `test_hint_messages_match_their_outcome_direction` (added *after* I caught the inverted-message bug by hand — it asserts `"LOWER"` appears in the `"Too High"` message and `"HIGHER"` in the `"Too Low"` message, so that specific mistake can't silently reappear). Running `pytest` after each fix — 7/7 passing — combined with actually starting `streamlit run app.py` and clicking through a full round, is what let me call each bug closed.

---

## 4. What did you learn about Streamlit and state?

Imagine every click on the page — submitting a guess, checking a box, clicking "New Game" — doesn't just update one widget, it re-runs your *entire Python script from top to bottom*, like refreshing the whole page and re-executing `app.py` line by line. Normal local variables (`secret = random.randint(...)`) would get wiped and recreated fresh on every single click, which is exactly why the game would forget your secret number if it were stored as a plain variable. `st.session_state` is the one dictionary-like object that *survives* those reruns — it's the only place safe to keep the secret number, the score, and the attempt count, because everything else effectively gets thrown away and rebuilt after every interaction. Once that clicked, bugs like "New Game doesn't fully reset the game" made sense as a session-state problem specifically: the code reset `attempts` and `secret` in session state but forgot `status`, so that one stale value survived every rerun and kept the game stuck.

---

## 5. Looking ahead: your developer habits

The habit I want to keep is writing the bug reproduction log *before* touching any code — pinning down an exact input, the expected output, and the actual output turns a vague "the hints are wrong" into something I can literally paste into a test assertion later. Every regression test I added this project came directly from a row in that table, so the documentation and the test suite reinforced each other instead of being separate chores.

One thing I'd do differently: check semantic correctness, not just structural correctness, before trusting a refactor. I moved `check_guess`'s message dictionary over correctly (no import errors, no test failures) but never asked "does 'Too High' + 'Go HIGHER' actually make sense together?" until I was writing the demo walkthrough and traced through an example by hand. Next time I'll deliberately walk through 2–3 concrete example outputs for any user-facing text before calling a refactor done, not just check that it runs and the existing tests pass.

This project changed how much I trust "the tests pass" as proof of correctness on its own: the inverted hint messages ran clean through pytest and the live app the entire time, because nothing was asserting on that specific relationship — it took a human (me) actually reading the output like a player would to catch it. AI-generated (and AI-refactored) code can be internally consistent and still be wrong in a way no automated check catches unless someone thought to test for that exact thing.
