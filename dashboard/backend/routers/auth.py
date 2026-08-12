"""认证路由 (ARCH-ROUND 2 / GAP-3.1): 登录 / 当前用户 / 用户管理。"""
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from auth import (create_token, get_current_user, get_db, hash_password,
                  require_role, verify_password)
from models import User

router = APIRouter(prefix="/api/auth", tags=["auth"])


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    token: str
    user: dict


class UserCreate(BaseModel):
    username: str
    password: str
    role: str = "viewer"  # viewer/auditor/admin


def user_dict(u: User) -> dict:
    return {"id": u.id, "username": u.username, "role": u.role}


@router.post("/login", response_model=LoginResponse)
def login(req: LoginRequest, db: Session = Depends(get_db)):
    """登录 → JWT（成功更新 last_login）。"""
    user = db.query(User).filter(User.username == req.username).first()
    if user is None or not verify_password(req.password, user.password_hash):
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    user.last_login = datetime.utcnow()
    db.commit()
    return LoginResponse(token=create_token(user), user=user_dict(user))


@router.get("/me")
def me(user: User = Depends(get_current_user)):
    """当前用户信息（前端路由守卫用）。"""
    return user_dict(user)


@router.post("/users", status_code=201)
def create_user(
    req: UserCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_role("admin")),
):
    """创建用户（仅 admin）。"""
    if req.role not in ("viewer", "auditor", "admin"):
        raise HTTPException(status_code=422, detail="role 必须为 viewer/auditor/admin")
    if db.query(User).filter(User.username == req.username).first():
        raise HTTPException(status_code=409, detail="用户名已存在")
    user = User(username=req.username, password_hash=hash_password(req.password), role=req.role)
    db.add(user)
    db.commit()
    return user_dict(user)


@router.get("/users")
def list_users(
    db: Session = Depends(get_db),
    admin: User = Depends(require_role("admin")),
):
    """用户列表（仅 admin）。"""
    return [user_dict(u) for u in db.query(User).all()]


@router.delete("/users/{username}")
def delete_user(
    username: str,
    db: Session = Depends(get_db),
    admin: User = Depends(require_role("admin")),
):
    """删除用户（仅 admin; 测试幂等清理用）。"""
    if username == admin.username:
        raise HTTPException(status_code=422, detail="不能删除当前登录用户")
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise HTTPException(status_code=404, detail="用户不存在")
    db.delete(user)
    db.commit()
    return {"deleted": username}


def seed_admin_if_empty(db: Session) -> None:
    """首次启动种子: 若 users 空则创建 admin/admin123（生产需立即改密/设置 GOV_AUTH_SECRET）。"""
    if db.query(User).count() == 0:
        db.add(User(username="admin", password_hash=hash_password("admin123"), role="admin"))
        db.commit()
