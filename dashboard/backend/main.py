"""治理中心 Dashboard 后端入口 (FastAPI)。

运行: uvicorn main:app --port 8010 --reload
"""
import os
import sys

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from governance_engine import GovernanceEngine  # noqa: E402
from routers import governance  # noqa: E402

app = FastAPI(
    title="Governance Center Dashboard",
    version="0.1.0 (S68 Phase 1 MVP)",
    description="BottleSumo 治理中心 — 代理清单/策略管理/审计查看/VCE 可视化",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 引擎门面: 同进程集成 agent-governance-v2
app.state.governance_engine = GovernanceEngine()

app.include_router(governance.router)


@app.get("/api/health")
def health():
    return {"status": "ok", "engine": "agent-governance-v2", "sprint": "S68"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8010)
