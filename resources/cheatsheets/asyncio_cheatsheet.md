# Python Asyncio 速查表

## 基础语法

### 定义协程
```python
async def my_coroutine():
    await asyncio.sleep(1)
    return "完成"
```

### 运行协程
```python
# 顶层运行
asyncio.run(my_coroutine())

# 在async函数中
await my_coroutine()
```

---

## 并发执行

### gather - 并发执行多个协程
```python
results = await asyncio.gather(
    coro1(),
    coro2(),
    coro3()
)
```

### create_task - 创建任务
```python
task1 = asyncio.create_task(coro1())
task2 = asyncio.create_task(coro2())

result1 = await task1
result2 = await task2
```

### wait - 更灵活的等待
```python
done, pending = await asyncio.wait(
    [task1, task2],
    return_when=asyncio.FIRST_COMPLETED
)
```

---

## 延迟与超时

### sleep - 异步睡眠
```python
await asyncio.sleep(1)  # 睡眠1秒
```

### wait_for - 设置超时
```python
try:
    result = await asyncio.wait_for(coro(), timeout=5)
except asyncio.TimeoutError:
    print("超时")
```

---

## aiohttp - 异步HTTP

### GET请求
```python
import aiohttp

async with aiohttp.ClientSession() as session:
    async with session.get(url) as response:
        data = await response.text()
```

### POST请求
```python
async with aiohttp.ClientSession() as session:
    async with session.post(url, json=data) as response:
        result = await response.json()
```

### 并发请求
```python
async def fetch_all(urls):
    async with aiohttp.ClientSession() as session:
        tasks = [session.get(url) for url in urls]
        responses = await asyncio.gather(*tasks)
        return responses
```

---

## 错误处理

### try-except
```python
try:
    result = await risky_operation()
except Exception as e:
    print(f"错误: {e}")
```

### 忽略特定错误
```python
results = await asyncio.gather(
    coro1(),
    coro2(),
    return_exceptions=True  # 返回异常而不是抛出
)
```

---

## 常用模式

### 并发限制（信号量）
```python
sem = asyncio.Semaphore(10)  # 最多10个并发

async def limited_task():
    async with sem:
        await actual_work()
```

### 定时执行
```python
while True:
    await do_periodic_task()
    await asyncio.sleep(60)  # 每分钟执行一次
```

---

## 性能对比

| 操作 | 同步方式 | 异步方式 |
|------|---------|---------|
| 3个网络请求(各2s) | ~6秒 | ~2秒 |
| 10个数据库查询 | ~10秒 | ~1秒 |

**记住：异步适合I/O密集型，不适合CPU密集型！**
