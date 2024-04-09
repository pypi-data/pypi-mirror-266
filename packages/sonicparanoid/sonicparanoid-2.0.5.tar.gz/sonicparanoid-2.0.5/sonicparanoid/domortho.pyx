# -*- coding: utf-8 -*-
# cython: profile=False
"""
This module contains functions related to domain-based orthology inference.
"""

from __future__ import annotations

# Gitlab pipeline does not support pyx files
from libc.math cimport ceil, sqrt

import sys
import os
import logging
from collections import deque
from pickle import dump
import multiprocessing as mp
import queue
from tqdm import tqdm
from time import perf_counter
from typing import TextIO, BinaryIO
from dataclasses import dataclass

# import scipy sparse matrixes
from scipy.sparse import csr_matrix

import numpy as np
cimport numpy as cnp
cimport cython

# internal modules
# from sonicparanoid import <module_name>


'''
__module_name__ = "Domain orthology"
__source__ = "domortho.pyx"
__author__ = "Salvatore Cosentino"
__license__ = "GPLv3"
__version__ = "1.0"
__maintainer__ = "Cosentino Salvatore"
__email__ = "salvo981@gmail.com"



cdef void info():
    """Functions related to domain-based orthology inference."""
    print(f"MODULE NAME:\t{__module_name__}")
    print(f"SOURCE FILE NAME:\t{__source__}")
    print(f"MODULE VERSION:\t{__version__}")
    print(f"LICENSE:\t{__license__}")
    print(f"AUTHOR:\t{__author__}")
    print(f"EMAIL:\t{__email__}")
'''


# Logger that will be used in this module
# It is child of the root logger and
# should be initialiazied using the function set_logger()
logger: logging.Logger = logging.getLogger()


### CLASSES ###
# HACK: remove the query name; removed domains; addded document with the phrase used in training
@dataclass
class Arch:
    """Domain architecture of protein.

    This dataclass contains information about the domain architecture of a protein.

    Args:
        seqlen: protein length.
        coverage: percentage of the protein covered by matched profiles.
        size: size of the architecture (matched profiles, and unknown interregions).
        domCnt: count of domains in the architecture
        domWvIdx: array of integers representing the index in the vocabulary (and word2vec dictionary) for matched domains. [8 -> "PF07686@CL0011"]
        this array is useful to quickly see if two words (domains) are the same without the need to compare the word vectors.
        regState: State of the region: 1 -> domain; 0 -> uncovered
        regLengths: Lengths of the domain or uncovered region
        phrase: list of words representing a single phrase (architecture). ["4", "PF07686@CL0011", "8"]
        embedding: embedding of the phrase from doc2vec
        domain_types: String of number encoding for PFamA types (e.g., Family, profile, disordered etc.)
    """
    seqlen: int
    coverage: float
    size: int
    domCnt: int
    domWvIdx: np.ndarray
    regState: np.ndarray
    regLengths: np.ndarray
    phrase: np.ndarray
    embedding: np.ndarray
    domain_types: long


    # FIXME: this should be removed when Cython will natively support dataclass objects
    __annotations__ = {
        'seqlen': int,
        'coverage': float,
        'size': int,
        'domCnt': int,
        'domWvIdx': np.ndarray,
        'regState': np.ndarray,
        'regLengths': np.ndarray,
        'phrase': np.ndarray,
        'embedding': np.ndarray, # embedding of the phrase from doc2vec
        'domain_types': long, # unsigned long
    }



@dataclass
class ArchClstr:
    """Cluster of arch-based ortholog relationships.

    Args:
        size: number of orthologs in the cluster (from both species).
        sp1Ids: Protein IDs of ortholog archs froms species 1
        sp2Ids: Protein IDs of ortholog archs froms species 2
        cosineValues: list of arrays of doubles with the cosine similarities
    """

    size: int
    sp1Ids: np.ndarray
    sp2Ids: np.ndarray
    cosineValues: list


    # FIXME: this should be removed when Cython will natively support dataclass objects
    __annotations__ = {
        'size': int,
        'sp1Ids': np.ndarray,
        'sp2Ids': np.ndarray,
        'cosineValues': list,
    }



### Workers ###
# def consume_infer_arch_orthologs(jobs_queue, results_queue, archMasterDict, seqCntDict: dict[str, int], outDir: str, lenDiffThr: float=3.0, maxCovDiff: float = 0.20, domCntDiffThr: float=2.0, minCosine: float = 0.5, storeMtx: bool = True) -> None:
cdef void consume_infer_arch_orthologs(object jobs_queue, object results_queue, dict archMasterDict, dict seqCntDict, str mtxDir, str archOrthoDbDir, double lenDiffThr, double maxCovDiff, double domCntDiffThr, double minCosine, bint storeMtx):
    """
    Find arch-based otyhologs.
    """

    cdef unsigned long sp1ProtCnt, sp2ProtCnt
    cdef unsigned long sp1, sp2
    # HACK: add values from ortholog clustering
    cdef (double, double, double, double, double, unsigned long, unsigned long, unsigned long, unsigned long, unsigned long, unsigned long, unsigned long, unsigned long, unsigned long) archAnalysisTpl

    cdef str spPairStr
    cdef list outlist
    cdef double totextime

    while True:
        spPair = jobs_queue.get(True, 1)

        if spPair is None:
            break

        sp1, sp2 = spPair
        # Extract protein counts
        sp1ProtCnt = seqCntDict[str(sp1)]
        sp2ProtCnt = seqCntDict[str(sp2)]
        spPairStr = f"{sp1}-{sp2}"
        archAnalysisTpl = infer_arch_orthologs(sp1=sp1, sp2=sp2, sp1ProtCnt=seqCntDict[str(sp1)], sp2ProtCnt=seqCntDict[str(sp2)], sp1ArchsDict=archMasterDict[sp1], sp2ArchsDict=archMasterDict[sp2], mtxDir=mtxDir, archOrthoDbDir=archOrthoDbDir, lenDiffThr=lenDiffThr, maxCovDiff=maxCovDiff, domCntDiffThr=domCntDiffThr, minCosine=minCosine, storeMtx=storeMtx)
        # sys.exit("DEBUG: domortho.pyx :: after infer_arch_orthologs")

        # compute the total execution time
        totextime = archAnalysisTpl[0] + archAnalysisTpl[1] + archAnalysisTpl[2] + archAnalysisTpl[3] + archAnalysisTpl[4]

        outlist = [spPairStr, sp1ProtCnt, sp2ProtCnt]
        for v in archAnalysisTpl:
            outlist.append(v)
        # Insert the total execution time
        outlist.insert(8, totextime)
        # print(archAnalysisTpl)
        # Put a list with all the values in the queue
        results_queue.put(outlist)



### Multi-threaded functions ###
# cdef void parallel_infer_arch_orthologs(list rawArchFilePaths, double minqcov, unsigned short mbsize, str outDocFilePath, str outDir, bint skipUnknown=0, unsigned short threads=4):
def parallel_infer_arch_orthologs(spPairs: list[tuple[int, int]], archMasterDict: dict[int, dict[int, Arch]], seqCntDict: dict[str, int], outDir: str, lenDiffThr: float=3.0, maxCovDiff: float = 0.20, domCntDiffThr: float=2.5, minCosine: float = 0.5, storeMtx: bool = True, threads: int = 4) -> None:
    """Perform selection of orthlogs architectures.

    Parameters:
    spPairs list[tuple[int, int]]: pairs of species for which the Architectures should be compared
    archMasterDict Dict[int, Dict[int, Arch]]: Dictionary that will be shared among the processes
    seqCntDict Dict[str, int]: Dictionary number of proteins for each input species
    outDir (str): Directory in which the prefiltered pairs will be stored
    lenDiffThr (float): maximum allowed length difference for a pair of archs
    maxCovDiff (float): maximum allowed difference in query coverage among 2 archs
    domCntDiffThr (float): maximum allowed arch size difference for a pair of archs
    minCosine (float): minimum cosine similarity for a arch pair to be considered
    storeMtx (bint): store matrixes to disk

    threads (unsigned int): Threads

    Returns:
    void

    """

    # Create the output directories if required
    makedir(outDir)
    cdef str archOrthoDbDir = os.path.join(outDir, "arch_orthologs")
    makedir(archOrthoDbDir)
    cdef str mtxDir = os.path.join(outDir, "arch_mtx")
    makedir(mtxDir)

    debugStr: str = f"""parallel_infer_arch_orthologs :: START
    Species pairs to be compared:\t{len(spPairs):d}
    Species in master arch dictionary:\t{len(archMasterDict):d}
    Species with protein counts:\t{len(seqCntDict):d}
    Output directory: {outDir}
    Directory in which ortholog tables are stored: {archOrthoDbDir}
    Directory in which matrix files are stored: {mtxDir}
    Length difference threshold:\t{lenDiffThr:.2f}
    Arch coverage difference threshold:\t{maxCovDiff:.2f}
    Domain count difference threshold:\t{domCntDiffThr:.2f}
    Minimum cosine similarity:\t{minCosine:.2f}
    Threads:\t{threads:d}"""
    logger.debug(debugStr)

    cdef str runInfoFile
    runInfoFile = os.path.join(outDir, "arch_analysis.info.txt")
    cdef dict infoDict = {"Module:":__name__}
    infoDict["Main output dir:"] = outDir
    infoDict["Ortholog tables directory:"] = archOrthoDbDir
    infoDict["Matrix files directory:"] = mtxDir
    infoDict["Pairs of species:"] = str(len(spPairs))
    infoDict["Species in master arch dictionary:"] = str(len(archMasterDict))
    infoDict["Species with protein counts:"] = str(len(seqCntDict))
    infoDict["Length difference threshold:"] = f"{lenDiffThr:.2f}"
    infoDict["Arch coverage difference threshold:"] = f"{maxCovDiff:.2f}"
    infoDict["Domain count difference threshold:"] = f"{domCntDiffThr:.2f}"
    infoDict["Minimum cosine similarity:"] = f"{minCosine:.2f}"
    infoDict["Store matrix files:"] = str(storeMtx)
    infoDict["Threads:"] = str(threads)
    write_run_info_file(runInfoFile, infoDict)

    # reset timers
    cdef double start_time = 0.0
    # tmpPath: str = ""
    cdef long jobsCnt = len(spPairs)
    cdef size_t i
    cdef (unsigned long, unsigned long) tmpPair
    # create the queue and start adding
    proc_queue: mp.queues.Queue = mp.Queue(maxsize=jobsCnt + threads)

    for i in range(0, jobsCnt):
        tmpPair = spPairs[i]
        proc_queue.put(tmpPair)

    # add flags for ended jobs
    for i in range(0, threads):
        sys.stdout.flush()
        proc_queue.put(None)

    # Queue to contain the documents for each file
    results_queue: mp.queues.Queue = mp.Queue(maxsize=jobsCnt)

    # List of running jobs
    cdef list runningJobs = [mp.Process(target=consume_infer_arch_orthologs, args=(proc_queue, results_queue, archMasterDict, seqCntDict, mtxDir, archOrthoDbDir, lenDiffThr, maxCovDiff, domCntDiffThr, minCosine, storeMtx)) for i_ in range(threads)]

    # calculate cpu-time for alignments
    start_time = perf_counter()
    # write some message...
    sys.stdout.write(f"\nIdentifing orthologs at the domain level for {jobsCnt} species pairs...")

    # All documents will be written in this file
    cdef str outPath = os.path.join(outDir, "ex_time.arch_analysis.tsv")
    # ofd: TextIO = open(outPath, "wt", buffering=1) # Default buffering should be ok
    ofd: TextIO = open(outPath, "wt") # Default buffering should be ok

    # Write the HDR
    # ofd.write("pair\tsp1_prot_cnt\tsp2_prot_cnt\tfiltering\trowwise\tcolwise\tone2one\ttot_time\tprot_pairs_cnt\tarch_pairs_cnt\treject_len_cnt\treject_cov_cnt\treject_size_cnt\treject_cos_cnt\tone2one_cnt\n")
    # HACK: add the fields from clustering creation
    ofd.write("pair\tsp1_prot_cnt\tsp2_prot_cnt\tfiltering\trowwise\tcolwise\tone2one\ttable_creation\ttot_time\tprot_pairs_cnt\tarch_pairs_cnt\treject_len_cnt\treject_cov_cnt\treject_size_cnt\treject_cos_cnt\tpairs_cnt\tcluster_cnt\tbiggest_cluster\n")


    # FIXME: this can be error prone as it is hardcoded
    # Length of list with results from each job
    cdef bint allExited = 0
    cdef list resList

    # execute the jobs
    for proc in runningJobs:
        proc.start()

    # Show the progress bars
    pbar: tqdm = tqdm(total=jobsCnt, desc="Arch-based prediction", unit="proteome pairs", disable=None, smoothing=0.3, ascii=False, miniters=1, mininterval=2.0, colour='red')

    # write output when available
    while True:
        try:
            resList = results_queue.get(False, 0.01)
            # HACK: include information from ortholog table creation
            ofd.write('{:s}\t{:d}\t{:d}\t{:.3f}\t{:.3f}\t{:.3f}\t{:.3f}\t{:.3f}\t{:.3f}\t{:d}\t{:d}\t{:d}\t{:d}\t{:d}\t{:d}\t{:d}\t{:d}\t{:d}\n'.format(*resList))
            # Update the status bar
            pbar.update(1)

        except queue.Empty:
            pass
        allExited = 1
        for t in runningJobs:
            if t.exitcode is None:
                allExited = 0
                break
        if allExited & results_queue.empty():
            break

    ofd.close()

    # Close the progress bar
    pbar.close()

    # this joins the processes after we got the results
    for proc in runningJobs:
        while proc.is_alive():
            proc.join()

    # stop the counter for the alignment time
    sys.stdout.write(f"\nElapsed time for comparing architectures (seconds):\t{round(perf_counter() - start_time, 3)}\n")
    # logger.warning("Just debugging...")
    # sys.exit(-10)



