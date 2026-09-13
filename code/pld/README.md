# rosco_6502 PLDs

[Building and programming PLDs](../../docs/pld-firmware.md) provides the full instructions for IC2 and IC5.

| Position | Source | JEDEC | Programming script |
| --- | --- | --- | --- |
| IC2 | [ic2_address_decoder.pld](address_decoder/ic2_address_decoder.pld) | [ic2_address_decoder.jed](address_decoder/ic2_address_decoder.jed) | [burn.sh](address_decoder/burn.sh) |
| IC5 | [ic5_glue_logic.pld](glue/ic5_glue_logic.pld) | [ic5_glue_logic.jed](glue/ic5_glue_logic.jed) | [burn.sh](glue/burn.sh) |

The scripts program existing JEDEC files into ATF22V10C(UES) devices. Run each script from its own directory. After changing equations, rebuild the JEDEC files as described in the guide before programming.

[Documentation index](../../docs/README.md)