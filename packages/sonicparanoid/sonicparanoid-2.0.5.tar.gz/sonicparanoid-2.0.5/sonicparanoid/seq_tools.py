"""
This module contains different utility functions to get info on seuquence files
it also include some functions to format blast output
"""
import sys
from sonicparanoid import sys_tools as systools
import os
import subprocess

__module_name__ = 'Sequence Tools'
__source__ = 'seq_tools.py'
__author__ = 'Salvatore Cosentino'
#__copyright__ = ''
__license__ = 'GPL'
__version__ = '1.7'
__maintainer__ = 'Cosentino Salvatore'
__email__ = 'salvo981@gmail.com'



def info():
    """
    Thi module contains different utility functions to get info on seuquence files.

    it also include some functions to format blast output
    """
    print('MODULE NAME:\t%s'%__module_name__)
    print('SOURCE FILE NAME:\t%s'%__source__)
    print('MODULE VERSION:\t%s'%__version__)
    print('LICENSE:\t%s'%__license__)
    print('AUTHOR:\t%s'%__author__)
    print('EMAIL:\t%s'%__email__)



def checkMoleculeType(inSeq, debug=True):
    """Check if the input fasta sequences are Proteins."""
    if debug:
        print('checkMoleculeType :: START')
        print('INPUT SEQ:\n%s'%inSeq)
    # parse the file using biopython
    from Bio import SeqIO
    cnt = 0
    #cntList = []
    cumulativeSet = set()
    for record in SeqIO.parse(open(inSeq), "fasta"):
        cnt += 1
        seqLetters = set(str(record.seq).upper())
        # add the letters to the cumulative set
        cumulativeSet = cumulativeSet.union(seqLetters)
    # calculate the average number of letters in the sequences
    if len(cumulativeSet) < 15:
        sys.stderr.write('\nWARNING: the {:d} sequences for {:s} are composed of only the following {:d} symbols:'.format(cnt, os.path.basename(inSeq), len(cumulativeSet)))
        sys.stderr.write('\n{:s}\nPlease make sure that your FASTA files contain proteins and not DNA, nor RNA sequences.\n'.format(', '.join(str(s) for s in cumulativeSet)))
    elif len(cumulativeSet) > 29:
        sys.stderr.write('\nERROR: the {:d} sequences for {:s} contain too many ({:d}) symbols:'.format(cnt, os.path.basename(inSeq), len(cumulativeSet)))
        sys.stderr.write('\n{:s}\nPlease make sure that your FASTA files contain valid proteins.\n'.format(', '.join(str(s) for s in cumulativeSet)))
        sys.exit(-5)



def countSeqs(inSeq, debug=False):
    """Count sequences in the input fasta file."""
    if debug:
        print('\ncountSeqs START:')
        print('INPUT SEQ ::\t%s'%inSeq)
    #check that there file is not empty
    stInfo = os.stat(inSeq)
    if stInfo.st_size == 0:
        sys.stderr.write('\nWARNING: the input file is empty, 0 will be returned.\n')
        return 0
    faHdrCnt = 0#counter for fasta headers
    lnCnt = 0#line counter
    #let's open the input file and start counting
    ifd = open(inSeq)
    for ln in ifd:
        if len(ln.strip()) == 0: #empty line
            continue
        lnCnt += 1
        if ln[0] == '>':
            faHdrCnt += 1
    ifd.close()
    #return the count
    return faHdrCnt



def fltrSeqByLen(inSeq, outDir=None, minLen=100, debug=True):
    """filter a fasta sequence file based on the minimum length given as input parameter."""
    from Bio import SeqIO
    if debug:
        print('fltrSeqByLen :: START')
        print('INPUT SEQ:\n%s'%inSeq)
    #check the existence of the input file
    if not os.path.isfile(inSeq):
        sys.stderr.write('The file %s was not found, please provide a valid file path'%inSeq)
        sys.exit(-2)
    #check the existence of the output directory
    if outDir != None:
        if not os.path.isdir(outDir):
            sys.stderr.write('The directory %s was not found, please provide the path to a valid directory'%outDir)
            sys.exit(-2)
    else:
        outDir = os.path.dirname(inSeq) + '/'
    #set output file name
    if minLen < 50:
        minLen = 50
    outName = os.path.basename(inSeq)
    flds = outName.split('.')
    outName = '.'.join(flds[0:len(flds)-1]) + '.%sbp.'%str(minLen) + flds[-1]
    outPath = outDir + outName
    if debug:
        print('OUTPUT SEQ:\n%s'%outPath)
    #open output file
    fdOut = open(outPath, 'w')
    totSeq = 0
    removedSeqCnt = 0
    for seq_record in SeqIO.parse(open(inSeq), 'fasta'):
        totSeq = totSeq + 1
        if len(seq_record) < minLen:
            removedSeqCnt = removedSeqCnt + 1
        else:
            SeqIO.write(seq_record, fdOut, 'fasta')
    fdOut.close()
    if debug:
        print('Sequences:\t%d'%totSeq)
        print('Filtered (shorter than %d):\t%d'%(minLen, removedSeqCnt))
        print('Remaining Seqs:\t%d'%(totSeq-removedSeqCnt))
    #return a tuple with the total number of sequences and removed sequences
    return (outPath, totSeq, removedSeqCnt)