import socket
import struct
# from constants import c_packet_type
from scipy.spatial.transform import Rotation as R

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind(("0.0.0.0", 6969))
print("UDP bound on port 6000...")
az=b'\x03Hey OVR =D 5\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
cnt=50
while cnt:
    data, addr = s.recvfrom(64)
    #print("Receive from %s:%s" % addr)
    
    # if data == b"exit":
    #     s.sendto(b"Good bye!\n", addr)
    #     continue
    
    if(data):
        # print('Data type: ',data[3])
        if data[3]==3:
            s.sendto(az,addr)
        if(data[3]==17):
            #data=b'\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00?\x00\x00\x00?\x00\x00\x00?\x00\x00\x00?\x00\x00\x00'
            
            packet_num=struct.unpack("!Q",data[4:12])
            x=data[14:18]
            y=data[18:22]
            z=data[22:26]
            w=data[26:30]
            x=struct.unpack(">f",x)[0]
            y=struct.unpack(">f",y)[0]
            z=struct.unpack(">f",z)[0]
            w=struct.unpack(">f",w)[0]
            print('\033[2J\033[H')
            # print('Packet:',packet_num,',Quat: ',x,y,z,w)
            r = R.from_quat((x,y,z,w))
            print(r.as_euler('xyz', degrees=True))
        # cnt-=1
        # print('Data[3]:',int(data[3]),', len_data:',len(data))
    #s.sendto(b"Hello %s!\n" % data, addr)