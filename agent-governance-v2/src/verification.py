"""verification — 声明验证器 (S66 重建).

契约 (S66 report):
  - VerificationResult / DeclarationValidator 协议 / NoopValidator / BaselineDeclarationValidator
  - evaluate_verified: ok 规则 (satisfied 声明) 验证失败 → action 降级 ESCALATE
  - 诚实边界: 基线只做一致性检查 (不伪称语义), 深层语义谎报留给 LLM 插槽

基线检查 (确定性):
  #1 c=0.95 矛盾声明: violation + satisfied 并存 → fail
  #2 c=0.6  无锚点声明: satisfied=true 但无 output/evidence/triggered → fail
           (拦截裸 `{"satisfied":true}`, 锚点 = 真实工作产物)
"""
from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass
class VerificationResult:
    verified: bool
    reason: str = ""
    confidence: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {"verified": self.verified, "reason": self.reason,
                "confidence": self.confidence}


class DeclarationValidator:
    """验证器协议 (可插拔, 单一接口容纳 LLM/签名等未来实现)。"""

    def verify(self, rule, body: Any) -> VerificationResult:  # pragma: no cover
        raise NotImplementedError


class NoopValidator(DeclarationValidator):
    """无验证 (S66 之前默认; 此时 declaration_only 盲点存在)。"""

    def verify(self, rule, body: Any) -> VerificationResult:
        return VerificationResult(verified=True, reason="noop", confidence=0.0)


class BaselineDeclarationValidator(DeclarationValidator):
    """确定性基线验证器: 一致性检查, 不伪称语义真伪。"""

    def verify(self, rule, body: Any) -> VerificationResult:
        module = self._module_of(rule)
        state = self._state_of(body, module)
        satisfied = bool(state.get("satisfied", False)) if state else False
        violation = state.get("violation") if state else None
        anchored = self._anchor_of(state)

        # #1 矛盾声明 (violation + satisfied 并存) — 高置信拦截
        if violation and satisfied:
            return VerificationResult(
                verified=False,
                reason="contradictory_declaration (violation + satisfied)",
                confidence=0.95,
            )
        # #2 无锚点声明 (satisfied 但无 output/evidence/triggered) — 拦截裸 satisfied
        if satisfied and not anchored:
            return VerificationResult(
                verified=False,
                reason="unanchored_declaration (satisfied without output/evidence/triggered)",
                confidence=0.6,
            )
        return VerificationResult(
            verified=True, reason="baseline consistency ok", confidence=0.8,
        )

    @staticmethod
    def _anchor_of(state: Any) -> bool:
        """有效锚点判定: output / evidence / triggered 任一非空字段。

        锚点 = 真实工作产物 (S66 seed 契约): 声明 satisfied 时必须携带
        可核验的工作产物字段, 否则视为谎报 (裸 `{"satisfied":true}`)。
        """
        if not isinstance(state, dict):
            return False
        for key in ("output", "evidence", "triggered"):
            val = state.get(key)
            if val is None:
                continue
            if isinstance(val, bool):
                if val:
                    return True
            elif isinstance(val, (list, dict, str)):
                if val:  # 非空容器/字符串
                    return True
            elif val:
                return True
        return False

    @staticmethod
    def _module_of(rule) -> str:
        parts = (rule.name or "").split("-")
        return parts[1] if len(parts) >= 3 else ""

    @staticmethod
    def _state_of(body: Any, module: str) -> Dict:
        if not module or not isinstance(body, dict):
            return {}
        state = body.get("governance", {}).get("protocols", {}).get(module, {})
        return state if isinstance(state, dict) else {}
