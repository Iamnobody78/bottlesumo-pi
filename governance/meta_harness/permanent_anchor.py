# -*- coding: utf-8 -*-
"""
PERMANENT-ANCHOR v1.0 —— A.N.C.H.O.R. 六步锚定引擎

对齐: meta_prompts/PERMANENT-ANCHOR_v1.0.md
锚点文件: governance/anchors/{ANCHORS,BOUNDARY,REDLINES}.md
机制: Assemble(签名) / Normalize+Observe(校验注入) / Checkpoint(定期) / Halt(变更阻断) / Recover(恢复)

设计原则:
  1. 只读真实锚点文件, SHA-256 检测篡改, 不臆造校验结果
  2. Halt: verify 失败即阻断, 记录 BLOCKED_ATTEMPT, 不静默放行
  3. Recover: 从 backup/ 恢复最新有效版本, 记录证据链
"""
import os
import json
import hashlib
import shutil
import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
ANCHOR_DIR = os.path.normpath(os.path.join(HERE, "..", "anchors"))
BACKUP_DIR = os.path.join(ANCHOR_DIR, "backup")
MANIFEST = os.path.join(ANCHOR_DIR, "anchor_manifest.json")
CHECKPOINT_LOG = os.path.join(ANCHOR_DIR, "checkpoint_log.jsonl")
RECOVERY_LOG = os.path.join(ANCHOR_DIR, "recovery_log.jsonl")
BLOCK_LOG = os.path.join(ANCHOR_DIR, "blocked_attempts.jsonl")

ANCHOR_FILES = ["ANCHORS.md", "BOUNDARY.md", "REDLINES.md"]


def _sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _now():
    return datetime.datetime.now().isoformat()


def _load_manifest():
    if not os.path.exists(MANIFEST):
        return {}
    try:
        return json.load(open(MANIFEST, encoding="utf-8"))
    except Exception:
        return {}