### Other functions ###
# def check_magnitude_difference(v1:float, v2:float, xDiffThr:float) -> Tuple[int, float]:
@cython.cdivision(True)
# NOTE: cdivision greatly decreases exection time, but many more are  accepted
# cdef inline (int, double) check_magnitude_difference(float v1, float v2, double xDiffThr):
# WARNING: using cdivions requires at least one operand to be flating point
# If both operands are non-floating point types a rounded double is returned
cdef inline (bint, double) check_magnitude_difference(double v1, double v2, double xDiffThr):
    """
    Check the difference in magnitude between two values.
    This can be used for example, to compare length difference, or the arch sizes.

    Return a tuple of type (1, 1.5) where 1 indicates that the xDiffThr was surpassed.
    The last value says how many times one value is smaller (or bigger) than the other (e.g., 2X)
    If the first value is 0 then the threshold was not surpassed
    """

    '''
    cdef bint debug = 1
    if debug:
        print(f"""check_magnitude_difference :: START
        v1:\t{v1}
        v2:\t{v2}
        Diff. threholds:\t{xDiffThr:.2f}""")
    '''

    # Declare main variables
    cdef double v1VSv2, absV1vsV2
    # Output Tuple

    # simply return that it should be kept
    if v1 == v2:
        # resTpl = (0, 1.0)
        return(0, 1.0)
    else:
        # how many times v2 is bigger than v1
        v1VSv2 = 1.0
        # this should be a negative multiplier if v1 is bigger than v2
        # consider which value is the biggest:
        if v2 < v1:
            # NOTE: Python working version
            # v1VSv2 = -round(v1/v2, 2)
            v1VSv2 = -(v1/v2)

        else: # v2 is bigger
            # NOTE: Python working version
            # v1VSv2 = round(v2/v1, 2)
            v1VSv2 = v2/v1

        # print(abs(v1VSv2))
        absV1vsV2 = abs(v1VSv2)
        # Check if the threhold has been surpassed
        # and return the output tuple accordingly
        # if abs(v1VSv2) > xDiffThr: # drop it
        if absV1vsV2 > xDiffThr: # drop it
            # if v1VSv2 < 0:
                # print(v1VSv2, abs(v1VSv2))
                # sys.exit("DEBUG")
            return(1, absV1vsV2)
        else: # keep it
            # print(v1VSv2, abs(v1VSv2))
            return (0, absV1vsV2)



@cython.boundscheck(False)  # Deactivate bounds checking
cpdef inline double dot_view(cnp.float32_t[:] view1, cnp.float32_t[:] view2) nogil:

    cdef double result = 0
    cdef size_t i
    cdef long length = view1.shape[0]
    cdef double el1 = 0
    cdef double el2 = 0
    
    for i in range(length):
      el1 = view1[i]
      el2 = view2[i]
      result += el1*el2
    return result



''' NOTE: this working but the memory view version is much faster 
@cython.boundscheck(False)  # Deactivate bounds checking
cdef inline double dot(cnp.ndarray[cnp.float32_t, ndim = 1] v1, cnp.ndarray[cnp.float32_t, ndim = 1] v2):

    cdef double result = 0
    cdef size_t i
    cdef int length = v1.size
    cdef double el1 = 0
    cdef double el2 = 0
    
    for i in range(length):
      el1 = v1[i]
      el2 = v2[i]
      result += el1*el2

    return result
'''



@cython.cdivision(True) # Use C division instead of Python division
# def cluster_arch_orthologs(sp1: int, sp2: int, M: csr_matrix, outDir: str, writePairs: bool = False) -> tuple[float, int, int, int]:
cdef (double, unsigned long, unsigned long, unsigned long) cluster_arch_orthologs(long sp1, long sp2, object M, str outDir, bint writePairs=0):
    """
    Process arch-based ortholog matrix for two species.
    Create a file with clusters of arch-based orthologs

    Parameters:
    sp1 (int): Name of proteome 1
    sp2 (int): Name of proteome 2
    M (csr_matrix): Matrix containing the arch-based orthologs
    outDir (str): Directory in which the ortholog tables will be stored
    writePairs (str): create file with oortholog pairs

    Returns:
    void

    """

    debugStr: str = f"""cluster_arch_orthologs :: START
    Sp1:\t{sp1}
    Sp2:\t{sp2}
    M:\t{M.nnz}
    Output directory: {outDir}
    Create file with ortholog pairs:\t{writePairs}"""
    logger.debug(debugStr)

    ''' # HACK: pass the matrix directly to avoid loading times
    # Chek that the matrix with orthologs exists
    if not os.path.isfile(mtxPath):
        logger.error(f"The file with the ortholog matrix for {sp1}-{sp2}\nwas not found at\n{mtxPath}")
        sys.exit(-2)

    # Load the matrix
    M = load_npz(mtxPath)
    '''

    # Set the timers
    cdef double start_time, end_time, extime
    start_time = perf_counter()

    # print(f"Mtx format:\t{M.getformat()}")
    cdef unsigned long nnzCnt = M.nnz # Count of nonzero values in matrix

    # Go through the matrix to find
    # orthologs with multiple orthology relationships
    # Set some tmp variables and arrays
    cdef cnp.ndarray[cnp.float32_t, ndim=1] tmpCosineVals = np.zeros(0, dtype=np.float32)
    # Will contain uniq columns/rows indexes with at least 1 non-zero entry
    cdef cnp.ndarray[cnp.uint32_t, ndim=1] nzRows = np.zeros(0, dtype=np.uint32)
    cdef cnp.ndarray[cnp.uint32_t, ndim=1] nzCols = np.zeros(nnzCnt, dtype=np.uint32)
    cdef cnp.ndarray[cnp.uint32_t, ndim=1] candIdx = np.zeros(0, dtype=np.uint32)
    cdef unsigned long loopRangeI, loopRangeJ
    cdef unsigned long tmpRowIdx, tmpColIdx
    # Extract unique indexes of columns and rows with at least 1 non-zero entry
    nzRows, nzCols = [np.unique(arr.astype(np.uint32)) for arr in M.nonzero()]
    loopRangeI = nzRows.size

    # Keep track of columns (protein from sp2)
    # with relationships with multiple proteins from sp1
    # The key is a protein from sp2 (a column index),
    # The value is the a set of protein ids from sp1 (row indexes)
    sp2tosp1ortho: dict[int, set[int]] = {}
    cdef size_t i, j # Indexes to be used in for loops
    cosineValsDict: dict[tuple[int, int], float] = {}

    # print(f"\nProcessing ortholog mtx with {nnzCnt} ortholog relations...")
    for i in range(loopRangeI):
        tmpRowIdx = nzRows[i]
        tmpCosineVals = M.getrow(tmpRowIdx).toarray().ravel()
        # print(f"Extracted cosine values/row:\t{tmpCosineVals}\t{i}")
        candIdx = np.where(tmpCosineVals > 0)[0].astype(np.uint32)
        # print(f"Idxs with cosine > 0/row:\t{candIdx}\t{i}")
        # print(f"Cosine values > 0/row:\t{tmpCosineVals[tmpCosineVals>0]}\t{i}")
        loopRangeJ = candIdx.size
        # Add the values to the matrix
        for j in range(loopRangeJ):
            tmpColIdx = candIdx[j]
            # Add the cosine value in the dictionary
            cosineValsDict[tmpRowIdx, tmpColIdx] = M[tmpRowIdx, tmpColIdx]
            # Associate a set of sp1 genes (row indxs) to each sp2 protein (col idx)
            if tmpColIdx in sp2tosp1ortho:
                sp2tosp1ortho[tmpColIdx].add(tmpRowIdx)
                # print(f"\nRepeated sp2 proteins:\t{tmpColIdx}\t{sp2tosp1ortho[tmpColIdx]}")
                # print(f"current row/candidates:\t{tmpRowIdx}\t{candIdx}")
            else: # inizialize the set
                sp2tosp1ortho[tmpColIdx] = set([tmpRowIdx])
                # print(f"\nFirst appearance for sp2 proteins:\t{tmpColIdx}\t{sp2tosp1ortho[tmpColIdx]}")
                # print(f"current row/candidates:\t{tmpRowIdx}\t{candIdx}")

    # Delete the arrays
    del nzCols
    del nzRows
    del tmpCosineVals
    del candIdx

    # Will have as keys sets of proteins (as tuples of integers) from sp1 with protein 
    # with more than one ortholog relation
    # and as values, set of proteins from sp2 with more than one ortholog relationship
    sp1Set2sp2Set: dict[tuple[Any], set[int]] = {}
    sp1ProtTpl: tuple[Any]
    sp2ProtTpl: tuple[Any]

    # Define some variables
    sp1Set: set[int] = set()
    cdef unsigned long sp1Id, sp2Id
    sp2IdList: list[int] = list(sp2tosp1ortho.keys())
    sp1SetList: list[set[int]] = list(sp2tosp1ortho.values())
    loopRangeI = len(sp2IdList)

    # Create the dictionary with the clusters
    for i in range(loopRangeI):
        sp2Id = sp2IdList.pop()
        sp1Set = sp1SetList.pop()
        sp1ProtTpl = tuple(sorted(sp1Set))
        # print(f"\n{sp2Id}:\t{sp1ProtTpl}")
        if sp1ProtTpl in sp1Set2sp2Set:
            sp1Set2sp2Set[sp1ProtTpl].add(sp2Id)
            # print(f"Repeated sp1 tpl:\t{sp1ProtTpl}\t{sp1Set2sp2Set[sp1ProtTpl]}\t{sp2Id}")
        else:
            # Create the new set
            sp1Set2sp2Set[sp1ProtTpl] = set([sp2Id])
            # print(f"First found sp1 tpl:\t{sp1ProtTpl}\t{sp1Set2sp2Set[sp1ProtTpl]}\t{sp2Id}")

    # Create the final dictionary containing
    # tuples of int both as keys and values
    # this might save as some time if the pairs are created
    # NOTE: the tuples are of variable lenghts
    sp1Tpl2sp2Tpl: dict[tuple[int], tuple[int]] = {}
    sp2Set: set[int] = set()

    # Create dictionary with tuples both as keys and values
    for sp1ProtTpl, sp2Set in sp1Set2sp2Set.items():
        sp1Tpl2sp2Tpl[sp1ProtTpl] = tuple(sorted(sp2Set))

    # Remove the temporary variables
    del sp1Set
    del sp2Set
    del sp1Set2sp2Set
    del sp2tosp1ortho
    del sp2IdList
    del sp1SetList

    '''
    # NOTE: only for debugging
    # Reuse during optimization
    tmpSet: set[int] = set()

    # Make sure that row ids are not repeated
    # NOTE: this should not happen when using overlaps
    for tpl in sp1Set2sp2Set.keys():
        for v in tpl:
            if v in tmpSet:
                print(f"Protein {v} in species {sp1} appreas multiple times!")
                sys.exit(-10)
            else:
                tmpSet.add(v)

    tmpSet.clear()

    # Make sure that column ids are not repeated
    # NOTE: this should not happen when using overlaps
    for sp2Set in sp1Set2sp2Set.values():
        for v in sp2Set:
            if v in tmpSet:
                print(f"Protein {v} in species {sp2} appreas multiple times!")
                sys.exit(-10)
            else:
                tmpSet.add(v)

    tmpSet.clear()
    '''

    # Output cluster in text files
    cdef bint outputTextFiles = 0
    # Counters for groups and pairs
    cdef unsigned long pairsCnt = 0
    cdef unsigned long clstrsCnt = len(sp1Tpl2sp2Tpl)
    cdef unsigned long sp1ProtCnt
    cdef unsigned long sp2ProtCnt
    cdef unsigned long biggestClstr = 0
    cdef unsigned long clstrSize
    # Create the file with ortholog groups
    cdef str outFileBname = f"{sp1}-{sp2}"
    cdef str outTbl = os.path.join(outDir, f"{outFileBname}.arch.ortho.tsv")
    cdef str outPckl = os.path.join(outDir, f"{outFileBname}.arch.ortho.pckl")
    if outputTextFiles:
        ofd: TextIO = open(outTbl, "wt")
    cdef str tmpClstrSp1, tmpClstrSp2
    cdef str tmpCosValsStr
    tmpCosValsLists: list[list[int]] = []
    tmpCosValsList: list[int] = []
    tmpCosValsStrList: list[str] = []
    cdef list sp1TplList = list(sp1Tpl2sp2Tpl.keys())
    cdef list sp2TplList = list(sp1Tpl2sp2Tpl.values())
    # Create the deque that will contain the clusters
    # This data structure will contain the arch based clusters
    # two tuples of integers containing the ids of the proteins
    # from sp1 and sp2 respectively
    # a list of lists stores the cosine values of the clusters
    # for example the following cluster
    # 0.77,0.77:0.60,0.60 23.299 23.4073 33.5536 33.8309
    # will be stored in the deque as follows:
    # ((298, 4072),(5535, 8308), [[0.77,0.77], [0.60,0.60]])
    # Remembering that the indexing should be incremented by 1, then, for example
    # cosine(23.299, 33.8309) = 0.60 and so on...
    # archClstrs: collections.deque[tuple[tuple[int], tuple[int], list[list[int]]]] = deque(maxlen = clstrsCnt)
    cdef dict archClstrs = {} # dict[int, tuple[tuple[int], tuple[int], list[list[int]]]]
    cdef cnp.ndarray[cnp.uint32_t, ndim=1] sp1Ids = np.zeros(0, dtype=np.uint32)
    cdef cnp.ndarray[cnp.uint32_t, ndim=1] sp2Ids = np.zeros(0, dtype=np.uint32)

    # Create ortholog tables, using dicts of tuples
    for i in range(clstrsCnt):
        sp1ProtTpl = sp1TplList[i]
        sp2ProtTpl = sp2TplList[i]
        sp1ProtCnt = len(sp1ProtTpl)
        sp2ProtCnt = len(sp2ProtTpl)
        clstrSize = sp1ProtCnt * sp2ProtCnt
        if clstrSize > biggestClstr:
            biggestClstr = clstrSize
        pairsCnt += clstrSize

        # Create the string with the cosine vals
        for j in range(sp1ProtCnt):
            tmpCosValsList = [cosineValsDict[sp1ProtTpl[j], x] for x in sp2ProtTpl]
            # tmpCosValsLists.append(tmpCosValsList)
            tmpCosineVals = np.array(tmpCosValsList, dtype=np.float32)
            tmpCosValsLists.append(tmpCosineVals)

            if outputTextFiles:
                tmpCosValsStrList.append(",".join([f"{x:.6f}" for x in tmpCosValsList]))

        # add the information in the ouput deque
        # archClstrs.appendleft((sp1ProtTpl, sp2ProtTpl, tmpCosValsLists.copy()))
        sp1Ids = np.array([(x+1) for x in sp1ProtTpl], dtype=np.uint32)
        sp2Ids = np.array([(x+1) for x in sp2ProtTpl], dtype=np.uint32)
        # archClstrs.append(ArchClstr(sp1ProtCnt + sp2ProtCnt, sp1Ids, sp2Ids, tmpCosValsLists.copy()))
        archClstrs[i + 1] = ArchClstr(sp1ProtCnt + sp2ProtCnt, sp1Ids, sp2Ids, tmpCosValsLists.copy())

        tmpCosValsLists.clear()
        # Write the clusters into a text file
        if outputTextFiles:
            # Write the genes from sp1
            tmpClstrSp1 = " ".join([f"{sp1:d}.{x+1}" for x in sp1ProtTpl])
            tmpClstrSp2 = " ".join([f"{sp2:d}.{x+1}" for x in sp2ProtTpl])
            ofd.write(f"{':'.join(tmpCosValsStrList)}\t{tmpClstrSp1}\t{tmpClstrSp2}\n")
            tmpCosValsStrList.clear()

    if outputTextFiles:
        ofd.close()

    # Dump the pickle
    dump(archClstrs, open(outPckl, "wb"))

    '''
    print(f"\nClusters:\t{clstrsCnt}")
    print(f"Pairs:\t{pairsCnt}")
    print(f"Biggest cluster:\t{biggestClstr}")
    print(f"Orthologs in MTX:\t{M.nnz}")
    '''

    cdef list sp1Genes, sp2Genes
    cdef str gSp1, gSp2

    # Write the file with pairs if required
    if writePairs:
        outTbl = os.path.join(outDir, f"{outFileBname}.arch.pairs.tsv")
        ofd = open(outTbl, "wt")
        for i in range(clstrsCnt):
            sp1ProtTpl = sp1TplList.pop()
            sp2ProtTpl = sp2TplList.pop()
            sp1Genes = [f"{sp1}.{x+1}" for x in sp1ProtTpl]
            sp2Genes = [f"{sp2}.{x+1}" for x in sp2ProtTpl]
            for gSp1 in sp1Genes:
                for gSp2 in sp2Genes:
                    ofd.write(f"{gSp1}\t{gSp2}\n")
        ofd.close()

    end_time = perf_counter()
    extime = end_time - start_time

    # Return a tuple with:
    # Execution time
    # Clusters count
    # Biggest cluster
    # Pairs count
    cdef (double, unsigned long, unsigned long, unsigned long) outTpl = (extime, clstrsCnt, biggestClstr, pairsCnt)
    return outTpl



