# -*- coding: utf-8 -*-
# cython: profile=False
"""
This module contains functions create ortholog matrixes.
"""
from __future__ import annotations

from libc.stdio cimport FILE
from libc.stdlib cimport atoi, atof

cdef extern from "stdio.h":
    FILE *fopen(const char *, const char *)
    int fclose(FILE *)
    ssize_t getline(char **, size_t *, FILE *)


import sys
import os
import pickle
import multiprocessing as mp
import queue
from tqdm import tqdm
from itertools import combinations
# import numpy as np
from scipy.sparse import dok_matrix, lil_matrix, csr_matrix, save_npz, load_npz, triu
import time
from typing import BinaryIO, TextIO

import numpy as np
cimport numpy as cnp
cimport cython



__module_name__ = "Graph"
__source__ = "graph_c.pyx"
__author__ = "Salvatore Cosentino"
__license__ = "GPLv3"
__version__ = "0.8"
__maintainer__ = "Cosentino Salvatore"
__email__ = "salvo981@gmail.com"



def info() -> None:
    """Functions to create a graph from ortholog tables."""
    print(f"MODULE NAME:\t{__module_name__}")
    print(f"SOURCE FILE NAME:\t{__source__}")
    print(f"MODULE VERSION:\t{__version__}")
    print(f"LICENSE:\t{__license__}")
    print(f"AUTHOR:\t{__author__}")
    print(f"EMAIL:\t{__email__}")



""" Worker functions (1 cpu) """
# def consume_merge_inparalog_matrixes(jobs_queue, results_queue, combMtx: csr_matrix, mtxDir: str, outDir: str, removeMerged: bool):
cdef consume_merge_inparalog_matrixes(object jobs_queue, object results_queue, object combMtx, str mtxDir, str outDir, bint removeMerged):
    """Merge inparalog matrixes."""
    cdef str mtxPath
    while True:
        current_sp  = jobs_queue.get(True, 1)
        if current_sp is None:
            break
        # merge the matrixes
        mtxPath = merge_inparalog_matrixes(current_sp, combMtx=combMtx, inDir=mtxDir, outDir=outDir, removeMerged=removeMerged, debug=False)
        # sys.exit("DEBUG@graph_c.pyx -> consume_merge_inparalog_matrixes")
        # add the path to the output
        if mtxPath is None:
          results_queue.put((current_sp, False))
        else:
          results_queue.put((current_sp, True))



# def consume_write_per_species_mcl_graph(jobs_queue, results_queue, offSetDict: dict[int, int], mtxDir: str, outDir: str, combMtxPath: str) -> None:
cdef void consume_write_per_species_mcl_graph(object jobs_queue, object results_queue, dict offSetDict, str mtxDir, str outDir, str combMtxPath):
    """Generate MCL graph for the input species."""
    cdef str mclSpGraphPath

    while True:
        current_sp = jobs_queue.get(True, 1)
        if current_sp is None:
            break
        mclSpGraphPath = write_per_species_mcl_graph(current_sp, offSetDict, mtxDir, outDir, combMtxPath, debug=False)
        # add the path to the output
        results_queue.put((current_sp, mclSpGraphPath))
        # sys.exit("DEBUG@graph_c.pyx -> consume_write_per_species_mcl_graph")



# def consume_create_matrix_from_orthotbl(jobs_queue, results_queue, inDir: str, outDir:str, storeDgraph: bool=False, mergedTables: bool=False):

# cdef void consume_integrate_arch_ortho_into_gclstr(object jobs_queue, object results_queue, str outDir, dict archMasterDict):
cdef void consume_create_matrix_from_orthotbl(object jobs_queue, object results_queue, str inDir, str outDir, bint storeDgraph, bint mergedTables):
    """Parse ortholog table and fill matrixes."""
    cdef str sp1, sp2, tblType, current_pair, tblDir, inTbl
    cdef unsigned int aSize
    cdef unsigned int bSize

    while True:
        jobTpl  = jobs_queue.get(True, 1)
        if jobTpl is None:
            break
        current_pair = jobTpl[0]
        aSize = jobTpl[1]
        bSize = jobTpl[2]
        # print(f"\nCreating Matrix for pair:\t{current_pair}")
        sp1, sp2 = current_pair.split("-", 1)
        #print(current_pair, aSize, bSize)
        # Set a different name depending if the table is merged with arch-based predictions
        # or only contains graph-based ones
        if mergedTables:
            tblType = "mtable"
        else:
            tblType = "table"
        tblDir = os.path.join(inDir, f"{sp1}")
        inTbl = os.path.join(tblDir, f"{tblType}.{current_pair}")
        # print(f"\ninTbl: {inTbl}")
        outTpl: tuple[str, str, str] = create_matrix_from_orthotbl(inTbl=inTbl, outDir=outDir, aSize=aSize, bSize=bSize, storeDgraph=storeDgraph, debug=False)
        # sys.exit("DEBUG@graph_c -> consume_create_matrix_from_orthotbl")
        # add the matrixes names
        results_queue.put(outTpl)



