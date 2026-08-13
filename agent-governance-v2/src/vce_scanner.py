"""vce_scanner — VCE 2.0 规则扫描器 (S65 重建, 契约对齐 + 冲突/盲点扩展)。

契约 (S65 report):
  Polarization_Index / Value_Tensions / Asymmetric_Perspectives (VCE 2.0)
  RuleConflicts (扩展): priority_collision / condition_overlap / action_ambiguity
  RuleBlindSpots (扩展): missing_rule_type / declaration_only
  declaration_only 盲点: 当验证通道启用时被缓解 (S66), 盲点消失但可审计。
"""
from typing import Any, Dict, List

from .policy import Rule

_RULE_TYPES = ("ethics", "enforce", "ok")
_PERSPECTIVES = {
    "ethics": "agent 单方面自报 violation, 无独立验证",
    "enforce": "agent 单方面自报 triggered, 无独立验证",
    "ok": "agent 单方面自报 satisfied, 无独立验证 (declaration_only 高风险)",
}


def _rule_type(rule: Rule) -> str:
    parts = rule.name.split("-")
    return parts[2] if len(parts) >= 3 else "?"


def _module_of(rule: Rule) -> str:
    parts = rule.name.split("-")
    return parts[1] if len(parts) >= 3 else rule.name


def vce_scan_rules(rules: List[Rule], verification_channel: bool = False) -> Dict[str, Any]:
    conflicts: List[Dict[str, Any]] = []
    blindspots: List[Dict[str, Any]] = []

    # --- 冲突: 同 json_path + 同 priority 但不同 action ---
    by_key: Dict[tuple, List[Rule]] = {}
    for r in rules:
        by_key.setdefault((r.json_path, r.priority), []).append(r)
    for (path, pri), rs in by_key.items():
        actions = {r.action for r in rs}
        if len(actions) > 1 and path:
            conflicts.append({
                "rule": rs[0].name, "type": "priority_collision",
                "detail": f"json_path={path} priority={pri} actions={sorted(actions)}",
            })

    # --- 冲突: 同 module 同 rule_type 重复 ---
    seen_types: Dict[str, str] = {}
    for r in rules:
        t = _rule_type(r)
        if t in _RULE_TYPES:
            key = (_module_of(r), t)
            if key in seen_types and seen_types[key] != r.name:
                conflicts.append({
                    "rule": r.name, "type": "condition_overlap",
                    "detail": f"duplicate rule_type {t} for module {key[0]}",
                })
            seen_types[key] = r.name

    # --- 盲点: 模块缺失规则类型 (3 类应齐备) ---
    module_types: Dict[str, set] = {}
    for r in rules:
        t = _rule_type(r)
        if t in _RULE_TYPES:
            module_types.setdefault(_module_of(r), set()).add(t)
    for m, ts in module_types.items():
        for t in _RULE_TYPES:
            if t not in ts:
                blindspots.append({
                    "rule": f"protocol-{m}-{t}", "type": "missing_rule_type",
                    "detail": f"module {m} missing {t} rule",
                })

    # --- 盲点: declaration_only (json_path 指向治理声明区) ---
    # 验证通道启用 → 被缓解 (S66), 不报盲点但记录于 Verification_Channel
    if not verification_channel:
        for r in rules:
            if r.json_path.startswith("$.governance.protocols"):
                blindspots.append({
                    "rule": r.name, "type": "declaration_only",
                    "detail": f"matching depends on agent self-declaration ({r.action})",
                })

    # --- 张力: 规则类型两两 (伦理/执行/放行) ---
    tensions: List[Dict[str, str]] = []
    for a, b in (("ethics", "ok"), ("ethics", "enforce"), ("enforce", "ok")):
        tensions.append({"pair": f"{a}↔{b}", "tension": "单方面声明相互制约"})

    # --- 极化指数 (0-1): action 多样性 + priority 差距 ---
    actions = [r.action for r in rules]
    diversity = len(set(actions)) / max(len(actions), 1)
    priorities = [r.priority for r in rules]
    gap = (max(priorities) - min(priorities)) / 30.0 if priorities else 0.0
    polarization = round(0.5 * diversity + 0.5 * gap, 3)

    return {
        "Polarization_Index": polarization,
        "Value_Tensions": tensions,
        "Asymmetric_Perspectives": dict(_PERSPECTIVES),
        "RuleConflicts": conflicts,
        "RuleBlindSpots": blindspots,
    }
