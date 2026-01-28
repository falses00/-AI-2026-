# 🔄 Python异步编程核心概念

> **学习目标**：理解异步编程的本质，掌握协程、事件循环等核心概念

---

## 📺 推荐B站视频

在开始学习之前，推荐先观看这些高质量教程：

| UP主 | 视频标题 | 链接 |
|------|---------|------|
| 武沛齐 | Python async异步编程（asyncio必备） | https://www.bilibili.com/video/BV1dv411G7NR |
| 编程浪子 | Python异步编程从入门到精通 | https://www.bilibili.com/video/BV1wW4y1z7Bu |
| 黑马程序员 | Python进阶之异步IO | https://www.bilibili.com/video/BV1qd4y1f7p3 |

---

## 1. 为什么需要异步编程？

### 传统同步编程的问题

假设你要煮饭、洗衣服、写代码。**同步方式**是：

1. 煮饭（30分钟）→ 站在锅边等待 ⏳
2. 洗衣服（40分钟）→ 站在洗衣机旁等待 ⏳
3. 写代码（60分钟）

**总时间：130分钟**

### 异步编程的优势

**异步方式**是：

1. 启动煮饭（30分钟）
2. 启动洗衣服（40分钟）
3. 在等待期间写代码（60分钟）
4. 煮饭完成 → 收饭
5. 洗衣服完成 → 晾衣服

**总时间：约60分钟**

> **关键点**：异步编程让你在**等待I/O操作**时，可以去做其他事情，而不是傻等。

---

## 2. 同步 vs 异步代码对比

### 同步代码示例

```python
import time
import requests

def fetch_data(url):
    """同步获取数据"""
    print(f"开始获取: {url}")
    response = requests.get(url)  # 这里会阻塞！
    print(f"完成获取: {url}")
    return response.text

# 依次获取三个网页
start = time.time()
result1 = fetch_data("https://httpbin.org/delay/2")  # 等待2秒
result2 = fetch_data("https://httpbin.org/delay/2")  # 等待2秒
result3 = fetch_data("https://httpbin.org/delay/2")  # 等待2秒
end = time.time()

print(f"总耗时: {end - start:.2f}秒")  # 约6秒
```

**输出**：
```
开始获取: https://httpbin.org/delay/2
完成获取: https://httpbin.org/delay/2
开始获取: https://httpbin.org/delay/2
完成获取: https://httpbin.org/delay/2
开始获取: https://httpbin.org/delay/2
完成获取: https://httpbin.org/delay/2
总耗时: 6.23秒
```

---

### 异步代码示例

```python
import asyncio
import aiohttp
import time

async def fetch_data_async(session, url):
    """异步获取数据"""
    print(f"开始获取: {url}")
    async with session.get(url) as response:  # 不会阻塞！
        await response.text()
        print(f"完成获取: {url}")

async def main():
    async with aiohttp.ClientSession() as session:
        # 并发执行三个请求
        tasks = [
            fetch_data_async(session, "https://httpbin.org/delay/2"),
            fetch_data_async(session, "https://httpbin.org/delay/2"),
            fetch_data_async(session, "https://httpbin.org/delay/2")
        ]
        await asyncio.gather(*tasks)

start = time.time()
asyncio.run(main())
end = time.time()

print(f"总耗时: {end - start:.2f}秒")  # 约2秒！
```

**输出**：
```
开始获取: https://httpbin.org/delay/2
开始获取: https://httpbin.org/delay/2
开始获取: https://httpbin.org/delay/2
完成获取: https://httpbin.org/delay/2
完成获取: https://httpbin.org/delay/2
完成获取: https://httpbin.org/delay/2
总耗时: 2.15秒
```

> ⚡ **性能提升：3倍！** 这就是异步编程的威力。

---

## 3. 核心概念详解

### 3.1 协程（Coroutine）

**协程**是可以暂停和恢复的函数。

```python
import asyncio

async def my_coroutine():
    """这是一个协程"""
    print("开始执行")
    await asyncio.sleep(1)  # 暂停1秒，让出控制权
    print("恢复执行")
    return "完成"

# 运行协程
result = asyncio.run(my_coroutine())
print(result)
```

**关键点**：
- `async def` 定义协程
- `await` 暂停执行，等待异步操作完成
- 协程不会自动执行，需要用`asyncio.run()`或`await`

---

### 3.2 事件循环（Event Loop）

事件循环是异步编程的核心，它负责：
1. 调度协程
2. 在协程等待时切换到其他协程
3. 处理I/O事件