""" Job processing Functions """
def create_matrix_from_orthotbl_parallel(pairsList: list[str], runDir: str=os.getcwd(), orthoDbDir: str=os.getcwd(), outDir: str=os.getcwd(), mergedTables: bool = False, threads: int=4, debug: bool=False) -> None:
    """Compute paralog matrixes in parallel."""
    if debug:
        print("\ncreate_matrix_from_orthotbl_parallel :: START")
        print(f"Pairs to be processed:\t{len(pairsList)}")
        print(f"Run directory: {runDir}")
        print(f"Directory with ortholog tables: {orthoDbDir}")
        print(f"Output directory: {outDir}")
        print(f"Merged graph- and arch-based predictions:\t{mergedTables}")
        print(f"Threads:\t{threads}")
    # load the size of each input proteomes
    cdef str pcklPath = os.path.join(runDir, "protein_counts.pckl")
    cdef dict seqCountsDict # dict[str, int]
    cdef unsigned int pairsCnt = len(pairsList)
    if not os.path.isfile(pcklPath):
      sys.stderr.write(f"\nERROR: the pickle file with the sequence counts\n{pcklPath}\nis missing in the run directory\n")
      sys.exit(-2)
    else:
      with open(pcklPath, "rb") as ifd:
        seqCountsDict = pickle.load(ifd)
    # sys.exit("DEBUG :: create_matrix_from_orthotbl_parallel :: after loading sequence counts.")
    # Start timer
    sys.stdout.write("\nCreating orthology matrixes...\n")
    timer_start = time.perf_counter()

    # create the queue and start adding
    ortho2mtx_queue = mp.Queue(maxsize=pairsCnt + threads)
    # print(pairsList)

    # fill the queue with the pairs
    for pair in pairsList:
        sys.stdout.flush()
        spA, spB = pair.split("-", 1)
        ortho2mtx_queue.put((pair, seqCountsDict[spA], seqCountsDict[spB]))

    # add flags for completed jobs
    for i in range(0, threads):
        sys.stdout.flush()
        ortho2mtx_queue.put(None)
    # Queue to contain the execution time
    results_queue = mp.Queue(maxsize=pairsCnt)

    # call the method inside workers
    cdef list runningJobs = [mp.Process(target=consume_create_matrix_from_orthotbl, args=(ortho2mtx_queue, results_queue, orthoDbDir, outDir, False, mergedTables)) for i_ in range(threads)]

    for proc in runningJobs:
        proc.start()

    # Show the progress bars
    pbar: tqdm = tqdm(total=pairsCnt, desc="Ortholog matrices creation", unit="proteome pairs", disable=None, smoothing=0.3, ascii=False, miniters=1, mininterval=2.0, colour="green")

    while True:
        try:
            resTpl = results_queue.get(False, 0.01)
            resPair: str = resTpl[0].rsplit(".", 1)[0]
            # Update the status bar
            pbar.update(1)

            if debug:
              sys.stdout.write("Matrixes created for pair {:s}\t{:s}\n".format(resPair, str(resTpl)))
        except queue.Empty:
            pass
        allExited = True
        for t in runningJobs:
            if t.exitcode is None:
                allExited = False
                break
        if allExited & results_queue.empty():
            break

    # Close the progress bar
    pbar.close()

    # this joins the processes after we got the results
    for proc in runningJobs:
        while proc.is_alive():
            proc.join()

    sys.stdout.write("Ortholog matrixes creation elapsed time (seconds):\t{:s}\n".format(str(round(time.perf_counter() - timer_start, 3))))
    # sys.exit("DEBUG :: create_matrix_from_orthotbl_parallel :: DONE.")



def merge_inparalog_matrixes_parallel(spArray, combMtxPath: str, inDir: str=os.getcwd(), outDir: str=os.getcwd(), threads: int=4,  removeMerged: bool=False, debug: bool=False):
    """MCL graph for a species from matrixes in parallel."""
    if debug:
        print("\nmerge_inparalog_matrixes_parallel :: START")
        print(f"Species for which the graph will created:\t{len(spArray)}")
        print(f"Path to the combination matrix:\t{combMtxPath}")
        print(f"Input directory: {inDir}")
        print(f"Output directory: {outDir}")
        print(f"Threads:{threads}")
        print(f"Remove merged matrixes:\t{removeMerged}")

    # sys.exit("DEBUG@graph_c.pyx -> merge_inparalog_matrixes_parallel")
    # check that the matrix with combinations exists
    if not os.path.isfile(combMtxPath):
      sys.stderr.write(f"\nERROR: the file with the combination matrix\n{combMtxPath}\nwas not found!\n")
      sys.exit(-2)
    
    # Create directory that will contain merged inparalog matrixes
    makedir(os.path.join(outDir, "inparalogs"))
    # load the matrix
    combMtx: csr_matrix = load_npz(combMtxPath) # this an upper triangular matrix
    # create the queue and start adding the species
    sp_queue: mp.queues.Queue = mp.Queue(maxsize=len(spArray) + threads)

    # fill the queue with the pairs
    for tmpSp in spArray:
        sys.stdout.flush()
        sp_queue.put(tmpSp)

    # add flags for completed jobs
    for i in range(0, threads):
        sys.stdout.flush()
        sp_queue.put(None)
    # Queue to contain the execution time
    results_queue = mp.Queue(maxsize=len(spArray))
    #sys.exit("DEBUG :: merge_inparalog_matrixes_parallel :: before starting jobs...")

    # call the method inside workers
    runningJobs = [mp.Process(target=consume_merge_inparalog_matrixes, args=(sp_queue, results_queue, combMtx, inDir, outDir, removeMerged)) for i_ in range(threads)]

    for proc in runningJobs:
        proc.start()

    # Dictionary with False if the merging failed
    resDict: dict[int, bool] = {}

    while True:
        try:
            processedSp, mergeOk = results_queue.get(False, 0.01)
            if not mergeOk:
              sys.stdout.write(f"Merging in-paralogs for species {processedSp} failed.\n")
              resDict[processedSp] = False
            else:
              resDict[processedSp] = True
        except queue.Empty:
            pass
        allExited = True
        for t in runningJobs:
            if t.exitcode is None:
                allExited = False
                break
        if allExited & results_queue.empty():
            break

    # this joins the processes after we got the results
    for proc in runningJobs:
        while proc.is_alive():
            proc.join()
    # return the sorted dictionary with the paths
    return dict(sorted(resDict.items()))



