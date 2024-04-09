from libc.stdio cimport *
#from libc.stdlib cimport atoi
#from libc.stdlib cimport atof
import sys
import os
import pickle
import numpy as np
from pandas import read_csv
from scipy.sparse import dok_matrix, save_npz
from typing import Dict, List, Tuple, Set
from io import BytesIO


__module_name__ = "Essential alignments"
__source__ = "essentials_c.pyx"
__author__ = "Salvatore Cosentino"
__license__ = "GPLv3"
__version__ = "0.7"
__maintainer__ = "Cosentino Salvatore"
__email__ = "salvo981@gmail.com"



### FUNCTIONS ####
def info() -> None:
    """Functions to map and prepare the input file for essential alignments."""
    print(f"MODULE NAME:\t{__module_name__}")
    print(f"SOURCE FILE NAME:\t{__source__}")
    print(f"MODULE VERSION:\t{__version__}")
    print(f"LICENSE:\t{__license__}")
    print(f"AUTHOR:\t{__author__}")
    print(f"EMAIL:\t{__email__}")



cdef extern from "stdio.h":
    #FILE * fopen ( const char * filename, const char * mode )
    FILE *fopen(const char *, const char *)
    #int fclose ( FILE * stream )
    int fclose(FILE *)
    #ssize_t getline(char **lineptr, size_t *n, FILE *stream);
    ssize_t getline(char **, size_t *, FILE *)



def create_essential_stacks(alignPath: str, cntA: int, cntB: int, debug: bool=False) -> Tuple[Dict[int, List[int]], float, float]:
    """Parse an alignments file and create for each proteome a Deque with the required gene ids"""
    # extract the proteome names
    bname: str = os.path.basename(alignPath)
    A: str = ""
    B: str = ""
    A, B = bname.split("-", 1)
    tmpA: int = 0
    tmpB: int = 0
    if debug:
        print("\ncreate_essential_stacks :: START")
        print(f"Alignment path: {alignPath}")
        print(f"Proteins in {A}: {cntA}")
        print(f"Proteins in {B}: {cntB}")

    # create the sets
    tmpSetA: Set[int] = set()
    tmpSetB: Set[int] = set()

    # Read the alignment file and create the stacks with sequence IDs
    # define file names and file descriptor pointer in C
    filename_byte_string = alignPath.encode("UTF-8")
    cdef char* alignPath_c = filename_byte_string
    #file pointer
    cdef FILE* cfile
    # varibales for files and lines
    cdef char * line = NULL
    cdef size_t l = 0
    cdef ssize_t read

    #open the pairwise ortholog table
    cfile = fopen(alignPath_c, "rb")
    if cfile == NULL:
        raise FileNotFoundError(2, f"No such file or directory: '{alignPath_c}'")

    # read the file, remap the ids and write in the new output table
    # the lines of the alingment file have the following format
    # 1.10 2.36 42 69 88 49 50 49 50
    # Where the first 2 columns contains the gene ids for
    # the first second proteomes respectively
    while True:
        read = getline(&line, &l, cfile)
        if read == -1:
            break
        # split the line
        flds = line.split(b"\t", 2)[:-1]
        tmpA = int(flds[0].decode().split(".", 1)[-1])
        tmpB = int(flds[1].decode().split(".", 1)[-1])

        # check if the gene for A existed already
        if not tmpA in tmpSetA:
            tmpSetA.add(tmpA)
        if not tmpB in tmpSetB:
            tmpSetB.add(tmpB)
    #close input file
    fclose(cfile)

    # if debug:
    #   sys.stdout.write(f"\nLoaded sequences for proteome {A}:\t{len(tmpSetA)}")
    #   sys.stdout.write(f"\nLoaded sequences for proteome {B}:\t{len(tmpSetB)}\n")

    # convert to sorted lists of integers
    tmpListA: List[int] = list(tmpSetA)
    tmpListA.sort(reverse=True)
    tmpListB: List[int] = list(tmpSetB)
    tmpListB.sort(reverse=True)
    del tmpSetA, tmpSetB

    # print some debug
    cdef float essentialPctA = <float> (100. * (len(tmpListA) / cntA))
    cdef float essentialPctB = <float> (100. * (len(tmpListB) / cntB))
    if debug:
        print(f"\nSummary for the reduction of alignments for {bname}")
        print(f"Essential proteins for {A}:\t{len(tmpListA)}")
        print(f"% essential {A}:\t{essentialPctA:.2f}")
        print(f"Essential proteins for {B}:\t{len(tmpListB)}")
        print(f"% essential {B}:\t{essentialPctB:.2f}")

    # put the two stacks in a dictionary with swapped order
    finalDict: Dict[int, List[int]] = {int(B): tmpListB, int(A): tmpListA}
    # return the path and count of essential proteins
    return (finalDict, essentialPctA, essentialPctB)



