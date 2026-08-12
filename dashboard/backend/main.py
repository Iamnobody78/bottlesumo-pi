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
from routers import auth, governance  # noqa: E402

setup_logging()

app = FastAPI(
    title="Governance Center Dashboard",
    version="0.2.0 (S69 策略编辑器 + ARCH T0.3 可观测性 + ARCH-ROUND 2 RBAC)",
    description="BottleSumo 治理中心 — 代理清单/策略管理/审计查看/VCE 可视化/RBAC",
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
app.include_router(auth.router)


@app.on_event("startup")
def startup_seed():
    """首次启动种子: users 空则创建 admin 用户 (RBAC, GAP-3.1)。"""
    from auth import get_db
    from routers.auth import seed_admin_if_empty
    db = next(get_db())
    try:
        seed_admin_if_empty(db)
    finally:
        db.close()


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
