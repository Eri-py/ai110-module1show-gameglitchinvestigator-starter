@.claude/rules/core.md

# Game Glitch Investigator

A single-page Streamlit number-guessing game used as a course assignment
(AI110, Module 1). The app ships intentionally buggy, and the assignment is
to play it, diagnose the bugs, fix them, and document the process.

## Shape
Solo assignment, single Python module. `app.py` holds the Streamlit UI and
(currently) the game logic inline; `logic_utils.py` is the intended home for
pure game-logic functions (`get_range_for_difficulty`, `parse_guess`,
`check_guess`, `update_score`) once refactored out — see its docstrings,
which currently `raise NotImplementedError` as placeholders. `tests/`
exercises `logic_utils.py` with `pytest`.

## Known bugs (tracked in `reflection.md`)
- Hints go backwards on odd-numbered guesses: the secret is cast to `str`
  when `attempts` is even, so `check_guess` falls into a lexicographic
  string comparison instead of a numeric one.
- "New Game 🔁" never resets `st.session_state.status` back to `"playing"`,
  so the app is stuck showing "already won"/"game over" after one round.
- `attempts` starts at `1` and increments before the guess is scored, so
  players get one fewer real guess than `attempt_limit` advertises.
- The guess-range prompt is hardcoded to "1 to 100" regardless of
  difficulty, and "New Game" reseeds with `random.randint(1, 100)` instead
  of the selected difficulty's actual range.
- The "Developer Debug Info" expander prints the secret in plain text to
  the player.

Full repro table: `reflection.md` § 1.

## Tooling
- No package manager is mandated — `pyproject.toml` is the single source of
  truth for dependencies. `pip install -e .` (plus `pip install pytest` for
  the dev dependency) works; so does any other pyproject-aware tool.
- Run the app: `streamlit run app.py`. Run tests: `pytest`.
- Python `>=3.12` (see `pyproject.toml`).

## Documentation
- `reflection.md` — the assignment's required write-up (bugs found, AI
  collaboration notes, testing, Streamlit/session-state understanding).
- `ai_interactions.md` — optional stretch-feature AI interaction log.
- `README.md` — assignment brief and setup instructions from the course.
