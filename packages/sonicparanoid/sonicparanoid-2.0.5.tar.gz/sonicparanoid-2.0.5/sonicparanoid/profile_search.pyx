# -*- coding: utf-8 -*-
"""
This module contains functions required for the creation of PFam DBs
as well as function for profile search using MMseqs
"""
from __future__ import annotations

import os
import sys
import logging
from time import perf_counter, sleep
import subprocess
import multiprocessing as mp
from tqdm import tqdm
from shutil import rmtree
from pickle import dump, load
from typing import TextIO
from collections import deque, Counter
from math import ceil
from cpython cimport *
from pandas import DataFrame, read_csv, unique

import numpy as np
cimport numpy as cnp
cimport cython


# Load internal modules
from sonicparanoid import sys_tools as systools
from sonicparanoid.workers import parallel_dbs_creation, mmseqs_createdb, get_mmseqs_path



cdef extern from "stdio.h":
    #FILE * fopen ( const char * filename, const char * mode )
    FILE *fopen(const char *, const char *)
    #int fclose ( FILE * stream )
    int fclose(FILE *)
    #ssize_t getline(char **lineptr, size_t *n, FILE *stream);
    ssize_t getline(char **, size_t *, FILE *)



# Logger that will be used in this module
# It is child of the root logger and
# should be initialiazied using the function set_logger()
logger: logging.Logger = logging.getLogger()


'''
__module_name__ = "Profile search"
__source__ = "dev_profile_search.py"
__author__ = "Salvatore Cosentino"
__license__ = "GPL"
__version__ = "0.9"
__maintainer__ = "Cosentino Salvatore"
__email__ = "salvo981@gmail.com"

cdef info():
    """
    This module contains functions required for the creation of PFam DBs
    as well as function for profile search using MMseqs
    """
    print(f"MODULE NAME:\t{__module_name__}")
    print(f"SOURCE FILE NAME:\t{__source__}")
    print(f"MODULE VERSION:\t{__version__}")
    print(f"LICENSE:\t{__license__}")
    print(f"AUTHOR:\t{__author__}")
    print(f"EMAIL:\t{__email__}")
'''

# NOTE: Workers (functions that perfom single jobs)

''' FIXME: this function might not be used in the final version
cdef void consume_pfam_hits2architecture(object jobs_queue, object results_queue, str outDir, int minBitscore, int minUncovLen, double minTargetCov, double minTotQueryCov, bint settingsInFileNames):
    """
    Perform architecture extraction.
    """
    cdef int seqCnt
    cdef str tmpPath
    # will contain the results from the alignment job
    # arch_extraction_time raw_hits_cnt pct_query_w_raw_hits usable_hits_cnt pct_query_w_usable_hits arch_cnt pct_query_w_arch
    cdef (double, int, double, int, double, int, double) resTpl
    cdef list resList
    cdef bint debug

    while True:
        # current_input: tuple[str, int] = ("", 0)
        current_input: tuple[str, int] = jobs_queue.get(True, 1)
        if current_input is None:
            break
        # extract job information
        seqCnt = current_input[1]
        tmpPath = current_input[0]
        resTpl = pfam_hits2architecture(tmpPath, outDir, seqCnt, minbits=minBitscore, minUncovLen=minUncovLen, mintcov=minTargetCov, minTotQueryCov=minTotQueryCov, settingsInFileNames=settingsInFileNames)
        # Will contain the final restuls
        resList: list[Any] = [os.path.basename(tmpPath)]
        # Add the values from profile search and conversion
        resList = resList + [x for x in resTpl]
        # add the results in the output queue
        results_queue.put(resList)
'''



def consume_profile_search_1pass(jobs_queue, results_queue, pfamProfPath:str, dbDir:str, profSearchOutDir:str, archsOutDir:str, runDir:str, kmer:int, sens:float, minBitscore:int, minUncovLen:int, minTargetCov:float, missingBinSize:int, minTotQueryCov:float, noArchs:bool, compress:bool, complev:int, sharedValues: list[int], lock) -> None:
    """
    Perform a profile search using MMseqs2, and optionally extract archs.
    """
    cdef long seqCnt
    cdef unsigned int threads 
    # will contain the results from the alignment job
    # psearch_time psearch_conv_time arch_extraction_time raw_hits_cnt pct_query_w_raw_hits usable_hits_cnt pct_query_w_usable_hits arch_cnt pct_query_w_arch
    cdef (double, double, double, int, double, int, double, int, double) resTpl
    cdef list resList

    while True:
        # current_input: tuple[str, int] = ("", 0)
        current_input = jobs_queue.get(True, 1)
        if current_input is None:
            break
        # extract job information
        spName: str = ""
        auxDir: str = os.path.join(runDir, "aux")
        inDir: str = os.path.join(auxDir, "mapped_input")
        # inputSeqInfoDir: str = os.path.join(auxDir, "input_seq_info")
        threads = 1
        spName, seqCnt = current_input
        # Assign cores to the job
        threads = assign_cores_to_job(sharedValues, lock)
        # Updated shared variables
        with lock:
            sharedValues[2] += 1
        # create main directories and paths
        querySeq = os.path.join(inDir, spName)
        tmpProfSearchDirName: str = f"tmp_{spName}"
        # Perform profile search and archs extraction
        # tuple[float, float, float, int, float, int, float, int, float]
        resTpl = profile_search_1pass(queryName=spName, pfamProfPath=pfamProfPath, profSearchOutDir=profSearchOutDir,  archsOutDir=archsOutDir, dbDir=dbDir, runDir=runDir, seqCnt=seqCnt, kmer=kmer, sens=sens, minBitscore=minBitscore, minUncovLen=minUncovLen, minTargetCov=minTargetCov, missingBinSize=missingBinSize, minTotQueryCov=minTotQueryCov, noArchs=noArchs, compress=compress, complev=complev, threads=threads)

        # Updated shared variables
        with lock:
            sharedValues[0] += 1
            sharedValues[1] -= 1
            sharedValues[2] -= 1
            sharedValues[4] -= threads

        # Will contain the final restuls
        resList = [f"{spName}-{os.path.basename(pfamProfPath)}"]
        # Add the values from profile search and conversion
        resList = resList + [x for x in resTpl]
        resList.append(threads)
        # add the results in the output queue
        results_queue.put(resList)



# NOTE: Parallel jobs inizialiazation and management

''' FIXME: this function might not be used in the final version
# Remember to comment it out
def parallel_pfam_hits2architecture(profileSearchResPaths: list[str], protCntDict:dict[str, int], outDir:str, minBitscore:int=30, minUncovLen:int=5, minTargetCov=0.75, minTotQueryCov:float=0.10, settingsInFileNames:bool=False, threads: int = 4) -> None:
    """Perform parallel architecture extraction from files with raw profile searches.

    Parameters:
    profileSearchResPaths list[str]: paths to profile search result files
    protCntDict dict[str, int]: Dictionary associating a protein count to each proteome
    outDir (str): directory in which the architectures will be stored
    minBitscore (int): Minimum bitscore
    minUncovLen (int): Minimum length for uncovered interregions
    minTargetCov (float): Minimum target coverage (%)
    minTotQueryCov (float): Minimum query coverage for extracted archs
    threads (unsigned int): Threads

    Returns:
    void

    """

    debugStr: str = f"""parallel_pfam_hits2architecture :: START
    Files with profile search results:\t{len(profileSearchResPaths):d}
    Proteomes involved:\t{len(protCntDict):d}
    Output directory: {outDir}
    Minimum bitscore:\t{minBitscore:d}
    Shortest uncovered interregions (aa):\t{minUncovLen:d}
    Minimum target coverage (%):\t{minTargetCov:.2f}
    Minimum query coverage for extracted archs (%):\t{minTotQueryCov:.2f}
    Threads:\t{threads:d}"""
    logger.debug(debugStr)

    # Create the pickle file with pfam-clans if not available
    cdef str binDir = os.path.join(os.path.dirname(__file__), "bin")
    cdef list pcklList = ["profile2clan.pckl", "profile2type.pckl", "pfam_unknown.pckl"]
    for fname in pcklList:
        if not os.path.isfile(os.path.join(binDir, fname)):
            # This will create 3 pckl files
            # and the metadata table
            create_pfam_info_table()
            break
    # Call again the meta-data table does not exist
    cdef str pfamDir = os.path.join(os.path.dirname(__file__), "pfam_files")
    if not os.path.isfile(os.path.join(pfamDir, "Pfam-A.hmm.metadata.tsv")):
        create_pfam_info_table()

    del pfamDir, binDir
    cdef str tmpPath, tmpStr
    cdef int i = 0
    cdef int pathsCnt = len(profileSearchResPaths)

    # reset timers
    start_time = end_time = 0.0

    # create the queue and start adding
    search_queue: mp.queues.Queue = mp.Queue(maxsize=pathsCnt + threads)
    # Fill the queue with the path and protein count for the proteome
    # for sp, w in profileSearchResPaths:
    profileSearchResPaths.sort()
    while i < pathsCnt:
        # print(profileSearchResPaths.pop())
        tmpPath = profileSearchResPaths.pop()
        tmpStr = os.path.basename(tmpPath).split("-", 1)[0]
        i += 1
        search_queue.put((tmpPath, protCntDict[tmpStr]))

    # add flags for ended jobs
    for i in range(0, threads):
        sys.stdout.flush()
        search_queue.put(None)

    # Queue to contain the execution times
    results_queue: mp.queues.Queue = mp.Queue(maxsize=pathsCnt)

    # List of running jobs
    cdef list runningJobs = [mp.Process(target=consume_pfam_hits2architecture, args=(search_queue, results_queue, outDir, minBitscore, minUncovLen, minTargetCov, minTotQueryCov, <bint>settingsInFileNames)) for i_ in range(threads)]

    # execute the jobs
    for proc in runningJobs:
        proc.start()

    # Create the file in which the time information and stats
    # for the profile search will be stored
    # cdef str runName = os.path.basename(runDir.rstrip("/"))
    cdef str searchExTimeFileName = f"arch_extraction_ex_times_{minBitscore}bits_tcov{minTargetCov}_totqcov{minTotQueryCov}.tsv" 
    cdef str execTimeOutPath = os.path.join(outDir, searchExTimeFileName)
    del searchExTimeFileName
    # ofd: TextIO = open(execTimeOutPath, "w", buffering=1, encoding="utf-8")
    ofd: TextIO = open(execTimeOutPath, "w", encoding="utf-8")
    # Write the header for the output file
    # search: <proteome-Profile_DB>
    # psearch_time: ex time for profile search with MMseqs
    # psearch_conv_time: time for conversion with convertalis
    # arch_extraction_time: time to process and extract archs
    # raw_hits_cnt: total profile search hits before filtering
    # pct_query_w_raw_hits: ratio of proteome with at least one hit (before filtering)
    # usable_hits_cnt: number of hits after filtering by minimum bitscore and minimum target coverage
    # pct_query_w_usable_hits: ratio of proteome with at least one hit (after filtering)
    # arch_cnt: total number of architectures for the proteome
    # pct_query_w_arch: ratio of proteome with architecture
    # threads: number of threads used in the profile search
    ofd.write("search\tpsearch_time\tpsearch_conv_time\tarch_extraction_time\traw_hits_cnt\tpct_query_w_raw_hits\tusable_hits_cnt\tpct_query_w_usable_hits\tarch_cnt\tpct_query_w_arch\tthreads\n")

    # calculate cpu-time for alignments
    align_start = perf_counter()
    # write some message...
    sys.stdout.write(f"\nExtracting architectures for {pathsCnt} from profile search result files...")
    # Contains the information from arch extraction
    resList: list[tuple[str, float, int, float, int, float, int, float]] = []
    # write output when available
    while True:
        try:
            resList = results_queue.get(False, 0.01)
            # Example of output
            # ['48-pfama.mmseqs', 0, 0, 0.05000000074505806, 1711, 60.445682525634766, 1307, 55.20891189575195, 981, 54.65180969238281, 1]
            ofd.write("{:s}\t0\t0\t{:.3f}\t{:d}\t{:.3f}\t{:d}\t{:.3f}\t{:d}\t{:.3f}\t1\n".format(*resList))

        #except queue.Empty:
        except:
            pass
        allExited = True
        for t in runningJobs:
            if t.exitcode is None:
                allExited = False
                break
        if allExited & results_queue.empty():
            break
    ofd.close()

    # this joins the processes after we got the results
    for proc in runningJobs:
        while proc.is_alive():
            proc.join()

    # stop the counter for the alignment time
    sys.stdout.write(f"\nElapsed time for the extraction of architectures (seconds):\t{(perf_counter() - align_start):.3f}\n")
'''