```python
import asyncio

async def task1():
    print("任务1开始")
    await asyncio.sleep(2)
    print("任务1完成")

async def task2():
    print("任务2开始")
    await asyncio.sleep(1)
    print("任务2完成")

async def main():
    # 创建两个任务，事件循环会自动调度
    await asyncio.gather(task1(), task2())

asyncio.run(main())
```

**输出**：
```
任务1开始
任务2开始
任务2完成  # 1秒后
任务1完成  # 2秒后
```

---

### 3.3 Task（任务）

Task是对协程的封装，可以并发执行：

```python
import asyncio

async def fetch_user(user_id):
    print(f"获取用户{user_id}...")
    await asyncio.sleep(1)
    return f"用户{user_id}的数据"

async def main():
    # 创建多个任务
    task1 = asyncio.create_task(fetch_user(1))
    task2 = asyncio.create_task(fetch_user(2))
    task3 = asyncio.create_task(fetch_user(3))
    
    # 等待所有任务完成
    results = await asyncio.gather(task1, task2, task3)
    print(results)

asyncio.run(main())
```

---

## 4. 常用API速查

### 基本操作

| API | 说明 | 示例 |
|-----|------|------|
| `async def` | 定义协程 | `async def my_func():` |
| `await` | 等待异步操作 | `await asyncio.sleep(1)` |
| `asyncio.run()` | 运行协程 | `asyncio.run(main())` |

### 并发控制

| API | 说明 | 示例 |
|-----|------|------|
| `asyncio.gather()` | 并发执行多个协程 | `await asyncio.gather(task1, task2)` |
| `asyncio.create_task()` | 创建任务 | `task = asyncio.create_task(coro)` |
| `asyncio.wait()` | 等待多个任务 | `await asyncio.wait(tasks)` |

### 延迟与超时

| API | 说明 | 示例 |
|-----|------|------|
| `asyncio.sleep()` | 异步睡眠 | `await asyncio.sleep(1)` |
| `asyncio.wait_for()` | 设置超时 | `await asyncio.wait_for(coro, timeout=5)` |

---

## 5. 实战练习

### 练习1：基础协程

编写一个协程，模拟下载文件的过程：

```python
import asyncio

async def download_file(filename, size_mb):
    """
    模拟下载文件
    
    Args:
        filename: 文件名
        size_mb: 文件大小（MB）
    """
    print(f"开始下载: {filename} ({size_mb}MB)")
    # TODO: 使用asyncio.sleep模拟下载时间（每MB需要0.1秒）
    # TODO: 打印下载完成信息
    # TODO: 返回文件名

# TODO: 运行这个协程
```

<details>
<summary>▶ 点击查看答案</summary>

```python
async def download_file(filename, size_mb):
    print(f"开始下载: {filename} ({size_mb}MB)")
    await asyncio.sleep(size_mb * 0.1)
    print(f"下载完成: {filename}")
    return filename

asyncio.run(download_file("video.mp4", 100))
```
</details>

---

### 练习2：并发下载

同时下载3个文件，比较总时间：

```python
async def main():
    files = [
        ("file1.txt", 10),
        ("file2.mp4", 50),
        ("file3.zip", 30)
    ]
    
    # TODO: 使用asyncio.gather()并发下载所有文件
    # TODO: 计算总时间

# 运行main函数
```

<details>
<summary>▶ 点击查看答案</summary>

```python
import time

async def main():
    files = [
        ("file1.txt", 10),
        ("file2.mp4", 50),
        ("file3.zip", 30)
    ]
    
    start = time.time()
    tasks = [download_file(name, size) for name, size in files]
    results = await asyncio.gather(*tasks)
    end = time.time()
    
    print(f"所有文件下载完成: {results}")
    print(f"总耗时: {end - start:.2f}秒")

asyncio.run(main())
```
</details>

---

## 6. 关键要点总结

> ⚠️ **记住这些要点：**
> 
> 1. ⏳ **异步 ≠ 并行**：异步是单线程，通过切换实现"并发"
> 2. 🎯 **适用场景**：I/O密集型任务（网络请求、文件读写）
> 3. ❌ **不适用**：CPU密集型任务（图像处理、数学计算）
> 4. 🔑 **核心三要素**：`async def` + `await` + 事件循环

---

## 7. 继续学习

学完异步编程后，在左侧菜单选择下一个教程：

📌 **推荐学习顺序**：
1. ✅ 异步编程核心概念（本教程）
2. ➡️ Pydantic数据验证
3. ➡️ FastAPI快速入门
4. ➡️ Docker基础入门

---

**记住：异步编程一开始会觉得奇怪，多写几次就熟悉了！💪**
