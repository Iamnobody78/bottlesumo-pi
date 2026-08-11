# Changelog

遵循 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/) 风格，按治理 Sprint 组织。

## [Unreleased]

## [v2.0.0] — 2026-08-10 · Sprint 69（产品化 + 开源治理资产 + CI/CD）

### Added
- **Governance Center Dashboard**（S68 合并，S69 增强）：
  - 四视图 MVP：仪表盘 / 策略管理 / 审计 / VCE 可视化
  - GovernanceEngine 门面（同进程 import agent-governance-v2，`GOV_AGENTS_V2_PATH` 可覆盖）
  - audit_sink 审计回调（fail-open）
  - **策略编辑器**（S69）：YAML 源查看 / 零副作用校验 / 带回滚部署
- **开源治理资产**（PM P0）：README / ARCHITECTURE / CONTRIBUTING / LICENSE (MIT) / SECURITY / CHANGELOG
- **CI/CD 基础设施**：ci.yml（主仓库冒烟 + Dashboard backend pytest + frontend build）、e2e（Playwright 计划）、docs（GitHub Pages 计划）、release（tag → 产物）

### Changed
- README 定位：旗舰主体 + 治理中枢双层呈现

### Fixed
- 编辑器 deploy 测试隔离：临时协议目录，不污染真实 config（S69）

### Security
- 策略部署通道：校验 → 写入 → 重建网关 → `.bak` 回滚；路径遍历防护

## [v11.11-IndustrialGrade] — 2026-07-31 · 旗舰主体基线（S53-S62）

### Added
- 工具固化 + 熵断路器 + 评估者硬化（3 层）+ 四深水区（错误分类/回归/锁/因果）
- 9 层架构（Layer 0 执行宪法 + L1 治理 + L2-8 物理栈 + L9 软件 + L10 工具链）
- 14 层工具链（PlatformIO / KiCad / FreeCAD / Renode / Gazebo / PyTorch 等）

---

## 版本索引

| 版本 | 阶段 | 日期 |
|---|---|---|
| v11.11 | 旗舰主体 9 层基线 | 2026-07-31 |
| v2.0.0 | 产品化 Dashboard + 开源资产 + CI/CD | 2026-08-10 |

## 贡献

见 [CONTRIBUTING.md](CONTRIBUTING.md) 8-GATE 流程；Changelog 随代码同提交更新。
