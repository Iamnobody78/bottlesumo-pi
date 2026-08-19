# 游离 MCP 清单（Hermes enabled 但 registry 未对齐）

**日期**: 2026-08-19
**对账依据**: reconcile.py 实测（Hermes 20 enabled vs registry v2.2.0）

## 结论：20 = 14 registry-ready + 6 无条目 + 1 状态脱节

### 6 个无 registry 条目（全为手工部署）

| # | 名称 | 安装方式 | 来源时期 | 状态 |
|---|------|---------|---------|------|
| 1 | aionui-browser | node CLI | S57 平台化 | enabled |
| 2 | platform-filesystem | Python 自研 | S57 平台化 | enabled |
| 3 | platform-fetch | Python 自研 | S57 平台化 | enabled |
| 4 | platform-memory | Python 自研 | S57 平台化 | enabled |
| 5 | team-coordinator | Python 自研 | S57 团队协调 | enabled |
| 6 | axiom-math | npm (Giac/WASM CAS) | S69 数学域 | enabled |

### 1 个状态脱节

| # | 名称 | registry 状态 | 实际状态 | 需修正 |
|---|------|-------------|---------|--------|
| 7 | axiom-math | registry-only | Hermes enabled | registry → ready |

### 修正动作
- 6 个无条目 → 补 registry 条目（含 transport/command/来源标注）
- axiom-math → status 改 ready
- 修正后 20 = 20（registry 与 Hermes 完全对齐）

### 扫描脚本的"来源"标注
- registry-ready: 14 个（visionsearch/llm-vision/image-recognition/three-ws-vision/cad-mcp-server/mcp-cad-studio/loki-cad-mcp/playwright/sequential-thinking/memory/github/filesystem/cognify/chrome-devtools）
- 手工部署: 6 个（aionui-browser/platform-filesystem/platform-fetch/platform-memory/team-coordinator/axiom-math）
