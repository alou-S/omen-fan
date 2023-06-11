#!/usr/bin/env python3

import os
import subprocess
import signal
import sys
import glob
from time import sleep

import click
from click_aliases import ClickAliasedGroup


ECIO_FILE = "/sys/kernel/debug/ec/ec0/io"
IPC_FILE = "/tmp/omen-fand.PID"
BOOST_FILE = glob.glob("/sys/devices/platform/hp-wmi/hwmon/*/pwm1_enable")[0]
FAN1_SPEED_FILE = glob.glob("/sys/devices/platform/hp-wmi/hwmon/*/fan1_input")[0]
FAN2_SPEED_FILE = glob.glob("/sys/devices/platform/hp-wmi/hwmon/*/fan2_input")[0]

FAN1_OFFSET = 52  # 0x34
FAN2_OFFSET = 53  # 0x35
BIOS_OFFSET = 98  # 0x62
TIMER_OFFSET = 99  # 0x63
BOOST_OFFSET = 236  # 0xEC

FAN1_SPEED_MAX = 55
FAN2_SPEED_MAX = 57
DEVICE_LIST = ["OMEN by HP Laptop 16"]


def is_root():
    if os.geteuid() != 0:
        print("  This program should be run as root")
        sys.exit(1)


def is_valid_device():
    if any(
        devices not in subprocess.getoutput(["dmidecode", "-s", "system-product-name"])
        for devices in DEVICE_LIST
    ):
        print("  ERROR: Your laptop is not in the list of supnported laptops")
        print("  You may manually force the app to run at your own risk")
        sys.exit(1)


def load_ec_module():
    if "ec_sys" not in str(subprocess.check_output("lsmod")):
        subprocess.run(["modprobe", "ec_sys", "write_support=1"], check=True)

    if not bool(os.stat(ECIO_FILE).st_mode & 0o200):
        subprocess.run(["modprobe", "-r", "ec_sys"], check=True)
        subprocess.run(["modprobe", "ec_sys", "write_support=1"], check=True)


def update_fan(speed1, speed2):
    bios_control(False)
    print(f"  Set Fan1: {speed1*100} RPM, Set Fan2: {speed2*100} RPM")
    with open(ECIO_FILE, "r+b") as ec:
        ec.seek(FAN1_OFFSET)
        ec.write(bytes([speed1]))
        ec.seek(FAN2_OFFSET)
        ec.write(bytes([speed2]))


def bios_control(enabled):
    if enabled is False:
        print("  WARNING: BIOS Fan Control Disabled")
        with open(ECIO_FILE, "r+b") as ec:
            ec.seek(BIOS_OFFSET)
            ec.write(bytes([6]))
            sleep(0.1)
            ec.seek(TIMER_OFFSET)
            ec.write(bytes([0]))
    elif enabled is True:
        print("  The BIOS now controls Fans")
        with open(ECIO_FILE, "r+b") as ec:
            ec.seek(BIOS_OFFSET)
            ec.write(bytes([0]))
            ec.seek(FAN1_OFFSET)
            ec.write(bytes([0]))
            ec.seek(FAN2_OFFSET)
            ec.write(bytes([0]))
    else:
        print("  ERROR: Needs a boolean value (0 or 1)")
        sys.exit(1)


def parse_rpm(rpm, fan, max_speed):
    is_percent = 0
    if "%" in rpm:
        rpm = rpm.replace("%", "")
        is_percent = 1
    try:
        rpm = int(rpm)
    except ValueError:
        print(f"  ERROR: '{rpm}' is not a valid integer.")
        sys.exit(1)

    if is_percent == 1 and (rpm < 0 or rpm > 100):
        print(f"  ERROR: '{rpm}' is not a valid percentage.")
        sys.exit(1)
    elif is_percent == 1:
        return int(max_speed * rpm / 100)
    elif 0 <= rpm <= max_speed:
        return int(rpm)
    else:
        print(
            f"  ERROR: '{rpm}' is not a valid RPM/100 value for Fan{fan}. Min: 0 Max: {max_speed}"
        )
        sys.exit(1)


def ni(var):
    print("    :) Need to implement subcommand", var)


