"""治理中心 Dashboard 后端入口 (FastAPI)。

运行: uvicorn main:app --port 8010 --reload
"""
import os
import sys

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from governance_engine import GovernanceEngine  # noqa: E402
from logging_setup import setup_logging  # noqa: E402
from metrics import MetricsMiddleware, metrics_response  # noqa: E402
from routers import governance  # noqa: E402

setup_logging()

app = FastAPI(
    title="Governance Center Dashboard",
    version="0.1.0 (S68 Phase 1 MVP + S69 策略编辑器 + ARCH T0.3 可观测性)",
    description="BottleSumo 治理中心 — 代理清单/策略管理/审计查看/VCE 可视化",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(MetricsMiddleware)

# 引擎门面: 同进程集成 agent-governance-v2
app.state.governance_engine = GovernanceEngine()

app.include_router(governance.router)


@app.get("/api/health")
def health():
    return {"status": "ok", "engine": "agent-governance-v2", "sprint": "S69"}


@app.get("/metrics")
def metrics():
    """Prometheus 指标端点（governance_* 命名空间, GAP-1.1）。"""
    return metrics_response()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8010)
