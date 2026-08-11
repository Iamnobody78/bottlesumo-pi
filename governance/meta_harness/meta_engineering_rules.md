# Meta-Engineering Rules（元认知工程规则库）

> FSCL-ARCH Phase L 学习闭环沉淀库 (MAA-ARCH 元认知层专属)。
> 与 dashboard/engineering_rules.md (SEFS-ARCH 工程规则库) 分离：
> 本库记录**元认知失败模式**（停滞/循环/延迟异常）→ 学习规则，
> 供 outer_loop 自指改进与 V9 裁决门参考。
> 编号: `RULE-MC-<n>` | 追加制, 仅标记 OBSOLETE。

## 规则表

| ID | 规则 | 来源 |
| :--- | :--- | :--- |

<!-- cell_learner 追加位置 -->

| RULE-MC-001 | 探索停滞: 连续 3 轮无 Pareto 改进, 应切换目标文件优先级 或扩大检索范围, 而非重复同层候选 | cell_learner 2026-08-07 |
| RULE-MC-002 | 提议器循环: 变体 mh_probe_01 在 [3, 4] 轮内重复 2 次, 需注入多样性 (温度扰动或换层) | cell_learner 2026-08-07 |
| RULE-MC-003 | 评估延迟异常: 单轮耗时 60.0s > 5.0x 滚动平均, 检查环境负载/资源水位后再继续迭代 | cell_learner 2026-08-07 |

| RULE-MC-004 | 提议器循环: 变体 ca_rules_002 在 [2, 3] 轮内重复 2 次, 需注入多样性 (温度扰动或换层) | cell_learner 2026-08-07 |

| RULE-MC-005 | 提议器循环: 变体 ca_rules_007 在 [4, 5] 轮内重复 2 次, 需注入多样性 (温度扰动或换层) | cell_learner 2026-08-07 |

| RULE-MC-006 | 提议器循环: 变体 ca_rules_001 在 [3, 4] 轮内重复 2 次, 需注入多样性 (温度扰动或换层) | cell_learner 2026-08-07 |

| RULE-MC-007 | 提议器循环: 变体 ca_reward_001 在 [1, 2] 轮内重复 2 次, 需注入多样性 (温度扰动或换层) | cell_learner 2026-08-08 |

| RULE-MC-008 | 提议器循环: 变体 ca_reward_001 在 [1, 2, 3] 轮内重复 3 次, 需注入多样性 (温度扰动或换层) | cell_learner 2026-08-08 |

| RULE-MC-009 | 提议器循环: 变体 ca_reward_001 在 [2, 3] 轮内重复 2 次, 需注入多样性 (温度扰动或换层) | cell_learner 2026-08-08 |

| RULE-MC-010 | 提议器循环: 变体 ca_reward_001 在 [3, 5] 轮内重复 2 次, 需注入多样性 (温度扰动或换层) | cell_learner 2026-08-08 |

| RULE-MC-011 | 提议器循环: 变体 ca_mapping_001 在 [1, 2] 轮内重复 2 次, 需注入多样性 (温度扰动或换层) | cell_learner 2026-08-08 |

| RULE-MC-012 | 提议器循环: 变体 ca_reward_001 在 [3, 4] 轮内重复 2 次, 需注入多样性 (温度扰动或换层) | cell_learner 2026-08-08 |

| RULE-TS-004 | 测试隔离: 凡测试涉及写持久化文件的辅助函数 (如 `_record_diff_decision`), 必须在 fixture 层隔离 (mock 或临时目录), 禁止直接修改运行时审计日志 | PM 治理 2026-08-08 (FP-MC-016 修复经验) |

| RULE-MC-011 | 传感器退化段不是失锁: 码/浮点解 (fix=2) 携带冻结/陈旧坐标, 按退化段处理 (软位置更新 + 协方差增长), 而非纯 DR 保持; 检测特征 = 连续相同坐标 + fix 降级 (NCLT 实证: 02-23 154s -> +10km) | meta_bootstrap S56 实证 2026-08-10 |
