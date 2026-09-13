# Troubleshooting

[Documentation index](README.md)

## Build tools and programmer

| Symptom | Check |
| --- | --- |
| `ca65`, `ld65` or `da65` not found | cc65 must be on PATH in the current Bash environment |
| Make cannot find Bash, cat or rm | The Makefile requires Unix utilities; a plain PowerShell environment is insufficient |
| `srec_cat` not found | Required for `.hex`; an individual `.bin` target can be built without it |
| Output does not change after editing | Run `make clean`, then the desired target separately; include dependencies are incomplete |
| Warning about `S_INCLUDES` | This variable is undefined in the ROM Makefile; use a clean build |
| Link failure or ROM overflow | Inspect the `.map`, selected cfg and segment sizes |
| minipro cannot find the programmer | USB connection and access from the environment running minipro |
| minipro does not recognize the profile | Support for the exact device; do not substitute a similar name |
| PLD script cannot find JEDEC | Run from the directory containing the corresponding `burn.sh` |
| Write or verification failure | Orientation, contacts, profile and correct file for the device |

## Board and terminal

| Symptom | Check |
| --- | --- |
| No output | 5 V power, JP1/JP2, UART A, TX/RX/GND, ROM and IC2/IC5 placement |
| Garbled text | 38400, 8N1, flow control disabled and common ground |
| Unexpected Enter or line display behavior | Send one CR and display received CR as CRLF |
| Incorrect ROM detection | EEPROM model, complete image, four-bank order and bank selection lines |
| RAM bank test failure | IC2, IC5, bank register, RAM and solder joints on the relevant signals |
| Hang when calling screen APIs | `CLRSCR`, `MOVEXY` and `SETCURSOR` jump to themselves in the current RAM table |
| Intel HEX CRC errors | Add a line delay, use text transfer and reload |

## SD and FAT32

The boot code's `not found` message can arise at different stages: SD initialization, FAT32 initialization or file opening. Check them in order: card → MBR/FAT32 → full filename → valid binary for `$0800`.

`FS_ZP_ERRORCODE` values are defined in [defines.inc](../code/firmware/rosco_6502/inc/defines.inc):

| Code | Meaning |
| --- | --- |
| 0 | No error |
| 1 | MBR signature check failed |
| 2 | FAT32 partition not found |
| 3 | Invalid BPB |
| 4 | Invalid RootEntCnt |
| 5 | Invalid TotalSec16 |
| 6 | Sector size is not 512 bytes |
| 7 | Media access error |
| 8 | Path too long |
| 9 | File or path not found |
| 10 | Read past end of file |
| 11 | Read extends beyond the last RAM bank |

The filesystem stores state in system RAM and zero page. If your program overwrites those areas, check its linker configuration. The existence of `BD_WRITE` does not imply support for writing FAT32 files.

## Reporting a problem

Include the board revision, ROM and PLD models, repository commit (`git rev-parse HEAD`), build command, complete error output and UART startup log. For programming failures, include the programmer model and selected profile. For failures after a code change, include the relevant diff and map file.