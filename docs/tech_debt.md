# 技术债务清单（DEBT-PRIORITY-EVOLVE Probe 结果落盘）

**日期**: 2026-08-19
**来源**: .aionui/debt/ 四维债务库 + 本次 Probe
**排序模型**: 影响40% + 频率25% + 成本20% + 安全15%

## 安全债务（security_debt.yaml）

| ID | 严重度 | 暴露面 | 标题 | 建议修复轨 |
|----|--------|--------|------|-----------|
| SD-001 | CRITICAL | Dashboard JWT 鉴权（HTTP 面） | 硬编码 JWT 密钥 | ✅ **已修复** (2026-08-19): fail-closed，生产无 GOV_AUTH_SECRET 拒绝启动 |
| SD-003 | MEDIUM | 固件调试口 | OpenOCD 调试接口未被禁用 | 生产固件禁用 SWD/JTAG（比赛前） |

> 注：SD-001 severity=CRITICAL 但 priority 由暴露面决定——MCP 全走 stdio 不触 JWT 链，故不阻塞任务A（独立债务轨道）。

## 运维债务（operational_debt.yaml）

| ID | 严重度 | 暴露面 | 标题 | 建议修复轨 |
|----|--------|--------|------|-----------|
| OD-001 | P0 | 构建/CI | Renode 路径硬编码（WSL 容器化不可移植）| 环境变量化（参照 cognify paths.py 模式）|
| OD-002 | P1 | CI 耗时 | pip-audit 与 safety 重复扫描 | 二选一保留 |
| OD-004 | P2 | 成本 | deepseek-v4-pro 计费未追踪 | 接入 token 计数（Hermes 已有 cost 字段）|

## 技术债务（debt_registry.yaml）

| ID | 严重度 | 暴露面 | 标题 | 建议修复轨 |
|----|--------|--------|------|-----------|
| D-002 | P0 | 训练管线 | bottlesumo_gym 集成 | 仿真→训练闭环 |
| D-005 | P1 | V9 门 | 边缘掉落率 >37% | 边缘规避强化 |
| D-006 | P1 | V9 门 | 胜率 47%→60% | DDQN+PER |
| D-007 | P1 | 部署 | v9 distill 模型 → STM32 | 固件烧录 |
| D-009 | P2 | 泛化 | 跨对手泛化测试 | 对手增强训练 |

## 认知债务（cognitive_debt.yaml）

| ID | 严重度 | 暴露面 | 标题 | 建议修复轨 |
|----|--------|--------|------|-----------|
| CD-001 | P1 | 归因 | V9 胜率归因分析缺失 | 因果分析 |
| CD-002 | P1 | Onboarding | 元治理对新人不可见 | 教育层补全 |
| CD-003 | P2 | 一致性 | Phase 0 与 architecture_overview 不一致 | 文档同步 |
| CD-005 | P3 | 合规 | CTEA 赛规可能过时 | 规则重检 |

## 插件/MCP 相关债务（DEBT-PRIORITY-EVOLVE 优先轨道）

| ID | 债务 | 状态 |
|----|------|------|
| MCP-001 | registry 非事实源（7 个 Hermes enabled 未同步 registry）| 🔲 待补清单 |
| MCP-002 | 批 1 候选后端空心（mlflow/neo-mcp/automl/tabicl）| 🔲 已确认剔除 |
| MCP-003 | zerofit/predicatalot 镜像未拉取（docker 可用）| 🔲 批 1 候选 |
| MCP-004 | 记忆域写策略未定 | ✅ 已定（DSH 主写，见 MEMORY_WRITE_POLICY.md）|

## 本轮处置汇总（2026-08-19）

- ✅ SD-001 已修复（fail-closed，commit c6c9b07）
- ✅ MCP-004 写策略已定（DSH dsh-memory 主写）
- ✅ MCP-002 批 1 空心候选已剔除（后端存在性检查）
- 🔲 剩余 12 条按优先级排队（P0: OD-001/D-002 → P1: SD-003/D-005/D-006/D-007/CD-001/CD-002/OD-002 → P2/P3）
