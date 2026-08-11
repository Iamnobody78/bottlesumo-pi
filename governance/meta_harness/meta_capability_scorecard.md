# 元能力五维评估表 (META-CAPABILITY SCORECARD)

> 生成: 2026-08-10 (20260810_194948) | 工具: META-BOOTSTRAP v1.0 | 标签: META_SCORECARD
> 依据: meta_decisions.jsonl / pareto_frontier.md / failure_analysis.md /
> meta_engineering_rules.md / experience/hypotheses.jsonl / sprint 报告

## 总分与成熟度

| 维度 | 分数 (0-5) | 成熟度 | 关键证据 | 主要差距 |
| :--- | :---: | :---: | :--- | :--- |
| 元认知 (Meta-Cognition) | 2.5 | L2 | hypotheses_jsonl_lines=63; reasoning_chain=sprint 报告 + failure_analysis 记录; bias_detection_formalized=S56 进行中 (fix=2 退化段 + jump 排除实证) | 不确定性来源识别 (数据不足/模型局限/工具不可用) 未形式化 |
| 元监督 (Meta-Supervision) | 4.0 | L4 | meta_decisions_jsonl=1536; pareto_frontier_lines=548; gate_progress=V9 门 10% -> 90% (S38, chase-BC 直投 + defensive 审计) | HONEST-BOUNDARY 边界感知已设计未全量落地 |
| 元调节 (Meta-Regulation) | 3.5 | L3~L4 | param_bounds_updates=88; meta_config=temperature/retrieval_threshold/target_priority 自适应 (stagnation 触发); target_priority_rotation=physics->reward->mapping 轮换 | 资源分配未与 SRS 联动 |
| 元学习 (Meta-Learning) | 4.0 | L4 | rules_entries=13; cell_learning_events=169; failure_analysis_lines=1813 | 知识迁移跨领域形式化 (NCLT 教训 -> 其他传感器融合域) 未沉淀 |
| 元进化 (Meta-Evolution) | 2.5 | L2~L3 | sprint_reports=11; code_agent_proposer=存在 (56KB); candidates_dir=53 | 架构演进决策未形式化 (无 ROADMAP.md 决策记录) |

**综合元能力指数 (MCI)**: 3.30/5.0 (L3 主导)

## 逐维度详情

### 元认知 (Meta-Cognition) — L2 (2.5/5)

**证据**:
- hypotheses_jsonl_lines: 63
- reasoning_chain: sprint 报告 + failure_analysis 记录
- bias_detection_formalized: S56 进行中 (fix=2 退化段 + jump 排除实证)
- uncertainty_source_id: 待落地 (框架自评 ⚡)

**差距 (改进候选)**:
- 不确定性来源识别 (数据不足/模型局限/工具不可用) 未形式化
- 偏差检测已实证 (S56: 02-23 fix=2 退化段 154s -> +10km) 但未固化为可复用能力

### 元监督 (Meta-Supervision) — L4 (4.0/5)

**证据**:
- meta_decisions_jsonl: 1536
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
- rules_entries: 13
- cell_learning_events: 169
- failure_analysis_lines: 1813
- distill: distill_loop.py nano 蒸馏 (789 params, 87.5% 门)

**差距 (改进候选)**:
- 知识迁移跨领域形式化 (NCLT 教训 -> 其他传感器融合域) 未沉淀

### 元进化 (Meta-Evolution) — L2~L3 (2.5/5)

**证据**:
- sprint_reports: 11
- code_agent_proposer: 存在 (56KB)
- candidates_dir: 53

**差距 (改进候选)**:
- 架构演进决策未形式化 (无 ROADMAP.md 决策记录)
- 自举循环 (用自身输出改进自身) 未落地
- 开放式改进未与 Meta-Harness 变体生成联动

## 结论与自举建议

- MCI=3.30: 元监督/元学习最成熟 (L4), 元认知/元进化最薄弱 (L2-L3)
- **自举优先级**: 先补元认知 (偏差检测形式化 + 不确定性来源识别), 再补元进化 (架构演进决策 + 自举循环)
- S56 实证已为元认知-偏差检测提供现成素材: fix=2 退化段检测 (JUMP_DMAX/F2_SIGMA) 可固化为可复用能力
