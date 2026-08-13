"""test_protocol_gateway — 网关运行时单测 (S63/S66 契约回归)."""
import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from src.protocol_gateway import (  # noqa: E402
    Protocol, ProtocolError, ProtocolGateway, compile_protocol_rules,
    load_protocols,
)
from src.verification import BaselineDeclarationValidator, NoopValidator  # noqa: E402


def _proto(module="feynman_test", level="L3", **kw):
    base = {
        "module": module, "category": "governance", "level": level,
        "core_purpose": "test protocol", "metacognitive_q": "q",
        "collab_directive": "d", "trigger": "t", "ethics_boundary": "e",
        "source": "s", "frequency": "f", "strategy": "st", "expected_output": "eo",
    }
    base.update(kw)
    return {"schema_version": "11-col-v1", "protocol": base}


class TestProtocolFromYaml(unittest.TestCase):
    def test_ok(self):
        p = Protocol.from_yaml(_proto())
        self.assertEqual(p.module, "feynman_test")

    def test_bad_schema_fail_closed(self):
        d = _proto(); d["schema_version"] = "9-col-old"
        with self.assertRaises(ProtocolError):
            Protocol.from_yaml(d)

    def test_missing_field_fail_closed(self):
        d = _proto(); del d["protocol"]["module"]
        with self.assertRaises(ProtocolError):
            Protocol.from_yaml(d)

    def test_invalid_level(self):
        d = _proto(level="X9")
        with self.assertRaises(ProtocolError):
            Protocol.from_yaml(d)

    def test_schema_v2_accepted(self):
        d = _proto(level="L0-L5"); d["schema_version"] = "13-col-v2"
        p = Protocol.from_yaml(d)
        self.assertIn("L0", p.level)


class TestCompile(unittest.TestCase):
    def test_three_rules(self):
        rules = compile_protocol_rules([Protocol.from_yaml(_proto())])
        self.assertEqual(len(rules), 3)
        types = {r.name.split("-")[2] for r in rules}
        self.assertEqual(types, {"ethics", "enforce", "ok"})
        # priority 升序: DENY < enforce < ok
        self.assertEqual([r.action for r in rules], ["DENY", "ESCALATE", "ALLOW_WITH_WARNING"])


class TestEvaluate(unittest.TestCase):
    def setUp(self):
        self.gw = ProtocolGateway.__new__(ProtocolGateway)  # bypass 构造, 手动注入
        from src.policy import PolicyEngine
        self.gw.protocols = [Protocol.from_yaml(_proto())]
        self.gw.rules = compile_protocol_rules(self.gw.protocols)
        self.gw._engine = PolicyEngine(self.gw.rules)
        self.gw.validator = NoopValidator()
        self.gw.audit_sink = None
        self.gw._verification_enabled = False

    def _body(self, **state):
        return {"governance": {"protocols": {"feynman_test": state}}}

    def test_zero_impact_allows(self):
        self.assertIsNone(self.gw.evaluate("/api/x", "POST", {}))

    def test_violation_deny(self):
        r = self.gw.evaluate("/api/x", "POST", self._body(violation="bad"))
        self.assertEqual(r.action, "DENY")

    def test_triggered_escalate(self):
        r = self.gw.evaluate("/api/x", "POST", self._body(triggered=True))
        self.assertEqual(r.action, "ESCALATE")

    def test_satisfied_allow(self):
        r = self.gw.evaluate("/api/x", "POST", self._body(triggered=True, satisfied=True))
        self.assertEqual(r.action, "ALLOW_WITH_WARNING")


class TestEvaluateVerified(unittest.TestCase):
    def _make(self, **body_state):
        rules = compile_protocol_rules([Protocol.from_yaml(_proto())])
        from src.policy import PolicyEngine
        gw = ProtocolGateway.__new__(ProtocolGateway)
        gw.protocols = [Protocol.from_yaml(_proto())]
        gw.rules = rules
        gw._engine = PolicyEngine(rules)
        gw.validator = BaselineDeclarationValidator()
        gw.audit_sink = None
        gw._verification_enabled = True
        return gw

    def test_bare_satisfied_escalates(self):
        gw = self._make()
        res = gw.evaluate_verified("/api/x", "POST",
                                   {"governance": {"protocols": {"feynman_test": {"satisfied": True}}}})
        self.assertEqual(res["action"], "ESCALATE")
        self.assertFalse(res["verification"]["verified"])

    def test_anchored_satisfied_stays_allow(self):
        gw = self._make()
        res = gw.evaluate_verified("/api/x", "POST",
                                   {"governance": {"protocols": {"feynman_test": {"triggered": True, "satisfied": True}}}})
        self.assertEqual(res["action"], "ALLOW_WITH_WARNING")
        self.assertTrue(res["verification"]["verified"])

    def test_contradiction_denies(self):
        # violation 存在 → ethics 规则 (priority 5 DENY) 先于 ok 规则命中, 比降级更强
        gw = self._make()
        res = gw.evaluate_verified("/api/x", "POST",
                                   {"governance": {"protocols": {"feynman_test": {"triggered": True, "satisfied": True, "violation": "x"}}}})
        self.assertEqual(res["action"], "DENY")

    def test_audit_sink_gets_event(self):
        events = []
        gw = self._make()
        gw.audit_sink = events.append
        gw.evaluate_verified("/api/x", "POST",
                             {"governance": {"protocols": {"feynman_test": {"satisfied": True}}}})
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]["path"], "/api/x")


class TestScan(unittest.TestCase):
    def _gw(self, enable_verification):
        rules = compile_protocol_rules([Protocol.from_yaml(_proto())])
        from src.policy import PolicyEngine
        gw = ProtocolGateway.__new__(ProtocolGateway)
        gw.protocols = [Protocol.from_yaml(_proto())]
        gw.rules = rules
        gw._engine = PolicyEngine(rules)
        gw.validator = BaselineDeclarationValidator() if enable_verification else NoopValidator()
        gw.audit_sink = None
        gw._verification_enabled = enable_verification
        return gw

    def test_scan_shape(self):
        rep = self._gw(True).scan()
        self.assertIn("Polarization_Index", rep)
        self.assertIn("RuleConflicts", rep)
        self.assertIn("RuleBlindSpots", rep)
        self.assertIn("conflict_count", rep)
        self.assertIn("blindspot_count", rep)
        self.assertIn("Verification_Channel", rep)

    def test_declaration_only_mitigated_by_channel(self):
        rep_on = self._gw(True).scan()
        rep_off = self._gw(False).scan()
        types_on = {b["type"] for b in rep_on["RuleBlindSpots"]}
        types_off = {b["type"] for b in rep_off["RuleBlindSpots"]}
        self.assertNotIn("declaration_only", types_on)
        self.assertIn("declaration_only", types_off)
        self.assertTrue(rep_on["Verification_Channel"]["enabled"])


class TestIntrospect(unittest.TestCase):
    def test_mce_shape(self):
        rules = compile_protocol_rules([Protocol.from_yaml(_proto())])
        mce = ProtocolGateway.__new__(ProtocolGateway).__class__  # noop
        from src.mce_introspection import build_mce_introspection
        out = build_mce_introspection(rules, [Protocol.from_yaml(_proto())])
        self.assertIn("feynman_test", out["protocols"])
        self.assertEqual(len(out["protocols"]["feynman_test"]), 3)
        self.assertEqual(set(out["protocols"]["feynman_test"][0]),
                         {"rule", "why_exists", "what_it_governs"})


if __name__ == "__main__":
    unittest.main(verbosity=2)