def create_essential_stacks_from_archive(alignPath: str, cntA: int, cntB: int, debug: bool=False) -> Tuple[Dict[int, List[int]], float, float]:
    """Parse an alignments file and create for each proteome a Deque with the required gene ids"""
    import gzip
    # extract the proteome names
    bname: str = os.path.basename(alignPath)
    A: str = ""
    B: str = ""
    line: bytes = bytes()
    A, B = bname.split("-", 1)
    cdef int tmpA = 0
    cdef int tmpB = 0
    flds: List[bytes] = []
    if debug:
        print("\ncreate_essential_stacks_from_archive :: START")
        print(f"Alignment path: {alignPath}")
        print(f"Proteins in {A}:\t{cntA}")
        print(f"Proteins in {B}:\t{cntB}")

    # create the sets
    tmpSetA: Set[int] = set()
    tmpSetB: Set[int] = set()

    # Read the alignment file and create the stacks with sequence IDs
    # define file names and file descriptor pointer in C
    # filename_byte_string = alignPath.encode("UTF-8")
    # cdef char* alignPath_c = filename_byte_string
    #file pointer
    # cdef FILE* cfile
    # varibales for files and lines
    # cdef char * line = NULL
    # cdef size_t l = 0
    # cdef ssize_t read

    # read the file, remap the ids and write in the new output table
    # the lines of the alingment file have the following format
    # 1.10 2.36 42 69 88 49 50 49 50
    # Where the first 2 columns contains the gene ids for
    # the first second proteomes respectively
    with gzip.open(alignPath, "rb") as gzifd:
        for line in gzifd.readlines():
            # split the line
            flds = line.split(b"\t", 2)[:-1]
            tmpA = int(flds[0].decode().split(".", 1)[-1])
            tmpB = int(flds[1].decode().split(".", 1)[-1])
            # check if the gene for A existed already
            if not tmpA in tmpSetA:
                tmpSetA.add(tmpA)
            if not tmpB in tmpSetB:
                tmpSetB.add(tmpB)
    # close input file
    gzifd.close()

    if debug:
      sys.stdout.write(f"\nLoaded sequences for proteome {A}:\t{len(tmpSetA)}")
      sys.stdout.write(f"\nLoaded sequences for proteome {B}:\t{len(tmpSetB)}\n")

    # convert to sorted lists of integers
    tmpListA: List[int] = list(tmpSetA)
    tmpListA.sort(reverse=True)
    tmpListB: List[int] = list(tmpSetB)
    tmpListB.sort(reverse=True)
    del tmpSetA, tmpSetB

    # print some debug
    cdef float essentialPctA = <float> (100. * (len(tmpListA) / cntA))
    cdef float essentialPctB = <float> (100. * (len(tmpListB) / cntB))
    if debug:
        print(f"\nSummary for the reduction of alignments for {bname}")
        print(f"Essential proteins for {A}:\t{len(tmpListA)}")
        print(f"% essential {A}:\t{essentialPctA:.2f}")
        print(f"Essential proteins for {B}:\t{len(tmpListB)}")
        print(f"% essential {B}:\t{essentialPctB:.2f}")

    # put the two stacks in a dictionary with swapped order
    finalDict: Dict[int, List[int]] = {int(B): tmpListB, int(A): tmpListA}
    # return the path and count of essential proteins
    return (finalDict, essentialPctA, essentialPctB)