def parallel_profile_search_1pass(spToSearch: list[str], protCntDict:dict[str, int], runDir:str, dbDir:str, pfamProfPath:str, profSearchOutDir:str, archsOutDir:str, kmer:int=5, sens:float=7.0, minBitscore:int=30, minUncovLen:int=5, minTargetCov=0.75, missingBinSize=1, minTotQueryCov:float=0.75, noArchs:bool=False, compress:bool=False, complev:int=5, threads:int=4) -> None:
    """Perform parallel profile searches.

    Parameters:
    spToSearch list[str]: paths to files to search
    protCntDict dict[str, int]: Dictionary associating a protein count to each proteome
    runDir (str): SonicParanoid run directory
    dbDir (str): Directory with MMseqs2 query DB files
    pfamProfPath (str): PFamA profile DB
    profSearchOutDir (str): Directory with profile search results
    archsOutDir (str): Directory with extracted architectures
    kmer (unsigned int): KMER value for Profile search
    sens (float): MMseqs sensitivity
    minBitscore (int): Minimum bitscore
    minTargetCov (float): Minimum target coverage (%)
    missingBinSize (unsigned int): Missing bin size
    minTotQueryCov (float): Minimum query coverage for extracted archs
    noArchs (bint): Skip extraction of architectures
    compress (bint): Compress processed profile searches
    complev (unsigned int): Compression level
    threads (unsigned int): Threads

    Returns:
    void

    """

    auxDir: str = os.path.join(runDir, "aux")
    debugStr: str = f"""parallel_profile_search_1pass :: START
    Profile search jobs to be performed:\t{len(spToSearch):d}
    Query proteomes:\t{len(protCntDict):d}
    Directory containing run files: {runDir:s}
    Directory with auxiliary files: {auxDir:s}
    Directory with MMseqs2 query DB files: {dbDir:s}
    PFamA profile DB: {pfamProfPath:s}
    Directory with profile search results: {profSearchOutDir:s}
    Directory with extracted architectures: {archsOutDir}
    KMER value for Profile search:\t{kmer:d}
    MMseqs sensitivity:\t{sens:.2f}
    Minimum bitscore:\t{minBitscore:d}
    Shortest uncovered interregions (aa):\t{minUncovLen:d}
    Minimum target coverage (%):\t{minTargetCov:.2f}
    Missing bin size:\t{missingBinSize:d}
    Minimum query coverage for extracted archs (%):\t{minTotQueryCov:.2f}
    Skip arch extraction:\t{noArchs}
    Compress output:\t{compress}
    Compression level:\t{complev:d}
    Threads:\t{threads:d}"""
    logger.debug(debugStr)

    # Create the pickle file with pfam-clans if not available
    cdef str binDir = os.path.join(os.path.dirname(__file__), "bin")
    cdef list pcklList = ["profile2clan.pckl", "profile2type.pckl", "pfam_unknown.pckl"]
    for fname in pcklList:
        if not os.path.isfile(os.path.join(binDir, fname)):
            # This will create 3 pckl files
            # and the metadata table
            create_pfam_info_table()
            break
    # Call again if the meta-data table does not exist
    cdef str pfamDir = os.path.join(os.path.dirname(__file__), "pfam_files")
    if not os.path.isfile(os.path.join(pfamDir, "Pfam-A.hmm.metadata.tsv")):
        create_pfam_info_table()

    del pfamDir, binDir

    # Fill dict with required profile searches and genome size
    # rnovergicus -> 11080203
    # str -> int
    cdef dict requiredSearches = {sp:protCntDict[sp] for sp in spToSearch}
    cdef unsigned long profSearchCnt = len(spToSearch)

    # Sort by proteome size [biggest to smallest]
    requiredSearches = {sp: requiredSearches[sp] for sp in sorted(requiredSearches, key=requiredSearches.get, reverse=True)}
    cdef list missingDbSpList = [] # list[str]
    cdef str tmpPath
    for sp in spToSearch:
        tmpPath = os.path.join(dbDir, f"{sp}.mmseqs2db")
        if not os.path.isfile(tmpPath):
            missingDbSpList.append(sp)
    logger.debug(f"DB files are missing for proteomes\n{missingDbSpList}")

    # Create the database if do not exist already
    cdef float start_time, end_time, align_start
    if len(missingDbSpList) > 0:
        fastaDir: str = os.path.join(auxDir, "mapped_input")
        # create the directory which will contain the databases
        makedir(dbDir)
        # create databases
        sys.stdout.write(f"\nCreating {len(missingDbSpList)} MMseqs DBs...\n")
        # timer for databases creation
        start_time = perf_counter()
        # create databases in parallel
        parallel_dbs_creation(missingDbSpList, fastaDir, dbDir, create_idx=False, alnTool="mmseqs", dmndSens="default", threads=threads, debug=False)
        # end time for databases creation
        end_time: float = perf_counter()
        sys.stdout.write(f"\nMMseqs DBs creation elapsed time (seconds):\t{round(end_time - start_time, 3)}\n")

    # Write a file with the profile search settings
    cdef str runInfoFile
    runInfoFile = os.path.join(profSearchOutDir, "profile_search.info.txt")

    # Fill the dictionary with the required information
    cdef dict infoDict = {"Module:":__name__}
    infoDict["Run directory:"] = runDir
    infoDict["Profile searches to be performed:"] = str(profSearchCnt)
    infoDict["PFamA profile DB:"] = pfamProfPath
    infoDict["Sequence DB directory:"] = dbDir
    infoDict["Profile searches output dir:"] = profSearchOutDir
    infoDict["Architectures dir:"] = archsOutDir
    infoDict["KMER value for Profile search:"] = str(kmer)
    infoDict["MMseqs sensitivity:"] = f"{sens:.2f}"
    infoDict["Minimum bitscore:"] = str(minBitscore)
    infoDict["Shortest uncovered interregions (aa):"] = str(minUncovLen)
    infoDict["Minimum target coverage (%):"] = f"{minTargetCov:.2f}"
    infoDict["Missing bin size:"] = str(missingBinSize)
    infoDict["Minimum query coverage for extracted archs (%):"] = f"{minTotQueryCov:.2f}"
    infoDict["Skip arch extraction:"] = str(noArchs)
    infoDict["Compress output:"] = str(compress)
    infoDict["Compression level:"] = str(complev)
    infoDict["Threads:"] = str(threads)
    write_run_info_file(profSearchOutDir, infoDict)
    del infoDict, runInfoFile

    # reset timers
    start_time = end_time = 0.0

    # Set variables shared among processes
    # sharedValues -> completedJob, requiredJobs, processing, waiting, cpusInUse, totCores
    sharedValues: list[int] = mp.Array("i", [0, profSearchCnt, 0, 0, 0, threads])
    sharedValsLock: mp.synchronize.Lock = mp.Lock()

    # create the queue and start adding
    search_queue: mp.queues.Queue = mp.Queue(maxsize=profSearchCnt + threads)
    for sp, w in requiredSearches.items():
        # w is the number of proteins associated to the proteom
        # print((sp, w))
        search_queue.put((sp, w))

    # add flags for ended jobs
    for i in range(0, threads):
        sys.stdout.flush()
        search_queue.put(None)

    # Queue to contain the execution times
    results_queue: mp.queues.Queue = mp.Queue(maxsize=profSearchCnt)

    # List of running jobs
    cdef list runningJobs = [mp.Process(target=consume_profile_search_1pass, args=(search_queue, results_queue, pfamProfPath, dbDir, profSearchOutDir, archsOutDir, runDir, kmer, sens, minBitscore, minUncovLen, minTargetCov, missingBinSize, minTotQueryCov, noArchs, compress, complev, sharedValues, sharedValsLock)) for i_ in range(threads)]


    # Create the file in which the time information and stats
    # for the profile search will be stored
    cdef str runName = os.path.basename(runDir.rstrip("/"))
    cdef str searchExTimeFileName = f"prof_search_ex_times_{minBitscore}bits_tcov{minTargetCov}_totqcov{minTotQueryCov}.{runName}.tsv" 
    cdef str execTimeOutPath = os.path.join(profSearchOutDir, searchExTimeFileName)
    del searchExTimeFileName
    ofd: TextIO = open(execTimeOutPath, "wt", buffering=1)
    # Write the header for the output file
    # search: <proteome-Profile_DB>
    # psearch_time: ex time for profile search with MMseqs
    # psearch_conv_time: time for conversion with convertalis
    # arch_extraction_time: time to process and extract archs
    # raw_hits_cnt: total profile search hits before filtering
    # pct_query_w_raw_hits: ratio of proteome with at least one hit (before filtering)
    # usable_hits_cnt: number of hits after filtering by minimum bitscore and minimum target coverage
    # pct_query_w_usable_hits: ratio of proteome with at least one hit (after filtering)
    # arch_cnt: total number of architectures for the proteome
    # pct_query_w_arch: ratio of proteome with architecture
    # threads: number of threads used in the profile search
    ofd.write("search\tpsearch_time\tpsearch_conv_time\tarch_extraction_time\traw_hits_cnt\tpct_query_w_raw_hits\tusable_hits_cnt\tpct_query_w_usable_hits\tarch_cnt\tpct_query_w_arch\tthreads\n")

    # calculate cpu-time for alignments
    align_start = perf_counter()
    # write some message...
    print(f"\nPerforming {profSearchCnt} profile searches and extraction of architectures...")

    # execute the jobs
    for proc in runningJobs:
        proc.start()

    # Show the progress bars
    pbar: tqdm = tqdm(total=profSearchCnt, desc="profile searches", unit="proteomes", disable=None, smoothing=0.3, ascii=False, miniters=1, mininterval=2.0, colour='red')

    cdef list resList = []

    # write output when available
    while True:
        try:
            resList = results_queue.get(False, 0.01)
            # Example of output
            # ['48-pfama.mmseqs', 10.829999923706055, 0.009999999776482582, 0.05000000074505806, 1711, 60.445682525634766, 1307, 55.20891189575195, 981, 54.65180969238281, 1]
            ofd.write("{:s}\t{:.3f}\t{:.3f}\t{:.3f}\t{:d}\t{:.3f}\t{:d}\t{:.3f}\t{:d}\t{:.3f}\t{:d}\n".format(*resList))
            # Update the status bar
            pbar.update(1)

        #except queue.Empty:
        except:
            pass
        allExited = True
        for t in runningJobs:
            if t.exitcode is None:
                allExited = False
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
    sys.stdout.write(f"\nElapsed time for profile searches using MMseqs (seconds):\t{round(perf_counter() - align_start, 3)}\n")



