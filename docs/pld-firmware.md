# Building and programming PLDs

[Documentation index](README.md)

The PLDs implement hardware logic. Their JEDEC files are programmed separately from the EEPROM; building ROM does not update the PLDs.

## Device and file mapping

| Position | Function | Directory | Programming file |
| --- | --- | --- | --- |
| IC2 | Address decoder | [address_decoder](../code/pld/address_decoder) | `ic2_address_decoder.jed` |
| IC5 | Glue logic | [glue](../code/pld/glue) | `ic5_glue_logic.jed` |

Both `burn.sh` scripts use the `ATF22V10C(UES)` profile. The source files specify the `GAL22V10` architecture; this does not mean any GAL is a suitable replacement for the actual device. Check the chip markings and your board schematic.

## Files and tools

- `.pld`: source equations and pin assignments.
- `.jed`: JEDEC data for the programmer.
- `.pin`, `.chp`, `.fus`: pin, package and fuse-array reports.
- `burn.sh`: programs an existing JEDEC file without compiling it.

The checked-in JEDEC headers identify **GALasm 2.1**. Rebuilding requires GALasm. Programming requires Bash, minipro and a compatible programmer. See the [GALasm documentation](https://github.com/daveho/GALasm#readme) for syntax and options.

## Rebuild after changing the logic

From the repository root, build each PLD separately:

```sh
cd code/pld/address_decoder
galasm ic2_address_decoder.pld
```

```sh
cd code/pld/glue
galasm ic5_glue_logic.pld
```

The second block also starts from the repository root. The executable name depends on your installation: use `GALasm` instead of `galasm` if that is its name.

Compilation must finish without errors and generate the corresponding `.jed`. Review the pin reports and run `git diff -- code/pld` from the repository root to inspect changes. Do not program after a failed build: an older JEDEC file may still be present. This repository has no separate PLD Makefile.

If the equations have not changed, you can use the checked-in JEDEC files after confirming the board revision and device assignments.

## Program IC2

With board power disconnected, remove IC2 and insert it into the programmer according to its placement instructions. From the repository root:

```sh
cd code/pld/address_decoder
bash burn.sh
```

The script executes:

```sh
minipro -p 'ATF22V10C(UES)' -w ic2_address_decoder.jed
```

## Program IC5

Insert IC5 into the programmer separately. From the repository root:

```sh
cd code/pld/glue
bash burn.sh
```

The equivalent command is:

```sh
minipro -p 'ATF22V10C(UES)' -w ic5_glue_logic.jed
```

Quotes protect the parentheses in the device profile from Bash interpretation. The scripts use relative paths, so run each from its own directory.

After each operation, confirm that writing and verification completed successfully. Label the devices IC2 and IC5 to avoid mixing them up, then reinstall them in the correct orientation with board power disconnected.

## What the equations implement

IC2 selects low RAM, banked RAM, I/O, ROM, the DUART and the bank register. `BANKSEL` is active high; both `$0000` and `$0001` activate it.

IC5 generates `RD`, `WR`, `BANKCLK` and two ROM output-enable signals, and controls `RESET` and `RDY`. The source comment explains the two `BANKCLK` pulses during a write: an intermediate incorrect value is replaced by the correct value before banked RAM is used. This is an intentional timing tradeoff; changes require hardware measurements.

After installation, check ROM startup and the RAM banks. Successful JEDEC verification confirms device programming, but does not validate board timing. See [Troubleshooting](troubleshooting.md).