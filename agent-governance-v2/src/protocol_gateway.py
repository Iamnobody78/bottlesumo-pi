"""protocol_gateway — ProtocolGateway 网关运行时 (S63/S66 重建).

契约 (S63 report + protocol_gateway_compilation + 门面):
  - Protocol.from_yaml: fail-closed (schema_version 11-col-v1 / 13-col-v2 + 12 必填字段 + level 校验)
  - load_protocols: fail-closed (缺失/重名 → RuntimeError)
  - compile_protocol_rules: 1 协议 → 3 规则 (ethics DENY / enforce ESCALATE / ok ALLOW_WITH_WARNING)
  - ProtocolGateway: evaluate / evaluate_verified (validator + audit_sink) / scan (VCE) / introspect (MCE)

编译逻辑 (每协议 3 规则, priority 升序 = DENY < enforce < ok):
  ethics   json_path=$.governance.protocols.{m}.violation  pattern=.+         DENY(5)
  enforce  json_path=$.governance.protocols.{m}  pattern=triggered&!satisfied ESCALATE(15/20)
  ok       json_path=$.governance.protocols.{m}  pattern=satisfied            ALLOW_WITH_WARNING(25/30)
"""
import json
import os
from typing import Any, Callable, Dict, List, Optional

from .policy import Rule, PolicyEngine
from .verification import BaselineDeclarationValidator, NoopValidator
from .vce_scanner import vce_scan_rules
from .mce_introspection import build_mce_introspection

SCHEMA_VERSIONS = ("11-col-v1", "13-col-v2")
REQUIRED_FIELDS = (
    "module", "category", "level", "core_purpose", "metacognitive_q",
    "collab_directive", "trigger", "ethics_boundary", "source",
    "frequency", "strategy", "expected_output",
)
VALID_LEVELS = ("L0", "L1", "L2", "L3", "L4", "L5")


class ProtocolError(RuntimeError):
    """fail-closed: 协议非法时抛出, 调用方必须中断而非降级。"""


class Protocol:
    """单个治理协议 (从 YAML dict 解析, fail-closed)。"""

    def __init__(self, module: str, level: str, source: str, core_purpose: str,
                 ethics_boundary: str, **rest):
        self.module = module
        self.level = level
        self.source = source
        self.core_purpose = core_purpose
        self.ethics_boundary = ethics_boundary
        self.extra = rest

    @classmethod
    def from_yaml(cls, data: Dict[str, Any]) -> "Protocol":
        if not isinstance(data, dict):
            raise ProtocolError("protocol root must be a mapping")
        sv = data.get("schema_version")
        if sv not in SCHEMA_VERSIONS:
            raise ProtocolError(
                f"unsupported schema_version {sv!r} (need {SCHEMA_VERSIONS})")
        proto = data.get("protocol")
        if not isinstance(proto, dict):
            raise ProtocolError("'protocol' block missing or not a mapping")
        missing = [f for f in REQUIRED_FIELDS if f not in proto]
        if missing:
            raise ProtocolError(f"missing required fields: {missing}")
        module = str(proto["module"]).strip()
        if not module:
            raise ProtocolError("'module' must be non-empty")
        level = str(proto["level"]).strip()
        if not any(lv in level for lv in VALID_LEVELS):
            raise ProtocolError(f"invalid level {level!r} (need {VALID_LEVELS})")
        return cls(
            module=module, level=level,
            source=str(proto.get("source", "")).strip(),
            core_purpose=str(proto.get("core_purpose", "")).strip(),
            ethics_boundary=str(proto.get("ethics_boundary", "")).strip(),
            **{k: v for k, v in proto.items() if k not in REQUIRED_FIELDS},
        )


def load_protocols(protocols_dir: str) -> List[Protocol]:
    """fail-closed: 目录缺失 / 无 YAML / 模块重名 → 抛错。"""
    import yaml  # 延迟导入, 保持模块可被门面仅 import 时不强依赖
    if not os.path.isdir(protocols_dir):
        raise ProtocolError(f"protocols dir not found: {protocols_dir}")
    protocols: List[Protocol] = []
    seen: Dict[str, str] = {}
    for fn in sorted(os.listdir(protocols_dir)):
        if not fn.endswith((".yaml", ".yml")):
            continue
        fp = os.path.join(protocols_dir, fn)
        with open(fp, "r", encoding="utf-8") as fh:
            data = yaml.safe_load(fh)
        p = Protocol.from_yaml(data)
        if p.module in seen:
            raise ProtocolError(
                f"duplicate module {p.module!r} in {seen[p.module]} and {fn}")
        seen[p.module] = fn
        protocols.append(p)
    if not protocols:
        raise ProtocolError(f"no protocol YAML found in {protocols_dir}")
    return protocols