# @cython.cdivision(True) # Use C division instead of Python division
# @cython.boundscheck(False)  # Deactivate bounds checking
cpdef inline bint domain_check(cnp.uint32_t[:] domsSp1, cnp.uint32_t[:] domsSp2, unsigned int domCntSp1, unsigned int  domCntSp2):
    """ This function compares the domains from two architectures as sets of integers.
        Returns False if the pair should be removed.
    """

    cdef unsigned int longest
    cdef unsigned int commonDomCnt = 0
    # cdef double minCommonDoms
    # Will contains the common elements between the arrays
    # cdef cnp.ndarray[cnp.uint16_t, ndim=1] commonDomains = np.zeros(0, dtype=np.uint16)
    # cdef cnp.uint16_t[:] commonDomains

    # Use array view instead

    # Set longest and shortest
    if domCntSp1 >= domCntSp2:
        longest = domCntSp1
    else:
        longest = domCntSp2

    # cdef double result = 0
    # cdef bint keep = 1
    # cdef size_t i
    # cdef Py_ssize_t i
    # cdef int length = view1.shape[0]
    # cdef double el1 = 0
    # cdef double el2 = 0

    # Case in which both contains a single domain
    if (domCntSp1 == 1) and (domCntSp2 == 1):
        if domsSp1[0] == domsSp2[0]:
            return 1
    elif (domCntSp1 < 3) and (domCntSp2 < 3):
        # commonDomains = np.intersect1d(domsSp1, domsSp2)
        # commonDomCnt = commonDomains.shape[0]
        commonDomCnt = np.intersect1d(domsSp1, domsSp2).shape[0]

        # Case in which both have two domains
        if (domCntSp1 == 2) and (domCntSp2 == 2):
            # if commonDomCnt > 0:
            #     print(f"domCntSp1, domCntSp2, interctions lenght:\t{domCntSp1}\t{domCntSp2}\t{commonDomCnt}")
            # Find a swap event

            # if domCntSp1 + domCntSp2 > 3:
            #     if (domsSp1[0] == domsSp2[1]) and (commonDomCnt == 2):
            #         print(f"domCntSp1, domCntSp2, intersection lenght:\t{domCntSp1}\t{domCntSp2}\t{commonDomCnt}")
            #         print(f"[d1Sp1, d2Sp1],[d1Sp2, d2Sp2]:\t[{domsSp1[0]}, {domsSp1[1]}]\t[{domsSp2[0]}, {domsSp2[1]}]")

            if commonDomCnt == 2: # Does not work if there are repeats
                return 1
        else: # 1 domain vs 2 domains (needed ro find human-ecoli switch scenario)
            # if commonDomCnt > 0:
            #     print(f"domCntSp1, domCntSp2, interctions lenght:\t{domCntSp1}\t{domCntSp2}\t{commonDomCnt}")
            # Find a swap event

            # if domCntSp1 + domCntSp2 > 3:
            #     if (domsSp1[0] == domsSp2[1]) and (commonDomCnt == 2):
            #         print(f"domCntSp1, domCntSp2, intersection lenght:\t{domCntSp1}\t{domCntSp2}\t{commonDomCnt}")
            #         print(f"[d1Sp1, d2Sp1],[d1Sp2, d2Sp2]:\t[{domsSp1[0]}, {domsSp1[1]}]\t[{domsSp2[0]}, {domsSp2[1]}]")

            if commonDomCnt == 1: # Works with repeats
                return 1

    # HACK: (more stringent) all the domains must be the same
    # Many domains for each architecture.
    # In this case we want the architectures
    # to share all of the domains 
    else:
        # NOTE: All domains must be the same!
        if np.intersect1d(domsSp1, domsSp2).shape[0] == longest:
            return 1

    '''
    # NOTE: 2/3 of the domains must be the same
    # Many domains for each architecture.
    # In this case we want the architectures to share
    # at least 2/3 of the domain count of the arch with more domains
    else:
        # Compute the minimum number of shared domains
        # minCommonDoms = ceil((longest/3.0)*2)
        # print(f"minCommonDoms:\t{minCommonDoms:.2f}")
        # commonDomains = np.intersect1d(domsSp1, domsSp2)
        # commonDomCnt = commonDomains.shape[0]
        commonDomCnt = np.intersect1d(domsSp1, domsSp2).shape[0]

        # if commonDomCnt >= minCommonDoms:
        if commonDomCnt >= ceil((longest/3.0)*2):
            # print(f"minCommonDoms:\t{minCommonDoms:.2f}")
            return 1
    '''

    return 0



'''#
@cython.cdivision(True) # Use C division instead of Python division
'''#
# def infer_arch_orthologs(sp1: int, sp2: int, sp1ProtCnt: int, sp2ProtCnt: int, sp1ArchsDict: dict[str, Arch], sp2ArchsDict: dict[str, Arch], outDir: str, lenDiffThr: float=3.0, maxCovDiff: float = 0.20, archSizeDiffThr: float=2.0, minCosine: float = 0.5, storeMtx: bool = False) -> None:
# cdef (double, double, double, double, unsigned int, unsigned int, unsigned int, unsigned int, unsigned int, unsigned int, unsigned short) infer_arch_orthologs(int sp1, int sp2, int sp1ProtCnt, int sp2ProtCnt, dict sp1ArchsDict, dict sp2ArchsDict, str outDir, double lenDiffThr, double maxCovDiff, double archSizeDiffThr, double minCosine = 0.5, bint storeMtx = 0):
# HACK: This is working
# in order to restore it uncomment
# code block between ['''#] 
'''#
cdef (double, double, double, double, double, unsigned int, unsigned int, unsigned int, unsigned int, unsigned int, unsigned int, unsigned short, unsigned int, unsigned int) infer_arch_orthologs(int sp1, int sp2, int sp1ProtCnt, int sp2ProtCnt, dict sp1ArchsDict, dict sp2ArchsDict, str outDir, str archOrthoDbDir, double lenDiffThr, double maxCovDiff, double archSizeDiffThr, double minCosine = 0.5, bint storeMtx = 0):
'''#

"""
    Compares architectures from different proteomes based on different features (protein lenghts, architecture size etc.).
    Returns two Sets of protein IDs that can be further compared for orthology inference

    Parameters:
    sp1 (int): Name of proteome 1
    sp2 (int): Name of proteome 2
    sp1ArchsDict dict[str, Arch]: associates a arch to each protein in proteome 1
    sp2ArchsDict dict[str, Arch]: associates a arch to each protein in proteome 2
    outDir (str): Directory in which the prefiltered pairs will be stored
    archOrthoDbDir (str): Directory in which arch-based ortholog tables are stored
    lenDiffThr (float): maximum allowed length difference for a pair of archs
    maxCovDiff (float): maximum allowed difference in query coverage among 2 archs
    archSizeDiffThr (float): maximum allowed arch size difference for a pair of archs
    minCosine (float): minimum cosine similarity for a arch pair to be considered
    storeMtx (bint): store matrixes to disk

    Returns:
    void

"""

