"""Rule / PolicyEngine — agent-governance-v2 规则引擎基础 (S63 重建).

Rule 字段契约 (与 dashboard/backend/governance_engine.py 门面对齐):
  name / action / priority / path_pattern / method / json_path / json_pattern / origin
  (额外: level / why_exists / what_it_governs 供 MCE 自省)

PolicyEngine: 按 priority 升序返回首个命中 Rule (DENY < enforce < ok)。
"""
import fnmatch
import json
import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

ACTIONS = ("ALLOW", "ALLOW_WITH_WARNING", "DENY", "ESCALATE", "SUSPEND")


@dataclass
class Rule:
    name: str
    action: str
    priority: int = 0
    path_pattern: str = "*"
    method: str = "*"
    json_path: str = ""
    json_pattern: str = ""
    origin: str = ""
    level: str = "L0"
    why_exists: str = ""
    what_it_governs: str = ""

    def matches_path(self, path: str) -> bool:
        return self.path_pattern == "*" or fnmatch.fnmatch(path, self.path_pattern)

    def matches_method(self, method: str) -> bool:
        return self.method == "*" or (self.method or "").upper() == (method or "").upper()

    def matches_json(self, body: Any) -> bool:
        if not self.json_path:
            return True  # 无 json 条件 → 仅靠 path/method
        value = extract_json_path(body, self.json_path)
        return match_json_pattern(value, self.json_pattern)

    def match(self, path: str, method: str, body: Any) -> bool:
        return (self.matches_path(path) and self.matches_method(method)
                and self.matches_json(body))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name, "action": self.action, "priority": self.priority,
            "path_pattern": self.path_pattern, "method": self.method,
            "json_path": self.json_path, "json_pattern": self.json_pattern,
            "origin": self.origin, "level": self.level,
        }


def extract_json_path(body: Any, json_path: str) -> Any:
    """从 body 提取 `$.a.b.c` 路径值; 路径不存在返回 None。"""
    if not json_path or body is None:
        return None
    parts = json_path.lstrip("$").strip(".").split(".")
    cur = body
    for p in parts:
        if p == "":
            continue
        if isinstance(cur, dict):
            if p not in cur:
                return None
            cur = cur[p]
        else:
            return None
    return cur


def match_json_pattern(value: Any, pattern: str) -> bool:
    """把提取值序列化为紧凑 JSON 字符串, 再做正则 (支持正/负向前瞻)。"""
    if not pattern:
        return value is not None
    if value is None:
        return False
    if isinstance(value, (dict, list)):
        text = json.dumps(value, ensure_ascii=False, separators=(",", ":"))
    else:
        text = str(value)
    return re.search(pattern, text) is not None


class PolicyEngine:
    """按 priority 升序返回首个命中规则; 无命中返回 None。"""

    def __init__(self, rules: List[Rule]):
        self.rules = sorted(rules, key=lambda r: r.priority)

    def evaluate(self, path: str, method: str, body: Any) -> Optional[Rule]:
        for r in self.rules:
            if r.match(path, method, body):
                return r
        return None