# NOTE: Other functions
def set_logger(loggerName: str, lev: int, propagate: bool, customFmt: logging.Formatter = None) -> None:
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



def assign_cores_to_job(sharedVals: list[int], lock) -> int:
    """
    Modify shared variables and assign number of cores based on available resources
    """
    # NOTE: use debug only if required
    # cdef bint debug = 1
    # sharedValues -> completedJob, requiredJobs, processing, waiting, cpusInUse, totCores
    cdef unsigned long remainingAln, processing, waiting, cpusInUse, totCores, availCores, coresPerAln
    coresPerAln = 1
    with lock:
        remainingAln = sharedVals[1]
        processing = sharedVals[2]
        waiting = sharedVals[3]
        cpusInUse = sharedVals[4]
        totCores = sharedVals[5]
        availCores = totCores - cpusInUse
        coresPerAln = ceil(availCores / (remainingAln - processing))
        if coresPerAln <= 1:
            sharedVals[4] += 1
        else: # Assign an higher number of cores
            sharedVals[4] += coresPerAln

        '''
        if debug:
            print(f"availCores (before updating CPUs in use count):\t{availCores}")
            print(f"(remaining/processing/waiting):\t{remainingAln}\t{processing}\t{waiting}")
            print(f"remainingAln:\t{sharedVals[1]}")
            print(f"processing:\t{sharedVals[2]}")
            print(f"waiting:\t{sharedVals[3]}")
            print(f"cpusInUse:\t{sharedVals[4]}")
            print(f"Assigned CPUs:\t{coresPerAln}")
        '''
    # Return the number of assigned jobs
    return coresPerAln



