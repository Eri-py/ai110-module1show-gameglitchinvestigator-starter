# AI Interactions Log

> **Stretch features only.** Only fill in the sections that apply to stretch features you attempted. If you did not attempt a stretch feature, leave its section blank or delete it. This file is not required for the core project.

---

## Agent Workflow (SF8)

> Document your experience using an AI agent (e.g., Cursor Agent, Claude, Copilot) to make multi-step changes autonomously.

**What task did you give the agent?** "Implement a High Score tracker: best score per difficulty, saved to a local file so it survives app restarts, shown in the sidebar, and celebrated when beaten. Keep persistence logic out of `app.py` -- it should just call into `logic_utils.py`."

**What did the agent do?**
- Added `HIGH_SCORE_FILE`, `load_high_scores()`, and `save_high_score()` to `logic_utils.py` -- JSON read/write, with a missing or corrupt file treated as "no scores yet" instead of raising.
- Modified `app.py`: imported the two new functions, added a sidebar caption showing the current difficulty's best score, and called `save_high_score()` right after the existing win-handling code, showing an extra `st.success("🏆 New high score!")` only when it returns `True`.
- Added three new tests (`tests/test_game_logic.py`) using pytest's `tmp_path` fixture to test file creation, that a lower score doesn't overwrite a higher one, and that a missing file returns an empty dict rather than crashing.
- Added `high_scores.json` to `.gitignore` (it's per-player runtime data, not something that belongs in version control) and re-ran the full suite + a live `streamlit run` smoke test to confirm nothing broke.

**What did you have to verify or fix manually?** Being honest: this one didn't need a correction cycle, but I did double-check one specific design choice rather than accept it blindly -- the agent gave `load_high_scores`/`save_high_score` an optional `file_path` parameter (defaulting to the real save file) instead of hardcoding the path. That's what let the three new tests write to a throwaway pytest `tmp_path` file instead of the real `high_scores.json`, so running the test suite repeatedly can't pollute (or, worse, accidentally commit) real save data. I verified this by running the full suite and then checking the project directory for a stray `high_scores.json` afterward -- there wasn't one. I also manually started the live app (`streamlit run app.py`) rather than trusting "the tests pass" alone, since the sidebar caption and the win-time save call are both Streamlit UI code that no pytest test touches.

---

## Test Generation (SF7)

> Document how you used AI to help generate or improve tests.

**Prompt used:** "Identify three edge-case inputs to `parse_guess`/`check_guess` that might still break the game (think negative numbers, decimals, extremely large values), then write pytest cases in `tests/test_game_logic.py` that verify each is handled gracefully."

| Edge Case | Prompt Used | AI-Suggested Test | Did It Pass? | Your Reasoning |
|-----------|-------------|-------------------|--------------|----------------|
| Negative guess (`"-5"`) | (above) | `test_negative_number_guess_is_handled_gracefully` — asserts `parse_guess("-5")` returns `(True, -5, None)` and `check_guess(-5, 50) == "Too Low"` | Yes | Nothing in `parse_guess`/`check_guess` special-cases sign, and the game never validates the guess is within `[low, high]` before scoring it — worth locking in that a negative guess is scored normally instead of crashing or silently being dropped. |
| Decimal guess (`"50.9"`) | (above) | `test_decimal_guess_truncates_toward_zero` — asserts `parse_guess("50.9")` returns `(True, 50, None)` | Yes | `parse_guess` does `int(float(raw))` when a `.` is present, which **truncates** rather than rounds. `50.9` becoming `50` (not `51`) is surprising enough to a player that it's worth a test documenting the actual behavior, not just assuming it "just works." |
| Extremely large guess (30-digit number) | (above) | `test_extremely_large_guess_does_not_crash` — asserts a 30-digit guess parses to the correct (huge) int and still compares correctly via `check_guess` | Yes | Python ints are arbitrary-precision, so this can't overflow the way it might in a fixed-width-int language — but it's still worth verifying the game doesn't choke on a guess many orders of magnitude outside any real secret, since nothing caps input length before `int()` is called. |

---

## Linting & Style (SF9)

> Document your use of AI for linting or code style improvements.

**Prompt used:**

```
Add professional-grade docstrings (Args/Returns) to every function in
logic_utils.py, then check the whole project for PEP 8 compliance with
ruff (pycodestyle E/W, pyflakes F, isort I) and fix everything it flags.
```

**Linting output before** (`ruff check --select E,W,F,I .`):

```
I001 [*] Import block is un-sorted or un-formatted
  --> app.py:1:1
   |
 1 | / import random
 2 | | import streamlit as st
 3 | |
 4 | | from logic_utils import (
   | |_^
   |
help: Organize imports

E501 Line too long (91 > 88)
   --> logic_utils.py:154:89
    |
154 | def save_high_score(difficulty: str, score: int, file_path: str = HIGH_SCORE_FILE) -> bool:
    |                                                                                         ^^^

I001 [*] Import block is un-sorted or un-formatted
  --> tests\test_game_logic.py:1:1
   |
 1 | / from logic_utils import (
   | |_^
   |
help: Organize imports

Found 3 errors.
[*] 2 fixable with the `--fix` option.
```

**Linting output after:**

```
$ ruff check .
All checks passed!
```

**Changes applied:** Ran `ruff check --fix` to auto-fix the two unsorted/unformatted import blocks (it inserted a blank line separating the stdlib `import random` from the third-party `import streamlit as st`, per isort convention). Manually wrapped `save_high_score`'s signature across two lines to get under the 88-char limit -- `ruff` flags line length but doesn't auto-wrap function signatures. Also added `ruff` as a dev dependency and a `[tool.ruff]` config block to `pyproject.toml` (scoped to `E`, `W`, `F`, `I`, line-length 88) so re-running the check later doesn't require re-typing the `--select` flags. I did *not* apply ruff's default-ruleset suggestions from an earlier unscoped run (`BLE001` "don't catch blind Exception", a pylint-style refactor suggestion for the score-clamping `if`) -- those are lint/style-opinion rules beyond plain PEP 8, and the assignment specifically asked for PEP 8 compliance, not a full pylint pass.

---

## Model Comparison (SF11)

> Compare two AI models on the same task.

Note on methodology: I don't have direct access to ChatGPT/Gemini/Copilot from inside this coding session, so per the assignment's own "e.g." wording ("Claude vs. Gemini, or ChatGPT vs. Copilot") I compared two different Claude models instead -- Sonnet 5 (used for the whole project) and Haiku 4.5 (spawned as an independent sub-agent). This is a fair comparison of the actual underlying models, not a re-run of the same one. Caveat: Haiku was given only the original buggy `check_guess` code and its caller, not the project's test file (`tests/test_game_logic.py`), so its answer wasn't optimizing for that specific contract the way Sonnet's (already-committed) fix was -- noted below where it matters.

**Task given to both models:** the exact original buggy code -- `check_guess()` (returning `(outcome, message)` tuples, with the `try/except TypeError` fallback) plus its caller (the `attempts % 2` block that casts `secret` to `str` on even attempts) -- with the prompt: "the hint is sometimes backwards; find the root cause, fix it, and explain why it happened."

| | Model A | Model B |
|-|---------|---------|
| **Model name** | Claude Sonnet 5 (this session, already applied as the project's actual fix) | Claude Haiku 4.5 (spawned as a sub-agent with only the buggy snippet, no other project context) |
| **Response summary** | Removed the `str(secret)` cast from the caller entirely (always compares as `int`), and simplified `check_guess` to return a bare outcome string (`"Win"`/`"Too High"`/`"Too Low"`) with message text split into a separate `OUTCOME_MESSAGES` dict -- required because `tests/test_game_logic.py` asserts `check_guess(60, 50) == "Too High"`, a bare string, not a tuple. | Correctly diagnosed the same root cause (lexicographic vs. numeric comparison), and offered two fixes: a primary one that keeps the original `(outcome, message)` tuple shape but adds an `isinstance(secret, str)` check with a `try/except ValueError` to coerce it back to `int` inside `check_guess` (plus a new, previously-nonexistent `"Error"` outcome for the ValueError case); and an "even better" secondary suggestion to just stop casting `secret` to `str` in the caller in the first place -- which matches what Sonnet actually did. |
| **More Pythonic?** | Sonnet's, by a clear margin. It trusts the caller's guarantee that `guess`/`secret` are always ints (true everywhere in this codebase) instead of defensively re-validating inside `check_guess` for a case that can't actually occur -- 4 lines of straight-line comparison logic, no `try/except`, no `isinstance`. | Haiku's *primary* fix adds defensive type-coercion and a speculative new `"Error"` outcome for a scenario (a non-numeric secret string) that never happens given how the secret is actually generated (`random.randint`) -- unnecessary complexity for dead code. Its *secondary* suggestion, though, is exactly as clean as Sonnet's. |
| **Clearer explanation?** | Verified claims empirically rather than just asserting them -- e.g. ran `'9' > '10'` in the interpreter to confirm the lexicographic-comparison claim, and re-ran the exact broken input through the fixed code to show the corrected output (see section 2 above). | Very clear on its own terms -- walked through concrete examples (`"5" > "50"` is `True` alphabetically vs. `5 > 50` is `False` numerically) directly in the explanation, which is an effective way to make the bug's mechanism obvious without needing a REPL. Slight edge to Haiku for packing the "aha" moment directly into prose. |

**Which did you prefer and why?** Sonnet's actual fix, mainly because it happens to match the project's real constraints (the bare-string test contract) that Haiku wasn't given -- an advantage of context, not raw capability. On the code-quality question alone, judging each model's *best* answer (Haiku's secondary suggestion, since it's the one worth adopting), the two models converged on the identical minimal fix: stop mutating `secret`'s type in the caller and keep `check_guess` a pure numeric comparison. That convergence is itself the most interesting result -- both models correctly identified that removing the buggy cast at its source beats patching around it with more type-checking inside the callee, but only Sonnet's answer was actually validated end-to-end against this repo's test suite and live app rather than reasoned about in isolation.
