"""
Week 1 练习题：Python异步编程 + FastAPI

运行方式:
    cd "i:\Study FastAPI"
    D:\Anaconda\envs\pytorch_Gpu\python.exe week1/exercises/async_exercises.py
"""

import asyncio
import time


# ============================================================
# 练习1：基础协程
# ============================================================

async def count_down(name: str, seconds: int):
    """
    练习1：倒计时协程
    
    TODO: 实现一个倒计时功能
    - 每秒打印剩余时间
    - 使用 asyncio.sleep 实现等待
    """
    # 你的代码
    pass


# ============================================================
# 练习2：并发执行
# ============================================================

async def download_file(filename: str, size_mb: int) -> str:
    """模拟下载文件（每MB需要0.1秒）"""
    print(f"开始下载: {filename} ({size_mb}MB)")
    await asyncio.sleep(size_mb * 0.1)
    print(f"完成下载: {filename}")
    return filename


async def exercise_2_concurrent_download():
    """
    练习2：并发下载
    
    TODO: 使用 asyncio.gather 同时下载以下3个文件，并计算总时间
    - ("video.mp4", 50)
    - ("music.mp3", 20)
    - ("document.pdf", 10)
    
    提示：同步下载需要8秒，并发应该只需5秒左右
    """
    files = [
        ("video.mp4", 50),
        ("music.mp3", 20),
        ("document.pdf", 10)
    ]
    
    # TODO: 实现并发下载
    pass


# ============================================================
# 练习3：超时控制
# ============================================================

async def slow_operation():
    """一个很慢的操作"""
    await asyncio.sleep(10)
    return "完成"


async def exercise_3_timeout():
    """
    练习3：超时控制
    
    TODO: 使用 asyncio.wait_for 给 slow_operation 设置3秒超时
    - 如果超时，捕获异常并打印 "操作超时"
    - 如果成功，打印结果
    """
    # TODO: 实现超时控制
    pass


# ============================================================
# 参考答案
# ============================================================

async def _answer_1(name: str, seconds: int):
    """练习1答案"""
    for i in range(seconds, 0, -1):
        print(f"{name}: {i}秒")
        await asyncio.sleep(1)
    print(f"{name}: 完成!")


async def _answer_2():
    """练习2答案"""
    files = [
        ("video.mp4", 50),
        ("music.mp3", 20),
        ("document.pdf", 10)
    ]
    
    start = time.time()
    tasks = [download_file(name, size) for name, size in files]
    results = await asyncio.gather(*tasks)
    end = time.time()
    
    print(f"下载完成: {results}")
    print(f"总时间: {end - start:.2f}秒")


async def _answer_3():
    """练习3答案"""
    try:
        result = await asyncio.wait_for(slow_operation(), timeout=3)
        print(f"结果: {result}")
    except asyncio.TimeoutError:
        print("操作超时")


# ============================================================
# 运行入口
# ============================================================

if __name__ == "__main__":
    print("=" * 60)
    print("Week 1 练习题：Python异步编程")
    print("=" * 60)
    
    print("\n✅ 运行练习1答案演示：")
    asyncio.run(_answer_1("计时器", 3))
    
    print("\n✅ 运行练习2答案演示：")
    asyncio.run(_answer_2())
    
    print("\n✅ 运行练习3答案演示：")
    asyncio.run(_answer_3())
    
    print("\n" + "=" * 60)
    print("完成练习后，继续学习下一个教程！")
    print("=" * 60)
