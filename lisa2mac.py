#!/usr/bin/env python
# -*- coding: utf-8 -*- 
import os
import glob
import sys

## MAIN ##

print "lisa2mac.py 0.1 by @paulrickards Nov 16, 2023"
print

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

infile = outfile = ''

if len(sys.argv) > 1:
    for i in range(1, len(sys.argv)):
        if sys.argv[i].startswith("infile"):
            a = sys.argv[i].split("=")
            if a[1]:
                infile = a[1]
                print "Infile :", infile
        if sys.argv[i].startswith("outfile"):
            a = sys.argv[i].split("=")
            if a[1]:
                outfile = a[1]
                print "Outfile:", outfile

if not infile and not outfile:
    print "Converts an ArduinoFile MacWorks disk image with 532 byte blocks to standard 512 byte block images."
    print "Removes 5:1 interleaving and header/tag bytes/page labels. For use in emulators such as MiniVMac."
    print "Generates MacWorks boot block file which is needed to convert back as well as the original source image."
    print "example: lisa2mac.py infile=\"System6.0.8-Lisa.image\" outfile=\"System6.0.8-Mac.image\""
    print
    exit()

if not infile:
    print "ERROR: infile not specified."
    exit()
if not outfile:
    print "ERROR: outfile not specified."
    exit()

f = open(infile,'rb')
f.seek(0)
totalsize = os.stat(infile).st_size
of = open(outfile, 'wb')
debugout = open("debugout.txt", 'wb')

if totalsize%532:
    print "ERROR: infile is not evenly divisble by 532 (ProFile block size)"
    exit()
totalread = 0
totalwrite = 0
print "Blocks  :", '{:,}'.format(totalsize/532)
print

# Define interleaving pattern ProFile -> Mac
# https://github.com/rayarachelian/lisaem/blob/master/src/tools/src/raw-to-dc42.c
# static const int offset[]={0,5,10,15,4,9,14,3,8,13,2,7,12,1,6,11,16,21,26,31,20,25,30,19,24,29,18,23,28,17,22,27};
# offset = [0 ,5-1, 10-2, 15-3, 4-4, 9-5, 14-6, 3-7, 8-8, 13-9, 2-10, 7-11, 12-12, 1-13, 6-14, 11-15, 16-16, 21-17, 26-18, 31-19, 20-20, 25-21, 30-22, 19-23, 24-24, 29-25, 18-26, 23-27, 28-28, 17-29, 22-30, 27-31]
offset = [0, 4, 8 ,12, 0, 4, 8, -4, 0, 4, -8, -4, 0, -12, -8, -4]

# Source blocks are 532. Destination blocks are 512.

output = ''
numBlocks = totalsize/532
for n in range(numBlocks):
    blockno = n + offset[n % 16]
    #print "Block", n, "maps to block", blockno
    printProgress(iteration=n, total=numBlocks, prefix="Converting to Mac Format", suffix="Complete", barLength=50)
    f.seek(blockno * 532)
    block = f.read(532)
    output += block[20:]
print
of.write(output[201728:]) # skip over boot blocks
of.close
print "Saved", outfile
# Save MacWorks boot block located at 0x0000 - 0x31400 (201728)
of = open('macworks-bootblocks.bin', 'wb')
of.write(output[:201728])
of.close
print "Saved macworks-bootblocks.bin. Keep this file for conversion back to Lisa."
print "Done."
exit()
