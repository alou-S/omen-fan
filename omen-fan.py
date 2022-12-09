#!/usr/bin/env python3

import os
import subprocess
import signal
from time import sleep
from sys import argv

ec_file="/sys/kernel/debug/ec/ec0/io"
ipc_file="/tmp/omen-fand.PID"

fan1_offset=52 #0x34
fan2_offset=53 #0x35
bios_offset=98 #0x62
timer_offset=99 #0x63

fan1_max=55
fan2_max=57

if (os.geteuid() != 0):
    print("  This program should be run as root")
    exit(1)

def UpdateFan(speed1, speed2):
    BiosControl('0')
    print(f"  Set Fan1: {speed1*100} RPM, Set Fan2: {speed2*100} RPM")
    with open(ec_file, "r+b") as ec:
        ec.seek(fan1_offset)
        ec.write(bytes([speed1]))
        ec.seek(fan2_offset)
        ec.write(bytes([speed2]))

def BiosControl(enabled):
    if enabled == '0':
        print("  WARNING: BIOS Fan Control Disabled")
        with open(ec_file, "r+b") as ec:
            ec.seek(bios_offset)
            ec.write(bytes([6]))
            sleep(0.1)
            ec.seek(timer_offset)
            ec.write(bytes([0]))
    elif enabled == '1':
        print("  The BIOS now controls Fans")
        with open(ec_file, "r+b") as ec:
            ec.seek(bios_offset)
            ec.write(bytes([0]))
            ec.seek(fan1_offset)
            ec.write(bytes([0]))
            ec.seek(fan2_offset)
            ec.write(bytes([0]))
    else:
        print("  ERROR: Needs a boolean value (0 or 1)")
        exit(1)

def ParseRPM(rpm, fan, max):
    isPercent=0
    if '%' in rpm:
        rpm=rpm.replace('%', '')
        isPercent=1
    try:
        rpm=int(rpm)
    except ValueError:
        print(f"  ERROR: \'{rpm}\' is not a valid integer.")
        exit(1)

    if isPercent == 1 and (rpm < 0 or rpm > 100):
        print(f"  ERROR: \'{rpm}\' is not a valid percentage.")
        exit(1)
    elif isPercent == 1:
        return int(max*rpm/100)
    elif rpm<=max and rpm>=0:
        return int(rpm)
    else:
        print(f"  ERROR: \'{rpm}\' is not a valid RPM/100 value for Fan{fan}. Min: 0 Max: {max}")
        exit(1)

def NI(var):
    print("    :) Need to implement subcommand", var)

if len(argv) == 1 or argv[1] in ('help', 'h'):
    print("Usage:")
    print(f"    omen-fan <subcommand> <argument>")
    print(f"    omen-fan bios-control 1")
    print(f"    omen-fan b 1")

    print("\nSubcommands:")
    print("    bios-control (b)        Enable/Disable BIOS control")
    print("    configure    (c)        Configure Fan curves for service")
    print("    start/stop   (e/d)      Starts/Stops Fan management service")
    print("    help         (h)        Prints current dialogue")
    print("    info         (i)        Gets Fan status")
    print("    set          (s)        Set Fan Speed (Disables BIOS control)")
    print("                            Fan speed can be set in Percentage '100%' or RPM/100 '55'")
    print("    version      (v)        Gives version info")

elif argv[1] in ('bios-control', 'b'):
    if len(argv) < 3:
        print(f"  Subcommand \'{argv[1]}\' needs another argument")
    else:
        BiosControl(argv[2])

elif argv[1] in ('configure', 'config', 'c'):
    NI(argv[1])

elif argv[1] in ('start', 'e'):
    if(os.path.isfile(ipc_file)):
        ipc = open(ipc_file, "r")
        print(f"  omen-fan service is already running with PID:{ipc.read()}")
    else:
        BiosControl('0')
        subprocess.Popen('omen-fand')
        print("  omen-fan service has been started")

elif argv[1] in ('stop', 'd'):
    if(os.path.isfile(ipc_file)):
        ipc = open(ipc_file, "r")
        
        try:
            os.kill(int(ipc.read()), signal.SIGTERM)
        except ProcessLookupError:
            print(" PID file exists without process.")
            print(" omen-fan service was killed unexpectedly.")
            os.remove("/tmp/omen-fand.PID")
            exit(1)

        print("  omen-fan service has been stopped")
        BiosControl('1')
    else:
        print("  omen-fan service is not running")
        

elif argv[1] in ('info', 'i'):
    if(os.path.isfile(ipc_file)):
        ipc = open(ipc_file, "r")
        print(f"  Service Status : Running (PID: {ipc.read()})")
    else:
        print("  Service Status : Stopped")
    
    ec = open(ec_file, "rb")
    ec.seek(bios_offset)
    if(int.from_bytes(ec.read(1), 'big') == 6):
        print("  BIOS Control : Disabled")
        ec.seek(fan1_offset)
        print(f"  Fan 1 : {int.from_bytes(ec.read(1), 'big') * 100} RPM")
        ec.seek(fan2_offset)
        print(f"  Fan 2 : {int.from_bytes(ec.read(1), 'big') * 100} RPM")
    else:
        print("  BIOS Control : Enabled")

elif argv[1] in ('set', 's'):
    if len(argv) < 3:
        print("Usage:")
        print(f"  \'omen-fan {argv[1]} <fan-speed>\'")
        print(f"  \'omen-fan {argv[1]} <fan1-speed> <fan2-speed>\'")
    elif len(argv) > 3:
        UpdateFan(ParseRPM(argv[2], 1, fan1_max), ParseRPM(argv[3], 2, fan2_max))
    else:
        UpdateFan(ParseRPM(argv[2], 1, fan1_max), ParseRPM(argv[2], 2, fan2_max))

elif argv[1] in ('version', 'v'):
    print("  Omen Fan Control v0.1")
    print("  Made and tested on Omen 16-c0xxx by alou-S")
    print("  Beta software, use at your own risk")

else:
    print(f"  \'{argv[1]}\' is not a valid argument.")
    print(f"  Use \'omen-fan help\' to get usage.")
