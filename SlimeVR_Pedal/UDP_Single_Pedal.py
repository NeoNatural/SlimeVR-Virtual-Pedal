import nest_asyncio
import asyncio
import struct
import mido
from scipy.spatial.transform import Rotation as R

# 允许 Jupyter 运行 asyncio 事件循环
nest_asyncio.apply()

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
MAX_ANGLE = 8  # 最大 pitch 角
PITCH_DOWN_THRESHOLD = 0.5 * MAX_ANGLE  # 进入触发区间
PITCH_UP_THRESHOLD = 0.6 * MAX_ANGLE  # 离开触发区间
is_down = False  # 状态机，跟踪是否已经触发 note_on

# UDP 相关
RESPONSE_PACKET = b'\x03Hey OVR =D 5' + b'\x00' * 56

# 存储初始姿态
initial_rotation = None


async def get_initial_rotation():
    """等待用户按 Enter 记录初始姿态"""
    global initial_rotation
    print("请保持传感器在基准位置，按 Enter 记录初始姿态...")
    input()  # 等待用户输入
    initial_rotation = None
    print("等待第一个数据包记录初始姿态...")


class UDPProtocol(asyncio.DatagramProtocol):
    """异步 UDP 服务器协议"""
    
    def datagram_received(self, data, addr):
        global initial_rotation, is_down

        if data:
            if data[3] == 3:
                self.transport.sendto(RESPONSE_PACKET, addr)
            elif data[3] == 17:
                x, y, z, w = struct.unpack(">ffff", data[14:30])
                r = R.from_quat((x, y, z, w))

                # 记录初始姿态
                if initial_rotation is None:
                    initial_rotation = r.inv()
                    print("初始姿态记录完成！")
                    return

                # 计算相对姿态
                relative_rotation = r * initial_rotation
                pitch = relative_rotation.as_euler('xyz', degrees=True)[1]  # 提取 pitch 分量

                # 迟滞比较
                if not is_down and pitch < PITCH_DOWN_THRESHOLD:
                    is_down = True
                    print("Kick DOWN! (Pitch = {:.2f}°)".format(pitch))
                    midi_output.send(note_on)
                
                elif is_down and pitch > PITCH_UP_THRESHOLD:
                    is_down = False
                    print("Raise UP! (Pitch = {:.2f}°)".format(pitch))
                    midi_output.send(note_off)

    def connection_made(self, transport):
        self.transport = transport
        print("UDP 服务器已启动，监听端口 6969...")

    def error_received(self, exc):
        print(f"UDP 错误: {exc}")

    def connection_lost(self, exc):
        print("UDP 服务器关闭。")


async def main():
    """主程序：等待用户记录初始姿态，然后运行 UDP 服务器"""
    await get_initial_rotation()
    
    loop = asyncio.get_running_loop()
    transport, protocol = await loop.create_datagram_endpoint(
        lambda: UDPProtocol(),
        local_addr=("0.0.0.0", 6969)
    )

    try:
        while True:
            await asyncio.sleep(3600)  # 让事件循环保持运行
    finally:
        transport.close()


# 运行主事件循环
asyncio.run(main())
