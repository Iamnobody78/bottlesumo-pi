"""agent-governance-v2 — BottleSumo 治理引擎运行时 (打捞重建 2026-08-13).

来源: S63/S64/S65/S66 S.A.M.U.E.L. 报告 + protocol_gateway_compilation 模式 +
      dashboard/backend/governance_engine.py 门面 API 契约。

子模块:
  - policy             Rule / PolicyEngine (规则引擎基础)
  - verification       VerificationResult / BaselineDeclarationValidator
  - protocol_gateway   Protocol / load_protocols / compile_protocol_rules / ProtocolGateway
  - vce_scanner        VCE 2.0 扫描 (冲突/盲点/极化)
  - mce_introspection  MCE 2.0 AST 自省
"""

__version__ = "2.0.0-rebuild"
