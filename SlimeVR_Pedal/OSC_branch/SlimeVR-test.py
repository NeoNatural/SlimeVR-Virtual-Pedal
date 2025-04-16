# -*- coding: utf-8 -*-
"""
Created on Sun Mar  2 16:37:12 2025

@author: liang
"""

from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import ThreadingOSCUDPServer
from datetime import datetime

# ANSI 清屏代码（跨平台）
CLEAR_SCREEN = "\033[H\033[J"

def handle_message(address, *args):
    # 使用 ANSI 代码清屏
    print(CLEAR_SCREEN, end='')
    
    # 格式化时间戳
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
    
    # 打印关键信息
    print(f"\n=== 最新 OSC 消息 ===")
    print(f"时间: {timestamp}")
    print(f"地址: {address}")
    print(f"参数: {', '.join(map(str, args))}")
    print("-" * 40)

def main():
    ip = "127.0.0.1"     # 服务端IP（本地即 127.0.0.1）
    port = 9001     # OSC 端口（根据实际情况修改）
    
    # 创建调度器和服务器
    dispatcher = Dispatcher()
    dispatcher.set_default_handler(handle_message)
    
    server = ThreadingOSCUDPServer((ip, port), dispatcher)
    print(f"\n=== OSC 监听器已启动 ===")
    print(f"监听地址: {ip}:{port}")
    print("-" * 40)
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print(CLEAR_SCREEN, end='')
        print("\n=== 监听器已停止 ===")

if __name__ == "__main__":
    main()