"""治理中心数据模型 (SQLAlchemy)。

四张表 (S67 dashboard_spec.md §3.2):
  - agents          代理清单
  - audit_events    审计事件 (evaluate_verified 自动入库)
  - vce_scans       VCE 扫描历史 (趋势图数据源)
  - policy_snapshots 策略快照 (编译时入库)
"""
from datetime import datetime

from sqlalchemy import (JSON, Boolean, Column, DateTime, Float, ForeignKey,
                        Integer, String, Text)
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Agent(Base):
    __tablename__ = "agents"

    id = Column(String, primary_key=True)       # agent_id
    name = Column(String, nullable=False)
    role = Column(String, default="executor")   # 执行器/审查器/规划器...
    status = Column(String, default="active")   # active/idle/suspended
    last_seen = Column(DateTime, default=datetime.utcnow)
    sessions = Column(Integer, default=0)


class AuditEvent(Base):
    __tablename__ = "audit_events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    ts = Column(DateTime, default=datetime.utcnow, index=True)
    agent_id = Column(String, ForeignKey("agents.id"), index=True)
    path = Column(String, default="")
    method = Column(String, default="POST")
    matched_rule = Column(String, index=True)
    action = Column(String, index=True)         # 最终动作 (含降级后 ESCALATE)
    channel = Column(String, default="none", index=True)
    verification = Column(JSON, default=dict)   # VerificationResult.to_dict()
    raw_body = Column(JSON, default=dict)       # 请求体 (声明)


class VceScan(Base):
    __tablename__ = "vce_scans"

    id = Column(Integer, primary_key=True, autoincrement=True)
    ts = Column(DateTime, default=datetime.utcnow)
    report = Column(JSON, default=dict)         # vce_scan_report 全量快照
    polarization = Column(Float, default=0.0, index=True)
    conflict_count = Column(Integer, default=0)
    blindspot_count = Column(Integer, default=0)
    channel_enabled = Column(Boolean, default=False)


class PolicySnapshot(Base):
    __tablename__ = "policy_snapshots"

    id = Column(Integer, primary_key=True, autoincrement=True)
    ts = Column(DateTime, default=datetime.utcnow)
    protocol = Column(String, index=True)
    rule_type = Column(String)                  # ethics/enforce/ok
    rule_name = Column(String)
    priority = Column(Integer)
    action = Column(String)
    json_path = Column(String, default="")
    json_pattern = Column(Text, default="")
    origin = Column(String, default="")
