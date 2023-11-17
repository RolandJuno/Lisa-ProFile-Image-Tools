#!/usr/bin/env python
# -*- coding: utf-8 -*- 
import os
import glob
import sys

## MAIN ##

print "mac2lisa.py 0.1 by @paulrickards Nov 16, 2023"
print

# Calculate block checksum for header/tag bytes/page labels. Byte 0x14 should
# initially be 0x00 and this checksum should replace it.
def checksum(data):
    checksum = 0
    for el in data:
        checksum ^= ord(el)
    #print checksum, hex(checksum), chr(checksum)
    return checksum

# Print iterations progress
def printProgress (iteration, total, prefix = '', suffix = '', decimals = 1, barLength = 100):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        barLength   - Optional  : character length of bar (Int)
    """
    formatStr       = "{0:." + str(decimals) + "f}"
    percents        = formatStr.format(100 * (iteration / float(total)))
    filledLength    = int(round(barLength * iteration / float(total)))
    bar             = '█' * filledLength + '-' * (barLength - filledLength)
    sys.stdout.write('\r%s |%s| %s%s %s' % (prefix, bar, percents, '%', suffix)),
    if iteration == total:
        sys.stdout.write('\n')
    sys.stdout.flush()

infile = outfile = mwboot = ''

if len(sys.argv) > 1:
    for i in range(1, len(sys.argv)):
        if sys.argv[i].startswith("infile"):
            a = sys.argv[i].split("=")
            if a[1]:
                infile = a[1]
                print "Infile  :", infile
        if sys.argv[i].startswith("outfile"):
            a = sys.argv[i].split("=")
            if a[1]:
                outfile = a[1]
                print "Outfile :", outfile
        if sys.argv[i].startswith("mwboot"):
            a = sys.argv[i].split("=")
            if a[1]:
                mwboot = a[1]
                print "MacWorks:", mwboot

if not infile and not outfile:
    print "Converts a non-interleaved and tag-less MacWorks disk image back to an ArduinoFile/ProFile disk image."
    print "Adds 5:1 interleaving and header/tag bytes/pagelabels. Results in 532 byte blocks. For use Lisa hardware."
    print "Requires previously created macworks-bootblocks.bin file made with lisa2mac.py."
    print "example: mac2lisa.py infile=\"System6.0.8-Mac.image\" outfile=\"System6.0.8.img\" mwboot=\"macworks-bootblocks.bin\""
    print
    exit()

if not infile:
    print "ERROR: infile not specified."
    exit()
if not outfile:
    print "ERROR: outfile not specified."
    exit()
if not mwboot:
    mwboot="macworks-bootblocks.bin"
    print "MacWorks:", mwboot

# Open Mac image to convert
f = open(infile,'rb')
f.seek(0)
totalsize = os.stat(infile).st_size + 201728 # Image + MacWorks boot blocks
numblocks = totalsize/512

print "Blocks  :", '{:,}'.format(totalsize/512)
if totalsize%512:
    print "ERROR: infile is not evenly divisible by 512 (the number of bytes in a Mac disk image."
    exit()

# Open new ArduinoFile/Lisa image
of = open(outfile, 'wb')

# Read MacWorks bootblock
with open(mwboot, 'rb') as bb:
    macworksbootblock = bb.read(201728)
bb.close
totalread = 0
totalwrite = 0

# Define interleaving pattern Mac -> ProFile
# https://github.com/rayarachelian/lisaem/blob/master/src/tools/src/raw-to-dc42.c
#offset = [0, 13-1, 10-2, 7-3, 4-4, 1-5, 14-6, 11-7, 8-8, 5-9, 2-10, 15-11, 12-12, 9-13, 6-14, 3-15, 16-16, 29-17, 26-18, 23-19, 20-20, 17-21, 30-22, 27-23, 24-24, 21-25, 18-26, 31-27, 28-28, 25-29, 22-30, 19-31]
offset = [0, 12, 8, 4, 0, -4, 8, 4, 0, -4, -8, 4, 0, -4, -8, -12]

# Read in entire drive image and concatenate to MacWorks boot block
source = macworksbootblock + f.read(totalsize)
f.close

# Reverse the process. Adds tags back in and interleaves
# Boot block 0x0000 - 0x31400
# Source blocks are 512 bytes. Destination blocks are 532 bytes.

print
output = ''
for n in range(numblocks):
    blockno = n + offset[n % 16]
    #print "Block", n, "maps to block", blockno, (blockno*512,(blockno*512)+512)
    printProgress(iteration=n, total=numblocks, prefix="Converting to Lisa Format", suffix="Complete", barLength=50)
    if n==0: tags = "\xAA\xAA\xAA\xAA\xAA\xAA\xAA\xAA\xAA\xAA\xAA\xAA\x00\x00\x00\x00\x00\x00\x00"
    else: tags = "\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
    data = tags + chr(0) + source[blockno*512:(blockno*512)+512] # New tag is set to 0 before checksum
    chksum = checksum(data)
    data = data[:19] + chr(chksum) + data[20:] # Add new checksum back to tag and block
    of.write(data) # Add new 532 byte block to our output.
    totalwrite += len(data)

of.close
print '\n'
expectedsize=numblocks*532
print "Expected:", '{:,}'.format(expectedsize), 'bytes.'
print "Actual  :", '{:,}'.format(totalwrite),  'bytes.'
if expectedsize != totalwrite: print "ERROR: Output file size", totalwrite, "is not expected size", expectedsize, "(difference of", totalwrite-expectedsize, ")"
print "Done."
exit()
