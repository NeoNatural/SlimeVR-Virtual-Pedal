#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Mar  2 15:51:04 2025

@author: liang
"""
# from gevent import monkey
# monkey.patch_all()

from pythonosc import osc_server
from pythonosc.dispatcher import Dispatcher

from pyquaternion import Quaternion

from scipy.spatial.transform import Rotation

from collections import deque

import time
# import pyautogui

# import ctypes

import mido

# In[]

MAX_LEN = 20

BUFF_SIZE = 4

THRES_FACTOR = 0.4

MUL_FACTOR = MAX_LEN * THRES_FACTOR

SAMPLE_TIME = 0.012 # in seconds, roughly measured by visual

PAUSE_INTERVAL = 0.1#MAX_LEN * SAMPLE_TIME * 2

# In[]


def print_rotation(addr,*angles):
    # print(addr)
    # print(angles)
    global last_quat
    global summ
    global is_pause
    global pause_time
    # global last_time
    
    quat = Rotation.from_euler('zxy', angles,degrees=True).as_quat(scalar_first=True)
    
    quat = Quaternion(*quat)
    
    if last_quat is not None:
        angle = (quat * last_quat.inverse).angle
        # print(angle)
        left = _queue.popleft()
        summ = summ - left + angle
        _queue.append(angle)
        
        last_quat = quat
     
        if not is_pause:
            #abs(summ/MAX_LEN) > 2 and 
            if abs(summ/MAX_LEN) > 0.15 and abs(summ) > abs(sum([_queue[-1-i] for i in range(BUFF_SIZE)])) * MUL_FACTOR:
                is_pause = True
                pause_time = time.time()
                
                # pyautogui.press('a')
                
                # send_key(ord('C'))
                print('突然停止, 平均角速度为: ',summ/MAX_LEN)
                
                
                # 4/0
        elif time.time() - pause_time >= PAUSE_INTERVAL:
            is_pause = False
            
        
        # tmp = np.array(_queue)
        
        # now_time = time.time()
        # time_diff = now_time  - last_time
        # last_time = now_time
        # print('time diff: ',time_diff)
    else:
        last_quat = quat
        # last_time = time.time()
    
    # print(quat)
    


def print_rotation_2(addr,angle1,angle2,angle3):
    # print(addr)
    print((angle1,angle2,angle3))    

if __name__ == '__main__':
    dispatcher = Dispatcher()
    dispatcher.map('/tracking/trackers/6/rotation',print_rotation)
    
    server = osc_server.BlockingOSCUDPServer(('127.0.0.1',9000),dispatcher)
    # server = osc_server.ThreadingOSCUDPServer(('127.0.0.1',9000),dispatcher)
    
    _queue = deque(maxlen=MAX_LEN)
    for i in range(MAX_LEN):
        _queue.append(0)
    
    last_quat = None
    summ = 0
    is_pause = False
    
    server.serve_forever()
    