Bitstream format
================

Some documentation on the ECP5 bitstream format is published by Lattice themselves
in th ECP5 sysCONFIG Usage Guide (TN1260_).

.. _TN1260: http://www.latticesemi.com/~/media/LatticeSemi/Documents/ApplicationNotes/EH/TN1260.pdf

Basic Structure
----------------

The ECP5 is primarily byte oriented and always byte aligned. Multi-byte words are always in big endian format.

Before the start of the bitstream itself is a comment section, which starts with FF 00 and 00 FF.
Inside it are several null-terminated strings used as metadata by Lattice. The start of the bitstream
is demarcated by a preamable, 0xFFFFBDB3. This is then followed by a 0xFFFFFFFF dummy section and then the
start of functional commands.

At minimum, a bitstream command is an 8 bit command type field, then 24 bits of command information.
The MSB of command information is set to 1 if a CRC16 follows the command. The other 23 bits are command-specific,
but usually zeros. Then follows a command-specific number of payload bytes, and the CRC16 if applicable.

The CRC16 is accumulated over all commands until a CRC16 check is reached. It is not reset at the end of commands
without a CRC16 check - except the ``LSC_RESET_CRC`` command, and after the actual bitstream payload
(``LSC_PROG_INCR_RTI``).

The CRC16 is calculated using the polynomial 0x8005 with no bit reversal. This algorithm is sometimes known as
"CRC16-BUYPASS".

    NB: Lattice's documents talk about the CRC16 being flipped. This is based on standard
    CRC16 code with reversal, effectively performing double bit reversal. CRC16 code with no
    bit reversal at all matches the actual format.

Control Commands
------------------
Control commands seen in a typical uncompressed, unencrypted bitstream are:

+-------------------------------+-----+--------------------------+---------------------------------------------------+
| Command                       | Hex | Parameters               | Description                                       |
+==========================+====+=====+==========================+===================================================+
| Dummy                         | FF  | N/A                      | Ignored, used for padding                         |
+-------------------------------+-----+--------------------------+---------------------------------------------------+
| ``LSC_RESET_CRC``             | 3B  | 24 bit info: all 0       | Resets the CRC16 register                         |
+-------------------------------+-----+--------------------------+---------------------------------------------------+
| ``VERIFY_ID``                 | E2  | - 24 bit info: all 0     | This checks the actual device ID against the given|
|                               |     | - 32 bit device JTAG ID  | value and fails if they do not match.             |
+-------------------------------+-----+--------------------------+---------------------------------------------------+
| ``LSC_PROG_CNTRL0``           | 22  | - 24 bit info: all 0     | This sets the value of device control register 0  |
|                               |     | - 32 bit CtlReg0 value   | Normally 0x40000000                               |
+-------------------------------+-----+--------------------------+---------------------------------------------------+
| ``LSC_INIT_ADDRESS``          | 46  | 24 bit info: all 0       | Resets the frame address register                 |
+-------------------------------+-----+--------------------------+---------------------------------------------------+
| ``ISC_PROGRAM_SECURITY``      | CE  | 24 bit info: all 0       | Program the security bit (prevents readback (?) ) |
+-------------------------------+-----+--------------------------+---------------------------------------------------+
| ``ISC_PROGRAM_USERCODE``      | C2  | - CRC bit set, 23 bits 0 | Sets the value of the USERCODE register           |
|                               |     | - 32 bit USERCODE value  |                                                   |
+-------------------------------+-----+--------------------------+---------------------------------------------------+
| ``ISC_PROGRAM_DONE``          | 5E  | 24 bit info: all 0       | End of bitstream, set DONE high                   |
+-------------------------------+-----+--------------------------+---------------------------------------------------+

Configuration Data
-------------------
The FPGA configuration data itself is programmed by using command ``LSC_PROG_INCR_RTI`` (0x82). Following this command,
there are some setup bits:

 - 1 bit: CRC16 comparison flag, normally set
 - 1 bit: CRC16 comparison at end flag, normally cleared = CRC check after every frame
 - 1 bit: dummy bits setting, normally cleared = include dummy bits in bitstream
 - 1 bit: dummy byte setting, normally cleared = use following bits as number of dummy bytes
 - 4 bits: number of dummy bytes between frames, usually 1
 - 16 bits: number of configuration frames

This is then followed by a number of frames, each in the following format:

 - The configuration frame itself, such that bit 0 of the first byte sent is the MSB of the frame,
   bit 7 of the first byte the MSB-7 and bit 0 of the last byte (if there are no dummy bits) being the LSB of the frame.
 - Any dummy bits needed to pad the frame to a whole number of bytes
 - A CRC-16 checksum:

    - For the first frame, this also covers any other commands sent
      before the programming command but after a CRC reset, and the programming command itself.
    - For subsequent frames, this excludes dummy bytes between frames
 - Dummy 0xFF bytes, usually only 1

The highest numbered frame in the chip is sent first.

Separate commands are used if EBR needs to be configured in the bitstream. ``EBR_ADDRESS`` (0xF6) is used to select the
EBR to program and the starting address in the EBR; and ``LSC_EBR_WRITE`` (0xB2) is used to program the EBR itself using
72-bit frames. The specifics of these still need to be documented.

Device-Specific Information
------------------------------

+-----------+-------------+--------+-----------------------+----------------------+
| Device    | Device ID   | Frames | Config Bits per Frame | Dummy Bits per Frame |
+===========+=============+========+=======================+======================+
| LFE5U-25  | 0x41111043  | 7562   | 592                   | 0                    |
+-----------+-------------+--------+-----------------------+----------------------+
| LFE5UM-25 |  0x01111043 | 7562   | 592                   | 0                    |
+-----------+-------------+--------+-----------------------+----------------------+
| LFE5U-45  | 0x41112043  | 9470   | 846                   | 2                    |
+-----------+-------------+--------+-----------------------+----------------------+
| LFE5UM-45 | 0x01112043  | 9470   | 846                   | 2                    |
+-----------+-------------+--------+-----------------------+----------------------+
| LFE5U-85  | 0x41113043  | 13294  | 1136                  | 0                    |
+-----------+-------------+--------+-----------------------+----------------------+
| LFE5UM-85 | 0x01113043  | 13294  | 1136                  | 0                    |
+-----------+-------------+--------+-----------------------+----------------------+