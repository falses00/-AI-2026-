# 🔐 用户认证与权限管理

> **学习目标**：为企业RAG系统实现完整的认证授权体系

---

## 1. 认证系统架构

```
┌─────────────────────────────────────────────────────────────────┐
│                    企业级认证系统架构                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────┐         ┌─────────────────┐                    │
│  │   用户登录   │ ──────► │  认证服务       │                    │
│  │  (账密/SSO) │         │  (验证身份)     │                    │
│  └─────────────┘         └────────┬────────┘                    │
│                                   │                              │
│                                   ▼                              │
│                          ┌─────────────────┐                    │
│                          │  生成JWT令牌    │                    │
│                          │  (access_token) │                    │
│                          └────────┬────────┘                    │
│                                   │                              │
│                                   ▼                              │
│  ┌─────────────┐         ┌─────────────────┐                    │
│  │   API请求   │ ──────► │  权限检查       │                    │
│  │ (带Token)   │         │  (RBAC)        │                    │
│  └─────────────┘         └────────┬────────┘                    │
│                                   │                              │
│                     ┌─────────────┼─────────────┐               │
│                     ▼             ▼             ▼               │
│              ┌──────────┐  ┌──────────┐  ┌──────────┐          │
│              │  查询    │  │  上传    │  │  管理    │          │
│              │  (read)  │  │  (write) │  │  (admin) │          │
│              └──────────┘  └──────────┘  └──────────┘          │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. 数据模型设计

```python
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Table
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime

Base = declarative_base()

# 用户-角色关联表
user_roles = Table(
    'user_roles',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('role_id', Integer, ForeignKey('roles.id'))
)

# 角色-权限关联表
role_permissions = Table(
    'role_permissions',
    Base.metadata,
    Column('role_id', Integer, ForeignKey('roles.id')),
    Column('permission_id', Integer, ForeignKey('permissions.id'))
)

class User(Base):
    """用户模型"""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 关联角色
    roles = relationship("Role", secondary=user_roles, back_populates="users")

class Role(Base):
    """角色模型"""
    __tablename__ = 'roles'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(String(200))
    
    users = relationship("User", secondary=user_roles, back_populates="roles")
    permissions = relationship("Permission", secondary=role_permissions)

class Permission(Base):
    """权限模型"""
    __tablename__ = 'permissions'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)  # e.g., "documents:read"
    description = Column(String(200))
```

---

## 3. 认证服务实现

```python
from datetime import datetime, timedelta
from jose import jwt, JWTError
from argon2 import PasswordHasher
from pydantic import BaseModel
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

# 配置
SECRET_KEY = "your-secret-key-here"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

ph = PasswordHasher()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

