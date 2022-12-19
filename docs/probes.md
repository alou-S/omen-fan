# List of EC Probes

## General Info
Most of these registers were found by monitoring using ec_probe while tweaking around in the Omen Fan Control in Windows.

Registers with * are writable and effect the system.  
Registers with ** are writable and effect the system but immediately reset.  
Registers with ~ are writable but have no visible effect on Linux systems.  
Registers with ? are writable but something effects the system and somtimes doesn't.


## Fan related
```
0x34*   Fan 1 Speed Set     units of 100RPM  
0x2E    Fan 1 Speed %       Range 0 - 100  
0xB1    Fan 1 Speed         Range 0 - 16

0x35*   Fan 2 Speed Set     units of 100RPM  
0x2F    Fan 2 Speed %       Range 0 - 100  
0xB3    Fan 2 Speed         Range 0 - 16

0xEC?   Fan Boost           00 (Boost OFF), 12 (Boost ON)
0xF4*   Fan State           00 (Enable), 02 (Disable)
```
## Temperature and BIOS related
```
0x57    CPU Temp            int °C
0xB7    GPU Temp            int °C

0x62*   BIOS Control        00, 01  
0x63*   Timer               Counts down from whatever set to 0.
                            Resets BIOS control and other values when reaches 0.
```

## Power Related
```
0x95~    Performance    
```