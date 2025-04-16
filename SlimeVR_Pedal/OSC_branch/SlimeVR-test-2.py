# -*- coding: utf-8 -*-
"""
Created on Sun Mar  2 16:37:12 2025

@author: liang
"""

from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import ThreadingOSCUDPServer
from datetime import datetime, timedelta
from collections import deque
import math

CLEAR_SCREEN = "\033[H\033[J"

DEVICE_ID = "6"
WINDOW_SIZE = 5
THRESHOLD_FACTOR = 0.3
TIMEOUT = 0.1  # 突然停止持续时间阈值（秒）

def euler_to_quaternion(roll_deg, pitch_deg, yaw_deg):
    """将 Z→X→Y 顺序的欧拉角（度数）转换为四元数"""
    roll = math.radians(roll_deg)
    pitch = math.radians(pitch_deg)
    yaw = math.radians(yaw_deg)
    
    # Z→X→Y 顺序的四元数构造
    qx = math.sin(roll / 2) * math.cos(pitch / 2) * math.cos(yaw / 2)
    qy = math.cos(roll / 2) * math.sin(pitch / 2) * math.cos(yaw / 2)
    qz = math.cos(roll / 2) * math.cos(pitch / 2) * math.sin(yaw / 2)
    qw = math.cos(roll / 2) * math.cos(pitch / 2) * math.cos(yaw / 2)
    
    return [qx, qy, qz, qw]

def compute_angular_velocity(q_current, q_previous, dt):
    """计算角速度 ω = 2 * (q_dot · q)"""
    if dt == 0:
        return [0.0, 0.0, 0.0]
    
    q_dot = [(qc - pc) / dt for qc, pc in zip(q_current, q_previous)]
    q_normalized = q_current  # 假设 q_current 是单位四元数
    
    # 叉乘计算
    omega_x = 2 * (q_dot[1] * q_normalized[2] - q_dot[2] * q_normalized[1])
    omega_y = 2 * (q_dot[2] * q_normalized[0] - q_dot[0] * q_normalized[2])
    omega_z = 2 * (q_dot[0] * q_normalized[1] - q_dot[1] * q_normalized[0])
    
    return [omega_x, omega_y, omega_z]

def main():
    ip = "127.0.0.1"
    port = 9001

    # 存储历史四元数
    history = deque(maxlen=WINDOW_SIZE)
    last_q = None
    last_time = datetime.now()
    stop_detected = False
    stop_start_time = None

    dispatcher = Dispatcher()
    dispatcher.set_default_handler(lambda addr, *args: handle_message(addr, args))

    server = ThreadingOSCUDPServer((ip, port), dispatcher)
    print(f"\n=== 监听器已启动 ===")
    print(f"监听地址: {ip}:{port}, 设备ID: {DEVICE_ID}")
    print("-" * 40)

    try:
        while True:
            server.process_receiving()
            current_time = datetime.now()
            dt = (current_time - last_time).total_seconds()

            if not stop_detected:
                if history and len(args) == 3:
                    # 解析欧拉角（度数）
                    roll_deg, pitch_deg, yaw_deg = args
                    current_q = euler_to_quaternion(roll_deg, pitch_deg, yaw_deg)
                    
                    if last_q is not None:
                        # 计算角速度
                        omega = compute_angular_velocity(current_q, last_q, dt)
                        omega_mag = math.sqrt(sum(omega**2))
                        
                        # 动态阈值计算
                        avg_omega = sum(history[-1:]) / len(history[-1:]) if history else 0.0
                        threshold = avg_omega * THRESHOLD_FACTOR
                        
                        # 判断是否触发停止
                        if omega_mag < threshold:
                            if stop_start_time is None:
                                stop_start_time = current_time
                            elif (current_time - stop_start_time).total_seconds() > TIMEOUT:
                                print(f"\n=== 设备 {DEVICE_ID} 突然停止！ ===")
                                stop_detected = True
                    
                    # 更新历史记录
                    history.append(current_q)
                    last_q = current_q.copy()
                else:
                    # 第一次接收数据或格式错误
                    pass
            
            last_time = current_time

    except KeyboardInterrupt:
        print(CLEAR_SCREEN, end='')
        print("\n=== 监听器已停止 ===")

if __name__ == "__main__":
    main()

