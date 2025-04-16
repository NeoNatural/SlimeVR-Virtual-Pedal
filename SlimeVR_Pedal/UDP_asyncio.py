import nest_asyncio
nest_asyncio.apply()

import asyncio
import struct
from scipy.spatial.transform import Rotation as R

RESPONSE_PACKET = b'\x03Hey OVR =D 5\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'

class UDPProtocol(asyncio.DatagramProtocol):
    def __init__(self):
        self.cnt = 50  # 只接收50次数据

    def datagram_received(self, data, addr):
        if not self.cnt:
            return

        if data:
            if data[3] == 3:
                self.transport.sendto(RESPONSE_PACKET, addr)
            elif data[3] == 17:
                packet_num = struct.unpack("!Q", data[4:12])
                x, y, z, w = struct.unpack(">ffff", data[14:30])
                print('\033[2J\033[H')  # 清屏
                r = R.from_quat((x, y, z, w))
                print(r.as_euler('xyz', degrees=True))

        # self.cnt -= 1
        if self.cnt == 0:
            self.transport.close()

    def connection_made(self, transport):
        self.transport = transport
        print("UDP server started on port 6969...")

    def error_received(self, exc):
        print(f"Error: {exc}")

    def connection_lost(self, exc):
        print("UDP server closed.")

async def main():
    loop = asyncio.get_running_loop()
    listen = await loop.create_datagram_endpoint(
        lambda: UDPProtocol(),
        local_addr=("0.0.0.0", 6969)
    )

    transport, protocol = listen
    try:
        await asyncio.sleep(100)  # 让事件循环保持运行
    finally:
        transport.close()

asyncio.run(main())