def write_per_species_mcl_graph_parallel(spArray, runDir: str=os.getcwd(), mtxDir: str=os.getcwd(), outDir: str=os.getcwd(), threads: int=4, debug: bool=False) -> dict[int, str]:
    """MCL graph for a species from matrixes in parallel."""
    if debug:
        print("\nwrite_per_species_mcl_graph_parallel :: START")
        print(f"Species for which the graph will created:\t{len(spArray)}")
        print(f"Run directory: {runDir}")
        print(f"Directory with Matrixes: {mtxDir}")
        print(f"Output directory: {outDir}")
        print(f"Threads:\t{threads}")

    # load the size of each input proteomes
    pcklPath = os.path.join(runDir, "protein_counts.pckl")
    # compute offsets
    offSetDict = compute_offsets(pcklPath)[0]
    # path to the combination matrix
    combMtxPath = os.path.join(runDir, "combination_mtx.npz")
    # create the queue and start adding the species
    sp_queue = mp.Queue(maxsize=len(spArray) + threads)

    # fill the queue with the pairs
    for tmpSp in spArray:
        sys.stdout.flush()
        sp_queue.put(<int>tmpSp)

    # add flags for completed jobs
    for i in range(0, threads):
        sys.stdout.flush()
        sp_queue.put(None)
    # Queue to contain the execution time
    results_queue = mp.Queue(maxsize=len(spArray))
    #sys.exit("DEBUG :: write_per_species_mcl_graph_parallel :: before starting jobs...")

    # call the method inside workers
    runningJobs = [mp.Process(target=consume_write_per_species_mcl_graph, args=(sp_queue, results_queue, offSetDict, mtxDir, outDir, combMtxPath)) for i_ in range(threads)]

    for proc in runningJobs:
        proc.start()

    # output dictionary which associate
    # a species ID to a the path of MCL subgraph created for it
    mclSpGraphDict: dict[int, str] = {}

    while True:
        try:
            processedSp, spGraphPath = results_queue.get(False, 0.01)
            if debug:
              sys.stdout.write("MCL graph for species {processedSp} created\n{spGraphPath}\n")
            # add the path to the dictionary
            mclSpGraphDict[processedSp] = spGraphPath
        except queue.Empty:
            pass
        allExited = True
        for t in runningJobs:
            if t.exitcode is None:
                allExited = False
                break
        if allExited & results_queue.empty():
            break

    # this joins the processes after we got the results
    for proc in runningJobs:
        while proc.is_alive():
            proc.join()
    # return the sorted dictionary with the paths
    return dict(sorted(mclSpGraphDict.items()))



""" Other functions """
# def compute_offsets(protCntPckl: str, debug: bool=False):
cpdef inline object compute_offsets(str protCntPckl, bint debug=0):
    """Compute index offsets for each species from pickle with sizes"""

    '''
    if debug:
        print("\ncompute_offsets :: START")
        print(f"Pickle with sequence counts for each species: {protCntPckl}")
    '''
    # check that the file the protein counts exists
    if not os.path.isfile(protCntPckl):
      sys.stderr.write(f"\nERROR: the file with the protein counts\n{protCntPckl}\nwas not found!\n")
      sys.exit(-2)
    cdef dict protCntDict
    # load the protein count
    with open(protCntPckl, "rb") as ifd:
      protCntDict = pickle.load(ifd)
    cdef unsigned int spCnt = len(protCntDict)
    cdef list spList = list(protCntDict.keys())
    # fill the dictionary with offsets
    cdef size_t i # used for for loop
    cdef dict offSetDict = {} # dict[int, int]
    cdef dict sizeDict = {} # dict[int, int]
    cdef unsigned int accumulator = 0
    cdef unsigned int prevCnt = 0
    cdef unsigned int loopCnt = 0
    cdef unsigned int spId
    cdef str spIdStr
    cdef unsigned int seqCnt

    # sys.exit("DEBUG")
    for i in range(spCnt):
        spIdStr = spList[i]
        spId = int(spIdStr)
        seqCnt = protCntDict[spIdStr]
        sizeDict[spId] = seqCnt
        if loopCnt == 0:
            offSetDict[spId] = 0
        else:
            accumulator += prevCnt
            offSetDict[spId] = accumulator
        prevCnt = seqCnt
        loopCnt += 1


    '''
    for spId, pCnt in protCntDict.items():
      sizeDict[int(spId)] = pCnt
      if loopCnt == 0:
        offSetDict[int(spId)] = 0
      else:
        accumulator += prevCnt
        offSetDict[int(spId)] = accumulator
      prevCnt = pCnt
      loopCnt += 1
    '''
    # print some debug
    if debug:
      for spId, offset in offSetDict.items():
        print(f"sp={spId}\tproteins={protCntDict[str(spId)]}\toffset={offset}")
    # free some memory
    del protCntDict
    # return the dictionary
    return (offSetDict, sizeDict)



