# 🔐 FastAPI安全与认证

> **学习目标**：掌握JWT认证、OAuth2安全机制，保护你的API

---

## 1. 为什么需要API安全？

没有认证的API就像没有锁的门：

```python
# ❌ 危险：任何人都能访问
@app.get("/users/{user_id}/secrets")
def get_secrets(user_id: int):
    return {"secrets": "敏感数据..."}
```

我们需要：
- ✅ 用户身份验证（谁在访问？）
- ✅ 权限控制（能访问什么？）
- ✅ 数据加密（传输安全）

---

## 2. JWT认证完整实现

### 2.1 安装依赖

```bash
pip install python-jose[cryptography] python-argon2
```

### 2.2 配置与模型

```python
from datetime import datetime, timedelta
from typing import Optional
from pydantic import BaseModel
from jose import jwt, JWTError
from argon2 import PasswordHasher

# 配置
SECRET_KEY = "your-secret-key-generate-with-openssl-rand-hex-32"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# 密码哈希器（Argon2id - 2024推荐算法）
ph = PasswordHasher()

# 数据模型
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
    scopes: list[str] = []

class User(BaseModel):
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    disabled: bool = False

class UserInDB(User):
    hashed_password: str
```

### 2.3 核心认证逻辑

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm, SecurityScopes

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="token",
    scopes={
        "me": "读取当前用户信息",
        "items": "读取物品列表",
        "admin": "管理员权限"
    }
)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码（使用Argon2id）"""
    try:
        ph.verify(hashed_password, plain_password)
        return True
    except:
        return False

def hash_password(password: str) -> str:
    """哈希密码"""
    return ph.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """创建JWT令牌"""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(
    security_scopes: SecurityScopes,
    token: str = Depends(oauth2_scheme)
) -> User:
    """获取当前用户（带权限验证）"""
    if security_scopes.scopes:
        authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
    else:
        authenticate_value = "Bearer"
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无法验证凭据",
        headers={"WWW-Authenticate": authenticate_value},
    )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_scopes = payload.get("scope", "").split()
        token_data = TokenData(username=username, scopes=token_scopes)
    except JWTError:
        raise credentials_exception
    
    # 获取用户（这里用模拟数据库）
    user = get_user_from_db(token_data.username)
    if user is None:
        raise credentials_exception
    
    # 检查权限
    for scope in security_scopes.scopes:
        if scope not in token_data.scopes:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="权限不足",
                headers={"WWW-Authenticate": authenticate_value},
            )
    
    return user
```

### 2.4 API端点

```python
from fastapi import FastAPI, Security

app = FastAPI(title="安全API示例")

@app.post("/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """登录获取令牌"""
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(
        data={"sub": user.username, "scope": " ".join(form_data.scopes)},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me", response_model=User)
async def read_users_me(
    current_user: User = Security(get_current_user, scopes=["me"])
):
    """获取当前用户信息（需要me权限）"""
    return current_user

@app.get("/admin/users")
async def admin_list_users(
    current_user: User = Security(get_current_user, scopes=["admin"])
):
    """管理员查看所有用户（需要admin权限）"""
    return {"users": ["user1", "user2"]}
```

---

## 3. 安全最佳实践

### 3.1 密码安全

```python
# ✅ 使用Argon2id（2024推荐）
from argon2 import PasswordHasher
ph = PasswordHasher()

# ❌ 不要使用MD5/SHA1
# import hashlib
# hashlib.md5(password.encode()).hexdigest()  # 不安全！
```

### 3.2 令牌安全

```python
# ✅ 短期令牌 + 刷新令牌模式
ACCESS_TOKEN_EXPIRE_MINUTES = 30  # 访问令牌30分钟
REFRESH_TOKEN_EXPIRE_DAYS = 7     # 刷新令牌7天

# ✅ 使用强密钥
# openssl rand -hex 32
SECRET_KEY = "生成的64位十六进制字符串"

# ❌ 不要硬编码简单密钥
# SECRET_KEY = "secret"  # 太简单！
```

### 3.3 CORS配置

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-frontend.com"],  # ✅ 指定允许的源
    # allow_origins=["*"],  # ❌ 生产环境不要用*
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)
```

---

## 4. 学习检查清单

- [ ] 理解JWT的工作原理
- [ ] 能够实现密码哈希和验证
- [ ] 会使用OAuth2 scopes进行权限控制
- [ ] 了解安全最佳实践

---

## 继续学习

📌 **Week 1 学习顺序**：
1. ✅ 异步编程核心概念
2. ✅ Pydantic数据验证
3. ✅ FastAPI快速入门
4. ✅ FastAPI安全与认证（本教程）
5. ➡️ Docker基础入门

---

**安全不是可选项，是必需品！🔒**
