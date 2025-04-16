# import nest_asyncio
import asyncio
import socket
import numpy as np
import mido
from scipy.spatial.transform import Rotation as R

# 允许 Jupyter 运行 asyncio 事件循环
# nest_asyncio.apply()

# 配置 MIDI 设备
for device in mido.get_output_names():
    if 'loopMIDI' in device:
        out_midi_device = device
        break
else:
    raise RuntimeError("未找到 loopMIDI 设备，请检查 MIDI 设备连接")

midi_output = mido.open_output(out_midi_device)
note_on = mido.Message('note_on', note=36, velocity=120)
note_off = mido.Message('note_off', note=36)

# 迟滞比较阈值
MAX_ANGLE = 8
PITCH_DOWN_THRESHOLD = 0.2 * MAX_ANGLE
PITCH_UP_THRESHOLD = 0.3 * MAX_ANGLE
is_down = False  # 状态机

# UDP 相关
RESPONSE_PACKET = b'\x03Hey OVR =D 5' + b'\x00' * 56
initial_rotation = None  # 初始旋转矩阵

# 创建 UDP socket，开启 SO_REUSEADDR
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind(("0.0.0.0", 6969))


async def get_initial_rotation():
    """等待用户按 Enter 记录初始姿态"""
    global initial_rotation
    print("请保持传感器在基准位置，按 Enter 记录初始姿态...")
    input()
    initial_rotation = None  # 重置初始姿态
    print("等待第一个数据包记录初始姿态...")


async def send_midi(message):
    """异步 MIDI 发送"""
    midi_output.send(message)


async def udp_server():
    """UDP 监听循环"""
    global initial_rotation, is_down
    print("UDP 服务器已启动，监听端口 6969...")

    loop = asyncio.get_running_loop()

    while True:
        data, addr = await loop.run_in_executor(None, sock.recvfrom, 64)

        if not data:
            continue

        if data[3] == 3:
            sock.sendto(RESPONSE_PACKET, addr)
        elif data[3] == 17:
            # 解析四元数（优化版）
            x, y, z, w = np.frombuffer(data[14:30], dtype=">f4")

            # 记录初始姿态
            if initial_rotation is None:
                initial_rotation = R.from_quat([x, y, z, w]).inv()  # 存储初始旋转矩阵
                print("初始姿态记录完成！")
                continue

            # 计算相对旋转
            relative_rotation = R.from_quat([x, y, z, w]) * initial_rotation
            pitch = -relative_rotation.as_euler('xyz', degrees=True)[1]  # 取 Pitch 分量

            # 迟滞比较
            if not is_down and pitch < PITCH_DOWN_THRESHOLD:
                is_down = True
                # print("Kick DOWN! (Pitch = {:.2f}°)".format(pitch))
                asyncio.create_task(send_midi(note_on))
            
            elif is_down and pitch > PITCH_UP_THRESHOLD:
                is_down = False
                # print("Raise UP! (Pitch = {:.2f}°)".format(pitch))
                #asyncio.create_task(send_midi(note_off))


async def main():
    """主程序：等待用户记录初始姿态，然后运行 UDP 服务器"""
    await get_initial_rotation()
    await udp_server()


asyncio.run(main())
