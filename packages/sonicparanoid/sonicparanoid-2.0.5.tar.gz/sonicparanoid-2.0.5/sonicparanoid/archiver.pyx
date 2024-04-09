"""Functions to compress and de-compress files."""
from libc.stdio cimport *
import sys
import os
from typing import Dict, Tuple, Deque
import gzip
from sonicparanoid import sys_tools as systools



__module_name__ = "archiver"
__source__ = "archiver.pyx"
__author__ = "Salvatore Cosentino"
__license__ = "GPLv3"
__version__ = "0.1"
__maintainer__ = "Cosentino Salvatore"
__email__ = "salvo981@gmail.com"



""" FUNCTIONS """
cdef void info():
    """Functions to create a graph from ortholog tables."""
    print(f"MODULE NAME:\t{__module_name__}")
    print(f"SOURCE FILE NAME:\t{__source__}")
    print(f"MODULE VERSION:\t{__version__}")
    print(f"LICENSE:\t{__license__}")
    print(f"AUTHOR:\t{__author__}")
    print(f"EMAIL:\t{__email__}")



cdef void compress_gzip(str inpath, str outpath, unsigned int complev = 5, bint removeSrc = 0, bint debug = 0):
    """Create a Gzip file from flat file."""
    if debug:
      print("compress_gzip :: START")
      print(f"Input: {inpath}")
      print(f"Output: {outpath}")
      print(f"Compression level:\t{complev}")
      print(f"Remove original:\t{removeSrc}")
    if not os.path.isfile(inpath):
        sys.stderr.write(f"The file to archive\n{inpath}\nwas not found, please provide a valid path")
        sys.exit(-2)

    # make sure the paths are different
    if inpath == outpath:
        sys.stderr.write("\nERROR: input and output file paths cannot be the same.\n")
        sys.exit(-2)

    # create the output directory
    systools.makedir(os.path.dirname(outpath))  
    line: bytes = bytes()

    # define file names and file descriptor pointer in C
    filename_byte_string = inpath.encode("UTF-8")
    cdef char* inputPathC = filename_byte_string
    #file pointers
    cdef FILE* cInputFile
    # varibales for files and lines
    cdef char * ln = NULL
    cdef size_t l = 0
    cdef ssize_t read

    #open the output file
    gzofd = gzip.open(outpath, "wb", compresslevel=complev)
    # open alignments file
    cInputFile = fopen(inputPathC, "rb")
    #start reading the output file
    while True:
        ##### Q: query; S: subject; H: hsp
        # Stop reading if it is not the STDOUT stream
        read = getline(&ln, &l, cInputFile)
        if read == -1:
            break
        # write the archive
        gzofd.write(ln)
    #close input and output files
    fclose(cInputFile)
    gzofd.close()

    # remove  the source filke oif required
    if removeSrc:
        os.remove(inpath)



cdef void extract_gzip(str inpath, str outpath, bint removeSrc = 0, bint debug = 0):
    """Unarchive a Gzip file."""
    if debug:
      print("extract_gzip :: START")
      print(f"Input: {inpath}")
      print(f"Output: {outpath}")
      print(f"Remove original:\t{removeSrc}")
    if not os.path.isfile(inpath):
        sys.stderr.write(f"The Gzip archive\n{inpath}\nwas not found, please provide a valid path")
        sys.exit(-2)

    # make sure the paths are different
    if inpath == outpath:
        sys.stderr.write("\nERROR: input and output paths cannot be the same.\n")
        sys.exit(-2)

    # create the output directory
    systools.makedir(os.path.dirname(outpath))  
    line: bytes = bytes()

    #open the alignments for AB
    with gzip.open(inpath, "rb") as gzifd:
        with open(outpath, "wt") as ofd:
            # read the file write an archive
            [ofd.write(line.decode("utf-8")) for line in gzifd.readlines()]

    # remove  the source filke oif required
    if removeSrc:
        os.remove(inpath)