'''#
    debugStr: str = f"""infer_arch_orthologs :: START
    Sp1:\t{sp1}
    Sp2:\t{sp2}
    Proteins Sp1:\t{sp1ProtCnt}
    Proteins Sp2:\t{sp2ProtCnt}
    Architectures for Sp1: {len(sp1ArchsDict)}
    Architectures for Sp2: {len(sp2ArchsDict)}
    Output directory: {outDir}
    Directory in which ortholog tables are stored: {archOrthoDbDir}
    Length difference threshold:\t{lenDiffThr:.2f}
    Arch coverage difference threshold:\t{maxCovDiff:.2f}
    Arch size difference threshold:\t{archSizeDiffThr:.2f}
    Minimum cosine similarity:\t{minCosine:.2f}
    Store matrixes:\t{storeMtx}
    """
    logger.debug(debugStr)

    # Check that the cosine similarity is not > 1
    if minCosine > 1:
        logger.warning("The minimum cosine similarity must be < 1.\nIt will be set to 0.5.")
        minCosine = 0.5

    cdef int sp1ArchCnt = len(sp1ArchsDict)
    cdef int sp2ArchCnt = len(sp2ArchsDict)
    cdef long archPairs = sp1ArchCnt * sp2ArchCnt
    cdef long protPairs = sp1ProtCnt * sp2ProtCnt
'''#

''' NOTE: debug only
    print(f"""Possible pairs Arch pairs:
    Archs {sp1}:\t{sp1ArchCnt}
    Archs {sp2}:\t{sp2ArchCnt}
    Proteins {sp1}:\t{sp1ProtCnt}
    Proteins {sp2}:\t{sp2ProtCnt}
    Arch pairs:\t{archPairs}""")
'''

'''#
    # Note that check magnitude requires doubles
    cdef double lenSp1, lenSp2, sizeSp1, sizeSp2, covSp1, covSp2

    # These vectors witll store the temporary embeddings
    # and will be used to compute the cosine similarity
    # memory views for the two vectors
    cdef cnp.float32_t[:] sp1Vec_view
    cdef cnp.float32_t[:] sp2Vec_view
    cdef bint aboveThr
    cdef double tmpDiff
    cdef double cosineSim
    # Counters for rejected and kept arch pairs
    cdef unsigned int rejectCovDiffCnt = 0
    cdef unsigned int rejectLenDiffCnt = 0
    cdef unsigned int rejectSizeDiffCnt = 0
    cdef unsigned int rejectCosine = 0
    cdef unsigned int keptPairsCnt = 0
    cdef size_t i, j # Indexes to be used in for loops

    # Extract the protein IDs that will be filtered
    cdef list sp1Archs = list(sp1ArchsDict.values())
    cdef list sp2Archs = list(sp2ArchsDict.values())
    # Extract the architectures
    cdef list sp1ProtIDs = list(sp1ArchsDict.keys())
    cdef list sp2ProtIDs = list(sp2ArchsDict.keys())

    # Free some memory
    del sp1ArchsDict, sp2ArchsDict

    # Data structures used to store the pairs with hig cosine similarities
    cdef (unsigned short, unsigned short) tmpPair
    highCosinePairs: dict[tuple[int, int], float] = {}
    tmpArchSp1: Arch
    tmpArchSp2: Arch
    cdef double d11, d22, d12

    cdef double start_time, step_start, step_end
    cdef double filter_time, rowwise_time, colwise_time, one2one_time
    start_time = perf_counter()
    step_start = start_time

    # NOTE: directly insert elements in the matrix
    # M = lil_matrix((sp1ProtCnt, sp2ProtCnt), dtype=np.float32)

    # Idexes for the matrix
    # NOTE: protein IDs are 1-indexed
    # while Matrixes are 0-indexes
    cdef unsigned short mtxi, mtxj
    # Use 3 vectors to create matrix
    cdef cnp.ndarray[cnp.uint16_t, ndim=1] mtxiArr = np.zeros(archPairs, dtype=np.uint16)
    cdef cnp.ndarray[cnp.uint16_t, ndim=1] mtxjArr = np.zeros(archPairs, dtype=np.uint16)
    cdef cnp.ndarray[cnp.float32_t, ndim=1] mtxData = np.zeros(archPairs, dtype=np.float32)
    # This is used to keep track of how many element will be written in the matrix
    cdef size_t dataIdx = 0

    #  NOTE: filter order: length, coverage, arch size
    for i in range(sp1ArchCnt):
        tmpArchSp1 = sp1Archs[i]
        lenSp1 = <double>getattr(tmpArchSp1, "seqlen")
        sizeSp1 = <double>getattr(tmpArchSp1, "size")
        sp1Vec_view = getattr(tmpArchSp1, "embedding")
        covSp1 = getattr(tmpArchSp1, "coverage")
        # Row index for matrix
        mtxi = sp1ProtIDs[i] - 1

        for j in range(sp2ArchCnt):
            tmpArchSp2 = sp2Archs[j]
            # Check the length difference
            lenSp2 = <double>getattr(tmpArchSp2, "seqlen")
            # Check the length difference
            aboveThr, tmpDiff = check_magnitude_difference(v1=lenSp1, v2=lenSp2, xDiffThr=lenDiffThr)
            if aboveThr:
                rejectLenDiffCnt += 1
            # Check coverage difference
            else:
                covSp2 = getattr(tmpArchSp2, "coverage")
                # Skip if coverage is too different
                if abs(covSp1 - covSp2) > maxCovDiff:
                    rejectCovDiffCnt += 1
                else:
                    # Check the difference in Arch.size
                    # Set the required values
                    sizeSp2 = <double>getattr(tmpArchSp2, "size")
                    # TODO: Remember to keep short archs regardless
                    # For example, archs with < 4 words
                    # This would allow us to find orthologs at domain level after duplication
                    # The code sahould be as follows:
                    if (sizeSp1 < 4) and (sizeSp2 < 4):
                    # if (sizeSp1 < archSizeDiffThr) and (sizeSp2 < archSizeDiffThr):
                        sp2Vec_view = getattr(tmpArchSp2, "embedding")
                        # Use re-implemented dot product using memory views
                        d11 = dot_view(sp1Vec_view, sp1Vec_view)
                        d22 = dot_view(sp2Vec_view, sp2Vec_view)
                        d12 = dot_view(sp1Vec_view, sp2Vec_view)
                        cosineSim = d12 / sqrt(d11 * d22)

                        if cosineSim >= minCosine:
                            keptPairsCnt += 1
                            # Update the arrays
                            mtxj = sp2ProtIDs[j] - 1
                            mtxiArr[dataIdx] = mtxi
                            mtxjArr[dataIdx] = mtxj
                            mtxData[dataIdx] = cosineSim
                            dataIdx += 1
                            # Add in dictionary
                            tmpPair = (mtxi, mtxj)
                            highCosinePairs[tmpPair] = cosineSim
                        else:
                            rejectCosine += 1
                    else:
                        aboveThr, tmpDiff = check_magnitude_difference(v1=sizeSp1, v2=sizeSp2, xDiffThr=archSizeDiffThr)
                        # print(f"Size check:\t{sizeSp1}\t{sizeSp2}\t{archSizeDiffThr}\t{aboveThr}\t{tmpDiff}")
                        if aboveThr:
                            # Reject the pair
                            rejectSizeDiffCnt += 1
                        else:
                            # HACK: this is computationally expensive
                            sp2Vec_view = getattr(tmpArchSp2, "embedding")
                            # Use re-implemented dot product using memory views
                            d11 = dot_view(sp1Vec_view, sp1Vec_view)
                            d22 = dot_view(sp2Vec_view, sp2Vec_view)
                            d12 = dot_view(sp1Vec_view, sp2Vec_view)
                            cosineSim = d12 / sqrt(d11 * d22)

                            if cosineSim >= minCosine:
                                keptPairsCnt += 1
                                # Update the arrays
                                mtxj = sp2ProtIDs[j] - 1
                                mtxiArr[dataIdx] = mtxi
                                mtxjArr[dataIdx] = mtxj
                                mtxData[dataIdx] = cosineSim
                                dataIdx += 1
                                # Add to dictionary
                                tmpPair = (mtxi, mtxj)
                                highCosinePairs[tmpPair] = cosineSim
                            else:
                                rejectCosine += 1

    # remove some unecessary objects
    del sp1Vec_view
    del sp2Vec_view

    # Create COO Matrix using the slices of the vectors
    M = csr_matrix((mtxData[:dataIdx], (mtxiArr[:dataIdx], mtxjArr[:dataIdx])), shape=(sp1ProtCnt, sp2ProtCnt), dtype=np.float32)
    cdef unsigned int nnzCnt
    nnzCnt = M.nnz # Count of nonzero values in matrix
    cdef double sparsity = 1 - (<double>nnzCnt / <double>protPairs)
'''#

''' NOTE: debug only
    print(f"Protein pairs:\t{protPairs}")
    print(f"M.shape:\t{M.shape}")
    print(f"M.size:\t{M.size}")
    print(f"M.nnz:\t{nnzCnt}")
    print(f"M.density:\t{(<double>nnzCnt / <double>protPairs)}")
    print(f"M.sparsity:\t{sparsity}")
    print(f"High-cosine arch pairs:\t{len(highCosinePairs)}")
'''

'''#
    # Store the matrix to disk
    cdef str pairName = f"{sp1}-{sp2}"
    cdef str outMtxPath
    ofdBin: BinaryIO
'''#

''' NOTE: debug only
    if storeMtx:
        outMtxPath = os.path.join(outDir, f"{pairName}.cosine.mtx.npz")
        # save the matrix
        ofdBin = open(outMtxPath, "wb")
        save_npz(outMtxPath, M, compressed=True)
        ofdBin.close()
'''

''' HACK: this is working!
    #  NOTE: filter order: length, arch size
    for i in range(sp1ArchCnt):
        tmpArchSp1 = sp1Archs[i]
        lenSp1 = <double>getattr(tmpArchSp1, "seqlen")
        sizeSp1 = <double>getattr(tmpArchSp1, "size")
        # sp1TmpId = sp1ProtIDs[i]
        sp1Vec_view = getattr(tmpArchSp1, "embedding")
        # sp1Phrase = " ".join(getattr(tmpArchSp1, "phrase").tolist())

        for j in range(sp2ArchCnt):
            tmpArchSp2 = sp2Archs[j]
            lenSp2 = <double>getattr(tmpArchSp2, "seqlen")
            # sp2TmpId = sp2ProtIDs[j]
            # Check the length difference
            aboveThr, tmpDiff = check_magnitude_difference(v1=lenSp1, v2=lenSp2, xDiffThr=lenDiffThr)
            if aboveThr:
                # print(lenSp1, lenSp2, lenDiffThr, tmpDiff, aboveThr)
                rejectLenDiffCnt += 1
            else:
                # Check the difference in Arch.size
                # Set the required values
                sizeSp2 = <double>getattr(tmpArchSp2, "size")
                # TODO: Remember to keep short archs regardless
                # For example, archs with <4 words
                # This would allow us to find orthologs at domain level after duplication
                # The code sahould be as follows:
                if (sizeSp1 < 4) and (sizeSp2 < 4):
                # if (sizeSp1 < archSizeDiffThr) and (sizeSp2 < archSizeDiffThr):
                    keptPairsCnt += 1
                    sp2Vec_view = getattr(tmpArchSp2, "embedding")
                    # sp2Phrase = " ".join(getattr(tmpArchSp2, "phrase").tolist())

                    # Use re-implemented dot product using memory views
                    d11 = dot_view(sp1Vec_view, sp1Vec_view)
                    d22 = dot_view(sp2Vec_view, sp2Vec_view)
                    d12 = dot_view(sp1Vec_view, sp2Vec_view)
                    cosineSim = d12 / sqrt(d11 * d22)

                    # print(cosineSim)
                    # ofd.write(f"{sp1Phrase}\t{sp2Phrase}\t{cosineSim}\n")
                    # if keptPairsCnt == 5:
                    #     sys.exit("Exit :: IF")

                else:
                    aboveThr, tmpDiff = check_magnitude_difference(v1=sizeSp1, v2=sizeSp2, xDiffThr=archSizeDiffThr)
                    # print(f"Size check:\t{sizeSp1}\t{sizeSp2}\t{archSizeDiffThr}\t{aboveThr}\t{tmpDiff}")
                    if aboveThr:
                        # Reject the pair
                        rejectSizeDiffCnt += 1
                    else:
                        keptPairsCnt += 1
                        sp2Vec_view = getattr(tmpArchSp2, "embedding")
                        # sp2Phrase = " ".join(getattr(tmpArchSp2, "phrase").tolist())

                        # Use re-implemented dot product using memory views
                        d11 = dot_view(sp1Vec_view, sp1Vec_view)
                        d22 = dot_view(sp2Vec_view, sp2Vec_view)
                        d12 = dot_view(sp1Vec_view, sp2Vec_view)
                        cosineSim = d12 / sqrt(d11 * d22)

                        # print(cosineSim)
                        # ofd.write(f"{sp1Phrase}\t{sp2Phrase}\t{cosineSim}\n")
                        # if keptPairsCnt == 5:
                        #     sys.exit("Exit :: ELSE")
                        # cosineSim = np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
'''

