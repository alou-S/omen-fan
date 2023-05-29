# omen-fan
- A simple utility to manually control the fans of a HP Omen laptop
- Works on various HP Omen laptop and even some Victus laptops from testing. 
- Also has a service that actively adjusts the fan speed according to tempertatures (cause the default BIOS control sucks)
- Supports enabling boost mode via sysfs
- Made and tested on an Omen 16-c0140AX

# WARNING
- Forcing this program to run on incompatible laptops may cause hardware damage. Use at your own risk.
- Max speed of the fans are configured based on the "Boost" state. Increasing them is not recommended and won't provide huge thermal beinifits.

# Documentation
- Use `omen-fan help` to see all available subcommands
- EC Probe documentation can be found at [docs/probes.md](https://github.com/alou-S/omen-fan/blob/main/docs/probes.md)
