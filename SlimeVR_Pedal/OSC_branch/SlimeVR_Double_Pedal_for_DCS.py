# -*- coding: utf-8 -*-
"""
Created on Sat Mar  8 23:49:08 2025

@author: liang
"""

from pythonosc import osc_server
from pythonosc.dispatcher import Dispatcher

osc_server.BlockingOSCUDPServer.allow_reuse_address = True
osc_server.AsyncIOOSCUDPServer.allow_reuse_address = True

# from pyquaternion import Quaternion

from scipy.spatial.transform import Rotation

import numpy as np

from pyvjoystick import vjoy

import asyncio

import nest_asyncio
nest_asyncio.apply()

# In[]
# /tracking/trackers/3 右小腿(佩戴位置：前)
# /tracking/trackers/2 左小腿(佩戴位置：前)

max_angle = 20

# In[]

def handle_right_rotaion(addr,angle0,angle1,angle2):    
    global j
    
    ########################## compute left pedal    
    trans = Rotation.from_euler('xyz', left_tmp,degrees=True) * down_pos_left
    
    left_angle = trans.as_euler('xyz',degrees=True)[1] 
    
    ########################## compute right pedal
    right_tmp = np.ones(3)

    right_tmp[0] = angle2
    right_tmp[1] = angle0
    right_tmp[2] = angle1
    
    trans = Rotation.from_euler('xyz', right_tmp,degrees=True) * down_pos_right
    
    right_angle = trans.as_euler('xyz',degrees=True)[1] 
    
    ########################## update vJoy axes
    
    left_value = int(0x01 + 0x8000 * min(max(left_angle,0),max_angle)/max_angle)
    right_value = int(0x01 + 0x8000 * min(max(right_angle,0),max_angle)/max_angle)
    
    
    j._data.wAxisXRot = 0x8000 - left_value
    j._data.wAxisYRot = 0x8000 - right_value
    # j._data.wAxisZRot = int(-(right_value - left_value)/2 + 0x4000)
    
    j.update() 
    

def save_right_rotaion(addr,angle0,angle1,angle2):
    global right_tmp

    right_tmp[0] = angle2
    right_tmp[1] = angle0
    right_tmp[2] = angle1

def save_left_rotaion(addr,angle0,angle1,angle2):
    global left_tmp

    left_tmp[0] = angle2
    left_tmp[1] = angle0
    left_tmp[2] = angle1
    
    # print('left_tmp saved')

def print_info(addr,*data):
    print('Addr: ',addr)
    print('Data: ',data)
    print()
    
def print_trans(addr,angle0,angle1,angle2):
    tmp = np.empty(3)
    tmp[0] = angle2
    tmp[1] = angle0
    tmp[2] = angle1
    
    trans = Rotation.from_euler('xyz', tmp,degrees=True) * down_pos
    
    print('\033[2J\033[H')
    print(trans.as_euler('xyz',degrees=True))
    # print('Addr: ',addr)
    # print('Data: ',data)
    # print()

# In[] Asynio main loop

async def loop():
    # to keep the process running, otherwise it will be shut down
    while True:
        
        await asyncio.sleep(100)

async def init_main():
    server = osc_server.AsyncIOOSCUDPServer(('127.0.0.1',9000),dispatcher,asyncio.get_event_loop())

    transport, protocol = await server.create_serve_endpoint()  # Create datagram endpoint and start serving
    
    await loop()  # Enter main loop of program

    transport.close()  # Clean up serve endpoint

# In[]
if __name__ == '__main__':
    
    # initialize base pos
    left_tmp = np.ones(3)
    right_tmp = np.ones(3)
    
    dispatcher = Dispatcher()
    
    dispatcher.map('/tracking/trackers/3/rotation',save_right_rotaion)
    dispatcher.map('/tracking/trackers/2/rotation',save_left_rotaion)
    
    input('Get ready and press any key to save the [DOWN] position')
    
    server = osc_server.BlockingOSCUDPServer(('127.0.0.1',9000),dispatcher)
    
    server.handle_request()
    
    server.server_close()
    
    down_pos_left = Rotation.from_euler('xyz', left_tmp,degrees=True).inv()
    down_pos_right = Rotation.from_euler('xyz', right_tmp,degrees=True).inv()
    
    # 4/0
    
    # In[]    
    
    dispatcher = Dispatcher()
    # dispatcher.map('/tracking/trackers/*/rotation',print_info)
    
    dispatcher.map('/tracking/trackers/2/rotation',save_left_rotaion)
    dispatcher.map('/tracking/trackers/3/rotation',handle_right_rotaion)
    
    
    
    j = vjoy.VJoyDevice(1)
    
    asyncio.run(init_main())
    # server.serve()
    
    