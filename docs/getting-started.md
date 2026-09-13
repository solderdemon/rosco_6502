# Getting started

[Documentation index](README.md)

## What you need

Prepare an assembled board of the appropriate revision, programmed IC2 and IC5 devices, an EEPROM containing the matching ROM image, a 5 V DC supply and a UART adapter with logic levels compatible with the board schematic. Check connector pin assignments and orientation against the [schematic](../design/kicad/rosco_6502.pdf) and your board markings.

For an unprogrammed board, complete [PLD programming](pld-firmware.md), then [ROM programming](rom-firmware.md). Insert and remove ICs only with board power disconnected.

## Power

- Supply external 5 V DC through J6 or J7. J7 requires a centre-positive plug.
- Leave JP1 and JP2 open when using external power.
- When powering through FTDI, close only the JP1 or JP2 jumper corresponding to the connected module.
- Do not close both jumpers or combine FTDI power with an external supply.
- The r4 notice requires the FTDI power source to provide at least 400 mA for the main board alone. Peripherals need additional current.

See [Revision 4 notes](revision-4.md) for the complete notices.

## Terminal setup

The current board uses an SCN68681C1A44 DUART. The firmware's main console uses UART A. Connect adapter TX to board RX, adapter RX to board TX, and a common ground, checking the pins against the schematic. Connect the power line only as required by your chosen power arrangement.

| Setting | Value |
| --- | --- |
| Baud rate | 38400 bit/s |
| Data, parity, stop bits | 8N1 |
| Flow control | Disabled |
| Enter key | Send a single CR |
| Received CR display | CRLF |
| Emulation | VT100/ANSI for control sequences |

UART A and B are initialized in [bank0.s](../code/firmware/rosco_6502/bank0.s). Its baud-rate comments still say `115k2` from the previous UART configuration; use the 38400 bit/s terminal setting above for the current SCN68681C1A44 board. The console RAM vector routes output to UART A.

## Check startup

1. Open the serial port in your terminal and power on the board.
2. Check the startup banner, memory information and RAM bank test result. This is a brief test of bank endpoints, not a complete memory test.
3. Without a usable SD card or boot file, the firmware should enter WozMon.
4. Enter `0800.080F` followed by Enter to inspect a range of RAM.
5. Load a [test program](software.md).

If the banner is missing or characters are corrupted, see [Troubleshooting](troubleshooting.md).