def extract_essential_proteins(rawFasta: str, essentialStack: List[int], outPath: str, debug: bool=False) -> None:
    """Extract FASTA sequences mathing IDs in stored in Stack subsets"""
    if debug:
        print('\nextract_essential_proteins :: START')
        print(f"FASTA path: {rawFasta}")
        print(f"Essential proteins:\t{len(essentialStack)}")
        print(f"Essential FASTA path: {outPath}")

    # extract elements from the stack untils
    # until all sequences are not found
    spId: str = os.path.basename(rawFasta) # files are expected to be named as integers
    cdef int essentialId = essentialStack.pop() # protein ID of essential protein
    seqLenDict: Dict[str, int] = {}
    cdef int tmpLen = len(essentialStack)
    tmpId: str = ""
    wrMode: bool = False # flag to control file writing

    # open output FASTA file
    ofd = open(outPath, "wb")
    # Read the alignment file and create the stacks with sequence IDs
    # define file names and file descriptor pointer in C
    filename_byte_string = rawFasta.encode("UTF-8")
    cdef char* rawFasta_c = filename_byte_string
    #file pointer
    cdef FILE* cfile
    # varibales for files and lines
    cdef char * line = NULL
    cdef size_t l = 0
    cdef ssize_t read

    #open the pairwise ortholog table
    cfile = fopen(rawFasta_c, "rb")
    if cfile == NULL:
        raise FileNotFoundError(2, "No such file or directory: '%s'" % rawFasta_c)

    # read the file, remap the ids and write in the new output table
    # the lines of the alingment file have the following format
    # 1.10 2.36 42 69 88 49 50 49 50
    # Where the first 2 columns contains the gene ids for
    # the first second proteomes respectively
    while True:
        read = getline(&line, &l, cfile)
        if read == -1:
            break

        # create a byte buffer
        bytesBuff = BytesIO(line)

        # if the first char is a '>'
        if bytesBuff.read1(1).decode() == ">":
            if wrMode: # then we were already writing
                if tmpLen > 0:
                    essentialId = essentialStack.pop()
                    wrMode = False
                    tmpLen = len(essentialStack)
                else:
                    #print("All essential sequences were extracted!")
                    break
            # check if the sequence id is matched
            if bytesBuff.read().decode()[:-1] == f"{spId}.{essentialId}":
                # the ID matches
                ofd.write(bytesBuff.getvalue())
                wrMode = True
                continue
            else:
                if wrMode:
                    wrMode = False
        else:
            # rewind
            bytesBuff.seek(0)
            if wrMode:
                ln = bytesBuff.getvalue().decode()
                ofd.write(bytesBuff.getvalue())
                # add element to lengths dictionary
                tmpId = f"{spId}.{essentialId}"
                if not tmpId in seqLenDict:
                    seqLenDict[tmpId] = len(ln) - 1
                else:
                    sys.exit("extract_essential_proteins :: The same HDR was already inserted before!!!")
    #close input file
    fclose(cfile)
    # close FASTA file
    ofd.close()
    # dump the pickle with sequence lengths
    pickle.dump(seqLenDict, open(f"{outPath}.len.pckl", 'wb'), protocol=4)



