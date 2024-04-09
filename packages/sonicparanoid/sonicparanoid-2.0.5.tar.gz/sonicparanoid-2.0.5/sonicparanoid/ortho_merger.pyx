# -*- coding: utf-8 -*-
# cython: profile=False
"""
This module contains functions related to domain-based orthology inference.
"""

from __future__ import annotations

from libc.stdio cimport FILE
from libc.stdlib cimport atol, atof

cdef extern from "stdio.h":
    FILE *fopen(const char *, const char *)
    int fclose(FILE *)
    ssize_t getline(char **, size_t *, FILE *)

import sys
import os
import logging
# from collections import deque
from pickle import load
import multiprocessing as mp
import queue
from tqdm import tqdm
from time import perf_counter
from typing import TextIO, BinaryIO
from dataclasses import dataclass

# import scipy sparse matrixes
# from scipy.sparse import dok_matrix, lil_matrix, csr_matrix, coo_matrix, save_npz, load_npz, triu

import numpy as np
cimport numpy as cnp
cimport cython

# internal modules
# from sonicparanoid import <module_name>


'''
__module_name__ = "cluster merging"
__source__ = "cluster_merging.pyx"
__author__ = "Salvatore Cosentino"
__license__ = "GPLv3"
__version__ = "1.3"
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



@dataclass
class MergedClstr:
    """Cluster of merged arch- and graph-based orthologs relationships.

    Args:
        size: number of orthologs in the cluster (from both species).
        sp1Ids: Protein IDs of ortholog archs froms species 1
        sp2Ids: Protein IDs of ortholog archs froms species 2
        sp1Scores: array of doubles with the scores assigned orhtologs from species 1
        sp2Scores: array of doubles with the scores assigned orhtologs from species 2
    """

    size: int
    sp1Ids: np.ndarray
    sp2Ids: np.ndarray
    sp1Scores: np.ndarray
    sp2Scores: np.ndarray

    # FIXME: this should be removed when Cython will natively support dataclass objects
    __annotations__ = {
        'size': int,
        'sp1Ids': np.ndarray,
        'sp2Ids': np.ndarray,
        'sp1Scores': np.ndarray,
        'sp2Scores': np.ndarray,
    }



### Workers ###
cdef void consume_integrate_arch_ortho_into_gclstr(object jobs_queue, object results_queue, str outDir, dict archMasterDict, double covThr):
    """
    Integrate arch-ortholog into graph based clusters
    """

    cdef str gTblPath
    cdef str aTblPath
    cdef (unsigned int, unsigned int) pair
    cdef dict graphSp1Ortho2info # dict[int, tuple[int, float]]
    cdef dict graphSp2Ortho2info # dict[int, tuple[int, float]]
    cdef dict aClstrDict = {} # dict[int, ArchClstr] Dictionary containing arch-based clusters
    cdef dict mClstrDict = {} # dict[int, MergedClstr] Dictionary containing merged clusters
    # cdef double totextime
    cdef (unsigned long, unsigned long, unsigned long, unsigned long, unsigned long, unsigned long, unsigned long, unsigned long) mergeResTpl

    while True:
        jobTpl: tuple[tuple[int, int], str, str] = jobs_queue.get(True, 1)

        if jobTpl is None:
            break

        # Set main variables
        pair = jobTpl[0]
        gTblPath = jobTpl[1]
        aTblPath = jobTpl[2]
        # print(f"Pair:\t{pair}")
        # Load graph based orthologs
        mClstrDict, graphSp1Ortho2info, graphSp2Ortho2info = load_graph_orto_tbl(tblPath=gTblPath)
        # print(f"\nGraph clusters file: {gTblPath}")
        # print(f"Loaded Graph clusters:\t{len(mClstrDict)}")
        # Load arch based orthologs
        # aClstrDict = load_arch_orto_tbl(tblPath=aTblPath)
        aClstrDict = load_arch_ortho_pckl(pcklPath=aTblPath)
        # print(f"\nArch clusters file: {aTblPath}")
        # print(f"Loaded Arch clusters:\t{len(aClstrDict)}")

        # Merge the orthlog tables
        mergeResTpl = integrate_arch_ortho_into_gclstr(aClstrDict, mClstrDict, graphSp1Ortho2info, graphSp2Ortho2info, pair[0], pair[1], archMasterDict, covThr)
        # sys.exit("\nDEBUG: ortho_merger :: consume_integrate_arch_ortho_into_gclstr")

        # print(f"Clusters:\t{len(aClstrDict)}")
        # Write the ortholog table to TSV
        write_merged_clstr_to_file(mClstrDict, outDir=outDir, sp1Id=f"{pair[0]:d}", sp2Id=f"{pair[1]:d}")
        # Write the file with pairs
        # write_pairs_to_file(mClstrDict, outDir=outDir, sp1Id=f"{pair[0]:d}", sp2Id=f"{pair[1]:d}", mergedClstrs=1)

        # sys.exit("DEBUG :: consume_integrate_arch_ortho_into_gclstr")
        # Put the results in the output queue
        results_queue.put(mergeResTpl)



### Multi-threaded functions ###
def parallel_integrate_arch_ortho_into_gclstr(spPairs: list[tuple[int, int]], inDirGraphBased: str, inDirArchBased: str, archMasterDict: dict[int, dict[int, Arch]], outDir: str, covThr: float = 0.75, threads: int = 4) -> None:
    """Merge arch- an graph-based ortholog tables.

    Parameters:
    spPairs list[tuple[int, int]]: pairs of species for which ortholog tables should be merged
    inDirGraphBased (str): Path to the directory with graph-based orhtolog tables
    inDirArchBased (str): Path to the directory with arch-based orhtolog tables
    archMasterDict Dict[int, Dict[int, Arch]]: Dictionary with architecture information
    outDir (str): Directory in which the merged tables will be stored
    covThr (float): coverage threshold used for arch-based orhtologs
    threads (unsigned int): Threads

    Returns:
    void

    """

    cdef unsigned int spCnt = len(archMasterDict)
    cdef unsigned int pairsCnt = len(spPairs)

    debugStr: str = f"""parallel_integrate_arch_ortho_into_gclstr :: START
    Species pairs to be compared:\t{pairsCnt:d}
    Directory with graph-based ortholog tables: {inDirGraphBased}
    Directory with arch-based ortholog tables: {inDirArchBased}
    Species in master arch dictionary:\t{spCnt:d}
    Output directory: {outDir}
    Minimum coverage for arch orthologs:\t{covThr:.2f}
    Threads:\t{threads:d}"""
    logger.debug(debugStr)
    '''
    '''

    cdef size_t i
    cdef str gTblPath = ""
    cdef str aTblPath = ""
    cdef (unsigned int, unsigned int) pair = (0, 0)
    # Extract the path of ortholog tables
    graphBasedPaths: dict[tuple[int, int], str] = get_graph_ortho_table_paths(inDir=inDirGraphBased, spPairs=spPairs)
    # print(f"Loaded graph paths:\t{len(graphBasedPaths)}")
    archBasedPaths: dict[tuple[int, int], str] = get_arch_ortho_table_paths(inDir=inDirArchBased, spPairs=spPairs, pcklFiles=1)
    # print(f"Loaded arch-based paths:\t{len(archBasedPaths)}")
    cdef str runInfoFile = os.path.join(outDir, "ortholog_tables_merging.info.txt")
    cdef dict infoDict = {"Module:":__name__}
    infoDict["Pairs of species:"] = str(pairsCnt)
    infoDict["Graph-based ortholog tables directory:"] = inDirGraphBased
    infoDict["Arch-based ortholog tables directory:"] = inDirArchBased
    infoDict["Species in master arch dictionary:"] = str(spCnt)
    infoDict["Main output dir:"] = outDir
    infoDict["Minimum coverage for arch orthologs:"] = f"{covThr:.2f}"
    infoDict["Threads:"] = str(threads)
    write_run_info_file(runInfoFile, infoDict)

    # Create the output directories if required
    makedir(outDir)
    # this contains the contains the following:
    # 0 -> (int,int)
    # 1 -> path to graph-based table
    # 2 -> path to arch-based table
    jobTpl: tuple[tuple[int, int], str, str] = ((0, 0), "", "")

    # reset timers
    cdef double start_time
    # create the queue and start adding
    proc_queue: mp.queues.Queue = mp.Queue(maxsize=pairsCnt + threads)

    for i in range(pairsCnt):
        pair = spPairs[i]
        gTblPath = graphBasedPaths[pair]
        aTblPath = archBasedPaths[pair]
        jobTpl = (pair, gTblPath, aTblPath)
        proc_queue.put(jobTpl)

    # add flags for ended jobs
    for i in range(0, threads):
        sys.stdout.flush()
        proc_queue.put(None)

    # Queue to contain the documents for each file
    results_queue: mp.queues.Queue = mp.Queue(maxsize=pairsCnt)

    # List of running jobs
    cdef list runningJobs = [mp.Process(target=consume_integrate_arch_ortho_into_gclstr, args=(proc_queue, results_queue, outDir, archMasterDict, covThr)) for i_ in range(threads)]

    # calculate cpu-time for alignments
    start_time = perf_counter()
    # write some message...
    sys.stdout.write(f"\nMerging {pairsCnt} arch- and graph-based ortholog tables...")
    # All documents will be written in this file
    cdef str outPath = os.path.join(outDir, "stats.ortho_tbls_merging.tsv")
    # ofd: TextIO = open(outPath, "wt", buffering=1) # Default buffering should be ok
    ofd: TextIO = open(outPath, "wt") # Default buffering should be ok

    # Write the HDR
    ofd.write("pair\tg_clstrs\ta_clstrs\tmerged_clstrs\tnew_clstrs\tmodified_g_clstr\trejected_a_clstrs\n")
    # Length of list with results from each job
    cdef bint allExited = 0

    # execute the jobs
    for proc in runningJobs:
        proc.start()

    # Show the progress bars
    pbar: tqdm = tqdm(total=pairsCnt, desc="Ortholog merging", unit="table pairs", disable=None, smoothing=0.3, ascii=False, miniters=1, mininterval=2.0, colour='green')

    cdef (unsigned int, unsigned int, unsigned int, unsigned int, unsigned int, unsigned int, unsigned int, unsigned int) mergeResTpl
    # write output when available
    while True:
        try:
            # pair = results_queue.get(False, 0.01)
            mergeResTpl = results_queue.get(False, 0.01)
            ofd.write(f"{mergeResTpl[0]:d}-{mergeResTpl[1]:d}\t{mergeResTpl[2]:d}\t{mergeResTpl[3]:d}\t{mergeResTpl[4]:d}\t{mergeResTpl[5]:d}\t{mergeResTpl[6]:d}\t{mergeResTpl[7]:d}\n")
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

    # Close the progress bar
    pbar.close()

    # Close output file
    ofd.close()

    # this joins the processes after we got the results
    for proc in runningJobs:
        while proc.is_alive():
            proc.join()

    # stop the counter for the alignment time
    sys.stdout.write(f"\nElapsed time for merging ortholog tables (seconds):\t{round(perf_counter() - start_time, 3)}\n")



### Other functions ###

# def get_arch_ortho_table_paths(inDir: str, spPairs: list[tuple[int, int]]) -> dict[tuple[int, int], str]:
cdef dict get_arch_ortho_table_paths(str inDir, list spPairs, bint pcklFiles):
    """Obtain paths gof raph-based ortholog tables."""

    logger.debug(f"""get_arch_ortho_table_paths :: START
        inDir: {inDir}
        Pairs:\t{len(spPairs)}""")

    cdef size_t i
    cdef str tmpPath
    # associate a path to each file name
    cdef dict outDict = {} # dict[tuple[int, int], str] = {}
    cdef (unsigned long, unsigned long) pair = (0, 0)
    cdef unsigned long pairsCnt = len(spPairs)
    cdef unsigned long pathsCnt
    # Set the suffix of the file name first
    # The pckl file names should have the following pattern
    # <sp1>-<sp2>.arch.ortho.pckl
    cdef str fnameSuffix = "arch.ortho.pckl"
    # The TSV-table file names should have the following pattern
    # <sp1>-<sp2>.arch.ortho.tsv
    if pcklFiles == 0:
        fnameSuffix = "arch.ortho.tsv"

    # Check if the table files exist
    for i in range(pairsCnt):
        pair = spPairs[i]
        tmpTblName = f"{pair[0]}-{pair[1]}.{fnameSuffix}"
        # tmpPath = os.path.join(inDir, tmpTblName)
        tmpPath = os.path.join(inDir, f"{pair[0]}/{tmpTblName}")
        if not os.path.isfile(tmpPath):
            logging.error(f"""The file {tmpTblName} for the arch-based table pair {pair} was not found!""")
            sys.exit(-5)
        else:
            outDict[pair] = tmpPath

    pathsCnt = len(outDict)
    # Check that all tables where found
    if pathsCnt != pairsCnt:
        logging.error(f"""The number of arch-based table files found {pathsCnt} differs from the nummber of species combinations {pairsCnt}!""")
        sys.exit(-5)

    return outDict



# def get_graph_ortho_table_paths(inDir: str, spPairs: list[tuple[int, int]]) -> dict[tuple[int, int], str]:
cdef dict get_graph_ortho_table_paths(str inDir, list spPairs):
    """Obtain paths gof raph-based ortholog tables."""

    logger.debug(f"""get_graph_ortho_table_paths :: START
        inDir: {inDir}
        Pairs:\t{len(spPairs)}""")

    cdef size_t i
    cdef str tmpPath
    cdef str tmpTblName
    # associate a path to each file name
    cdef dict outDict = {} # dict[tuple[int, int], str] = {}
    cdef (unsigned long, unsigned long) pair = (0, 0)
    cdef unsigned long pairsCnt = len(spPairs)
    cdef unsigned long pathsCnt

    # Check if the table files exist
    for i in range(pairsCnt):
        pair = spPairs[i]
        # print(pair)
        # The file names should have the following pattern
        # <sp1>-<sp2>arch.ortho.tsv
        # tmpTblName = f"table.{sp1}-{sp2}"
        tmpTblName = f"table.{pair[0]}-{pair[1]}"
        tmpPath = os.path.join(inDir, f"{pair[0]}/{tmpTblName}")
        if not os.path.isfile(tmpPath):
            logging.error(f"""The file {tmpTblName} for the graph-based table pair {pair} was not found!""")
            sys.exit(-5)
        else:
            outDict[pair] = tmpPath

    pathsCnt = len(outDict)

    # Check that all tables where found
    if pathsCnt != pairsCnt:
        logging.error(f"""The number of graph-based table files found {pathsCnt} differs from the nummber of species combinations {pairsCnt}!""")
        sys.exit(-5)

    return outDict



cdef dict check_arch_cluster_membership(cnp.uint32_t[:] aSp1IdsView, cnp.uint32_t[:] aSp2IdsView, cnp.ndarray[cnp.uint32_t, ndim=1] gSp1Orthologs, cnp.ndarray[cnp.uint32_t, ndim=1] gSp2Orthologs):
    """
        Check if the a cluster of arch-based ortholog is also predicted by the graph method.

        Returns a dictionary containing, for each of the two species in the cluster,
        An integer representing the kind of membership, and an array with indexes of ortholog that are already in G.
    """

    '''
    debugStr: str = f"""check_arch_cluster_membership :: START
    Arch-based ortho Sp1:\t{aSp1IdsView.shape[0]}
    Arch-based ortho Sp2:\t{aSp2IdsView.shape[0]}
    Graph ortho from Sp1:\t{gSp1Orthologs.shape[0]}
    Graph ortho from Sp2:\t{gSp2Orthologs.shape[0]}"""
    logger.debug(debugStr)
    '''

    cdef size_t i # Indexes to be used in for loops
    cdef unsigned int aSp1OrthoCnt = aSp1IdsView.shape[0]
    cdef unsigned int aSp2OrthoCnt = aSp2IdsView.shape[0]
    # these arrays will contain the indexes of the arrays with ortholog IDs
    # that are contained in G
    # NOTE: if none of the members are contained in G
    # then idx array must contain no element (e.g., sp1ContainedIdxs.shape[0]==0)
    cdef cnp.ndarray[cnp.uint8_t, ndim=1] sp1ContainedIdxs = np.zeros(aSp1OrthoCnt, dtype=np.uint8)
    cdef cnp.ndarray[cnp.uint8_t, ndim=1] sp2ContainedIdxs = np.zeros(aSp2OrthoCnt, dtype=np.uint8)

    # Used to see how these clusters are contained (or not) in G
    # 0: not contained in G (new orthologs)
    # 1: contained in a single cluster in G
    # 2: some orthologs are contained in G some are not
    cdef unsigned int sp1ContainedCnt = 0
    cdef unsigned int sp2ContainedCnt = 0
    cdef unsigned int sp1Membership = 0
    cdef unsigned int sp2Membership = 0

    # Check in different ways depending
    # if it is a pair or not
    # print("aOrthos from Sp1:")
    for i in range(aSp1OrthoCnt):
        # print(i, aSp1IdsView[i])
        if aSp1IdsView[i] in gSp1Orthologs:
            # print(aSp1IdsView[i])
            sp1ContainedCnt += 1
            sp1ContainedIdxs[i] = 1

    # Now count those from sp2
    # print("aOrthos from Sp2:")
    for i in range(aSp2OrthoCnt):
        # print(i, aSp2IdsView[i])
        if aSp2IdsView[i] in gSp2Orthologs:
            # print(aSp2IdsView[i])
            sp2ContainedCnt += 1
            sp2ContainedIdxs[i] = 1

    # Set membership for sp1
    if sp1ContainedCnt == 0:
        sp1Membership = 0
        sp1ContainedIdxs = np.zeros(0, dtype=np.uint8)
    # All are contained in G
    elif sp1ContainedCnt == aSp1OrthoCnt:
        sp1Membership = 1
        # print(f"sp1 in G:\t{sp1ContainedIdxs}")
    # Some are contained, and some are not
    else:
        sp1Membership = 2
        # print(f"sp1 (mixed membership):\t{sp1ContainedIdxs}")

    # Set membership for sp2
    if sp2ContainedCnt == 0:
        sp2Membership = 0
        sp2ContainedIdxs = np.zeros(0, dtype=np.uint8)
    # All are contained in G
    elif sp2ContainedCnt == aSp2OrthoCnt:
        sp2Membership = 1
        # print(f"sp2 in G:\t{sp2ContainedIdxs}")
    # Some are contained, and some are not
    else:
        sp2Membership = 2
        # print(f"sp2 (mixed membership):\t{sp2ContainedIdxs}")

    # The output dictionary contains one tuple for each of the 2 species
    # 0 -> represents sp1, and the tuple repsents the membership and the indexes contained in G
    # 1 -> represents sp2
    return {0:(sp1Membership, sp1ContainedIdxs), 1:(sp2Membership, sp2ContainedIdxs)} # dict[tuple[int, ndarray]]



cdef inline dict compute_avg_cosine_scores(list cosineValsList, unsigned int sp1OrthoCnt, unsigned int sp2OrthoCnt):
    """
    Compute the average cosine similarity values to be used when adding
    new arch-based clusters to graph-based ones.
    """
    cdef unsigned int clstrSize = sp1OrthoCnt + sp2OrthoCnt

    '''
    print(f"\nAvg scores computation:")
    print(f"Orhtologs from sp1:\t{sp1OrthoCnt}")
    print(f"Orhtologs from sp2:\t{sp2OrthoCnt}")
    print(f"Cluster size:\t{clstrSize}")
    '''

    # Will contain the average cosine scores for Sp1 and Sp2
    cdef cnp.ndarray[cnp.float32_t, ndim=1] sp1GraphAvgScores
    cdef cnp.ndarray[cnp.float32_t, ndim=1] sp2GraphAvgScores
    cdef cnp.ndarray[cnp.float32_t, ndim=1] tmpScArray
    cdef double cosine = 0

    # Simple case in which avg computation is not required
    if clstrSize == 2:
        tmpScArray = cosineValsList[0]
        return {0:tmpScArray, 1:tmpScArray}

    # inizialize the tmp arrays
    sp1GraphAvgScores = np.zeros(sp1OrthoCnt, dtype=np.float32)
    sp2GraphAvgScores = np.zeros(sp2OrthoCnt, dtype=np.float32)
    tmpScArray = np.zeros(sp1OrthoCnt, dtype=np.float32)

    # Array of sp2OrthoCnt x sp1OrthoCnt dimensions to store the cosine values
    # for orthologs from sp2. Tthe average valuesare computed from this array
    cdef cnp.ndarray[cnp.float32_t, ndim=2] sp2CosineVals = np.zeros(shape=(sp2OrthoCnt, sp1OrthoCnt), dtype=np.float32)

    # First compute the averages for sp1 (simle case)
    for i in range(sp1OrthoCnt):
        # Extract the scores for the ortholog i from Sp1
        tmpScArray = cosineValsList[i]
        # print(tmpScArray)

        # More than 1 orthologs from Sp2
        # x-to-many
        if tmpScArray.shape[0] > 1:
            sp1GraphAvgScores[i] = avg_array_double(tmpScArray)
            for j in range(tmpScArray.shape[0]):
                sp2CosineVals[j][i] = tmpScArray[j]
        # Only one orthologs from sp2
        # many-to-1
        else: # tmpScArray.shape[0] == 1
            cosine = tmpScArray[0]
            sp1GraphAvgScores[i] = cosine
            if sp1OrthoCnt > 1: # many-to-1
                sp2CosineVals[0][i] = cosine

    # Compute the averages cosine values for sp2
    for i in range(sp2OrthoCnt):
        # print("Computing averages for Sp2...")
        # Extract the scores for the ortholog i from Sp1
        tmpScArray = sp2CosineVals[i]
        if tmpScArray.shape[0] > 1:
            sp2GraphAvgScores[i] = avg_array_double(tmpScArray)
        else:
            sp2GraphAvgScores[i] = tmpScArray[0]

    # Output dictionary will contain two arrays of doubles
    # 0: array with average cosine similarities for sp1
    # 1: array with average cosine similarities for sp2
    return {0:sp1GraphAvgScores, 1:sp2GraphAvgScores}



cdef inline bint contained_in_same_g_clstr(cnp.uint32_t[:] aSpxIdsView, cnp.uint8_t[:] spxContainedIdxs,  unsigned long spxOrthoCnt, dict graphSpxOrtho2info):
    """
    For a given set of orhologs already contained in G, check if they all belong to the same G cluster.
    """
    # Contains the IDs of G clusters containing the input orthologs
    cdef dict gClstrs = {}
    cdef size_t i
    cdef bint allInSameGClstr = 0

    for i in range(spxOrthoCnt):
        if spxContainedIdxs[i] == 1:
            gClstrs[graphSpxOrtho2info[aSpxIdsView[i]][0]] = 0

    if len(gClstrs) == 1:
        allInSameGClstr = 1
    '''
    else:
        print(gClstrs)
    '''

    return allInSameGClstr



# def write_merged_clstr_to_file(clstrDict: dict[int, MergedClstr], filePath: str, sp1Id: str, sp2Id: str) -> None:
cdef inline void write_merged_clstr_to_file(dict clstrDict, str outDir, str sp1Id, str sp2Id):
    """Given a dictionary with merged ortholog clusters write a file with the ortholog table."""

    # Tmp variables
    # NOTE: a MergedCluster cluster also refers to graph-based clusters
    tmpClstr: MergedClstr = MergedClstr(0, np.zeros(0, dtype=np.uint32), np.zeros(0, dtype=np.uint32), np.zeros(0, dtype=np.float32), np.zeros(0, dtype=np.float32))
    cdef size_t i, j # Indexes to be used in for loops
    cdef unsigned long clstrCnt = len(clstrDict)
    cdef cnp.uint32_t[:] sp1Ids
    cdef cnp.uint32_t[:] sp2Ids
    cdef cnp.float32_t[:] sp1Scores
    cdef cnp.float32_t[:] sp2Scores
    cdef unsigned long sp1OrthoCnt
    cdef unsigned long sp2OrthoCnt
    cdef unsigned long clstrSize
    cdef unsigned long clstrId
    cdef double tmpScore
    cdef str tmpOrthoStr
    cdef str filePath

    # print(f"\nMerged clusters to write:\t{clstrCnt}")
    # Update the output path to have the sp1 as subdirectory
    outDir = os.path.join(outDir, sp1Id)
    makedir(outDir)
    filePath = f"{outDir}/mtable.{sp1Id}-{sp2Id}"
    # Create the output file
    ofd: TextIO = open(filePath, "wt")
    # Write the file header
    ofd.write("Size\tRelations\tOrthoA\tOrthoB\n")

    for i in range(clstrCnt):
        clstrId = i + 1
        tmpClstr = clstrDict[clstrId]
        clstrSize = getattr(tmpClstr, "size")
        sp1Ids = getattr(tmpClstr, "sp1Ids")
        sp1OrthoCnt = sp1Ids.shape[0]
        sp1Scores = getattr(tmpClstr, "sp1Scores")
        sp2Ids = getattr(tmpClstr, "sp2Ids")
        sp2OrthoCnt = sp2Ids.shape[0]
        sp2Scores = getattr(tmpClstr, "sp2Scores")

        # Case in which it is a single pair
        if clstrSize == 2:
            # FIXME: check the score is not necesserary if it is a pair
            tmpScore = sp2Scores[0]
            # It is a pair with both scores set to 1.0
            if tmpScore == 1:
                ofd.write(f"2\t2\t{sp1Id}.{str(sp1Ids[0])} 1\t{sp2Id}.{str(sp2Ids[0])} 1\n")
            else:
                # This is an arch based pair, and the value is the same for both orthologs
                ofd.write(f"2\t2\t{sp1Id}.{str(sp1Ids[0])} {tmpScore:.3f}\t{sp2Id}.{str(sp2Ids[0])} {tmpScore:.3f}\n")
                # sys.exit("ERROR: this should never happen!")
        else:
            tmpOrthoStr = ""
            # print(f"\nCluster {clstrId}:\n{tmpClstr}")
            # print(f"Clstr size\sp1\sp2:\t{clstrSize}\t{sp1OrthoCnt}\t{sp2OrthoCnt}")
            # Write the cluster size nad number of pairs
            ofd.write(f"{clstrSize}\t{sp1OrthoCnt * sp2OrthoCnt}\t")
            # Process orthologs from sp1
            for j in range(sp1OrthoCnt):
                # ofd.write(f"{sp1Ids[j]} {}\n")
                tmpScore = sp1Scores[j]
                if tmpScore == 1:
                    tmpOrthoStr = f"{tmpOrthoStr}{sp1Id}.{sp1Ids[j]} 1 "
                else:
                    tmpOrthoStr = f"{tmpOrthoStr}{sp1Id}.{sp1Ids[j]} {tmpScore:.3f} "
            # Remove the last space and write sp1 part of the cluster
            ofd.write(f"{tmpOrthoStr[:-1]}\t")
            tmpOrthoStr = ""

            # Process orthologs from sp2
            for j in range(sp2OrthoCnt):
                tmpScore = sp2Scores[j]
                if tmpScore == 1:
                    tmpOrthoStr = f"{tmpOrthoStr}{sp2Id}.{sp2Ids[j]} 1 "
                else:
                    tmpOrthoStr = f"{tmpOrthoStr}{sp2Id}.{sp2Ids[j]} {tmpScore:.3f} "
            ofd.write(f"{tmpOrthoStr[:-1]}\n")

    ofd.close()



cdef inline void write_pairs_to_file(dict clstrDict, str outDir, str sp1Id, str sp2Id, bint mergedClstrs):
    """Given a dictionary with ortholog clusters write a file with the orhtolog pairs."""

    # NOTE: a MergedCluster cluster also refers to graph-based clusters
    tmpClstr: MergedClstr = MergedClstr(0, np.zeros(0, dtype=np.uint32), np.zeros(0, dtype=np.uint32), np.zeros(0, dtype=np.float32), np.zeros(0, dtype=np.float32))
    if not mergedClstrs:
        tmpClstr: ArchClstr =  ArchClstr(0, np.zeros(0, dtype=np.uint32), np.zeros(0, dtype=np.uint32), [])

    # Tmp variables
    cdef size_t i, j, w # Indexes to be used in for loops
    cdef unsigned long clstrCnt = len(clstrDict)
    cdef cnp.uint32_t[:] aSp1IdsView
    cdef cnp.uint32_t[:] aSp2IdsView
    cdef unsigned long sp1OrthoCnt
    cdef unsigned long sp2OrthoCnt
    cdef unsigned long clstrId
    cdef str outPairsStr = ""
    cdef str sp1Ortho = ""
    cdef str filePath

    # The following are used to assure that
    # the are no repeated pairs
    cdef (unsigned long, unsigned long) tmpPair = (0, 0)
    pairSet: set[int, int] = set()
    cdef unsigned long sp1OrthoInt = 0

    # Update the output path to have the sp1 as subdirectory
    outDir = os.path.join(outDir, sp1Id)
    makedir(outDir)
    filePath = f"{outDir}/{sp1Id}-{sp2Id}.merged.ortho.pairs.tsv"
    # Create the output file
    ofd: TextIO = open(filePath, "wt")

    for i in range(clstrCnt):
        clstrId = i + 1
        tmpClstr = clstrDict[clstrId]
        aSp1IdsView = getattr(tmpClstr, "sp1Ids")
        sp1OrthoCnt = aSp1IdsView.shape[0]
        aSp2IdsView = getattr(tmpClstr, "sp2Ids")
        sp2OrthoCnt = aSp2IdsView.shape[0]

        ''' DEBUG ONLY
        if (sp1OrthoCnt + sp2OrthoCnt) != getattr(tmpClstr, "size"):
            print("ERROR: The cluster sizes IDs arrays counts do not match!")
            print(f"Lengths of ID arrays (from array lengths):\t{sp1OrthoCnt}\t{sp2OrthoCnt}")
            print(f"Cluster size:\t{getattr(tmpClstr, 'size')}")
            print(f"Pairs (from array lengths):\t{sp1OrthoCnt * sp2OrthoCnt}")
            sys.exit(-10)
        pairsCntDebug += sp1OrthoCnt * sp2OrthoCnt
        '''

        # Case in which it is a single pair
        if sp1OrthoCnt + sp2OrthoCnt == 2:
            tmpPair = (aSp1IdsView[0], aSp2IdsView[0])
            if not tmpPair in pairSet:
                pairSet.add(tmpPair)
                ofd.write(f"{sp1Id}.{str(aSp1IdsView[0])}\t{sp2Id}.{str(aSp2IdsView[0])}\n")
                # pairsCnt += 1
        else:
            for w in range(sp1OrthoCnt):
                sp1Ortho = str(aSp1IdsView[w])
                sp1OrthoInt = aSp1IdsView[w]
                for j in range(sp2OrthoCnt):
                    tmpPair = (sp1OrthoInt, aSp2IdsView[j])
                    if not tmpPair in pairSet:
                        pairSet.add(tmpPair)
                        outPairsStr = f"{outPairsStr}{sp1Id}.{sp1Ortho}\t{sp2Id}.{str(aSp2IdsView[j])}\n"
                        # pairsCnt += 1
            ofd.write(outPairsStr)
            outPairsStr = ""
    ofd.close()

    # if pairsCnt != pairsCntDebug:
    #     sys.exit(f"The pair counts do not match!\n{pairsCnt}\t{pairsCntDebug}")

    # Print the pairs counts
    # print(f"{sp1Id}-{sp2Id}\t{pairsCnt}")



# @cython.cdivision(True) # Use C division instead of Python division
@cython.boundscheck(False) # Check array bounds
cdef inline list extract_arch_clstr_cosine_vals(bytes rawScoresStr, unsigned long grpLenSp1, unsigned long grpLenSp2):
    """
        Extract cosine values from encoded string.

        Returns a list of arrays of doubles containing the cosine simialries of pairs.
    """
    # print("extract_arch_clstr_cosine_vals :: START")

    # Example of arch-based clusters scores
    # 0.82,0.82:0.73,0.73:0.74,0.74
    # Each list of N scores before the ','
    # represent the cosine values of a protein in Sp1
    # with the N proteins from Sp2

    cdef size_t i # Indexes to be used in for loops
    cdef cnp.ndarray[cnp.float32_t] perProtScores
    scoresList: list[np.andarray] = []
    # Extract the score for a single protein
    tmpBytesList: list[bytes] = rawScoresStr.split(b":", grpLenSp1-1)
    encodedScores: list[bytes] = []

    # Extract the scores for each protein from Sp1
    for i in range(grpLenSp1):
        # encodedScores = tmpBytesList.pop().split(b",", grpLenSp2) # works but the order is inverted
        encodedScores = tmpBytesList[i].split(b",", grpLenSp2)
        # Add the scores into an array
        perProtScores = np.array([atof(x) for x in encodedScores], dtype=np.float32)
        scoresList.append(perProtScores)

    # Return the list with arrays of doubles with the cosine values
    return scoresList



# TODO: change the parameters so that objects are not passed
# HACK: when cython will support DataClasses as paramters in cdef functions
# reduce the number of paramaters and directly passing the DataClass objects (e.g., ArchClstr)
cdef (unsigned long, unsigned long) filter_and_add_arch_ortho2g_clstr(cnp.uint32_t[:] aSp1IdsView, cnp.uint32_t[:] aSp2IdsView, cnp.float32_t[:] aSp1Scores, cnp.float32_t[:] aSp2Scores, cnp.uint8_t[:] aSp1ContainedIdxs, cnp.uint8_t[:] aSp2ContainedIdxs, dict mClstrDict, unsigned long gClstrId, dict archMasterDict, unsigned long sp1Id, unsigned long sp2Id, double covThr, bint allowDomCntMismatch):
    """
    Modify a cluster in G, by adding new arch orthologs if conditions are met.

    NOTE: the functions assumes that all the from A already in G are in the same cluster.
    """

    # print("\nfilter_and_add_arch_ortho2g_clstr :: START")
    # Tmp variables
    cdef size_t i, j # Indexes to be used in for loops
    cdef unsigned long sp1OrthoCnt = aSp1IdsView.shape[0]
    cdef unsigned long sp2OrthoCnt = aSp2IdsView.shape[0]
    # If 1 the arch-cluster should be ignored
    cdef bint ignoreClstr = 0
    cdef double sp1ArchCov
    cdef double sp2ArchCov
    cdef unsigned long sp1ArchDomCnt = 0
    cdef unsigned long sp2ArchDomCnt = 0
    # Tmp variables used to modify the input cluster
    cdef cnp.ndarray[cnp.uint8_t, ndim=1] toRemoveSp1Ids = np.zeros(0, dtype=np.uint8)
    cdef cnp.ndarray[cnp.uint8_t, ndim=1] toRemoveSp2Ids = np.zeros(0, dtype=np.uint8)
    # The first interger describes the state of the cluster
    # 0 -> rejected
    # 1 -> Accepted with some orthologs rejected
    # 2 -> Accepted with no ortholog rejected
    cdef (unsigned long, unsigned long) clusterModOutcome = (0, 0)

    tmpSp1Arch: Arch = Arch(0, 0.0, 0, 0, np.zeros(0, dtype=np.uint32), np.zeros(0, dtype=np.uint32), np.zeros(1, dtype=np.uint32), np.array(["sp1"], dtype=np.str_), np.zeros(0, dtype=np.float32), 1)
    tmpSp2Arch: Arch = Arch(0, 0.0, 0, 0, np.zeros(0, dtype=np.uint32), np.zeros(0, dtype=np.uint32), np.zeros(0, dtype=np.uint32), np.array(["sp2"], dtype=np.str_), np.zeros(0, dtype=np.float32), 1)

    # Iniziliaze the arrays to keep track
    # of what should be removed
    toRemoveSp1Ids = np.zeros(sp1OrthoCnt, dtype=np.uint8)
    toRemoveSp2Ids = np.zeros(sp2OrthoCnt, dtype=np.uint8)
    # Identify orthologs that should be removed
    for i in range(sp1OrthoCnt):
        # Skip if already conatined in G
        if aSp1ContainedIdxs[i] == 1:
            # print(f"Excluding ortholog from Sp1 already in G (at position {i}) from filtering.")
            continue
        # Skip if already flagged as removable
        if toRemoveSp1Ids[i] == 1:
            continue
        # print(f"Processing ortho Sp1:\t{aSp1IdsView[i]}")
        tmpSp1Arch = archMasterDict[sp1Id][aSp1IdsView[i]]
        sp1ArchCov = getattr(tmpSp1Arch, "coverage")
        sp1ArchDomCnt = getattr(tmpSp1Arch, "domCnt")

        if sp1ArchCov < covThr:
            # print(f"Reject ortho Sp1:\tlow coverage\t{sp1ArchCov}")
            # print(getattr(tmpSp1Arch, "phrase"))
            toRemoveSp1Ids[i] = 1
            continue
        for j in range(sp2OrthoCnt):
            # Skip if already conatined in G
            if aSp2ContainedIdxs[j] == 1:
                # print(f"Excluding ortholog from Sp2 already in G (at position {j}) from filtering.")
                continue
            if toRemoveSp2Ids[j] == 1:
                continue # No need to check again
            # print(f"Processing ortho Sp2:\t{aSp2IdsView[j]}")
            tmpSp2Arch = archMasterDict[sp2Id][aSp2IdsView[j]]
            sp2ArchCov = getattr(tmpSp2Arch, "coverage")
            sp2ArchDomCnt = getattr(tmpSp2Arch, "domCnt")

            # NOTE: we reject the whole cluster
            # even if we found a single domain count mismatch
            # this is probably too strict
            # Check the domain counts
            if not allowDomCntMismatch:
                if sp1ArchDomCnt != sp2ArchDomCnt:
                    # print("Domain count mismatch in cluster!")
                    # print(getattr(tmpSp1Arch, "phrase"))
                    # print(getattr(tmpSp2Arch, "phrase"))
                    clusterModOutcome = (0, gClstrId)
                    return clusterModOutcome

            if sp2ArchCov < covThr:
                # print(f"Reject ortho Sp2:\tlow coverage\t{sp2ArchCov}")
                # print(getattr(tmpSp2Arch, "phrase"))
                toRemoveSp2Ids[j] = 1

    # print("Orthologs that will be removed:")
    # print(toRemoveSp1Ids)
    # print(toRemoveSp2Ids)

    # Variables used to create a modified version of the Arch cluster
    # to be added to a graph based cluster
    cdef unsigned long sp1ToRemoveCnt = sum_bint_array(toRemoveSp1Ids)
    cdef unsigned long sp2ToRemoveCnt = sum_bint_array(toRemoveSp2Ids)

    # Number of new orthologs that wil be added to the G cluster
    cdef unsigned long sp1ToAddCnt = sp1OrthoCnt - sum_bint_array(aSp1ContainedIdxs) - sp1ToRemoveCnt
    cdef unsigned long sp2ToAddCnt = sp2OrthoCnt - sum_bint_array(aSp2ContainedIdxs) - sp2ToRemoveCnt
    # print(f"To add cnts Sp1/Sp2:\t{sp1ToAddCnt}\t{sp2ToAddCnt}")

    # HACK: reject only if there is nothing new to add on both sides (sp1 and sp2)
    # This would allow us to new orthologs even if only in one of subcluster of the G cluster
    # if (sp1ToRemoveCnt == sp1OrthoCnt) or (sp2ToRemoveCnt == sp2OrthoCnt):
    if (sp1ToAddCnt == 0) and (sp2ToAddCnt == 0):
        # print(f"Promoted to ignored cluster")
        # print(f"Sp1 Cnts:\t{sp1ToRemoveCnt}\t{sp1ToAddCnt}\t{sp1OrthoCnt}")
        # print(f"Sp2 Cnts:\t{sp2ToRemoveCnt}\t{sp2ToAddCnt}\t{sp2OrthoCnt}")
        # ignoreClstr = 1
        clusterModOutcome = (0, gClstrId)
        return clusterModOutcome

    # Vectors used for the modified G clusters
    cdef cnp.ndarray[cnp.uint32_t, ndim=1] newGSp1Ids
    cdef cnp.ndarray[cnp.uint32_t, ndim=1] newGSp2Ids
    cdef cnp.ndarray[cnp.float32_t, ndim=1] newGSp1Scores
    cdef cnp.ndarray[cnp.float32_t, ndim=1] newGSp2Scores
    cdef unsigned long newGSp1OrthoCnt = 0
    cdef unsigned long newGSp2OrthoCnt = 0
    cdef unsigned long tmpGorthoCnt = 0

    # Tmp views to store the original vectors of the G cluster
    cdef cnp.uint32_t[:] oldGSpxIds
    cdef cnp.float32_t[:] oldGSpxScores
    # To remember at what index to write
    cdef unsigned long wtPosition

    # Identify the orthologs that should be added and modify the G cluster
    cdef cnp.ndarray[cnp.uint8_t, ndim=1] aSpxDoNotAdd = aSp1ContainedIdxs + toRemoveSp1Ids
    # Extract information from the G cluster
    # print(f"G cluster ID:\t{gClstrId}")
    tmpMclstr: MergedClstr = mClstrDict[gClstrId]
    # print(tmpMclstr)

    # NOTE: at present we are adding even to a single side of G
    # for example, if all orhtologs from aSp1 are rejected
    # but some of those from aSp2 are OK, those from aSp2 will be added to G
    # Create the new vectors for Sp1
    # print(f"\nDo not add to Sp1:\t{aSpxDoNotAdd}")

    # Create the new vectors for Sp1
    if sp1ToAddCnt > 0:
        # initialize write idx
        wtPosition = 0
        # Extract the old vectors
        oldGSpxIds = getattr(tmpMclstr, "sp1Ids")
        oldGSpxScores = getattr(tmpMclstr, "sp1Scores")
        # Set the new size
        tmpGorthoCnt = oldGSpxIds.shape[0]
        newGSp1OrthoCnt = tmpGorthoCnt + sp1ToAddCnt
        # initiliaze the new vectors
        newGSp1Ids = np.zeros(newGSp1OrthoCnt, dtype=np.uint32)
        newGSp1Scores = np.zeros(newGSp1OrthoCnt, dtype=np.float32)
        # Fill the new vectors with the original values
        for i in range(tmpGorthoCnt):
            newGSp1Ids[i] = oldGSpxIds[i]
            newGSp1Scores[i] = oldGSpxScores[i]
        # print("New G arrays update I Sp1:")
        # print(np.asarray(newGSp1Ids))
        # print(np.asarray(newGSp1Scores))
        # Add the new orthologs from A
        # based on the content of aSpxDoNotAdd
        for i in range(sp1OrthoCnt):
            if aSpxDoNotAdd[i] == 0:
                # print(f"Add {aSp1IdsView[i]} to Sp1 in G")
                newGSp1Ids[tmpGorthoCnt + wtPosition] = aSp1IdsView[i]
                newGSp1Scores[tmpGorthoCnt + wtPosition] = aSp1Scores[i]
                wtPosition += 1
        # print("New G arrays update II Sp1:")
        # print(np.asarray(newGSp1Ids))
        # print(np.asarray(newGSp1Scores))

    # Initiliaze the new arrays for Sp2
    aSpxDoNotAdd = aSp2ContainedIdxs + toRemoveSp2Ids
    # print(f"Do not add to Sp2:\t{aSpxDoNotAdd}")

    # Create the new vectors for Sp2
    if sp2ToAddCnt > 0:
        # initialize write idx
        wtPosition = 0
        # Extract the old vectors
        oldGSpxIds = getattr(tmpMclstr, "sp2Ids")
        oldGSpxScores = getattr(tmpMclstr, "sp2Scores")
        # Set the new size
        tmpGorthoCnt = oldGSpxIds.shape[0]
        newGSp2OrthoCnt = tmpGorthoCnt + sp2ToAddCnt
        # initiliaze the new vectors
        newGSp2Ids = np.zeros(newGSp2OrthoCnt, dtype=np.uint32)
        newGSp2Scores = np.zeros(newGSp2OrthoCnt, dtype=np.float32)
        # Fill the new vectors with the original values
        for i in range(tmpGorthoCnt):
            newGSp2Ids[i] = oldGSpxIds[i]
            newGSp2Scores[i] = oldGSpxScores[i]
        # print("New G arrays update I Sp2:")
        # print(np.asarray(newGSp2Ids))
        # print(np.asarray(newGSp2Scores))
        # Add the new orthologs from A
        # based on the content of aSpxDoNotAdd
        for i in range(sp2OrthoCnt):
            if aSpxDoNotAdd[i] == 0:
                # print(f"Add {aSp2IdsView[i]} to Sp2 in G")
                newGSp2Ids[tmpGorthoCnt + wtPosition] = aSp2IdsView[i]
                newGSp2Scores[tmpGorthoCnt + wtPosition] = aSp2Scores[i]
                wtPosition += 1
        # print("New G arrays update II Sp2:")
        # print(np.asarray(newGSp2Ids))
        # print(np.asarray(newGSp2Scores))

    # print(f"New sizes for G {gClstrId} sp1\\sp2 (UPDATED):\t{newGSp1OrthoCnt}\t{newGSp2OrthoCnt}")

    # If we at least a new ortholog for both species
    # then we substitute the old G cluster with a new one
    if (sp1ToAddCnt > 0) and (sp2ToAddCnt > 0):
        mClstrDict[gClstrId] = MergedClstr(newGSp1OrthoCnt + newGSp2OrthoCnt, newGSp1Ids, newGSp2Ids, newGSp1Scores, newGSp2Scores)
        # print(f"Updated G clstr [{gClstrId}] (all):\t{mClstrDict[gClstrId]}")
    # New orthologs added only to Sp1
    elif sp1ToAddCnt > 0:
        # Extract the ortholog count for Sp2 in G
        tmpGorthoCnt = getattr(tmpMclstr, "size") - tmpGorthoCnt
        mClstrDict[gClstrId] = MergedClstr(newGSp1OrthoCnt + tmpGorthoCnt, newGSp1Ids, getattr(tmpMclstr, "sp2Ids"), newGSp1Scores, getattr(tmpMclstr, "sp2Scores"))
        # print(f"Updated G clstr [{gClstrId}] (Sp1):\t{mClstrDict[gClstrId]}")
    elif sp2ToAddCnt > 0:
        # Extract the ortholog count for Sp1 in G
        tmpGorthoCnt = getattr(tmpMclstr, "size") - tmpGorthoCnt
        mClstrDict[gClstrId] = MergedClstr(newGSp2OrthoCnt + tmpGorthoCnt, getattr(tmpMclstr, "sp1Ids"), newGSp2Ids, getattr(tmpMclstr, "sp1Scores"), newGSp2Scores)
        # print(f"Updated G clstr [{gClstrId}] (Sp2):\t{mClstrDict[gClstrId]}")

    # Some of the new ortholog were rejected
    if (sp1ToRemoveCnt + sp2ToRemoveCnt) != 0:
        clusterModOutcome = (1, gClstrId)
        return clusterModOutcome
    # All new orthologs were added to G
    else:
        clusterModOutcome = (2, gClstrId)
        return clusterModOutcome
        # sys.exit("DEBUG")



# TODO: change the parameters so that objects are not passed
# HACK: when cython will support DataClasses as paramters in cdef functions
# reduce the number of paramaters and directly passing the DataClass objects (e.g., ArchClstr)
cdef (unsigned long, unsigned long) filter_and_add_new_arch_clstr(cnp.uint32_t[:] aSp1IdsView, cnp.uint32_t[:] aSp2IdsView, cnp.float32_t[:] aSp1Scores, cnp.float32_t[:] aSp2Scores, dict mClstrDict, dict archMasterDict, unsigned long sp1Id, unsigned long sp2Id, double covThr):
    """
    Given an arch-based cluster that is not in G, integrate it into G if conditions are met.
    """

    # print("filter_and_add_new_arch_clstr :: START")
    # Tmp variables
    cdef size_t i, j # Indexes to be used in for loops
    cdef unsigned long sp1OrthoCnt = aSp1IdsView.shape[0]
    cdef unsigned long sp2OrthoCnt = aSp2IdsView.shape[0]
    cdef unsigned long clstrSize = sp1OrthoCnt + sp2OrthoCnt
    cdef unsigned long newClstrId = len(mClstrDict) + 1
    # Says that the complete arch cluster should be ignored
    cdef bint ignoreClstr = 0
    cdef double sp1ArchCov
    cdef double sp2ArchCov
    cdef unsigned long sp1ArchDomCnt = 0
    cdef unsigned long sp2ArchDomCnt = 0
    # Tmp variables used to modify the input cluster
    cdef cnp.ndarray[cnp.uint8_t, ndim=1] toRemoveSp1Ids = np.zeros(0, dtype=np.uint8)
    cdef cnp.ndarray[cnp.uint8_t, ndim=1] toRemoveSp2Ids = np.zeros(0, dtype=np.uint8)

    tmpSp1Arch: Arch = Arch(0, 0.0, 0, 0, np.zeros(0, dtype=np.uint32), np.zeros(0, dtype=np.uint32), np.zeros(1, dtype=np.uint32), np.array(["sp1"], dtype=np.str_), np.zeros(0, dtype=np.float32), 1)
    tmpSp2Arch: Arch = Arch(0, 0.0, 0, 0, np.zeros(0, dtype=np.uint32), np.zeros(0, dtype=np.uint32), np.zeros(0, dtype=np.uint32), np.array(["sp2"], dtype=np.str_), np.zeros(0, dtype=np.float32), 1)

    # Only the coverages and domain counts must be compared
    if clstrSize == 2:
        # print("\nNew (PAIR) cluster!")
        tmpSp1Arch = archMasterDict[sp1Id][aSp1IdsView[0]]
        tmpSp2Arch = archMasterDict[sp2Id][aSp2IdsView[0]]
        sp1ArchCov = getattr(tmpSp1Arch, "coverage")
        sp2ArchCov = getattr(tmpSp2Arch, "coverage")

        # Reject  the pair if the coverage is lower than 75%
        if (sp1ArchCov < covThr) or (sp2ArchCov < covThr):
            # print("Reject pair:\tlow coverage")
            # print(f"{sp1Id}.{aSp1IdsView[0]}\t{sp2Id}.{aSp2IdsView[0]}")
            # ignoreClstr = 1
            return (0, newClstrId)
        # Remove if the domain count is different
        elif getattr(tmpSp1Arch, "domCnt") != getattr(tmpSp2Arch, "domCnt"): # Check the domain count
            # print("Reject pair:\tdomain count mismatch")
            # print(f"{sp1Id}.{aSp1IdsView[0]}\t{sp2Id}.{aSp2IdsView[0]}")
            # ignoreClstr = 1
            return (0, newClstrId)
    # We can use extra conditions
    else:
        # print("\nNew (MULTI) cluster!")
        # Iniziliaze the arrays to keep track
        # of what should be removed
        toRemoveSp1Ids = np.zeros(sp1OrthoCnt, dtype=np.uint8)
        toRemoveSp2Ids = np.zeros(sp2OrthoCnt, dtype=np.uint8)
        for i in range(sp1OrthoCnt):
            if ignoreClstr == 1:
                break
            # Skip if already flagged as removable
            if toRemoveSp1Ids[i] == 1:
                continue
            # print(aSp1IdsView[i])
            tmpSp1Arch = archMasterDict[sp1Id][aSp1IdsView[i]]
            sp1ArchCov = getattr(tmpSp1Arch, "coverage")
            sp1ArchDomCnt = getattr(tmpSp1Arch, "domCnt")

            if sp1ArchCov < covThr:
                # print(f"Reject ortho Sp1:\tlow coverage\t{sp1ArchCov}")
                # print(getattr(tmpSp1Arch, "phrase"))
                toRemoveSp1Ids[i] = 1
                continue

            for j in range(sp2OrthoCnt):
                if toRemoveSp2Ids[j] == 1:
                    continue # No need to check again
                # print(aSp2IdsView[j])
                tmpSp2Arch = archMasterDict[sp2Id][aSp2IdsView[j]]
                sp2ArchCov = getattr(tmpSp2Arch, "coverage")
                sp2ArchDomCnt = getattr(tmpSp2Arch, "domCnt")

                # NOTE: we reject the whole cluster
                # even if we found a single domain count mismatch
                # this is probably too strict
                # Check the domain counts
                if sp1ArchDomCnt != sp2ArchDomCnt:
                    # print("Domain count mismatch in cluster!")
                    # print(getattr(tmpSp1Arch, "phrase"))
                    # print(getattr(tmpSp2Arch, "phrase"))
                    ignoreClstr = 1
                    break

                if sp2ArchCov < covThr:
                    # print(f"Reject ortho Sp2:\tlow coverage\t{sp2ArchCov}")
                    # print(getattr(tmpSp2Arch, "phrase"))
                    toRemoveSp2Ids[j] = 1

    # print("Orthologs that will be removed:")
    # print(toRemoveSp1Ids)
    # print(toRemoveSp2Ids)

    # Variables used to create a modified version of the Arch cluster
    # to be added to a graph based cluster
    cdef cnp.ndarray[cnp.uint32_t, ndim=1] newSp1Ids
    cdef cnp.ndarray[cnp.uint32_t, ndim=1] newSp2Ids
    cdef cnp.ndarray[cnp.float32_t, ndim=1] newSp1Scores
    cdef cnp.ndarray[cnp.float32_t, ndim=1] newSp2Scores
    cdef unsigned long sp1ToRemoveCnt = sum_bint_array(toRemoveSp1Ids)
    cdef unsigned long sp2ToRemoveCnt = sum_bint_array(toRemoveSp2Ids)
    cdef unsigned long orthoToRemoveCnt = sp1ToRemoveCnt + sp2ToRemoveCnt

    cdef cnp.ndarray[cnp.float32_t, ndim=1] tmpScArray
    # To remember at what index to write
    cdef unsigned long wtPosition = 0

    # print(f"Orthologs that will be removed Sp1/Sp2/To remove cnt:\t{sp1ToRemoveCnt}\t{sp2ToRemoveCnt}\t{orthoToRemoveCnt}")

    if (sp1ToRemoveCnt == sp1OrthoCnt) or (sp2ToRemoveCnt == sp2OrthoCnt):
        # print(f"Promoted to ignored cluster")
        ignoreClstr = 1

    # print(f"ignoreClstr/newClstrId:\t{ignoreClstr}\t{newClstrId}")

    # return an interger describing the state of the cluster
    # 0 -> reject
    if ignoreClstr:
        return (0, newClstrId)
    # 1 -> add with modifications (remove only some orthologs)
    elif (orthoToRemoveCnt) != 0:
        # Reuse the cluster size variable
        clstrSize = clstrSize - orthoToRemoveCnt
        # Extract the IDs for Sp1
        if sp1ToRemoveCnt > 0:
            # initialize the new arrays for Ids and scores
            newSp1Ids = np.zeros(sp1OrthoCnt - sp1ToRemoveCnt, dtype=np.uint32)
            newSp1Scores = np.zeros(sp1OrthoCnt - sp1ToRemoveCnt, dtype=np.float32)
            for i in range(sp1OrthoCnt):
                if toRemoveSp1Ids[i] == 0:
                    # print(f"sp1 keep:\t{aSp1IdsView[i]}")
                    newSp1Ids[wtPosition] = aSp1IdsView[i]
                    newSp1Scores[wtPosition] = aSp1Scores[i]
                    wtPosition += 1

            wtPosition = 0
        # Keep the original ids
        else:
            newSp1Ids = np.asarray(aSp1IdsView)
            newSp1Scores = np.asarray(aSp1Scores)

        # Extract the IDs for Sp2
        if sp2ToRemoveCnt > 0:
            newSp2Ids = np.zeros(sp2OrthoCnt - sp2ToRemoveCnt, dtype=np.uint32)
            newSp2Scores = np.zeros(sp2OrthoCnt - sp2ToRemoveCnt, dtype=np.float32)
            for i in range(sp2OrthoCnt):
                if toRemoveSp2Ids[i] == 0:
                    # print(f"sp2 keep:\t{aSp2IdsView[i]}")
                    newSp2Ids[wtPosition] = aSp2IdsView[i]
                    newSp2Scores[wtPosition] = aSp2Scores[i]
                    wtPosition += 1

        # Keep the original ids
        else:
            newSp2Ids = np.asarray(aSp2IdsView)
            newSp2Scores = np.asarray(aSp2Scores)

        # Make sure it would not overwrite other clusters
        if newClstrId in mClstrDict:
            sys.exit(f"The cluster ID {newClstrId} already exists in the Master Cluster dictionary.")

        # Add the new cluster
        mClstrDict[newClstrId] = MergedClstr(clstrSize, newSp1Ids, newSp2Ids, newSp1Scores, newSp2Scores)
        # print(f"New (modified) Graph-cluster [ID: {newClstrId}]:\n{mClstrDict[newClstrId]}")
        return (1, newClstrId)
    # 2 -> Add the ortholog without any modifications
    else:
        # Make sure it would not overwrite other clusters
        if newClstrId in mClstrDict:
            sys.exit(f"The cluster ID {newClstrId} already exists in the Master Cluster dictionary.")
        # Add the new cluster
        mClstrDict[newClstrId] = MergedClstr(clstrSize, np.asarray(aSp1IdsView), np.asarray(aSp2IdsView), np.asarray(aSp1Scores), np.asarray(aSp2Scores))
        # print(f"New Graph-cluster [ID: {newClstrId}]:\n{mClstrDict[newClstrId]}")
        return (2, newClstrId)



# @cython.boundscheck(False) # Check array bounds
# @cython.profile(False)
# def load_arch_ortho_pckl(pcklPath:str) -> dict[int, ArchClstr]:
cdef inline dict load_arch_ortho_pckl(str pcklPath):
    """
        Load arch-based pickle with ortholog clusters onto multiple data structures.
    """

    # Example of line with arch-based clusters
    # 0.68,0.74 23.4368 33.14856 33.17428
    # 0.69 23.4363 33.12080

    '''
    cdef bint debug = 1
    debugStr: str = f"""load_arch_orto_pckl :: START
    pcklPath:\t{pcklPath}"""
    logger.debug(debugStr)
    '''

    # Tmp vars
    cdef unsigned long clstrId = 0
    cdef unsigned long tmpOrthoId
    cdef size_t i, j # Indexes to be used in for loops
    # Dictionary associating repeated orhtologs to the cluster IDs
    sp1Rep2Clstr: dict[int, list[int]] = {}
    # sp2Rep2Clstr: dict[int, list[int]] = {}
    # Associate a ArchClstr object to each cluster ID
    # arch clusters dictionaries
    # stored in pckl have the following tuples as values
    # 0 -> sp1 ortho IDs (6, 1817, 20270) as tuple[int]
    # 1 -> sp2 ortho IDs (11432, 15532) as tuple[int]
    # 2 -> list[] cosine values between the orthologs 
    # [[0.715364, 0.7919177], [0.715364, 0.7919177], [0.715364, 0.7919177]]
    aClstrDict: dict[int, ArchClstr] = load(open(pcklPath, "rb"))
    cdef unsigned long clstrCnt = len(aClstrDict)
    # print(f"Loaded arch clusters (including does with repetitions):\t{clstrCnt}")

    tmpArchClstr: ArchClstr = ArchClstr(0, np.zeros(0, dtype=np.uint32), np.zeros(0, dtype=np.uint32), [])
    cdef cnp.uint32_t[:] sp1Ids
    cdef unsigned long grpLenSp1
    # cdef cnp.uint32_t[:] sp2Ids

    # Go through the ortholog cluster to identify repetitions
    # print("\nGo through the arch clusted and identify repeated orthologs.")
    for i in range(clstrCnt):
        clstrId += 1
        # print(f"\ni/Clstr ID:{i}\t{clstrId}")
        tmpArchClstr = aClstrDict[clstrId]
        # print(f"type(spIds):\t{type(spIds)}")
        sp1Ids = getattr(tmpArchClstr, "sp1Ids")
        grpLenSp1 = sp1Ids.shape[0]
        # Insert the orto ids into the dictionary
        # sp2Ids = getattr(tmpArchClstr, "sp2Ids")
        # grpLenSp2 = sp2Ids.shape[0]
        # Increment the main counters
        # clstrSize = grpLenSp1 + grpLenSp2
        # pairsCnt += grpLenSp1 * grpLenSp2
        # sp1OrthoCnt += grpLenSp1
        # sp2OrthoCnt += grpLenSp2
        # Extract the scores

        # Fill dictionaries with repeated orthologs
        # print(f"grpLenSp1:\t{grpLenSp1}")
        for j in range(grpLenSp1):
            # tmpOrthoId = ortoListSp1.pop()
            tmpOrthoId = sp1Ids[j]
            # print(f"Sp1 Ids (position/ID):\t{j}\t{tmpOrthoId}")
            if tmpOrthoId not in sp1Rep2Clstr:
                sp1Rep2Clstr[tmpOrthoId] = [clstrId]
            else:
                sp1Rep2Clstr[tmpOrthoId].append(clstrId)
                # print(f"Repetition found in cluster {clstrId}:\t{tmpOrthoId}")

        ''' FIXME: This should never happend
        # TODO: there should be no repetitions for the Sp2
        # because of the way in which we create the clusters
        # Remove it no repeations appear in a complete run
        # Now for Sp2
        for j in range(grpLenSp2):
            tmpOrthoId = sp2Ids[j]
            if tmpOrthoId not in sp2Rep2Clstr:
                sp2Rep2Clstr[tmpOrthoId] = [clstrId]
            else:
                sp2Rep2Clstr[tmpOrthoId].append(clstrId)
        '''

    # Filter the dictionary for sp1 to contain only repeated ortholog
    # ortoListSp1: list[int] = []
    # print(f"\nRepeated arch orthologs:\t{len(sp1Rep2Clstr)}")
    cdef list ortoListSp1 = list(sp1Rep2Clstr.keys())
    cdef unsigned long loopLimit = len(ortoListSp1)

    # print(f"sp1Rep2Clstr (all):\t{len(sp1Rep2Clstr)}")

    # Filter the first dictionary to contain only
    # orthologs which are repeated in clusters
    for i in range(loopLimit):
        tmpProtId = ortoListSp1.pop()
        # print(f"tmpProtId:\t{tmpProtId}")
        # Print the repeated ortholog
        # Remove from the dictionary if not repeated
        if len(sp1Rep2Clstr[tmpProtId]) == 1:
            del sp1Rep2Clstr[tmpProtId]

    # NOTE: the above could have been done with the one-liner below
    # sp1Rep2Clstr = {key:sp1Rep2Clstr[key] for key in ortoListSp1 if len(sp1Rep2Clstr[key]) == 1}

    # print(f"\nRepeated orthologs before pruning:\t{len(sp1Rep2Clstr)}")
    aClstrDict = remove_repeaded_arch_orthologs(aClstrDict, sp1Rep2Clstr)
    # print(f"sp1Rep2Clstr (repeated only):\t{len(sp1Rep2Clstr)}")
    # print(f"Pruned clusters:\t{len(aClstrDict)}")

    '''
    if debug:
        print(f"""Arch-based orthologs loaded:
        Clusters:\t{clstrId}
        Clusters (after pruning):\t{len(aClstrDict)}""")
    '''

    # return dictionary that associates repeated ortolog proteins with the cluster IDs they appear in
    return aClstrDict


# NOTE: the below function is used for debugging
'''
# @cython.boundscheck(False) # Check array bounds
# @cython.profile(False)
# def load_arch_orto_tbl(tblPath:str) -> dict[int, ArchClstr]:
cdef dict load_arch_orto_tbl(str tblPath):
    """
        Load arch-based ortholog clusters onto multiple data structures.
    """

    # Example of line with arch-based clusters
    # 0.68,0.74 23.4368 33.14856 33.17428
    # 0.69 23.4363 33.12080

    cdef bint debug = 0
    debugStr: str = f"""load_arch_orto_tbl :: START
    tblPath:\t{tblPath}"""
    logger.debug(debugStr)

    # Tmp vars
    cdef unsigned int clstrId = 0
    # cdef unsigned int pairsCnt = 0
    cdef unsigned int sp1OrthoCnt = 0
    cdef unsigned int sp2OrthoCnt = 0
    cdef unsigned int one2oneCnt = 0
    cdef unsigned int tmpOrthoId
    cdef size_t i # Indexes to be used in for loops
    cdef unsigned int grpLenSp1, grpLenSp2, clstrSize
    # temporary list for ortholog IDs
    ortoListSp1: list[int] = []
    ortoListSp2: list[int] = []
    # Associate a ArchClstr object to each cluster ID
    aClstrDict: dict[int, ArchClstr] = {}
    # Dictionary associating repeated orhtologs to the cluster IDs
    sp1Rep2Clstr: dict[int, list[int]] = {}
    sp2Rep2Clstr: dict[int, list[int]] = {}
    # Used in splits
    flds: list[bytes] = []
    # Will contain the arrays of doubles
    # with the cosine similarities
    scoreArrays: list[np.array] = []

    # define file names and file descriptor pointer in C
    cdef bytes filename_byte_string = tblPath.encode("UTF-8")
    cdef char* tblPath_c = filename_byte_string
    #file pointer
    cdef FILE* cfile
    # varibales for files and lines
    cdef char * line = NULL
    cdef size_t l = 0
    cdef ssize_t read

    #open the pairwise ortholog table
    cfile = fopen(tblPath_c, "rb")
    if cfile == NULL:
        raise FileNotFoundError(2, f"No such file or directory: {tblPath_c}")

    # Create ArchClstr objects
    while True:
        read = getline(&line, &l, cfile)
        if read == -1:
            break

        # split the binary stream
        flds = line.split(b"\t", 3)
        clstrId += 1
        ortoListSp1 = process_arch_ortho_subgroup(subgrp=flds[1])
        grpLenSp1 = len(ortoListSp1)
        # Insert the orto ids into the dictionary
        ortoListSp2 = process_arch_ortho_subgroup(subgrp=flds[2])
        grpLenSp2 = len(ortoListSp2)

        # Increment the main counters
        clstrSize = grpLenSp1 + grpLenSp2
        # pairsCnt += grpLenSp1 * grpLenSp2
        sp1OrthoCnt += grpLenSp1
        sp2OrthoCnt += grpLenSp2

        # Extract the scores
        scoreArrays = extract_arch_clstr_cosine_vals(flds[0], grpLenSp1, grpLenSp2)

        if clstrSize == 2:
            one2oneCnt += 1

        # create ArchClstr objects
        aClstrDict[clstrId] = ArchClstr(clstrSize, np.array(ortoListSp1, dtype=np.uint32), np.array(ortoListSp2, dtype=np.uint32), scoreArrays)

        # Fill dictionaries with repeated orthologs
        for i in range(grpLenSp1):
            tmpOrthoId = ortoListSp1.pop()
            if tmpOrthoId not in sp1Rep2Clstr:
                sp1Rep2Clstr[tmpOrthoId] = [clstrId]
            else:
                sp1Rep2Clstr[tmpOrthoId].append(clstrId)

        # TODO: there should be no repetitions for the Sp2
        # because of the way in which we create the clusters
        # Remove it no repeations appear in a complete run
        # Now for Sp2
        for i in range(grpLenSp2):
            tmpOrthoId = ortoListSp2.pop()
            if tmpOrthoId not in sp2Rep2Clstr:
                sp2Rep2Clstr[tmpOrthoId] = [clstrId]
            else:
                sp2Rep2Clstr[tmpOrthoId].append(clstrId)

        # if clstrId == 2:
        #     break

    #close input file
    fclose(cfile)

    # Filter the dictionary for sp1 to contain only repeated ortholog
    ortoListSp1 = list(sp1Rep2Clstr.keys())
    cdef unsigned int loopLimit = len(ortoListSp1)
    tmpIdList: list[int] = []

    # Filter the first dictionary to contain only
    # orthologs which are repeated in clusters
    for i in range(loopLimit):
        tmpProtId = ortoListSp1.pop()
        # Print the repeated ortholog
        # print(f"Repeated ortholog:\t{sp1Rep2Clstr[tmpProtId]}")
        tmpIdList = sp1Rep2Clstr[tmpProtId]
        # Remove from the dictionary if not repeated
        if len(tmpIdList) == 1:
            del sp1Rep2Clstr[tmpProtId]

    # NOTE: the above could have been done with the one-liner below
    # sp1Rep2Clstr = {key:sp1Rep2Clstr[key] for key in ortoListSp1 if len(sp1Rep2Clstr[key]) > 1}

    if debug:
        print(f"""Arch-based orthologs loaded:
        Clusters:\t{clstrId}
        1-to-1 relations:\t{one2oneCnt}
        Pairs:\t{pairsCnt}
        Ortho sp1:\t{sp1OrthoCnt}
        Ortho sp2:\t{sp2OrthoCnt}""")

    aClstrDict = remove_repeaded_arch_orthologs(aClstrDict, sp1Rep2Clstr)

    # return dictionary that associates repeated ortolog proteins with the cluster IDs they appear in
    return aClstrDict
