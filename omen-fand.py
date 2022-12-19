#!/usr/bin/env python3

import os
import signal
from time import sleep
from sys import argv

ec_file="/sys/kernel/debug/ec/ec0/io"
gpu_temp="/sys/class/hwmon/"+os.listdir('/sys/class/drm/card0/device/hwmon/')[0]+"/temp2_input"
gpu_state="/sys/class/drm/card0/device/power_state"
gpu_busy="/sys/class/drm/card0/device/gpu_busy_percent"
ipc_file="/tmp/omen-fand.PID"

fan1_offset=52 #0x34
fan2_offset=53 #0x35
bios_offset=98 #0x62
timer_offset=99 #0x63
cpu_temp_offset=87 #0x57

fan1_max=55
fan2_max=57

UpThreshold = [50, 60, 70, 80, 89, 95]
DownThreshold = [48, 58, 66, 78, 87, 93]
SpeedCurve = [20, 40, 60, 70, 85, 100]
Ambient = 0
Linear = 1
PollInterval = 1

def SigHandler(signal, frame):
    os.remove("/tmp/omen-fand.PID")
    global doLoop
    doLoop = False

def UpdateFan(speed1, speed2):
    with open(ec_file, "r+b") as ec:
        ec.seek(fan1_offset)
        ec.write(bytes([speed1]))
        ec.seek(fan2_offset)
        ec.write(bytes([speed2]))

def GetTemp():
    global cooldown
    with open(ec_file, "rb") as ec:
        ec.seek(cpu_temp_offset)
        tempc = int.from_bytes(ec.read(1), 'big')

    state = open(gpu_state, "r")
    if cooldown < 1 and state.read() != "D3cold\n":
        busy = open(gpu_busy, "r")
        if busy.read() == '0\n':
            cooldown = 8

        with open(gpu_temp, "r") as temp:
            tempg = int(temp.read())/1000
        return max(tempc, tempg)
    elif cooldown > 0:
        cooldown-=1

    return tempc

def BiosControl():
    ec = open(ec_file, "r+b")
    ec.seek(bios_offset)
    if int.from_bytes(ec.read(1), 'big') != 6:
        ec.seek(bios_offset)
        ec.write(bytes([6]))
        sleep(0.1)
        ec.seek(timer_offset)
        ec.write(bytes([0]))

signal.signal(signal.SIGTERM, SigHandler)

with open(ipc_file, "w") as ipc:
    ipc.write(str(os.getpid()))

if Linear == 1:
    DownThreshold = UpThreshold
doLoop = True
cooldown = 0
index = -1
oldspeed = -1

while doLoop:
    temp=GetTemp()
    while index != 5 and temp > UpThreshold[index+1]:
        index+=1
    while index != -1 and temp < DownThreshold[index]:
        index-=1

    if index == -1:
        speed=Ambient
    elif Linear == 0 or index == 5:
        speed=SpeedCurve[index]
    else:
        speed=SpeedCurve[index]+((SpeedCurve[index+1]-SpeedCurve[index])*(1-(UpThreshold[index+1]-temp)/(UpThreshold[index+1]-UpThreshold[index])))

    if oldspeed != speed:
        oldspeed=speed
        UpdateFan(int(fan1_max*speed/100), int(fan2_max*speed/100))

    BiosControl()
    sleep(PollInterval)