class TokenPair(BaseModel):
    """令牌对"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class AuthService:
    """认证服务"""
    
    def __init__(self, db_session):
        self.db = db_session
    
    def hash_password(self, password: str) -> str:
        """哈希密码"""
        return ph.hash(password)
    
    def verify_password(self, password: str, hashed: str) -> bool:
        """验证密码"""
        try:
            ph.verify(hashed, password)
            return True
        except:
            return False
    
    def create_access_token(self, user_id: int, permissions: list[str]) -> str:
        """创建访问令牌"""
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        payload = {
            "sub": str(user_id),
            "permissions": permissions,
            "exp": expire,
            "type": "access"
        }
        return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    
    def create_refresh_token(self, user_id: int) -> str:
        """创建刷新令牌"""
        expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        payload = {
            "sub": str(user_id),
            "exp": expire,
            "type": "refresh"
        }
        return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    
    def create_token_pair(self, user: User) -> TokenPair:
        """创建令牌对"""
        # 收集用户权限
        permissions = set()
        for role in user.roles:
            for perm in role.permissions:
                permissions.add(perm.name)
        
        return TokenPair(
            access_token=self.create_access_token(user.id, list(permissions)),
            refresh_token=self.create_refresh_token(user.id)
        )
    
    def verify_token(self, token: str) -> dict:
        """验证令牌"""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="无效的令牌"
            )
    
    async def authenticate(self, username: str, password: str) -> User:
        """认证用户"""
        user = self.db.query(User).filter(User.username == username).first()
        if not user or not self.verify_password(password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户名或密码错误"
            )
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="用户已被禁用"
            )
        return user
```

---

## 4. 权限检查装饰器

```python
from functools import wraps
from typing import List

class PermissionChecker:
    """权限检查器"""
    
    def __init__(self, required_permissions: List[str]):
        self.required = required_permissions
    
    async def __call__(self, token: str = Depends(oauth2_scheme)):
        """检查权限"""
        payload = verify_token(token)
        user_permissions = set(payload.get("permissions", []))
        
        # 检查是否有必要权限
        for perm in self.required:
            if perm not in user_permissions:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"缺少权限: {perm}"
                )
        
        return payload

# 使用
require_read = PermissionChecker(["documents:read"])
require_write = PermissionChecker(["documents:write"])
require_admin = PermissionChecker(["admin:*"])

@app.get("/api/documents")
async def list_documents(auth: dict = Depends(require_read)):
    """列出文档（需要读权限）"""
    return {"documents": [...]}

@app.post("/api/documents")
async def upload_document(auth: dict = Depends(require_write)):
    """上传文档（需要写权限）"""
    return {"status": "uploaded"}

@app.delete("/api/documents/{doc_id}")
async def delete_document(doc_id: int, auth: dict = Depends(require_admin)):
    """删除文档（需要管理员权限）"""
    return {"status": "deleted"}
```

---

## 5. API端点实现

```python
from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter(prefix="/api/auth", tags=["认证"])

@router.post("/register")
async def register(username: str, email: str, password: str):
    """用户注册"""
    auth_service = AuthService(get_db())
    
    # 检查用户名是否存在
    existing = db.query(User).filter(User.username == username).first()
    if existing:
        raise HTTPException(status_code=400, detail="用户名已存在")
    
    # 创建用户
    user = User(
        username=username,
        email=email,
        hashed_password=auth_service.hash_password(password)
    )
    db.add(user)
    db.commit()
    
    return {"message": "注册成功"}

@router.post("/login", response_model=TokenPair)
async def login(form: OAuth2PasswordRequestForm = Depends()):
    """用户登录"""
    auth_service = AuthService(get_db())
    user = await auth_service.authenticate(form.username, form.password)
    return auth_service.create_token_pair(user)

@router.post("/refresh")
async def refresh_token(refresh_token: str):
    """刷新令牌"""
    auth_service = AuthService(get_db())
    payload = auth_service.verify_token(refresh_token)
    
    if payload.get("type") != "refresh":
        raise HTTPException(status_code=400, detail="无效的刷新令牌")
    
    user_id = int(payload["sub"])
    user = db.query(User).get(user_id)
    
    return auth_service.create_token_pair(user)

@router.get("/me")
async def get_current_user(token: str = Depends(oauth2_scheme)):
    """获取当前用户信息"""
    auth_service = AuthService(get_db())
    payload = auth_service.verify_token(token)
    user_id = int(payload["sub"])
    user = db.query(User).get(user_id)
    
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "roles": [r.name for r in user.roles],
        "permissions": payload.get("permissions", [])
    }
```

---

## 6. 预置角色和权限

```python
def init_permissions(db):
    """初始化权限数据"""
    permissions = [
        ("documents:read", "读取文档"),
        ("documents:write", "上传文档"),
        ("documents:delete", "删除文档"),
        ("chat:access", "使用对话功能"),
        ("admin:users", "管理用户"),
        ("admin:*", "超级管理员"),
    ]
    
    for name, desc in permissions:
        if not db.query(Permission).filter(Permission.name == name).first():
            db.add(Permission(name=name, description=desc))
    
    db.commit()

def init_roles(db):
    """初始化角色数据"""
    roles = {
        "viewer": ["documents:read", "chat:access"],
        "editor": ["documents:read", "documents:write", "chat:access"],
        "admin": ["documents:read", "documents:write", "documents:delete", 
                  "chat:access", "admin:users"],
        "superadmin": ["admin:*"]
    }
    
    for role_name, perm_names in roles.items():
        role = db.query(Role).filter(Role.name == role_name).first()
        if not role:
            role = Role(name=role_name)
            db.add(role)
        
        # 关联权限
        for perm_name in perm_names:
            perm = db.query(Permission).filter(Permission.name == perm_name).first()
            if perm and perm not in role.permissions:
                role.permissions.append(perm)
    
    db.commit()
```

---

## 7. 学习检查清单

- [ ] 理解RBAC权限模型
- [ ] 能够实现JWT认证
- [ ] 会设计权限检查装饰器
- [ ] 能够实现令牌刷新机制

---

## 继续学习

📌 **Week 7 学习顺序**：
1. ✅ 企业级系统架构
2. ✅ 多格式文档处理
3. ✅ 用户认证与权限（本教程）
4. ➡️ 云平台部署
