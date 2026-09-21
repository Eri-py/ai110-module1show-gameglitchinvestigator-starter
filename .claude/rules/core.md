# Core conventions

## Spec-driven development
- Non-trivial work starts with a spec file, committed before implementation:
  goal, contracts affected, task breakdown, acceptance criteria.
- Specs live in `features/<name>/spec.md`. Code changes reference which spec
  they implement.
- For this project's size (a single-session course assignment), "non-trivial"
  means a multi-step feature or refactor — a one-line bug fix doesn't need
  a spec.

## Code organization
- One file, one concern. Game logic (`get_range_for_difficulty`,
  `parse_guess`, `check_guess`, `update_score`) belongs in `logic_utils.py`;
  `app.py` should only wire up the Streamlit UI and session state, calling
  into `logic_utils.py` rather than redefining the logic inline.
- Tests live in `tests/`, mirroring the module they exercise (e.g.
  `tests/test_game_logic.py` for `logic_utils.py`).

## Comments
- One line, ideally under ~100 chars. Two lines only when truly needed.
- Explain *why*, not what the code already says. Skip if self-evident.
- No multi-line block comments restating the obvious.

## Git workflow
- Never `git push` directly to `main`. Default flow is a feature branch +
  PR, even for small/urgent fixes.
- An explicit go-ahead to push straight to `main` covers that one commit
  only — it is not standing permission for subsequent commits in the same
  session. Ask again each time.