# def create_matrix_from_orthotbl(inTbl: str, outDir: str, aSize: int, bSize: int, storeDgraph: bool=False, debug: bool=False) -> tuple[str, str, str]:
cdef object create_matrix_from_orthotbl(str inTbl, str outDir, unsigned int aSize, unsigned int bSize, bint storeDgraph=0, bint debug=0): # tuple[str, str, str]
    """Load ortholog relationships from pickle of tuple to a matrix."""
    '''
    if debug:
        print("\ncreate_matrix_from_orthotbl :: START")
        print(f"Table path: {inTbl}")
        print(f"Output directory:\t{outDir}")
        print(f"Size A:\t{aSize}")
        print(f"Size B:\t{bSize}")
        print(f"Store a directed graph for orthologs:\t{storeDgraph}")
    '''

    if not os.path.isfile(inTbl):
        sys.stderr.write(f"\nERROR: the ortholog table\n{inTbl}\nwas not found.")
        sys.exit(-2)

    if storeDgraph:
      import networkx as nx
      G = nx.DiGraph()

    # extract the species names
    cdef str pairName = os.path.basename(inTbl).split(".", 1)[-1]
    cdef str spAstr, spBstr
    cdef unsigned int spA, spB
    spAstr, spBstr = pairName.split("-", 1)
    spA = int(spAstr)
    spB = int(spBstr)
    # Adjust the output directory so that the matrixes are organized in subdirectories
    # For example, given the matrixes 1-2, 2-3, and 1-3,
    # 1-2 and 1-3 will be store in '1', while 2-3 will be stored in 2
    outDir = os.path.join(outDir, spAstr)
    makedir(outDir)

    # define temporary variables
    cdef str clstrLx = "" # part from species A
    cdef str clstrRx = "" # part from species B
    cdef dict lxDict # dict[str, float]
    cdef dict lxDictInp # dict[str, float]
    cdef dict lxDictMain # dict[str, float]
    cdef dict rxDict # dict[str, float]
    cdef dict rxDictInp # dict[str, float]
    cdef dict rxDictMain # dict[str, float]

    # will store parts (left or right) of each clusters
    cdef list tmpList # list[str]

    # other variables
    cdef unsigned int rdCnt = 0
    #cdef float tmpSc
    cdef double tmpSc = 0
    # define file names and file descriptor pointer in C
    filename_byte_string = inTbl.encode("UTF-8")
    cdef char* inTbl_c = filename_byte_string
    #file pointer
    cdef FILE* cfile
    # varibales for files and lines
    cdef char * line = NULL
    cdef size_t l = 0
    cdef ssize_t read

    #open the pairwise ortholog table
    cfile = fopen(inTbl_c, "rb")
    if cfile == NULL:
        raise FileNotFoundError(2, "No such file or directory: '%s'" % inTbl_c)

    # example of line to be parsed
    # 334	64	1.1110 0.051 1.943 1.0	2.16 1.0 2.653 0.18

    # output dictionary (a digest for each file name)
    cdef dict relDict # dict[int, dict[str, list[tuple[str, str, float]]]]
    # relList: list[dict[int, dict[str, list[tuple[str, str, float]]]]] = []
    # relListLx: list[dict[str, list[tuple[str, str, float]]]] = []
    # relListRx: list[dict[str, list[tuple[str, str, float]]]] = []

    # use to check if a given protein appears multiple times in the input table
    cdef dict repeatTrapLx = {} # dict[str, int]
    cdef dict repeatTrapRx = {} # dict[str, int]

    # use to check if a given protein appears multiple times in the input table
    # instantiate the matrixes
    AB = lil_matrix((aSize, bSize), dtype=np.float32)
    Ai = lil_matrix((aSize, aSize), dtype=np.float32)
    Bi = lil_matrix((bSize, bSize), dtype=np.float32)

    cdef list inParaRel # list[tuple[int, int]] = []
    cdef list flds # list[bytes]

    # counters
    cdef unsigned int inparaWrtA = 0
    cdef unsigned int inparaWrtB = 0
    # Create array of doubles
    cdef cnp.ndarray[cnp.float32_t, ndim=1] rxSc # = np.zeros(aSp1OrthoCnt, dtype=np.uint8)
    cdef unsigned int i, j, orthoLx, orthoRx, tmpIdx, tmpJ, tmpI
    cdef double tmpInpaW

    while True:
        read = getline(&line, &l, cfile)
        if read == -1:
            break

        # if the first letter is a 'O' then it is the cluster headers
        if line.decode()[-2] == "B":
            continue
        rdCnt += 1
        relDict = {1:{}, 2:{}}
        # print(f"line\\content:{rdCnt}\n{line}")
        # split the cluster string
        flds = line.rstrip(b"\n").rsplit(b"\t", 2)
        # print(flds)
        clstrLx = flds[1].decode()
        clstrRx = flds[2].decode()
        # temporary dictionaries
        lxDict = {}
        lxDictInp = {}
        lxDictMain = {}
        rxDict = {}
        rxDictInp = {}
        rxDictMain = {}

        # extract orthologs from the left part of the cluster
        # example: 3.1653 1.0 3.373 0.385 -> gene1 1.0 gene2 0.385
        tmpList = clstrLx.split(" ")
        for i, ortho in enumerate(tmpList):
          if i % 2 == 0: # then we add the element to the dictionary
            tmpSc = round(float(tmpList[i+1]), 3)
            tmpIdx = int(ortho.split(".", 1)[1]) - 1
            if not tmpIdx in repeatTrapLx:
              repeatTrapLx[tmpIdx] = 1
            else:
              #sys.exit("\nERROR: the protein {:s} from species A was found in multiple ortholog relations...".format(tmpIdx))
              repeatTrapLx[tmpIdx] += 1
              continue
            lxDict[tmpIdx] = tmpSc
            if tmpSc < 1:
              lxDictInp[tmpIdx] = tmpSc
            else:
              lxDictMain[tmpIdx] = tmpSc

        # extract the right part
        tmpList = clstrRx.split(" ")
        #print("rx_tmp_list:", tmpList)
        for i, ortho in enumerate(tmpList):
          if i % 2 == 0: # then we add the element to the dictionary
            tmpSc = round(float(tmpList[i+1]), 3)
            tmpIdx = int(ortho.split(".", 1)[1]) - 1
            if not tmpIdx in repeatTrapRx:
              repeatTrapRx[tmpIdx] = 1
            else:
              #sys.exit("\nERROR: the protein {:s} from species A was found in multiple ortholog relations...".format(tmpIdx))
              repeatTrapRx[tmpIdx] += 1
              continue
            rxDict[tmpIdx] = tmpSc
            if tmpSc < 1:
              if not ortho in rxDictInp: # this check should be removed later!
                rxDictInp[tmpIdx] = tmpSc
              else:
                print(f"ERROR: the inparalog {ortho} was already in the dictionary!")
                sys.exit(-5)
            else:
              rxDictMain[tmpIdx] = tmpSc
        lxOrthoList = list(lxDict.keys())
        rxOrthoList = list(rxDict.keys())

        #if debug:
        #  print("\nCompute scores and add orthologs to matrix for current cluster...")
        #  print(clstrLx, clstrRx)
        # extract the ortholog scores in a array
        rxSc = np.array(list(rxDict.values()), dtype=np.float32)
        for orthoLx, tmpSc in lxDict.items():
          # compute the weights
          wArr = (rxSc + tmpSc)/2.
          #print("\ncurrent:\t", orthoLx, tmpSc)
          i = orthoLx
          # search for orthologs to store in AB
          for idx, orthoRx in enumerate(rxOrthoList):
            # add the connection (if not between InParalogs)
            j = orthoRx

            ''' AVOID INTER-SPECIES INPARALOGS
            # add the relation if at least one of the 2 is main ortholog
            if not (orthoLx in lxDictInp and orthoRx in rxDictInp):
              tmpW = wArr[idx]
              #print("Candidate ortholog...")
              #print("{:s} -> {:s}".format(orthoLx, orthoRx))
              #print("{:d} -> {:d}".format(i, j))
              #relDict[1][orthoLx].append((orthoRx, round(w[i], 3)))
              # ADD THIS PART
              if not AB[i, j]:
                AB[i, j] = round(tmpW, 3)
                # add edge to the graph if required
            #'''

            #''' Allow interspecies in-paralogs
            # add the relation (includes also relations amongst inparalogs)
            # from different species
            tmpW = wArr[idx]
            #print("Candidate ortholog...")
            #print("{:s} -> {:s}".format(orthoLx, orthoRx))
            #print("{:d} -> {:d}".format(i, j))
            #relDict[1][orthoLx].append((orthoRx, round(w[i], 3)))
            # ADD THIS PART
            if not AB[i, j]:
              AB[i, j] = round(tmpW, 3)
            #'''

        # variable used to store the weight for inparalogs
        tmpInpaW = 0.0

        # search for in-paralogs to store in Ai (for the left part)
        # compute all the possible combinations
        #print("\nadd inparalogs relations for {:d} paralogs in species {:d}...".format(len(lxOrthoList), spA))
        inParaRel = list(combinations(sorted(lxOrthoList), r=2))
        #print(inParaRel)

        for tplIdx in inParaRel:
          i, j = tplIdx
          tmpInpaW = round((lxDict[i] + lxDict[j]) / 2. , 3)
          # make sure that the matrix is upper triangular
          if i > j: # below the diagonal
            #print("i > j", i, j)
            # swap the indexes
            tmpJ = i
            tmpI = j
            #print("swapped(i, j)", tmpI, tmpJ)
            if not Ai[tmpI, tmpJ]:
              # print(str(Ai[tmpI, tmpJ]))
              Ai[tmpI, tmpJ] = tmpInpaW
              inparaWrtA += 1
              continue
          elif i == j:
            diagCntA += 1
            print("same!", i, j)
            print("This should not happen!")
            sys.exit("DEBUG :: filling InParalog matrix for A")
          else:
            if not Ai[i, j]:
              Ai[i, j] = tmpInpaW
              inparaWrtA += 1

        # search for in-paralogs to store in Ai (for the left part)
        # compute all the possible combinations
        #print("\nadd inparalogs relations for {:d} paralogs in species {:d}...".format(len(rxOrthoList), spB))
        inParaRel = list(combinations(sorted(rxOrthoList), r=2))
        #print(inParaRel)
        for tplIdx in inParaRel:
          i, j = tplIdx
          tmpInpaW = round( (rxDict[i] + rxDict[j]) / 2. , 3)
          # make sure that the matrix is upper triangular
          if i > j: # below the diagonal
            #print("i > j", i, j)
            # swap the indexes
            tmpJ = i
            tmpI = j
            #print("swapped(i, j)", tmpI, tmpJ)
            if not Bi[tmpI, tmpJ]:
              print(str(Bi[tmpI, tmpJ]))
              Bi[tmpI, tmpJ] = tmpInpaW
              inparaWrtB += 1
              continue
          elif i == j:
            diagCntB += 1
            print("same!", i, j)
            print("This should not happen!")
            sys.exit("DEBUG :: filling InParalog matrix for A")
          else:
            if not Bi[i, j]:
              Bi[i, j] = tmpInpaW
              inparaWrtB += 1
        #print("Cluster processing done!\n")
        #sys.exit("DEBUG :: create_matrix_from_orthotbl")

    #close input file
    fclose(cfile)

    # sys.exit("DEBUG@graph_c -> create_matrix_from_orthotbl")

    # empty the dictionary for checking repeats
    repeatTrapLx.clear()
    repeatTrapRx.clear()
    del repeatTrapLx
    del repeatTrapRx
    lxDict.clear()
    lxDictInp.clear()
    lxDictMain.clear()
    rxDict.clear()
    rxDictInp.clear()
    rxDictMain.clear()
    del rxDict, rxDictInp, rxDictMain
    del lxDict
    del lxDictInp
    del lxDictMain

    # print the current ortholog matrix
    #print(AB.todense())
    # store the matrix with orthologs
    # convert to a CSR matrix AB
    AB = AB.tocsr()
    cdef str AB_name = f"{pairName}.npz"
    cdef str tmpMtxFilePath = os.path.join(outDir, AB_name)
    # save the matrix AB
    ofd: BinaryIO = open(tmpMtxFilePath, "wb")
    save_npz(tmpMtxFilePath, AB, compressed=False)
    ofd.close()

    # convert to a CSR matrix and save matrix Ai
    Ai = Ai.tocsr()
    cdef str Ai_name = f"{pairName}_i{spA}.npz"
    tmpMtxFilePath = os.path.join(outDir, Ai_name)
    # save the matrix Ai
    ofd: BinaryIO = open(tmpMtxFilePath, "wb")
    save_npz(tmpMtxFilePath, Ai, compressed=False)
    ofd.close()

    # convert to a CSR matrix and save matrix Bi
    Bi = Bi.tocsr()
    cdef str Bi_name = f"{pairName}_i{spB}.npz"
    tmpMtxFilePath = os.path.join(outDir, Bi_name)
    # save the matrix Bi
    ofd: BinaryIO = open(tmpMtxFilePath, "wb")
    save_npz(tmpMtxFilePath, Bi, compressed=False)
    ofd.close()

    '''
    if debug:
      print(f"\nOrtholog relations in matrix for {pairName}:\t{AB.nnz}")
      print(f"Inparalog relations in matrix for species {spA}:\t{Ai.nnz}")
      print(f"Inparalog relations in matrix for species {spB}:\t{Bi.nnz}")
    '''
    # Free memory used by matrixes
    del Bi
    del Ai
    del AB

    # return names of created matrixes
    return(AB_name, Ai_name, Bi_name)



