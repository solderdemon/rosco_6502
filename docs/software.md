# Developing and loading programs

[Documentation index](README.md)

RAM programs are built separately from ROM. The current ca65 examples link for execution at `$0800`, use the main firmware headers and can produce binary and Intel HEX files.

## Examples

| Directory | Purpose |
| --- | --- |
| [msg_test_ca65](../code/software/msg_test_ca65) | Simple message input and output |
| [fs_test_ca65](../code/software/fs_test_ca65) | Filesystem test |
| [fs_menushell](../code/software/fs_menushell) | Experimental filesystem utility |
| [msg_test](../code/software/msg_test), [sd_test](../code/software/sd_test), [fat_test](../code/software/fat_test) | Older VASM examples |

`fs_menushell` is not yet a complete command shell: its active path accepts input, passes it to `showdir` and exits.

## rosco CLI and emulator

Two companion projects cover the develop–upload–run loop outside this repository:

- [rosco CLI](https://github.com/solderdemon/rosco-cli) provides the `rosco` command for Linux and Windows. It creates a rosco_6502 project (a Makefile, sources and an ld65 configuration linked at `$0800`), builds it with cc65 either in Docker or on the host, uploads the binary as Intel HEX through the monitor, and shows the program's output.
- [rosco-emulator](https://github.com/solderdemon/rosco-emulator) is a MAME-based emulator with a `rosco_6502` machine: W65C02S, 16KB low RAM, 16 × 32KB RAM banks, banked ROM, XR68C681 DUART and SPI SD card. It can boot your own ROM image as well as run a program on the stock firmware.

A typical session with the CLI:

```sh
cargo install --path .          # in a rosco-cli checkout
rosco init hello --board rosco_6502 --language asm --target emulator
cd hello
rosco build
rosco run                       # in the emulator; use --hardware for the board
```

To run an existing binary directly in the emulator:

```sh
./rosco rosco_6502 -quik msg_test.bin
```

See each project's README for installation, the Docker images and all options. Validate results on the physical board as well, since the emulator does not reproduce every hardware timing detail.

## Build the test program

Use the same tools as for [ROM](rom-firmware.md), plus `srec_cat` to generate Intel HEX.

```sh
cd code/software/msg_test_ca65
make clean
make all
```

The outputs are `msg_test.bin` and `msg_test.hex`. If you only need the binary, run `make msg_test.bin`; this does not invoke `srec_cat`. Perform a clean build, especially after changing included files.

## Load through WozMon

1. Start the board without an SD boot file to enter the monitor.
2. Type `L` and press Enter.
3. Send `msg_test.hex` as text through the terminal. The loader expects Intel HEX, not XMODEM or a raw binary.
4. Wait for completion with no checksum errors.
5. Type `0800R` and press Enter.

If characters are lost during transfer, add a delay between lines in the terminal and retry. Do not run the program after a checksum error.

Useful monitor commands:

| Command | Action |
| --- | --- |
| `0800` | Inspect a byte |
| `0800.080F` | Inspect a range |
| `0800: A9 41 60` | Write bytes to RAM |
| `0800R` | Call the program at that address |
| `L` | Load Intel HEX |

## Boot from SD

The current FAT32 code searches the MBR for a partition of type `$0B` or `$0C` and checks for 512-byte sectors. Use an SDHC card with MBR partitioning and FAT32 for this boot path. exFAT, GPT and media without a partition table do not match this initialization path.

1. Back up any needed data before repartitioning or formatting the card.
2. Copy the RAM binary to the FAT32 root directory as **ROSC0DE_6502.BIN**. The character in `ROSC0DE` is the digit **0**.
3. For a test, copy and rename the built `msg_test.bin`. The boot filename exceeds 8.3 format, so preserve its full long filename.
4. Insert the card and restart the board.

The loader reads the file starting at `$0800` and executes `JSR $0800` after a successful read. The binary must not contain a load-address header. On reaching `$C000`, the reader continues at `$4000` in the next RAM bank. This does not give the application a linear address space beyond 64 KiB.

## Write your own program

Include `defines.inc` from the current firmware and use an example linker configuration. Start application zero page at `$0040`; leave system buffers and RAM vectors available to the firmware.

A minimal character output program, following normal ROM initialization:

```asm
.include "defines.inc"

.segment "CODE"
.global _start
_start:
    lda #'A'
    jsr PRINTCHAR
    rts
```

`PRINTCHAR` takes the character in A. `INPUTCHAR` waits for input and returns the character in A. For `FS_OPEN`, pass the string address with the low byte in A and the high byte in X. Check headers and implementations for other function contracts; do not assume registers are preserved.

Returning with RTS works if the program has maintained a valid stack. When using banking and the filesystem, follow the [memory map](hardware.md) and account for the [API limitations](rom-firmware.md).