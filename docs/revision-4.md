# Revision 4 notes

[Documentation index](README.md)

This is a Markdown adaptation of **rosco_6502 Additional Information v1 (Jan 2024)** issued by The Really Old-School Company Limited. It replaces `r4 Information.docx` and `r4 Information.pdf`. The information applies to revision 4.

## JP1 and JP2

JP1 and JP2 are optional jumpers for powering the board through an FTDI module. Only one jumper may be closed at a time, and only when the board receives power from the corresponding module.

Do not close either jumper when external power is connected, and do not close both at once. Doing so may damage the board, FTDI modules, power supply and connected equipment.

The FTDI module and USB source must provide at least 400 mA for the main board alone. Insufficient power may cause incorrect operation and, in rare cases, permanent damage.

## Power connection

When not using FTDI power, supply 5 V DC through J6, the two-pin header at the bottom right of the board, or through J7, the barrel jack.

Higher voltage or incorrect polarity may permanently damage the board and peripherals. Follow the polarity markings on the board. J7 requires a centre-positive plug.

## ROM selection

The board supports an 8 KiB AT28C64B or a banked 32 KiB AT28C256. Program the standard firmware build matching the EEPROM capacity. The standard firmware detects and reports the ROM size at startup.

See the [ROM programming guide](rom-firmware.md) for commands.

## Manufacturer notices

The following preserves the substance of the manufacturer's January 2024 notices. It is not a new compliance assessment of an individually assembled board.

The manufacturer states that it has sought to make documentation accurate at the time of writing, subject to errors and omissions.

Compliance with local electromagnetic interference requirements may require a suitable grounded enclosure with application-specific shielding. The Really Old-School Company Limited neither specifies nor supplies such enclosures and recommends seeking expert guidance when selecting one.

The manufacturer does not authorize its products for safety-critical or life-support applications where a product failure could cause system failure or significantly affect system safety or effectiveness. Examples include human life support, nuclear safety and control, air-traffic control and vehicular control. Such use is not authorized under any circumstances.

According to the manufacturer, the PCBs and components it supplies comply with RoHS. Compliance of a completed kit also depends on the solder selected during assembly.

Dispose of waste in accordance with the applicable Waste Electrical and Electronic Equipment (WEEE) recycling requirements in your jurisdiction.

## Editorial notes

The original jumper warning referred to `rosco_m68k`; this adaptation uses “the board” to match the document's subject. Repeated section numbering has been replaced with headings. Power requirements and manufacturer notices have been preserved in substance.