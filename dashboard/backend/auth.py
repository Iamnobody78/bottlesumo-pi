"""认证与授权 (ARCH-ROUND 2 / GAP-3.1): JWT + 角色访问控制。

角色层级: viewer(只读) < auditor(审计+验证) < admin(策略部署+用户管理)

- JWT: HS256, 从 GOV_AUTH_SECRET 读取（未设置时用开发默认值并告警）
- 密码: passlib bcrypt
- 与 agent-governance-v2 租户打通: 见 docs/architecture/authz.md §5
  （共享 GOV_AUTH_SECRET + 角色映射表, 打通实现列 P1）
"""
import os
from datetime import datetime, timedelta
from typing import Optional

import bcrypt
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from database import get_session_factory
from models import User

# ---- 配置 ----
DEV_SECRET = "dev-only-secret-change-me"  # 生产必须设置 GOV_AUTH_SECRET
SECRET = os.getenv("GOV_AUTH_SECRET", DEV_SECRET)
if SECRET == DEV_SECRET:
    import logging
    logging.getLogger("governance.auth").warning(
        "GOV_AUTH_SECRET 未设置——使用开发默认值, 生产环境必须配置!"
    )
TOKEN_TTL_HOURS = int(os.getenv("GOV_AUTH_TTL_HOURS", "12"))
ALGORITHM = "HS256"

# 角色等级（数字越大权限越高）
ROLE_LEVEL = {"viewer": 1, "auditor": 2, "admin": 3}

bearer_scheme = HTTPBearer(auto_error=False)


# ---- 密码 (bcrypt 原生 API; passlib 1.7.4 与 bcrypt>=4.1 不兼容, 弃用) ----
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))
    except ValueError:
        return False


# ---- JWT ----
def create_token(user: User) -> str:
    payload = {
        "sub": user.username,
        "role": user.role,
        "exp": datetime.utcnow() + timedelta(hours=TOKEN_TTL_HOURS),
        "iat": datetime.utcnow(),
    }
    return jwt.encode(payload, SECRET, algorithm=ALGORITHM)


def decode_token(token: str) -> Optional[dict]:
    try:
        return jwt.decode(token, SECRET, algorithms=[ALGORITHM])
    except jwt.PyJWTError:
        return None


# ---- 依赖注入 ----
def get_db():
    """FastAPI 依赖: 会话（与既有 get_session_factory 通道一致）。"""
    factory = get_session_factory()
    db = factory()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    """从 Bearer token 解析当前用户；无效/缺失 → 401。"""
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="缺少认证凭据 (Authorization: Bearer <token>)",
        )
    payload = decode_token(credentials.credentials)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="token 无效或已过期"
        )
    user = db.query(User).filter(User.username == payload.get("sub")).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="用户不存在"
        )
    return user


def require_role(min_role: str):
    """角色门控依赖工厂: min_role 为 viewer/auditor/admin。"""
    def _checker(user: User = Depends(get_current_user)) -> User:
        if ROLE_LEVEL.get(user.role, 0) < ROLE_LEVEL.get(min_role, 99):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"权限不足: 需要 {min_role} 角色 (当前: {user.role})",
            )
        return user
    return _checker
