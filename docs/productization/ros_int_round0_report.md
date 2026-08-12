# ROS 2 集成报告 [#ROS-INT-ROUND_0]

> 日期: 2026-08-11 | 协议: ROS-INTEGRATE v1.0 | 报告人: 治理智能体（Sprint 70）

## 摘要

ROS-INTEGRATE 协议装载后的首次环境探测（Phase R 侦察）。**核心发现：ROS 2 迁移地基已存在但未完成** —— `/bottlesumo_env/ros2_env/bottlesumo_pi/` 是一个构建过的 colcon 工作区（含 `bottlesumo_gym` 完整 gym 环境实现，已是 ROS 2 节点），但 ROS 2 运行时本体未安装。就绪度评估：**L2 部分实现 / L5 未验证**，下一步需 PM 批准安装 ROS 2 Humble。

## [Phase R: Ready] — 环境探测

| 项目 | 状态 | 证据 |
|------|------|------|
| WSL 发行版 | ✅ Ubuntu 22.04 | `python3 --version` → 3.10.12（ROS 2 Humble 目标版本） |
| ROS 2 运行时 | ❌ **未安装** | `ros2 --version` → NOT INSTALLED |
| colcon | ❌ 未安装（系统级） | `colcon --version` → NOT INSTALLED |
| Gazebo | ✅ 11.10.2 | Gazebo Classic（ROS 2 Humble 官方配对） |
| 工作区骨架 | ✅ **已存在** | `/bottlesumo_env/ros2_env/bottlesumo_pi/`（2026-07-26 创建） |
| 构建产物 | ✅ **install/ + build/ 非空** | 两个包均有产物 = colcon build 曾成功（可能在其他环境） |
| 磁盘 | ✅ 919G 空闲 | 安装 ROS 2 Humble（约 3-5GB）无压力 |

### 工作区内容审计

```
/bottlesumo_env/ros2_env/bottlesumo_pi/
├── src/
│   ├── bottlesumo_gym/          # ament_python, v0.1.0, MIT
│   │   ├── package.xml          # 依赖: rclpy/std_msgs/geometry_msgs/sensor_msgs/nav_msgs/gazebo_msgs
│   │   └── bottlesumo_gym/bottlesumo_gym_env.py  # 263 行完整 gym 环境
│   └── bottlesumo_description/  # URDF xacro + worlds + launch + controller.yaml
├── worlds/                      # sumo_arena.sdf, arena_mini.sdf
├── meshes/ urdf/ launch/        # 描述资产
├── install/ build/ log/         # colcon 产物（已构建过）
└── (1.8M 总量)
```

### L2 现状：`bottlesumo_gym_env.py` 已是 ROS 2 节点

- rclpy Node `bottlesumo_gym_node`，SingleThreadedExecutor
- 订阅: `LaserScan` / `Range` / `Odometry`
- 发布: `Twist`（速度指令）
- **动作空间: 11 离散动作（对齐 V9 指令集）** ← 与治理引擎指令集一致
- 观测空间: `[edge_F, edge_B, edge_L, edge_R, opponent_dist, opponent_angle]`
- 奖励: +200 推对手出界 / -100 自己出界 / +1 接近 / -2×边缘距离（对齐现有奖励函数）
- headless 模式: 自动 xvfb + Gazebo 启动

## [Phase O: Organize] — 现状与缺口

| 项 | 状态 | 说明 |
|----|------|------|
| 控制器节点 | ⚠️ 部分 | gym env 已封装执行层，但决策算法节点未封装 |
| 治理服务 | ❌ 无 | `agent-governance-v2` 未服务化（无 .srv/.action） |
| 接口定义 | ❌ 无 | 无 `.msg`/`.srv`/`.action` 文件（隐式代码内定义） |
| launch 文件 | ⚠️ 部分 | description 包内有 launch，但无一键全栈 launch |
| setup 脚本 | ❌ 无 | 无 `setup_ros2_workspace.sh` |

## [Phase S: Simulate] — 未执行

本机从未运行过 ROS 2 闭环（运行时未安装）。`install/` 产物来源不明（可能在其他环境构建），**不可作为验证依据**。

## [Phase E: Evaluate & Evolve] — 未执行

N/A（L5 未验证前不评估）

## 路线图（提案）

| 阶段 | 动作 | 依赖 | 预估 |
|------|------|------|------|
| L1a | PM 批准安装 `ros-humble-desktop` + colcon（~3-5GB，磁盘 919G 空闲） | PM 批准 | 30-60min |
| L1b | 编写 `setup_ros2_workspace.sh` + colcon 全量重建验证 | L1a | 30min |
| L2a | 封装 `bottlesumo_controller_node.py`（决策算法 → 节点） | L1b | 1-2h |
| L3a | `governance_action_server.py`（治理引擎 → action server，裁决语义与引擎一致） | L2a | 1-2h |
| L4a | 定义 `.msg`/`.srv`/`.action` 接口 | L2a | 1h |
| L5a | Gazebo 闭环 + 与原始仿真输出对比（行为差异基线） | L4a | 2-4h |
| L6a | `sim2real_gap_report.md` | L5a | 1h |

## [Honest Boundary]

- **本次完成范围**: L1 侦察（无写入、无安装）
- **本次未处理项**:
  - ROS 2 Humble 运行时安装（需 PM 批准 + 磁盘/apt 权限，红线 #4：未过构建不提交）
  - L2-L6 全部未启动（依赖 L1a 批准）
  - `install/` 产物来源未验证（不排除其他机器构建）
  - WSL 内网络/apt 源状态未验证
- **风险提示**: 若在 Windows 主机另装 ROS 2（Windows 原生支持 Humble），与 WSL 工作区会分裂成两套环境 —— 建议统一在 WSL 内完成（HONEST-BOUNDARY）
