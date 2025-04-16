# SlimeVR-Virtual-Pedal
Use SlimeVR trackers to act as virtual pedals, for like driving pedals, airplane rudder and drum kick midi signal.

# Dependencies on external softwares
+ You will need to install python with several packages to run the scripts. 
+ To use with drum kick midi output, *loopMIDI* is required. 
+ To use as virtual axis for driving and flying simulators, *vJoy* is required.

# UDP and OSC version
UDP version does not require SlimeVR server, and is more efficient and low-latency. However, only MIDI usage case is implemented. Full function examples are in the OSC version. You can migrate as needed.
