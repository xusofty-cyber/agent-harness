#!/usr/bin/env python3
"""Unit tests for eval/evaluate.py (merged from v3-yunyi, verdict rule
adapted to the skeleton's eval/rubric.md: Accept = total >= 9 and no 0).

Run: python3 tests/eval_test.py
"""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "eval"))
import evaluate  # noqa: E402


def card(verdict, scores):
    return {"task": "t", "verdict": verdict,
            "scores": {d: {"score": s, "evidence": f"evidence for {d}"}
                       for d, s in scores.items()}}


class EvalTests(unittest.TestCase):
    def test_verdict_is_computed(self):
        def scores_with(ones=(), zero=None):
            scores = {d: {"score": 2} for d in evaluate.DIMS}
            for d in ones:
                scores[d] = {"score": 1}
            if zero:
                scores[zero] = {"score": 0}
            return scores

        # All 2s: total 12 -> Accept.
        self.assertEqual(evaluate.computed_verdict(scores_with()), "Accept")
        # All 1s: total 6 -> Revise.
        self.assertEqual(evaluate.computed_verdict(
            scores_with(ones=evaluate.DIMS)), "Revise")
        # Three 1s: total 9, no 0 -> Accept (boundary).
        self.assertEqual(evaluate.computed_verdict(
            scores_with(ones=("correctness", "verification", "reliability"))),
            "Accept")
        # Four 1s: total 8, no 0 -> Revise (boundary).
        self.assertEqual(evaluate.computed_verdict(
            scores_with(ones=("correctness", "verification", "reliability",
                              "maintainability"))), "Revise")
        # Any 0 -> Block, however high the rest is.
        self.assertEqual(evaluate.computed_verdict(
            scores_with(zero="correctness")), "Block")

    def test_handpicked_verdict_is_invalid(self):
        scores = {d: 2 for d in evaluate.DIMS}
        problems = evaluate.validate(card("Revise", scores))
        self.assertTrue(any("does not match computed" in p for p in problems))

    def test_score_without_evidence_is_invalid(self):
        scores = {d: 2 for d in evaluate.DIMS}
        c = card("Accept", scores)
        c["scores"]["correctness"]["evidence"] = ""
        self.assertTrue(any("evidence" in p for p in evaluate.validate(c)))

    def test_status_is_advisory_only_and_gate_refuses(self):
        # D28, user final ruling 2026-10-29: standing advisory-only
        # (was provisional). Gate behavior is unchanged: still refuses.
        status = json.loads(
            (ROOT / "eval" / "rubric-status.json").read_text(encoding="utf-8"))
        self.assertEqual(status["status"], "advisory-only")
        self.assertFalse(status["auto_approve_allowed"])
        self.assertGreaterEqual(status["rounds_completed"], 5)
        with tempfile.TemporaryDirectory() as d:
            card_path = Path(d) / "card.json"
            card_path.write_text(json.dumps(card(
                "Accept", {dim: 2 for dim in evaluate.DIMS})))
            proc = subprocess.run(
                [sys.executable, str(ROOT / "eval" / "evaluate.py"),
                 "--gate", str(card_path)],
                capture_output=True, text=True, cwd=ROOT)
            self.assertEqual(proc.returncode, 2, proc.stdout + proc.stderr)
            self.assertIn("GATE REFUSED", proc.stderr)

    def test_valid_accept_card_passes_check(self):
        with tempfile.TemporaryDirectory() as d:
            card_path = Path(d) / "card.json"
            card_path.write_text(json.dumps(card(
                "Accept", {dim: 2 for dim in evaluate.DIMS})))
            proc = subprocess.run(
                [sys.executable, str(ROOT / "eval" / "evaluate.py"),
                 "check", str(card_path)],
                capture_output=True, text=True, cwd=ROOT)
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            self.assertIn("scorecard valid", proc.stdout)


if __name__ == "__main__":
    unittest.main()
