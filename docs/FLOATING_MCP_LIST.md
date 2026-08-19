# 游离 MCP 清单（Hermes enabled vs registry 对账）— 最终版

**日期**: 2026-08-19（最终）
**对账依据**: reconcile.py + reconcile_table.py 实测

## 结论：20/20 全部对齐，0 游离

| # | 服务器 | 来源 | 扫描 | registry | verified |
|---|--------|------|------|----------|----------|
| 1 | visionsearch | registry-ready | ok | verified | true |
| 2 | llm-vision | registry-ready | ok | verified | true |
| 3 | image-recognition | registry-ready | ok | verified | true |
| 4 | three-ws-vision | registry-ready | ok | verified | true |
| 5 | cad-mcp-server | registry-ready | ok | verified | true |
| 6 | mcp-cad-studio | registry-ready | ok | verified | true |
| 7 | loki-cad-mcp | registry-ready | ok | verified | true |
| 8 | playwright | registry-ready | ok | verified | true |
| 9 | sequential-thinking | registry-ready | ok | verified | true |
| 10 | memory | registry-ready | ok | verified | true |
| 11 | github | registry-ready | ok | verified | true |
| 12 | filesystem | registry-ready | ok | verified | true |
| 13 | cognify | registry-ready | ok | verified | true |
| 14 | chrome-devtools | registry-ready | ok | verified | true |
| 15 | aionui-browser | manual | **fail** | **falsified** | false |
| 16 | platform-filesystem | manual | ok | verified | true |
| 17 | platform-fetch | manual | ok | verified | true |
| 18 | platform-memory | manual | ok | verified | true |
| 19 | team-coordinator | manual | ok | verified | true |
| 20 | axiom-math | manual | ok | verified | true |

## 处置记录

1. **6 个手工部署（S57-S69）**：platform-filesystem/fetch/memory/team-coordinator/aionui-browser/axiom-math
   - 5 个扫描通过 → 补 registry 条目并 verified
   - aionui-browser 连接失败 → falsified（reason: Connection closed 8891ms, 挂 DEBT 轨道修复）
2. **axiom-math**：registry-only → verified（状态脱节已修正）
3. **佐证**：失败项恰好落在手工安装批 → 手工部署可信度低于 registry 流程部署，写入验收文档

## 证据文件
- `hermes_mcp_health.json`（20 服务器 connect/tools 实测 + state.db 副作用记录）
- registry v2.2.0（274 条目，verified/last_verified/evidence_file 字段）