'''#
    # Get the execution time
    step_end = perf_counter()
    filter_time = step_end - step_start
    # sys.stdout.write(f"\nElapsed time for filtering and filling CSR sparse matrix (seconds):\t{filter_time:.3f}\n")

    # Free some memory
    del sp1ProtIDs, sp2ProtIDs, sp1Archs, sp2Archs, tmpArchSp1, tmpArchSp2

    # Reset timers
    step_start = step_end

    # Find ROW-WISE candidates
    # Reset idx arrays
    cdef cnp.ndarray[cnp.float32_t, ndim=1] tmpCosineVals = np.zeros(nnzCnt, dtype=np.float32)
    # Will contain uniq columns/rows indexes with at least 1 non-zero entry
    cdef cnp.ndarray[cnp.uint16_t, ndim=1] nzRows = np.zeros(0, dtype=np.uint16)
    cdef cnp.ndarray[cnp.uint16_t, ndim=1] nzCols = np.zeros(nnzCnt, dtype=np.uint16)
    cdef cnp.ndarray[cnp.uint16_t, ndim=1] candIdx = np.zeros(0, dtype=np.uint16)
    cdef double tmpMaxCosine
    cdef unsigned long loopRangeI, loopRangeJ
    cdef unsigned short tmpRowIdx, tmpColIdx

    # Extract unique indexes of columns and rows with at least 1 non-zero entry
    nzRows, nzCols = [np.unique(arr.astype(np.uint16)) for arr in M.nonzero()]
    loopRangeI = nzRows.size
    # Reset the idx arrays used to construct the matrixes
    mtxiArr = np.zeros(nnzCnt, dtype=np.uint16)
    mtxjArr = np.zeros(nnzCnt, dtype=np.uint16)
    dataIdx = 0

    # print(f"\nStart pruning {loopRangeI} rows...")
    for i in range(loopRangeI):
        tmpRowIdx = nzRows[i]
        # print(f"row/loop idx:\t{tmpRowIdx}\t{i}")
        tmpCosineVals = M.getrow(tmpRowIdx).toarray().ravel()
        tmpMaxCosine = tmpCosineVals[tmpCosineVals > 0].max()
        # print(tmpMaxCosine)
        candIdx = np.where(tmpCosineVals == tmpMaxCosine)[0].astype(np.uint16)
        # print(tmpRowIdx, candIdx)

        # Add the values to the matrix
        loopRangeJ = candIdx.size
        for j in range(loopRangeJ):
            # Fill the vectors
            mtxiArr[dataIdx] = tmpRowIdx
            mtxjArr[dataIdx] = candIdx[j]
            # mtxData can be filled later with ones
            dataIdx += 1

    # Create matrix using 3 vectors
    cdef cnp.ndarray[cnp.uint8_t, ndim=1] mtxDataInt = np.ones(dataIdx, dtype=np.uint8)
    MrowOrtho = csr_matrix((mtxDataInt, (mtxiArr[:dataIdx], mtxjArr[:dataIdx])), shape=(sp1ProtCnt, sp2ProtCnt), dtype=np.uint8)
    sparsity = 1 - (<double>MrowOrtho.nnz / <double>protPairs)
'''#


''' NOTE: debug only
    print(f"MrowOrtho.shape:\t{MrowOrtho.shape}")
    print(f"MrowOrtho.size:\t{MrowOrtho.size}")
    print(f"MrowOrtho.nnz:\t{MrowOrtho.nnz}")
    print(f"MrowOrtho.density:\t{(MrowOrtho.nnz / protPairs)}")
    print(f"MrowOrtho.sparsity:\t{sparsity}")
    print(f"High-cosine arch pairs:\t{len(highCosinePairs)}")

    # Store the matrix into a file
    if storeMtx:
        outMtxPath = os.path.join(outDir, f"{pairName}.row.candidate.mtx.npz")
        # save the matrix
        ofdBin = open(outMtxPath, "wb")
        save_npz(outMtxPath, MrowOrtho, compressed=True)
        ofdBin.close()
'''

'''#
    # Get the execution time
    step_end = perf_counter()
    rowwise_time = step_end - step_start
    # sys.stdout.write(f"\nElapsed time for selecting row-wise candidate orthologs (seconds):\t{rowwise_time:.3f}\n")

    # Reset the timer
    step_start = step_end
    # Find candidates column-wise
    # Reset all required arrays and variables
    tmpCosineVals = np.zeros(nnzCnt, dtype=np.float32)
    candIdx = np.zeros(0, dtype=np.uint16)
    tmpMaxCosine = 0.
    tmpRowIdx = 0
    tmpColIdx = 0
    loopRangeJ = nzCols.size
    loopRangeI = 0
    mtxiArr = np.zeros(nnzCnt, dtype=np.uint16)
    mtxjArr = np.zeros(nnzCnt, dtype=np.uint16)
    dataIdx = 0

    # NOTE: Optimization shows that CSC mtx is the fastest
    M = M.tocsc()
    # print(f"\nStart pruning {loopRangeJ} columns...")
    for j in range(loopRangeJ):
        tmpColIdx = nzCols[j]
        # print(f"column/loop idx:\t{tmpColIdx}\t{j}")
        tmpCosineVals = M.getcol(tmpColIdx).toarray().ravel()
        tmpMaxCosine = tmpCosineVals[tmpCosineVals > 0].max()
        # print(tmpMaxCosine)
        candIdx = np.where(tmpCosineVals == tmpMaxCosine)[0].astype(np.uint16)
        # Add the values to the matrix
        loopRangeI = candIdx.size
        # if candIdx.size > 1:
            # print(candIdx, tmpColIdx)

        for i in range(loopRangeI):
            # print(i)
            # Fill the vectors
            mtxiArr[dataIdx] = candIdx[i]
            mtxjArr[dataIdx] = tmpColIdx
            dataIdx += 1

    # Create the matrix
    mtxDataInt = np.ones(dataIdx, dtype=np.uint8)
    McolOrtho = csr_matrix((mtxDataInt, (mtxiArr[:dataIdx], mtxjArr[:dataIdx])), shape=(sp1ProtCnt, sp2ProtCnt), dtype=np.uint8)
    sparsity = 1 - (<double>McolOrtho.nnz / <double>protPairs)
'''#


''' NOTE: debug only
    print(f"McolOrtho.shape:\t{McolOrtho.shape}")
    print(f"McolOrtho.size:\t{McolOrtho.size}")
    print(f"McolOrtho.nnz:\t{McolOrtho.nnz}")
    print(f"McolOrtho.density:\t{(McolOrtho.nnz / protPairs)}")
    print(f"McolOrtho.sparsity:\t{sparsity}")
    print(f"High-cosine arch pairs:\t{len(highCosinePairs)}")

    # Store the matrix into a file
    if storeMtx:
        outMtxPath = os.path.join(outDir, f"{pairName}.col.candidate.mtx.npz")
        # save the matrix
        ofdBin = open(outMtxPath, "wb")
        save_npz(outMtxPath, McolOrtho, compressed=True)
        ofdBin.close()
'''

'''#
    # Get the execution time
    step_end = perf_counter()
    colwise_time = step_end - step_start
    # sys.stdout.write(f"\nElapsed time for selecting column-wise candidate orthologs (seconds):\t{colwise_time:.3f}\n")
    # reset the timer
    step_start = step_end

    # Sum the two matrixes and extract potential orthologs
    Moverlap = MrowOrtho + McolOrtho

    # Free some memory
    del McolOrtho, MrowOrtho, tmpCosineVals

    # Extract unique indexes of columns and rows with at least 1 non-zero entry
    nzRows, nzCols = [np.unique(arr.astype(np.uint16)) for arr in Moverlap.nonzero()]
    sparsity = 1 - (<double>Moverlap.nnz / <double>protPairs)
'''#

''' NOTE: debug only
    print(f"\nProtein pairs:\t{protPairs}")
    print(f"Moverlap.shape:\t{Moverlap.shape}")
    print(f"Moverlap.size:\t{Moverlap.size}")
    print(f"Moverlap.nnz:\t{Moverlap.nnz}")
    print(f"Moverlap.density:\t{(<double>Moverlap.nnz / <double>protPairs)}")
    print(f"Moverlap.sparsity:\t{sparsity}")
    print(f"High-cosine arch pairs:\t{len(highCosinePairs)}")
    # Store the matrix into a file
    if storeMtx:
        outMtxPath = os.path.join(outDir, f"{pairName}.sum.candidate.mtx.npz")
        # save the matrix
        ofdBin = open(outMtxPath, "wb")
        save_npz(outMtxPath, Moverlap, compressed=True)
        ofdBin.close()
'''

'''#
    # Reset some of the variables
    cdef bint overlapOnly = 0
    cdef cnp.ndarray[cnp.uint8_t, ndim=1] tmpOverlapVals = np.zeros(0, dtype=np.uint8)
    cdef cnp.ndarray[cnp.uint32_t, ndim=1] tmpNonZeroCols = np.zeros(0, dtype=np.uint32)
    # cdef cnp.ndarray[cnp.uint32_t, ndim=1] tmpNoOverlapCols = np.zeros(0, dtype=np.uint32)
    nnzCnt = Moverlap.nnz
    mtxiArr = np.zeros(nnzCnt, dtype=np.uint16)
    mtxjArr = np.zeros(nnzCnt, dtype=np.uint16)
    mtxData = np.zeros(nnzCnt, dtype=np.float32)
    dataIdx = 0
    loopRangeI = nzRows.size
    loopRangeJ = nzCols.size

    # Create the matrix with the ortholog relations
    # TODO: implement the non-overlap version (in which entries with 1 and 2 in overlap matrix are considered)
    if overlapOnly:
        # Select only overlapping values (e.g., M[i, j] = 2)
        for i in range(loopRangeI):
            tmpRowIdx = nzRows[i]
            # Extract only indexes with overlaps
            # print(f"\nrow/loop idx:\t{tmpRowIdx}\t{i}")
            tmpOverlapVals = Moverlap.getrow(tmpRowIdx).toarray().ravel()
            # Extract indexes of columns which have value = 2
            tmpNonZeroCols = np.asarray(tmpOverlapVals > 1).nonzero()[0].astype(np.uint32)
            # print(f"tmpOverlapVals.size:\t{tmpOverlapVals.size}")
            loopRangeJ = tmpNonZeroCols.size
            # Iterate through the rows and write the candidate pairs
            for j in range(loopRangeJ):
                tmpColIdx = tmpNonZeroCols[j]
                # print(f"tmpColIdx:\t{tmpColIdx}")
                mtxiArr[dataIdx] = tmpRowIdx
                mtxjArr[dataIdx] = tmpColIdx
                # mtxData[dataIdx] = highCosinePairs[(tmpRowIdx, tmpColIdx)]
                mtxData[dataIdx] = highCosinePairs.pop((tmpRowIdx, tmpColIdx))
                dataIdx += 1
    # FIXME: Note that when overlap is not used,
    # the creation of the overlap matrix is redundant
    else:
        # Select all elements regardless of the overlap
        for i in range(loopRangeI):
            tmpRowIdx = nzRows[i]
            tmpNonZeroCols = Moverlap.getrow(tmpRowIdx).toarray().ravel().nonzero()[0].astype(np.uint32)
            # print(f"tmpOverlapVals.size:\t{tmpOverlapVals.size}")
            loopRangeJ = tmpNonZeroCols.size
            # Iterate through the rows and write the candidate pairs
            for j in range(loopRangeJ):
                tmpColIdx = tmpNonZeroCols[j]
                # print(f"tmpColIdx:\t{tmpColIdx}")
                mtxiArr[dataIdx] = tmpRowIdx
                mtxjArr[dataIdx] = tmpColIdx
                # mtxData[dataIdx] = highCosinePairs[(tmpRowIdx, tmpColIdx)]
                mtxData[dataIdx] = highCosinePairs.pop((tmpRowIdx, tmpColIdx))
                dataIdx += 1

    # Create the matrix with 1-to-1 ortholog relations (based on the max cosine)
    M1to1ortho = csr_matrix((mtxData[:dataIdx], (mtxiArr[:dataIdx], mtxjArr[:dataIdx])), shape=(sp1ProtCnt, sp2ProtCnt), dtype=np.float32)
    nnzCnt = M1to1ortho.nnz # Count of nonzero values in matrix
    sparsity = 1 - (<double>nnzCnt / <double>protPairs)
'''#

''' FIXME: remove when mature
    print(f"\nProtein pairs:\t{protPairs}")
    print(f"M1to1ortho.shape:\t{M1to1ortho.shape}")
    print(f"M1to1ortho.size:\t{M1to1ortho.size}")
    print(f"M1to1ortho.nnz:\t{nnzCnt}")
    print(f"M1to1ortho.density:\t{(<double>nnzCnt / <double>protPairs)}")
    print(f"M1to1ortho.sparsity:\t{sparsity}")
    print(f"High-cosine arch pairs:\t{len(highCosinePairs)}")
'''

'''
    # Store the matrix into a file
    if storeMtx:
        outMtxPath = os.path.join(outDir, f"{pairName}.1to1.ortho.mtx.npz")
        # save the matrix
        ofdBin = open(outMtxPath, "wb")
        save_npz(outMtxPath, M1to1ortho, compressed=True)
        ofdBin.close()
'''

