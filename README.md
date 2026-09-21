# 🎮 Game Glitch Investigator: The Impossible Guesser

## 🚨 The Situation

You asked an AI to build a simple "Number Guessing Game" using Streamlit.
It wrote the code, ran away, and now the game is unplayable. 

- You can't win.
- The hints lie to you.
- The secret number seems to have commitment issues.

## 🛠️ Setup

1. Create and activate a virtual environment: `python -m venv .venv` then `.venv\Scripts\activate` (Windows) or `source .venv/bin/activate` (macOS/Linux)
2. Install dependencies: `pip install -e .` (or `pip install -e ".[dev]"` — see note below — to also get `pytest`)
3. Run the broken app: `streamlit run app.py`

> `pip install -e .` installs only the `[project.dependencies]` listed in `pyproject.toml`. `pytest` lives in `[dependency-groups].dev`, which plain `pip` doesn't read yet — for now just run `pip install pytest` separately, or use any pyproject-aware tool (`uv sync`, `pdm install`, `poetry install`, etc.) that does support dependency groups.

## 🕵️‍♂️ Your Mission

1. **Play the game.** Open the "Developer Debug Info" tab in the app to see the secret number. Try to win.
2. **Find the State Bug.** Why does the secret number change every time you click "Submit"? Ask ChatGPT: *"How do I keep a variable from resetting in Streamlit when I click a button?"*
3. **Fix the Logic.** The hints ("Higher/Lower") are wrong. Fix them.
4. **Refactor & Test.** - Move the logic into `logic_utils.py`.
   - Run `pytest` in your terminal.
   - Keep fixing until all tests pass!

## 📝 Document Your Experience

- [x] **Purpose:** A Streamlit number-guessing game — pick a difficulty, guess the secret number within a limited number of attempts, and score points based on how quickly you find it.
- [x] **Bugs found:** see `reflection.md` § 1 for the full write-up and reproduction table. In short: the "Too High"/"Too Low" hint *messages* were swapped relative to their own outcome labels (wrong on every guess), a separate string-vs-int comparison bug could additionally mislabel the outcome itself on top of that, "New Game" never reset the win/loss status so the app got permanently stuck after one round, players got one fewer attempt than the sidebar advertised (an off-by-one in the attempt counter), the guess-range prompt and "New Game" ignored the selected difficulty, and the win-score formula was off by one attempt's worth of points.
- [x] **Fixes applied:** moved `get_range_for_difficulty`, `parse_guess`, `check_guess`, and `update_score` into `logic_utils.py`; swapped the inverted `OUTCOME_MESSAGES` so "Too High" tells you to go lower and vice versa; removed the `str(secret)` cast that could mislabel the outcome, so guesses are always compared numerically; had "New Game 🔁" reset `status`, `score`, `history`, and reseed the secret from the *current* difficulty's range instead of a hardcoded 1–100; started `attempts` at `0` instead of `1` so the attempt count matches what's displayed; made the guess-range prompt use the actual `low`/`high` for the selected difficulty; and fixed `update_score`'s win formula (`100 - 10 * attempt_number`, no extra `+1`) and made "Too High" always cost points instead of occasionally rewarding a wrong guess.

## 📸 Demo Walkthrough

Describe your fixed game in numbered steps so a reader can follow along without watching a video. Sample game on Normal difficulty (range 1–100, 8 attempts), secret = 63:

1. Start the app (`streamlit run app.py`), select **Normal** difficulty. Sidebar shows "Range: 1 to 100" and "Attempts allowed: 8". Debug panel confirms the secret is `63`.
2. User enters a guess of `40` → Game returns **"Too Low"** with the hint "📈 Go HIGHER!" (direction now correct). Score: `-5`.
3. User enters a guess of `70` → **"Too High"** with the hint "📉 Go LOWER!" (previously this said "Go HIGHER!", which was backwards). Score: `-10`.
4. User enters a guess of `63` → **"Win"**. Balloons fire, score updates to `-10 + (100 - 10 × 3) = 60`, and the app shows "You won! The secret was 63. Final score: 60."
5. Any further guess is blocked with "You already won. Start a new game to play again." instead of silently accepting more input.
6. User clicks **"New Game 🔁"** → status resets to "playing", score resets to `0`, attempts reset to `0`, and a brand-new secret is drawn from the Normal range (1–100) — the game is immediately playable again instead of staying stuck on the win screen.