'''
def dump_inpara_adjacency(mtxPath: str, sp: int, outDir: str, dumpGraph: bool = False, debug: bool=False) -> str:
    """Load inparalogs from matrix and store a dictionary with adjacency paths."""
    if not os.path.isfile(mtxPath):
        sys.stderr.write("\nERROR: the matrix file\n{:s}\n was not found.".format(mtxPath))
        sys.exit(-2)
    # define the input species
    bname: str = os.path.basename(mtxPath).rsplit(".", 1)[0] # remove extension and directory name
    currentSp: str = str(sp)

    if debug:
        print("\ndump_inpara_adjacency :: START")
        print("Input matrix:\t{:s}".format(mtxPath))
       # print("Proteome pair:\t{:s}".format(pair))
        print("Current proteome:\t{:s}".format(currentSp))
        print("Output directory:\t{:s}".format(outDir))
        print("Output graph file:\t{:s}".format(str(dumpGraph)))

    #sys.exit("DEBUG :: dump_inpara_adjacency")

    # load the matrix file
    M = load_npz(mtxPath)
    # add the transpose
    M = M + M.transpose()
    # create the directed graph
    G = nx.from_scipy_sparse_matrix(M, create_using=nx.DiGraph)
    # extract dict with adjacency
    edjDict = {x[0]:x[1] for x in G.adjacency() if len(x[1])>0}
    # dump it in a pickle
    pcklPath = os.path.join(outDir, "{:s}_adj.pckl".format(bname))
    with open(pcklPath, "wb") as ofd:
      pickle.dump(edjDict, ofd)
    if debug:
      print("In-paralog nodes with degree > 0 for proteome {:s}:\t{:d}".format(currentSp, len(edjDict)))
    # dump the graph if requested
    if dumpGraph:
      # view using Cythoscape
      nx.write_graphml(G, os.path.join(outDir, "{:s}.graphml".format(bname)))
    return pcklPath



def dump_ortho_adjacency(mtxPath: str, outDir: str, dumpGraph: bool = False, debug: bool=False) -> str:
    """Load orthologs from matrix and store a dictionary with adjacency paths."""
    if not os.path.isfile(mtxPath):
        sys.stderr.write("\nERROR: the matrix file\n{:s}\n was not found.".format(mtxPath))
        sys.exit(-2)
    # define the input species
    bname: str = os.path.basename(mtxPath).rsplit(".", 1)[0] # remove extension and directory name
    sp1, sp2 = bname.split("-", 1)
    if debug:
        print("\ndump_ortho_adjacency :: START")
        print("Input matrix:\t{:s}".format(mtxPath))
        print("Proteome pair:\t{:s}".format(bname))
        print("Output directory:\t{:s}".format(outDir))
        print("Output graph file:\t{:s}".format(str(dumpGraph)))

    # create the Graph
    G = nx.DiGraph()
    # load the matrix file
    M = load_npz(mtxPath)
    # iterate through the matrix and fill the graph
    nnzR, nnzC = M.nonzero()
    for i, row in enumerate(nnzR):
      col = nnzC[i]
      orthoW = M[row, col]
      # add the node to the graph
      #G.add_edge(row, col, weight=orthoW)
      #G.add_edge(col, row, weight=orthoW)
      # to avoid the possibility of self-loop
      # use string IDs instead
      rowStr = "{:s}.{:d}".format(sp1, row)
      colStr = "{:s}.{:d}".format(sp2, col)
      G.add_edge(rowStr, colStr, weight=orthoW)
      G.add_edge(colStr, rowStr, weight=orthoW)
      if col == row:
        print("WARNING: row and column are same ({:d}, {:d}). This could be a self loop.".format(row, col))

    # extract dict with adjacency
    edjDict = {x[0]:x[1] for x in G.adjacency() if len(x[1])>0}
    # dump it in a pickle
    pcklPath = os.path.join(outDir, "{:s}_adj.pckl".format(bname))
    with open(pcklPath, "wb") as ofd:
      pickle.dump(edjDict, ofd)
    if debug:
      print("Orthology nodes with degree > 0 for pair {:s}:\t{:d}".format(bname, len(edjDict)))
    # dump the graph if requested
    if dumpGraph:
      # view using Cythoscape
      nx.write_graphml(G, os.path.join(outDir, "{:s}.graphml".format(bname)))

    return pcklPath
'''



