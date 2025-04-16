# -*- coding: utf-8 -*-
"""
Created on Wed Mar  5 18:15:41 2025

@author: liang
"""

import mido
import time

out_midi_device = 'loopMIDI 1'

midi_output = mido.open_output(out_midi_device)

note_on = mido.Message('note_on', note=36, velocity=127)



note_off = mido.Message('note_off', note=36, velocity=120)

while(True):
    midi_output.send(note_on)
    time.sleep(0.5)
    # midi_output.send(note_off)
    time.sleep(1)