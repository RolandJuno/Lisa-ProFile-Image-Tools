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

infile = outfile = mwboot = origfile = ''

if len(sys.argv) > 1:
    for i in range(1, len(sys.argv)):
        if sys.argv[i].startswith("infile"):
            a = sys.argv[i].split("=")
            if a[1]:
                infile = a[1]
                print "Infile:", infile
        if sys.argv[i].startswith("outfile"):
            a = sys.argv[i].split("=")
            if a[1]:
                outfile = a[1]
                print "Outfile:", outfile
        if sys.argv[i].startswith("mwboot"):
            a = sys.argv[i].split("=")
            if a[1]:
                mwboot = a[1]
                print "MacWorks Bootblock:", mwboot
        if sys.argv[i].startswith("origfile"):
            a = sys.argv[i].split("=")
            if a[1]:
                origfile = a[1]
                print "Original Lisa Image:", origfile

if not infile and not outfile and not origfile:
    print "Converts a non-interleaved and tag-less MacWorks disk image back to an ArduinoFile/ProFile disk image."
    print "Adds 5:1 interleaving and header/tag bytes/pagelabels. Results in 532 byte blocks. For use Lisa hardware."
    print "Requires previously created macworks-bootblocks.bin file made with lisa2mac.py and the original Lisa disk image from the lisa2mac conversion."
    print "example: mac2lisa.py infile=\"System6.0.8-Mac.image\" origfile=\"System6.0.8-Old.image\" outfile=\"System6.0.8.img\" mwboot=\"macworks-bootblocks.bin\""
    print
    exit()

if not infile:
    print "ERROR: infile not specified."
    exit()
if not outfile:
    print "ERROR: outfile not specified."
    exit()
if not origfile:
    print "ERROR: origfile not specified."
    exit()
if not mwboot:
    mwboot="macworks-bootblocks.bin"
    print "MacWorks boot blocks:", mwboot

# Open Mac image to convert
f = open(infile,'rb')
f.seek(0)
totalsize = os.stat(infile).st_size
print "Total blocks to process:", totalsize/512
if totalsize%512:
    print "ERROR: infile is not evenly divisible by 512 (the number of bytes in a Mac disk image."
    exit()

# Open new ArduinoFile/Lisa image
of = open(outfile, 'wb')

# Open original MacWorks Lisa image to grab the headers/tag bytes/page labels
tagsf = open(origfile, 'rb')
tagsf.seek(0)

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

output = ''
totalsize += 201728 # Account for additional size from adding MacWorks boot block
numBlocks = totalsize/512
for n in range(numBlocks):
    blockno = n + offset[n % 16]
    #print "Block", n, "maps to block", blockno, (blockno*512,(blockno*512)+512)
    printProgress(iteration=n, total=numBlocks, prefix="Converting to Lisa Format", suffix="Complete", barLength=50)
    tagsf.seek(n*532)
    tags = tagsf.read(19) # Get old tag minus chksum
    data = tags + chr(0) + source[blockno*512:(blockno*512)+512] # New tag is set to 0 before checksum
    chksum = checksum(data)
    data = data[:19] + chr(chksum) + data[20:] # Add new checksum back to tag and block
    of.write(data) # Add new 532 byte block to our output.
    totalwrite += len(data)
    if n == 0: # Check the boot block
        if ord(data[4:5]) != 170 or ord(data[5:6]) != 170:
            print "ERROR: Bytes 4 and 5 of block 0 header are not set to AA:AA, this image will not boot on a Lisa."
            print "Check the source MacWorks boot block or create a new one by running lisa2mac.py again."
            exit()
of.close
print
if numBlocks * 532 != totalwrite: print "ERROR: Output file is not expected size", totalwrite, "is not expected size of", numBLocks*532
else: print "Wrote", totalwrite, "bytes."
print "Done."
exit()
