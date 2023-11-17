# Lisa ProFile Image Tools
A set of tools to minipulate ArduinoFile or cameo/aphid ProFile MacWorks image to Mac and back to Lisa.

## lisa2mac.py

This tool converts a MacWorks disk image from an ArduinoFile or cameo/aphid ProFile drive emulator to a standard Mac raw disk image. You can then use it in an emulator such as MiniVMac.

## mac2lisa.py

This tools converts a standard Mac raw disk image to a MacWorks disk image for an ArduinoFile or cameo/aphid ProFile drive emulator. You can then use it to boot your Lisa into MacWorks.

## Notes

- These tools will not work on any other type of disk image from a Lisa other than MacWorks.
- Mac disk images have 512 byte blocks. MacWorks disk image have 532 byte blocks.
- Mac disk image blocks are in consecutive order. MacWorks disk image blocks are inteleaved 5:1.
- MacWorks disk images have a several boot blocks that occupy the first 201,728 bytes (394 blocks).
- All header/tag bytes/page labels (the 20 bytes of additional data a ProFile stores) are converted to all zeros except the last digit which is the XOR checksum of the block. In a MacWorks disk image for a Lisa, these bytes are stored at the beginning of each block, followed by the 512 byte block of data. For a Mac disk image, they are removed completely.

