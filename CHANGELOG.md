# Changelog

遵循 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/) 风格，按治理 Sprint 组织。

## [Unreleased]

## [v2.1.0] — 2026-08-10 · ARCH-ROUND 1（生产基线：数据库 + 可观测性 + 容器化）

### Added
- **生产级数据库支持**（GAP-2.1）：`GOV_DASH_DB_URL` 标准 SQLAlchemy URL 一键切换 PostgreSQL；SQLite 保持默认零配置；`resolve_db_url` 纯函数 + 5 单测；CI 新增 PostgreSQL 16 矩阵 job
- **可观测性**（GAP-1.1）：`GET /metrics` Prometheus 端点（统一 `governance_*` 命名空间，DUAL-ECO 双项目一致）；JSON 结构化日志（`GOV_LOG_FORMAT=json`，零额外依赖）；4 单测
- **容器化部署**（GAP-5.1）：多阶段 Dockerfile（构建时锁定拉取 agent-governance-v2 ref）；docker-compose（backend/frontend/postgres + `observability` profile 含 Prometheus/Grafana）；nginx SPA 托管 + /api 反代；HEALTHCHECK
- **生产化路线图**（GAP-6.1）：`docs/architecture/ROADMAP_PRODUCTION.md`（v2.x 稳固核心 / v3.0 能力增强 / v4.0+ 生态构建，含 DoD 门）
- 文档：`docs/architecture/database.md` / `observability.md` / `deployment.md`；根级 `.env.example`；`.dockerignore`

### Changed
- Dashboard backend requirements：+ `psycopg[binary]`、+ `prometheus-client`
- CI gate 扩展：`dashboard-backend-pg`（PostgreSQL 16 service）纳入 gate 依赖
- CHANGELOG 结构：v2.0.0 细化为四视图 MVP 行（S69 变更回填）

### Fixed
- `build_engine` 向后兼容：第一位置参数保持 `db_path`（governance_engine.py 依赖）；`resolve_db_url` 实时读环境变量（支持测试 monkeypatch）
- E2E 部署残留协议污染真实 config（`e2e_demo.yaml`）导致 seed 规则 12≠9：本版清理，E2E 自清理列入 P1（GAP-4.2 周边）

### 跨项目影响（DUAL-ECO）
- 引擎（agent-governance-v2）零代码变更；指标命名空间 `governance_*` 已在引擎侧约定，双项目可共用一个 Grafana 面板
- 容器构建需访问 GitHub 拉取引擎（Iamnobody78/agent-governance-v2，`GOV_ENGINE_REF` 锁定）

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
