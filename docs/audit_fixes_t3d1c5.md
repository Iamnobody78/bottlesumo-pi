# T3/D1/C5 验证证据（2026-08-19）

## 审计缺陷处置记录

| 缺陷 | 审计描述 | 处置 | 证据 |
|------|---------|------|------|
| **T3** | agent-governance-v2 无测试覆盖率门禁 | 已实现 | ci.yml line 56: `--cov-fail-under=90`；本地实测 **54 passed, coverage 94.99% ≥ 90%**（2026-08-19 16:4x） |
| **D1** | bottlesumo-pi architecture_overview.md 404 | 已解决 | 文件存在（17,580 bytes）+ mkdocs.yml nav 68 条目含之 |
| **C5** | 架构文档与代码同提交未 CI 强制 | 部分解决 | docs/architecture.md 现引用 ARCHITECTURE.md + architecture_overview.md（commit d8d7287） |

## T3 本地实测输出（Python 3.11.15, dashboard/backend）

```
models.py                         53      0   100%
routers/auth.py                   69      8    88%
routers/governance.py             91      3    97%
seed.py                           26      3    88%
TOTAL                            979     49    95%
Required test coverage of 90% reached. Total coverage: 94.99%
54 passed, 3 warnings in 16.20s
```

## 说明
- T3 门禁在 **agent-governance-v2 的 CI**（`--cov-fail-under=90`），本地实测在 bottlesumo_pi/dashboard/backend（依赖引擎）
- C5 的"CI 强制"完整实现需 mkdocs build --strict 纳入 CI（docs.yml 已有，待验证链）
