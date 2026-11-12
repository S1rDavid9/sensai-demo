"""The Stage 1 classifier trained on the pilot (analysis/stage1.py).

It predicts one of three classes from the learner's last five answers; each
class maps to a behavioural state. "Needs support" maps to struggling: the
pilot had too few "hard" and "lost" check-ins to separate struggling from
stuck.
"""

from __future__ import annotations

from functools import cached_property
from pathlib import Path

import joblib
import numpy as np

from pilot.core.states import BehaviouralState
from pilot.core.telemetry import LearnerHistory
from pilot.labelling.base import StateLabeler

DEFAULT_MODEL = Path(__file__).resolve().parents[2] / "models" / "stage1" / "stage1_logreg.joblib"
WINDOW = 5
CLASS_TO_STATE = {
    "under_challenged": BehaviouralState.RUSHING,
    "on_task": BehaviouralState.ON_TASK,
    "needs_support": BehaviouralState.STRUGGLING,
}


class Stage1Labeler(StateLabeler):
    source = "stage1_logreg_v1_smoothed2_rules"

    def __init__(self, model_path: Path = DEFAULT_MODEL) -> None:
        self.model_path = model_path

    @cached_property
    def _bundle(self) -> dict:
        return joblib.load(self.model_path)

    def warm_up(self) -> None:
        # Loading the model also imports scikit-learn and SciPy, about two
        # seconds the first time; the stress test showed it landing on the first
        # adaptive learner's answer.
        model = self._bundle["model"]
        model.predict_proba(np.zeros((1, len(self._bundle["features"]))))

    def features(self, history: LearnerHistory) -> dict[str, float]:
        return {
            "error_rate": history.error_rate(WINDOW),
            "median_rt": history.median_response_time(WINDOW),
        }

    def probabilities(self, history: LearnerHistory) -> dict[str, float]:
        feats = self.features(history)
        x = np.array([[feats[f] for f in self._bundle["features"]]])
        model = self._bundle["model"]
        p = model.predict_proba(x)[0]
        return {self._bundle["classes"][int(c)]: float(v) for c, v in zip(model.classes_, p)}

    def label(self, history: LearnerHistory) -> BehaviouralState:
        """Average the class probabilities after this answer and the one
        before, so one answer near the decision boundary doesn't flip the
        label back and forth (demo smoothing; the report used one answer)."""
        probs = self.probabilities(history)
        if len(history.answers) > 1:
            before = self.probabilities(LearnerHistory(history.answers[:-1]))
            probs = {k: (probs[k] + before.get(k, 0.0)) / 2 for k in probs}
        # Two wrong answers in a row: the learner needs support, whatever the
        # five-answer window says (it reacts slowly after a run of right answers).
        last_two = history.answers[-2:]
        if len(last_two) == 2 and not any(a.correct for a in last_two):
            return CLASS_TO_STATE["needs_support"]
        return CLASS_TO_STATE[max(probs, key=probs.get)]
