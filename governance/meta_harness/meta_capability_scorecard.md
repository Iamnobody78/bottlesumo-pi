# 元能力五维评估表 (META-CAPABILITY SCORECARD)

> 生成: 2026-08-13 (20260813_164458) | 工具: META-BOOTSTRAP v1.0 | 标签: META_SCORECARD
> 依据: meta_decisions.jsonl / pareto_frontier.md / failure_analysis.md /
> meta_engineering_rules.md / experience/hypotheses.jsonl / sprint 报告

## 总分与成熟度

| 维度 | 分数 (0-5) | 成熟度 | 关键证据 | 主要差距 |
| :--- | :---: | :---: | :--- | :--- |
| 元认知 (Meta-Cognition) | 3.0 | L3 | hypotheses_jsonl_lines=63; reasoning_chain=sprint 报告 + failure_analysis 记录; bias_detection_formalized=S56 fix=2 退化段已固化 (RULE-MC-013); jump 排除仍进行中 | 偏差检测 jump 排除未固化 (S56 进行中) |
| 元监督 (Meta-Supervision) | 4.0 | L4 | meta_decisions_jsonl=1541; pareto_frontier_lines=548; gate_progress=V9 门 10% -> 90% (S38, chase-BC 直投 + defensive 审计) | HONEST-BOUNDARY 边界感知已设计未全量落地 |
| 元调节 (Meta-Regulation) | 3.5 | L3~L4 | param_bounds_updates=88; meta_config=temperature/retrieval_threshold/target_priority 自适应 (stagnation 触发); target_priority_rotation=physics->reward->mapping 轮换 | 资源分配未与 SRS 联动 |
| 元学习 (Meta-Learning) | 4.0 | L4 | rules_entries=16; cell_learning_events=169; failure_analysis_lines=1813 | 知识迁移跨领域形式化 (NCLT 教训 -> 其他传感器融合域) 未沉淀 |
| 元进化 (Meta-Evolution) | 3.0 | L3 | sprint_reports=11; code_agent_proposer=存在 (56KB); candidates_dir=53 | 开放式改进未与 Meta-Harness 变体生成联动 (meta_evol 缺口 3) |

**综合元能力指数 (MCI)**: 3.50/5.0 (L3 主导)

## 逐维度详情

### 元认知 (Meta-Cognition) — L3 (3.0/5)

**证据**:
- hypotheses_jsonl_lines: 63
- reasoning_chain: sprint 报告 + failure_analysis 记录
- bias_detection_formalized: S56 fix=2 退化段已固化 (RULE-MC-013); jump 排除仍进行中
- uncertainty_source_id: 已形式化 (uncertainty_source.py 三通道 + RULE-MC-014), 待真实运行积累标注

**差距 (改进候选)**:
- 偏差检测 jump 排除未固化 (S56 进行中)
- 不确定性标注机制已建 (uncertainty_source.py) 但未在真实运行中 exercise

### 元监督 (Meta-Supervision) — L4 (4.0/5)

**证据**:
- meta_decisions_jsonl: 1541
- pareto_frontier_lines: 548
- gate_progress: V9 门 10% -> 90% (S38, chase-BC 直投 + defensive 审计)
- monitor: meta_monitor.py (stagnation/loop/latency_anomaly)

**差距 (改进候选)**:
- HONEST-BOUNDARY 边界感知已设计未全量落地

### 元调节 (Meta-Regulation) — L3~L4 (3.5/5)

**证据**:
- param_bounds_updates: 88
- meta_config: temperature/retrieval_threshold/target_priority 自适应 (stagnation 触发)
- target_priority_rotation: physics->reward->mapping 轮换

**差距 (改进候选)**:
- 资源分配未与 SRS 联动
- 工具选择未与 MCP 联动 (mcp_usage_report.jsonl 已有数据)

### 元学习 (Meta-Learning) — L4 (4.0/5)

**证据**:
- rules_entries: 16
- cell_learning_events: 169
- failure_analysis_lines: 1813
- distill: distill_loop.py nano 蒸馏 (789 params, 87.5% 门)

**差距 (改进候选)**:
- 知识迁移跨领域形式化 (NCLT 教训 -> 其他传感器融合域) 未沉淀

### 元进化 (Meta-Evolution) — L3 (3.0/5)

**证据**:
- sprint_reports: 11
- code_agent_proposer: 存在 (56KB)
- candidates_dir: 53
- architecture_decisions_formalized: ROADMAP.md DEC-001..003 (架构演进决策记录)
- self_evolve_loop: bootstrap_loop.py 数据驱动闭环 (scan->select->allocate->formalize)

**差距 (改进候选)**:
- 开放式改进未与 Meta-Harness 变体生成联动 (meta_evol 缺口 3)

## 结论与自举建议

- MCI=3.50: 元监督/元学习最成熟 (L4), 元认知 (L3, 已升) / 元进化 (L2-L3) 为当前最薄弱
- **自举优先级**: 元认知不确定性来源已形式化 (R-014); 下一优先 = 元进化 (架构演进决策已落地 ROADMAP, 变体生成联动仍缺口) + 元认知 jump 排除固化
- S56 实证已为元认知-偏差检测提供现成素材: fix=2 退化段检测已固化 (RULE-MC-013), jump 排除待固化
