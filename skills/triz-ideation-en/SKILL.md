---
name: triz-ideation-en
description: >
  A TRIZ-based ideation skill for solving stuck problems or when a non-obvious idea or new approach is needed.
  It first strips out the "safe answer" the AI always gives, then pulls solution candidates from unexpected
  directions using contradiction formulation, the Ideal Final Result (IFR), a forced sweep of the 40 inventive
  principles, and extremizing tools. Triggers: "come up with ideas", "is there a new way", "what other approaches
  are there", "I'm stuck", "not the obvious answer", "shift my thinking", "out-of-the-box", "TRIZ",
  "resolve the contradiction", and the Korean phrases "아이디어 내줘", "새로운 방법 없을까", "다른 접근 뭐가 있어",
  "막혔어", "뻔한 답 말고", "발상 전환", "트리즈로", "모순 해결". NOT targets: requirements interviews,
  implementation planning, plan review, code bug diagnosis, scheduling. Use this skill only to
  "generate new candidates for a problem where no answer comes".
---

# TRIZ Ideation

**Purpose:** Produce candidates beyond the safe answer. For principles and sources see [40 principles](reference/principles.md)
and [tools](reference/tools.md).

## Why it works this way

- The AI converges on the most plausible = most common answer. Thinking harder only circles near the same answer.
- So **replace the starting point with a procedure.** If principles are assigned by list instead of picked by the AI,
  the starting point moves to directions it normally avoids.
- Three rules: (1) write down the common answers first and discard them; (2) no realism judging during divergence;
  (3) use the principle assigned, not the one that appeals.

## Modes

| Mode | When | Sweep range | Minimum ideas |
|---|---|---|---|
| Quick (default) | everyday or light problems, little time | 2 each from 5 directions (10 total) | 15 |
| Deep | "do it properly", important decisions, long-stuck problems | all 40 | 30 |

If the user does not say, use quick. If the result is thin, ask on the last line of Next steps whether to go deeper.

## Procedure

**0. Input** — Answer entirely in the language the user wrote in, including card titles, field labels (What to do / Why it fits / Where it fails / First experiment), section headings (Next steps / Reasoning / Appendix) and principle tags, translating principle names into that language. Never mix English labels into a non-English answer.
Ask questions only when the goal is too vague to state in one sentence (at most 3: goal, constraints, what has been tried).
Otherwise do not ask: write down your assumptions and proceed. Put whatever the user has already tried on the ban list first.

**1. Redefine as a function** — State "what are we trying to achieve" in one sentence, with no solution nouns.
Ask "why?" twice to widen the goal; if the wider goal can be solved, switch to that sentence.
Write down the user's stated **constraints** (budget, people, time, things that must not change) separately. Recommendations must respect them.
Write the **cause** of why this problem occurs in one line ("Because of A, B happens"). If you do not know the cause,
say it is a guess, and add one line on how the answer would change if that guess is wrong.

**2. Obvious-answer dump** — Before using any device, write the 5–8 answers that come to mind. This is the **ban list**.
From here on, anything with the same mechanism as a ban-list item does not count as a novel idea.

