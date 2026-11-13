"""Turning a scaffolding action into what the learner sees next.

`CurriculumPlanner` maps each of the eight actions to a target difficulty
and a rule for the question type, then picks the closest unseen question
from the bank. It also returns the support shown to the learner (a message,
or a hint shown straight away). Learner-facing text never names the action.
"""

from __future__ import annotations

import random
from dataclasses import dataclass

from pilot.core.tasks import MAX_LEVEL, MIN_LEVEL, Question, QuestionBank

SAME, DIFFERENT, ANY, NEW_TOPIC = "same", "different", "any", "new_topic"


@dataclass(frozen=True)
class ActionEffect:
    level_change: int
    kind_rule: str           # SAME / DIFFERENT / ANY question type as the last one
    messages: tuple[str, ...]   # one is picked at random, so learners don't see the same line every time
    badge: str               # short, child-friendly name of what SensAI is doing
    show_hint: bool = False


EFFECTS: dict[str, ActionEffect] = {
    "increase_difficulty": ActionEffect(+1, ANY, (
        "Nice work! This one is a little harder.",
        "You are doing great, so here is a slightly harder one!",
        "Ready for something trickier? Here you go!",
    ), "harder"),
    "decrease_difficulty": ActionEffect(-1, ANY, (
        "Now try one that is a bit easier.",
        "Here is a smaller step for this one.",
        "This one should feel a bit easier. You can do it!",
    ), "easier"),
    "change_task_type": ActionEffect(0, DIFFERENT, (
        "Now try a different kind of puzzle.",
        "Time for something new! A different kind of puzzle.",
        "Here is a new type of puzzle to try.",
    ), "new_type"),
    "offer_hint": ActionEffect(0, ANY, (
        "Here is a tip to help with this one.",
        "I will give you a clue for this one.",
        "We can look at this one together. Here is a hint!",
    ), "hint", show_hint=True),
    "add_encouragement": ActionEffect(0, ANY, (
        "You are working hard. Keep going, you can do this!",
        "Mistakes help us learn. Try this one!",
        "I believe in you! Take your time with this one.",
        "Every puzzle makes your brain stronger. Keep going!",
    ), "encourage"),
    "introduce_challenge": ActionEffect(+1, DIFFERENT, (
        "Challenge time! Can you crack this one?",
        "Here is a challenge puzzle, just for you!",
        "You are on a roll. Try this challenge!",
    ), "challenge"),
    "repeat_simplified": ActionEffect(-1, SAME, (
        "Now try a simpler one like the last.",
        "Here is a similar one, a little simpler.",
        "Practise that kind again, a bit easier this time.",
    ), "simpler"),
    "advance_topic": ActionEffect(+1, NEW_TOPIC, (
        "Great, now we move on to something new.",
        "You have got that! Now try a new topic.",
        "Well done! On to the next kind of puzzle.",
    ), "new_topic"),
}

# When the bank can't move the difficulty the way the action intended (easier
# at level 1, harder at level 5), say what actually happens instead.
AT_EASIEST = (
    "Practise another one like that. Take your time.",
    "We can do another one at this level together.",
    "Here is another one to practise. You can do it!",
    "Practice makes us stronger. Try this one!",
    "Keep practising at this level. Nice and steady.",
)
AT_HARDEST = (
    "You are at the top level! Here is another tough one.",
    "These are the hardest puzzles, and you are doing them! Try this one.",
    "Top level again. Can you crack this one too?",
    "Wow, still at the top! Here is another hard one.",
    "You are a puzzle master! One more tough one.",
)


@dataclass(frozen=True)
class NextStep:
    question: Question
    message: str
    hint: str | None          # shown straight away when the action was offer_hint
    badge: str = ""


class CurriculumPlanner:
    def __init__(self, bank: QuestionBank) -> None:
        self.bank = bank

    def first_question(self) -> Question:
        return self.bank.pilot_form()[0]

    def next_step(self, action: str, last: Question, seen: set[str], seed: int) -> NextStep:
        effect = EFFECTS[action]
        rng = random.Random(seed)
        target = min(MAX_LEVEL, max(MIN_LEVEL, last.difficulty + effect.level_change))
        question = self._pick(target, effect.kind_rule, last, seen, rng)
        message, badge = self._message(effect, last, question, rng)
        return NextStep(question, message, question.hint if effect.show_hint else None, badge)

    @staticmethod
    def _message(effect: ActionEffect, last: Question, question: Question, rng: random.Random) -> tuple[str, str]:
        """The action's message and badge, unless the bank couldn't move the
        difficulty the way the action intended (e.g. "easier" at level 1)."""
        moved = question.difficulty - last.difficulty
        if effect.level_change < 0 and moved >= 0:
            return rng.choice(AT_EASIEST), "practise"
        if effect.level_change > 0 and moved <= 0:
            return rng.choice(AT_HARDEST), "top_level"
        if effect.kind_rule == NEW_TOPIC and question.domain == last.domain:
            return rng.choice(EFFECTS["increase_difficulty"].messages), "harder"
        return rng.choice(effect.messages), effect.badge

    def _pick(self, target: int, kind_rule: str, last: Question, seen: set[str], rng: random.Random) -> Question:
        """Closest level first (target, then ±1, ±2 …); within a level, prefer
        the requested type; never repeat a question while unseen ones remain."""
        for distance in range(MAX_LEVEL):
            levels = [target] if distance == 0 else [target - distance, target + distance]
            for level in levels:
                if not MIN_LEVEL <= level <= MAX_LEVEL:
                    continue
                pool = [q for q in self.bank.at_level(level) if q.id not in seen]
                if not pool:
                    continue
                preferred = [q for q in pool if self._kind_ok(q, kind_rule, last)]
                return rng.choice(preferred or pool)
        return rng.choice([q for q in self.bank.questions if q.id != last.id])

    @staticmethod
    def _kind_ok(q: Question, kind_rule: str, last: Question) -> bool:
        if kind_rule == SAME:
            return q.kind == last.kind
        if kind_rule == DIFFERENT:
            return q.kind != last.kind
        if kind_rule == NEW_TOPIC:   # arithmetic <-> patterns, not just another kind of sum
            return q.domain != last.domain
        return True
