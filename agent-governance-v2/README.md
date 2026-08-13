# agent-governance-v2 — BottleSumo 治理引擎运行时

> 打捞重建 (2026-08-13)。原 agent-governance-v2 (commit 72bb513/1001c11) 丢失，
> 依据 S63/S64/S65/S66 S.A.M.U.E.L. 报告 + `dashboard/backend/governance_engine.py` 门面 API 精确重建。
> 现 vendor 进 `bottlesumo-pi-clone` 作为治理中心运行时，与 Dashboard 深度融合成单一产品。

## 架构

```
agent-governance-v2/
  src/
    policy.py             Rule / PolicyEngine (规则引擎基础)
    protocol_gateway.py   Protocol / load_protocols / compile_protocol_rules / ProtocolGateway
    verification.py       VerificationResult / BaselineDeclarationValidator
    vce_scanner.py        VCE 2.0 扫描 (冲突/盲点/极化)
    mce_introspection.py  MCE 2.0 AST 自省
  config/
    protocols/            3 个治理协议 (11-col-v1: feynman_test / entropy_denoise / logic_chain_check)
    protocol_policies.generated.yaml
    mce_introspection.generated.json
    verification_channel.generated.json
  examples/
    honesty_permanent.yaml  13-col-v2 演进样例 (schema 已兼容, 但非默认协议集)
  scripts/compile_protocol_policies.py
  tests/                  pytest/unittest
```

## 核心机制

- **协议 → 3 规则** (fail-closed): 每协议编译出 ethics(DENY,5) / enforce(ESCALATE,15/20) / ok(ALLOW_WITH_WARNING,25/30)，按 priority 升序裁决。
- **零影响**: 请求体无 `$.governance.protocols.*` 声明时，规则不命中 → ALLOW。
- **声明验证 (S66)**: `BaselineDeclarationValidator` 做一致性检查 —— 裸 `{"satisfied":true}` (无 output/evidence/triggered 锚点) 与 `violation+satisfied` (矛盾) 均验证失败 → 降级 ESCALATE。
- **VCE 扫描 (S65)**: Polarization_Index / RuleConflicts / RuleBlindSpots；`declaration_only` 盲点在验证通道启用时被缓解 (可审计)。
- **MCE 自省 (S64)**: 每规则回答 why_exists / what_it_governs。

## 使用

```python
from src.protocol_gateway import ProtocolGateway
gw = ProtocolGateway(protocols_dir="config/protocols")
res = gw.evaluate_verified("/api/audit", "POST", body)  # {action, rule, channel, verification}
report = gw.scan()                                       # VCE 扫描
mce = gw.introspect()                                    # MCE 自省
```

## 测试

```bash
python -m pytest tests/ -v     # 或 python -m unittest discover tests -v
```
