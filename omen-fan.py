#!/usr/bin/env python3

import os
from time import sleep
from sys import argv

ec_file="/sys/kernel/debug/ec/ec0/io"

fan1_offset=52 #0x34
fan2_offset=53 #0x35
bios_offset=98 #0x62
timer_offset=99 #0x63

fan1_max=55
fan2_max=57

if (os.geteuid() != 0):
    print("  This program should be run as root")
    exit()

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
        print("ERROR: Needs a boolean value (0 or 1)")
        exit()

def ParseRPM(rpm, fan, max):
    isPercent=0
    if '%' in rpm:
        rpm=rpm.replace('%', '')
        isPercent=1
    try:
        rpm=int(rpm)
    except ValueError:
        print(f"  ERROR: \'{rpm}\' is not a valid integer.")
        exit()

    if isPercent == 1 and (rpm < 0 or rpm > 100):
        print(f"  ERROR: \'{rpm}\' is not a valid percentage.")
        exit()
    elif isPercent == 1:
        return int(max*rpm/100)
    elif rpm<=max and rpm>=0:
        return int(rpm)
    else:
        print(f"  ERROR: \'{rpm}\' is not a valid RPM/100 value for Fan{fan}. Min: 0 Max: {max}")
        exit()

def NI(var):
    print("    :) Need to implement subcommand", var)

if len(argv) == 1 or argv[1] in ('help', 'h'):
    print("Usage:")
    print(f"    {argv[0]} <subcommand> <argument>")
    print(f"    {argv[0]} bios-control 1")
    print(f"    {argv[0]} b 1")

    print("\nSubcommands:")
    print("    bios-control (b)        Enable/Disable BIOS control")
    print("    configure    (c)        Configure Fan curves")
    print("    start/stop   (e/d)      Starts/Stops Fan management service")
    print("    help         (h)        Prints current dialogue")
    print("    info         (i)        Gets Fan status")
    print("    set          (s)        Set Fan Speed (Disables BIOS control)")
    print("                            Fan speed can be set in Percentage '100%' or RPM/100 '55'")
    print("    version      (v)        Gives version info")

elif argv[1] in ('bios-control', 'b'):
    if len(argv) < 3:
        print(f"Subcommand \'{argv[1]}\' needs another argument")
    else:
        BiosControl(argv[2])

elif argv[1] in ('configure', 'config', 'c'):
    NI(argv[1])

elif argv[1] in ('start', 'e'):
    NI(argv[1])

elif argv[1] in ('stop', 'd'):
    NI(argv[1])

elif argv[1] in ('info', 'i'):
    NI(argv[1])

elif argv[1] in ('set', 's'):
    if len(argv) < 3:
        print("Usage:")
        print(f"  \'{argv[0]} {argv[1]} <fan-speed>\'")
        print(f"  \'{argv[0]} {argv[1]} <fan1-speed> <fan2-speed>\'")
    elif len(argv) > 3:
        UpdateFan(ParseRPM(argv[2], 1, fan1_max), ParseRPM(argv[3], 2, fan2_max))
    else:
        UpdateFan(ParseRPM(argv[2], 1, fan1_max), ParseRPM(argv[2], 2, fan2_max))

elif argv[1] in ('version', 'v'):
    print("  Omen Fan Control v0.1")
    print("  Made and tested on Omen 16-c0xxx by alou-S")
    print("  Beta software, use at your own risk")

else:
    print(f"\'{argv[1]}\' is not a valid argument.")
    print(f"Use \'{argv[0]} help\' to get usage.")
