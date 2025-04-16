#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Mar  2 15:51:04 2025

@author: liang
"""
from pythonosc import osc_server
from pythonosc.dispatcher import Dispatcher

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

# MAX_LEN = 50

# BUFF_SIZE = 4

# THRES_FACTOR = 0.25

# MUL_FACTOR = MAX_LEN * THRES_FACTOR

# SAMPLE_TIME = 0.012 # in seconds, roughly measured by visual

# PAUSE_INTERVAL = MAX_LEN * SAMPLE_TIME * 2

# In[]
        
def detect_down(addr,angle0,angle1,angle2):
    # print(addr)
    # print(angles)
    # global down_pos,max_angle
    global is_down
    
    max_angle = 8
    
    tmp = np.empty(3)
    tmp[0] = angle2
    tmp[1] = angle0
    tmp[2] = angle1
    
    trans = Rotation.from_euler('xyz', tmp,degrees=True) * down_pos
    
    _angle = trans.as_euler('xyz',degrees=True)[1] # 1 for Y axis (roll)
    
    if not is_down and _angle < 0.5 * max_angle:
        is_down = True
        # print('Kick DOWN!!')
        midi_output.send(note_on)
        return
    
    if is_down and _angle > 0.6 * max_angle:
        is_down = False
        # print('Raise UP!!')
        # midi_output.send(note_off)
        return
 
    # print('\033[2J\033[H')
    # print(trans.as_euler('xyz')/np.pi*180)
    
def save_rotaion(addr,angle0,angle1,angle2):
    global tmp
    # tmp[:] = np.array(angles)
    tmp[0] = angle2
    tmp[1] = angle0
    tmp[2] = angle1

if __name__ == '__main__':
    # In[]
    for device in mido.get_output_names():
        if 'loopMIDI' in device:
            out_midi_device = device
            break

    midi_output = mido.open_output(out_midi_device)

    note_on = mido.Message('note_on', note=36, velocity=120)
    note_off = mido.Message('note_off', note=36)
    
    # In []
    
    tmp = np.zeros(3)
    
    dispatcher = Dispatcher()
    
    dispatcher.map('/tracking/trackers/6/rotation',save_rotaion)
    
    osc_server.BlockingOSCUDPServer.allow_reuse_address = True
    osc_server.AsyncIOOSCUDPServer.allow_reuse_address = True
    
    input('Get ready and press any key to save the [DOWN] position')
    
    server = osc_server.BlockingOSCUDPServer(('127.0.0.1',9000),dispatcher)
    
    server.handle_request()
    
    server.server_close()
    
    rot1 = tmp.copy()
    
    input('Get ready and press any key to save the [UP] position')
    
    server = osc_server.BlockingOSCUDPServer(('127.0.0.1',9000),dispatcher)
    
    server.handle_request()
    server.server_close()
    rot2 = tmp.copy()
    
    down_pos = Rotation.from_euler('xyz', rot1,degrees=True).inv()
    
    base_trans = Rotation.from_euler('xyz', rot2,degrees=True) * down_pos
           
    max_angle = base_trans.as_euler('xyz',degrees=True)[1]  # 1 for Y axis (roll)
    
    assert(max_angle>0) # ensure the correct rotation direction
    
    
    # In[]
    dispatcher = Dispatcher()
    dispatcher.map('/tracking/trackers/6/rotation',detect_down)
    
    server = osc_server.AsyncIOOSCUDPServer(('127.0.0.1',9000),dispatcher,asyncio.get_event_loop())
    # count = 0
    is_down = True
    # server.serve_forever()
    server.serve()
    
    # input()