**Screenshot** *(optional)*: <!-- Insert a screenshot of your fixed, winning game here -->

## 🧪 Test Results

```
$ pytest
============================= test session starts =============================
platform win32 -- Python 3.12.13, pytest-9.1.1, pluggy-1.6.0
rootdir: C:\Users\eriol\Desktop\Projects\Foundations Of AI Engineering\ai110-module1show-gameglitchinvestigator-starter
configfile: pyproject.toml
collected 7 items

tests\test_game_logic.py .......                                         [100%]

============================== 7 passed in 0.01s ==============================
```

7 tests: the 3 starter tests plus 4 regression tests added while fixing bugs — one per bug fixed (backwards outcome classification, win-score off-by-one, "Too High" wrongly rewarding a bad guess, and the inverted hint-message direction).

## 🚀 Stretch Features

### Challenge 1: Advanced Edge-Case Testing

Three edge cases identified and tested (see `ai_interactions.md` for the prompts and reasoning behind each): a negative guess, a decimal guess, and an extremely large guess. All three are handled gracefully by the existing `parse_guess`/`check_guess` — no bugs found, but each is now locked in by a regression test in `tests/test_game_logic.py`.

```
$ pytest -v
============================= test session starts =============================
platform win32 -- Python 3.12.13, pytest-9.1.1, pluggy-1.6.0
rootdir: C:\Users\eriol\Desktop\Projects\Foundations Of AI Engineering\ai110-module1show-gameglitchinvestigator-starter
configfile: pyproject.toml
collected 10 items

tests/test_game_logic.py::test_winning_guess PASSED                      [ 10%]
tests/test_game_logic.py::test_guess_too_high PASSED                     [ 20%]
tests/test_game_logic.py::test_guess_too_low PASSED                      [ 30%]
tests/test_game_logic.py::test_guess_too_low_regression_backwards_hint_bug PASSED [ 40%]
tests/test_game_logic.py::test_update_score_win_awards_full_points_on_first_attempt PASSED [ 50%]
tests/test_game_logic.py::test_update_score_too_high_always_costs_points PASSED [ 60%]
tests/test_game_logic.py::test_hint_messages_match_their_outcome_direction PASSED [ 70%]
tests/test_game_logic.py::test_negative_number_guess_is_handled_gracefully PASSED [ 80%]
tests/test_game_logic.py::test_decimal_guess_truncates_toward_zero PASSED [ 90%]
tests/test_game_logic.py::test_extremely_large_guess_does_not_crash PASSED [100%]

============================= 10 passed in 0.01s ==============================
```

### Challenge 2: Feature Expansion

Added a **High Score tracker** that persists across app restarts, saved to a local `high_scores.json` (gitignored — it's per-player runtime data, not source). `logic_utils.load_high_scores()`/`save_high_score()` handle the file I/O (missing/corrupt file → empty dict, never a crash); `app.py` shows the current best score for the selected difficulty in the sidebar ("🏆 High Score (Normal): 85") and calls `save_high_score()` right after a win, showing a "🏆 New high score!" banner when the player beats their previous best for that difficulty. See `ai_interactions.md` → Agent Workflow for how this was planned and implemented.

### Challenge 3: Professional Documentation and Linting

Every function in `logic_utils.py` now has a Google-style docstring (Args/Returns, plus behavior notes like "truncates toward zero" or "missing file is treated as no scores yet"). Linted with `ruff check .` (config in `pyproject.toml`: pycodestyle `E`/`W`, pyflakes `F`, isort `I`, line length 88) — found and fixed an unsorted import block in `app.py` and `tests/test_game_logic.py`, and one line over 88 chars in `logic_utils.py`. See `ai_interactions.md` for the before/after linting output and prompts used.

### Challenge 4: Enhanced Game UI

<!-- filled in below once implemented -->

### Challenge 5: AI Model Comparison

See `ai_interactions.md` for the full comparison.