'''#
    # Get the execution time
    step_end = perf_counter()
    one2one_time = step_end - step_start
    nnzCnt = M1to1ortho.size
    # sys.stdout.write(f"\nElapsed time to generate overlap matrix (seconds):\t{one2one_time:.3f}\n")

    debugStr = f"""infer_arch_orthologs :: SUMMARY
    Starting pairs:\t{archPairs:d}
    Keep:\t{keptPairsCnt}
    Reject (by length):\t{rejectLenDiffCnt}
    Reject (by coverage):\t{rejectCovDiffCnt}
    Reject (by size):\t{rejectSizeDiffCnt}
    Reject (by cosine < {minCosine:.2f}):\t{rejectCosine}
    1-to-1 ortho-archs:\t{nnzCnt}
    Total ex-time (seconds):\t{(step_end - start_time):.3f}"""
    logger.debug(debugStr)

    # Create the ortholog tables
    cdef (double, unsigned int, unsigned int, unsigned int) clsteringTpl
    # The tuple contains:
    # Execution time
    # Clusters count
    # Biggest clusters (number of pairs)
    # Number of orhtolog pairs in the cluster

    clusteringTpl = cluster_arch_orthologs(sp1=sp1, sp2=sp2, M=M1to1ortho, outDir=archOrthoDbDir, writePairs=1)

    # Output tuple
    # cdef (double, double, double, double, unsigned int, unsigned int, unsigned int, unsigned int, unsigned int, unsigned int, unsigned short) outTpl
    # outTpl = (filter_time, rowwise_time, colwise_time, one2one_time, protPairs, archPairs, rejectLenDiffCnt, rejectCovDiffCnt, rejectSizeDiffCnt, rejectCosine, nnzCnt)
    # HACK: add the information from the clustering

    # (double, double, double, double, double, unsigned int, unsigned int, unsigned int, unsigned int, unsigned int, unsigned int, unsigned short, unsigned int, unsigned int, unsigned int)

    cdef (double, double, double, double, double, unsigned int, unsigned int, unsigned int, unsigned int, unsigned int, unsigned int, unsigned short, unsigned int, unsigned int) outTpl
    outTpl = (filter_time, rowwise_time, colwise_time, one2one_time, clusteringTpl[0], protPairs, archPairs, rejectLenDiffCnt, rejectCovDiffCnt, rejectSizeDiffCnt, rejectCosine, nnzCnt, clusteringTpl[1], clusteringTpl[2])

    return outTpl
'''#