def predict_fastest_pairs(outDir: str, pairs: List[str], protCnts: Dict[str, int], protSizes: Dict[str, int], debug: bool = False) -> str:
    """Predict the fastest pairs"""
    if debug:
        print("\npredict_fastest_pairs :: START")
        print(f"Output directory: {outDir}")
        print(f"Combinations:\t{pairs}")
        print(f"Protein counts:\t{len(protCnts)}")
        print(f"Proteome sizes:\t{len(protSizes)}")

    # path to the file with the predictions
    predPath: str = os.path.join(outDir, "fastest_pairs.tsv")
    # write the starting dataset
    tmpA: str = ""
    tmpB: str = ""
    cdef int seqCntA, seqCntB, proteomeSizeA, proteomeSizeB = 0
    cdef float avgLenA, avgLenB, cntDiff, sizeDiff, avgLenDiff = 0.0

    # Columns in the dataframe
    sampleFileCols: List[str] = ["seq_cnt_a", "seq_cnt_b", "seq_cnt_diff_folds_b_gt_a", "proteome_size_a", "proteome_size_b", "prot_size_diff_folds_b_gt_a", "avg_seq_len_a", "avg_seq_len_b", "avg_seq_len_diff_folds_b_gt_a"]
    # NOTE: The part below uses the model trained for ISMB2021
    # generate samples to be predicted
    with open(predPath, "wt") as ofd:
        hdr = "\t".join(sampleFileCols)
        hdr = f"pair\t{hdr}\n"
        # write the header
        ofd.write(hdr)
        del hdr
        for p in pairs:
            tmpA, tmpB = p.split("-", 1)
            # compute values for A
            seqCntA = <int> protCnts[tmpA]
            proteomeSizeA = <int> protSizes[tmpA]
            avgLenA = <float> (proteomeSizeA / seqCntA)
            # compute values for B
            seqCntB = <int> protCnts[tmpB]
            proteomeSizeB = <int> protSizes[tmpB]
            avgLenB = <float> (proteomeSizeB / seqCntB)
            # compute protein counts difference folds considering B > A
            if seqCntA > seqCntB:
                cntDiff = <float> -(seqCntA / seqCntB)
            else:
                cntDiff = <float> (seqCntB / seqCntA)
            # compute proteome size difference folds considering B > A
            if proteomeSizeA > proteomeSizeB:
                sizeDiff = <float> -(proteomeSizeA / proteomeSizeB)
            else:
                sizeDiff = <float> (proteomeSizeB / proteomeSizeA)
            # compute avg protein length difference folds considering B > A
            if avgLenA > avgLenB:
                avgLenDiff = <float> -(avgLenA / avgLenB)
            else:
                avgLenDiff = <float> (avgLenB / avgLenA)
            # write the output file
            ofd.write(f"{p}\t{seqCntA}\t{seqCntB}\t{cntDiff:.3f}\t{proteomeSizeA}\t{proteomeSizeB}\t{sizeDiff:.3f}\t{avgLenA:.3f}\t{avgLenB:.3f}\t{avgLenDiff:.3f}\n")
    del tmpA, tmpB

    # set path to the model
    modelPath: str = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bin/guess_fast_pair.pckl")
    # this model predict samples with 9 fields as follow
    # seq_cnt_a seq_cnt_b seq_cnt_diff_folds_b_gt_a proteome_size_a proteome_size_b prot_size_diff_folds_b_gt_a avg_seq_len_a avg_seq_len_b avg_seq_len_diff_folds_b_gt_a
    # 3085 4406 1.428 949308 1377648 1.451 307.717 312.675 1.016

    model = pickle.load(open(modelPath, "rb"))
    # try it doing the following
    #print(model.predict([[cntDiff, sizeDiff, proteomeSizeA, proteomeSizeB, avgLenA, avgLenB]]))
    # load the dataframe with predictions
    df = read_csv(predPath, sep="\t")
    samples = df[sampleFileCols].to_numpy()
    predictions = model.predict(samples)
    # add the predictions to the dataframes
    # HACK: invert the prediction for testing
    # predictions = np.abs(predictions - 1)
    df.insert(len(df.columns), column="pred", value=predictions)
    # overwrite the previous dataset
    df.to_csv(predPath, sep="\t", float_format="%.3f", index=False)

    '''
    print("\nDEBUG lines from essentials.predict_fastest_pairs")
    print(modelPath)
    print(model)
    # print(f"predictions: {predictions}")
    '''

    # write a smaller file to be used to fill the matrix
    predPath = os.path.join(outDir, "prediction_results.tsv")
    simpleDf = df[["pair", "pred"]]
    simpleDf.to_csv(predPath, sep="\t", float_format="%.3f", index=False)

    # delete not required objects
    del samples
    del simpleDf
    del df

    # Now create the matrix with the fastest predictions
    spListInt = [int(x) for x in list(protCnts.keys())]
    cdef int maxSp = 0
    maxSp = max(spListInt)
    M = dok_matrix((maxSp, maxSp), dtype=np.int8)
    if debug:
        print(f"Matrix shape:\t{str(M.shape)}")

    # temporary variables
    spA: int = 0
    spB: int = 0
    rawPred: str = ""
    tmpPair: str = ""

    # open and process the file with predictions
    fd = open(predPath, "rt")
    fd.readline()  # skip the hdr
    for ln in fd:
        tmpPair, rawPred = ln.rstrip("\n").split("\t", 1)
        spA, spB = [int(x) for x in tmpPair.split("-", 1)]
        # adjust the indexes
        spA -= 1
        spB -= 1
        # set the value to 1 for the fastest pairs
        if int(rawPred) == 1:  # then set as the fastes (will be aligned normally)
            M[spA, spB] = 1
        else:  # set B-A as the first alignment
            M[spB, spA] = 1
    fd.close()

    # remove file with predictions
    if not debug:
        os.remove(predPath)

    # store to a npz file
    M = M.tocsr()
    fastMtxPath: str = os.path.join(outDir, "fast_aln_mtx.npz")
    mtxOfd = open(fastMtxPath, "wb")
    save_npz(mtxOfd, M, compressed=False)
    mtxOfd.close()
    del M
    del spListInt

    # sys.exit("DEBUG: essentials_c.pyx -> predict_fastest_pairs")
    # return the paths to the prediction
    return predPath