# List of EC Probes

## General Info
Most of these registers were found by monitoring using ec_probe while tweaking around in the Omen Fan Control in Windows.

Registers with * are writable and effect the system.  
Registers with ** are writable and effect the system but immediately reset.  
Registers with ~ are writable but have no visible effect on Linux systems.  
Registers with ? are writable but something effects the system and sometimes doesn't.  


## Fan related
```
0x34*   Fan 1 Speed Set     units of 100RPM  
0x2E    Fan 1 Speed %       Range 0 - 0x64 (100)
0xB1    Fan 1 Speed         Range 0 - 0x16

0x35*   Fan 2 Speed Set     units of 100RPM
0x2F    Fan 2 Speed %       Range 0 - 0x64 (100)
0xB3    Fan 2 Speed         Range 0 - 0x16 

0xEC?   Fan Boost           00 (Boost OFF), 0x0C (Boost ON)
0xF4*   Fan State           00 (Enable), 02 (Disable)
```

## Temperature and BIOS related
```
0x57    CPU Temp            int °C
0xB7    GPU Temp            int °C

0x62*   BIOS Control        00 (Enabled) , 06 (Disabled)
0x63*   Timer               Counts down from whatever set to 0.
                            Set to 0x78 (120 secs) when certian EC changes are made.
                            Resets BIOS control and other values when reaches 0.
                            
```

## Power Related
```
0x95*    Performance        Technically Performance Mode. Set to 0x31 to mitigate some
                            weird perfomance issues and throttling. 0x01 for Victus Laptops.

                            Found to be tweaked via Omen Gaming Hub when changing performance modes.
                            Ranging from 0x10 to 0x50 in Balanced mode and
                            0x11 to 0x51 in performance mode incrementing in values of 0x10.

0xBA**  Thermal Power       Seems to determine the absolute maximum Power (CPU + GPU) the laptop can consume
                            Ranges from 00 to 05 with 05 being 50 Watts.
                            Seems to momentarily effect Linux systems before being immediately reset.
```
