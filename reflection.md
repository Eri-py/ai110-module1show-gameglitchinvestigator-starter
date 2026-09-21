# 💭 Reflection: Game Glitch Investigator

Answer each question in 3 to 5 sentences. Be specific and honest about what actually happened while you worked. This is about your process, not trying to sound perfect.

## 1. What was broken when you started?

The first time I ran the app it looked like a normal number-guessing game (title, difficulty picker, a text input, a "Submit Guess" button, and a "Developer Debug Info" panel that conveniently reveals the secret number). But playing it a few rounds exposed several real bugs:

1. **The hints lie on (roughly) every other guess.** In `app.py`, every time `st.session_state.attempts` is even, the code does `secret = str(st.session_state.secret)` before calling `check_guess(guess_int, secret)`. That makes the comparison `guess > secret` compare an `int` to a `str`, which raises a `TypeError`. `check_guess` silently catches that and falls back to comparing `str(guess) > secret` **lexicographically** instead of numerically. So a guess like `9` against a secret of `10` gets told "Go HIGHER!" even though 9 is already lower than 10. Because `attempts` starts at `1` and is incremented *before* the guess is checked, this string-comparison path actually triggers on the very first guess of every game, not just "sometimes."
2. **"New Game 🔁" doesn't actually let you play again.** After winning or losing, `st.session_state.status` gets set to `"won"` or `"lost"` and is never reset back to `"playing"` anywhere in the "New Game" button handler (it only resets `attempts` and `secret`). Since the very next check in the script is `if st.session_state.status != "playing": ... st.stop()`, clicking New Game after a win/loss just re-shows "You already won" / "Game over" and freezes the form — the game becomes permanently unplayable until you manually clear session state.
3. **You get fewer attempts than advertised.** `st.session_state.attempts` is initialized to `1` (not `0`), and is incremented at the *start* of the submit handler before the guess is scored. The sidebar says "Attempts allowed: 6" on Easy, but the game calls "Out of attempts!" after only 5 real guesses, because the counter is already one ahead of the actual number of guesses made.
4. **The stated guess range is wrong for Hard mode, and "New Game" ignores difficulty entirely.** The instructions text is hardcoded to `"Guess a number between 1 and 100"` no matter which difficulty is selected, even though Hard mode's sidebar caption says "Range: 1 to 50." Worse, the "New Game" button always calls `random.randint(1, 100)` instead of using the difficulty's actual `low`/`high`, so a "Hard" secret can be seeded well outside the range the UI told you to guess in.
5. **The debug panel gives away the answer.** The "Developer Debug Info" expander is visible in the normal player UI and prints `st.session_state.secret` in plain text, so there's no need to actually guess — you can just read the answer.

**Bug Reproduction Log**

| Input Used | Expected Behavior | Actual Behavior | Console Error / Output |
|-------|-------------------|-----------------|------------------------|
| Secret = 10 (read from Debug panel), first guess = `9` | "Too Low" hint (📉 Go LOWER!), since 9 < 10 | "Too High" hint shown (📈 Go HIGHER!) — direction is backwards | None shown to the user; internally `TypeError: '>' not supported between instances of 'int' and 'str'` is raised and silently swallowed by the `except TypeError` block in `check_guess()` |
| Win a round, then click "New Game 🔁" | Board resets, status returns to "playing", new guesses are accepted | App immediately re-shows "You already won. Start a new game to play again." and the guess form is disabled via `st.stop()` — game is stuck | none |
| Difficulty = Easy (attempt_limit = 6), submit 5 incorrect guesses in a row | 6 guesses should be usable before "Out of attempts" (per sidebar: "Attempts allowed: 6") | "Out of attempts!" fires after only 5 submitted guesses | none |
| Difficulty = Hard, click "New Game 🔁" | New secret generated within 1–50 (the range shown in the sidebar for Hard) | Secret regenerated with `random.randint(1, 100)`, so it can fall outside the advertised 1–50 range | none |
| Open the "Developer Debug Info" expander during play | Secret number is hidden from the player during normal play | Expander prints `Secret: <number>` in plain text, revealing the answer | none |

---

## 2. How did you use AI as a teammate?

- Which AI tools did you use on this project (for example: ChatGPT, Gemini, Copilot)?
- Give one example of an AI suggestion that was correct (including what the AI suggested and how you verified the result).
- Give one example of an AI suggestion that was incorrect or misleading (including what the AI suggested and how you verified the result).

---

## 3. Debugging and testing your fixes

- How did you decide whether a bug was really fixed?
- Describe at least one test you ran (manual or using pytest)  
  and what it showed you about your code.
- Did AI help you design or understand any tests? How?

---

## 4. What did you learn about Streamlit and state?

- How would you explain Streamlit "reruns" and session state to a friend who has never used Streamlit?

---

## 5. Looking ahead: your developer habits

- What is one habit or strategy from this project that you want to reuse in future labs or projects?
  - This could be a testing habit, a prompting strategy, or a way you used Git.
- What is one thing you would do differently next time you work with AI on a coding task?
- In one or two sentences, describe how this project changed the way you think about AI generated code.