@cython.cdivision(True) # Use C division instead of Python division
# def infer_arch_orthologs(sp1: int, sp2: int, sp1ProtCnt: int, sp2ProtCnt: int, sp1ArchsDict: dict[str, Arch], sp2ArchsDict: dict[str, Arch], mtxDir: str, lenDiffThr: float=3.0, maxCovDiff: float = 0.20, domCntDiffThr: float=2.5, minCosine: float = 0.5, storeMtx: bool = False) -> None:
cdef (double, double, double, double, double, unsigned long, unsigned long, unsigned long, unsigned long, unsigned long, unsigned long, unsigned long, unsigned long, unsigned long) infer_arch_orthologs(long sp1, long sp2, long sp1ProtCnt, long sp2ProtCnt, dict sp1ArchsDict, dict sp2ArchsDict, str mtxDir, str archOrthoDbDir, double lenDiffThr, double maxCovDiff, double domCntDiffThr, double minCosine = 0.5, bint storeMtx = 0):

    """
    Compares architectures from different proteomes based on different features (protein lenghts, architecture size etc.).
    Returns two Sets of protein IDs that can be further compared for orthology inference

    Parameters:
    sp1 (int): Name of proteome 1
    sp2 (int): Name of proteome 2
    sp1ArchsDict dict[str, Arch]: associates a arch to each protein in proteome 1
    sp2ArchsDict dict[str, Arch]: associates a arch to each protein in proteome 2
    mtxDir (str): Directory in which the prefiltered pairs and matrices will be stored
    archOrthoDbDir (str): Directory in which arch-based ortholog tables are stored
    lenDiffThr (float): maximum allowed length difference for a pair of archs
    maxCovDiff (float): maximum allowed difference in query coverage among 2 archs
    domCntDiffThr (float): maximum allowed difference in domain count between a pair of archs
    minCosine (float): minimum cosine similarity for a arch pair to be considered
    storeMtx (bint): store matrixes to disk

    Returns:
    void

    """

    debugStr: str = f"""infer_arch_orthologs :: START
    Sp1:\t{sp1}
    Sp2:\t{sp2}
    Proteins Sp1:\t{sp1ProtCnt}
    Proteins Sp2:\t{sp2ProtCnt}
    Architectures for Sp1: {len(sp1ArchsDict)}
    Architectures for Sp2: {len(sp2ArchsDict)}
    Output directory: {mtxDir}
    Directory in which ortholog tables are stored: {archOrthoDbDir}
    Length difference threshold:\t{lenDiffThr:.2f}
    Arch coverage difference threshold:\t{maxCovDiff:.2f}
    Domain count difference threshold:\t{domCntDiffThr:.2f}
    Minimum cosine similarity:\t{minCosine:.2f}
    Store matrixes:\t{storeMtx}
    """
    logger.debug(debugStr)

    # Update the output directories to have the subdirectory with Sp1
    archOrthoDbDir = f"{archOrthoDbDir}/{sp1:d}"
    makedir(archOrthoDbDir)
    mtxDir = f"{mtxDir}/{sp1:d}"
    makedir(mtxDir)

    # Check that the cosine similarity is not > 1
    if minCosine > 1:
        logger.warning("The minimum cosine similarity must be < 1.\nIt will be set to 0.5.")
        minCosine = 0.5

    cdef unsigned long sp1ArchCnt = len(sp1ArchsDict)
    cdef unsigned long sp2ArchCnt = len(sp2ArchsDict)
    cdef unsigned long archPairs = sp1ArchCnt * sp2ArchCnt
    cdef unsigned long protPairs = sp1ProtCnt * sp2ProtCnt

    ''' NOTE: debug only
    print(f"""Possible pairs Arch pairs:
    Archs {sp1}:\t{sp1ArchCnt}
    Archs {sp2}:\t{sp2ArchCnt}
    Proteins {sp1}:\t{sp1ProtCnt}
    Proteins {sp2}:\t{sp2ProtCnt}
    Arch pairs:\t{archPairs}""")
    '''

    # Note that check magnitude requires doubles
    cdef double lenSp1, lenSp2, covSp1, covSp2
    cdef unsigned int domCntSp1, domCntSp2
    # These vectors witll store the temporary embeddings
    # and will be used to compute the cosine similarity
    # memory views for the two vectors
    cdef cnp.float32_t[:] sp1Vec_view
    cdef cnp.float32_t[:] sp2Vec_view
    cdef cnp.uint32_t[:] domsSp1_view
    cdef cnp.uint32_t[:] domsSp2_view

    cdef bint aboveThr
    # Outcome from domain check
    cdef bint domCheckOK
    cdef double tmpDiff
    cdef double cosineSim
    # Counters for rejected and kept arch pairs
    cdef unsigned long rejectCovDiffCnt = 0
    cdef unsigned long rejectLenDiffCnt = 0
    cdef unsigned long rejectSizeDiffCnt = 0
    cdef unsigned long rejectCosine = 0
    cdef unsigned long rejectDomCheck = 0
    cdef unsigned long keptPairsCnt = 0
    cdef size_t i, j # Indexes to be used in for loops

    # Extract the protein IDs that will be filtered
    cdef list sp1Archs = list(sp1ArchsDict.values())
    cdef list sp2Archs = list(sp2ArchsDict.values())
    # Extract the architectures
    cdef list sp1ProtIDs = list(sp1ArchsDict.keys())
    cdef list sp2ProtIDs = list(sp2ArchsDict.keys())

    # Free some memory
    del sp1ArchsDict, sp2ArchsDict

    # Data structures used to store the pairs with hig cosine similarities
    cdef (unsigned long, unsigned long) tmpPair
    highCosinePairs: dict[tuple[int, int], float] = {}
    tmpArchSp1: Arch
    tmpArchSp2: Arch
    cdef double d11, d22, d12

    cdef double start_time, step_start, step_end
    cdef double filter_time, rowwise_time, colwise_time, one2one_time
    start_time = perf_counter()
    step_start = start_time

    # NOTE: directly insert elements in the matrix
    # M = lil_matrix((sp1ProtCnt, sp2ProtCnt), dtype=np.float32)

    # Idexes for the matrix
    # NOTE: protein IDs are 1-indexed
    # while Matrixes are 0-indexes
    cdef unsigned long mtxi, mtxj
    # Use 3 vectors to create matrix
    cdef cnp.ndarray[cnp.uint32_t, ndim=1] mtxiArr = np.zeros(archPairs, dtype=np.uint32)
    cdef cnp.ndarray[cnp.uint32_t, ndim=1] mtxjArr = np.zeros(archPairs, dtype=np.uint32)
    cdef cnp.ndarray[cnp.float32_t, ndim=1] mtxData = np.zeros(archPairs, dtype=np.float32)
    # This is used to keep track of how many element will be written in the matrix
    cdef size_t dataIdx = 0

    '''
    # NOTE: filter order: length, coverage, arch size
    '''
    for i in range(sp1ArchCnt):
        tmpArchSp1 = sp1Archs[i]
        lenSp1 = <double>getattr(tmpArchSp1, "seqlen")
        domCntSp1 = getattr(tmpArchSp1, "domCnt")
        sp1Vec_view = getattr(tmpArchSp1, "embedding")
        covSp1 = getattr(tmpArchSp1, "coverage")
        # Row index for matrix
        mtxi = sp1ProtIDs[i] - 1

        for j in range(sp2ArchCnt):
            tmpArchSp2 = sp2Archs[j]
            # Check the length difference
            lenSp2 = <double>getattr(tmpArchSp2, "seqlen")
            # Check the length difference
            aboveThr, tmpDiff = check_magnitude_difference(v1=lenSp1, v2=lenSp2, xDiffThr=lenDiffThr)
            if aboveThr:
                rejectLenDiffCnt += 1
            # Check coverage difference
            else:
                covSp2 = getattr(tmpArchSp2, "coverage")
                # Skip if coverage is too different
                if abs(covSp1 - covSp2) > maxCovDiff:
                    rejectCovDiffCnt += 1
                else:
                    # Check the difference in Arch.size
                    # Set the required values
                    domCntSp2 = getattr(tmpArchSp2, "domCnt")
                    # TODO: Remember to keep short archs regardless
                    # For example, archs with < 4 words
                    # This would allow us to find orthologs at domain level after duplication
                    # The code sahould be as follows:
                    if (domCntSp1 < 3) and (domCntSp2 < 3):
                        sp2Vec_view = getattr(tmpArchSp2, "embedding")
                        # Use re-implemented dot product using memory views
                        d11 = dot_view(sp1Vec_view, sp1Vec_view)
                        d22 = dot_view(sp2Vec_view, sp2Vec_view)
                        d12 = dot_view(sp1Vec_view, sp2Vec_view)
                        cosineSim = d12 / sqrt(d11 * d22)

                        if cosineSim >= minCosine:
                            # Extract column index
                            mtxj = sp2ProtIDs[j] - 1


                            ''' NOTE: debug only
                            '''
                            # Check that domains compared are same
                            # and the set of domains compares are same
                            if cosineSim < 1:
                                # Obtain the views from the domain ids
                                domsSp1_view = getattr(tmpArchSp1, "domWvIdx")
                                domsSp2_view = getattr(tmpArchSp2, "domWvIdx")

                                # print(f"Pair:\t{mtxi}-{mtxj}")
                                domCheckOK = domain_check(domsSp1_view, domsSp2_view, domCntSp1, domCntSp2)
                                if domCheckOK:
                                    '''
                                    print(f"""Domain counts < 3 AND cosine < 1:
    Pair {mtxi+1}-{mtxj+1}\cosine\lengths:\t{cosineSim:.3f}\t{lenSp1}\t{lenSp2}
    Domain Counts {sp1}\\{sp2}:\t{domCntSp1}\t{domCntSp2}
    Archs:\t{getattr(tmpArchSp1, "phrase")}\t{getattr(tmpArchSp2, "phrase")}""")
                                    '''

                                    '''
                                    if domCntSp1 + domCntSp2 >= 4:
                                        print(f"""Domain counts < 3 AND cosine < 1 AND > 2 domains:
    Pair {mtxi+1}-{mtxj+1}\cosine\lengths:\t{cosineSim:.3f}\t{lenSp1}\t{lenSp2}
    Domain Counts {sp1}\{sp2}:\t{domCntSp1}\t{domCntSp2}
    Archs:\t{getattr(tmpArchSp1, "phrase")}\t{getattr(tmpArchSp2, "phrase")}""")
                                    '''

                                    ''' NOTE: print swap event
                                    if domCntSp1 + domCntSp2 > 3:
                                        print(domsSp1_view[0] == domsSp2_view[1])
                                        if domsSp1_view[0] == domsSp2_view[1]:
                                            print(f"""Domain counts < 3 AND cosine < 1 AND > 2 domains:
    Pair {mtxi+1}-{mtxj+1}\cosine\lengths:\t{cosineSim:.3f}\t{lenSp1}\t{lenSp2}
    Domain Counts{sp1}/{sp2}:\t{domCntSp1}\t{domCntSp2}
    Archs:\t{getattr(tmpArchSp1, "phrase")}\t{getattr(tmpArchSp2, "phrase")}""")
                                    '''

                                    # Update the arrays
                                    mtxiArr[dataIdx] = mtxi
                                    mtxjArr[dataIdx] = mtxj
                                    mtxData[dataIdx] = cosineSim
                                    dataIdx += 1
                                    # Add in dictionary
                                    tmpPair = (mtxi, mtxj)
                                    highCosinePairs[tmpPair] = cosineSim
                                    # increment counter
                                    keptPairsCnt += 1
                                else:
                                    rejectDomCheck += 1

                            else: # cosineSim == 1 => OK
                                # Update the arrays
                                mtxiArr[dataIdx] = mtxi
                                mtxjArr[dataIdx] = mtxj
                                mtxData[dataIdx] = cosineSim
                                dataIdx += 1
                                # Add in dictionary
                                tmpPair = (mtxi, mtxj)
                                highCosinePairs[tmpPair] = cosineSim
                                # increment counter
                                keptPairsCnt += 1

                        else:
                            rejectCosine += 1
                    else:
                        aboveThr, tmpDiff = check_magnitude_difference(v1=<double>domCntSp1, v2=<double>domCntSp2, xDiffThr=domCntDiffThr)
                        # print(f"Size check:\t{domCntSp1}\t{domCntSp2}\t{domCntDiffThr}\t{aboveThr}\t{tmpDiff}")
                        if aboveThr:
                            # Reject the pair
                            rejectSizeDiffCnt += 1
                        else:
                            # HACK: this is computationally expensive
                            sp2Vec_view = getattr(tmpArchSp2, "embedding")
                            # Use re-implemented dot product using memory views
                            d11 = dot_view(sp1Vec_view, sp1Vec_view)
                            d22 = dot_view(sp2Vec_view, sp2Vec_view)
                            d12 = dot_view(sp1Vec_view, sp2Vec_view)
                            cosineSim = d12 / sqrt(d11 * d22)

                            #######
                            '''
                            # FIXME: debug only!
                            # Remove if not needed anymore
                            mtxj = sp2ProtIDs[j] - 1
                            if mtxj == 18641:
                                if (mtxi == 569) or (mtxi == 568):
                                    # print(f"{mtxi+1}-{mtxj+1}:{tmpDiff}\t{aboveThr}")
                                    # print(f"{mtxi+1}-{mtxj+1} (coverage check):{abs(covSp1 - covSp2)}>{maxCovDiff}\t{abs(covSp1 - covSp2) > maxCovDiff}")
                                    # print(f"{mtxi+1}-{mtxj+1} (both sizes < 4):{domCntSp1} and {domCntSp2} < 4\t{(domCntSp1 < 4) and (sizeSp2 < 4)}")
                                    # print(f"{mtxi+1}-{mtxj+1} (size check):{domCntSp1}\t{domCntSp2}\t{tmpDiff}\t{aboveThr}")
                                    print(f"{mtxi+1}-{mtxj+1} (cosine check):{cosineSim}>{minCosine}\t{cosineSim >= minCosine}")
                            '''
                            ######
                            if cosineSim >= minCosine:
                                mtxj = sp2ProtIDs[j] - 1
                                if cosineSim == 1:
                                    keptPairsCnt += 1
                                    # Update the arrays
                                    mtxiArr[dataIdx] = mtxi
                                    mtxjArr[dataIdx] = mtxj
                                    mtxData[dataIdx] = cosineSim
                                    dataIdx += 1
                                    # Add to dictionary
                                    tmpPair = (mtxi, mtxj)
                                    highCosinePairs[tmpPair] = cosineSim
                                # Check domains
                                else:
                                    # Obtain the views from the domain ids
                                    domsSp1_view = getattr(tmpArchSp1, "domWvIdx")
                                    domsSp2_view = getattr(tmpArchSp2, "domWvIdx")

                                    domCheckOK = domain_check(domsSp1_view, domsSp2_view, domCntSp1, domCntSp2)
                                    if domCheckOK:
                                        '''
                                        print(f"""Domain counts > 2 AND cosine < 1:
    Pair {mtxi+1}-{mtxj+1}\cosine\lengths:\t{cosineSim:.3f}\t{lenSp1}\t{lenSp2}
    Domain Counts{sp1}/{sp2}:\t{domCntSp1}\t{domCntSp2}
    Archs:\t{getattr(tmpArchSp1, "phrase")}\t{getattr(tmpArchSp2, "phrase")}""")
                                        '''

                                        # Update the arrays
                                        mtxiArr[dataIdx] = mtxi
                                        mtxjArr[dataIdx] = mtxj
                                        mtxData[dataIdx] = cosineSim
                                        dataIdx += 1
                                        # Add in dictionary
                                        tmpPair = (mtxi, mtxj)
                                        highCosinePairs[tmpPair] = cosineSim
                                        # increment counter
                                        keptPairsCnt += 1
                                    else:
                                        rejectDomCheck += 1

                            else:
                                rejectCosine += 1

    # remove some unecessary objects
    del sp1Vec_view
    del sp2Vec_view

    # Create COO Matrix using the slices of the vectors
    M = csr_matrix((mtxData[:dataIdx], (mtxiArr[:dataIdx], mtxjArr[:dataIdx])), shape=(sp1ProtCnt, sp2ProtCnt), dtype=np.float32)
    cdef unsigned long nnzCnt
    nnzCnt = M.nnz # Count of nonzero values in matrix
    cdef double sparsity = 1 - (<double>nnzCnt / <double>protPairs)

    ''' NOTE: debug only
    print(f"Protein pairs:\t{protPairs}")
    print(f"M.shape:\t{M.shape}")
    print(f"M.size:\t{M.size}")
    print(f"M.nnz:\t{nnzCnt}")
    print(f"M.density:\t{(<double>nnzCnt / <double>protPairs)}")
    print(f"M.sparsity:\t{sparsity}")
    print(f"High-cosine arch pairs:\t{len(highCosinePairs)}")
    '''

    # Store the matrix to disk
    ''' NOTE: debug only
    cdef str pairName = f"{sp1}-{sp2}"
    cdef str outMtxPath

    ofdBin: BinaryIO

    if storeMtx:
        outMtxPath = os.path.join(mtxDir, f"{sp1:d}/{pairName}.cosine.mtx.npz")
        # save the matrix
        ofdBin = open(outMtxPath, "wb")
        save_npz(outMtxPath, M, compressed=True)
        ofdBin.close()
    '''

    # Get the execution time
    step_end = perf_counter()
    filter_time = step_end - step_start
    # sys.stdout.write(f"\nElapsed time for filtering and filling CSR sparse matrix (seconds):\t{filter_time:.3f}\n")

    # Free some memory
    del sp1ProtIDs, sp2ProtIDs, sp1Archs, sp2Archs, tmpArchSp1, tmpArchSp2

    # Reset timers
    step_start = step_end

    # Find ROW-WISE candidates
    # Reset idx arrays
    cdef cnp.ndarray[cnp.float32_t, ndim=1] tmpCosineVals = np.zeros(nnzCnt, dtype=np.float32)
    # Will contain uniq columns/rows indexes with at least 1 non-zero entry
    cdef cnp.ndarray[cnp.uint32_t, ndim=1] nzRows = np.zeros(0, dtype=np.uint32)
    cdef cnp.ndarray[cnp.uint32_t, ndim=1] nzCols = np.zeros(nnzCnt, dtype=np.uint32)
    cdef cnp.ndarray[cnp.uint32_t, ndim=1] candIdx = np.zeros(0, dtype=np.uint32)
    cdef double tmpMaxCosine
    cdef unsigned long loopRangeI, loopRangeJ
    cdef unsigned long tmpRowIdx, tmpColIdx

    # Extract unique indexes of columns and rows with at least 1 non-zero entry
    nzRows, nzCols = [np.unique(arr.astype(np.uint32)) for arr in M.nonzero()]
    loopRangeI = nzRows.size
    # Reset the idx arrays used to construct the matrixes
    mtxiArr = np.zeros(nnzCnt, dtype=np.uint32)
    mtxjArr = np.zeros(nnzCnt, dtype=np.uint32)
    dataIdx = 0

    # print(f"\nStart pruning {loopRangeI} rows...")
    for i in range(loopRangeI):
        tmpRowIdx = nzRows[i]
        # print(f"row/loop idx:\t{tmpRowIdx}\t{i}")
        tmpCosineVals = M.getrow(tmpRowIdx).toarray().ravel()
        tmpMaxCosine = tmpCosineVals[tmpCosineVals > 0].max()
        # print(tmpMaxCosine)
        candIdx = np.where(tmpCosineVals == tmpMaxCosine)[0].astype(np.uint32)
        # print(tmpRowIdx, candIdx)

        # Add the values to the matrix
        loopRangeJ = candIdx.size
        for j in range(loopRangeJ):
            # Fill the vectors
            mtxiArr[dataIdx] = tmpRowIdx
            mtxjArr[dataIdx] = candIdx[j]
            # mtxData can be filled later with ones
            dataIdx += 1

        '''
        #####
        # FIXME: use only for debug
        if (tmpRowIdx == 568) or (tmpRowIdx == 569):
            print(f"\nMax cosine for {tmpRowIdx}:\t{tmpMaxCosine}")
            print(f"Min cosine for {tmpRowIdx}:\t{tmpCosineVals[tmpCosineVals > 0].min()}")
            print(candIdx)
        #####
        '''

    # Create matrix using 3 vectors
    cdef cnp.ndarray[cnp.uint8_t, ndim=1] mtxDataInt = np.ones(dataIdx, dtype=np.uint8)
    MrowOrtho = csr_matrix((mtxDataInt, (mtxiArr[:dataIdx], mtxjArr[:dataIdx])), shape=(sp1ProtCnt, sp2ProtCnt), dtype=np.uint8)
    sparsity = 1 - (<double>MrowOrtho.nnz / <double>protPairs)

    '''
    #####
    # FIXME: use only for debug
    i = 568
    j = 18641
    print(f"MrowOrtho[{i}, {j}]:\t{MrowOrtho[i, j]}")
    print(f"M[{i}, {j}]:\t{M[i, j]}")
    i = 569
    print(f"MrowOrtho[{i}, {j}]:\t{MrowOrtho[i, j]}")
    print(f"M[{i}, {j}]:\t{M[i, j]}")
    #####
    '''

    ''' NOTE: debug only
    print(f"MrowOrtho.shape:\t{MrowOrtho.shape}")
    print(f"MrowOrtho.size:\t{MrowOrtho.size}")
    print(f"MrowOrtho.nnz:\t{MrowOrtho.nnz}")
    print(f"MrowOrtho.density:\t{(MrowOrtho.nnz / protPairs)}")
    print(f"MrowOrtho.sparsity:\t{sparsity}")
    print(f"High-cosine arch pairs:\t{len(highCosinePairs)}")

    # Store the matrix into a file
    if storeMtx:
        outMtxPath = os.path.join(mtxDir, f"{sp1:d}/{pairName}.row.candidate.mtx.npz")
        # save the matrix
        ofdBin = open(outMtxPath, "wb")
        save_npz(outMtxPath, MrowOrtho, compressed=True)
        ofdBin.close()
    '''

    # Get the execution time
    step_end = perf_counter()
    rowwise_time = step_end - step_start
    # sys.stdout.write(f"\nElapsed time for selecting row-wise candidate orthologs (seconds):\t{rowwise_time:.3f}\n")

    # Reset the timer
    step_start = step_end
    # Find candidates column-wise
    # Reset all required arrays and variables
    tmpCosineVals = np.zeros(nnzCnt, dtype=np.float32)
    candIdx = np.zeros(0, dtype=np.uint32)
    tmpMaxCosine = 0.
    tmpRowIdx = 0
    tmpColIdx = 0
    loopRangeJ = nzCols.size
    loopRangeI = 0
    mtxiArr = np.zeros(nnzCnt, dtype=np.uint32)
    mtxjArr = np.zeros(nnzCnt, dtype=np.uint32)
    dataIdx = 0

    # NOTE: Optimization shows that CSC mtx is the fastest
    M = M.tocsc()
    # print(f"\nStart pruning {loopRangeJ} columns...")
    for j in range(loopRangeJ):
        tmpColIdx = nzCols[j]
        # print(f"column/loop idx:\t{tmpColIdx}\t{j}")
        tmpCosineVals = M.getcol(tmpColIdx).toarray().ravel()
        tmpMaxCosine = tmpCosineVals[tmpCosineVals > 0].max()
        # print(tmpMaxCosine)
        candIdx = np.where(tmpCosineVals == tmpMaxCosine)[0].astype(np.uint32)
        # Add the values to the matrix
        loopRangeI = candIdx.size

        for i in range(loopRangeI):
            # print(i)
            # Fill the vectors
            mtxiArr[dataIdx] = candIdx[i]
            mtxjArr[dataIdx] = tmpColIdx
            dataIdx += 1

    # Create the matrix
    mtxDataInt = np.ones(dataIdx, dtype=np.uint8)
    McolOrtho = csr_matrix((mtxDataInt, (mtxiArr[:dataIdx], mtxjArr[:dataIdx])), shape=(sp1ProtCnt, sp2ProtCnt), dtype=np.uint8)
    # sparsity = 1 - (<double>McolOrtho.nnz / <double>protPairs)

    ''' NOTE: debug only
    print(f"McolOrtho.shape:\t{McolOrtho.shape}")
    print(f"McolOrtho.size:\t{McolOrtho.size}")
    print(f"McolOrtho.nnz:\t{McolOrtho.nnz}")
    print(f"McolOrtho.density:\t{(McolOrtho.nnz / protPairs)}")
    print(f"McolOrtho.sparsity:\t{sparsity}")
    print(f"High-cosine arch pairs:\t{len(highCosinePairs)}")

    # Store the matrix into a file
    if storeMtx:
        outMtxPath = os.path.join(mtxDir, f"{sp1:d}/{pairName}.col.candidate.mtx.npz")
        # save the matrix
        ofdBin = open(outMtxPath, "wb")
        save_npz(outMtxPath, McolOrtho, compressed=True)
        ofdBin.close()
    '''

    # Get the execution time
    step_end = perf_counter()
    colwise_time = step_end - step_start
    # sys.stdout.write(f"\nElapsed time for selecting column-wise candidate orthologs (seconds):\t{colwise_time:.3f}\n")
    # reset the timer
    step_start = step_end

    # Sum the two matrixes and extract potential orthologs
    Moverlap = MrowOrtho + McolOrtho

    # Free some memory
    del McolOrtho, MrowOrtho, tmpCosineVals

    # Extract unique indexes of columns and rows with at least 1 non-zero entry
    nzRows, nzCols = [np.unique(arr.astype(np.uint32)) for arr in Moverlap.nonzero()]
    # sparsity = 1 - (<double>Moverlap.nnz / <double>protPairs)

    ''' NOTE: debug only
    print(f"\nProtein pairs:\t{protPairs}")
    print(f"Moverlap.shape:\t{Moverlap.shape}")
    print(f"Moverlap.size:\t{Moverlap.size}")
    print(f"Moverlap.nnz:\t{Moverlap.nnz}")
    print(f"Moverlap.density:\t{(<double>Moverlap.nnz / <double>protPairs)}")
    print(f"Moverlap.sparsity:\t{sparsity}")
    print(f"High-cosine arch pairs:\t{len(highCosinePairs)}")
    # Store the matrix into a file
    if storeMtx:
        outMtxPath = os.path.join(mtxDir, f"{sp1:d}/{pairName}.sum.candidate.mtx.npz")
        # save the matrix
        ofdBin = open(outMtxPath, "wb")
        save_npz(outMtxPath, Moverlap, compressed=True)
        ofdBin.close()
    '''

    # Reset some of the variables
    cdef bint overlapOnly = 0
    cdef cnp.ndarray[cnp.uint8_t, ndim=1] tmpOverlapVals = np.zeros(0, dtype=np.uint8)
    cdef cnp.ndarray[cnp.uint32_t, ndim=1] tmpNonZeroCols = np.zeros(0, dtype=np.uint32)
    # cdef cnp.ndarray[cnp.uint32_t, ndim=1] tmpNoOverlapCols = np.zeros(0, dtype=np.uint32)
    nnzCnt = Moverlap.nnz
    mtxiArr = np.zeros(nnzCnt, dtype=np.uint32)
    mtxjArr = np.zeros(nnzCnt, dtype=np.uint32)
    mtxData = np.zeros(nnzCnt, dtype=np.float32)
    dataIdx = 0
    loopRangeI = nzRows.size
    loopRangeJ = nzCols.size

    # Create the matrix with the ortholog relations
    # TODO: implement the non-overlap version (in which entries with 1 and 2 in overlap matrix are considered)
    if overlapOnly:
        # Select only overlapping values (e.g., M[i, j] = 2)
        for i in range(loopRangeI):
            tmpRowIdx = nzRows[i]
            # Extract only indexes with overlaps
            # print(f"\nrow/loop idx:\t{tmpRowIdx}\t{i}")
            tmpOverlapVals = Moverlap.getrow(tmpRowIdx).toarray().ravel()
            # Extract indexes of columns which have value = 2
            tmpNonZeroCols = np.asarray(tmpOverlapVals > 1).nonzero()[0].astype(np.uint32)
            # print(f"tmpOverlapVals.size:\t{tmpOverlapVals.size}")
            loopRangeJ = tmpNonZeroCols.size
            # Iterate through the rows and write the candidate pairs
            for j in range(loopRangeJ):
                tmpColIdx = tmpNonZeroCols[j]
                # print(f"tmpColIdx:\t{tmpColIdx}")
                mtxiArr[dataIdx] = tmpRowIdx
                mtxjArr[dataIdx] = tmpColIdx
                # mtxData[dataIdx] = highCosinePairs[(tmpRowIdx, tmpColIdx)]
                mtxData[dataIdx] = highCosinePairs.pop((tmpRowIdx, tmpColIdx))
                dataIdx += 1
    # FIXME: Note that when overlap is not used,
    # the creation of the overlap matrix is redundant
    else:
        # Select all elements regardless of the overlap
        for i in range(loopRangeI):
            # print(f"i:\t{i}")
            tmpRowIdx = nzRows[i]
            # print(f"tmpRowIdx:\t{tmpRowIdx}")
            tmpNonZeroCols = Moverlap.getrow(tmpRowIdx).toarray().ravel().nonzero()[0].astype(np.uint32)
            loopRangeJ = tmpNonZeroCols.size
            # print(f"tmpNonZeroCols.size:\t{loopRangeJ}")
            # Iterate through the rows and write the candidate pairs
            for j in range(loopRangeJ):
                # print(f"j:\t{j}")
                # print(f"tmpColIdx:\t{tmpColIdx}")
                tmpColIdx = tmpNonZeroCols[j]
                # print(f"tmpColIdx:\t{tmpColIdx}")
                mtxiArr[dataIdx] = tmpRowIdx
                mtxjArr[dataIdx] = tmpColIdx
                # print(f"highCosinePairs:\t({tmpRowIdx}, {tmpColIdx})")
                # mtxData[dataIdx] = highCosinePairs[(tmpRowIdx, tmpColIdx)]
                mtxData[dataIdx] = highCosinePairs.pop((tmpRowIdx, tmpColIdx))
                # print(f"mtxData[dataIdx]:\t{mtxData[dataIdx]}")
                dataIdx += 1

    # Create the matrix with 1-to-1 ortholog relations (based on the max cosine)
    M1to1ortho = csr_matrix((mtxData[:dataIdx], (mtxiArr[:dataIdx], mtxjArr[:dataIdx])), shape=(sp1ProtCnt, sp2ProtCnt), dtype=np.float32)
    nnzCnt = M1to1ortho.nnz # Count of nonzero values in matrix
    # sparsity = 1 - (<double>nnzCnt / <double>protPairs)

    # FIXME: remove when mature
    '''
    print(f"\nProtein pairs:\t{protPairs}")
    print(f"M1to1ortho.shape:\t{M1to1ortho.shape}")
    print(f"M1to1ortho.size:\t{M1to1ortho.size}")
    print(f"M1to1ortho.nnz:\t{nnzCnt}")
    print(f"M1to1ortho.density:\t{(<double>nnzCnt / <double>protPairs)}")
    print(f"M1to1ortho.sparsity:\t{sparsity}")
    print(f"High-cosine arch pairs:\t{len(highCosinePairs)}")

    # Store the matrix into a file
    if storeMtx:
        outMtxPath = os.path.join(mtxDir, f"{pairName}.1to1.ortho.mtx.npz")
        # save the matrix
        ofdBin = open(outMtxPath, "wb")
        save_npz(outMtxPath, M1to1ortho, compressed=True)
        ofdBin.close()
    '''

    '''
    #####
    # FIXME: use only for debug
    print("\nFinal ortho Matrix!")
    i = 568
    j = 18641
    print(f"M1to1ortho[{i}, {j}]:\t{M1to1ortho[i, j]}")
    i = 569
    print(f"M1to1ortho[{i}, {j}]:\t{M1to1ortho[i, j]}")
    #####
    '''

    # Get the execution time
    step_end = perf_counter()
    one2one_time = step_end - step_start
    nnzCnt = M1to1ortho.size
    # sys.stdout.write(f"\nElapsed time to generate overlap matrix (seconds):\t{one2one_time:.3f}\n")

    debugStr = f"""infer_arch_orthologs :: SUMMARY
    Starting pairs:\t{archPairs:d}
    Keep:\t{keptPairsCnt}
    Reject (by length):\t{rejectLenDiffCnt}
    Reject (by coverage):\t{rejectCovDiffCnt}
    Reject (by domain count):\t{rejectSizeDiffCnt}
    Reject (by cosine < {minCosine:.2f}):\t{rejectCosine}
    Reject (by domain check):\t{rejectDomCheck}
    1-to-1 ortho-archs:\t{nnzCnt}
    Total ex-time (seconds):\t{(step_end - start_time):.3f}"""
    logger.debug(debugStr)

    # Create the ortholog tables
    # The tuple contains:
    # Execution time
    # Clusters count
    # Biggest clusters (number of pairs)
    # Number of orhtolog pairs in the cluster
    cdef (double, unsigned long, unsigned long, unsigned long) clusteringTpl = cluster_arch_orthologs(sp1=sp1, sp2=sp2, M=M1to1ortho, outDir=archOrthoDbDir, writePairs=0)

    # Output tuple
    # cdef (double, double, double, double, unsigned int, unsigned int, unsigned int, unsigned int, unsigned int, unsigned int, unsigned short) outTpl
    # outTpl = (filter_time, rowwise_time, colwise_time, one2one_time, protPairs, archPairs, rejectLenDiffCnt, rejectCovDiffCnt, rejectSizeDiffCnt, rejectCosine, nnzCnt)
    # HACK: add the information from the clustering

    # (double, double, double, double, double, unsigned int, unsigned int, unsigned int, unsigned int, unsigned int, unsigned int, unsigned short, unsigned int, unsigned int, unsigned int)

    cdef (double, double, double, double, double, unsigned long, unsigned long, unsigned long, unsigned long, unsigned long, unsigned long, unsigned long, unsigned long, unsigned long) outTpl
    outTpl = (filter_time, rowwise_time, colwise_time, one2one_time, clusteringTpl[0], protPairs, archPairs, rejectLenDiffCnt, rejectCovDiffCnt, rejectSizeDiffCnt, rejectCosine, nnzCnt, clusteringTpl[1], clusteringTpl[2])

    # sys.exit("DEBUG :: infer_arch_orthologs")

    return outTpl



