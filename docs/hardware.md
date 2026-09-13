# Hardware and memory map

[Documentation index](README.md)

## Main components

| Component | Purpose |
| --- | --- |
| WDC 65C02 | CPU |
| SCN68681C1A44 | Two UARTs, timer, GPIO for SPI and indicators |
| 16 KiB low RAM | Permanently mapped memory, stack and system structures |
| 16 × 32 KiB RAM | Banked memory; 528 KiB total including low RAM |
| AT28C64B or AT28C256 | 8 KiB ROM or four 8 KiB banks |
| IC2 | Address decoder PLD |
| IC5 | Glue logic PLD |

The original README specifies up to 14 MHz in theory, with 10 MHz as the testing target. This does not guarantee that every combination of components will operate at that frequency.

The current board uses an SCN68681C1A44 DUART, with the console configured for 38400 bit/s. Older design files and source comments may still refer to the previous XR68C681 device; check them against the populated board.

## CPU address space

| CPU addresses | Window size | Purpose |
| --- | --- | --- |
| `$0000–$3FFF` | 16 KiB | Low RAM; writes at the beginning also control banking |
| `$4000–$BFFF` | 32 KiB | Selected RAM bank, 0–15 |
| `$C000–$C00F` | 16 bytes | DUART registers |
| `$C010–$DFFF` | Remaining I/O | Reserved I/O space |
| `$E000–$FFFF` | 8 KiB | ROM; one of four banks with an AT28C256 |

`BANK_SET = $0000`: bits 0–3 select RAM and bits 4–5 select ROM. Preserve the ROM bits when changing the RAM bank. Do not switch banks while executing in the affected window without a deliberately arranged transition.

The headers reserve `$0001` as `BANK_RSVD`, but the IC2 equation decodes both `$0000/$0001`. Do not use either address as an ordinary variable. Reads return the contents of the underlying RAM.

## System RAM

| Range | Usage |
| --- | --- |
| `$0002–$000F` | Firmware zero page |
| `$0010–$001F` | Filesystem zero page according to the constants |
| `$0020–$002F` | Monitor zero page according to the constants |
| `$0030–$003F` | Avoid in portable examples: comments and constants disagree |
| `$0040–$00FF` | Application zero page in the example linker configurations |
| `$0100–$01FF` | CPU stack |
| `$0200–$023F` | Firmware variables and reserved space |
| `$0240–$029F` | RAM vector area |
| `$02A0–$02FF` | ROM switching helper code |
| `$0300–$03FF` | Input buffer |
| `$0400–$05FF` | Filesystem sector buffer |
| `$0600–$06FF` | Filename buffer |
| `$0700–$07FF` | Scratch buffer / bank copying |
| `$0800–$3FFF` | 14 KiB low RAM for applications |

The introductory table in `defines.inc` disagrees with the constants about zero page and the RAM vector boundaries. The vector boundaries above follow the linker configuration. The conservative application zero-page start follows the example configurations (`$0040`).

## Board design files

- [KiCad schematic](../design/kicad/rosco_6502.kicad_sch), [PDF schematic](../design/kicad/rosco_6502.pdf).
- [PCB](../design/kicad/rosco_6502.kicad_pcb), [KiCad project](../design/kicad/rosco_6502.kicad_pro).
- [Component CSV](../design/kicad/rosco_6502.csv), [manufacturing files](../design/CAMOutputs).
- [Firmware constants](../code/firmware/rosco_6502/inc/defines.inc), [ROM linker configuration](../code/firmware/rosco_6502/rosco_6502_32K.cfg).

Before manufacturing, check that the schematic, PCB and Gerber revisions match. The PLD source headers still say r1, whereas the hardware notice covers r4.