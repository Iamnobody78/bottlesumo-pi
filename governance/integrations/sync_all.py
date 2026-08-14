#!/usr/bin/env python3
"""SYNC-ALL v1.0 -- AionUi ↔ DeepSeek Harness 统一上下文同步层

- 检测 DSH 会话数据 (storages/ 下的 JSONL/workspace 变更)
- 生成会话摘要写入 AionUi 可见的共享知识库 (bottlesumo_pi/governance/sync/)
- 提供 CLI: --status / --export / --watch

生成: 2026-08-14  AION-MULTI-AGENT 集成层 · SYNC-ALL 元提示词落地
"""
from __future__ import annotations
import os
import sys
import json
import glob
import time
import datetime
import hashlib

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

DSH_HOME = os.environ.get("DSH_HOME", os.path.expanduser("~/.dsh"))
DSH_STORAGES = os.path.join(DSH_HOME, "storages")
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SYNC_DIR = os.path.join(PROJECT_ROOT, "governance", "sync")
INDEX_FILE = os.path.join(SYNC_DIR, "sync_index.json")


def _now() -> str:
    return datetime.datetime.now().isoformat()


def _scan_dsh_sessions() -> list:
    """扫描 DSH storages 中的会话数据文件。"""
    found = []
    for pattern in ("*.jsonl", "*.json", "*.db", "*.sqlite"):
        for p in glob.glob(os.path.join(DSH_STORAGES, "**", pattern), recursive=True):
            if "workspace.json" in p:
                continue
            try:
                mtime = os.path.getmtime(p)
                found.append({
                    "path": p,
                    "name": os.path.basename(p),
                    "mtime": datetime.datetime.fromtimestamp(mtime).isoformat(),
                    "size": os.path.getsize(p),
                    "sha256": hashlib.sha256(open(p, "rb").read()).hexdigest()[:16],
                })
            except Exception:
                pass
    return found


def _scan_aionui_contexts() -> list:
    """扫描 AionUi 会话/元认知目录。"""
    found = []
    roots = [
        os.path.join(PROJECT_ROOT, ".aionui", "metacognition", "thoughts"),
        os.path.join(PROJECT_ROOT, "governance", "anchors"),
    ]
    for r in roots:
        if os.path.isdir(r):
            for f in os.listdir(r):
                p = os.path.join(r, f)
                if os.path.isfile(p) and f.endswith((".md", ".jsonl")):
                    found.append({
                        "path": p,
                        "name": f,
                        "mtime": datetime.datetime.fromtimestamp(os.path.getmtime(p)).isoformat(),
                        "size": os.path.getsize(p),
                    })
    return found


def _load_index() -> dict:
    if os.path.exists(INDEX_FILE):
        try:
            return json.load(open(INDEX_FILE, encoding="utf-8"))
        except Exception:
            return {}
    return {"dsh": {}, "aionui": {}}


def _save_index(idx: dict) -> None:
    os.makedirs(SYNC_DIR, exist_ok=True)
    json.dump(idx, open(INDEX_FILE, "w", encoding="utf-8", newline="\n"),
              ensure_ascii=False, indent=2)


def cmd_status() -> int:
    print("== SYNC-ALL 状态 ==")
    dsh_sessions = _scan_dsh_sessions()
    aionui_ctx = _scan_aionui_contexts()
    print("[DSH 侧] 会话/数据文件: %d 个" % len(dsh_sessions))
    for s in dsh_sessions[:10]:
        print("  - %s (%s, %dB, %s)" % (s["name"], s["mtime"], s["size"], s["sha256"]))
    print("[AionUi 侧] 上下文/锚点: %d 个" % len(aionui_ctx))
    for c in aionui_ctx[:10]:
        print("  - %s (%s, %dB)" % (c["name"], c["mtime"], c["size"]))
    idx = _load_index()
    print("[索引] DSH 已追踪: %d | AionUi 已追踪: %d" % (len(idx.get("dsh", {})), len(idx.get("aionui", {}))))
    print("[工作区] DSH 工作区: %s" % os.path.join(DSH_STORAGES, "workspace.json"))
    return 0


def cmd_export() -> int:
    """导出 DSH 会话为 AionUi 可读的共享摘要。"""
    os.makedirs(SYNC_DIR, exist_ok=True)
    idx = _load_index()
    dsh_sessions = _scan_dsh_sessions()
    new_or_changed = 0
    for s in dsh_sessions:
        key = s["sha256"]
        if idx.get("dsh", {}).get(key) == s["mtime"]:
            continue
        # 复制为共享摘要
        target = os.path.join(SYNC_DIR, "dsh_" + s["name"].replace(".", "_") + ".json")
        sh = {k: s[k] for k in ("name", "mtime", "size", "sha256", "path")}
        json.dump(sh, open(target, "w", encoding="utf-8", newline="\n"),
                  ensure_ascii=False, indent=2)
        idx.setdefault("dsh", {})[key] = s["mtime"]
        new_or_changed += 1
    _save_index(idx)
    print("== SYNC-ALL 导出 ==")
    print("新同步: %d 个 DSH 文件 → %s" % (new_or_changed, SYNC_DIR))
    print("共享目录: %s" % SYNC_DIR)
    return 0


def cmd_watch(interval: int = 60) -> int:
    """监听 DSH storages 变更并增量导出。"""
    print("SYNC-ALL watch: 每 %ds 检测 DSH storages 变更 (Ctrl+C 退出)" % interval)
    try:
        while True:
            cmd_export()
            time.sleep(interval)
    except KeyboardInterrupt:
        print("\nSYNC-ALL watch 已停止")
    return 0


def main() -> int:
    args = sys.argv[1:]
    if not args or args[0] == "--status":
        return cmd_status()
    if args[0] == "--export":
        return cmd_export()
    if args[0] == "--watch":
        iv = int(args[1]) if len(args) > 1 else 60
        return cmd_watch(iv)
    print(__doc__)
    return 1


if __name__ == "__main__":
    sys.exit(main())