**3. IFR and resources** — Write in one sentence "ideally the goal is achieved by itself, with no cost or device,"
and find 5 or more resources that already exist for free (people, time, data, waste, idle space).
Among them, always include at least one from a **nuisance, waste, or constraint** (something that is a burden now) that can be used in reverse. → [tools](reference/tools.md#ifr-and-resources)

**4. Contradiction formulation** — (a) Technical contradiction: "Improving A makes B worse." (b) Physical contradiction: "X must be P
and at the same time must not be P." For a physical contradiction, resolve it with the four separations (time, space, condition, level).
If no real contradiction is visible, write "no contradiction (plain optimization problem)" and go to 5. Do not force one.
If you wrote a contradiction, give each recommendation one line in the Reasoning section on "which side of this contradiction it resolves and how."
At least 1 of recommendations ①②③ must directly resolve one side of the contradiction. For a recommendation not connected to the contradiction,
do not force a link; instead write one line on where it came from (which resource from step 3, which extremizing tool).

**5. Forced divergence** — Apply the principles to the problem one by one over the mode's sweep range and write ideas.
- Tag each idea `[principle name]`. Tag only an idea that **actually started** from that principle's prompt question.
  Thinking of the idea first and then attaching a fitting principle is forbidden.
  If it is a stretch, leave `SKIP(reason)` and move on. 2–3 SKIPs in a sweep is normal.
- Write absurd ideas too. Deleting an idea for being "unrealistic" is forbidden at this stage.
- After the sweep, use **at least 2** extremizing tools: size/time/cost 0/∞, 9 windows, doing it backwards,
  far-field analogy, flipping obvious assumptions, starting with no resources. → [tools](reference/tools.md#extremizing-tools)
- Variants of the same mechanism count as 1. Do not count SKIPs or variants to reach the number. Keep only the titles of the divergent list in the appendix.

**6. Bridging** — From the 3 most absurd ideas, pull out **the core mechanism in one line**, and build a
realistic version that keeps only that.

**7. Convergence** — Score each candidate 1–5 on novelty (distance from the safe answer), doability (can it start tomorrow within the constraints),
and effect (does it really solve the problem), then fill the recommendations like this:
- **① An idea to start tomorrow** — the idea with the highest doability and effect. Even better if it can start as a small step, such as one setting
  or one line of wording. It may be a sharpened version of a common answer, but it must actually solve the problem the user stated.
- **②③ New ideas** — ideas whose **operating mechanism** differs from the safe-answer list and that can actually work.
- **Wildcard** — the strangest idea. State that it is risky and attach a cheap experiment.
- **Operating mechanism = "what removes the problem."** If only position, shape, strength, count, or name differs, it is the same mechanism.
  For ②③ and the wildcard, silently write for each candidate "closest common answer: ○○ / what differs in mechanism: □□";
  if you cannot write □□, treat it as a variant and move it down to ① or to a supporting idea.
- Attach to each idea **one condition where it fails** and **one first experiment**. The experiment states who tries it, for how long, and what
  number means continue. For ideas that need development, start with a hand-made version (paper mockup, manual sending).
- Novelty 4 or higher goes to at most half of the candidates, and a 5 to fewer than one.

## Output format (in this order, conclusion first)

The only visible headings are the card titles and "Next steps", "Reasoning" and "Appendix". Never write internal labels anywhere, such as "One-line conclusion", "Recommendation slots",
the mode name, the number of principles, or "closest common answer / what differs in mechanism".

1. **Conclusion** — "Start with ○○ first. The reason is △△." Write one bold sentence on the very first line with no label or heading.
   Do not list assumptions at length; put them in one line in section 4.
2. **Four recommendation cards (①, ②, ③, wildcard)** — each card in the format below (within 6 lines). Card titles are a number and a name like "① Idea name";
   the wildcard is "Wildcard: idea name". Do not use TRIZ terms or principle names. The reader must be able to decide and act from this section alone. Follow the **plain-language rules** under "Writing in plain language" below.
   Provide the field labels and the three section headings in the user's language: translate "What to do", "Why it fits", "Where it fails", "First experiment", "Next steps", "Reasoning" and "Appendix".
   ```
   ### ① Idea name (one line)
   - What to do: one or two sentences, who does what and how
   - Why it fits: how it respects the constraint I stated (○○) + how it differs from the common answer "□□" (one sentence)
   - Where it fails: the weakest assumption this idea rests on
   - First experiment: who, for how long → what number means continue
   ```
3. **Next steps** — within 3 lines. If the cause of the problem is still unknown, the first line is "check as cheaply as possible whether the cause matches my guess."
4. **Reasoning (short)** — within 8 lines in total: the problem redefinition, the contradiction pair, the user's constraint list, and for each recommendation one line on how it resolved the contradiction or where it came from (resource or tool).
5. **Appendix (within 12 lines)** — the safe-answer list and the titles of divergent ideas (`[principle name] idea`). Use technical terms only here,
   and explain each in parentheses the first time it appears. Do not use arrows or symbols; write sentences.

**Length:** no more than about 1,000 words in quick mode, about 1,800 words in deep mode. If over, cut the appendix first. Sections 1–3 are at least 70% of the text.
Quality is the clarity of sections 1–2, not length.

## Writing in plain language

The result must make sense to a colleague who does not know the field. Sections 1–3 (conclusion, recommendations, next steps) most of all.

- Keep sentences short (about 20 words or fewer), one idea per sentence.
- Choose everyday words over jargon, abbreviations and industry terms. A term the user used first can stay, but explain any other
  technical term in one line the first time it appears.
- Avoid abstract, stiff phrasing ("leverage to facilitate"); say who does what with a subject and a verb.
- Cut arrows (→), slashes, nested parentheses and numbered lists. Split into two or three short sentences if needed.
- Write numeric criteria so they can be pictured at once (how many out of how many people, for how many days, how many times out of how many).
- Write the conclusion sentence so that "what to do" is visible first.

## Do not

- Do not fill contradiction matrix (39×39) cells from memory. Filling them without a source is fabrication. This skill uses the principle sweep.
- Do not pretend a principle fits. If it does not fit, SKIP.
- Do not produce output that leaves the user unable to decide (long with no conclusion). The conclusion comes first.
- Assume the user does not know TRIZ. Terms like IFR, contradiction, separation, 9 windows and principle numbers appear only in section 4 and below (Reasoning, Appendix),
  with a one-line explanation in parentheses the first time. Never in sections 1–3 (conclusion, recommendations, next steps).
