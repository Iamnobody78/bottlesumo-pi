"""mce_introspection — MCE 2.0 AST 自省 (S64 重建).

契约 (S64 report):
  build_mce_introspection(rules, protocols) → {protocols: {module: [{rule, why_exists, what_it_governs}, ...]}}
  每规则回答: 为什么存在 (why_exists) + 治理什么 (what_it_governs)。
"""
from typing import Any, Dict, List


def build_mce_introspection(rules: List[Any], protocols: List[Any]) -> Dict[str, Any]:
    out: Dict[str, Any] = {"protocols": {}}
    for p in protocols:
        entries: List[Dict[str, str]] = []
        for r in rules:
            if r.name.startswith(f"protocol-{p.module}-"):
                entries.append({
                    "rule": r.name,
                    "why_exists": r.why_exists or p.core_purpose,
                    "what_it_governs": r.what_it_governs or p.ethics_boundary,
                })
        out["protocols"][p.module] = entries
    return out