def _enforce_priority(level: str) -> int:
    return 15 if "L3" in level else 20


def _ok_priority(level: str) -> int:
    return 25 if "L3" in level else 30


def compile_protocol_rules(protocols: List[Protocol]) -> List[Rule]:
    """1 协议 → 3 规则 (ethics/enforce/ok)。"""
    rules: List[Rule] = []
    for p in protocols:
        m = p.module
        state_path = f"$.governance.protocols.{m}"
        rules.append(Rule(
            name=f"protocol-{m}-ethics",
            action="DENY", priority=5,
            json_path=f"{state_path}.violation", json_pattern=r".+",
            origin=p.source, level=p.level,
            why_exists=p.core_purpose, what_it_governs=p.ethics_boundary,
        ))
        rules.append(Rule(
            name=f"protocol-{m}-enforce",
            action="ESCALATE", priority=_enforce_priority(p.level),
            json_path=state_path,
            json_pattern=r'(?=.*"triggered":true)(?!.*"satisfied":true)',
            origin=p.source, level=p.level,
            why_exists=p.core_purpose, what_it_governs=p.ethics_boundary,
        ))
        rules.append(Rule(
            name=f"protocol-{m}-ok",
            action="ALLOW_WITH_WARNING", priority=_ok_priority(p.level),
            json_path=state_path,
            json_pattern=r'(?=.*"satisfied":true)',
            origin=p.source, level=p.level,
            why_exists=p.core_purpose, what_it_governs=p.ethics_boundary,
        ))
    return rules


class ProtocolGateway:
    """治理网关: 独立裁决 + 声明验证 + VCE 扫描 + MCE 自省。"""

    def __init__(self, protocols_dir: str, validator=None, audit_sink=None,
                 enable_verification: bool = True):
        self.protocols = load_protocols(protocols_dir)
        self.rules = compile_protocol_rules(self.protocols)
        self._engine = PolicyEngine(self.rules)
        if validator is None:
            validator = (BaselineDeclarationValidator() if enable_verification
                         else NoopValidator())
        self.validator = validator
        self.audit_sink = audit_sink
        self._verification_enabled = not isinstance(validator, NoopValidator)

    # --- 独立裁决 ---
    def evaluate(self, path: str, method: str, body: Any) -> Optional[Rule]:
        return self._engine.evaluate(path, method, body)

    # --- 裁决 + 验证 (S66) ---
    def evaluate_verified(self, path: str, method: str, body: Any) -> Dict[str, Any]:
        rule = self.evaluate(path, method, body)
        result: Dict[str, Any] = {
            "path": path, "method": method, "rule": None,
            "action": "ALLOW", "channel": "none", "verification": {},
        }
        if rule is not None:
            result["rule"] = rule.name
            result["action"] = rule.action
            result["channel"] = "protocol"
            if rule.action in ("ALLOW_WITH_WARNING", "ALLOW"):
                v = self.validator.verify(rule, body)
                result["verification"] = v.to_dict()
                if not v.verified:
                    result["action"] = "ESCALATE"  # 降级
                    result["channel"] = "verification"
        self._emit_audit(rule, result, body)
        return result

    def _emit_audit(self, rule: Optional[Rule], result: Dict[str, Any], body: Any):
        if self.audit_sink is None:
            return
        event = {
            "path": result["path"], "method": result["method"],
            "rule": rule.name if rule else "",
            "action": result["action"], "channel": result["channel"],
            "verification": result["verification"], "body": body or {},
        }
        self.audit_sink(event)

    # --- VCE 扫描 (S65) ---
    def scan(self) -> Dict[str, Any]:
        report = vce_scan_rules(self.rules, verification_channel=self._verification_enabled)
        report["Verification_Channel"] = {
            "enabled": self._verification_enabled,
            "type": "pluggable-validator",
            "validator": type(self.validator).__name__.lower(),
            "mitigates": ["declaration_only"] if self._verification_enabled else [],
        }
        report["conflict_count"] = len(report.get("RuleConflicts", []))
        report["blindspot_count"] = len(report.get("RuleBlindspots", []))
        return report

    # --- MCE 自省 (S64) ---
    def introspect(self) -> Dict[str, Any]:
        return build_mce_introspection(self.rules, self.protocols)