cdef void makedir(str path):
    """Create a directory including the intermediate directories in the path if not existing."""
    # check the file or dir does not already exist
    if os.path.isfile(path):
        sys.stderr.write(f"\nWARNING: {path}\nalready exists as a file, and the directory cannot be created.\n")
    try:
        os.makedirs(path)
    except OSError:
        if not os.path.isdir(path):
            raise



cpdef void set_logger(str loggerName, int lev, bint propagate, object customFmt):
    """Set the global logger for this module"""
    global logger
    logger = logging.getLogger(loggerName)
    logger.setLevel(lev)
    logger.propagate = propagate
    # Create the handler and 
    clsLogger: logging.StreamHandler = logging.StreamHandler(stream=sys.stdout)
    # This makes sure that the log file is created even if not in debug mode
    clsLogger.setLevel(logger.level)
    # Set the formatter
    if customFmt is not None:
        clsLogger.setFormatter(customFmt)
    logger.addHandler(clsLogger)
    # write some log about it!
    logger.debug(f"General logger for {loggerName} loaded!")



cdef void write_run_info_file(str infoFilePath, dict infoDict):
    """Write a file summarizing the run settings."""
    logger.debug(f"""write_run_info_file :: START
    Output file:\t{infoFilePath}
    Parameters: {len(infoDict)}""")
    cdef str info
    ofd: TextIO = open(infoFilePath, "wt")
    for info, val in infoDict.items():
        if info == "Version":
            ofd.write(f"SonicParanoid {val}\n")
        else:
            ofd.write(f"{info}\t{val}\n")
    ofd.close()