'''


# @cython.profile(False)
@cython.boundscheck(False) # Check array bounds
# def load_graph_orto_tbl(tblPath:str) -> tuple[dict[int, MergedClstr], dict[int, tuple[int, float]], dict[int, tuple[int, float]]]:
cdef inline object load_graph_orto_tbl(str tblPath):
    """
        Load graph-based ortholog clusters onto multiple data structures.
    """

    # Example of line with raw arch information
    # OrtoId Score OrtoA OrtoB
    # 1 740 22.775 1.0 33.5301 1.0 33.5499 0.105
    # 2 717 22.857 1.0 33.5870 1.0

    '''
    cdef bint debug = 0
    debugStr: str = f"""load_graph_orto_tbl :: START
    tblPath:\t{tblPath}"""
    logger.debug(debugStr)
    '''

    # Tmp vars
    cdef unsigned long clstrId = 0
    cdef unsigned long pairsCnt = 0
    cdef unsigned long tmpProtId
    cdef size_t i # Indexes to be used in for loops
    cdef unsigned long gGrpLenSp1, gGrpLenSp2, gClstrSize
    # Associate a tuple with cluster ID and score to each graph-based ortholog
    ortho2infoSp1: dict[int, tuple(int, float)] = {}
    ortho2infoSp2: dict[int, tuple(int, float)] = {}

    # temporary list for ortholog IDs
    orthoListSp1: list[int] = []
    orthoListSp2: list[int] = []
    # temporary list for ortholog scores
    orthoScoresSp1: list[float] = []
    orthoScoresSp2: list[float] = []
    # Counter for 1-to-1 ortholog relations
    cdef unsigned long one2oneCnt = 0

    # Associate a MergedClstr object to each cluster ID
    mClstrDict: dict[int, MergedClstr] = {}
    flds: list[bytes] = []

    # define file names and file descriptor pointer in C
    cdef bytes filename_byte_string = tblPath.encode("UTF-8")
    cdef char* tblPath_c = filename_byte_string
    #file pointer
    cdef FILE* cfile
    # varibales for files and lines
    cdef char * line = NULL
    cdef size_t l = 0
    cdef ssize_t read

    #open the pairwise ortholog table
    cfile = fopen(tblPath_c, "rb")
    if cfile == NULL:
        raise FileNotFoundError(2, f"No such file or directory: {tblPath_c}")

    while True:
        read = getline(&line, &l, cfile)
        if read == -1:
            break

        # split the binary stream
        flds = line.split(b"\t", 3)
        # if the first letter is a 'O' then it is the cluster headers
        if flds[0].decode()[0] == 'O':
          # skip header
          continue

        clstrId += 1

        orthoListSp1, orthoScoresSp1 = process_graph_ortho_subgroup(subgrp=flds[2])
        orthoListSp2, orthoScoresSp2 = process_graph_ortho_subgroup(subgrp=flds[3])

        # print(f"ClusterID\OrthoSp1->ScoresSp1\OrthoSp2->ScoresSp2:{clstrId}\t{orthoListSp1}: {orthoScoresSp1}\t{orthoListSp2}: {orthoScoresSp2}")
        # print(f"Orthologs and scores for cluster {clstrId}:{ortho2scSp1}\t{ortho2scSp2}")

        gGrpLenSp1 = len(orthoListSp1)
        gGrpLenSp2 = len(orthoListSp2)
        gClstrSize = gGrpLenSp1 + gGrpLenSp2
        pairsCnt += gGrpLenSp1 * gGrpLenSp2

        # Create merged cluster object and add it to a dictionary
        mClstrDict[clstrId] = MergedClstr(gClstrSize, np.array(orthoListSp1, dtype=np.uint32), np.array(orthoListSp2, dtype=np.uint32), np.array(orthoScoresSp1, dtype=np.float32), np.array(orthoScoresSp2, dtype=np.float32))

        if gClstrSize == 2:
            one2oneCnt += 1

        # Add the gene and link it to a cluster
        for i in range(gGrpLenSp1):
            tmpProtId = orthoListSp1.pop()
            # if tmpProtId in ortho2infoSp1:
            #     logging.error(f"{tmpProtId} (from sp1) appears 2 times in the graph-ortholog table file")
            #     sys.exit(-5)
            ortho2infoSp1[tmpProtId] = (clstrId, orthoScoresSp1.pop())

        for i in range(gGrpLenSp2):
            tmpProtId = orthoListSp2.pop()
            # if tmpProtId in ortho2infoSp2:
            #     logging.error(f"{tmpProtId} (from sp2) appears 2 times in the graph-ortholog table file")
            #     sys.exit(-5)
            ortho2infoSp2[tmpProtId] = (clstrId, orthoScoresSp2.pop())

    #close input file
    fclose(cfile)

    '''
    if debug:
        print(f"""Graph-based orthologs loaded:
        Clusters:\t{clstrId}
        1-to-1 relations:\t{one2oneCnt}
        Pairs:\t{pairsCnt}
        Ortho sp1:\t{len(ortho2infoSp1)}
        Ortho sp2:\t{len(ortho2infoSp2)}""")
    '''

    # Return the datastructures with clusters info
    return(mClstrDict, ortho2infoSp1, ortho2infoSp2)


# def integrate_arch_ortho_into_gclstr(aClstrDict: dict[int, ArchClstr], mClstrDict: dict[int, MergedClstr], graphSp1Ortho2info: dict[int, tuple(int, float)], graphSp2Ortho2info: dict[int, tuple(int, float)], sp1Id: int, sp2Id: int, archMasterDict: dict[int, dict[int, Arch]]) -> tuple[int, int, int, int, int, int, int, int]:
cdef (unsigned long, unsigned long, unsigned long, unsigned long, unsigned long, unsigned long, unsigned long, unsigned long) integrate_arch_ortho_into_gclstr(dict aClstrDict, dict mClstrDict, dict graphSp1Ortho2info, dict graphSp2Ortho2info, unsigned long sp1Id,  unsigned long sp2Id, dict archMasterDict, double covThr):
    """
        Add arch-based ortholog pairs to graph based ones.

        This function might also split graph-based clusters if conditions are met.
    """

    '''
    cdef bint debug = 0
    debugStr: str = f"""integrate_arch_ortho_into_gclstr :: START
    Arch-based clusters:\t{len(aClstrDict)}
    Graph-based clusters:\t{len(mClstrDict)}
    Graph orthologs from Sp1:\t{len(graphSp1Ortho2info)}
    Graph orthologs from Sp2:\t{len(graphSp2Ortho2info)}
    Sp1 ID:\t{sp1Id}
    Sp2 ID:\t{sp2Id}
    Coverage threshold:\t{covThr}"""
    logger.debug(debugStr)
    '''

    # Arch based clusters have the following content
     # size=3 -> int
     # sp1Ids = array([4368], dtype=uint32)
     # sp2Ids = array([14856, 17428], dtype=uint32)
     # cosineValues=[array([0.68, 0.74], dtype=float32)])

    # Tmp variables
    cdef size_t i # Indexes to be used in for loops
    # Variables to store info on arch-based clusters
    cdef unsigned long aClstrSize = 0
    cdef unsigned long aClstrId = 0
    cdef unsigned long aClstrCnt = len(aClstrDict)
    cdef unsigned long mClstrCnt = len(mClstrDict)
    # Minimum coverage for a Arch to be kept
    # cdef double covThr = 0.75

    # The membership dictionary contains one tuple for each of the 2 species
    # 0 -> represents sp1, and the tuple represents the membership and the indexes contained in G
    # 1 -> represents sp2
    cdef dict membershipDict = {} # dict[tuple[int, ndarray]]

    # memory views for temporary vectors with scores and ids
    cdef cnp.uint32_t[:] aSp1IdsView
    cdef cnp.uint32_t[:] aSp2IdsView
    # tmp arch-based cluster
    tmpAclstr: ArchClstr = ArchClstr(0, np.zeros(0, dtype=np.uint32), np.zeros(0, dtype=np.uint32), [])

    # Variables to store info on graph-based clusters
    cdef cnp.ndarray[cnp.uint32_t, ndim=1] gSp1Orthologs = np.array(list(graphSp1Ortho2info.keys()), dtype=np.uint32)
    cdef cnp.ndarray[cnp.uint32_t, ndim=1] gSp2Orthologs = np.array(list(graphSp2Ortho2info.keys()), dtype=np.uint32)
    cdef unsigned long gSp1OrthoCnt = gSp1Orthologs.shape[0]
    cdef unsigned long gSp2OrthoCnt = gSp2Orthologs.shape[0]
    # This contains the result from functions that add or modify clusters
    # The first field indicates the type of modification (check each function for details)
    # The second field is the cluster ID, which could be different
    # from that passed to each modification function
    cdef (unsigned long, unsigned long) clusterModOutcome = (0, 0)

    # HACK: this is hardcoded and should be fixed
    # FIXME: The graph-based predictions might generate inparalogs happearing in multiple clusters
    # This should be fixed in future versions.
    # The issue is described in:
    # https://gitlab.com/salvo981/sonicparanoid2/-/issues/43
    '''
    cdef str sp1Str = str(sp1Id)
    cdef str sp2Str = str(sp2Id)
    outFile: str = "/home/salvocos/Desktop/sonicparanoid-arch-analysis/test-directory/graph-arch-orto-merging/test-output-pairs-graph"
    outFile = os.path.join(outFile, f"{sp1Id}-{sp2Id}.merged.ortho.pairs.tsv")
    write_pairs_to_file(mClstrDict, outFile, sp1Str, sp2Str, 1)
    '''

    ''' DEBUG ONLY
    '''
    # Counters for cases:
    # Case I: Completely new clusters (not in G)
    cdef unsigned long newAddedClstrsCnt = 0
    # Case II: Completely contained in G
    cdef unsigned long completelyContainedClstrsCnt = 0
    # Cases I and II mixed:
    #  one part of the cluster is completely new while the other is in G
    cdef unsigned long newAndOldClstrsCnt = 0

    # DEBUG ONLY
    cdef unsigned long addNewCnt = 0
    cdef unsigned long addNewModCnt = 0
    cdef unsigned long rejectNewCnt = 0
    # Case I: (1, 1)
    cdef unsigned long rejectContainedCnt = 0
    # Cases I and II: (1, 0); (0, 1)
    cdef unsigned long addNewAndOldCnt = 0
    cdef unsigned long rejectNewAndOldCnt = 0
    # Cases I and II and III mixed: (2, 2), (1, 2), (2, 1), (0, 2), (2, 0)
    cdef unsigned long mixedClstrsCnt = 0
    cdef unsigned long addMixedCnt = 0
    cdef unsigned long addMixedModCnt = 0
    cdef unsigned long addMixedModAllNewCnt = 0 # modification resulted in clstr of all new orthologs
    cdef unsigned long rejectMixedCnt = 0

    for i in range(aClstrCnt):
        aClstrId = i + 1
        tmpAclstr = aClstrDict[aClstrId]
        aClstrSize = getattr(tmpAclstr, "size")
        aSp1IdsView = getattr(tmpAclstr, "sp1Ids")
        aSp2IdsView = getattr(tmpAclstr, "sp2Ids")
        cosineValsList = getattr(tmpAclstr, "cosineValues")
        membershipDict = check_arch_cluster_membership(aSp1IdsView, aSp2IdsView, gSp1Orthologs, gSp2Orthologs)
        # print(f"Membership type:\t{membershipDict[0][0]}\t{membershipDict[1][0]}")

        # Based on the memebership different functions should be used
        # The problem is divided into 3 macro-cases handled by separate functions
        # (0, 0): Orthologs are all new and could be added to G
        if membershipDict[0][0] + membershipDict[1][0] == 0:
            # print("All arch-orthologs are new and not in G!")
            # print(f"Membership type:\t{membershipDict[0][0]}\t{membershipDict[1][0]}")
            newAddedClstrsCnt += 1
            # print(f"ID\Size\sp1\sp2:\t{aClstrId}\t{aClstrSize}\t{sp1Id}\t{sp2Id}")
            # print(f"aSp1IdView:\t{np.asarray(aSp1IdsView)}")
            # print(f"aSp2IdView:\t{np.asarray(aSp2IdsView)}")

            # HACK: needs to be updated so that objects are not passed
            clusterModOutcome = integrate_new_arch_clstr(aClstrId, aClstrSize, aClstrDict, aSp1IdsView, aSp2IdsView, cosineValsList, mClstrDict, archMasterDict, sp1Id, sp2Id, covThr)

            if clusterModOutcome[0] == 0:
                rejectNewCnt += 1
            elif clusterModOutcome[0] == 1:
                addNewModCnt += 1
            elif clusterModOutcome[0] == 2:
                # print(clusterModOutcome)
                addNewCnt += 1
            # sys.exit("DEBUG: ortho_merger.py :: integrate_arch_ortho_into_gclstr :: case (0, 0)")

        # All arch-based orthologs from sp1 and from sp2 are already contained in G
        # Note that orthologs from A might be in separate clusters in G
        # (1, 1): in this case all the orhtologs are already contained in G
        elif (membershipDict[0][0] == 1) and (membershipDict[1][0] == 1):
            # print(f"Cluster ({i+1}) already contained in G")
            completelyContainedClstrsCnt += 1

            # HACK: needs to be updated so that objects are not passed
            clusterModOutcome = integrate_contained_arch_clstr(aClstrId, aClstrSize, aClstrDict, aSp1IdsView, aSp2IdsView, cosineValsList, archMasterDict, sp1Id, sp2Id, graphSp1Ortho2info, graphSp2Ortho2info)

            if clusterModOutcome[0] == 0:
                rejectContainedCnt += 1
            # sys.exit("DEBUG: ortho_merger.py :: integrate_arch_ortho_into_gclstr :: case (1, 1)")

        # Case in which orthologs from one species
        # are either completely new [aClstrMembership == 0]
        # or completely contained [aClstrMembership == 1] in G
        # This case handles the following possible combinations for aClstrMembership:
        # (0, 1): all members from sp1 are new, those from sp2 are contained in G
        # (1, 0): all members from sp1 are contained in G, those from sp2 are new
        elif (membershipDict[0][0] + membershipDict[1][0]) == 1:
            newAndOldClstrsCnt += 1
            # HACK: needs to be updated so that objects are not passed
            # print(f"Cluster memberships (sp1\sp2)(inSp1/inSp2):\t{membershipDict[0][0]}\t{membershipDict[1][0]}\t{membershipDict[0][1]}\t{membershipDict[1][1]}")
            clusterModOutcome = integrate_contained_and_new_arch_clstr(aClstrId, aClstrSize, aClstrDict, aSp1IdsView, aSp2IdsView, cosineValsList, mClstrDict, archMasterDict, sp1Id, sp2Id, graphSp1Ortho2info, graphSp2Ortho2info, membershipDict, covThr)

            if clusterModOutcome[0] == 0:
                rejectNewAndOldCnt += 1
            elif clusterModOutcome[0] == 1:
                addNewAndOldCnt += 1
            # sys.exit("DEBUG: ortho_merger.py :: integrate_arch_ortho_into_gclstr :: case (0, 1) or (1, 0)")

        # Mixed case in which one part of the group are all new (0),
        # all contained (1) or partly new (2)
        # The folloe memberhips cobinations are handled below
        # (1, 2); (2, 1); (2, 2); (0, 2); (2, 0)
        else:
            mixedClstrsCnt += 1

            clusterModOutcome = integrate_mixed_arch_clstr(aSp1IdsView, aSp2IdsView, cosineValsList, mClstrDict, archMasterDict, sp1Id, sp2Id, graphSp1Ortho2info, graphSp2Ortho2info, membershipDict, covThr)

            # The ortholog from the arch-based cluster were all rejected
            if clusterModOutcome[0] == 0:
                # print(f"Rejected mixed:\t{clusterModOutcome}")
                rejectMixedCnt += 1
            # some of the new arch-orthologs were not added to G
            elif clusterModOutcome[0] == 1:
                addMixedModCnt += 1
            # all new arch-orthologs added to G
            elif clusterModOutcome[0]==2:
                addMixedCnt += 1
            # Modification led to a cluster of only new orthologs
            else:
                # print(f"Special new mixed case:\t{clusterModOutcome}")
                addMixedModAllNewCnt += 1
            # sys.exit("DEBUG: ortho_merger.py :: integrate_arch_ortho_into_gclstr :: mixed case")

    # For ech arch based cluster, its type in
    # relation to the graph-based clusters as follows:
    # New: none of the orhtologs are predicted by graph-method
    # Contained: all the orhtologs are predicted by graph-method
    # Partially new: some of the orhtologs are predicted by graph-method (others are new)
    # sys.exit("DEBUG: ortho_merger.py :: integrate_arch_ortho_into_gclstr")

    cdef unsigned long finalClstrCnt = len(mClstrDict)

    '''
    if debug:
        print(f"""Arch-orthologs integration summary:
        Graph-based clusters (before modifications):\t{mClstrCnt}
        Arch-based clusters (all):\t{aClstrCnt}
        Merged clusters (all):\t{finalClstrCnt}
        Completely new (total):\t{newAddedClstrsCnt}
        Completely new (added unchanged):\t{addNewCnt}
        Completely new (added modified):\t{addNewModCnt}
        Completely new (rejected):\t{rejectNewCnt}
        Completely contained (total):\t{completelyContainedClstrsCnt}
        Completely contained (rejected):\t{rejectContainedCnt}
        Completely new and contained (total):\t{newAndOldClstrsCnt}
        Completely new and contained (added modified):\t{addNewAndOldCnt}
        Completely new and contained (rejected):\t{rejectNewAndOldCnt}
        Mixed case (total):\t{mixedClstrsCnt}
        Mixed (all new added to old G):\t{addMixedCnt}
        Mixed (some new rejected):\t{addMixedModCnt}
        Mixed (added modified all new):\t{addMixedModAllNewCnt}
        Mixed (rejected):\t{rejectMixedCnt}
        Orthologs from Sp1/Sp2 (before merging):\t{gSp1OrthoCnt}\t{gSp2OrthoCnt}
        Orthologs from Sp1/Sp2 (after merging):\t{len(graphSp1Ortho2info)}\t{len(graphSp2Ortho2info)}""")
    '''

    # HACK: this is hardcoded and should be fixed
    '''
    outFile = "/home/salvocos/Desktop/sonicparanoid-arch-analysis/test-directory/graph-arch-orto-merging/test-output-pairs"
    outFile = os.path.join(outFile, f"{sp1Id}-{sp2Id}.merged.ortho.pairs.tsv")
    write_pairs_to_file(mClstrDict, outFile, sp1Str, sp2Str, 1)
    '''

    # Output tuple with information regarding the merging
    # 0 -> sp1
    # 1 -> sp2
    # 2 -> G clusters
    # 3 -> A clusters
    # 4 -> merged Clusters
    # 5 -> newly added arch clusters
    # 6 -> modified G clusters
    # 7 -> Rejected arch-clusters
    # NOTE: newlyAddedCnt + mClstrCnt must be finalClstrCnt
    cdef unsigned long newlyAddedCnt = addNewCnt + addNewModCnt + addMixedModAllNewCnt
    cdef unsigned long gClstrModCnt = addNewAndOldCnt + addMixedModCnt + addMixedCnt
    cdef unsigned long aClstrRejectCnt = rejectNewCnt + rejectContainedCnt + rejectNewAndOldCnt + rejectMixedCnt

    cdef (unsigned long, unsigned long, unsigned long, unsigned long, unsigned long, unsigned long, unsigned long, unsigned long) outTpl = (sp1Id, sp2Id, mClstrCnt, aClstrCnt, finalClstrCnt, newlyAddedCnt, gClstrModCnt, aClstrRejectCnt)

    return outTpl



# TODO: change the parameters so that objects are not passed
# HACK: when cython will support DataClasses as paramters in cdef functions
# reduce the number of paramaters and directly passing the DataClass objects (e.g., ArchClstr)
cdef inline (unsigned long, unsigned long) integrate_contained_and_new_arch_clstr(unsigned long aClstrId, unsigned long aClstrSize, dict aClstrDict, cnp.uint32_t[:] aSp1IdsView, cnp.uint32_t[:] aSp2IdsView, list cosineValsList, dict mClstrDict, dict archMasterDict, unsigned long sp1Id, unsigned long sp2Id, dict graphSp1Ortho2info, dict graphSp2Ortho2info, dict membershipDict, double covThr):
    """
        Given a arch-based cluster with members from one species already in G, and and those from the other not in G.
        Integrate into the Graph based cluster based on multiple conditions
    """

    # print("Cases: (1, 0), (0, 1)")
    # Tmp variables
    cdef size_t i # Indexes to be used in for loops
    cdef unsigned long sp1OrthoCnt = aSp1IdsView.shape[0]
    cdef unsigned long sp2OrthoCnt = aSp2IdsView.shape[0]
    cdef unsigned long gClstrSize = 0
    cdef unsigned long gSpxOrthoCnt
    cdef unsigned long gClstrId = 0
    cdef double tmpGorthoScore
    cdef bint sp1HasNewMembers
    cdef double cosine = 0.0
    # contains the cluster in which a given ortholog is
    # and its graph-based scores
    cdef (unsigned long, double) tmpGorthoInfo
    cdef dict graphSpxOrtho2info2Use
    cdef dict graphSpxOrtho2info2Mod
    cdef (unsigned long, unsigned long) clusterModOutcome = (0, 0)

    # Says that the complete arch cluster should be ignored
    cdef bint ignoreClstr = 0

    # NOTE: this is used only for debugging
    # tmpAclstr: ArchClstr = aClstrDict[aClstrId]
    tmpMclstr: MergedClstr = MergedClstr(0, np.array(0, dtype=np.uint32), np.array(0, dtype=np.uint32), np.array(0, dtype=np.float32), np.array(0, dtype=np.float32))
    cdef double sp1ArchCov
    cdef double sp2ArchCov
    cdef unsigned long spxId = 0
    cdef unsigned long sp1ArchDomCnt = 0
    cdef unsigned long sp2ArchDomCnt = 0

    # buffer arrays used to modify merged clusters
    cdef cnp.uint32_t[:] gSpxOrthologs
    cdef cnp.float32_t[:] gSpxScores
    cdef cnp.ndarray[cnp.uint32_t, ndim=1] newGSpxOrthologs
    cdef cnp.ndarray[cnp.float32_t, ndim=1] newGSpxScores
    # These to views are just pointers to the input ID view
    cdef cnp.uint32_t[:] aSpxNewIdsView
    cdef cnp.uint32_t[:] aSpxContainedIdsView

    tmpSp1Arch: Arch = Arch(0, 0.0, 0, 0, np.zeros(1, dtype=np.uint32), np.zeros(1, dtype=np.uint32), np.zeros(1, dtype=np.uint32), np.array(["sp1"], dtype=np.str_), np.zeros(1, dtype=np.float32), 1)
    tmpSp2Arch: Arch = Arch(0, 0.0, 0, 0, np.zeros(1, dtype=np.uint32), np.zeros(1, dtype=np.uint32), np.zeros(1, dtype=np.uint32), np.array(["sp2"], dtype=np.str_), np.zeros(1, dtype=np.float32), 1)

    # Identify the cluster in G that contains the not-new orthologs
    # The ortholog in sp1 is contained in G
    # if aClstrMembership[0] == 1:
    if membershipDict[0][0] == 1:
        sp1HasNewMembers = 0
    else:
        sp1HasNewMembers = 1

    # print(f"\naClstrSize:\t{aClstrSize}")
    # NOTE: this is working in the case of pairs
    # Assuming sp1 contains the new arch-based ortholog,
    # the code below handles:
    # 1-to-1 or 1-to-many clusters
    if aClstrSize == 2:
        # print(f"\nCluster {aClstrId} (PAIR):\n{tmpAclstr}")
        # print(f"Cluster memberships (sp1\sp2)(inSp1/inSp2):\t{membershipDict[0][0]}\t{membershipDict[1][0]}\t{membershipDict[0][1]}\t{membershipDict[1][1]}")

        # Extract the 2 archs first
        tmpSp1Arch = archMasterDict[sp1Id][aSp1IdsView[0]]
        tmpSp2Arch = archMasterDict[sp2Id][aSp2IdsView[0]]
        sp1ArchCov = getattr(tmpSp1Arch, "coverage")
        sp2ArchCov = getattr(tmpSp2Arch, "coverage")
        cosine = cosineValsList[0][0]
        # print(f"The two orthologs are in the following graph-clusters:\t{tmpSp1GclstrInfo[0]}\t{tmpSp2GclstrInfo[0]}")
        # Decide based on the otholog scores
        # One of the graph-based orthologs is an in-paralog
        # if (cosineValsList[0][0] == 1.0) and (sp1ArchCov > 0.98) and (sp2ArchCov > 0.98):

        # Remove if the domain count is different
        sp1ArchDomCnt = getattr(tmpSp1Arch, "domCnt")
        sp2ArchDomCnt = getattr(tmpSp2Arch, "domCnt")

        # Identify the cluster in G that contains the not-new orthologs
        # The ortholog in sp1 is contained in G
        if not sp1HasNewMembers:
            # Check the domain count difference
            if sp1ArchDomCnt < sp2ArchDomCnt: # Check the domain count
                # Print some info one the pair
                # print("\nDomain count mismatch with sp1 in G:")
                # print(getattr(tmpSp1Arch, "phrase"))
                # print(getattr(tmpSp2Arch, "phrase"))
                # print(f"Cosine:\t{cosine:.3f}")
                # print(f"Coverages:\t{sp1ArchCov:.3f}\t{sp2ArchCov:.3f}")
                # print(f"Domain counts:\t{sp1ArchDomCnt:}\t{sp2ArchDomCnt}")
                ignoreClstr = 1
            elif sp2ArchCov < covThr:
                # Print some info one the pair
                # print("\nNew ortholog in sp2 rejected due to low coverage:")
                # print(getattr(tmpSp1Arch, "phrase"))
                # print(getattr(tmpSp2Arch, "phrase"))
                # print(f"Cosine:\t{cosine:.3f}")
                # print(f"Coverages:\t{sp1ArchCov:.3f}\t{sp2ArchCov:.3f}")
                # print(f"Domain counts:\t{sp1ArchDomCnt:}\t{sp2ArchDomCnt}")
                ignoreClstr = 1
            else:
                tmpGorthoInfo = graphSp1Ortho2info[aSp1IdsView[0]]
                tmpGorthoScore = tmpGorthoInfo[1]
                gClstrId = tmpGorthoInfo[0]
                # print(tmpGorthoInfo)
        # The ortholog in sp2 is contained in G
        else:
            # Check the domain count difference
            if sp1ArchDomCnt > sp2ArchDomCnt: # Check the domain count
                # Print some info one the pair
                # print("\nDomain count mismatch with sp2 in G:")
                # print(getattr(tmpSp1Arch, "phrase"))
                # print(getattr(tmpSp2Arch, "phrase"))
                # print(f"Cosine:\t{cosine:.3f}")
                # print(f"Coverages:\t{sp1ArchCov:.3f}\t{sp2ArchCov:.3f}")
                # print(f"Domain counts:\t{sp1ArchDomCnt:}\t{sp2ArchDomCnt}")
                ignoreClstr = 1
            elif sp1ArchCov < covThr:
                # Print some info one the pair
                # print("\nNew ortholog in sp1 rejected due to low coverage:")
                # print(getattr(tmpSp1Arch, "phrase"))
                # print(getattr(tmpSp2Arch, "phrase"))
                # print(f"Cosine:\t{cosine:.3f}")
                # print(f"Coverages:\t{sp1ArchCov:.3f}\t{sp2ArchCov:.3f}")
                # print(f"Domain counts:\t{sp1ArchDomCnt:}\t{sp2ArchDomCnt}")
                ignoreClstr = 1
            else:
                tmpGorthoInfo = graphSp2Ortho2info[aSp2IdsView[0]]
                tmpGorthoScore = tmpGorthoInfo[1]
                gClstrId = tmpGorthoInfo[0]
                # print(tmpGorthoInfo)

        # If the arch cluster was not rejected
        if not ignoreClstr:
            # Check if included ortholog is inparalog with very low score
            # In such cases we might consider the following
            # Option 1: reject because very close inparalogs do not imply close orthologs
            # Option 2: create a new cluster with a single pair,
            #  and remove the inparalog from the old cluster
            # NOTE: in the Ecoli-Hsapiens study case gene 33.18642 from Hsapiens has very low score
            if tmpGorthoScore < 0.05:
                # Consider creating a new pair
                ignoreClstr = 1
                # if (sp1ArchCov >= 90) or (sp2ArchCov >= 90):
                #     print(f"\nInparalog with very low score and high-cov Archs!")
                #     print(getattr(tmpSp1Arch, "phrase"))
                #     print(getattr(tmpSp2Arch, "phrase"))
                #     print(f"Coverages:\t{sp1ArchCov:.2f}\t{sp2ArchCov:.2f}")
                #     print(f"Cosine:\t{cosine:.2f}")
                #     sys.exit("DEBUG: Low score inparalog and very-high Arch coverage!!!!")

            else:
                # Simply add the new ortholog
                # print(f"Modify MergedCluster {gClstrId}:")
                tmpMclstr = mClstrDict[gClstrId]
                # print(tmpMclstr)
                # Extract the information required to modify the merged cluster
                gClstrSize = getattr(tmpMclstr, "size")
                # Modify the sp1 part of the merged cluster
                if sp1HasNewMembers:
                    gSpxOrthologs = getattr(tmpMclstr, "sp1Ids") # could be a array view
                    gSpxOrthoCnt = gSpxOrthologs.shape[0]
                    gSpxScores = getattr(tmpMclstr, "sp1Scores") # could a array view
                    # inizialize the new arrays
                    newGSpxOrthologs = np.zeros(gSpxOrthoCnt + 1, dtype=np.uint32)
                    newGSpxScores = np.zeros(gSpxOrthoCnt + 1, dtype=np.float32)
                    # Fill the arrays with the old values
                    for i in range(gSpxOrthoCnt):
                        newGSpxOrthologs[i] = gSpxOrthologs[i]
                        newGSpxScores[i] = gSpxScores[i]
                    # update the gcluster size
                    gClstrSize += 1
                    # Now add the new ortholog and score
                    newGSpxOrthologs[gSpxOrthoCnt] = aSp1IdsView[0]
                    newGSpxScores[gSpxOrthoCnt] = cosine

                    # update graphSp1Ortho2info
                    # DEBUG ONLY
                    # if aSp1IdsView[0] in graphSp1Ortho2info:
                    #     sys.exit(f"{aSp1IdsView[0]} already in graphSp1Ortho2info! This should never happen!")
                    graphSp1Ortho2info[aSp1IdsView[0]] = (gClstrId, cosine)
                    # Finally modify the cluster
                    mClstrDict[gClstrId] = MergedClstr(gClstrSize, newGSpxOrthologs, getattr(tmpMclstr, "sp2Ids"), newGSpxScores, getattr(tmpMclstr, "sp2Scores"))
                    # print(f"Modified cluster (sp1HasNewMembers = {sp1HasNewMembers}):\n{mClstrDict[gClstrId]}")
                # Modify the sp2 part of the merged cluster
                else:
                    gSpxOrthologs = getattr(tmpMclstr, "sp2Ids") # could be a array view
                    gSpxOrthoCnt = gSpxOrthologs.shape[0]
                    gSpxScores = getattr(tmpMclstr, "sp2Scores") # could a array view

                    # inizialize the new arrays
                    newGSpxOrthologs = np.zeros(gSpxOrthoCnt + 1, dtype=np.uint32)
                    newGSpxScores = np.zeros(gSpxOrthoCnt + 1, dtype=np.float32)
                    # Fill the arrays with the old values
                    for i in range(gSpxOrthoCnt):
                        newGSpxOrthologs[i] = gSpxOrthologs[i]
                        newGSpxScores[i] = gSpxScores[i]
                    # update the gcluster size
                    gClstrSize += 1
                    # Now add the new ortholog and score
                    newGSpxOrthologs[gSpxOrthoCnt] = aSp2IdsView[0]
                    newGSpxScores[gSpxOrthoCnt] = cosine
                    # update graphSp2Ortho2info
                    # DEBUG ONLY
                    # if aSp2IdsView[0] in graphSp2Ortho2info:
                    #     sys.exit("This should never happen! (graphSp2Ortho2info update)")
                    graphSp2Ortho2info[aSp2IdsView[0]] = (gClstrId, cosine)
                    # Finally modify the cluster
                    mClstrDict[gClstrId] = MergedClstr(gClstrSize, getattr(tmpMclstr, "sp1Ids"), newGSpxOrthologs, getattr(tmpMclstr, "sp1Scores"), newGSpxScores)
                    # print(f"Modified cluster (sp1HasNewMembers = {sp1HasNewMembers}):\n{mClstrDict[gClstrId]}")
    # 1-to-many/ many-to-1 / many-to-many
    else:
        # Go through the new ortholog
        # and filter them based on the coverage
        # print(f"\nCluster {aClstrId} (MULTI):\n{tmpAclstr}")
        # print(f"Cluster memberships (sp1\sp2)(inSp1/inSp2):\t{membershipDict[0][0]}\t{membershipDict[1][0]}\t{membershipDict[0][1]}\t{membershipDict[1][1]}")

        # The new orthologs are contained in Sp1
        if sp1HasNewMembers:
            spxId = sp1Id
            aSpxNewIdsView = aSp1IdsView
            aSpxContainedIdsView = aSp2IdsView
            # Set the dictionary with cluster info
            graphSpxOrtho2info2Use = graphSp2Ortho2info
            graphSpxOrtho2info2Mod = graphSp1Ortho2info
        # The new orthologs are contained in Sp2
        else:
            spxId = sp2Id
            aSpxContainedIdsView = aSp1IdsView
            aSpxNewIdsView = aSp2IdsView
            # Set the dictionary with cluster info
            graphSpxOrtho2info2Use = graphSp1Ortho2info
            graphSpxOrtho2info2Mod = graphSp2Ortho2info

        # Call the function that performs the insertion if possible
        clusterModOutcome = integrate_new_arch_orthologs_into_g_clstr(sp1OrthoCnt, sp2OrthoCnt, aSpxNewIdsView, aSpxContainedIdsView, cosineValsList, mClstrDict, archMasterDict, spxId, graphSpxOrtho2info2Use, graphSpxOrtho2info2Mod, sp1HasNewMembers, covThr)
        return clusterModOutcome

    # sys.exit("\nDEBUG: ortho_merger.pyx :: integrate_contained_and_new_arch_clstr")
    # return an interger describing the state of the cluster
    # 0 -> reject
    if ignoreClstr:
        clusterModOutcome = (0, aClstrId)
    else:
        clusterModOutcome = (1, gClstrId)

    return clusterModOutcome


# TODO: change the parameters so that objects are not passed
# HACK: when cython will support DataClasses as paramters in cdef functions
# reduce the number of paramaters and directly passing the DataClass objects (e.g., ArchClstr)
cdef inline (unsigned long, unsigned long) integrate_contained_arch_clstr(unsigned long aClstrId, unsigned long aClstrSize, dict aClstrDict, cnp.uint32_t[:] aSp1IdsView, cnp.uint32_t[:] aSp2IdsView, list cosineValsList, dict archMasterDict, unsigned long sp1Id, unsigned long sp2Id, dict graphSp1Ortho2info, dict graphSp2Ortho2info):
    """
        Given an arch-based cluster with members already in G, integrate it into G if conditions are met.
    """

    cdef (unsigned long, unsigned long) clusterModOutcome = (0, aClstrId)

    ''' HACK: for now we reject the cluster regardless, as modification of graph cluster would over-complicate the methods
    # Tmp variables
    cdef (unsigned int, double) tmpSp1GclstrInfo
    cdef (unsigned int, double) tmpSp2GclstrInfo

    # Says that the complete arch cluster should be ignored
    # TODO: this is only used for debugging and could be removed
    # tmpAclstr: ArchClstr = aClstrDict[aClstrId]
    cdef double sp1ArchCov
    cdef double sp2ArchCov
    # NOTE: not used for now
    # aSp1Set: set[int] = set()
    # aSp2Set: set[int] = set()

    tmpSp1Arch: Arch = Arch(0, 0.0, 0, 0, np.zeros(0, dtype=np.uint32), np.zeros(0, dtype=np.uint32), np.zeros(0, dtype=np.uint32), np.array(["sp1"], dtype=np.str_), np.zeros(0, dtype=np.float32), 1)
    tmpSp2Arch: Arch = Arch(0, 0.0, 0, 0, np.zeros(0, dtype=np.uint32), np.zeros(0, dtype=np.uint32), np.zeros(0, dtype=np.uint32), np.array(["sp2"], dtype=np.str_), np.zeros(0, dtype=np.float32), 1)

    # Check if it is a pair
    if aClstrSize == 2:
        # FIXME: this could be heavily simplified,
        # if we are always simply rejecting the Arch-pair
        # If we do so, no condition is required

        # print(f"\nCluster membership:\t{aClstrMembership}")
        # print(f"Cluster {aClstrId}:\n{tmpAclstr}")
        # NOTE: this is the simplest case
        # print(f"Old pair found ({aClstrId})!")
        tmpSp1GclstrInfo = graphSp1Ortho2info[aSp1IdsView[0]]
        tmpSp2GclstrInfo = graphSp2Ortho2info[aSp2IdsView[0]]
        # make sure they belong to the same Graph-based cluster
        # print(graphSp1Ortho2info[aSp1IdsView[0]])
        if tmpSp1GclstrInfo[0] != tmpSp2GclstrInfo[0]:
            tmpSp1Arch = archMasterDict[sp1Id][aSp1IdsView[0]]
            tmpSp2Arch = archMasterDict[sp2Id][aSp2IdsView[0]]
            sp1ArchCov = getattr(tmpSp1Arch, "coverage")
            sp2ArchCov = getattr(tmpSp2Arch, "coverage")
            # print(f"The two orthologs are in the following graph-clusters:\t{tmpSp1GclstrInfo[0]}\t{tmpSp2GclstrInfo[0]}")
            # Decide based on the otholog scores
            # One of the graph-based orthologs is an in-paralog
            if (cosineValsList[0][0] == 1.0) and (sp1ArchCov > 0.98) and (sp2ArchCov > 0.98):
                # Both graph-graph-ortholog are inparalogs
                if (tmpSp1GclstrInfo[1] < 1) and (tmpSp2GclstrInfo[1] < 1):
                    print("\nBoth graph-ortholog are inparalogs!")
                    print(f"Pair:\t({sp1Id}, {sp2Id})")
                    # print(f"Cluster {aClstrId}:\n{tmpAclstr}")
                    print(f"The two orthologs are in the following graph-clusters:\t{tmpSp1GclstrInfo[0]}\t{tmpSp2GclstrInfo[0]}")
                    print(f"Graph ortholog scores:\t{tmpSp1GclstrInfo[1]}\t{tmpSp2GclstrInfo[1]}")
                    print(f"Arch ortholog coverages:\t{sp1ArchCov}\t{sp2ArchCov}")
                    sys.exit("DEBUG: both graph-ortholog are inparalog")

                    # Default option:
                    # Remove the inparalogs from the cluster containing them
                    # Extra option:
                    # Add the arch-pair as a new one
                    return (0, aClstrId)

                elif tmpSp1GclstrInfo[1] + tmpSp2GclstrInfo[1] < 2:
                    # print("\nOne of the graph-orthologs is inparalog!")
                    # print(f"Pair:\t({sp1Id}, {sp2Id})")
                    # print(f"Cluster {aClstrId}:\n{tmpAclstr}")
                    # print(f"The two orthologs are in the following graph-clusters:\t{tmpSp1GclstrInfo[0]}\t{tmpSp2GclstrInfo[0]}")
                    # print(f"Graph ortholog scores:\t{tmpSp1GclstrInfo[1]}\t{tmpSp2GclstrInfo[1]}")
                    # print(f"Arch ortholog coverages:\t{sp1ArchCov}\t{sp2ArchCov}")
                    # sys.exit("DEBUG: one graph-ortholog is inparalog")

                    # Option 1:
                    # Remove the inparalog from the cluster containing it
                    # Keep  the graph-cluster with the other ortholog as it is
                    return (0, aClstrId)
                else:
                    # print("\nBoth graph-pairs have score 1.0, but in different clusters!")
                    # print(f"Pair:\t({sp1Id}, {sp2Id})")
                    # print(f"Cluster {aClstrId}:\n{tmpAclstr}")
                    # print(f"The two orthologs are in the following graph-clusters:\t{tmpSp1GclstrInfo[0]}\t{tmpSp2GclstrInfo[0]}")
                    # print(f"Graph ortholog scores:\t{tmpSp1GclstrInfo[1]}\t{tmpSp2GclstrInfo[1]}")
                    # print(f"Arch ortholog coverages:\t{sp1ArchCov}\t{sp2ArchCov}")
                    # print(f"Reject arch-pair (cosine == 1 and cov>98%, graph scores == 1):\t{tmpSp1GclstrInfo[1]}\t{tmpSp2GclstrInfo[1]}")
                    return (0, aClstrId)

            # Do not modify the Graph-based pairs
            # and simply reject the Arch-based-prediction
            else:
                # print(f"Reject arch-pair (cosine < 1 or cov<98%):\t{tmpSp1GclstrInfo[1]}\t{tmpSp2GclstrInfo[1]}")
                return (0, aClstrId)

    # HACK: for now simply ignore the Arch-based cluster
    # and simply keep the graph-based ones without any modification
    else:
        # Create the sets for sp1 and sp2
        # to identify when some member are scattered
        # into multiple clusters in G

        # TODO: 
        # 1) Check the G clusters for sp1 and sp2
        # 2) If they are concordant, reject
        # Otherwise consider modifing the original G clusters

        return (0, aClstrId)
    '''

    return clusterModOutcome



cdef inline (unsigned long, unsigned long) integrate_mixed_arch_clstr(cnp.uint32_t[:] aSp1IdsView, cnp.uint32_t[:] aSp2IdsView, list cosineValsList, dict mClstrDict, dict archMasterDict, unsigned long sp1Id, unsigned long sp2Id, dict graphSp1Ortho2info, dict graphSp2Ortho2info, dict membershipDict, double covThr):
    """
    Integrate arch-based cluster which can be or not be already in G.
    """

    # Extract membership information
    cdef unsigned int aSp1Mem = membershipDict[0][0]
    cdef unsigned int aSp2Mem = membershipDict[1][0]
    cdef cnp.uint8_t[:] aSp1ContainedIdxs = membershipDict[0][1]
    cdef cnp.uint8_t[:] aSp2ContainedIdxs = membershipDict[1][1]
    cdef bint sp1HasOnlyNewMembers
    # Arrays needed for modification
    cdef cnp.uint32_t[:] aSpxAllNewIdsView
    cdef cnp.uint32_t[:] aSpxMixedIdsView
    cdef cnp.uint8_t[:] aSpxContainedIdxsView
    cdef dict graphSpxOrtho2infoAllNew
    cdef dict graphSpxOrtho2infoMixed
    cdef (unsigned long, unsigned long) clusterModOutcome = (0, 0)

    # print(f"Membership sp1/sp2:\t{membershipDict[0][0]}\t{membershipDict[1][0]}")

    # Handle cases (2, 0) and (0, 2)
    # In this case one side of the cluster is completely new,
    # while the other size contains a mix of new and already contained orthologs
    if (aSp1Mem == 0) or (aSp2Mem == 0):
        # print("\nCases: (2, 0) and (0, 2)")
        # print(f"Membership sp1\\sp2:\t{membershipDict[0][0]}\t{membershipDict[1][0]}")
        # print(f"Cluster {aClstrId} sizes sp1/sp2:\t{aSp1IdsView.shape[0]}\t{aSp2IdsView.shape[0]}")
        # print(f"Containment in G:\t{np.asarray(aSp1ContainedIdxs)}\t{np.asarray(aSp2ContainedIdxs)}")

        # Sp1 contains only new orthologs
        if aSp1Mem == 0:
            sp1HasOnlyNewMembers = 1
            aSpxAllNewIdsView = aSp1IdsView
            graphSpxOrtho2infoAllNew = graphSp1Ortho2info
            aSpxMixedIdsView = aSp2IdsView
            aSpxContainedIdxsView = aSp2ContainedIdxs
            graphSpxOrtho2infoMixed = graphSp2Ortho2info
            clusterModOutcome = integrate_new_and_mixed_arch_orthologs_into_g_clstr(aSpxAllNewIdsView, aSpxMixedIdsView, aSp1ContainedIdxs, aSp2ContainedIdxs, cosineValsList, mClstrDict, archMasterDict, graphSpxOrtho2infoAllNew, graphSpxOrtho2infoMixed, sp1Id, sp2Id, sp1HasOnlyNewMembers, covThr)
            # sys.exit("DEBUG :: All new in Sp1")
        # Sp2 contains only new orthologs
        else:
            sp1HasOnlyNewMembers = 0
            aSpxMixedIdsView = aSp1IdsView
            aSpxContainedIdxsView = aSp1ContainedIdxs
            graphSpxOrtho2infoMixed = graphSp1Ortho2info
            aSpxAllNewIdsView = aSp2IdsView
            graphSpxOrtho2infoAllNew = graphSp2Ortho2info
            clusterModOutcome = integrate_new_and_mixed_arch_orthologs_into_g_clstr(aSpxAllNewIdsView, aSpxMixedIdsView, aSp1ContainedIdxs, aSp2ContainedIdxs, cosineValsList, mClstrDict, archMasterDict, graphSpxOrtho2infoAllNew, graphSpxOrtho2infoMixed, sp1Id, sp2Id, sp1HasOnlyNewMembers, covThr)
    # Handles cases (2, 1), (1, 2) and (2, 2)
    else:
        # print("\nCases: (2, 1), (1, 2) and (2, 2)")
        # print(f"Membership sp1\\sp2:\t{membershipDict[0][0]}\t{membershipDict[1][0]}")
        # print(f"Cluster {aClstrId} sizes sp1/sp2:\t{aSp1IdsView.shape[0]}\t{aSp2IdsView.shape[0]}")
        # print(f"Cotainment in G:\t{np.asarray(aSp1ContainedIdxs)}\t{np.asarray(aSp2ContainedIdxs)}")
        clusterModOutcome = integrate_mixed_arch_orthologs_into_g_clstr(aSp1IdsView, aSp2IdsView, aSp1Mem, aSp2Mem, aSp1ContainedIdxs, aSp2ContainedIdxs, cosineValsList, mClstrDict, archMasterDict, graphSp1Ortho2info, graphSp2Ortho2info, sp1Id, sp2Id, covThr)

    return clusterModOutcome



cdef inline (unsigned long, unsigned long) integrate_mixed_arch_orthologs_into_g_clstr(cnp.uint32_t[:] aSp1IdsView, cnp.uint32_t[:] aSp2IdsView, unsigned int aSp1Mem, unsigned int aSp2Mem, cnp.uint8_t[:] aSp1ContainedIdxs, cnp.uint8_t[:] aSp2ContainedIdxs, list cosineValsList, dict mClstrDict, dict archMasterDict, dict graphSp1Ortho2info, dict graphSp2Ortho2info, unsigned long sp1Id, unsigned long sp2Id, double covThr):
    '''
    This function handles the cases (1, 2), (2, 1) and (2, 2)
    in which one side of the clusters (that with 0) contains only new orthologs,
    whether the other is mixed.
    '''

    # print("\nintegrate_mixed_arch_orthologs_into_g_clstr :: START")
    # print(f"Memberships Sp1\\Sp2:\t{aSp1Mem}\t{aSp2Mem}")
    # print(f"Sp1: {np.asarray(aSp1IdsView)}\tcontainement: {np.asarray(aSp1ContainedIdxs)}")
    # print(f"Sp2: {np.asarray(aSp2IdsView)}\tcontainement: {np.asarray(aSp2ContainedIdxs)}")

    cdef unsigned long aSp1OrthoCnt = aSp1IdsView.shape[0]
    cdef unsigned long aSp2OrthoCnt = aSp2IdsView.shape[0]
    # cdef bint allInSameGClstr = 0
    cdef bint sp1AllInSameGClstr = 0
    cdef bint sp2AllInSameGClstr = 0
    cdef bint allowDomCntMismatch = 0
    cdef dict avgArchScores
    cdef cnp.float32_t[:] aSp1GraphAvgScores
    cdef cnp.float32_t[:] aSp2GraphAvgScores
    # cdef cnp.uint8_t[:] aSpxContainedIdxsView

    # This contains the result from functions that add or modify clusters
    # The first field indicates the type of modification (check each function for details)
    # The second field is the cluster ID, which could be different
    # from that passed to each modification function
    cdef (unsigned long, unsigned long) clusterModOutcome = (0, 0)

    # Define variables to store modified mixed vectors
    cdef dict aSpxMixedModVectors
    cdef cnp.ndarray[cnp.uint32_t, ndim=1] aSpxMixedModIds
    cdef cnp.ndarray[cnp.float32_t, ndim=1] aSpxMixedModScores

    cdef unsigned int aSp1ContainedCnt
    cdef unsigned int aSp2ContainedCnt
    cdef unsigned int gClstrId
    cdef unsigned int sp1gClstrId
    cdef unsigned int sp2gClstrId
    # This will only contain zeros and will have the same length
    # as the array containing only new orthologs
    cdef cnp.ndarray[cnp.uint8_t, ndim=1] aSpxAllNewIdxs = np.zeros(0, dtype=np.uint8)

    # Check if the contained orthologs are all in the same G cluster
    sp1AllInSameGClstr = contained_in_same_g_clstr(aSp1IdsView, aSp1ContainedIdxs, aSp1OrthoCnt, graphSp1Ortho2info)
    # print(f"Contained in Sp1 all in same clstr:\t{sp1AllInSameGClstr}")

    # No new ortholog in Sp1 and those contained are in different clusters in G
    # In this case it not possible to recover any new ortholog from the A clstr
    if (not sp1AllInSameGClstr) and (aSp1Mem == 1):
        # print(f"Brute rejection as Sp1 membership {aSp1Mem} and the contained clusters are scattered in G.")
        # print(f"Sp1: {np.asarray(aSp1IdsView)}\tcontainement: {np.asarray(aSp1ContainedIdxs)}")
        # print(f"Sp2: {np.asarray(aSp2IdsView)}\tcontainement: {np.asarray(aSp2ContainedIdxs)}")
        # sys.exit("DEBUG: brute rejection on Sp1")
        return (0, 0)

    sp2AllInSameGClstr = contained_in_same_g_clstr(aSp2IdsView, aSp2ContainedIdxs, aSp2OrthoCnt, graphSp2Ortho2info)
    # print(f"Contained in Sp2 all in same clstr:\t{sp2AllInSameGClstr}")

    if (not sp2AllInSameGClstr) and (aSp2Mem == 1):
        # print(f"Brute rejection as Sp2 membership {aSp2Mem} and the contained clusters are scattered in G.")
        # print(f"Sp1: {np.asarray(aSp1IdsView)}\tcontainement: {np.asarray(aSp1ContainedIdxs)}")
        # print(f"Sp2: {np.asarray(aSp2IdsView)}\tcontainement: {np.asarray(aSp2ContainedIdxs)}")
        # sys.exit("DEBUG: brute rejection on Sp2")
        return (0, 0)

    # In this case we try
    if (not sp1AllInSameGClstr) and (not sp2AllInSameGClstr):
        # print("Worst scenario of G discordance")
        return (0, 0)

    # Try to recover some of the new orthologs
    if (not sp1AllInSameGClstr) or (not sp2AllInSameGClstr):
        # print(f"At least one discordance found with memberships/discordance Sp1/Sp2:\t{aSp1Mem}:{sp1AllInSameGClstr}\t{aSp2Mem}:{sp2AllInSameGClstr}")
        # NOTE: in this case the discordance should be on orthologs
        # from the species with mixed membership (2).
        # this is because the case with membership (1) and discordance
        # is already handled above.

        # In this situation we try to add only the new orthologs
        # from the subgroup with mixed memberships, to the alredy existing G cluster

        # FIXME: If the this increases the False positives, we might reject this case completely

        # Compute the average scores
        avgArchScores = compute_avg_cosine_scores(cosineValsList, aSp1OrthoCnt, aSp2OrthoCnt)
        aSp1GraphAvgScores = avgArchScores[0]
        aSp2GraphAvgScores = avgArchScores[1]

        # print(f"Sp1: {np.asarray(aSp1IdsView)}\tScores: {np.asarray(aSp1GraphAvgScores)}\tcontainement: {np.asarray(aSp1ContainedIdxs)}")
        # print(f"Sp2: {np.asarray(aSp2IdsView)}\tScores: {np.asarray(aSp2GraphAvgScores)}\tcontainement: {np.asarray(aSp2ContainedIdxs)}")

        # Do on exclude even if the domain count is not matching
        allowDomCntMismatch = 1

        # The mixed part is Sp2
        if sp1AllInSameGClstr:
            aSp2ContainedCnt = sum_bint_array(aSp2ContainedIdxs)
            aSpxMixedModVectors = remove_contained_in_g(aSp2IdsView, aSp2GraphAvgScores, aSp2ContainedIdxs, aSp2OrthoCnt, aSp2ContainedCnt)
            aSpxMixedModIds = aSpxMixedModVectors[0]
            aSpxMixedModScores = aSpxMixedModVectors[1]

            # Find the ID of the G cluster in which are the 'contained orthologs'
            for i in range(aSp1OrthoCnt):
                if aSp1ContainedIdxs[i] == 1:
                    # print(f"i\\contained\\ID:\t{i}\t{aSp1ContainedIdxs[i]}\t{aSp1IdsView[i]}")
                    # print(f"ID\\G Cluster:\t{aSp1IdsView[i]}\t{graphSp1Ortho2info[aSp1IdsView[i]]}")
                    # print(graphSpxOrtho2infoMixed[aSpxMixedIdsView[i]][0])
                    gClstrId = graphSp1Ortho2info[aSp1IdsView[i]][0]
                    break

            # print(f"G cluster ID:\t{gClstrId}")
            # print(f"Original G cluster:\n{mClstrDict[gClstrId]}")

            # All set to zero since these are all new
            aSpxAllNewIdxs = np.zeros(aSp2OrthoCnt - aSp2ContainedCnt, dtype=np.uint8)
            aSp2ContainedIdxs = aSpxAllNewIdxs
            clusterModOutcome = filter_and_add_arch_ortho2g_clstr(aSp1IdsView, aSpxMixedModIds, aSp1GraphAvgScores, aSpxMixedModScores, aSp1ContainedIdxs, aSp2ContainedIdxs, mClstrDict, gClstrId, archMasterDict, sp1Id, sp2Id, covThr, allowDomCntMismatch)

            # if clusterModOutcome[0] != 0:
            #     print(f"Updated G cluster {gClstrId}:\n{mClstrDict[clusterModOutcome[1]]}")

            # sys.exit("DEBUG :: trimmed contained from Sp2")
        # The mixed part is Sp1
        else:
            aSp1ContainedCnt = sum_bint_array(aSp1ContainedIdxs)
            aSpxMixedModVectors = remove_contained_in_g(aSp1IdsView, aSp1GraphAvgScores, aSp1ContainedIdxs, aSp1OrthoCnt, aSp1ContainedCnt)
            aSpxMixedModIds = aSpxMixedModVectors[0]
            aSpxMixedModScores = aSpxMixedModVectors[1]

            # Find the ID of the G cluster in which are the 'contained orthologs'
            for i in range(aSp2OrthoCnt):
                if aSp2ContainedIdxs[i] == 1:
                    # print(f"i\\contained\\ID:\t{i}\t{aSp2ContainedIdxs[i]}\t{aSp2IdsView[i]}")
                    # print(f"ID\\G Cluster:\t{aSp2IdsView[i]}\t{graphSp2Ortho2info[aSp2IdsView[i]]}")
                    # print(graphSpxOrtho2infoMixed[aSpxMixedIdsView[i]][0])
                    gClstrId = graphSp2Ortho2info[aSp2IdsView[i]][0]
                    break

            # print(f"G cluster ID:\t{gClstrId}")
            # print(f"Original G cluster:\n{mClstrDict[gClstrId]}")

            # All set to zero since these are all new
            aSpxAllNewIdxs = np.zeros(aSp1OrthoCnt - aSp1ContainedCnt, dtype=np.uint8)
            aSp1ContainedIdxs = aSpxAllNewIdxs
            clusterModOutcome = filter_and_add_arch_ortho2g_clstr(aSpxMixedModIds, aSp2IdsView, aSpxMixedModScores, aSp2GraphAvgScores, aSp1ContainedIdxs, aSp2ContainedIdxs, mClstrDict, gClstrId, archMasterDict, sp1Id, sp2Id, covThr, allowDomCntMismatch)


            # sys.exit("DEBUG :: trimmed contained from Sp1")

    # all must be in the same cluster
    else:
        # print("All contained in same G cluster!")
        # allInSameGClstr = 1

        # We need to make sure that that the contained in Sp1
        # and the contained in Sp2 are in the same G cluster

        # Find the G cluster ID for Sp1
        for i in range(aSp1OrthoCnt):
            if aSp1ContainedIdxs[i] == 1:
                # print(f"i\\contained\\ID:\t{i}\t{aSp1ContainedIdxs[i]}\t{aSp1IdsView[i]}")
                # print(f"ID\\G Cluster:\t{aSp1IdsView[i]}\t{graphSp1Ortho2info[aSp1IdsView[i]]}")
                sp1gClstrId = graphSp1Ortho2info[aSp1IdsView[i]][0]
                break

        # Find the G cluster ID for Sp2
        for i in range(aSp2OrthoCnt):
            if aSp2ContainedIdxs[i] == 1:
                # print(f"i\\contained\\ID:\t{i}\t{aSp2ContainedIdxs[i]}\t{aSp2IdsView[i]}")
                # print(f"ID\\G Cluster:\t{aSp2IdsView[i]}\t{graphSp2Ortho2info[aSp2IdsView[i]]}")
                sp2gClstrId = graphSp2Ortho2info[aSp2IdsView[i]][0]
                break

        # print(f"G cluster IDs Sp1/Sp2:\t{sp1gClstrId}\t{sp2gClstrId}")

        # Worst case of discordance
        if sp1gClstrId != sp2gClstrId:
            # print(f"Worst G clusters discordance! G IDs Sp1/Sp2:\t{sp1gClstrId}\t{sp2gClstrId}")
            return (0, 0)
        # Filter and add the new orthologs to G
        else:
            # Do on exclude even if the domain count is not matching
            allowDomCntMismatch = 1
            # NOTE: sp1gClstrId == sp2gClstrId
            gClstrId = sp1gClstrId
            # Compute the average scores
            avgArchScores = compute_avg_cosine_scores(cosineValsList, aSp1OrthoCnt, aSp2OrthoCnt)
            aSp1GraphAvgScores = avgArchScores[0]
            aSp2GraphAvgScores = avgArchScores[1]
            clusterModOutcome = filter_and_add_arch_ortho2g_clstr(aSp1IdsView, aSp2IdsView, aSp1GraphAvgScores, aSp2GraphAvgScores, aSp1ContainedIdxs, aSp2ContainedIdxs, mClstrDict, gClstrId, archMasterDict, sp1Id, sp2Id, covThr, allowDomCntMismatch)

    return clusterModOutcome



cdef inline (unsigned long, unsigned long) integrate_new_and_mixed_arch_orthologs_into_g_clstr(cnp.uint32_t[:] aSpxAllNewIdsView, cnp.uint32_t[:] aSpxMixedIdsView, cnp.uint8_t[:] aSp1ContainedIdxs, cnp.uint8_t[:] aSp2ContainedIdxs, list cosineValsList, dict mClstrDict, dict archMasterDict, dict graphSpxOrtho2infoAllNew, dict graphSpxOrtho2infoMixed, unsigned long sp1Id,  unsigned long sp2Id, bint sp1HasOnlyNewMembers, double covThr):
    '''
    This function handles the cases (0, 2) and (2, 0),
    in which one side of the clusters (that with 0) contains only new orthologs,
    whether the other is mixed.
    '''

    # print("\nintegrate_new_and_mixed_arch_orthologs_into_g_clstr :: START")
    cdef unsigned long aSpxAllNewOrthoCnt = aSpxAllNewIdsView.shape[0]
    cdef unsigned long aSpxMixedOrthoCnt = aSpxMixedIdsView.shape[0]
    cdef cnp.uint8_t[:] aSpxContainedIdxs
    cdef bint allInSameGClstr = 0
    cdef bint allowDomCntMismatch = 0
    cdef dict avgArchScores
    cdef cnp.float32_t[:] aSpxAllNewGraphAvgScores
    cdef cnp.float32_t[:] aSpxMixedGraphAvgScores
    # This contains the result from functions that add or modify clusters
    # The first field indicates the type of modification (check each function for details)
    # The second field is the cluster ID, which could be different
    # from that passed to each modification function
    cdef (unsigned long, unsigned long) clusterModOutcome = (0, 0)

    # Find which side has only new and accordingly compute the averages
    if sp1HasOnlyNewMembers:
        avgArchScores = compute_avg_cosine_scores(cosineValsList, aSpxAllNewOrthoCnt, aSpxMixedOrthoCnt)
        aSpxAllNewGraphAvgScores = avgArchScores[0]
        aSpxMixedGraphAvgScores = avgArchScores[1]
        aSpxContainedIdxs = aSp2ContainedIdxs
    else:
        avgArchScores = compute_avg_cosine_scores(cosineValsList, aSpxMixedOrthoCnt, aSpxAllNewOrthoCnt)
        aSpxMixedGraphAvgScores = avgArchScores[0]
        aSpxAllNewGraphAvgScores = avgArchScores[1]
        aSpxContainedIdxs = aSp1ContainedIdxs

    cdef unsigned long aSpxContainedCnt = sum_bint_array(aSpxContainedIdxs)
    # print(f"Sp1 are new: {sp1HasOnlyNewMembers}\tnew scores: {np.asarray(aSpxAllNewGraphAvgScores)}\tmixed scores: {np.asarray(aSpxMixedGraphAvgScores)}")

    # Define variables to store modified mixed vectors
    cdef dict aSpxMixedModVectors
    cdef cnp.ndarray[cnp.uint32_t, ndim=1] aSpxMixedModIds
    cdef cnp.ndarray[cnp.float32_t, ndim=1] aSpxMixedModScores
    # This will only contain zeros and will have the same length
    # as the array containing only new orthologs (aSpxAllNewIdsView)
    cdef cnp.ndarray[cnp.uint8_t, ndim=1] aSpxAllNewIdxs = np.zeros(aSpxAllNewOrthoCnt, dtype=np.uint8)

    # Check if all the contained orthologs are in the same cluster
    if aSpxContainedCnt > 1:
        allInSameGClstr = contained_in_same_g_clstr(aSpxMixedIdsView, aSpxContainedIdxs, aSpxMixedIdsView.shape[0], graphSpxOrtho2infoMixed)
        # print(f"All contained in same G cluster:\t{allInSameGClstr}")

        if not allInSameGClstr:
            aSpxMixedModVectors = remove_contained_in_g(aSpxMixedIdsView, aSpxMixedGraphAvgScores, aSpxContainedIdxs, aSpxMixedOrthoCnt, aSpxContainedCnt)
            aSpxMixedModIds = aSpxMixedModVectors[0]
            aSpxMixedModScores = aSpxMixedModVectors[1]
            # print(f"sp1HasOnlyNewMembers:\t{sp1HasOnlyNewMembers}")
            # NOTE: at this point there only new orthologs
            # the next step is to filter the orthologs
            # and see if we can obtain a new cluster to be added to G
            if sp1HasOnlyNewMembers:
                clusterModOutcome = filter_and_add_new_arch_clstr(aSpxAllNewIdsView, aSpxMixedModIds, aSpxAllNewGraphAvgScores, aSpxMixedModScores, mClstrDict, archMasterDict, sp1Id, sp2Id, covThr)
            # Sp2 contains only new orthologs
            else:
                clusterModOutcome = filter_and_add_new_arch_clstr(aSpxMixedModIds, aSpxAllNewIdsView, aSpxMixedModScores, aSpxAllNewGraphAvgScores, mClstrDict, archMasterDict, sp1Id, sp2Id, covThr)

            # HACK: special cluster type, better to remove later
            # In this case we set the cluster type to 3
            # which means that the new cluster only contains new orhtologs
            # due the old orthologs being in different clusters in G
            if clusterModOutcome[0] != 0:
                clusterModOutcome = (3, clusterModOutcome[1])

            return clusterModOutcome
    else:
        # print("Only 1 ortholog in G, then it must be in a single cluster")
        allInSameGClstr = 1

    # All contained in same cluster
    if allInSameGClstr:
        # print(f"All contained orthologs in same cluster.\nMixed:\t{np.asarray(aSpxMixedIdsView)}\nNew:\t{np.asarray(aSpxAllNewIdsView)}")

        # Find the ID of the G cluster in which are the 'contained orthologs'
        for i in range(aSpxMixedOrthoCnt):
            if aSpxContainedIdxs[i] == 1:
                # print(f"i\\contained\\ID:\t{i}\t{aSpxContainedIdxs[i]}\t{aSpxMixedIdsView[i]}")
                # print(f"ID\\G Cluster:\t{aSpxMixedIdsView[i]}\t{graphSpxOrtho2infoMixed[aSpxMixedIdsView[i]]}")
                gClstrId = graphSpxOrtho2infoMixed[aSpxMixedIdsView[i]][0]
                break

        # Do on exclude even if the domain count is not matching
        allowDomCntMismatch = 1
        if sp1HasOnlyNewMembers:
            aSp1ContainedIdxs = aSpxAllNewIdxs
            # Modify and existing G cluster
            clusterModOutcome = filter_and_add_arch_ortho2g_clstr(aSpxAllNewIdsView, aSpxMixedIdsView, aSpxAllNewGraphAvgScores, aSpxMixedGraphAvgScores, aSp1ContainedIdxs, aSp2ContainedIdxs, mClstrDict, gClstrId, archMasterDict, sp1Id, sp2Id, covThr, allowDomCntMismatch)
            # sys.exit("DEBUG: Sp1 are new")
        # Sp2 contains only new orthologs
        else:
            aSp2ContainedIdxs = aSpxAllNewIdxs
            # Modify and existing G cluster
            clusterModOutcome = filter_and_add_arch_ortho2g_clstr(aSpxMixedIdsView, aSpxAllNewIdsView, aSpxMixedGraphAvgScores, aSpxAllNewGraphAvgScores, aSp1ContainedIdxs, aSp2ContainedIdxs, mClstrDict, gClstrId, archMasterDict, sp1Id, sp2Id, covThr, allowDomCntMismatch)
            # sys.exit("DEBUG: Sp2 are new")

    return clusterModOutcome



# TODO: change the parameters so that objects are not passed
# HACK: when cython will support DataClasses as paramters in cdef functions
# reduce the number of paramaters and directly passing the DataClass objects (e.g., ArchClstr)
cdef inline (unsigned long, unsigned long) integrate_new_arch_clstr(unsigned long aClstrId, unsigned long aClstrSize, dict aClstrDict, cnp.uint32_t[:] aSp1IdsView, cnp.uint32_t[:] aSp2IdsView, list cosineValsList, dict mClstrDict, dict archMasterDict, unsigned long sp1Id, unsigned long sp2Id, double covThr):
    """
        Given an arch-based cluster that is not in G, integrate it into G if conditions are met.
    """

    # Tmp variables
    cdef size_t i, j # Indexes to be used in for loops
    cdef unsigned long sp1OrthoCnt = aSp1IdsView.shape[0]
    cdef unsigned long sp2OrthoCnt = aSp2IdsView.shape[0]
    cdef unsigned long newClstrId = len(mClstrDict) + 1
    cdef (unsigned long, unsigned long) clusterModOutcome = (0, aClstrId)
    # Says that the complete arch cluster should be ignored
    cdef bint ignoreClstr = 0

    # tmpAclstr: ArchClstr = aClstrDict[aClstrId]
    cdef double sp1ArchCov
    cdef double sp2ArchCov
    cdef unsigned long sp1ArchDomCnt = 0
    cdef unsigned long sp2ArchDomCnt = 0
    # Tmp variables used to modify the input cluster
    toRemoveSp1Ids: list[int] = []
    toRemoveSp2Ids: list[int] = []

    tmpSp1Arch: Arch = Arch(0, 0.0, 0, 0, np.zeros(0, dtype=np.uint32), np.zeros(0, dtype=np.uint32), np.zeros(1, dtype=np.uint32), np.array(["sp1"], dtype=np.str_), np.zeros(0, dtype=np.float32), 1)
    tmpSp2Arch: Arch = Arch(0, 0.0, 0, 0, np.zeros(0, dtype=np.uint32), np.zeros(0, dtype=np.uint32), np.zeros(0, dtype=np.uint32), np.array(["sp2"], dtype=np.str_), np.zeros(0, dtype=np.float32), 1)

    # Only the coverages and domain counts must be compared
    if aClstrSize == 2:
        # print("\nNew (PAIR) cluster!")
        tmpSp1Arch = archMasterDict[sp1Id][aSp1IdsView[0]]
        tmpSp2Arch = archMasterDict[sp2Id][aSp2IdsView[0]]
        sp1ArchCov = getattr(tmpSp1Arch, "coverage")
        sp2ArchCov = getattr(tmpSp2Arch, "coverage")

        # Reject  the pair if the coverage is lower than 75%
        if (sp1ArchCov < covThr) or (sp2ArchCov < covThr):
            # print("Reject pair:\tlow coverage")
            # print(f"{sp1Id}.{aSp1IdsView[0]}\t{sp2Id}.{aSp2IdsView[0]}")
            return clusterModOutcome
        # Remove if the domain count is different
        elif getattr(tmpSp1Arch, "domCnt") != getattr(tmpSp2Arch, "domCnt"): # Check the domain count
            # print("Reject pair:\tdomain count mismatch")
            # print(f"{sp1Id}.{aSp1IdsView[0]}\t{sp2Id}.{aSp2IdsView[0]}")
            # ignoreClstr = 1
            return clusterModOutcome
    # We can use extra conditions
    else:
        # print("\nNew (MULTI) cluster!")
        for i in range(sp1OrthoCnt):
            # Skip if already flagged as removable
            if i in toRemoveSp1Ids:
                continue
            
            tmpSp1Arch = archMasterDict[sp1Id][aSp1IdsView[i]]
            sp1ArchCov = getattr(tmpSp1Arch, "coverage")
            sp1ArchDomCnt = getattr(tmpSp1Arch, "domCnt")

            if sp1ArchCov < covThr:
                # print(f"Reject ortho Sp1:\tlow coverage\t{sp1ArchCov}")
                toRemoveSp1Ids.append(i)
                continue
            
            for j in range(sp2OrthoCnt):
                if j in toRemoveSp2Ids:
                    continue # No need to check again

                tmpSp2Arch = archMasterDict[sp2Id][aSp2IdsView[j]]
                sp2ArchCov = getattr(tmpSp2Arch, "coverage")
                sp2ArchDomCnt = getattr(tmpSp2Arch, "domCnt")

                # NOTE: we reject the whole cluster
                # even if we found a single domain count mismatch
                # this is probably too strict
                # Check the domain counts
                if sp1ArchDomCnt != sp2ArchDomCnt:
                    # print(f"Domain count mismatch in cluster {aClstrId}!")
                    return clusterModOutcome

                if sp2ArchCov < covThr:
                    # print(f"Reject ortho Sp2:\tlow coverage\t{sp2ArchCov}")
                    toRemoveSp2Ids.append(j)

    # Variables used to create a modified version of the Arch cluster
    # to be added to a graph based cluster
    newSp1Ids: list[int] = []
    newSp2Ids: list[int] = []
    newSp1Scores: list[np.ndarray] = []
    cdef unsigned long sp1ToRemoveCnt = len(toRemoveSp1Ids)
    cdef unsigned long sp2ToRemoveCnt = len(toRemoveSp2Ids)
    cdef unsigned long orthoToRemoveCnt = sp1ToRemoveCnt + sp2ToRemoveCnt
    cdef cnp.ndarray[cnp.float32_t, ndim=1] tmpScArray
    tmpScList: list[float] = []
    cdef dict avgCosineVals

    if (sp1ToRemoveCnt == sp1OrthoCnt) or (sp2ToRemoveCnt == sp2OrthoCnt):
        # print(f"Promote to ignore cluster:{aClstrId}")
        # ignoreClstr = 1
        return clusterModOutcome

    # return an interger describing the state of the cluster
    # 0 -> reject
    if ignoreClstr:
        # return (0, aClstrId)
        return clusterModOutcome

    # 1 -> add with modifications (remove only some orthologs)
    elif (orthoToRemoveCnt) != 0:
        # print(f"Original Arch cluster:\n{tmpAclstr}")
        # Reuse the cluster size variable
        aClstrSize = aClstrSize - orthoToRemoveCnt

        # Extract the IDs for Sp1
        if sp1ToRemoveCnt > 0:
            for i in range(sp1OrthoCnt):
                if i not in toRemoveSp1Ids:
                    # print(f"sp1 keep:\t{aSp1IdsView[i]}")
                    newSp1Ids.append(aSp1IdsView[i])
                    tmpScArray = cosineValsList[i]
                    newSp1Scores.append(tmpScArray)
        # Keep the original ids
        else:
            newSp1Ids = list(aSp1IdsView)
            newSp1Scores = cosineValsList

        # Extract the IDs for Sp2
        if sp2ToRemoveCnt > 0:
            for i in range(sp2OrthoCnt):
                if i not in toRemoveSp2Ids:
                    # print(f"sp2 keep:\t{aSp2IdsView[i]}")
                    newSp2Ids.append(aSp2IdsView[i])
            # sp1 scoresList needs to be pruned as well
            for i in range(len(newSp1Scores)):
                # print(type(newSp1Scores[i]))
                tmpScArray = newSp1Scores[i]
                for j in range(tmpScArray.shape[0]):
                    if j not in toRemoveSp2Ids:
                        tmpScList.append(tmpScArray[j])
                newSp1Scores[i] = np.array(tmpScList, dtype=np.float32)
                tmpScList.clear()
        # Keep the original ids
        else:
            newSp2Ids = list(aSp2IdsView)

        # Compute the arrays with the average cosine similarities
        # to be added to the graph-based cluster
        avgCosineVals = compute_avg_cosine_scores(newSp1Scores, sp1OrthoCnt - sp1ToRemoveCnt, sp2OrthoCnt - sp2ToRemoveCnt)
        # Make sure it would not overwrite other clusters
        # if newClstrId in mClstrDict:
        #     sys.exit(f"The cluster ID {newClstrId} already exists in the Master Cluster dictionary.")
        # Add the new cluster
        mClstrDict[newClstrId] = MergedClstr(aClstrSize, np.array(newSp1Ids, dtype=np.uint32), np.array(newSp2Ids, dtype=np.uint32), avgCosineVals[0], avgCosineVals[1])
        # print(f"New (modified) Graph-cluster [ID: {newClstrId}]:\n{mClstrDict[newClstrId]}")
        clusterModOutcome = (1, newClstrId)

    # 2 -> add the cluster as it is
    else:
        # print(f"\nOriginal Arch cluster:\n{tmpAclstr}")
        # Compute the average cosine values
        avgCosineVals = compute_avg_cosine_scores(cosineValsList, sp1OrthoCnt, sp2OrthoCnt)
        # Make sure it would not overwrite other clusters
        # if newClstrId in mClstrDict:
        #     sys.exit(f"The cluster ID {newClstrId} already exists in the Master Cluster dictionary.")
        # Add the new cluster
        mClstrDict[newClstrId] = MergedClstr(aClstrSize, np.asarray(aSp1IdsView), np.asarray(aSp2IdsView), avgCosineVals[0], avgCosineVals[1])
        # print(f"New (Graph-cluster [ID: {newClstrId}]:\n{mClstrDict[newClstrId]}")
        clusterModOutcome = (2, newClstrId)

    return clusterModOutcome



cdef inline (unsigned long, unsigned long) integrate_new_arch_orthologs_into_g_clstr(unsigned long sp1OrthoCnt, unsigned long sp2OrthoCnt, cnp.uint32_t[:] aSpxNewIdsView,  cnp.uint32_t[:] aSpxContainedIdsView, list cosineValsList, dict mClstrDict, dict archMasterDict, unsigned long spxId, dict graphSpxOrtho2info2Use, dict graphSpxOrtho2info2Mod, bint sp1HasNewMembers, double covThr):
    '''
    Add new arch-based orthologs into a G cluster with.
    This handles cases in which the Arch cluster has size > 2.
    Based on multiple conditions integrate the new arch-based orthologs into clusters already in G.
    '''

    cdef size_t i # Indexes to be used in for loops
    cdef unsigned long gClstrId
    cdef bint ignoreClstr = 0
    # Sentinel to remember the next writeable position in array
    cdef unsigned long arrayIdxSentinel = 0
    cdef unsigned long newOrthologsCnt = aSpxNewIdsView.shape[0]
    cdef unsigned long newOrthoToAddCnt = 0
    cdef unsigned long containedInGorthoCnt = aSpxContainedIdsView.shape[0]
    cdef (unsigned long, double) tmpGorthoInfo
    aContainedSet: set[int] = set()
    # buffer arrays used to modify merged clusters
    cdef cnp.uint32_t[:] gSpxOrthologs
    cdef cnp.float32_t[:] gSpxScores
    cdef unsigned long gSpxOrthoCnt
    cdef cnp.ndarray[cnp.uint32_t, ndim=1] newGSpxOrthologs
    cdef cnp.ndarray[cnp.float32_t, ndim=1] newGSpxScores
    cdef cnp.float32_t[:] aSpxAvgScores
    cdef double cosine
    # Indexes of new orthologs to be added
    cdef cnp.ndarray[cnp.uint8_t, ndim=1] newToAddIdxs
    cdef bint oldInMultipleGclstrs = 0
    cdef double spxArchCov = 0.0
    tmpSpxArch: Arch = Arch(0, 0.0, 0, 0, np.zeros(0, dtype=np.uint32), np.zeros(0, dtype=np.uint32), np.zeros(0, dtype=np.uint32), np.array(["sp1"], dtype=np.str_), np.zeros(0, dtype=np.float32), 1)
    # Merged cluster to be used for modification
    tmpMclstr: MergedClstr = MergedClstr(0, np.array(0, dtype=np.uint32), np.array(0, dtype=np.uint32), np.array(0, dtype=np.float32), np.array(0, dtype=np.float32))
    # Output tuple from the function
    cdef (unsigned long, unsigned long) clusterModOutcome

    # print(f"\nsp1OrthoCnt:\t{sp1OrthoCnt}")
    # print(f"sp2OrthoCnt:\t{sp2OrthoCnt}")
    # print(f"Contained in G:\t{containedInGorthoCnt}")

    # sys.exit("\nDEBUG: ortho_merger.pyx :: integrate_new_arch_orthologs_into_g_clstr :: before main loop")

    # Do different things depending on the number
    # of orthologs in G and if they are in different clusters
    if containedInGorthoCnt > 1:
        # print(f"Contained in G > 1:\t{containedInGorthoCnt}")
        # Check if all the contained clusters are
        # in the same cluster in G
        for i in range(containedInGorthoCnt):
            # tmpOrthoId = aSpxContainedIdsView[i]
            # print(f"i:\t{i}")
            # print(f"aSpxContainedIdsView[i]:\t{aSpxContainedIdsView[i]}")

            tmpGorthoInfo = graphSpxOrtho2info2Use[aSpxContainedIdsView[i]]

            # Insert the cluster ID in set
            aContainedSet.add(tmpGorthoInfo[0])
        # Reject the new orthologs they scattered in different clusters in G
        if len(aContainedSet) > 1:
            oldInMultipleGclstrs = 1
            # print(aContainedSet)
            # sys.exit("DEBUG: contained clusters (in Sp1) in different clusters")

        # Do different things depending if contained ortholog are in scattered
        # in multiple clusters in G
        if oldInMultipleGclstrs:
            ignoreClstr = 1
            # print(f"Reject ortholog contained in multiple G clusters:\t{aContainedSet}")
            # HACK: for now we just reject it,
            # but in the future we could choose a cluster
            # to which we add the new orhtolog
            # many-to-1 case (single orhtolog to add)
            # if newOrthologsCnt == 1:
            #     print(f"scattered in G: many-to-1 ({newOrthologsCnt} new orthologs)")
                # NOTE: An option could be to add the orthologs to the G cluster 
                # where the ortholog with the highest cosine is in
                # sys.exit("DEBUG")
            # many-to-many case (multiple new orhtologs to add)
            # else:
            #     print(f"scattered in G: many-to-many ({newOrthologsCnt} new orthologs)")
                # pass
                # sys.exit("DEBUG")

        # The orthologs already contained in G are all in the same cluster
        else:
            tmpGorthoInfo = graphSpxOrtho2info2Use[aSpxContainedIdsView[0]]
            # many-to-1 case (single orhtolog to add)
            if newOrthologsCnt == 1:
                # print(f"All in the same G cluster: many-to-1 ({newOrthologsCnt} new ortholog)")
                # Extract arch info for the new ortholog
                tmpSpxArch = archMasterDict[spxId][aSpxNewIdsView[0]]
                spxArchCov = getattr(tmpSpxArch, "coverage")
                # print(tmpSpxArch)
                # print(f"cov_new:\t{spxArchCov:.4f}")
                # Reject the pair if the coverage is lower than covThr
                if spxArchCov < covThr:
                    # print(f"Reject low coverage arch-orholog (min coverage={covThr:.2f}):\t{spxArchCov}")
                    # print(f"{sp1Id}.{aSp1IdsView[0]}\t{sp2Id}.{aSp2IdsView[0]}")
                    ignoreClstr = 1
                else:
                    # print(f"G cluster containing the old ortholog:{tmpGorthoInfo}")
                    gClstrId = tmpGorthoInfo[0]
                    tmpMclstr = mClstrDict[gClstrId]
                    # Extract the information required to modify the merged cluster
                    gClstrSize = getattr(tmpMclstr, "size")

                    # Modify the sp1 part of the merged cluster
                    if sp1HasNewMembers:
                        gSpxOrthologs = getattr(tmpMclstr, "sp1Ids")
                        gSpxOrthoCnt = gSpxOrthologs.shape[0]
                        gSpxScores = getattr(tmpMclstr, "sp1Scores")
                        # print(np.frombuffer(gSpxOrthologs, dtype=np.uint32))
                        # print(np.frombuffer(gSpxScores, dtype=np.float32))
                        cosine = compute_avg_cosine_scores(cosineValsList, sp1OrthoCnt, sp2OrthoCnt)[0][0]
                    # Modify the sp2 part of the merged cluster
                    else:
                        gSpxOrthologs = getattr(tmpMclstr, "sp2Ids")
                        gSpxOrthoCnt = gSpxOrthologs.shape[0]
                        gSpxScores = getattr(tmpMclstr, "sp2Scores")
                        # print(np.frombuffer(gSpxOrthologs, dtype=np.uint32))
                        # print(np.frombuffer(gSpxScores, dtype=np.float32))
                        cosine = compute_avg_cosine_scores(cosineValsList, sp1OrthoCnt, sp2OrthoCnt)[1][0]

                    # inizialize the new arrays
                    newGSpxOrthologs = np.zeros(gSpxOrthoCnt + 1, dtype=np.uint32)
                    newGSpxScores = np.zeros(gSpxOrthoCnt + 1, dtype=np.float32)
                    # print(f"Buffer arrays:\n{newGSpxOrthologs}\n{newGSpxScores}")
                    # Fill the arrays with the old values
                    for i in range(gSpxOrthoCnt):
                        newGSpxOrthologs[i] = gSpxOrthologs[i]
                        newGSpxScores[i] = gSpxScores[i]
                    # update the gcluster size
                    gClstrSize += 1
                    # Now add the new ortholog and score
                    newGSpxOrthologs[gSpxOrthoCnt] = aSpxNewIdsView[0]
                    newGSpxScores[gSpxOrthoCnt] = cosine
                    # print(newGSpxOrthologs)
                    # print(newGSpxScores)

                    # update graphSp1Ortho2info
                    # DEBUG ONLY
                    '''
                    if aSpxNewIdsView[0] in graphSpxOrtho2info2Mod:
                        sys.exit("This should never happen!")
                    '''
                    graphSpxOrtho2info2Mod[aSpxNewIdsView[0]] = (gClstrId, cosine)

                    # Finally modify the cluster
                    if sp1HasNewMembers:
                        mClstrDict[gClstrId] = MergedClstr(gClstrSize, newGSpxOrthologs, getattr(tmpMclstr, "sp2Ids"), newGSpxScores, getattr(tmpMclstr, "sp2Scores"))
                        # print(f"UPDATED G cluster {gClstrId} (Sp1 side)\n{mClstrDict[gClstrId]}")
                        # sys.exit("DEBUG (Sp1 side modified)")
                    else:
                        mClstrDict[gClstrId] = MergedClstr(gClstrSize, getattr(tmpMclstr, "sp1Ids"), newGSpxOrthologs, getattr(tmpMclstr, "sp1Scores"), newGSpxScores)
                        # print(f"UPDATED G cluster {gClstrId} (Sp2 side)\n{mClstrDict[gClstrId]}")
                        # sys.exit("DEBUG (Sp2 side modified)")

            # many-to-many case (multiple orhtolog to add)
            else:
                # print(f"All in same G cluster: many-to-many ({newOrthologsCnt} new orthologs)")
                # HACK: in the future we might also consider to
                # filter orthologs based on the graph-scores of already contained orthologs
                tmpGorthoInfo = graphSpxOrtho2info2Use[aSpxContainedIdsView[0]]
                # print(tmpGorthoInfo)

                # NOTE: simple case
                newToAddIdxs = np.zeros(newOrthologsCnt, dtype=np.uint8)

                # add each new orthlog based on the coverage
                for i in range(newOrthologsCnt):
                    # print(aSpxNewIdsView[i])
                    # extract the coverage
                    tmpSpxArch = archMasterDict[spxId][aSpxNewIdsView[i]]
                    spxArchCov = getattr(tmpSpxArch, "coverage")
                    # Accept if above coverage
                    if spxArchCov >= covThr:
                        newToAddIdxs[i] = 1
                    # else:
                    #     print(f"Reject new ortholog {spxId}.{aSpxNewIdsView[i]} because of low coverage ({spxArchCov:.2f})")

                # The will actually be added to the G cluster
                newOrthoToAddCnt = sum_bint_array(newToAddIdxs)

                # Reject if all new orthologs have low coverages
                if newOrthoToAddCnt == 0:
                    ignoreClstr = 1
                    # print("Rejected many-to-many case")
                    # sys.exit("DEBUG")
                else:
                    # print(f"G cluster containing the old ortholog:{tmpGorthoInfo}")
                    gClstrId = tmpGorthoInfo[0]
                    tmpMclstr = mClstrDict[gClstrId]
                    # Extract the information required to modify the merged cluster
                    gClstrSize = getattr(tmpMclstr, "size")

                    # Modify the sp1 part of the merged cluster
                    if sp1HasNewMembers:
                        gSpxOrthologs = getattr(tmpMclstr, "sp1Ids")
                        gSpxOrthoCnt = gSpxOrthologs.shape[0]
                        gSpxScores = getattr(tmpMclstr, "sp1Scores")
                        # print(np.frombuffer(gSpxOrthologs, dtype=np.uint32))
                        # print(np.frombuffer(gSpxScores, dtype=np.float32))
                        aSpxAvgScores = compute_avg_cosine_scores(cosineValsList, sp1OrthoCnt, sp2OrthoCnt)[0]
                    # Modify the sp2 part of the merged cluster
                    else:
                        gSpxOrthologs = getattr(tmpMclstr, "sp2Ids")
                        gSpxOrthoCnt = gSpxOrthologs.shape[0]
                        gSpxScores = getattr(tmpMclstr, "sp2Scores")
                        # print(np.frombuffer(gSpxOrthologs, dtype=np.uint32))
                        # print(np.frombuffer(gSpxScores, dtype=np.float32))
                        aSpxAvgScores = compute_avg_cosine_scores(cosineValsList, sp1OrthoCnt, sp2OrthoCnt)[1]

                    # inizialize the new arrays
                    newGSpxOrthologs = np.zeros(gSpxOrthoCnt + newOrthoToAddCnt, dtype=np.uint32)
                    newGSpxScores = np.zeros(gSpxOrthoCnt + newOrthoToAddCnt, dtype=np.float32)

                    # Fill the arrays with the old values
                    for i in range(gSpxOrthoCnt):
                        newGSpxOrthologs[i] = gSpxOrthologs[i]
                        newGSpxScores[i] = gSpxScores[i]
                    # print(f"Buffer arrays (UPDATE 1):\n{newGSpxOrthologs}\n{newGSpxScores}")

                    # initialize the write sentinel
                    arrayIdxSentinel = gSpxOrthoCnt
                    # Add the new orhtologs and scores
                    for i in range(newOrthologsCnt):
                        if newToAddIdxs[i] == 1:
                            newGSpxOrthologs[arrayIdxSentinel] = aSpxNewIdsView[i]
                            newGSpxScores[arrayIdxSentinel] = aSpxAvgScores[i]

                            # Update the dictionary with ortholog information
                            ''' DEBUG ONLY
                            if aSpxNewIdsView[i] in graphSpxOrtho2info2Mod:
                                # print(f"Repeated:\t{aSpxNewIdsView[i]}")
                                # print(mClstrDict[graphSpxOrtho2info[aSpxNewIdsView[i]]])
                                # print(graphSpxOrtho2info2Mod[aSpxNewIdsView[i]])
                                # print(f"Cluster containing current old orthologs:\t{gClstrId}")
                                sys.exit("This should never happen, as it was a new ortholog!")
                            '''
                            graphSpxOrtho2info2Mod[aSpxNewIdsView[i]] = (gClstrId, aSpxAvgScores[i])
                            arrayIdxSentinel += 1

                    # print(f"Buffer arrays (UPDATE 2):\n{newGSpxOrthologs}\n{newGSpxScores}")
                    # update the gcluster size
                    gClstrSize += newOrthoToAddCnt
                    # print(f"New cluster size:\n{gClstrSize}")
                    # Finally modify the cluster
                    if sp1HasNewMembers:
                        mClstrDict[gClstrId] = MergedClstr(gClstrSize, newGSpxOrthologs, getattr(tmpMclstr, "sp2Ids"), newGSpxScores, getattr(tmpMclstr, "sp2Scores"))
                        # print(f"UPDATED G cluster {gClstrId} (Sp1 side)\n{mClstrDict[gClstrId]}")
                        # sys.exit("DEBUG (Sp1 side modified)")
                    else:
                        mClstrDict[gClstrId] = MergedClstr(gClstrSize, getattr(tmpMclstr, "sp1Ids"), newGSpxOrthologs, getattr(tmpMclstr, "sp1Scores"), newGSpxScores)
                        # print(f"UPDATED G cluster {gClstrId} (Sp2 side)\n{mClstrDict[gClstrId]}")
                        # sys.exit("DEBUG (Sp2 side modified)")
    # The ortholog already contained is only one
    else:
        # print(f"Only 1 ortholog in G: many-to-1 ({newOrthologsCnt} new orthologs)")
        tmpGorthoInfo = graphSpxOrtho2info2Use[aSpxContainedIdsView[0]]
        # NOTE: simple case
        newToAddIdxs = np.zeros(newOrthologsCnt, dtype=np.uint8)

        # add each new orthlog based on the coverage
        for i in range(newOrthologsCnt):
            # extract the coverage
            tmpSpxArch = archMasterDict[spxId][aSpxNewIdsView[i]]
            spxArchCov = getattr(tmpSpxArch, "coverage")
            # Accept if above coverage
            if spxArchCov >= covThr:
                newToAddIdxs[i] = 1
            # else:
            #     print(f"Reject new ortholog {spxId}.{aSpxNewIdsView[i]} because of low coverage ({spxArchCov:.2f})")

        # The number of orthologs that
        # will eventually be added to the G cluster
        newOrthoToAddCnt = sum_bint_array(newToAddIdxs)
        # Reject if al new orthologs have low coverages
        if newOrthoToAddCnt == 0:
            ignoreClstr = 1
        else:
            # print(f"G cluster containing the old ortholog:{tmpGorthoInfo}")
            gClstrId = tmpGorthoInfo[0]
            tmpMclstr = mClstrDict[gClstrId]
            # Extract the information required to modify the merged cluster
            gClstrSize = getattr(tmpMclstr, "size")
            # Modify the sp1 part of the merged cluster
            if sp1HasNewMembers:
                gSpxOrthologs = getattr(tmpMclstr, "sp1Ids") # could be a array view
                gSpxOrthoCnt = gSpxOrthologs.shape[0]
                gSpxScores = getattr(tmpMclstr, "sp1Scores") # could a array view
                # print(np.frombuffer(gSpxOrthologs, dtype=np.uint32))
                # print(np.frombuffer(gSpxScores, dtype=np.float32))
                aSpxAvgScores = compute_avg_cosine_scores(cosineValsList, sp1OrthoCnt, sp2OrthoCnt)[0]
            # Modify the sp2 part of the merged cluster
            else:
                gSpxOrthologs = getattr(tmpMclstr, "sp2Ids") # could be a array view
                gSpxOrthoCnt = gSpxOrthologs.shape[0]
                gSpxScores = getattr(tmpMclstr, "sp2Scores") # could a array view
                # print(np.frombuffer(gSpxOrthologs, dtype=np.uint32))
                # print(np.frombuffer(gSpxScores, dtype=np.float32))
                aSpxAvgScores = compute_avg_cosine_scores(cosineValsList, sp1OrthoCnt, sp2OrthoCnt)[1]

            # inizialize the new arrays
            newGSpxOrthologs = np.zeros(gSpxOrthoCnt + newOrthoToAddCnt, dtype=np.uint32)
            newGSpxScores = np.zeros(gSpxOrthoCnt + newOrthoToAddCnt, dtype=np.float32)
            # print(f"Buffer arrays:\n{newGSpxOrthologs}\n{newGSpxScores}")

            # Fill the arrays with the old values
            for i in range(gSpxOrthoCnt):
                newGSpxOrthologs[i] = gSpxOrthologs[i]
                newGSpxScores[i] = gSpxScores[i]
            # print(f"Buffer arrays (UPDATE 1):\n{newGSpxOrthologs}\n{newGSpxScores}")

            # Initialize the write sentinel
            arrayIdxSentinel = gSpxOrthoCnt
            # Add the new orhtologs and scores
            for i in range(newOrthologsCnt):
                if newToAddIdxs[i] == 1:
                    newGSpxOrthologs[arrayIdxSentinel] = aSpxNewIdsView[i]
                    newGSpxScores[arrayIdxSentinel] = aSpxAvgScores[i]
                    # Update the dictionary with ortholog information
                    ''' # DEBUG ONLY
                    if aSpxNewIdsView[i] in graphSpxOrtho2info2Mod:
                        print(f"Repeated:\t{aSpxNewIdsView[i]}")
                        # print(mClstrDict[graphSpxOrtho2info[aSpxNewIdsView[i]]])
                        print(graphSpxOrtho2info2Mod[aSpxNewIdsView[i]])
                        print(f"Cluster containing current old orthologs:\t{gClstrId}")
                        sys.exit("This should never happen, as it was a new ortholog!")
                    '''
                    graphSpxOrtho2info2Mod[aSpxNewIdsView[i]] = (gClstrId, aSpxAvgScores[i])
                    arrayIdxSentinel += 1

            # print(f"Buffer arrays (UPDATE 2):\n{newGSpxOrthologs}\n{newGSpxScores}")
            # update the gcluster size
            gClstrSize += newOrthoToAddCnt
            # print(f"New cluster size:\n{gClstrSize}")

            # Finally modify the cluster
            if sp1HasNewMembers:
                mClstrDict[gClstrId] = MergedClstr(gClstrSize, newGSpxOrthologs, getattr(tmpMclstr, "sp2Ids"), newGSpxScores, getattr(tmpMclstr, "sp2Scores"))
                # print(f"UPDATED G cluster {gClstrId} (Sp1 side)\n{mClstrDict[gClstrId]}")
                # sys.exit("DEBUG (Sp1 side modified)")
            else:
                mClstrDict[gClstrId] = MergedClstr(gClstrSize, getattr(tmpMclstr, "sp1Ids"), newGSpxOrthologs, getattr(tmpMclstr, "sp1Scores"), newGSpxScores)
                # print(f"UPDATED G cluster {gClstrId} (Sp2 side)\n{mClstrDict[gClstrId]}")
                # sys.exit("DEBUG (Sp2 side modified)")

    # sys.exit("\nDEBUG: ortho_merger.pyx :: integrate_new_arch_orthologs_into_g_clstr")
    if ignoreClstr:
        clusterModOutcome = (0, 0)
        return clusterModOutcome

    clusterModOutcome = (1, gClstrId)
    return clusterModOutcome



# @cython.cdivision(True) # Use C division instead of Python division
# @cython.boundscheck(False) # Check array bounds
cdef inline list process_arch_ortho_subgroup(bytes subgrp):
    """
        Split a subgroup of arch-based ortholog.

        Returns a dictionary that associates a protein (as int) to a score (as double)
    """
    # print("process_arch_ortho_subgroup :: START")

    cdef long gene
    cdef size_t i # Indexes to be used in for loops
    flds: list[bytes] = subgrp.split(b" ")
    geneIds: list[int] = []
    cdef bytes rawGeneId
    cdef unsigned long grpSize = len(flds)

    # Extract the gene names and scores
    # Subgroups of a arch based cluster have the following format
    # 0.96 23.1395 33.380
    # 1.00 23.1322 23.1861 33.12914
    for i in range(grpSize):
        # rawGeneId = flds.pop() # works, but genes order is different to that in TSV
        rawGeneId = flds[i]
        gene = atol(rawGeneId.split(b".", 1)[1])
        geneIds.append(gene)

    # Return the list with ortholog IDs
    return geneIds



cdef inline dict remove_contained_in_g(cnp.uint32_t[:] aSpxMixedIdsView, cnp.float32_t[:] aSpxMixedGraphAvgScores, cnp.uint8_t[:] aSpxContainedIdxsView, unsigned long aSpxMixedOrthoCnt, unsigned long aSpxContainedCnt):
    """
    Remove orthologs that are already contained in G clusters.
    """

    # Create the arrays to be returned
    cdef unsigned long outArrayLen = aSpxMixedOrthoCnt - aSpxContainedCnt
    cdef cnp.ndarray[cnp.uint32_t, ndim=1] aSpxModIds = np.zeros(outArrayLen, dtype=np.uint32)
    cdef cnp.ndarray[cnp.float32_t, ndim=1] aSpxModGraphAvgScores = np.zeros(outArrayLen, dtype=np.float32)
    # Counters
    cdef size_t i
    cdef unsigned long modOrthoCnt = 0
    cdef unsigned long tmpOrthoId

    # Returns a dictionary with the modified dictionaries
    # print(f"remove_contained_in_g :: START")
    # print("Remove contained in G from A.")
    # print(f"Mixed view:\t{np.asarray(aSpxMixedIdsView)}")
    # print(f"Mixed avg scores:\t{np.asarray(aSpxMixedGraphAvgScores)}")
    # print(f"Mixed contained idxs:\t{np.asarray(aSpxContainedIdxsView)}")
    # print(f"Mixed orhto cnt:\t{aSpxMixedOrthoCnt}")
    # print(f"Mixed contained cnt:\t{aSpxContainedCnt}")

    # Create arrays containing protein IDs
    # and avg scores of new orhtologs
    for i in range(aSpxMixedOrthoCnt):
        if aSpxContainedIdxsView[i] == 0:
            tmpOrthoId = aSpxMixedIdsView[i]
            aSpxModIds[modOrthoCnt] = tmpOrthoId
            aSpxModGraphAvgScores[modOrthoCnt] = aSpxMixedGraphAvgScores[i]
            modOrthoCnt += 1

    # The output dictionary will contain
    # 0 -> array with the remaining protein IDs (after removing the contained ones)
    # 1 -> array with average scores remaining new protein IDs
    return {0:aSpxModIds, 1:aSpxModGraphAvgScores}



# @cython.boundscheck(False) # Check array bounds
# @cython.profile(False)
cdef inline dict remove_repeaded_arch_orthologs(dict aClstrDict, dict sp1Rep2Clstr) except *:
    """
        Remove repeated arch-orthologs from previously generated arch-based clusters.

        Returns a modified version of the input dict of clusters.
    """

    cdef bint debug = 0
    '''
    debugStr: str = f"""remove_repeaded_arch_orthologs :: START
    Clusters:\t{len(aClstrDict)}
    Repeated orthologs from Sp1:\t{len(sp1Rep2Clstr)}"""
    logger.info(debugStr)
    '''

    # FIXME: not really an error,
    # but it is possible that 2 different repetitions
    # have exactly the same cosine similarity with orthologs from Sp2.
    # In such cases the first max found will be kept.
    # A more complex solution to this exception
    # could be keeping the repeats in the clusters
    # with the highest average cosine similarity
    # Multiple clusters with repats with cosine = 1.0
    # Should be merged in a single high-quality cluster containing
    # only relations with score 1.0

    # Examples of repeated orthologs for
    # Ecoli (species ID 23) and Hsapiens (species ID 33)
    # 0.96:0.96:0.80:0.96 23.1967 23.3852 23.3875 23.4323 33.16736
    # 0.87,0.87:0.87,0.87 23.1967 23.3852 33.3930 33.6641
    # 0.94:0.99:0.99 23.1607 23.1967 23.3852 33.5922

    # in the above example 23.1967 is repeated.
    # As a general rule, keeping the ortholog
    # With the highest cosine value should suffice
    # In the above case the highest cosine value
    # for 23.1967 the highest value is cosine(23.1967, 33.5922) = 0.99 in the third cluster
    # 23.1967 should then be removed from the other 2 clusters

    # Tmp vars
    # cdef unsigned int pairsCnt = 0
    cdef unsigned long prevClstrCnt = len(aClstrDict)
    cdef unsigned long newClstrCnt = 0
    cdef unsigned long totRepeated = len(sp1Rep2Clstr)
    cdef unsigned long clstrSize
    cdef unsigned long tmpPairsCnt
    cdef unsigned long clstrsToProcess
    cdef unsigned long tmpOrthoId
    cdef unsigned long tmpClstrId
    cdef unsigned long tmpOrthoIdx = 0 # initiliazed to hanled cython warning
    cdef unsigned long tmpSp1ClstrSize
    cdef unsigned long tmpSp2ClstrSize
    # Contains the indexes at which the repeated ortholog was found
    tmpOrthoIdxs: list[int] = []
    # This dict contains information on the clusters
    # and the position in which the repetion happens
    # The tuple will contain the following information
    # 1: number of ortho from sp1 in the original cluster
    # 2: number of ortho from sp2 in the original cluster
    # 3: original number of pairs in cluster
    # 4: list of indexes in sp1Ids of the proteins (and scores)
    # that should be remove from the cluster
    clstrsToRemove: dict[int, tuple[int, int, int, list[int]]] = {}
    # This dict contains information on the clusters
    # and the position in which the repetion happens
    # The tuple will contain the following information
    # 1: number of ortho from sp1 in the original cluster
    # 2: number of ortho from sp2 in the original cluster
    # 3: original number of pairs in cluster
    # 4: index in sp1Ids of the protein (and scores)
    # that should be removed from the cluster
    # NOTE: this will only contain the information regarding a single
    # repeated protein, and will be used to update the dictionary clstrsToRemove
    repeatsToRemove: dict[int, tuple[int, int, int, int]] = {}
    # Index of the clusters that should be kept
    # namely the one with the highest score for the current repetition
    cdef unsigned long rep2keepClstrIdx = 0
    cdef double localMaxCosine
    cdef double tmpCosine
    # Indicates if the second part of the cluster has more than one ortholog
    cdef size_t i, j, viewIdx, scoreIdx # Indexes to be used in for loops
    # memory views for temporary vectors with scores and ids
    cdef cnp.uint32_t[:] sp1IdsView
    cdef cnp.float32_t[:] sp1OrthoScoresView
    # Will contain the arrays of doubles
    # with the cosine similarities
    sp1RepeatList: list[int] = list(sp1Rep2Clstr.keys())
    # clstrsWithReps: list[int] = []
    cdef list clstrsWithReps = []
    # This will contain a temporary cluster
    tmpClstr: ArchClstr = ArchClstr(0, np.zeros(0, dtype=np.uint32), np.zeros(0, dtype=np.uint32), clstrsWithReps)

    ''' DEBUG ONLY
    print("OrthoId\Clusters containing it:")
    tmpOrthoIdxs = list(sp1Rep2Clstr.keys())
    tmpOrthoIdxs.sort()
    for k in tmpOrthoIdxs:
        print(f"{k}:\t{sp1Rep2Clstr[k]}")
    logging.warning("Debugging... (before repeat-to-cluster processing)")
    sys.exit(-20)
    '''

    # For each ortholog with repetition
    for i in range(totRepeated):
        tmpOrthoId = sp1RepeatList.pop()
        clstrsWithReps = sp1Rep2Clstr.pop(tmpOrthoId, None)
        clstrsToProcess = len(clstrsWithReps)
        # print(f"\nOrtho ID\Clusters containing it:\t{tmpOrthoId}\t{clstrsWithReps}")
        # print(sys.exit("DEBUG"))
        # Find the cluster in which tmpOrthoId is repeated which has the Max cosine score
        for j in range(clstrsToProcess):
             # We will reuse the the indexes in this list
            tmpClstrId = clstrsWithReps[j]
            tmpClstr = aClstrDict[tmpClstrId]
            # print(f"\n## cluster {tmpClstrId}:\n{tmpClstr}")
            clstrSize = getattr(tmpClstr, "size")

            # Extraction of the score is simpler
            # if it is a 1-to-1 relation
            if clstrSize == 2:
                localMaxCosine = getattr(tmpClstr, "cosineValues")[0][0]
                # print(f"Local max cosine:\t{localMaxCosine}")
                tmpOrthoIdx = 0
                tmpSp1ClstrSize = 1
                tmpSp2ClstrSize = 1
            else:
                # This scenario is more complicated and we need to do the following:
                # 1) Identify the index in the array in which our ortholog (tmpOrthoId) is stored in sp1Ids
                # 2) Find the max score for tmpOrthoId in the list of arrays with scores (cosineValues)
                sp1IdsView = getattr(tmpClstr, "sp1Ids")
                tmpSp1ClstrSize = sp1IdsView.shape[0]
                tmpSp2ClstrSize = clstrSize - tmpSp1ClstrSize

                for viewIdx in range(tmpSp1ClstrSize):
                    # print(f"viewIdx\Current sp1 ID:\t{viewIdx}\t{sp1IdsView[viewIdx]}")
                    if sp1IdsView[viewIdx] == tmpOrthoId:
                        tmpOrthoIdx = viewIdx
                        # Obtain a view of the array with the scores
                        sp1OrthoScoresView = getattr(tmpClstr, "cosineValues")[viewIdx]
                        # Compute the local maxium cosine value if there are multiple values
                        if sp1OrthoScoresView.shape[0] == 1:
                            localMaxCosine = sp1OrthoScoresView[0]
                        # Compute the maximum of all cosine values
                        else:
                            for scoreIdx in range(sp1OrthoScoresView.shape[0]):
                                tmpCosine = sp1OrthoScoresView[scoreIdx]
                                if tmpCosine > localMaxCosine:
                                    localMaxCosine = tmpCosine
                        # print(f"Local max cosine:\t{localMaxCosine}")
                        break

            # Add indexes to the dictionary with info on proteins that should be removed
            repeatsToRemove[tmpClstrId] = (tmpSp1ClstrSize, tmpSp2ClstrSize, tmpSp1ClstrSize * tmpSp2ClstrSize, tmpOrthoIdx)
            # Check that there is only cluster
            # where the repetion has cosine == 1.0
            # TODO: Clusters in that have the same repeat
            # with scores of 1.0 should ideally be merged
            # The safest solution would be to keep only pairs with score of 1.0
            # And create a clusters with scores of 1.0 only
            ''' FIXME: handle this exception when 
            # using only arch-based predictions
            if localMaxCosine == tmpMaxCosine == 1.0:
                print(f"Two cosine of 1.0 for same repeat:\t{tmpClstrId}\t{tmpOrthoId}\nThis should not happen!")
                logging.error("This should not happen!")
                sys.exit(-50)
            '''
            # Update the max cosine value
            if localMaxCosine > tmpMaxCosine: # Allow last MAX to be kept
                tmpMaxCosine = localMaxCosine
                # print(f"Updated max cosine for {tmpOrthoId}:\t{tmpMaxCosine}")
                rep2keepClstrIdx = tmpClstrId
            # reset the local Max value
            localMaxCosine = 0

        # Remove the cluster with highest cosine from those that should be removed
        del repeatsToRemove[rep2keepClstrIdx]

        # Update the master dictionary containing info
        # on the clusters that should be modified/removed
        clstrsWithReps = list(repeatsToRemove.keys())
        clstrsToProcess = len(clstrsWithReps)
        for j in range(clstrsToProcess):
            tmpClstrId = clstrsWithReps.pop()
            tmpSp1ClstrSize, tmpSp2ClstrSize, tmpPairsCnt, tmpOrthoIdx = repeatsToRemove.pop(tmpClstrId)
            # Update the dictionary with the clusters that should be removed
            if tmpClstrId in clstrsToRemove:
                # logger.warning(f"Cluster {tmpClstrId} (with ortholog {tmpOrthoId}) was already in the list of those to be removed!")
                # Add index of the current ortholog to the list
                # with idxs that should be removed
                tmpOrthoIdxs = clstrsToRemove[tmpClstrId][3]
                tmpOrthoIdxs.append(tmpOrthoIdx)
                clstrsToRemove[tmpClstrId] = (tmpSp1ClstrSize, tmpSp2ClstrSize, tmpPairsCnt, tmpOrthoIdxs.copy())
            # Add a new entry in the dictionary
            # with clusters to be removed
            else:
                clstrsToRemove[tmpClstrId] = (tmpSp1ClstrSize, tmpSp2ClstrSize, tmpPairsCnt, [tmpOrthoIdx])

        # Empty the list with indexes of sp1Ids
        tmpOrthoIdxs.clear()
        tmpMaxCosine = 0.0
        repeatsToRemove.clear()
        rep2keepClstrIdx = 0

    # Remove not unused variables
    del repeatsToRemove, sp1RepeatList

    ''' DEBUG ONLY
    # Print clusters to be removed
    print("\nClusters to be removed/modified:")
    clstrIdList: list[int] = list(clstrsToRemove.keys())
    clstrIdList.sort()
    for k in clstrIdList:
        print(f"{k}:\t{clstrsToRemove[k]}")

    logging.warning("Debugging... (After identification of clusters to be removed/modified)")
    sys.exit(-20)
    '''

    # Update the original cluster
    # remove complete clusters if needed
    clstrsWithReps = list(clstrsToRemove.keys())
    clstrsWithReps.sort()
    clstrsToProcess = len(clstrsWithReps)
    cdef unsigned long removedClstrCnt = 0
    cdef unsigned long removedPairsCnt = 0
    cdef unsigned long repToRemoveCnt = 0
    cdef unsigned long newClstrSize = 0
    cdef unsigned long currentListLen = 0
    # Variables that will contain the new info
    # To insert in the modified cluster
    sp1OrthoIds: list[int] = []
    tmpOrthoIds: list[int] = []
    cosineValsList: list[np.ndarray] = []
    newCosineValsList: list[np.ndarray] = []

    # print(f"Clusters with repetitions to be modified/removed:{clstrsToProcess}\t{len(clstrsToRemove)}")
    for i in range(clstrsToProcess):
        tmpClstrId = clstrsWithReps.pop()
        tmpSp1ClstrSize, tmpSp2ClstrSize, tmpPairsCnt, tmpOrthoIdxs = clstrsToRemove.pop(tmpClstrId, None)
        # print(f"Original cluster [{tmpClstrId}]:\n{aClstrDict[tmpClstrId]}")
        # print(f"Cluster ID\Sp1 size\\Sp2 size\\pairs\\To remove:{tmpClstrId}\t{tmpSp1ClstrSize}\t{tmpSp2ClstrSize}\t{tmpPairsCnt}\t{tmpOrthoIdxs}")

        # Check how many orthologs should be removed
        repToRemoveCnt = len(tmpOrthoIdxs)
        # If all proteins from sp1 are removed
        # then the whole cluster should be removed
        if repToRemoveCnt == tmpSp1ClstrSize:
            # print(f"Remove cluster {tmpClstrId}:\t{tmpClstrId}")
            # Remove the cluster from the main dictionary
            del aClstrDict[tmpClstrId]
            removedPairsCnt += tmpSp1ClstrSize * tmpSp2ClstrSize
            removedClstrCnt += 1
        # Modify the original cluster
        else:
            # print(f"Modify cluster {tmpClstrId}:\t{tmpClstrId}")
            tmpClstr = aClstrDict[tmpClstrId]
            clstrSize = getattr(tmpClstr, "size")
            newClstrSize = clstrSize - repToRemoveCnt
            # Increment the counter for removed pairs
            removedPairsCnt += repToRemoveCnt * tmpSp2ClstrSize
            # Extract the information that needs to be modified
            sp1OrthoIds = list(getattr(tmpClstr, "sp1Ids"))
            currentListLen = len(sp1OrthoIds)
            cosineValsList = getattr(tmpClstr, "cosineValues")

            ''' DEBUG ONLY
            print(f"OrthoIds before pruning:\t{sp1OrthoIds}")
            print(f"Cosine values:\t{cosineValsList}")
            print(f"Elements to be removed:\t{tmpOrthoIdxs}")
            '''

            # Create the new List with genes and scores
            for j in range(currentListLen):
                # print(f"{j} not in {tmpOrthoIdxs}:\t{j not in tmpOrthoIdxs}")
                # If j should not be removed
                # add it to the new list
                if not j in tmpOrthoIdxs:
                    tmpOrthoIds.append(sp1OrthoIds[j])
                    # Also add the cosine Values
                    newCosineValsList.append(cosineValsList[j])

            # print(f"Updated ortho ID list:\t{tmpOrthoIds}")
            # print(f"Updated list with cosine values:\t{newCosineValsList}")

            # Update the cluster with the modified information
            setattr(tmpClstr, "size", newClstrSize)
            setattr(tmpClstr, "sp1Ids", np.array(tmpOrthoIds, dtype=np.uint32))
            setattr(tmpClstr, "cosineValues", newCosineValsList.copy())
            aClstrDict[tmpClstrId] = tmpClstr
            # print(f"Pruned cluster {tmpClstrId}:\t{aClstrDict[tmpClstrId]}")
            tmpOrthoIds.clear()
            newCosineValsList.clear()

    # Set some output variables
    newClstrCnt = prevClstrCnt - removedClstrCnt

    # Create the output dictionary
    aClstrDictPruned: dict[int, ArchClstr] = {}
    oldClstrKeys: list[int] = list(aClstrDict.keys())
    oldClstrKeys.sort(reverse=True)

    # Since some clusters were removed
    # the cluster IDs (order in output file)
    # must be updated with a increasing sequencial digit
    for i in range(newClstrCnt):
        aClstrDictPruned[i+1] = aClstrDict.pop(oldClstrKeys.pop())

    if debug:
        print(f"""Summary from cluster pruning:
        Original clusters count:\t{prevClstrCnt}
        Removed clusters:\t{removedClstrCnt}
        Removed pairs:\t{removedPairsCnt}
        New clusters count:\t{newClstrCnt}""")

    # Delete the old dict
    del aClstrDict
    # return the modified clusters
    return aClstrDictPruned



@cython.cdivision(True) # Use C division instead of Python division
# @cython.boundscheck(False) # Check array bounds
# def process_graph_ortho_subgroup(subgrp: bytes) -> dict[int, float]:
cdef inline tuple process_graph_ortho_subgroup(bytes subgrp):
    """
        Split a subgroup of graph-based ortholog.

        Returns a tuple a list of protein IDs (int) and a list of ortholog scores (float)
    """
    # print("process_graph_ortho_subgroup :: START")

    cdef double sc
    cdef unsigned long gene
    cdef size_t i # Indexes to be used in for loops
    flds: list[bytes] = subgrp.split(b" ")
    geneIds: list[int] = []
    scores: list[float] = []
    cdef bytes rawGeneId
    cdef unsigned long grpSize = len(flds)

    # Extract the gene names and scores
    # Subgroups of a graph based cluster have the following format
    # 23.1825 1.0 23.172 0.85
    for i in range(grpSize):
        if i % 2 == 1:
            # sc = atof(flds.pop()) # works, but genes order is different to that in TSV
            sc = atof(flds[i])
            scores.append(sc)
            # rawGeneId = flds.pop() # works, but genes order is different to that in TSV
            rawGeneId = flds[i-1]
            gene = atol(rawGeneId.split(b".", 1)[1])
            geneIds.append(gene)

    # Return protein IDs and ortholog scores
    return (geneIds, scores)


@cython.wraparound(False) # Do not chek for negative array indexes
@cython.boundscheck(False)  # Deactivate bounds checking
@cython.cdivision(True)
cpdef inline double avg_array_double(cnp.float32_t[:] valuesToAverage) nogil:

    cdef size_t i
    cdef double result = 0.0
    cdef unsigned long arrayLen = valuesToAverage.shape[0]

    for i in range(arrayLen):
        result = result + valuesToAverage[i]

    # Divide by the number of elements
    return result / arrayLen



@cython.wraparound(False) # Do not chek for negative array indexes
@cython.boundscheck(False)  # Deactivate bounds checking
cpdef inline unsigned long sum_bint_array(cnp.uint8_t[:] valuesToSum) nogil:

    cdef size_t i
    cdef unsigned long result = 0
    cdef unsigned long arrayLen = valuesToSum.shape[0]

    for i in range(arrayLen):
        if valuesToSum[i] == 1:
            result = result + 1

    # Return the sum of values
    return result



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