# def merge_inparalog_matrixes(sp: int, combMtx: csr_matrix, inDir: str, outDir: str, removeMerged: bool=True, debug: bool=False) -> str:
cdef str merge_inparalog_matrixes(unsigned int sp, object combMtx, str inDir, str outDir, bint removeMerged=1, bint debug=0):
    """Merge all inparalog matrixes for a given species into a single one."""
    if debug:
        print("\nmerge_inparalog_matrixes :: START")
        print(f"Species:\t{sp}")
        print(f"Shape of matrix with combinations:\t{str(combMtx.shape)}")
        print(f"Input directory:\t{inDir}")
        print(f"Output directory:\t{outDir}")

    # sys.exit("DEBUG@graph_c.pyx -> merge_inparalog_matrixes")

    # extract the column and row corresponding to the input species
    cdef unsigned int spMtxIdx = sp - 1 # adjust the species idx (matrixes idxs start from 0)
    cdef cnp.ndarray[cnp.int64_t, ndim=1] rowSpY = combMtx.getrow(spMtxIdx).toarray().nonzero()[1] # only keep the column idx (Y), the row is spMtxIdx
    cdef cnp.ndarray[cnp.int64_t, ndim=1] colSpX = combMtx.getcol(spMtxIdx).toarray().nonzero()[0] # only keep the row idx (X), the column is spMtxIdx
    # save the combinations in a dictionary
    cdef dict combDict = {} #dict[tuple[int, int], int]
    cdef unsigned int cIdx, rIdx, sp1, sp2
    # extract from row non-zero indexes
    for cIdx in colSpX:
        combDict[(cIdx, spMtxIdx)] = 0
    # extract from row non-zero indexes
    for rIdx in rowSpY:
        combDict[(spMtxIdx, rIdx)] = 0

    # matrix with count for ortholog appearance
    cdef (unsigned int, unsigned int) mtxShape = (0, 0)
    accMtx = None
    masterM = None
    M = None
    if debug:
        print(f"Combinations found species {sp}:")
    cdef (unsigned int, unsigned int) tpl = (0, 0)
    cdef str mPath

    for i, tpl in enumerate(combDict):
        sp1, sp2 = tpl
        mPath = os.path.join(inDir, f"{sp1+1}/{sp1+1}-{sp2+1}_i{sp}.npz")
        '''
        if debug:
            print("\n", str(tpl))
            print("sp1 =", sp1, "sp2 =", sp2, "sp =", sp)
            print(f"Adding values from {os.path.basename(mPath)} to the master inparalog matrix...")
        '''
        if not os.path.isfile(mPath):
            sys.stderr.write(f"\nERROR: the matrix file\n{mPath}\nwas not found!\n")
            sys.exit(-2)
        # load the inparalog matrix
        M = load_npz(mPath)
        # initialize the count matrix if required
        if accMtx is None:
            mtxShape = M.shape
            if mtxShape[0] != mtxShape[1]:
                sys.stderr.write(f"\nERROR: the inparalog matrix must be a N x N matrix where N is the number of proteins in the proteome for species {sp}!\n")
                sys.exit(-5)
            # initilize the matrix as the ceiling of that with inparalogs
            # create an array of zeros
            # create the sparse matrix for the appearence counts
            # the ceiling of each value will be taken and stored as int8 type
            # and then converted to an upper triangular matrix
            accMtx = triu(csr_matrix(M.ceil(), dtype=np.int8), k=0)
            # set the master matrix as the one the first one loaded (M)
            masterM = M.copy()
            '''
            if debug:
                print("\nFirst initialization...")
                print("masterM info:")
                print(type(masterM))
                print(masterM.shape, masterM.nnz)
                print("M info:")
                print(type(M))
                print(M.shape, M.nnz)
                print("accMtx info:")
                print(type(accMtx))
                print(accMtx.shape, accMtx.nnz, "\n")
            '''
            if removeMerged:
                os.remove(mPath)
            continue
        # update the accumulator and sum the values in matrixes
        else:
            '''
            if debug:
                print("\nMatrix merging step...")
                print("M info:")
                print(type(M))
                print(M.shape, M.nnz)
                print("accMtx info:")
                print(type(accMtx))
                print(accMtx.shape, accMtx.nnz)
                print("masterM info:")
                print(type(masterM))
                print(masterM.shape, masterM.nnz, "\n")
            '''
            # sum the inparalog scores
            masterM = masterM + M
            # increment the accumulator
            accMtx = accMtx + triu(csr_matrix(M.ceil(), dtype=np.int8), k=0)
        # remove the merged matrix if required
        if removeMerged:
            os.remove(mPath)

    ##### NOTE #####
    # Because division by 0 would give a NaN which need to be stored in memory
    # better to iterate thrhough the non-zero indexes and perform the divisions
    ################
    cdef cnp.ndarray[cnp.int32_t, ndim=1] nnzR
    cdef cnp.ndarray[cnp.int32_t, ndim=1] nnzC
    nnzR, nnzC = masterM.nonzero()
    cdef unsigned int col, row
    cdef double currentVal
    cdef size_t loopIter

    for loopIter in range(nnzR.shape[0]):
        # the use row and column nnzC[i] to access the values
        row = nnzR[loopIter]
        col = nnzC[loopIter]
        currentVal = masterM[row, col]
        #print(row, col, currentVal, accMtx[row, col])
        # this should never happen
        if currentVal == 0:
            sys.stderr.write("ERROR: No value can be 0, make sure that the accumulator matrix and inparalog marix refer to the same species.\n")
            sys.exit(-5)
        masterM[row, col] = round(currentVal / accMtx[row, col], 3)

    '''
    if debug:
        print("masterM info after all merging:")
        print(type(masterM))
        print(masterM.shape)
        print(masterM.nnz)
    '''
    # make sure there are non NaN in the master matrix
    # store the matrix as a csr
    cdef str outMtxPath = os.path.join(outDir, f"inparalogs/master_i{sp}.npz")
    ofd: BinaryIO = open(outMtxPath, "wb")
    save_npz(ofd, masterM, compressed=False)
    ofd.close()
    # return the output path
    return outMtxPath



