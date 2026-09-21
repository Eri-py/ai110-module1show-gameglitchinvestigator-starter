@.claude/rules/core.md

# Game Glitch Investigator

A single-page Streamlit number-guessing game used as a course assignment
(AI110, Module 1). It shipped intentionally buggy; the core assignment
(play it, diagnose the bugs, fix them, document the process) is done. Now
working through the optional stretch challenges from the course README.

## Shape
Solo assignment, single Python module. `app.py` wires up the Streamlit UI
and session state; pure game-logic functions (`get_range_for_difficulty`,
`parse_guess`, `check_guess`, `update_score`, and the high-score
persistence helpers `load_high_scores`/`save_high_score`) live in
`logic_utils.py`. `tests/test_game_logic.py` exercises `logic_utils.py`
with `pytest`.

## Bugs found and fixed (see `reflection.md` § 1 for full detail)
- Inverted hint messages ("Too High" told the player to go higher, and
  vice versa) — wrong on every guess.
- A `str(secret)` cast on even-numbered attempts made `check_guess` compare
  guess vs. secret as strings instead of numbers, sometimes misclassifying
  the outcome itself.
- "New Game 🔁" never reset `st.session_state.status`, so the app got stuck
  on the win/loss screen after one round.
- `attempts` started at `1` instead of `0`, giving one fewer real guess
  than `attempt_limit` advertised.
- The guess-range prompt and "New Game" ignored the selected difficulty.
- `update_score`'s win formula double-counted the attempt, and "Too High"
  sometimes rewarded a wrong guess instead of costing points.

Each fix is marked with a `FIX:` comment at its site in `app.py`/`logic_utils.py`.

## Tooling
- No package manager is mandated — `pyproject.toml` is the single source of
  truth for dependencies. `pip install -e .` (plus `pip install pytest ruff`
  for the dev dependencies) works; so does any other pyproject-aware tool.
- Run the app: `streamlit run app.py`. Run tests: `pytest`.
- Lint: `ruff check .` (config in `pyproject.toml` under `[tool.ruff]` —
  scoped to pycodestyle E/W, pyflakes F, and isort I; line length 88).
- Python `>=3.12` (see `pyproject.toml`).

## Stretch challenges (optional, tracked in README.md § Stretch Features)
1. Edge-case tests (negative/decimal/huge guesses) — done.
2. Feature expansion: persistent high-score tracker — done.
3. Docstrings + PEP 8 linting — done.
4. Enhanced UI (color-coded hints, hot/cold, session summary) — in progress.
5. AI model comparison on one bug fix — in progress.

## Documentation
- `reflection.md` — the assignment's required write-up (bugs found, AI
  collaboration notes, testing, Streamlit/session-state understanding).
- `ai_interactions.md` — stretch-feature AI interaction log (prompts used,
  agent workflow, linting output, model comparison).
- `README.md` — assignment brief, setup instructions, and stretch feature
  write-ups.