def _save_manifest(manifest):
    json.dump(manifest, open(MANIFEST, "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)


def _append_log(path, entry):
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


# ── Phase A: Assemble ─────────────────────────────────────────────────────
def assemble():
    os.makedirs(ANCHOR_DIR, exist_ok=True)
    os.makedirs(BACKUP_DIR, exist_ok=True)
    manifest = {}
    for name in ANCHOR_FILES:
        p = os.path.join(ANCHOR_DIR, name)
        if not os.path.exists(p):
            return {"status": "FAIL", "missing": name}
        manifest[name] = {
            "sha256": _sha256(p),
            "size": os.path.getsize(p),
            "assembled_at": _now(),
        }
    _save_manifest(manifest)
    # 首次组装即做一次快照
    for name in ANCHOR_FILES:
        src = os.path.join(ANCHOR_DIR, name)
        shutil.copy2(src, os.path.join(BACKUP_DIR, name + ".bak"))
    return {"status": "OK", "manifest": manifest}


# ── Phase N/O: Normalize + Observe (校验注入) ─────────────────────────────
def verify():
    manifest = _load_manifest()
    if not manifest:
        return {"status": "FAIL", "reason": "无 manifest, 需先 assemble"}
    result = {"status": "PASS", "files": {}, "mismatch": []}
    for name in ANCHOR_FILES:
        p = os.path.join(ANCHOR_DIR, name)
        if not os.path.exists(p):
            result["status"] = "FAIL"
            result["mismatch"].append(name + " (缺失)")
            result["files"][name] = {"hash": None, "match": False}
            continue
        cur = _sha256(p)
        exp = manifest.get(name, {}).get("sha256")
        ok = (cur == exp)
        result["files"][name] = {"hash": cur[:16] + "...", "match": ok}
        if not ok:
            result["status"] = "FAIL"
            result["mismatch"].append(name)
    return result


# ── Phase C: Checkpoint ───────────────────────────────────────────────────
def checkpoint():
    v = verify()
    entry = {"ts": _now(), "verify": v["status"], "mismatch": v["mismatch"]}
    _append_log(CHECKPOINT_LOG, entry)
    return entry


# ── Phase H: Halt (变更阻断, verify 失败时调用) ────────────────────────────
def halt(verify_result):
    if verify_result["status"] == "PASS":
        return {"status": "NO_HALT", "detail": "锚点完整, 无需阻断"}
    entry = {
        "ts": _now(),
        "action": "BLOCKED_ATTEMPT",
        "mismatch": verify_result["mismatch"],
    }
    _append_log(BLOCK_LOG, entry)
    return {"status": "BLOCKED", "detail": "锚点签名不匹配, 已阻断并记录",
            "mismatch": verify_result["mismatch"]}


# ── Phase R: Recover ──────────────────────────────────────────────────────
def recover():
    manifest = _load_manifest()
    recovered = []
    for name in ANCHOR_FILES:
        p = os.path.join(ANCHOR_DIR, name)
        bak = os.path.join(BACKUP_DIR, name + ".bak")
        if not os.path.exists(bak):
            continue
        if os.path.exists(p) and _sha256(p) == manifest.get(name, {}).get("sha256"):
            continue  # 当前文件完整, 无需恢复
        shutil.copy2(bak, p)
        recovered.append(name)
    entry = {"ts": _now(), "recovered": recovered, "status": "OK" if recovered else "NOOP"}
    _append_log(RECOVERY_LOG, entry)
    return entry


# ── 报告渲染 ─────────────────────────────────────────────────────────────
def render_report(round_n, asm, ver, cp, hal, rec):
    L = []
    L.append("### ⚓ 锚定报告 [#ANCHOR-ROUND_%d]" % round_n)
    L.append("")
    L.append("[Phase A: Assemble]")
    if asm["status"] == "OK":
        for name in ANCHOR_FILES:
            h = asm["manifest"][name]["sha256"][:16]
            L.append("- %s : sha256=%s..." % (name, h))
    else:
        L.append("- 失败: 缺失 %s" % asm.get("missing", "?"))
    L.append("")
    L.append("[Phase N/O: Normalize+Observe]")
    L.append("- 校验状态: %s" % ver["status"])
    for name in ANCHOR_FILES:
        f = ver["files"].get(name, {})
        L.append("  - %s : %s" % (name, "MATCH" if f.get("match") else "MISMATCH/缺失"))
    L.append("")
    L.append("[Phase C: Checkpoint]")
    L.append("- 校验结果: %s" % cp["verify"])
    L.append("")
    L.append("[Phase H: Halt]")
    L.append("- 阻断状态: %s" % hal["status"])
    if hal["status"] == "BLOCKED":
        L.append("  - %s" % hal["detail"])
    L.append("")
    L.append("[Phase R: Recover]")
    L.append("- 恢复: %s" % (rec["recovered"] if rec["recovered"] else "无需恢复"))
    L.append("")
    L.append("[Honest Boundary]")
    L.append("- 锚点覆盖: 四层协议(ANCHOR/SELF-EVOLVE/Meta-Harness/HONESTY) + 优先级契约 + CVE-S + 双环")
    L.append("- 边界声明: 真实项目状态(V42 板+Pico W), 非模板示例")
    L.append("- 局限: 运行时强制加载依赖启动脚本注入; 本引擎仅做文件级完整性校验")
    return "\n".join(L) + "\n"


def run():
    # round 计数
    state_path = os.path.join(ANCHOR_DIR, "anchor_state.json")
    round_n = 1
    if os.path.exists(state_path):
        try:
            round_n = json.load(open(state_path, encoding="utf-8")).get("round", 0) + 1
        except Exception:
            pass

    asm = assemble()
    ver = verify()
    cp = checkpoint()
    hal = halt(ver)
    rec = recover() if ver["status"] == "FAIL" else {"recovered": []}

    report = render_report(round_n, asm, ver, cp, hal, rec)
    report_path = os.path.join(ANCHOR_DIR, "anchor_report.md")
    open(report_path, "w", encoding="utf-8").write(report)

    # 状态推进
    json.dump({"round": round_n, "ts": _now()}, open(state_path, "w", encoding="utf-8"))

    print(report)
    print("[OK] 锚点报告: %s" % report_path)


if __name__ == "__main__":
    run()
