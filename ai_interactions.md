# AI Interactions Log

> **Stretch features only.** Only fill in the sections that apply to stretch features you attempted. If you did not attempt a stretch feature, leave its section blank or delete it. This file is not required for the core project.

---

## Agent Workflow (SF8)

> Document your experience using an AI agent (e.g., Cursor Agent, Claude, Copilot) to make multi-step changes autonomously.

**What task did you give the agent?**

<!-- Describe the goal you asked the agent to accomplish -->

**What did the agent do?**

<!-- List the steps the agent took (files edited, commands run, etc.) -->

**What did you have to verify or fix manually?**

<!-- Describe anything the agent got wrong or that required human review -->

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
<!-- Paste the prompt you gave the AI -->
```

**Linting output before:**

```
<!-- Paste relevant linter warnings/errors -->
```

**Changes applied:**

<!-- Describe what you changed based on the AI's suggestions -->

---

## Model Comparison (SF11)

> Compare two AI models on the same task.

**Task given to both models:**

<!-- Describe what you asked each model to do -->

| | Model A | Model B |
|-|---------|---------|
| **Model name** | | |
| **Response summary** | | |
| **More Pythonic?** | | |
| **Clearer explanation?** | | |

**Which did you prefer and why?**

<!-- Your conclusion -->