cdef str create_mmseqs_pfam_profile_db(str dbType, str outDir, int kmer = 5, float sens = 7., int threads = 2, bint delTmp = 1, bint compressed = 0, bint index = 0, bint writeLog = 1):
    """Create mmseqs2 profile DB using the databases command in MMseqs."""
    # Set the log file path
    logPath: str = os.path.join(outDir, "log.create_mmseqs_pfam_profile_db.txt")
    cdef unsigned int currentLev = logger.level

    debugStr: str = f"""create_mmseqs_pfam_profile_db :: START\n\
    PFamA type:\t{dbType:s}
    KMER:\t{kmer:d}
    Sensitivity:\t{sens:g}
    Output directory: {outDir:s}
    Threads:\t{threads:d}
    Remove Tmp files:\t{delTmp}
    Compress output:\t{compressed}
    Index DB:\t{index}
    Write log:\t{writeLog}"""
    logger.debug(debugStr)

    flogger: logging.Logger = logging.Logger("")
    if writeLog:
        flogger = systools.create_flogger(logPath, loggerName=f"{__name__}.file_logger", lev=currentLev, mode="a", propagate=False)
    if writeLog:
        flogger.log(20, debugStr)

    # check that kmer size is in a valid range
    if kmer != 5:
        if kmer > 5:
            logger.warning(f"The kmer value ({kmer}) should not be increased unless there is a lot of available memory.\n\
        Increasing the kmer value would cause the DB size to be 5X bigger.")
            # increasing the kmer value would cause the DB size to be 5X bigger.")
        elif kmer < 4:
            logger.warning(f"WARNING: the kmer value ({kmer}) should not be below 4. It will be set to default value of 5\n")
 
    # check that the sensitivity is in a valid range
    if sens < 5.7:
        logger.warning(f"The sensitivity value ({sens}) should not be below 5.8. It will be set to default value of 7.0\n")
        sens = 7.0
    elif sens > 7.5:
        logger.warning(f"The sensitivity value ({sens}) cannot be higher than 7.5. It will be set to default value of 7.0\n")
        sens = 7.0

    opts: list[str] = []
    optsStr: str = ""
    if compressed:
        opts.append("--compressed 1")
    if delTmp:
        opts.append("--remove-tmp-files")
    # Final options strings
    if len(opts) > 0:
        optsStr = " ".join(opts)
    del opts

    # set the suffix for the dab name
    sensDecStr: str = str(sens).replace(".", "")
    # Set main variables
    suffix: str = f"k{kmer}s{sensDecStr}"
    dbName: str = f"pfama.{dbType}.{suffix}"
    dbNameSimple: str = f"pfama.mmseqs"
    dbPath: str = os.path.join(outDir, dbNameSimple)
    # Prepare file names and commands
    tmpDir: str = os.path.join(outDir, f"tmp_{dbName}")
    makedir(outDir)
    makedir(tmpDir)

    # extra options
    # Set the database type
    pfamType: str = "Pfam-A.seed"
    if dbType == "full":
        pfamType = "Pfam-A.full"

    # EXAMPLES of command to be executed
    # mmseqs databases <name> <o:sequenceDB> <tmpDir> [options]
    # mmseqs databases Pfam-A.seed my_pfam_seed_profiles_db myTmpDir --threads 6 --remove-tmp-files -v 3 
    # For a complete list of available DBs type 'mmseqs databases -h'
    mmseqsDatabasesCmd: str = f"{get_mmseqs_path()} databases {pfamType} {dbPath} {tmpDir} --threads {threads} -v 3 {optsStr}"
    logger.debug(f"MMseqs2 databases CMD:\n{mmseqsDatabasesCmd}")
    if writeLog:
        # Write also in the log file
        flogger.log(currentLev, f"\nMMseqs2 databases CMD:\n{mmseqsDatabasesCmd}")

    #execute the system call
    process = subprocess.Popen(mmseqsDatabasesCmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout_val, stderr_val = process.communicate() #get stdout and stderr
    process.wait()
    logger.debug(f"STDOUT:\n{stdout_val.decode()}\n\
        STDERR:\n{stderr_val.decode()}\n")
    if writeLog:
        # Write also in the log file
        flogger.log(currentLev, f"STDOUT:\n{stdout_val.decode()}\n\
        STDERR:\n{stderr_val.decode()}\n")

    if delTmp:
        # remove the temporary directory
        try:
            rmtree(tmpDir)
        except OSError:
            sleep(1)
            rmtree(tmpDir, ignore_errors=True)  # solve shutil NFS bug, ignore errors, file removal is less important

    # index the profile database
    if index:
        idxTmpDir: str = os.path.join(outDir, "tmp-indexing")
        index_profile_db(profilePath=dbPath, tmpDir=idxTmpDir, flogger=flogger, kmer=kmer, sens=sens, threads=threads)

    validate_profile_db(bname=dbNameSimple, dirPath=outDir, indexed=index)
    # Return profile DB path
    return dbPath



# def create_pfam_info_table(pfamSeedMetadataPath: str, outPath: str) -> str:
# def create_pfam_info_table() -> str:
cdef void create_pfam_info_table():
    """
    Generates a table with info on the pfam entries (e.g., ID, length, entry type, clan etc.)
    """
    import gzip
    logger.info(f"create_pfam_info_table :: START")

    cdef str srcDir = os.path.dirname(__file__)
    cdef str pfamDir = os.path.join(srcDir, "pfam_files/")
    cdef str pfamSeedMetadataPath = os.path.join(pfamDir, "Pfam-A.hmm.dat.gz")
    if not os.path.isfile(pfamSeedMetadataPath):
        sys.stderr.write(f"The file with info on PFam-A seed HMMs\n{pfamSeedMetadataPath}\nwas not found, please contact the developers for assistance.")
        sys.exit(-2)

    # Set the output directory for the pickles
    cdef str binDir = os.path.join(srcDir, "bin/")
    makedir(binDir)

    # The refence table is named Pfam-A.hmm.dat
    # It can be downloaded from /pub/databases/Pfam/releases/Pfam35.0/Pfam-A.hmm.dat.gz
    # and contains metadata regarding the SEED entries used in the HMM model

    # Entries have tghe foillowing format
    '''
    # STOCKHOLM 1.0
    #=GF ID   1-cysPrx_C
    #=GF AC   PF10417.12
    #=GF DE   C-terminal domain of 1-Cys peroxiredoxin
    #=GF GA   21.1; 21.1;
    #=GF TP   Domain
    #=GF ML   40
    //
    # STOCKHOLM 1.0
    #=GF ID   120_Rick_ant
    #=GF AC   PF12574.11
    #=GF DE   120 KDa Rickettsia surface antigen
    #=GF GA   25; 25;
    #=GF TP   Family
    #=GF ML   238
    //
    # STOCKHOLM 1.0
    #=GF ID   ZZ
    #=GF AC   PF00569.20
    #=GF DE   Zinc finger, ZZ type
    #=GF GA   21.4; 21.4;
    #=GF TP   Domain
    #=GF ML   45
    #=GF CL   CL0006
    //
    '''

    # Open output table and write header
    cdef str metaTblPath = os.path.join(pfamDir, "Pfam-A.hmm.metadata.tsv")
    ofd: TextIO = open(metaTblPath, "wt")
    ofd.write("pfam_acc\tpfam_id\tdesc\tlength\tentry_type\tclan\tunknown_func\n")

    # other variables
    cdef long entryCnt = 0
    # create the dict to map profiles to clans
    cdef dict pfam2clan = {} # dict[str, str]
    # create the dict to map profiles to pfam type
    # The type are the following and are encoded to integers
    # Family -> 1
    # Domain -> 2
    # Repeat -> 3
    # Coiled-coil -> 4
    # Motif -> 5
    # Disordered -> 6
    cdef dict pfam2type = {} # dict[str, int]
    # Will contain Accessions for entries with unknown function
    # cdef dict unknownPfam = {} # dict[str, None]
    cdef dict pfamType2Int = {"Family":1, "Domain":2, "Repeat":3, "Coiled-coil":4, "Motif":5, "Disordered":6}
    cdef dict pfamTypeCounter = {"Family":0, "Domain":0, "Repeat":0, "Coiled-coil":0, "Motif":0, "Disordered":0}
    cdef str tmpId, tmpAccession, tmpDesc, tmpType, tmpLenStr, tmpClan, tmpTag
    tmpId = tmpAccession = tmpDesc = tmpType = tmpLenStr = tmpClan = ""
    # Families that contain the DUF (Domain of Unknown Function) in the description
    unknownPfam: set[str] = set()
    cdef bint isUnknown = 0

    with gzip.open(pfamSeedMetadataPath, "rb") as gzifd:
        # read the file and extract profile and clans
        for line in gzifd.readlines():
            # if the first letter is a '/' then it is the end of the entry
            if line.decode()[1] == " ": # Then  is the line of new entry
                continue
            elif line.decode()[1] == "/": # Then  is the the closing of an entry
                entryCnt += 1
                ofd.write(f"{tmpAccession}\t{tmpId}\t{tmpDesc}\t{tmpLenStr}\t{tmpType}\t{tmpClan}\t{isUnknown:d}\n")
                tmpId = tmpAccession = tmpDesc = tmpType = tmpLenStr = tmpClan = ""
                # continue
            else: # then it is a line that should be processed
                flds = line.rstrip(b"\n").rsplit(b"   ", 2)
                tmpTag = flds[0].decode().split(" ", 1)[1]
                # Do different parsing depending on the tag
                # Main ID
                if tmpTag == "ID":
                    # print(flds[1])
                    tmpId = flds[1].decode()
                # Accession ID
                elif tmpTag == "AC":
                    # Extract the accession and remome the rightmost version
                    # e.g., PF09847.12 -> PF09847
                    tmpAccession = flds[1].decode().rsplit(".", 1)[0]
                # Description
                elif tmpTag == "DE":
                    tmpDesc = flds[1].decode()
                    # Check if it contains the DUF tag, for entries with unknown functions
                    if "DUF" in tmpDesc:
                        # Make sure it is not 'NDUF'
                        if not "NDUF" in tmpDesc:
                            isUnknown = 1
                            # unknownPfam[tmpAccession] = 0
                            unknownPfam.add(tmpAccession)
                    else:
                        isUnknown = 0
                # PFGamA Type
                elif tmpTag == "TP":
                    # print(flds[1])
                    tmpType = flds[1].decode()
                    pfamTypeCounter[tmpType] += 1
                    pfam2type[tmpAccession] = pfamType2Int[tmpType]
                # Length of the profile/protein
                elif tmpTag == "ML":
                    # print(flds[1])
                    tmpLenStr = flds[1].decode()
                # Clan (might be missing)
                elif tmpTag == "CL":
                    tmpClan = flds[1].decode()
                    pfam2clan[tmpAccession] = tmpClan
    ofd.close()

    # Store info to pckl
    cdef str tmpOutPath = os.path.join(binDir, "profile2clan.pckl")
    with open(tmpOutPath, "wb") as ofd:
        dump(pfam2clan, ofd, protocol=5)

    # Store info to pckl
    tmpOutPath = os.path.join(binDir, "profile2type.pckl")
    with open(tmpOutPath, "wb") as ofd:
        dump(pfam2type, ofd, protocol=5)

    # Store info to pckl
    tmpOutPath = os.path.join(binDir, "pfam_unknown.pckl")
    with open(tmpOutPath, "wb") as ofd:
        dump(unknownPfam, ofd, protocol=5)

    cdef str debugStr = f"""    PFam entries:\t{entryCnt}
    Profiles with clan:\t{len(pfam2clan)}
    Single clans:\t{len(set(pfam2clan.values()))}
    Profiles with type:\t{len(pfam2type)}
    Single types:\t{len(set(pfam2type.values()))}
    Profiles with unknown function:\t{len(unknownPfam)}"""
    logger.info(debugStr)

    # Write a file with simple stats
    ofd = open(os.path.join(pfamDir, "pfam.seed.stats.tsv"), "wt")
    ofd.write(f"Entries:\t{entryCnt}\n")
    ofd.write(f"Profiles with unknown function:\t{len(unknownPfam)}")
    ofd.write("\n\nSummary of profile types.\n")
    for entryType, cnt in pfamTypeCounter.items():
        ofd.write(f"{entryType}:\t{cnt}\n")
    ofd.close()


'''
cdef str create_profile2clans_pkl():
    """
    Generates a python pickle file of dictionary mapping a profile to a clan.
    """
    import gzip
    logger.info("create_profile2clans_pkl :: START")

    # set the directory with Pfam files
    cdef str srcDir = os.path.dirname(__file__)
    cdef str pfamDir = os.path.join(srcDir, "pfam_files/")
    cdef str clansFile = os.path.join(pfamDir, "Pfam-A.clans.tsv.gz")
    if not os.path.isfile(clansFile):
        sys.stderr.write(f"The mapping file {clansFile} was not found, please contact the developers for assistance.")
        sys.exit(-2)

    #create the dictionary to store the profiles and clans
    cdef dict mappingDict = {} # dict[str, str]
    #initialize counters
    cdef unsigned int lnCnt = 0
    line: bytes = bytes()
    # flds: list[bytes] = []
    cdef list flds = [] # list[bytes]
    # Input have the following format (No header)
    # pfam_acc clan_acc clan_id pfam_id pfam_descr
    # PF00001 CL0192 GPCR_A 7tm_1 "7 transmembrane receptor (rhodopsin family)"

    #open the alignments for AB
    with gzip.open(clansFile, "rb") as gzifd:
        # read the file and extract profile and clans
        for line in gzifd.readlines():
            lnCnt += 1
            #split the string
            flds = line.split(b"\t", 2)
            # Add entry into the dictionary
            # Only if the Clan field is not empty
            if len(flds[1]) > 0:
                mappingDict[flds[0].decode()] = flds[1].decode()

    del flds, line

    # Set the output path and write the pickle
    cdef str binDir = os.path.join(srcDir, "bin/")
    makedir(binDir)
    cdef str pcklPath = os.path.join(binDir, "prof2clan.pckl")

    # dump the pickle with with profile 2 clans mapping
    with open(pcklPath, "wb") as ofd:
        dump(mappingDict, ofd, protocol=4)

    cdef str debugStr = f"""Read lines:\t{lnCnt}
    Profiles with clan found:\t{len(mappingDict)}
    Clans found:\t{len(set(mappingDict.values()))}"""
    logger.info(debugStr)

    # return path to the pickle file
    return pcklPath
'''



# NOTE: we are passing the memoryview in order to avoid the warning due to the use of inline
# The execution time is not affected
# cdef inline cnp.ndarray[cnp.uint8_t, ndim=1] domain_overlap_slice(cnp.ndarray[cnp.uint32_t] qstartArr, cnp.ndarray[cnp.uint32_t] qendArr, cnp.ndarray[cnp.float64_t] qcovArr):
cdef inline cnp.ndarray[cnp.uint8_t, ndim=1] domain_overlap_slice(cnp.uint32_t[:] qstartArr, cnp.uint32_t[:] qendArr, cnp.float64_t[:] qcovArr):
    """
    Takes in input arrays with start and end align position on queries.
    Returns an array with indexes for which an overlap was found.
    If not overlap is found the output array will have 0 length.
    """

    '''
    cdef bint debug = 0
    if debug:
        print("\ndomain_overlap_slice :: START")
        print(f"Query start: {qstartArr.size}")
        print(f"Query end: {qendArr.size}")
        print(f"Query coverages: {qcovArr.size}")
    '''

    # Positions to be used in the comparison 
    cdef long acceptedStart, acceptedEnd, leftDomLen, rightDomLen
    acceptedStart = acceptedEnd = leftDomLen = rightDomLen = 0
    cdef long leftStart, leftEnd, rightStart, rightEnd, shortestDom
    leftStart = leftEnd = rightStart = rightEnd = shortestDom = 0
    cdef unsigned long SLICE_SIZE = qstartArr.size
    cdef double OVERLAP_THR = -0.05
    cdef double domOverlap = 0.
    # Will contain the positions of the accepted domains
    # Keep track of how much of the query is still uncovered
    cdef double tmpAvailCov = 1.
    # Flag indicating an overlap
    # set to 1 (True) if an overlap is found
    cdef bint hasOverlap = 0
    # Accept the first domain
    cdef long candStart = qstartArr[0]
    cdef long candEnd = qendArr[0]
    # Temporary variables to be used while searching for ovelaps
    cdef long candIdx = 0
    # Accept the first row and create the
    # Lost to keep track of accepted position
    # acceptedDomCoords: list[tuple[int, int]] = [(candStart, candEnd)]
    cdef (long, long) candidatePosTpl = (candStart, candEnd)
    cdef list acceptedDomCoords = [candidatePosTpl] # list[tuple[int, int]]

    cdef double tmpQcov = qcovArr[0]
    tmpAvailCov -= tmpQcov
    # toRemove: np.ndarray = np.zeros(SLICE_SIZE, dtype=np.uint8)
    cdef cnp.ndarray[cnp.uint8_t, ndim=1] toRemove = np.zeros(SLICE_SIZE, dtype=np.uint8)

    # DEBUG-LINES
    # # print(acceptedDoms, tmpAvailCov)
    # print(f"SLICE_SIZE =\t{SLICE_SIZE}")
    # print(f"First domain accepted: {acceptedDomCoords}, tmpAvailCov = {tmpAvailCov}")

    for candIdx in range(1, SLICE_SIZE):
        # print(f"\ncandIdx:\t{candIdx}")
        tmpQcov = qcovArr[candIdx]
        # Only check the overlaps if there is
        # enough portion of the query uncovered
        if tmpQcov > tmpAvailCov:
            toRemove[candIdx] = 1
            # print(f"DEBUG: Not enough uncovered aminoacids on current query! tmpQcov={tmpQcov}; tmpAvailCov={tmpAvailCov}")
        else:
            candStart = qstartArr[candIdx]
            candEnd = qendArr[candIdx]
            # Overlap check
            hasOverlap = 0 # Reset the flag
            # For each of the possible candidates, check the overlap
            # and set the flag hasOverlap to 0 if at least one ovelaps
            for acceptedStart, acceptedEnd in acceptedDomCoords:
                # print(f"debug: Cecking overlaps: ({candStart}, {candEnd}) ({acceptedStart}, {acceptedEnd})")
                # Overlap at the start
                if candStart == acceptedStart:
                    # print(f"debug: Overlap @ start position")
                    hasOverlap = 1
                    break
                elif candEnd == acceptedEnd:
                    # print(f"debug: Overlap @ end position")
                    hasOverlap = 1
                    break

                # WORKING VERSION with no IF
                # position the candidate domain on the left
                if candStart < acceptedStart:
                    leftStart = candStart
                    leftEnd = candEnd
                    rightStart = acceptedStart
                    rightEnd = acceptedEnd
                else: # acceptedStart < candStart
                    leftStart = acceptedStart
                    leftEnd = acceptedEnd
                    rightStart = candStart
                    rightEnd = candEnd

                # Skip simple non-overlap case
                # In this case the two sequencese are not overlapping at all
                if leftEnd < rightStart:
                    # print("debug: Simple non-overlap case!")
                    continue

                # compute lengths of the alignments and shortest domain
                leftDomLen = leftEnd - leftStart + 1
                rightDomLen = rightEnd - rightStart + 1
                shortestDom = min(leftDomLen, rightDomLen)
                # compute the overlap
                domOverlap = round((rightStart - leftEnd - 1) / shortestDom)
                if domOverlap <= OVERLAP_THR:
                    # print(f"debug: Overlap found!\t{domOverlap}")
                    hasOverlap = 1
                    break
                # else:
                #     print(f"No overlap found for this single domain! ({leftDomLen}, {rightDomLen}, {shortestDom}, {domOverlap})")

            if hasOverlap: # CHECK THE OVERLAP
                toRemove[candIdx] = 1
            else:
                # Accept the domain
                candidatePosTpl = (candStart, candEnd)
                acceptedDomCoords.append(candidatePosTpl)
                # acceptedDomCoords.append((candStart, candEnd))
                # sort the list
                acceptedDomCoords.sort()
                # update the available coverage
                tmpAvailCov -= tmpQcov
                # print(f"Updated tmpAvailCov:\t{tmpAvailCov}")

    # Return the array with indexes to remove
    return toRemove.nonzero()[0]



cdef long extract_query_pfam_arch(qArr: np.ndarray, tArr: np.ndarray, cnp.ndarray[cnp.uint32_t] qstartArr, cnp.ndarray[cnp.uint32_t] qendArr, cnp.ndarray[cnp.uint32_t] qlenArr, dict profile2clan, dict profile2type, ofd: TextIO, double minTotQueryCov, int minUncovLen=5, bint debug=0):
    if debug:
        print("\nextract_query_pfam_arch :: START")
        print(f"qArr:\t{qArr.size}")
        # print(f"tArr:\t{tArr.size}")
        # print(f"qstartArr:\t{qstartArr.size}")
        # print(f"qendArr:\t{qendArr.size}")
        # print(f"qlenArr:\t{qlenArr.size}")
        # print(f"minUncovLen:\t{minUncovLen}")

    # NOTE: minUncovLen was set to 5 as the short domain in PFam seed is 7aa

    # The input dataframe contains the following columns
    # query target qstart qend tstart tend alnlen mismatch qlen tlen qcov tcov bits avgcov mismatchratio
    # A0A1D8PMJ1 PF08701.12 14 89 1 76 76 31 526 76 0.144043 1.0 88 0.571777 0.407959

    # The output architecture should contain the following columns
    # query qlen totqcov uniq_clans uniq_doms tot_doms missing_doms repeated_doms max_repeated_doms arch arch_boundaries arch_size arch_complexity
    # at the end we want a lines similar to:
    # A0A2K4Z9M4 163 0.877 1 2 2 1 0 1 3.30.70.260/FF/21796,3.30.70.260/FF/21507,m:157:163 14:91,92:156,157:163 3 0.246

    # The line describing the architecture should have the following columns:
    #HDR query qlen totqcov uniq_clans uniq_doms tot_doms missing_doms repeated_doms max_repeated_doms arch arch_boundaries arch_size arch_complexity
    # query: ID of the query
    # qlen: query length
    # totqcov: total coverage for the query (based on actual boundaries for each accepted or missing profile)
    # uniq_clans: number of pfam clans appearing one or more times in the architecture
    # uniq_doms: number of domains appearing one or more times in the architecture
    # tot_doms: number of domains composing the architecture
    # missing_doms: number of interregions with no matching domain in the architecture
    # repeated_doms: number of pfam domains with multiple hits across the query
    # max_repeated_doms: max number of occurrences of a given domain in the arch
    # arch: string with the domain ids composing the architecture, and the start and end positions in the query (it should also include the missing interregions)
    # arch_size: total number of domains in the architecture (including missing)
    # arch_complexity: define some kind of complexity for the architecture
    # This should take into account: totqcov and number of pfam domains. For example a architecture with totqcov=1 and arch_size=1 has complexity 0!

    # Create zeros array set to one for each row that should be removed
    cdef long arrLen = qArr.size
    cdef long masterLoopIdx = 0
    cdef long qSliceStart = 0
    cdef long sliceSize = 0
    # Variable used when checking the overlap
    cdef double tmpAvailCov = 1.
    cdef double totQcov = 0.
    cdef long qstart = 0
    cdef long qend = 0
    # Temporary variable to keep
    # track of the current left boundary
    # when adding uncovered domains
    cdef long leftmostStart = 1
    cdef long uniqDomsCnt, domsCnt, uncovCnt, repeatedDomsCnt, maxRepeatedDoms, archSize
    # Slices of the input array
    # qstartArrSlice: np.ndarray
    cdef cnp.ndarray[cnp.uint32_t] qstartArrSlice
    # qendArrSlice: np.ndarray
    cdef cnp.ndarray[cnp.uint32_t] qendArrSlice
    tArrSlice: np.ndarray
    # Will contain infomation for the current slice as follows
    # (qstart, qend) -> target
    cdef dict sliceDict # dict[tuple[int, int], str]
    cdef list sortedPositions = [] # list[str]
    cdef list sortedTargets # list[tuple[int, int]]
    query = np.str_
    prev = np.str_
    cdef str archStr = ""
    cdef list archList = [] # list[str]
    # Final count for the extrated architectures
    cdef long archCnt = 0
    # will contain a string with the encoded types
    cdef str archTypesStr = ""
    # query qlen totqcov uniq_clans uniq_doms tot_doms missing_doms repeated_doms max_repeated_doms arch arch_boundaries arch_size
    # at the end we want a lines similar to:
    # A0A2K4Z9M4 163 0.877 1 2 2 1 0 1 3.30.70.260/FF/21796,3.30.70.260/FF/21507,m:157:163 14:91,92:156,157:163 3 0.246

    # NOTE: the arch should if the total query coverage is higher then the minimum 
    while masterLoopIdx < arrLen:
        query = qArr[masterLoopIdx]
        # print(f"masterLoopIdx = {masterLoopIdx}")
        # A new query was found
        if query != prev:
            # first record
            if masterLoopIdx == 0:
                pass
            else:
                totQcov = 0.
                qSliceStart = masterLoopIdx - sliceSize
                qlen = qlenArr[qSliceStart] # Because we are working on the prev query
                # print(f"\nArray slice for (prev={prev}, query={query}): [{qSliceStart} - {masterLoopIdx}]; sliceSize={sliceSize}")
                # If there are more than one hit for the current query
                if sliceSize > 1:
                    # extract architecture for query with multiple hits
                    # print(f"debug: extract architecture for multiple-hits ({prev})")
                    # Slice the arrays
                    qstartArrSlice = qstartArr[qSliceStart:masterLoopIdx]
                    qendArrSlice = qendArr[qSliceStart:masterLoopIdx]
                    tArrSlice = tArr[qSliceStart:masterLoopIdx]
                    # Compute the query coverage
                    totQcov = np.sum(qendArrSlice - qstartArrSlice + 1)/ qlen
                    # Skip the arch if needed
                    if totQcov >= minTotQueryCov:
                        # Create a dict with tuples of the positions, and sort it
                        sliceDict = {(qstartArrSlice[i], qendArrSlice[i]):tmpTarget.rsplit(".", 1)[0] for i, tmpTarget in enumerate(tArrSlice)}
                        # Sort the dictionary based on the keys
                        sortedPositions = sorted(sliceDict)
                        # Assign a pfam type to each profile and create the string with the types
                        archTypesStr = "".join([str(profile2type[prof]) for prof in [sliceDict[k] for k in sortedPositions]])
                        sortedTargets = [f"{sliceDict[k]}@{profile2clan[sliceDict[k]]}:{k[0]}-{k[1]}" if sliceDict[k] in profile2clan else f"{sliceDict[k]}:{k[0]}-{k[1]}" for k in sortedPositions]
                        sliceDict.clear()
                        # Initialize the counters
                        archSize = domsCnt = sliceSize
                        uncovCnt = 0
                        # Count the targets using a Counter
                        targetAcc = Counter(tArrSlice)
                        uniqDomsCnt = len(targetAcc)
                        repeatedDomsCnt = len([None for i in targetAcc.values() if i > 1])
                        maxRepeatedDoms = targetAcc.most_common()[0][1]

                        # Add the missing domain
                        for hitIdx, (qstart, qend) in enumerate(sortedPositions):
                            # Set the missing domains
                            # print(f"Set uncovered domains for multiple hits ({prev})! totQcov={totQcov}")
                            archList.append(sortedTargets[hitIdx])
                            if (qstart - leftmostStart) >= minUncovLen:
                                uncovCnt += 1
                                archSize += 1
                                archList.insert(len(archList) - 1, f"m:{leftmostStart}-{qstart-1}")
                            # update the leftmost boundary
                            leftmostStart = qend + 1

                        # add the rightmost missing domain
                        if (qlen - qend) >= minUncovLen:
                            uncovCnt += 1
                            archSize += 1
                            archList.append(f"m:{qend+1}-{qlen}")

                        # write the output line
                        archStr = ",".join(archList)
                        # ofd.write(f"{prev}\t{qlen}\t{totQcov:.3f}\t{uniqDomsCnt}\t{domsCnt}\t{uncovCnt}\t{repeatedDomsCnt}\t{maxRepeatedDoms}\t{archSize}\t{archStr}\n")
                        ofd.write(f"{prev}\t{qlen}\t{totQcov:.3f}\t{uniqDomsCnt}\t{domsCnt}\t{uncovCnt}\t{repeatedDomsCnt}\t{maxRepeatedDoms}\t{archSize}\t{archStr}\t{archTypesStr}\n")
                        archCnt += 1
                        # reset some variables
                        archList.clear()
                        leftmostStart = 1
                # if there is only one hit
                elif sliceSize == 1:
                    # extract architecture for query a single hit
                    # print(f"debug: extract architecture for single-hit ({prev})")
                    # Initialize variables
                    qstart = qstartArr[qSliceStart]
                    qend = qendArr[qSliceStart]
                    # Extract the domain (format it to plain string format)
                    archStr = f"{tArr[qSliceStart]}"
                    # remove pfam id version
                    archStr = archStr.rsplit(".", 1)[0]
                    archTypesStr = str(profile2type[archStr])
                    # add the Domain clan if available
                    if archStr in profile2clan:
                        archStr = f"{archStr}@{profile2clan[archStr]}"
                    # Add the boundaries
                    archStr =  f"{archStr}:{qstart}-{qend}"
                    # one domain only,
                    # these variables are updated if there are uncovered regions
                    archSize = 1
                    uncovCnt = 0
                    # Compute the query coverage
                    totQcov = (qend - qstart + 1) / qlen
                    # Skip the arch if needed
                    if totQcov >= minTotQueryCov:
                        # This might happen when totQcov > 1
                        # if totQcov > 1:
                        #     sys.stderr.write(f"\nERROR: The query {prev} of length {qlen} might be shorter than target.\n")
                        #     sys.exit(-7)

                        # Set the missing domains
                        if totQcov == 1: # no missing domains
                            # print(f"Single domain, totQcov={totQcov}")
                            pass
                        else:
                            # print(f"Set uncovered domains! totQcov={totQcov}")
                            # Check len of left uncovered region
                            if (qstart - 1) >= minUncovLen:
                                uncovCnt += 1
                                archSize += 1
                                archStr =  f"m:1-{qstart-1},{archStr}"

                            # Check len of right uncovered region
                            if (qlen - qend) >= minUncovLen:
                                uncovCnt += 1
                                archSize += 1
                                archStr =  f"{archStr},m:{qend+1}-{qlen}"
                        ofd.write(f"{prev}\t{qlen}\t{totQcov:.3f}\t1\t1\t{uncovCnt}\t0\t0\t{archSize}\t{archStr}\t{archTypesStr}\n")
                        archCnt += 1
                # Computations done for this slice
                sliceSize = 0

        masterLoopIdx += 1
        sliceSize += 1
        prev = query

    # Extract arch for the final slice, if needed
    if sliceSize > 0:
        totQcov = 0.
        qSliceStart = masterLoopIdx - sliceSize
        qlen = qlenArr[qSliceStart] # Because we are working on the prev query
        # print(f"\nArray slice for (prev={prev}, query={query}): [{qSliceStart} - {masterLoopIdx}]; sliceSiz{sliceSize}")
        # If there are more than one hit for the current query
        if sliceSize > 1:
            # extract architecture for query with multiple hits (last slice)
            # print(f"debug: extract architecture for multiple-hits ({prev})")
            # Slice the arrays
            qstartArrSlice = qstartArr[qSliceStart:masterLoopIdx]
            qendArrSlice = qendArr[qSliceStart:masterLoopIdx]
            tArrSlice = tArr[qSliceStart:masterLoopIdx]
            # Compute the query coverage
            totQcov = np.sum(qendArrSlice - qstartArrSlice + 1)/ qlen
            # Skip the arch if needed
            if totQcov >= minTotQueryCov:
                # Create a dict with tuples of the positions, and sort it
                sliceDict = {(qstartArrSlice[i], qendArrSlice[i]):tmpTarget.rsplit(".", 1)[0] for i, tmpTarget in enumerate(tArrSlice)}
                # Sort the dictionary based on the keys
                sortedPositions = sorted(sliceDict)
                archTypesStr = "".join([str(profile2type[prof]) for prof in [sliceDict[k] for k in sortedPositions]])
                # Get a list with the sorted pfam profile ids
                # and add the Pfam clan if available
                # sortedTargets = [sliceDict[k] for k in sortedPositions]
                sortedTargets = [f"{sliceDict[k]}@{profile2clan[sliceDict[k]]}:{k[0]}-{k[1]}" if sliceDict[k] in profile2clan else f"{sliceDict[k]}:{k[0]}-{k[1]}" for k in sortedPositions]
                sliceDict.clear()

                # Initialize the counters
                archSize = domsCnt = sliceSize
                uncovCnt = 0
                # Count the targets using a Counter
                targetAcc = Counter(tArrSlice)
                uniqDomsCnt = len(targetAcc)
                repeatedDomsCnt = len([None for i in targetAcc.values() if i > 1])
                maxRepeatedDoms = targetAcc.most_common()[0][1]

                # Add the missing domain
                for hitIdx, (qstart, qend) in enumerate(sortedPositions):
                    # Set the missing domains
                    # print(f"Set uncovered domains for multiple hits ({prev})! totQcov={totQcov}")
                    archList.append(sortedTargets[hitIdx])
                    if (qstart - leftmostStart) >= minUncovLen:
                        uncovCnt += 1
                        archSize += 1
                        archList.insert(len(archList) - 1, f"m:{leftmostStart}-{qstart-1}")
                    # update the leftmost boundary
                    leftmostStart = qend + 1

                # add the rightmost missing domain
                if (qlen - qend) >= minUncovLen:
                    uncovCnt += 1
                    archSize += 1
                    archList.append(f"m:{qend+1}-{qlen}")

                # write the output line
                archStr = ",".join(archList)
                ofd.write(f"{prev}\t{qlen}\t{totQcov:.3f}\t{uniqDomsCnt}\t{domsCnt}\t{uncovCnt}\t{repeatedDomsCnt}\t{maxRepeatedDoms}\t{archSize}\t{archStr}\t{archTypesStr}\n")
                archCnt += 1
                # reset some variables
                archList.clear()
                leftmostStart = 1
        # if there is only one hit
        elif sliceSize == 1:
            # extract architecture for query a single hit
            # print(f"debug: extract architecture for single-hit ({prev})")
            # Initialize variables
            qstart = qstartArr[qSliceStart]
            qend = qendArr[qSliceStart]
            # Extract the domain (format it to plain string format)
            archStr = f"{tArr[qSliceStart]}"
            # remove pfam id version
            archStr = archStr.rsplit(".", 1)[0]
            archTypesStr = str(profile2type[archStr])
            # add the Domain clan if available
            if archStr in profile2clan:
                archStr = f"{archStr}@{profile2clan[archStr]}"
            # Add the boundaries
            archStr =  f"{archStr}:{qstart}-{qend}"
            # one domain only,
            # these variables are updated if there are uncovered regions
            archSize = 1
            uncovCnt = 0
            # Compute the query coverage
            totQcov = (qend - qstart + 1) / qlen
            # Skip the arch if needed
            if totQcov >= minTotQueryCov:
                # print(totQcov)
                # print(qend - qstart + 1)
                # print(f"qstart={qstart}; qend={qend}; qlen={qlen}; totQcov={totQcov}")
                # This might happen when totQcov > 1
                # if totQcov > 1:
                #     sys.stderr.write(f"\nERROR: The query {prev} of length {qlen} might be shorter than target.\n")
                #     sys.exit(-7)

                # Set the missing domains
                if totQcov == 1: # no missing domains
                    # print(f"Single domain, totQcov={totQcov}")
                    pass
                else:
                    # print(f"Set uncovered domains! totQcov={totQcov}")
                    # Check len of left uncovered region
                    if (qstart - 1) >= minUncovLen:
                        uncovCnt += 1
                        archSize += 1
                        archStr =  f"m:1-{qstart-1},{archStr}"

                    # Check len of right uncovered region
                    if (qlen - qend) >= minUncovLen:
                        uncovCnt += 1
                        archSize += 1
                        archStr =  f"{archStr},m:{qend+1}-{qlen}"
                # Write the output line
                ofd.write(f"{prev}\t{qlen}\t{totQcov:.3f}\t1\t1\t{uncovCnt}\t0\t0\t{archSize}\t{archStr}\t{archTypesStr}\n")
                archCnt += 1

    return archCnt



# cdef cnp.ndarray[cnp.int64_t] find_overlaps(np.ndarray[np.str_] qArr, cnp.ndarray[cnp.uint32_t] qstartArr, cnp.ndarray[cnp.uint32_t] qendArr, cnp.ndarray[cnp.float64_t] qcovArr):
cdef cnp.ndarray[cnp.int64_t] find_overlaps(qArr: np.ndarray, cnp.ndarray[cnp.uint32_t] qstartArr, cnp.ndarray[cnp.uint32_t] qendArr, cnp.ndarray[cnp.float64_t] qcovArr):
    """
    Identify profile overlaps, and return an array with the indexes to be removed
    """

    # Create zeros array set to one for each row that should be removed
    cdef unsigned long arrLen = qArr.size
    cdef unsigned long masterLoopIdx = 0
    cdef unsigned long qSliceStart = 0
    cdef unsigned long sliceSize = 0
    # array with with 0 if no ovelap, 1 otherwise
    # overlapIdxs: np.ndarray = np.zeros(arrLen, dtype=np.uint8)
    cdef cnp.ndarray[cnp.uint8_t] overlapIdxs = np.zeros(arrLen, dtype=np.uint8)
    cdef cnp.uint32_t[:] qstartArrSlice
    cdef cnp.uint32_t[:] qendArrSlice
    cdef cnp.float64_t[:] qcovArrSlice

    # idxsWithOverlaps: np.ndarray
    query = np.str_
    prev = np.str_

    while masterLoopIdx < arrLen:
        query = qArr[masterLoopIdx]
        # print(f"masterLoopIdx = {masterLoopIdx}")
        # print(f"\nprev == query:\t{prev == query}")
        # print(f"query = {query}, prev = {prev}")

        # A new query was found
        if query != prev:
            # first record
            if masterLoopIdx == 0:
                pass
            else:
                # Version optimizied
                qSliceStart = masterLoopIdx - sliceSize
                # print(f"Array slice for (prev={prev}, query={query}): [{qSliceStart} - {masterLoopIdx}]; sliceSize={sliceSize}, sliceSize={sliceSize}")

                # If there are at least hits for the current query
                if sliceSize > 1:
                    # Check the overlaps
                    # Create the views of slices
                    qstartArrSlice = qstartArr[qSliceStart:masterLoopIdx]
                    qendArrSlice = qendArr[qSliceStart:masterLoopIdx]
                    qcovArrSlice = qcovArr[qSliceStart:masterLoopIdx]
                    idxsWithOverlaps: np.ndarray = domain_overlap_slice(qstartArrSlice, qendArrSlice, qcovArrSlice)
                    # Update the indexes that should be removed to 1
                    idxsWithOverlaps = idxsWithOverlaps + qSliceStart # add the offset
                    np.add.at(overlapIdxs, idxsWithOverlaps, 1)
                    # print(f"Check overlaps for {prev}: {qcovArr[qSliceStart:masterLoopIdx]}")
                    # print(idxsWithOverlaps)
                sliceSize = 0
                # else:
                #     print(f"Single entry for {prev} no overlap!")

        masterLoopIdx += 1
        sliceSize += 1
        prev = query

    # Check overlaps for last slice
    qSliceStart = masterLoopIdx - sliceSize
    if sliceSize > 1:
        # print(f"Last array slice: (prev={prev}, query={query}): [{qSliceStart} - {masterLoopIdx}]; sliceSize={sliceSize}")
        # Check the overlaps
        qstartArrSlice = qstartArr[qSliceStart:masterLoopIdx]
        qendArrSlice = qendArr[qSliceStart:masterLoopIdx]
        qcovArrSlice = qcovArr[qSliceStart:masterLoopIdx]
        idxsWithOverlaps: np.ndarray = domain_overlap_slice(qstartArrSlice, qendArrSlice, qcovArrSlice)

        # Update the indexes that should be removed to 1
        idxsWithOverlaps = idxsWithOverlaps + qSliceStart # add the offset
        np.add.at(overlapIdxs, idxsWithOverlaps, 1)

    # return the array with indexes with overlaps
    return overlapIdxs.nonzero()[0] # np.ndarray[np.int64_t]



# def index_profile_db(profilePath: str, tmpDir: str, flogger: logging.Logger, kmer: int = 5, sens: float = 7.0, threads: int = 4) -> None:
cdef void index_profile_db(str profilePath, str tmpDir, object flogger, int kmer = 5, double sens = 7.0, int threads = 4):
    """Index a profile database."""
    debugStr: str = f"""index_profile_db :: START
    Profile DB path:\t{profilePath}
    Tmp dir: {tmpDir}
    File logger: {flogger}
    k-mer:\t{kmer}
    Sensitivity:\t{sens}
    Threads:\t{threads}"""
    logger.debug(debugStr)

    # Index the profile DB
    makedir(tmpDir)
    logger.info("Indexing the profile database, be patient...")
    # mmseqs createindex <path/to/profile-db> </path/to/tmp/> -k 5 -s 7 --threads 6 -v 3
    indexCmd: str = f"{get_mmseqs_path()} createindex {profilePath} {tmpDir} -k {kmer} -s {sens} --threads {threads} -v 3"
    process: subprocess.Popen = subprocess.Popen(indexCmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout_val: bytes
    stderr_val: bytes
    stdout_val, stderr_val = process.communicate() #get stdout and stderr
    process.wait()
    logger.debug(f"STDOUT:\n{stdout_val.decode()}\n\
        STDERR:\n{stderr_val.decode()}\n")
    # Write also in the log file
    if flogger is not None:
        flogger.log(logger.level, f"STDOUT:\n{stdout_val.decode()}\n\
        STDERR:\n{stderr_val.decode()}\n")
    # Remove the temporary directory
    try:
        rmtree(path=tmpDir)
    except OSError:
        sleep(1)
        rmtree(path=tmpDir, ignore_errors=True)  # solve shutil NFS bug, ignore errors, file removal is less important



cdef (double, double) mmseqs_pfam_profile_search(str queryPath, str pfamProfPath, str outDir, str dbDir, unsigned int kmer = 5, double sens = 7.0, unsigned int threads = 4, bint cleanUp = 0):
    """Search PFamA profile DB using MMseqs2."""
    debugStr: str = f"""mmseqs_pfam_profile_search :: START
    Query FASTA file: {queryPath}
    PFamA profile DB: {pfamProfPath}
    Output directory: {outDir}
    Directory with MMseqs2 query DB files: {dbDir}
    KMER value for Profile search:\t{kmer}
    MMseqs2 sensitivity (-s):\t{sens}
    Threads:\t{threads}
    Remove temporary files:\t{cleanUp}"""
    logger.debug(debugStr)

    #check that the input file and the database exist
    if not os.path.isfile(queryPath):
        logger.error(f"The query file{queryPath}\nwas not found, please provide the path to a valid FASTA file")
        sys.exit(-2)
    if not os.path.isfile(pfamProfPath):
        logger.error(f"The target databse file\n{pfamProfPath}\nwas not found, please provide a valid path file")
        sys.exit(-2)

    # check that the sensitivity is in a valid range
    if sens < 5.7:
        logger.warning(f"The sensitivity value ({sens}) should not be below 5.7. It will be set to default value of 7.0\n")
        sens = 7.0
    elif sens > 7.5:
        logger.warning(f"The sensitivity value ({sens}) cannot be higher than 7.5. It will be set to default value of 7.0\n")
        sens = 7.0

    # create directory if not previously created
    makedir(outDir)
    makedir(dbDir)
    # check the query db name
    queryBname: str = os.path.basename(queryPath)
    queryDbPath: str = os.path.join(dbDir, f"{queryBname}.mmseqs2db")
    # create the database if does not exist yet
    # NOTE: the indexing is not needed because this is only a query DB
    if not os.path.isfile(queryDbPath):
        mmseqs_createdb(queryPath, outDir=dbDir, dbType=1, debug=True)
    # validate the profile DB files
    pfamDbName: str = os.path.basename(pfamProfPath)
    validate_profile_db(bname=pfamDbName, dirPath=os.path.dirname(pfamProfPath), indexed=1)
    # set output name
    profSearchName: str = f"{queryBname}-{pfamDbName}"
    # set the tmp dir
    tmpProfSearchDir: str = os.path.join(outDir, profSearchName)
    makedir(tmpProfSearchDir)
    rawOutPath: str = os.path.join(tmpProfSearchDir, f"{profSearchName}.raw")
    blastOutPath: str = os.path.join(outDir, f"{profSearchName}.blast.tsv")
    # start measuring the execution time
    cdef double start_time = 0.0
    start_time = perf_counter()

    '''
    # NOTE: In the search command, the coverage filtering should be applied.
    # for example: --cov-mode 1 -c 0.8 (c should be a parameter)
    # This has two advanges:
    # Reduces execution times by 5~10%
    # Downstream analysis is faster as output files are smaller
    '''

    # NOTE: workfloat from MMseqs manual:
    '''
    mmseqs createdb targetDB.fasta targetDB
    mmseqs createindex targetDB tmp
    mmseqs touchdb targetDB
    # alternative using vmtouch
    vmtouch -l -d -t targetDB.idx
    Once the database is in memory it is possible to run instant searches against it by using the
    --db-load-mode 2
    mmseqs search queryDB targetDB aln tmp --db-load-mode 2
    mmseqs convertalis queryDB targetDB aln aln.m8 --db-load-mode 2
    '''

    # command to be executed
    profSearchCmd: str = f"{get_mmseqs_path()} search {queryDbPath} {pfamProfPath} {rawOutPath} {tmpProfSearchDir} -s {sens} -k {kmer:d} --threads {threads:d} -v 0 --alignment-mode 2 --db-load-mode 2 --alt-ali 10 --search-type 1"
    # print(profSearchCmd)
    completedProc: subprocess.CompletedProcess = subprocess.run(profSearchCmd, shell=True, capture_output=True)
    if completedProc.returncode != 0:
        logger.error(f"MMseqs profile search failed with exit code {completedProc.returncode}\n{completedProc.stderr}")

    logger.debug(completedProc.args)
    # stop measuring the execution time
    cdef double end_search, search_time, convert_time
    end_search = perf_counter()
    search_time = round(end_search - start_time, 2)
    logger.debug(f"Profile search for {queryBname:s} took {search_time:.2f} seconds.")
    # convert the output to tab-separated BLAST output
    # EXAMPLE: mmseqs convertalis query.db target.db query_target_rawout query_target_blastout
    # Only output specific files in the BLAST-formatted output
    columns: str = "query,target,qstart,qend,tstart,tend,alnlen,mismatch,qlen,tlen,qcov,tcov,bits"
    # perform the file conversion
    convertCmd: str = f"{get_mmseqs_path():s} convertalis {queryDbPath:s} {pfamProfPath:s} {rawOutPath:s} {blastOutPath:s} -v 0 --search-type 1 --format-output {columns:s} --threads {threads:d}"
    completedProc = subprocess.run(convertCmd, shell=True, capture_output=True)
    if completedProc.returncode != 0:
        logger.error(f"MMseqs convertalis failed with exit code {completedProc.returncode}\n{completedProc.stderr}")
        sys.exit(-10)
    logger.debug(completedProc.args)
    # conversion exec time
    convert_time = round(perf_counter() - end_search, 2)
    # remove tmp dir
    if cleanUp:
        try:
            rmtree(path=tmpProfSearchDir)
        except OSError:
            sleep(1)
            rmtree(path=tmpProfSearchDir, ignore_errors=True)  # solve shutil NFS bug, ignore errors, file removal is less important

    # Return the output informations
    return (search_time, convert_time)



cpdef void obtain_precomputed_profiles(str archivePath, str outDir, unsigned int kmer = 5, double sens = 7.0, unsigned int threads = 4, bint index = 0, bint writeLog = 1):
    """Obtain precomputed profile database"""
    # Set the log file path
    logPath: str = os.path.join(outDir, "log.obtain_precomputed_profiles.txt")
    cdef unsigned long currentLev = logger.level
    debugStr: str = f"""obtain_precomputed_profiles :: START
    Archive with profile DB: {archivePath}
    Output directory: {outDir}
    KMER:\t{kmer}
    Sensitivity:\t{sens}
    Threads:\t{threads}
    Index DB:\t{index}
    Write log:\t{writeLog}"""
    logger.debug(debugStr)

    # Set the file logger
    flogger: logging.Logger = logging.Logger("")
    if writeLog:
        flogger = systools.create_flogger(logPath, loggerName=f"{__name__}.file_logger", lev=currentLev, mode="a", propagate=False)
    if writeLog:
        flogger.log(20, debugStr)

    # Extract the archive in the output directory
    systools.untar(archivePath, outDir=outDir)
    # Set the path to the profile database
    dbPath: str = os.path.join(outDir, "pfama.mmseqs")
    # Index the profile database
    if index:
        idxTmpDir: str = os.path.join(outDir, "tmp-indexing")
        index_profile_db(profilePath=dbPath, tmpDir=idxTmpDir, flogger=flogger, kmer=kmer, sens=sens, threads=threads)



# def pfam_hits2architecture(blastResults:str, outDir:str, seqCnt:int, minbits:int=30, minUncovLen:int=5,  mintcov:float=0.75, minTotQueryCov: float = 0.10) -> tuple[float, int, float, int, float, int, float]:
cdef (double, int, double, int, double, int, double) pfam_hits2architecture(str blastResults, str outDir, long seqCnt, long minbits=30, long minUncovLen=5, double mintcov=0.75, double minTotQueryCov=0.0, bint settingsInFileNames=0):
    """
        Collapse multiple pfam domain hits, to cover the query without overlaps
        blastResults: Path to the file with MMseqs2 output of profile search in Blast tab-delimited format.
        outDir: Main output directory.
        seqCnt: proteins in the input proteome.
        minbits: bitscore threshold.
        minUncovLen (int): minimum length for uncovered interregions.
        mintcov: minimum target coverage.
        minTotQueryCov: Minimum total query coverage.
        settingsInFileNames (bint): Include the run settings in output file names
    """
    cdef bint debug = 0
    '''
    if debug:
        print("\npfam_hits2architecture :: START")
        print(f"Raw profile hits: {blastResults}")
        print(f"Output directory: {outDir}")
        print(f"Proteins in the input proteome (must be > 0):\t{seqCnt}")
        print(f"Min bitscore:\t{minbits}")
        print(f"Minimum lenght uncovered interregions (aa):\t{minUncovLen}")
        print(f"Minimum profile coverage:\t{mintcov}")
        print(f"Minimum total query coverage:\t{minTotQueryCov:.2f}")
        print(f"Include run info in output file names:\t{settingsInFileNames}")
    '''

    if not os.path.isfile(blastResults):
        sys.stderr.write(f"\nERROR: the path with profile hits\n{blastResults}\nwas not found.")
        sys.exit(-2)

    # define some tmp variables
    cdef long rawHitsCnt = 0
    cdef long usableHitsCnt = 0
    cdef long archCnt = 0
    cdef double startTime, pfamHits2ArchsTime
    cdef double pctQueryWithRawHits, pctQueryWithUsableHits, pctQueryWithArchs
    # obtain the basename and remove 'blast.tsv'
    cdef str bname = os.path.basename(blastResults)[:-10]
    # Create the output file and write the HDR
    cdef str mintcovStr = f"{mintcov:.2f}".replace(".", "")
    cdef str minTotQueryCovStr = f"{minTotQueryCov:.2f}".replace(".", "")
    cdef str archPath = os.path.join(outDir, f"{bname}.archs.tsv")
    # Include run settings in output files
    if settingsInFileNames:
        archPath = os.path.join(outDir, f"{bname}.bits{minbits}.tcov{mintcovStr}.mulen{minUncovLen}.qcov{minTotQueryCovStr}.tsv")
    # start timing the execution
    startTime = perf_counter()
    # Create file with archs
    makedir(outDir)
    ofd: TextIO = open(archPath, "wt")
    # ofd.write("query\tqlen\ttotqcov\tuniq_doms\ttot_doms\tmissing_doms\trepeated_doms\tmax_repeated_doms\tarch_size\tarch\n")
    ofd.write("query\tqlen\ttotqcov\tuniq_doms\ttot_doms\tmissing_doms\trepeated_doms\tmax_repeated_doms\tarch_size\tarch\tarch_types\n")
    # The line describing the architecture should have the following columns:
    # query: ID of the query
    # qlen: query length
    # totqcov: total coverage for the query (based on actual boundaries for each accepted or missing profile)
    # uniq_clans: number of pfam clans appearing one or more times in the architecture
    # uniq_doms: number of domains appearing one or more times in the architecture
    # tot_doms: number of domains composing the architecture
    # missing_doms: number of interregions with no matching domain in the architecture
    # repeated_doms: number of pfam domains with multiple hits across the query
    # max_repeated_doms: max number of occurrences of a given domain in the arch
    # arch: string with the domain ids composing the architecture (it should also include the missing interregions)
    # arch_boundaries: string with start and end position of each domain and empty interregion in the architecture
    # arch_size: total number of domains in the architecture (including missing)
    # arch_complexity: define some kind of complexity for the architecture
    # This should take into account: totqcov and number of pfam domains. For example a architecture with totqcov=1 and arch_size=1 has complexity 0!

    # HDR: query target qstart qend tstart tend alnlen mismatch qlen tlen qcov tcov bits
    # H7C6D5 3.40.50.300/FF/627498 1 250 29 284 256 88 370 343 0.676 0.746 329

    # Load, filter, sort and modify the dataframe
    # NOTE: tstart and tend are not really used,
    # this should be not included in the mmseqs output, and not loaded
    colNames: list[str] = ["query", "target", "qstart", "qend", "tstart", "tend", "alnlen", "mismatch", "qlen", "tlen", "qcov", "tcov", "bits"]
    df = read_csv(blastResults, sep="\t", names=colNames, dtype= {"query": str, "target": "str", "qstart": np.uint32, "qend": np.uint32, "tstart": np.uint32, "tend": np.uint32, "alnlen": np.uint32, "mismatch": np.uint32,  "qlen": np.uint32, "tlen": np.uint32, "qcov": np.float64,  "tcov": np.float64, "bits": np.uint32}, engine="c")

    # Set of the initial number of entries
    rawHitsCnt = df.shape[0]
    # Variables to be returned
    # tot_raw_hits -> rawHitsCnt
    pctQueryWithRawHits = (unique(df["query"]).size / seqCnt) * 100.
    # NOTE: avgcov and mismatch-ratio are not used for now actually usable...
    # consider removing them from the the call to convertalis and other downstream steps
    # Keep only entries satisfying the input parameter thresholds
    df = df[(df["tcov"] >= mintcov) & (df["bits"] >= minbits)]
    # compute the column with the average coverage
    # NOTE: adding using the df["avgCov"] =<new column> would cause Warnings about Df copy
    df.insert(df.shape[1], "avgcov", ((df.qcov.to_numpy() + df.tcov.to_numpy())/2.).astype(np.float64))
    # Add the new column as a rightmost colum
    df.insert(df.shape[1], "mismatchratio", (df.mismatch.to_numpy()/df.alnlen.to_numpy()).astype(np.float64))
    # Drop the mismatch and alnlen columns as from now on these will not be directly used
    df.drop(columns=["mismatch", "alnlen", "tstart", "tend", "tlen"], axis=0, inplace=True)
    # sort inplace
    df.sort_values(by=["query", "bits", "tcov", "mismatchratio", "avgcov"], axis=0, ascending=[True, False, False, True, False], inplace=True, ignore_index=True)

    # Write the CSV before checking the overlaps
    # cdef str dummyPath = os.path.join(outDir, f"{bname}.filtered.{minbits}bits_tcov{mintcovStr}.tsv")
    # df.to_csv(dummyPath, sep="\t", index=False)
    # Find and remove hits with overlaps

    # initialize the arrays to be passed to find overlap
    # idxsWithOverlaps: np.ndarray = find_overlaps(df["query"].to_numpy(dtype=np.str_), df["qstart"].to_numpy(dtype=np.uint32), df["qend"].to_numpy(dtype=np.uint32), df["qcov"].to_numpy(dtype=np.float64))
    cdef cnp.ndarray[cnp.int64_t] idxsWithOverlaps = find_overlaps(df["query"].to_numpy(dtype=np.str_), df["qstart"].to_numpy(dtype=np.uint32), df["qend"].to_numpy(dtype=np.uint32), df["qcov"].to_numpy(dtype=np.float64))

    df.drop(labels=idxsWithOverlaps, axis=0, inplace=True)
    # Write table after removing the overlaps
    # dummyPath = os.path.join(outDir, f"{bname}.no-overlaps.{minbits}bits_tcov{mintcovStr}.tsv")
    # df.to_csv(dummyPath, sep="\t", index=False)
    # These are hits above thr and without overlaps
    usableHitsCnt = df.shape[0]
    pctQueryWithUsableHits = (unique(df["query"]).size / seqCnt) * 100.

    # Locate the file with mapping dictionaries for profiles
    pcklPath: str = os.path.dirname(__file__)
    pcklPath = os.path.join(pcklPath, "bin/profile2clan.pckl")
    prof2clanDict: dict[str, str] = {}

    if not os.path.isfile(pcklPath):
        sys.stderr.write(f"\nERROR: the file {pcklPath}\nwith the mapping dictionary for profiles, was not found.\nTerminating execution...\n")
        sys.exit(-2)
    else:
        with open(pcklPath, "br") as fd:
            profile2clanDict = load(fd)

    # Load pickle with profile types
    # The PFamA types are encoded as follows
    # Family -> 1
    # Domain -> 2
    # Repeat -> 3
    # Coiled-coil -> 4
    # Motif -> 5
    # Disordered -> 6
    cdef dict profile2typeDict = {} # dict[str, int]
    pcklPath = os.path.join(os.path.dirname(pcklPath), "profile2type.pckl")
    if not os.path.isfile(pcklPath):
        sys.stderr.write(f"\nERROR: the file {pcklPath}\nwith the mapping of profiles to types, was not found.\nTerminating execution...\n")
        sys.exit(-2)
    else:
        with open(pcklPath, "br") as fd:
            profile2typeDict = load(fd)

    # Extract the architectures
    archCnt = extract_query_pfam_arch(df["query"].to_numpy(dtype=np.str_), df["target"].to_numpy(dtype=np.str_), df["qstart"].to_numpy(dtype=np.uint32), df["qend"].to_numpy(dtype=np.uint32), df["qlen"].to_numpy(dtype=np.uint32), profile2clan=profile2clanDict, profile2type=profile2typeDict, ofd=ofd, minTotQueryCov=minTotQueryCov, minUncovLen=minUncovLen, debug=debug)
    del df
    # Close the output file
    ofd.close()
    # Compute ex time
    pfamHits2ArchsTime = round(perf_counter() - startTime, 2)
    # logger.debug(f"Arch extraction for  {bname:s} took {pfamHits2ArchsTime:.2f} seconds.")
    # sys.exit("DEBUG :: pfam_hits2architecture")

    # Compute ratio of queries with at least an arch
    pctQueryWithArchs = (archCnt / seqCnt) * 100.
    '''
    if debug:
        print(f"\nSummary on arch extraction for {bname}")
        print(f"Input hits:\t{rawHitsCnt}")
        print(f"% of queries with hits (unfiltered):\t{pctQueryWithRawHits}")
        print(f"Used hits:\t{usableHitsCnt}")
        print(f"% of queries with hits (tcov > {mintcov}; bitscore > {minbits}):\t{pctQueryWithUsableHits}")
        print(f"Overlaps found:\t{len(idxsWithOverlaps)}")
        print(f"Removed hits (thrs and overlaps):\t{rawHitsCnt - usableHitsCnt}")
        print(f"Extracted archs:\t{archCnt}")
        print(f"% of queries with a architecture:\t{pctQueryWithArchs}")
        print(f"Arch extraction for {bname:s} took {pfamHits2ArchsTime:.2f} seconds.")
    '''
    # sys.exit("DEBUG: pfam_hits2architecture")

    # pfamHits2ArchsTime: ex time for extraction
    # rawHitsCnt: total profile search hits before filtering
    # pctQueryWithRawHits: ratio of proteome with at least one hit (before filtering)
    # usableHitsCnt: number of hits after filtering by minimum bitscore and minimum target coverage
    # pctQueryWithUsableHits: ratio of proteome with at least one hit (after filtering)
    # archCnt: total number of architectures for the proteome
    # pctQueryWithArchs: ratio of proteome with architecture
    return (pfamHits2ArchsTime, rawHitsCnt, pctQueryWithRawHits, usableHitsCnt, pctQueryWithUsableHits, archCnt, pctQueryWithArchs)



cdef (double, double, double, int, double, int, double, int, double) profile_search_1pass(str queryName, str pfamProfPath, str profSearchOutDir, str archsOutDir, str dbDir, str runDir, long seqCnt=0, long kmer=5, double sens=7.0, long minBitscore=30, long minUncovLen=5, double minTargetCov=0.70, long missingBinSize=1, double minTotQueryCov=0.75, bint noArchs=0, bint compress=0, long complev=5, long threads=4):
    """Perform profile search using MMseqs and parse the results."""
    debugStr: str = f"""profile_search_1pass :: START
    Query FASTA file: {queryName}
    PFamA profile DB: {pfamProfPath}
    Directory profile searches: {profSearchOutDir}
    Directory with extracted architectures: {archsOutDir}
    Directory with MMseqs2 query DB files:{dbDir}
    Directory with run supplementary files: {runDir}
    Protein count (must be > 0):\t{seqCnt}
    KMER value for Profile search:\t{kmer}
    MMseqs2 sensitivity (-s):\t{sens}
    Minimum bitscore:\t{minBitscore}
    minUncovLen (int): minimum length for uncovered interregions.
    Minimum target coverage (%):\t{minTargetCov}
    Missing bin size:\t{missingBinSize}
    Skip arch extraction:\t{noArchs}
    Compress output:\t{compress}
    Compression level:\t{complev}
    Threads:\t{threads}"""
    logger.debug(debugStr)

    cdef double searchTime, convertTime, parseTime
    # extract job information
    auxDir: str = os.path.join(runDir, "aux")
    mappedInDir: str = os.path.join(auxDir, "mapped_input")
    querySeq: str = os.path.join(mappedInDir, queryName)
    searchTime = 0.
    convertTime = 0.
    parseTime = 0.
    profSearchName: str = f"{queryName}-{os.path.basename(pfamProfPath)}"
    tmpProfSearchDir: str = os.path.join(profSearchOutDir, profSearchName)
    # set the tmp dir
    tmpMMseqsDir: str = os.path.join(tmpProfSearchDir, f"tmp_{queryName}")
    makedir(tmpProfSearchDir)
    makedir(tmpMMseqsDir)
    blastOutPath: str = os.path.join(profSearchOutDir, f"{profSearchName}.blast.tsv")

    searchTime, convertTime = mmseqs_pfam_profile_search(queryPath=querySeq, pfamProfPath=pfamProfPath, outDir=profSearchOutDir, dbDir=dbDir, kmer=kmer, sens=sens, threads=threads, cleanUp=True)
    cdef double pfamHits2ArchsTime, pctQueryWithRawHits, pctQueryWithUsableHits, pctQueryWithArchs
    cdef long rawHitsCnt, usableHitsCnt, archCnt

    # Skip extraction of architectures
    if noArchs:
        return (searchTime, convertTime, 0.0, 0, 0.0, 0, 0.0, 0, 0.0)

    pfamHits2ArchsTime, rawHitsCnt, pctQueryWithRawHits, usableHitsCnt, pctQueryWithUsableHits, archCnt, pctQueryWithArchs = pfam_hits2architecture(blastResults=blastOutPath, outDir=archsOutDir, seqCnt=seqCnt, minbits=minBitscore, minUncovLen=minUncovLen, mintcov=minTargetCov, minTotQueryCov=minTotQueryCov, settingsInFileNames=0)

    return (searchTime, convertTime, pfamHits2ArchsTime, rawHitsCnt, pctQueryWithRawHits, usableHitsCnt, pctQueryWithUsableHits, archCnt, pctQueryWithArchs)



cdef void validate_profile_db(str bname, str dirPath, bint indexed = 0):
    """Check that all the required files for the profile database were created."""
    debugStr: str = f"""validate_profile_db :: START
    Profile basename:\t{bname}
    Profile DB directory: {dirPath}
    Indexed profiles:\t{indexed}"""
    logger.debug(debugStr)

    # Check if the directory with profiles exists
    if not os.path.isdir(dirPath):
        logger.error(f"The directory with profiles\n{dirPath}\nis not valid!")
        sys.exit(-2)
    cdef str basePath = os.path.join(dirPath, bname)
    cdef str tmpPath = basePath
    # Check the existance of profile db files
    if not os.path.isfile(tmpPath):
        logger.error(f"The profiles DB file\n{tmpPath}\nwas not found!\n\
            Please create the profile database before proceeding.")
        sys.exit(-2)
    # List of files to be checked
    fSuffixes: list[str] = [".dbtype", ".version", ".index", "_h", "_h.dbtype", "_h.index"]
    # Verify all the other files
    for f in fSuffixes:
        tmpPath = f"{basePath}{f}"
        if not os.path.isfile(tmpPath):
            logger.error(f"The profiles DB file\n{tmpPath}\nwas not found!\n\
                Please create the profile database before proceeding.")
            sys.exit(-2)
    # Check the files for the indexes
    if indexed:
        for f in [".idx.index", ".idx", ".idx.dbtype"]:
            tmpPath = f"{basePath}{f}"
            if not os.path.isfile(tmpPath):
                logger.error(f"The indexing file for the profiles DB\n{tmpPath}\nwas not found!\n\
                    Please create the profile database and perform the indexing.")
                sys.exit(-2)



cdef void write_run_info_file(str infoDir, dict infoDict):
    """Write a file summarizing the run settings."""
    logger.debug(f"""write_run_info_file :: START
    Directory with run info:\t{infoDict}
    Parameters: {len(infoDict)}""")
    cdef infoFile, val, info
    infoFile = os.path.join(infoDir, "profile_search.info.txt")
    ofd: TextIO = open(infoFile, "wt")
    for info, val in infoDict.items():
        if info == "Version":
            ofd.write(f"SonicParanoid {val}\n")
        else:
            ofd.write(f"{info}\t{val}\n")
    ofd.close()



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
