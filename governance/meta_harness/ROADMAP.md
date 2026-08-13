# ROADMAP —— 架构演进决策记录 (元进化)

> 生成: bootstrap_loop.py ｜ 性质: 架构演进决策形式化 (meta_evol 缺口 1 修复)
> 因果推理要求: 每个 DEC 必须回答 为何失败 / 在哪分歧 / 如何精准修复

## DEC-20260813-001 — 元进化自举循环落地 + 架构演进决策形式化

- **决策**: 以 bootstrap_loop.py 建立数据驱动闭环 (scan->select->allocate->formalize), 并用 ROADMAP.md DEC 记录形式化架构演进决策
- **维度**: 元进化 (Meta-Evolution)
- **因果推理**:
  - 为何失败: meta_bootstrap.evolve() 硬编码目标(元认知-偏差检测), select 阶段非数据驱动, 无法按 scorecard 最低分自动定位
  - 在哪分歧: 与 '自举优先级(先补最低分)' 的框架自评结论脱节; meta_evol 三缺口(决策未形式化/自举未落地/变体未联动)从未被闭环动作触及
  - 如何修复: scan_rules(检测 ID 冲突) + scan_scorecard(动态解析分数) + select_target(最低分) + allocate_rule_id(冲突安全) + formalize_decision(DEC 记录)
- **证据**: meta_bootstrap.py assess() 分数硬编码 (2.5/4.0/3.5/4.0/2.5); evolve() target 硬编码; RULE-MC-011 曾与 cell_learner 冲突(已修正为 013)
- **验收**: bootstrap_loop.py run() 产出 ROADMAP.md DEC 记录 + 下一轮可从 scorecard 动态重选目标

## DEC-20260813-002 — 数据驱动目标: 元认知 最低分 2.5/5

- **决策**: 针对 元认知 (Meta-Cognition) (scorecard 最低分 2.5/5), 将差距候选固化为下一轮可执行规则 RULE-MC-014
- **维度**: 元认知 (Meta-Cognition)
- **因果推理**:
  - 为何失败: 元认知 得分最低 (2.5/5), 是当前 5 维元能力中最薄弱环节
  - 在哪分歧: 自举闭环(scan/select/allocate/formalize)已能定位最低分, 但定位结果尚未转化为实际的规则/能力修复动作
  - 如何修复: 将 select_target 输出的差距候选 (不确定性来源识别 (数据不足/模型局限/工具不可用) 未形式化; 偏差检测已实证 (S56: 02-23 fix=2 退化段 154s -> +10km) 但未固化为可复用能力) 转成 RULE-MC-014, 在下一轮 loop 中闭合
- **证据**: scorecard={"元认知": 2.5, "元监督": 4.0, "元调节": 3.5, "元学习": 4.0, "元进化": 2.5}; 差距候选=不确定性来源识别 (数据不足/模型局限/工具不可用) 未形式化; 偏差检测已实证 (S56: 02-23 fix=2 退化段 154s -> +10km) 但未固化为可复用能力
- **验收**: 下一轮 scan_scorecard 中 元认知 分数提升 (需证据, 无证据不改分)

