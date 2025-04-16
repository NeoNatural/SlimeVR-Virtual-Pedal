#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Mar  2 15:51:04 2025

@author: liang
"""
from pythonosc import osc_server
from pythonosc.dispatcher import Dispatcher

osc_server.BlockingOSCUDPServer.allow_reuse_address = True
osc_server.AsyncIOOSCUDPServer.allow_reuse_address = True
# from pyquaternion import Quaternion

from scipy.spatial.transform import Rotation

from collections import deque

# import time

import mido

import numpy as np

import asyncio

import nest_asyncio
nest_asyncio.apply()

# In[]
# /tracking/trackers/3 右小腿(佩戴位置：前)
# /tracking/trackers/2 左小腿(佩戴位置：前)

max_angle = 8

# In[]
def handle_right_rotaion(addr,angle0,angle1,angle2):    
    global is_down_left,is_down_right
    
    ########################## compute left pedal    
    trans = Rotation.from_euler('xyz', left_tmp,degrees=True) * down_pos_left
    
    left_angle = trans.as_euler('xyz',degrees=True)[1] 
    
    if not is_down_left and left_angle < 0.5 * max_angle:
        is_down_left = True
        # print('Kick DOWN!!')
        midi_output.send(note_on)
    
    elif is_down_left and left_angle > 0.6 * max_angle:
        is_down_left = False
        # print('Raise UP!!')
        # midi_output.send(note_off)
    
    ########################## compute right pedal
    right_tmp = np.ones(3)

    right_tmp[0] = angle2
    right_tmp[1] = angle0
    right_tmp[2] = angle1
    
    trans = Rotation.from_euler('xyz', right_tmp,degrees=True) * down_pos_right
    
    right_angle = trans.as_euler('xyz',degrees=True)[1] 
    
    if not is_down_right and right_angle < 0.5 * max_angle:
        is_down_right = True
        # print('Kick DOWN!!')
        midi_output.send(note_on)
    
    elif is_down_right and right_angle > 0.6 * max_angle:
        is_down_right = False
        # print('Raise UP!!')
        # midi_output.send(note_off)
        
    
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
    
    for device in mido.get_output_names():
        if 'loopMIDI' in device:
            out_midi_device = device
            break

    midi_output = mido.open_output(out_midi_device)

    note_on = mido.Message('note_on', note=36, velocity=120)
    note_off = mido.Message('note_off', note=36)
    
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
    
    is_down_left = True
    is_down_right = True
    
    asyncio.run(init_main())