is_root()
is_valid_device()
load_ec_module()


@click.group(cls=ClickAliasedGroup)
def cli():
    pass


@cli.command(name="bios-control", aliases=["b"], help="Enable/Disable BIOS control")
@click.argument("arg", type=bool)
def bios_control_cli(arg):
    bios_control(arg)


@cli.command(name="boost", aliases=["x"], help="Enables boost mode via sysfs")
@click.argument("arg", type=bool)
def boost_cli(arg):
    if arg is False:
        with open(BOOST_FILE, "r+", encoding="utf-8") as file:
            file.write("2")
    elif arg is True:
        with open(BOOST_FILE, "r+", encoding="utf-8") as file:
            file.write("0")


@cli.command(
    name="configure", aliases=["config", "c"], help="Configure Fan curves for service"
)
def configure_cli():
    ni("configure")


@cli.command(name="service", aliases=["e"], help="Start/Stop Fan management service")
@click.argument("arg", type=str)
def service_cli(arg):
    if arg in ["start", "1"]:
        if os.path.isfile(IPC_FILE):
            with open(IPC_FILE, "r", encoding="utf-8") as ipc:
                print(f"  omen-fan service is already running with PID:{ipc.read()}")
        else:
            bios_control(False)
            subprocess.Popen("omen-fand")
            print("  omen-fan service has been started")

    if arg in ["stop", "0"]:
        if os.path.isfile(IPC_FILE):
            with open(IPC_FILE, "r", encoding="utf-8") as ipc:
                try:
                    os.kill(int(ipc.read()), signal.SIGTERM)
                except ProcessLookupError:
                    print(" PID file exists without process.")
                    print(" omen-fan service was killed unexpectedly.")
                    os.remove(IPC_FILE)
                    sys.exit(1)

            print("  omen-fan service has been stopped")
            bios_control(True)
        else:
            print("  omen-fan service is not running")


@cli.command(name="info", aliases=["i"], help="Gets Fan status")
def info_cli():
    if os.path.isfile(IPC_FILE):
        with open(IPC_FILE, "r", encoding="utf-8") as ipc:
            print(f"  Service Status : Running (PID: {ipc.read()})")
    else:
        print("  Service Status : Stopped")

    with open(ECIO_FILE, "rb") as ec:
        ec.seek(BOOST_OFFSET)
        if int.from_bytes(ec.read(1), "big") == 12:
            print("  Fan Boost : Enalbed")
            print("  Fan speeds are now maxed. BIOS and User controls are ignored")
        else:
            ec.seek(BIOS_OFFSET)
            if int.from_bytes(ec.read(1), "big") == 6:
                print("  BIOS Control : Disabled")
                with open(FAN1_SPEED_FILE, "r", encoding="utf-8") as fan1:
                    print("  Fan 1 : {} RPM".format(fan1.read().replace("\n", "")))
                with open(FAN2_SPEED_FILE, "r", encoding="utf-8") as fan2:
                    print("  Fan 2 : {} RPM".format(fan2.read().replace("\n", "")))
            else:
                print("  BIOS Control : Enabled")


@cli.command(
    name="set", aliases=["s", "set"],
    help="Set Fan Speed (Disables BIOS control) \n\
    Fan speed can be set in Percentage (100%) or RPM/100 (55)",
)
@click.argument("arg1", type=str)
@click.argument("arg2", type=str, required=False)
def set_cli(arg1, arg2):
    if os.path.isfile(IPC_FILE):
        print("  WARNING: omen-fan service running, may override fan speed")
    if arg2 is None:
        update_fan(parse_rpm(arg1, 1, FAN1_SPEED_MAX), parse_rpm(arg1, 2, FAN2_SPEED_MAX))
    else:
        update_fan(parse_rpm(arg1, 1, FAN1_SPEED_MAX), parse_rpm(arg2, 2, FAN2_SPEED_MAX))


@cli.command(name="version", aliases=["v"], help="Gives version info")
def version_cli():
    print("  Omen Fan Control")
    print("  Version 0.2.0")
    print("  Made and tested on Omen 16-c0xxx by alou-S")


if __name__ == "__main__":
    cli()
