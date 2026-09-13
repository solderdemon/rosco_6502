# Building and programming ROM

[Documentation index](README.md)

The main firmware is in [code/firmware](../code/firmware). It initializes the DUART, timer and RAM vectors, checks memory banks and attempts to load a program from SD. If loading fails or the program returns with RTS, execution enters WozMon.

## Tools

You need `ca65`, `ld65` and `da65` from cc65, GNU Make, Bash, `cat` and `rm`. Programming also requires `minipro` and a programmer supporting the specific EEPROM. On Windows, run the commands in a Bash environment; USB programmer access must be configured separately.

Check tool availability in Bash:

```sh
command -v make bash ca65 ld65 da65 cat rm
command -v minipro
```

## Choose an image

| EEPROM | Image | Size | Programming target |
| --- | --- | --- | --- |
| AT28C64B | `boot8k.bin` | 8192 bytes | `make burn8` |
| AT28C256 | `boot32k.bin` | 32768 bytes | `make burn32` |

ROM appears at CPU address `$E000`, but the image is programmed from EEPROM offset 0. A RAM program intended for SD boot is not a ROM image.

## Build

From the repository root:

```sh
cd code/firmware
make clean
make all
wc -c boot8k.bin boot32k.bin
```

To build only one variant, run `make boot8k.bin` or `make boot32k.bin` after `make clean`.

Clean before rebuilding: the assembly rule references `S_INCLUDES`, but the Makefile does not define it. Editing an included `.s` or `.inc` file may therefore fail to trigger an object rebuild.

The 32 KiB image concatenates `boot32k.0.bin`, `boot32k.1.bin`, `boot32k.2.bin` and `boot32k.3.bin` in that order. Each bank is 8192 bytes. Program the combined `boot32k.bin` into an AT28C256.

Other outputs are `.lst` listings, `.sym` symbols, `.map` linker maps and `.dis` disassemblies. Existing files without the `.bin` extension do not replace the output of a clean build.

## Program the EEPROM

1. Disconnect board power, remove the EEPROM and check its markings.
2. Insert the EEPROM into the programmer using its placement guide and pin 1 orientation.
3. From the firmware directory, run only the target for the installed chip:

```sh
# AT28C64B, 8 KiB
make burn8
```

or:

```sh
# AT28C256, 32 KiB
make burn32
```

These Makefile targets execute the following commands respectively:

```sh
minipro -p AT28C64B -s -w boot8k.bin
minipro -p AT28C256 -s -w boot32k.bin
```

The commands are alternatives for different chips. Check the programmer's write and verification results before reinstalling the EEPROM. If your minipro version does not recognize the required chip, do not substitute another device profile.

4. Reinstall the EEPROM in the correct orientation with board power disconnected.
5. Follow [Getting started](getting-started.md). Startup code attempts to detect the ROM bank count. An incorrect result calls for checking the image and hardware bank selection.

## Source layout

| File | Responsibility |
| --- | --- |
| [bank0.s](../code/firmware/bank0.s) | Reset, initialization, checks and SD boot |
| [bank1.s](../code/firmware/bank1.s), [bank2.s](../code/firmware/bank2.s), [bank3.s](../code/firmware/bank3.s) | Other ROM banks |
| [common.s](../code/firmware/common.s), [vectors.s](../code/firmware/vectors.s) | Common code and CPU vectors |
| [romtable.s](../code/firmware/romtable.s), [ramtable.s](../code/firmware/ramtable.s) | Call tables and bank transitions |
| [duart_spi.s](../code/firmware/duart_spi.s), [sd_card.s](../code/firmware/sd_card.s) | SPI and SD |
| [fat32_readonly.s](../code/firmware/fat32_readonly.s) | FAT32 reading |
| [wozmon.s](../code/firmware/wozmon.s) | Monitor and Intel HEX loader |

The `rosco_6502_8K.cfg` and `rosco_6502_32K.cfg` linker configurations define the layout. CPU vectors start at `$FFFA`. Common regions must retain matching addresses across all banks.

## Limitations

The ROM table routes `FAT_READ`, `FAT_SEEK`, `FAT_WRITE` and `FAT_CLOSE` to a stub. Use implemented operations such as `FS_READBYTE` and `FS_READFILE` for reading. The current `CLRSCR`, `MOVEXY` and `SETCURSOR` RAM vectors jump to themselves; calling them directly can hang execution.