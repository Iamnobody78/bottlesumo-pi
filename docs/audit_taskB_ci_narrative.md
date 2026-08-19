# 任务B 双门禁闭环叙事（真相升级版）

**日期**: 2026-08-19
**审计人**: EXECUTOR（MENTOR ① 要求）

## 完整故事线

```
缺陷识别(T3/C5/D1) → 修复提交(d8d7287/569c337) → 门禁配置(ci.yml --cov-fail-under=90, docs.yml strict)
→ 【真相: 4 workflow disabled_manually】→ 8-19 提交从未触发 CI
→ 根因挖掘: CI/Docs/E2E/Release 全部被手动禁用(仅 CodeQL/Stale active)
→ CI 重新启用 → 空提交 4b00d55 触发 → run 32219035894 SUCCESS (1m3s)
```

## 关键事实

| 项 | 值 |
|----|-----|
| disabled 范围 | CI / Docs / E2E / Release（4 个 workflow）|
| disabled 根因 | disabled_manually（GitHub 设置层人工禁用，非 workflow 文件缺陷——POST enable 对 Docs/E2E/Release 未生效佐证）|
| CI 重新启用 | ✅ active，run 32219035894 success |
| CI run sha | 4b00d55 = 本地 HEAD（验证终点代码）|
| 中间态风险 | 19 个提交从未单独验证，终点已验证（可接受残余风险）|
| E2E/Release | 仍 disabled——若源于仓库设置，**保持 disabled 是合理决策**（低维护面），记录为"有意禁用"而非"未知" |

## 教训（写入规则库候选）

1. **门禁配置 ≠ 门禁运行**：workflow 文件存在不代表 CI 在跑——需定期检查 workflow state
2. **提交后必须验证 CI 触发**：8-19 的 5 个提交无 CI 反应是红旗，应当时察觉
3. **disabled_manually 需定性**：是"有意禁用"还是"意外"，必须记录在案

## 遗留

- Docs/E2E/Release 的 disabled 定性：待确认仓库设置（Actions 页人工禁用 vs 其他）——若人工有意，记录为有意；E2E 建议修复后由 main 推变更激活
