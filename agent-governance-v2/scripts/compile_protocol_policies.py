#!/usr/bin/env python3
"""compile_protocol_policies — 协议编译管线 (S63/S64/S65/S66 产物生成).

生成 3 个产物:
  - config/protocol_policies.generated.yaml   (编译后的规则)
  - config/mce_introspection.generated.json   (MCE 自省)
  - config/verification_channel.generated.json (验证通道)
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import yaml  # noqa: E402

from src.protocol_gateway import (  # noqa: E402
    ProtocolGateway, load_protocols, compile_protocol_rules,
)
from src.vce_scanner import vce_scan_rules  # noqa: E402
from src.mce_introspection import build_mce_introspection  # noqa: E402


def main():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    cfg = os.path.join(root, "config")
    protocols_dir = os.path.join(cfg, "protocols")
    os.makedirs(cfg, exist_ok=True)

    protocols = load_protocols(protocols_dir)
    rules = compile_protocol_rules(protocols)

    # 1. 规则产物
    policies = {"schema_version": "generated", "rules": [r.to_dict() for r in rules]}
    with open(os.path.join(cfg, "protocol_policies.generated.yaml"), "w", encoding="utf-8") as fh:
        yaml.safe_dump(policies, fh, allow_unicode=True, sort_keys=False)

    # 2. MCE 自省
    mce = build_mce_introspection(rules, protocols)
    with open(os.path.join(cfg, "mce_introspection.generated.json"), "w", encoding="utf-8") as fh:
        json.dump(mce, fh, ensure_ascii=False, indent=2)

    # 3. 验证通道
    scan = vce_scan_rules(rules, verification_channel=True)
    vc = {
        "Verification_Channel": {
            "enabled": True, "type": "pluggable-validator",
            "validator": "baseline", "mitigates": ["declaration_only"],
        },
        "Polarization_Index": scan["Polarization_Index"],
        "conflict_count": len(scan["RuleConflicts"]),
        "blindspot_count": len(scan["RuleBlindSpots"]),
    }
    with open(os.path.join(cfg, "verification_channel.generated.json"), "w", encoding="utf-8") as fh:
        json.dump(vc, fh, ensure_ascii=False, indent=2)

    print(f"OK: {len(protocols)} protocols -> {len(rules)} rules")
    print(f"  polarization={scan['Polarization_Index']} "
          f"conflicts={len(scan['RuleConflicts'])} blindspots={len(scan['RuleBlindSpots'])}")
    print(f"  wrote: protocol_policies.generated.yaml / mce_introspection.generated.json "
          f"/ verification_channel.generated.json")


if __name__ == "__main__":
    main()