# NOTE consider generating the connections by iterating the matrix of inparalogs instead of generating the graph
# def write_per_species_mcl_graph(sp: int, offSetDict: dict[int, int], mtxDir: str, outDir: str, combMtxPath: str, debug: bool=False):
cdef str write_per_species_mcl_graph(unsigned int sp, dict offSetDict, str mtxDir, str outDir, str combMtxPath, bint debug=0):
    """Merge all inparalog matrixes for a given species into a single one."""
    if debug:
        print("\nwrite_per_species_mcl_graph :: START")
        print(f"Species:\t{sp}")
        print(f"Species offsets:\t{len(offSetDict)}")
        print(f"Directory with matrixes: {mtxDir}")
        print(f"Output directory: {outDir}")
        print(f"Path to the matrix with species combinations: {combMtxPath}")
    # check that the matrix with combinations exists
    if not os.path.isfile(combMtxPath):
      sys.stderr.write(f"\nERROR: the file with the combination matrix\n{combMtxPath}\nwas not found!\n")
      sys.exit(-2)

    # sys.exit("DEBUG@graph_c.pyx -> write_per_species_mcl_graph")
    # load the matrix
    ### NOTE: there could be a problem with species indexes when
    ### considering subset of species (e.g., 1,2,5)
    ### This issue can be handle by proving a list of the species
    ### to be considered in the run and skip those when loading the combinations
    M = load_npz(combMtxPath) # this an upper triangular matrix
    # extract the column and row corresponding to the input species
    cdef unsigned int spMtxIdx = sp - 1 # adjust the species idx (matrixes idxs start from 0)
    cdef cnp.ndarray[cnp.int64_t, ndim=1] rowSpY = M.getrow(spMtxIdx).toarray().nonzero()[1] # only keep the column idx (Y), the row is spMtxIdx
    cdef cnp.ndarray[cnp.int64_t, ndim=1] colSpX = M.getcol(spMtxIdx).toarray().nonzero()[0] # only keep the row idx (X), the column is spMtxIdx

    # save the combinations in a dictionary
    combDict: dict[tuple[int, int], int] = {}
    # extract from row non-zero indexes
    for cIdx in colSpX:
      combDict[(cIdx, spMtxIdx)] = 0
    # extract from row non-zero indexes
    for rIdx in rowSpY:
      combDict[(spMtxIdx, rIdx)] = 0
    if debug:
      print(f"Combinations found for species {sp}:")
      print(str(combDict))
    # free some memory
    del M

    # load adjacency from master inparalog matrix
    cdef str mtxPath = os.path.join(mtxDir, f"inparalogs/master_i{sp}.npz")
    if debug:
      print(f"Loading in-paralog matrix:\n{mtxPath}")
    M = load_npz(mtxPath)
    # add the transpose
    M = M + M.transpose()

    # create an array with the gene ids for the current species
    # as they would be in the MCL graph
    cdef cnp.ndarray[cnp.int64_t, ndim=1] colIdx = np.array(np.arange(M.shape[0]))

    # add offset the indexes
    cdef unsigned int tmpOffset = offSetDict[sp]
    if tmpOffset > 0:
      colIdx = colIdx + tmpOffset

    if debug:
      print(f"\nIndexes for species {sp} after adding a offset of {tmpOffset}")
      print(f"Elements:\t{len(colIdx)}")
      print(f"Start:\t{colIdx.min()}")
      print(f"End:\t{colIdx.max()}")

    # initialize the master dictionary that will contain the graph edjes
    # cdef dict masterAdjDict = {} # dict[int, dict[int, float]]

    cdef dict masterAdjDict = {x:{} for x in colIdx}
    del colIdx

    # iterate through the matrix and fill the graph
    cdef cnp.ndarray[cnp.int32_t, ndim=1] nnzR
    cdef cnp.ndarray[cnp.int32_t, ndim=1] nnzC
    nnzR, nnzC = M.nonzero()
    # add the offSets to the non-zero row and columns
    cdef cnp.ndarray[cnp.int32_t, ndim=1] mclRows = nnzR + tmpOffset
    cdef cnp.ndarray[cnp.int32_t, ndim=1] mclCols = nnzC + tmpOffset
    cdef unsigned int col, row, mclRow, mclCol
    cdef double currentW
    cdef size_t loopIter

    # sys.exit("DEBUG")
    # for i, row in enumerate(nnzR):
    for loopIter in range(nnzR.shape[0]):
      # the use row and column nnzC[i] to access the values
      row = nnzR[loopIter]
      col = nnzC[loopIter]
      # extract the values and fill the dictionary
      currentW = M[row, col]
      mclRow = mclRows[loopIter]
      mclCol = mclCols[loopIter]
      # add the entry in the master dictionary
      masterAdjDict[mclRow][mclCol] = currentW
      if debug:
        print(f"row: {row:d}->{mclRow:d}\tcol: {col:d}->{mclCol:d}\t{currentW:.3f}")
        print(f"{mclRow:d} ->\t{masterAdjDict[mclRow]}\n")

    if debug:
      print(f"### Finished processing the in-paralog matrix {os.path.basename(mtxPath)} ###")
      print(f"In-paralog nodes in connection dictionary:\t{len(masterAdjDict)}")

    # Extract the adjacency for orthologs
    # set to true if the the current species is the second in the pair
    # transpose: bool = False

    cdef (unsigned int, unsigned int) tpl
    cdef unsigned int sp1, sp2, colOffset, rowOffset
    # for each combination in combDict
    for tpl in combDict:
      if debug:
        print(f"Processing idx pair {str(tpl)}, with {sp} being the current species.\n")
      sp1, sp2 = tpl
      mtxPath = os.path.join(mtxDir, f"{sp1+1}/{sp1+1}-{sp2+1}.npz")
      # sys.exit("DEBUG@graph_c.pyx -> write_per_species_mcl_graph")
      if not os.path.isfile(mtxPath):
        sys.stderr.write("\nERROR: the ortholog matrix file\n{:s}\nwas not found!\n".format(mtxPath))
        sys.exit(-2)
      # load the ortholog matrix
      M = load_npz(mtxPath)
      # set the transpose flag
      if sp2 + 1 == sp:
        # traspose = True
        if debug:
          print(f"INFO: The transpose of {os.path.basename(mtxPath)} must be used for species {sp}")
        M = M.transpose()
        colOffset = offSetDict[sp1 + 1]
      else:
        # traspose = False
        colOffset = offSetDict[sp2 + 1]

      # set the offsets for row and column indexes
      rowOffset = tmpOffset
      if debug:
        print(f"Loaded ortholog matrix:\n{mtxPath}")
        print(f"Matrix shape:\t{M.shape}")
        print(f"Row offset:\t{rowOffset}")
        print(f"Column offset:\t{colOffset}\n")

      # iterate through the matrix and fill the graph
      nnzR, nnzC = M.nonzero()
      # add the offSets to the non-zero row and columns
      mclRows = nnzR + rowOffset
      mclCols = nnzC + colOffset
      # clear the graph and edje dictionary
      #G.clear()
      #edjDict.clear()

    #   for i, row in enumerate(nnzR):
      for loopIter in range(nnzR.shape[0]):
        # the use row and column nnzC[i] to access the values
        row = nnzR[loopIter]
        col = nnzC[loopIter]

        currentW = M[row, col]
        mclRow = mclRows[loopIter]
        mclCol = mclCols[loopIter]
        # add the entry in the master dictionary
        masterAdjDict[mclRow][mclCol] = currentW
        if debug:
          print(f"row: {row:d}->{mclRow:d}\tcol: {col:d}->{mclCol:d}\t{currentW:.3f}")
          print(f"{mclRow:d} ->\t{masterAdjDict[mclRow]:s}\n")

      if debug:
        print("### Finished processing the ortholog matrix {:s} ###".format(os.path.basename(mtxPath)))

    # create the graph file
    cdef str spGraphPath = os.path.join(outDir, f"mcl_graph_{sp}.txt")
    # open the output file
    ofd: TextIO = open(spGraphPath, "wt")
    # write the content of the master dictionary in the graph file
    for source, connections in masterAdjDict.items():
      ofd.write(f"{source:d}    ")
      for prot, weight in connections.items():
        if weight == 1:
          ofd.write(f"{prot}:1 ")
        else:
          ofd.write(f"{prot:d}:{weight:.3f} ")
      ofd.write("$\n")
    ofd.close()
    # return the path to the graph file
    return spGraphPath



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
