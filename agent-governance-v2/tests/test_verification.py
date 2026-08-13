"""test_verification — BaselineDeclarationValidator 单测 (S66 契约)."""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from src.verification import (  # noqa: E402
    BaselineDeclarationValidator, NoopValidator, VerificationResult,
)


class _R:
    def __init__(self, name):
        self.name = name


class TestBaseline(unittest.TestCase):
    def setUp(self):
        self.v = BaselineDeclarationValidator()
        self.ok_rule = _R("protocol-feynman_test-ok")

    def _body(self, **state):
        return {"governance": {"protocols": {"feynman_test": state}}}

    def test_noop(self):
        self.assertTrue(NoopValidator().verify(self.ok_rule, {}).verified)

    def test_anchored_consistent(self):
        r = self.v.verify(self.ok_rule, self._body(triggered=True, satisfied=True))
        self.assertTrue(r.verified)

    def test_bare_satisfied_fails(self):
        r = self.v.verify(self.ok_rule, self._body(satisfied=True))
        self.assertFalse(r.verified)
        self.assertIn("unanchored", r.reason)

    def test_contradiction_fails(self):
        r = self.v.verify(self.ok_rule, self._body(triggered=True, satisfied=True, violation="x"))
        self.assertFalse(r.verified)
        self.assertIn("contradictory", r.reason)

    def test_result_dict(self):
        r = self.v.verify(self.ok_rule, self._body(satisfied=True))
        d = r.to_dict()
        self.assertEqual(set(d), {"verified", "reason", "confidence"})


if __name__ == "__main__":
    unittest.main(verbosity=2)
