# -*- coding: utf-8 -*-
# cython: profile=False
"""
This module contains functions related doc2vec training and documents creation.
"""
from __future__ import annotations

# This to avoid Gitlab pipeline to fail
from libc.stdio cimport FILE, sprintf
from libc.stdlib cimport atoi, atof, atol
from libc.math cimport ceil

cdef extern from "stdio.h":
    FILE *fopen(const char *, const char *)
    int fclose(FILE *)
    ssize_t getline(char **, size_t *, FILE *)

import sys
import os
import time
import gensim
import logging
import multiprocessing as mp
from tqdm import tqdm
from collections import deque, Counter
from subprocess import CompletedProcess, run
from pickle import dump, load
from typing import TextIO
# from pandas import DataFrame, read_csv, unique
from dataclasses import dataclass
import numpy as np
cimport numpy as cnp
cimport cython

# internal modules
# from sonicparanoid import <module_name>


'''
__module_name__ = "d2v"
__source__ = "dev_d2v.pyx"
__author__ = "Salvatore Cosentino"
__license__ = "GPLv3"
__version__ = "0.9"
__maintainer__ = "Cosentino Salvatore"
__email__ = "salvo981@gmail.com"



# @cython.profile(False)
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


''' FIXME: This should be supported in Cython 3.0.0 alpha 11
# https://docs.cython.org/en/latest/src/changes.html

try:
    import typing
    import dataclasses
except ImportError:
    pass  # The modules don't actually have to exists for Cython to use them as annotations

@cython.dataclasses.dataclass
cdef class Arch:
    # NOTE: when defining using cdef
    # assignment of default value on a separate line
    # For example:
    # cdef int a
    # a = 5
    cdef int seqlen
    cdef float coverage
    cdef int size
    cdef cnp.ndarray regState # of type cnp.int_t
    cdef cnp.ndarray regLengths # of type cnp.int_t
    cdef cnp.ndarray phrase # of type cnp.str_t # might not compile...
    cdef cnp.ndarray embedding # of type cnp.float32_t
    cdef long domain_types
'''



'''
# NOTE: these are not working for now, better to use dataclass for now
# and wait for direct dataclass support from Cython 3.0.0 alpha 11

# Try using extension types
cdef class Arch:
    cdef int seqlen
    cdef float coverage
    cdef int size
    cdef cnp.ndarray regState # of type cnp.int_t
    cdef cnp.ndarray regLengths # of type cnp.int_t
    cdef cnp.ndarray phrase # of type cnp.str_t # might not compile...
    cdef cnp.ndarray embedding # of type cnp.float32_t
    cdef long domain_types

    def __init__(self, slen, qcov, archSize, rStates, regLens, tokens, vector, pfamTypes):
        self.seqlen = slen
        self.coverage = qcov
        self.size = archSize
        self.regState = rStates
        self.regLengths = regLens
        self.phrase = tokens
        self.embedding = vector
        self.domain_types = pfamTypes
'''



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


'''
# FIXME consider writing a slimmer version (e.g., containing only: name, coverage, size, domain_types)
@dataclass
class Arch:
    """Domain architecture of protein.

    This dataclass contains information about the domain architecture of a protein.

    Args:
        name: protein id.
        seqlen: protein length.
        coverage: percentage of the protein covered by matched profiles.
        size: size of the architecture (matched profiles, and unknown interregions).
        regState: State of the region: 1 -> domain; 0 -> uncovered
        regLengths: Lengths of the domain or uncovered region
        domains: ndarray containing the matched pfam domains
        domain_types: String of numbers encoding for PFamA types (e.g., Family, profile, disordered etc.)
    """
    name: str
    seqlen: int
    coverage: float
    size: int
    regState: np.ndarray
    regLengths: np.ndarray
    domains: np.ndarray
    domain_types: long


    # FIXME: this should be removed when Cython will natively support dataclass objects
    __annotations__ = {
        'name': str,
        'qlen': int,
        'coverage': float,
        'size': int,
        'regState': np.ndarray,
        'regLengths': np.ndarray,
        'domains': np.ndarray,
        'domain_types': long, # unsigned long
    }
'''

# NOTE: Workers used to consume single jobs
# def consume_assign_vectors2archs(jobs_queue, results_queue, archPcklPath: str, arch2vec: dict[str, cnp.ndarray[cnp.float32_t]], domain2vocabidx: dict[str, int], outDir:str) -> None:
cdef void consume_assign_vectors2archs(object jobs_queue, object results_queue, dict arch2vec, dict domain2vocabidx, str outDir, bint dumpArchDict):
    """
    Assign embeddings to Architectures.
    """

    cdef str archPcklPath
    cdef long spId

    while True:
        archPcklPath = jobs_queue.get(True, 1)

        if archPcklPath is None:
            break
        # Extract the species ID
        spId = int(os.path.basename(archPcklPath).split("-", 1)[0])
        # Put the updated Arch dictionary
        # and the species ID in the output queue
        results_queue.put((spId, assign_vectors2archs(archPcklPath=archPcklPath, arch2vec=arch2vec, domain2vocabidx=domain2vocabidx, outDir=outDir, dumpArchDict=dumpArchDict)))



# def consume_extract_documents(jobs_queue, results_queue, minqcov: float, mbsize:int , outDir:str, skipUnknown: bool) -> None:
cdef void consume_extract_documents(object jobs_queue, object results_queue, double minqcov, int mbsize, str outDir, bint skipUnknown):
    """
    Generate space-formatted documents starting from a file with raw architecture info.
    """

    while True:
        current_raw_path: str = jobs_queue.get(True, 1)
        if current_raw_path is None:
            break

        # Generate a list of documents
        # and store it in the output queue
        results_queue.put(extract_documents(current_raw_path, minqcov=minqcov, mbsize=mbsize, outDir=outDir, skipUnknown=skipUnknown))



# NOTE: Multi-threaded functions
# @cython.profile(False)
# def parallel_assign_vectors2archs(corpusPath: str, model: gensim.models.Doc2Vec, archPcklsPaths: list[str], outDir: str, threads: int = 4):
cdef void parallel_assign_vectors2archs(str corpusPath, object model, list archPcklsPaths, str outDir, bint dumpArchDicts=0, unsigned int threads=4):
    """
    Generate a mapping for document to vectors using the pre-trained model.
    Update the vector field for each Arch object.
    """

    # TODO: Make sure that the ordering
    # with which the Arch pckl paths are processed
    # does not affect the final output

    logger.debug(f"""parallel_assign_vectors2archs :: START
    Path to the corpus: {corpusPath}
    d2v corpus size:\t{model.corpus_count:d}
    Arch sets:\t{len(archPcklsPaths):d}
    Output directory: {outDir}
    Store single updates Arch dictionaries in pickles: {dumpArchDicts}
    Threads:\t{threads:d}""")

    # Tmp vars
    cdef cnp.ndarray[cnp.float32_t] tmpVec
    cdef size_t i
    # this index must start from 0
    # and is used to index the embedding in the model
    cdef long vecidx = 0
    # Will contain the document as a single string
    cdef str tmpDoc
    # These two vector could be useful
    # but fior now are not needed
    # vecidx2doc: dict[int, str] = {}
    doc2vecidx: dict[str, int] = {} # inverted vecidx2doc, might not be needed
    arch2vec: dict[str, cnp.ndarray[cnp.float32_t]] = {}

    '''
    # NOTE: this creates a memory view, which would be more efficient than accually assignning the array
    # for more informationcheck:
    # https://cython.readthedocs.io/en/latest/src/userguide/memoryviews.html
    cdef float[:,:] modelVectors
    modelVectors = model.dv.vectors
    '''

    # define file names and file descriptor pointer in C
    cdef bytes filename_byte_string = corpusPath.encode("UTF-8")
    cdef char* corpusPath_c = filename_byte_string
    #file pointer
    cdef FILE* cfile
    # varibales for files and lines
    cdef char * line = NULL
    cdef size_t l = 0
    cdef ssize_t read

    # Map vectors to documents
    cfile = fopen(corpusPath_c, "rb")
    if cfile == NULL:
        raise FileNotFoundError(2, f"The corpus file could not be found: {corpusPath_c}")

    while True:
        read = getline(&line, &l, cfile)
        if read == -1:
            break

        # Lines in the corpus have the following format:
        # 46 PF13537@CL0052 45 PF00733@CL0039 38
        tmpDoc = line.rstrip(b"\n").decode()
        # Fill the dictionaries
        # vecidx2doc[vecidx] = tmpDoc
        doc2vecidx[tmpDoc] = vecidx
        # Extract the vector from the model
        tmpVec = model.dv[vecidx]
        arch2vec[tmpDoc] = tmpVec
        # Increment the vector index
        vecidx += 1

    '''
    # NOTE: storing these vector might be not necessary
    # as it can be easily obtained from the original model
    # Save the dict mapping archs to vectors
    outPcklPath = os.path.join(outDir, f"arch2vector.mapping.pckl")
    # dump the dictionary
    with open(outPcklPath, "wb") as ofd:
        dump(arch2vec, ofd, protocol=4)
    '''
    cdef str outPcklPath
    # Save the dict mapping archs to vectors
    outPcklPath = os.path.join(outDir, f"doc2vecidx.mapping.pckl")

    # dump the dictionary
    with open(outPcklPath, "wb") as ofd:
        dump(doc2vecidx, ofd, protocol=4)

    # Store the vocubulary and the associated word2vec
    # IDs into a dictionary dict[str, int]
    cdef dict domain2vocabidx = model.wv.key_to_index
    cdef list words = list(domain2vocabidx.keys()) 
    # Compute some simple stats on the vocabulary
    cdef unsigned long vocabSize = len(domain2vocabidx)
    cdef long domCnt = 0
    cdef double pctDomain = 0.0
    cdef double pctMissing = 0.0
    # index to the word in vocubulary
    cdef long wIdx = vocabSize - 1
    cdef str tmpWord
    cdef str firstChar
    # Compute the stats
    for i in range(vocabSize):
        # Check if it is a domain
        tmpWord = words.pop()
        # print(f"{i}\t{wIdx}\t{tmpWord}")
        if domain2vocabidx[tmpWord] != wIdx:
            logger.error(f"Wrong vocabulary idx ({wIdx}) for word {tmpWord}")

        firstChar = tmpWord[0]
        if firstChar == "P" or firstChar == "C":
            # print(f"{i}\t{wIdx}\t{tmpWord}")
            domCnt += 1
        else: # Remove the entry from the dictionary
            domain2vocabidx.pop(tmpWord)
        wIdx -= 1

    ''' FIXME: these information should be extracted in compute_corpus_stats
    cdef long missingCnt = vocabSize - domCnt
    pctDomain = (domCnt / vocabSize) * 100
    pctMissing = 100 - pctDomain

    debugStr: str = f"""Vocabulary stats:
    Size:\t{vocabSize:d}
    Domains:\t{domCnt:d}
    Uncovered regions:\t{missingCnt:d}
    % Domains:\t{pctDomain:.2f}
    % Uncovered:\t{pctMissing:.2f}"""
    logger.info(debugStr)
    ''' 

    # Store the pickle with the dictionary
    cdef str domain2wvidxPcklPath = os.path.join(outDir, "domain2wv_idx.mapping.pckl")
    # dump the dictionary
    with open(domain2wvidxPcklPath, "wb") as ofd:
        dump(domain2vocabidx, ofd, protocol=4)

    # Prepare to update the pickles
    cdef str tmpPcklPath
    # Set the varibales need for parallelization
    cdef double start_time = 0.0
    cdef long jobsCnt = len(archPcklsPaths)

    # create the queue and start adding
    proc_queue: mp.queues.Queue = mp.Queue(maxsize=jobsCnt + threads)
    for tmpPcklPath in archPcklsPaths:
        proc_queue.put(tmpPcklPath)

    # add flags for ended jobs
    for i in range(0, threads):
        sys.stdout.flush()
        proc_queue.put(None)

    # Queue to contain the documents for each file
    results_queue: mp.queues.Queue = mp.Queue(maxsize=jobsCnt)

    # List of running jobs
    cdef list runningJobs = [mp.Process(target=consume_assign_vectors2archs, args=(proc_queue, results_queue, arch2vec, domain2vocabidx, outDir, dumpArchDicts)) for i_ in range(threads)]
    # execute the jobs
    for proc in runningJobs:
        proc.start()

    # calculate cpu-time for alignments
    start_time = time.perf_counter()
    # write some message...
    sys.stdout.write(f"\nAssigning embedding to domain architectures for {jobsCnt} proteomes...")

    cdef long spId
    cdef dict tmpArchDict
    # Master dictionary with all architectures
    # dict[int, dict[int, Arch]]
    # Where the first key is the species ID (1-indexed)
    # The keys to the second dict are protein ids (1-indexed)
    # The value of the inner dictioanry are Arch objects
    cdef dict masterArchsDict = {}

    pbar: tqdm = tqdm(total=jobsCnt, desc="Compute vectors for phrases", unit="phrases", disable=None, smoothing=0.3, ascii=False, miniters=1, mininterval=2.0, colour='green')

    # write output when available
    while True:
        try:
            # results_queue.get(False, 0.01)
            spId, tmpArchDict = results_queue.get(False, 0.01)
            masterArchsDict[spId] = tmpArchDict
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

    # Close the progress bar
    pbar.close()

    # this joins the processes after we got the results
    for proc in runningJobs:
        while proc.is_alive():
            proc.join()

    # Save the pckl with all the vectors
    tmpPcklPath = os.path.join(outDir, "master.archs.dict.pckl")
    # Save the updated arch pickles
    with open(tmpPcklPath, "wb") as ofd:
        dump(masterArchsDict, ofd, protocol=4)

    # stop the counter for the alignment time
    sys.stdout.write(f"\nElapsed time for assigning embeddings to Architectures (seconds):\t{round(time.perf_counter() - start_time, 3)}\n")



# def parallel_extract_documents(rawArchFilePaths: list[str], minqcov: float, mbsize: int, outDocFilePath: str, outDir: str, skipUnknown: bool = False, threads: int = 4) -> None:
cdef void parallel_extract_documents(list rawArchFilePaths, double minqcov, unsigned short mbsize, str outDocFilePath, str outDir, bint skipUnknown=0, unsigned short threads=4):
    """Perform parallel document extraction from files with raw architectures.

    Parameters:
    rawArchFilePath list[str]: paths to files from which documents should be created
    mbsize (int): Size of bins for missing interregions. Ex.: if mbsize=5 missing domains are assigned the word ceil((end-start+1)/mbsize)
    minqcov (float): minimum query coverage (computed considering the interregions with a profile)
    outDocFilePath (str): path to the file in which the documents will be stored
    dbDir (str): Directory which the pickles with infor about the architectures will be stored
    skipUnknown (bint): do include uncovered regions
    threads (unsigned int): Threads

    Returns:
    void

    """

    debugStr: str = f"""parallel_extract_documents :: START
    Files with raw architectures to be processed:\t{len(rawArchFilePaths):d}
    Missing interregion bin size:\t{mbsize:d}
    Minimum query coverage:\t{minqcov:.2f}
    Output file: {outDocFilePath}
    Directory in which pickles will be stored: {outDir}
    Skip uncovered interregions: {skipUnknown}
    Threads:\t{threads:d}"""
    logger.debug(debugStr)

    # reset timers
    cdef double start_time = 0.0
    tmpPath: str = ""
    cdef long jobsCnt = len(rawArchFilePaths)
    # create the queue and start adding
    proc_queue: mp.queues.Queue = mp.Queue(maxsize=jobsCnt + threads)
    for tmpPath in rawArchFilePaths:
        proc_queue.put(tmpPath)

    cdef size_t i = 0
    # add flags for ended jobs
    for i in range(0, threads):
        sys.stdout.flush()
        proc_queue.put(None)

    # Queue to contain the documents for each file
    results_queue: mp.queues.Queue = mp.Queue(maxsize=jobsCnt)

    # List of running jobs
    cdef list runningJobs = [mp.Process(target=consume_extract_documents, args=(proc_queue, results_queue, minqcov, mbsize, outDir, skipUnknown)) for i_ in range(threads)]

    # execute the jobs
    for proc in runningJobs:
        proc.start()

    # calculate cpu-time for alignments
    start_time = time.perf_counter()
    # write some message...
    sys.stdout.write(f"\nConverting {jobsCnt} domain architectures to documents...")

    # All documents will be written in this file
    ofd: TextIO = open(outDocFilePath, "wt") # Default buffering should be ok
    # ofd: TextIO = open(docFilepath, "w", buffering=1)
    cdef list tmpDocList # list[str]

    pbar: tqdm = tqdm(total=jobsCnt, desc="Arch to document conversion", unit="architectures", disable=None, smoothing=0.3, ascii=False, miniters=1, mininterval=2.0, colour='green')

    # write output when available
    while True:
        try:
            tmpDocList = results_queue.get(False, 0.01)
            [ofd.write(d) for d in tmpDocList]
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

    # Close the progress bar
    pbar.close()

    ofd.close()

    # this joins the processes after we got the results
    for proc in runningJobs:
        while proc.is_alive():
            proc.join()

    if not os.path.isfile(outDocFilePath):
        sys.stderr.write(f"WARNING: the file with raw documents\n{outDocFilePath}\nwas not found...")

    # Sort the file with documents to ensure consistency of training set
    # and reproducibility of model training
    tmpPath: str = os.path.join(outDir, f"sorted.{os.path.basename(outDocFilePath)}")
    # use run (or call)
    sortCmdOutput: CompletedProcess = run(f"sort -o {tmpPath} {outDocFilePath}", capture_output=True, shell=True)
    # There was an error during the sorting
    if sortCmdOutput.returncode != 0:
        logger.error(f"An error occurred sorting the raw document files:\n{sortCmdOutput.stderr.decode()}")
        sys.exit(-12)
    # remove the unsorted output and rename
    os.remove(outDocFilePath)
    os.rename(tmpPath, outDocFilePath)

    # stop the counter for the alignment time
    sys.stdout.write(f"\nElapsed time for documents creation (seconds):\t{round(time.perf_counter() - start_time, 3)}\n")



# NOTE: Other functions
# @cython.profile(False)
# def assign_vectors2archs(archPcklPath: str, arch2vec: dict[str, cnp.ndarray[cnp.float32_t]], domain2vocabidx: dict[str, int], outDir: str, dumpArchDict: bool) -> dict[int, Arch]:
cdef dict assign_vectors2archs(str archPcklPath, dict arch2vec, dict domain2vocabidx, str outDir, bint dumpArchDict):
    """
    Given a dictionary with info on arch and a model.
    Update the embedding field with the vector predicted by the d2v model.

    Return (str): path to generated pickle file
    """

    # tmp Variables
    archObj: Arch
    cdef size_t i, j
    tmpWords: list[str] = []
    cdef str tmpDoc
    cdef str pcklBname = os.path.basename(archPcklPath)
    cdef str outPcklPath = os.path.join(outDir, pcklBname)
    cdef long archCnt
    cdef long domCnt

    # Load the pickle
    # The has the following content
    # dict[int, Arch]
    # Where the key is a species id, and values are Arch objects
    cdef dict archDict = load(open(archPcklPath, "rb"))
    archCnt = len(archDict)
    # list containing arch object: list[Arch] 
    cdef list archsList = list(archDict.values())
    # Array that will contain the mappings
    # from domain to vocabulary in model.wv
    cdef cnp.ndarray[cnp.uint32_t] tmpDomWvIdx
    cdef cnp.ndarray[cnp.uint8_t] nzidxs = np.zeros(0, dtype=np.uint8)
    cdef cnp.ndarray[cnp.uint8_t] tmpRegState

    for i in range(archCnt):
        archObj = archsList.pop()
        # tmpDoc = " ".join(getattr(archObj, "phrase").tolist())
        tmpWords = getattr(archObj, "phrase").tolist()
        tmpDoc = " ".join(tmpWords)
        # Set the embedding of the archs
        setattr(archObj, "embedding", arch2vec[tmpDoc])
        # Update the vector mapping a domain to the id in the model.wv vocabulary
        # inizialiaze the array with vocabulary indexes
        domCnt = getattr(archObj, "domCnt")
        tmpDomWvIdx = np.zeros(domCnt, dtype=np.uint32)
        tmpRegState = getattr(archObj, "regState")
        # print(tmpRegState)
        nzidxs = tmpRegState.nonzero()[0].astype(np.uint8)
        # print(nzidxs)

        for j in range(domCnt):
            # Extract a domain
            tmpDoc = tmpWords[nzidxs[j]] # reuse the string
            tmpDomWvIdx[j] = domain2vocabidx[tmpDoc]
        # Update the vector with the domain to vocabulary mapping
        setattr(archObj, "domWvIdx", tmpDomWvIdx)

    # Save the updated arch pickles
    if dumpArchDict:
        with open(outPcklPath, "wb") as ofd:
            dump(archDict, ofd, protocol=4)

    return archDict



def compute_archs_and_embeddings(rawArchFilePaths: list[str], minqcov: float, mbsize: int, outDir: str, skipUnknown: bool = False, maxRep: int = 1, addTags: bool = True, saveAsPickle: bool = False, modelPrefix: str = "d2v_model", algorithm:int=1, vectorSize:int=100, window:int=5, minCnt:int=2, useAllWords:bool=False, epochs:int=50 , dbowWords:int=0, dumpArchDicts:bool=False, threads: int = 4):
    """Perform different tasks starting from the raw Architecture files:
    - Extract documents
    - Create corpus
    - Train d2v
    - Assign embeddings to documents

    """

    '''
    debugStr: str = f"""compute_archs_and_embeddings :: START
    Files with raw architectures to be processed:\t{len(rawArchFilePaths):d}
    Minimum query coverage:\t{minqcov:.2f}
    Missing interregion bin size:\t{mbsize:d}
    Main output directory: {outDir}
    Skip uncovered interregions: {skipUnknown}
    Maximum repeats:\t{maxRep:d}
    Add tags:\t{addTags}
    Save the corpus as iterator:\t{saveAsPickle}
    Model name prefix:\t{modelPrefix}
    Algorithm:\t{algorithm}
    Vector size:\t{vectorSize:d}
    Window size:\t{window}
    Min words count:\t{minCnt}
    Use all words:\t{useAllWords}
    Epochs:\t{epochs}
    DBow-words:\t{dbowWords}
    Store the updated Arch dictionaries in pickles:\t{dumpArchDicts}
    Threads:\t{threads}"""
    logger.debug(debugStr)
    '''

    # Write a file with the profile search settings
    cdef str runInfoFile
    runInfoFile = os.path.join(outDir, "archs2embeddings.info.txt")
    # Fill the dictionary with the required information
    cdef dict infoDict = {"Module:":__name__}
    infoDict["Main output dir:"] = outDir
    infoDict["Architecture files to be processed:"] = str(len(rawArchFilePaths))
    infoDict["Minimum query coverage:"] = str(minqcov)
    infoDict["Missing interregion bin size:"] = str(mbsize)
    infoDict["Skip uncovered interregions:"] = str(skipUnknown)
    infoDict["Maximum repeats in corpus:"] = str(maxRep)
    infoDict["Add tags to corpus:"] = str(addTags)
    infoDict["Save the corpus as iterator:"] = str(saveAsPickle)
    infoDict["Output prefix"] = modelPrefix
    infoDict["Algorithm:"] = str(algorithm)
    infoDict["Vector size:"] = str(vectorSize)
    infoDict["Window size:"] = str(window)
    infoDict["Min word count:"] = str(minCnt)
    infoDict["Use all words:"] = str(useAllWords)
    infoDict["Epochs:"] = str(epochs)
    infoDict["DBow-words:"] = str(dbowWords)
    infoDict["Threads:"] = str(threads)
    write_run_info_file(runInfoFile, infoDict)
    del infoDict, runInfoFile

    # Create the directory where the documents will be stored
    cdef str docsDir, modelsDir
    docsDir = os.path.join(outDir, "documents")
    makedir(docsDir)
    modelsDir = os.path.join(outDir, "models")
    makedir(modelsDir)

    # Create the document from arch files
    # File with unfiltered documents
    cdef str rawDocsFilePath
    rawDocsFilePath = os.path.join(docsDir, "documents.raw.txt")

    # Variables for execution time
    cdef float start_time = time.perf_counter()

    parallel_extract_documents(rawArchFilePaths=rawArchFilePaths, minqcov=minqcov, mbsize=mbsize, outDocFilePath=rawDocsFilePath, outDir=docsDir, skipUnknown=skipUnknown, threads=threads)
    # sys.exit(f"DEBUG :: {__name__} :: Documents extraction done")

    # Create the corpus file from the arw document files
    # File with unfiltered documents
    cdef str corpusFilePath
    corpusFilePath = os.path.join(modelsDir, "corpus.txt")
    create_corpus_file(rawDocFilePath=rawDocsFilePath, outDocFilePath=corpusFilePath, maxRep=maxRep, addTags=addTags, saveAsPickle=saveAsPickle)
    # sys.exit(f"DEBUG :: {__name__} :: Corpus file created")

    # Train the d2v model
    cdef str modelPath
    modelPath = train_d2v_gensim(corpusPath=corpusFilePath, outDir=modelsDir, modelPrefix=modelPrefix, algorithm=algorithm, vectorSize=vectorSize, window=window, minCnt=minCnt, useAllWords=useAllWords, threads=1, epochs=epochs , dbowWords=dbowWords)

    # Assign embeddings to Architectures
    # load the model
    predModel: gensim.models.doc2vec.Doc2Vec = gensim.models.Doc2Vec.load(modelPath, mmap="r")

    # Identify all the document pckl files in the documents directory
    cdef str tmpPath
    # associate a path to each file name
    cdef list fpaths = []
    for f in os.listdir(docsDir):
        if f == ".DS_Store":
            continue
        # The file names should have the following pattern
        # <sp>-pfama.mmseqs.<run-settings>.tsv
        if ("-pfama.mmseqs." in f) and f.endswith(f".pckl"):
            tmpPath = os.path.join(docsDir, f)
            if os.path.isfile(tmpPath):
                fpaths.append(tmpPath)
    # check that at least two input files were provided
    if len(fpaths) == 0:
        fnamesStr: str = '\n'.join(fpaths)
        logger.error(f"No document pckl file was found!\nPlease make the documents exraction step did not fail.\n")
        sys.exit(-5)
    # on the list with file paths
    fpaths.sort()

    # Create function to update the pickle files
    # updatedArchPcklsDir: str = os.path.join(modelsDir, "final_archs")
    # systools.makedir(updatedArchPcklsDir)

    # Assign vectors to architectures
    parallel_assign_vectors2archs(corpusPath=corpusFilePath, model=predModel, archPcklsPaths=fpaths, outDir=modelsDir, dumpArchDicts=dumpArchDicts, threads=threads)

    # stop the counter for the alignment time
    sys.stdout.write(f"\nElapsed time (Arch extraction, d2v training, and embedding) (seconds):\t{round(time.perf_counter() - start_time, 3)}\n")



cdef (unsigned long, unsigned long, unsigned long, float, float) compute_corpus_stats(str corpusPath):
    """Compute simple stats regarding the corpus file.

    Parameters:
    corpusPath (str): paths to file with space separated corpus file (no protein ids inside)

    Returns:
    tuple[int, int, float, float]: total docs, vocabulary size, words, percentage of uncovered, percentage of pfam profiles
    """

    debugStr: str = f"""compute_corpus_stats :: START
    Corpus file:\t{corpusPath}"""
    logger.debug(debugStr)

    # tmp variables
    # tmpArch: str = ""
    cdef list flds = [] # list[bytes]
    wSet: Set[str] = set()
    cdef long totWords = 0 # total number of words in corpus
    cdef long totDocuments = 0 # number of documents in the corpus
    cdef long profileCnt = 0
    cdef long archLen
    cdef size_t i
    cdef double pctProfiles
    # Set the output path for the file containing only tags
    tmpWord: str = ""

    # Define file names and file descriptor pointer in C
    cdef bytes filename_byte_string = corpusPath.encode("UTF-8")
    cdef char* corpusPath_c = filename_byte_string
    #file pointer
    cdef FILE* cfile
    # varibales for files and lines
    cdef char * line = NULL
    cdef size_t l = 0
    cdef ssize_t read
    #open the pairwise ortholog table
    cfile = fopen(corpusPath_c, "rb")
    if cfile == NULL:
        raise FileNotFoundError(2, f"No such file or directory: {corpusPath_c}")

    # The documents have the following format:
    # 9 PF04055@CL0036 3 PF16199 6
    # Where fields with profiules in the architecture
    # while numbers are uncovered regions (with their lengths encoded)
    while True:
        read = getline(&line, &l, cfile)
        if read == -1:
            break
        totDocuments = totDocuments + 1
        # split the arch string
        flds = line.rstrip(b"\n").split(b" ")
        archLen = len(flds)
        totWords = totWords + archLen
        # tmpArch = flds[1].decode()
        # Count missing interregions
        for i in range(archLen):
            tmpWord = flds[i].decode()
            wSet.add(tmpWord)
            if (tmpWord[0] == "P") or (tmpWord[0] == "C"):
                profileCnt += 1
    #close files
    fclose(cfile)

    # Compute the percentages
    pctProfiles = (profileCnt / totWords) * 100.

    # Return: total docs, vocabulary size, words, percentage of uncovered, percentage of pfam profiles
    return (totDocuments, len(wSet), totWords, 100. - pctProfiles, pctProfiles)



# @cython.profile(False)
cdef str create_corpus_file(str rawDocFilePath, str outDocFilePath, long maxRep=1, bint addTags=1, bint saveAsPickle=0):
# def create_corpus_file(rawDocFilePath: str, outDocFilePath: str, maxRep: int = 1, addTags: bool = True, saveAsPickle: bool = False) -> str:
    """Create corpus a file from a file with space-space-separated words.

    Parameters:
    rawDocFilePath (str): paths to file with space separated words
    mbsize int: Size of bins for missing interregions. Ex.: if mbsize=5 missing domains are assigned the word ceil((end-start+1)/mbsize)
    outDocFilePath (str): path to the file in which the final vocabulary will be stored
    dbDir (str): Directory which the pickles with infor about the architectures will be stored
    maxRep (unsigned int): Maximum number of times the same document can be repeated (set to 1 by default)
    Returns:
    void

    """

    debugStr: str = f"""create_corpus_file :: START
    File with all documents:\t{rawDocFilePath}
    Output file: {outDocFilePath}
    Maximum repeats:\t{maxRep:d}
    Add tags:\t{addTags}
    Save the corpus as iterator:\t{saveAsPickle}"""
    logger.debug(debugStr)

    # tmp variables
    tmpArch: str = ""
    cdef list flds = [] # list[bytes]
    archCounter: Counter = Counter()
    cdef unsigned long corpusSize = 0 # number of documents in the corpus

    # Set the output path for the file containing only tags
    outDir: str = os.path.dirname(outDocFilePath)
    bname: str = os.path.basename(outDocFilePath)
    docTagsPath:str = os.path.join(outDir, f"tags.{bname}")

    # Define file names and file descriptor pointer in C
    cdef bytes filename_byte_string = rawDocFilePath.encode("UTF-8")
    cdef char* rawDocFilePath_c = filename_byte_string
    #file pointer
    cdef FILE* cfile
    # varibales for files and lines
    cdef char * line = NULL
    cdef size_t l = 0
    cdef ssize_t read
    #open the pairwise ortholog table
    cfile = fopen(rawDocFilePath_c, "rb")
    if cfile == NULL:
        raise FileNotFoundError(2, f"No such file or directory: {rawDocFilePath_c}")

    # Open the output file
    ofd: TextIO = open(outDocFilePath, "wt")
    ofd2: TextIO = open(docTagsPath, "wt")
    # The documents have the following format:
    # @1.1002 PF04675 10 PF01068@CL0078 5 PF04679@CL0021 5
    # Where the '@' indicates the query id
    # and should be considered only if testing the model
    # using a tagged vocabulary
    while True:
        read = getline(&line, &l, cfile)
        if read == -1:
            break

        # split the arch string
        flds = line.rstrip(b"\n").split(b" ", 1)
        tmpArch = flds[1].decode()
        archCounter[tmpArch] += 1
        # The document is used only if the number of 
        # repetions is lower then the max repetitions allowed
        if archCounter[tmpArch] > maxRep:
            continue
        else:
            if addTags:
                ofd.write(line.decode())
            # Do not write the protein IDs
            else:
                ofd.write(f"{tmpArch}\n")
                ofd2.write(f"{flds[0].decode()[1:]}\n")
                # ofd.write(line.decode().split(" ", 1)[1])
            corpusSize += 1

    #close files
    fclose(cfile)
    ofd.close()
    ofd2.close()

    # Remove if Tags are in the main single text file
    if addTags:
        os.remove(docTagsPath)

    # Write some stats on the corpus
    # Extract the counts in array
    cdef cnp.ndarray[cnp.uint32_t] cntVals = np.array(list(archCounter.values()), dtype=np.uint32)
    # Return: total docs, vocabulary size, words, percentage of uncovered, percentage of pfam profiles
    cdef (unsigned long, unsigned long, unsigned long, float, float) corpusStatTuple = compute_corpus_stats(outDocFilePath)

    # Write some info on the corpus
    # Corpus size (1<=repetions_in_corpus<={maxRep}):\t{corpusSize}
    logger.debug(f"""    Processed archs:\t{cntVals.sum()}
    Uniq archs (appearing only 1 time):\t{cntVals[cntVals==1].sum()}
    Archs above max repeats ({maxRep}):\t{cntVals[cntVals>maxRep].sum()}
    Total documents:\t{corpusStatTuple[0]}
    Vocabulary size:\t{corpusStatTuple[1]}
    Total words:\t{corpusStatTuple[2]}
    % domains:\t{corpusStatTuple[3]:.2f}
    % uncovered:\t{corpusStatTuple[4]:.2f}
    """)

    if saveAsPickle:
        corpusPath: str = outDocFilePath.rstrip(".txt")
        corpusPath = f"{corpusPath}.pckl"
        # Process the corpus performing tokenization
        # store the final corpus in a pickle
        process_corpus_gensim(docFilePath=outDocFilePath, outPckl=corpusPath, addTags=addTags)

    # Return the path to the file with documents
    return outDocFilePath


# def eval_model_on_training_samples(modelPath: str, trainingDocsFilePath: str, docIdsFilePath: str) -> tuple[float, float, float, float, float, float]:
cdef (double, double, double, double, double, double) eval_model_on_training_samples(str modelPath, str trainingDocsFilePath, str docIdsFilePath):
    """
    Given a model, it will test for each training document if the predicted is the closest document.
    Note that this is not a very robust evaluation, but a simple sanity check.
    At present the deepest checked rank 100 since
    it would be too computationally expensive to obtain all the ranks for all query documents
    """

    logger.debug(f"""eval_model_on_training_samples :: START
    Model path: {modelPath}
    File with documents used in the training: {trainingDocsFilePath}
    File with query IDs: {docIdsFilePath}""")

    ln: str = ""
    cdef long idx = 0
    # associates a arch (as list of words) to an idx in the training file
    idx2words: dict[int, list[str]] = {}

    # load the model
    model: gensim.models.doc2vec.Doc2Vec = gensim.models.Doc2Vec.load(modelPath)
    # obtain document counts
    cdef unsigned long docsCnt = len(model.dv)

    # NOTE: DEBUG ONLY
    '''
    # Load the query names and associate a sequencial index
    idx2query: dict[int, str] = {}
    with open(docIdsFilePath, "rt") as ifd:
        for ln in ifd:
            idx2query[idx] = ln[:-1]
            idx += 1

    cdef int idx2querySize = len(idx2query)
    if idx2querySize != docsCnt:
        logger.error(f"The number of loaded tags ({idx2querySize}) is different from the number of documents used for training ({docsCnt}).")
        sys.exit(-5)
    '''

    # Load the documents used in the training
    idx = 0
    with open(trainingDocsFilePath, "rt") as ifd:
        for ln in ifd:
            idx2words[idx] = ln[:-1].split(" ")
            idx += 1

    cdef long idx2wordsSize = len(idx2words)
    if idx2wordsSize != docsCnt:
        logger.error(f"The number of loaded document ({idx2wordsSize}) is different from the number of documents used for training ({docsCnt}).")
        sys.exit(-5)

    # Define some temporary variables
    cdef cnp.ndarray[cnp.float32_t] inferredVector = np.zeros(model.vector_size, dtype=np.float32)
    # cdef int rank = 0
    ranks: list[int] = []
    similarDocs: list[tuple[int, float]] = []

    # Set variables for rank pcts
    # Percentage of training samples ranked as best
    cdef double rank4to10pct = 0.0
    # cdef int topnCnt = int(ceil(docsCnt/2.)) # This would compute half of the total documents
    # Compute predict only the closet 100
    cdef long topnCnt = 100
    tmpRankList: list[int] = []


    # filepath in tqdm(walkdir(inputpath), total=filecounter, unit="files"):
    # for idx in range(docsCnt):
    for idx in tqdm(range(docsCnt), total=docsCnt, unit="Architectures", ascii=True):
        inferredVector = model.infer_vector(idx2words[idx])
        # similarDocs = model.dv.most_similar([inferredVector], topn=5)
        ''' WORKING VERSION
        similarDocs = model.dv.most_similar([inferredVector], topn=docsCnt)
        rank = [docid for docid, sim in similarDocs].index(idx)
        ranks.append(rank)
        '''

        # HACK: predict only half of the ranks to speedup
        similarDocs = model.dv.most_similar([inferredVector], topn=topnCnt)
        # Note that idx could be not present
        tmpRankList = [docid for docid, sim in similarDocs]
        if idx in tmpRankList:
            # rank = tmpRankList.index(idx)
            # ranks.append(rank)
            ranks.append(tmpRankList.index(idx))
        # else:
        #     print(f"missing rank for {idx}")

        ''' DEBUG ONLY
        # print("\n")
        # print(similarDocs)
        # print(f"{idx}:\t{idx2query[idx]}\t{idx2words[idx]}")
        # print(f"rank:\t{rank}")
        # print(f"{similarDocs[wrongRank]}:\t{similarDocs[0]}")
        # print(f"{idx2query[similarDocs[wrongRank][0]]}:{idx2words[similarDocs[wrongRank][0]]}\t{idx2query[similarDocs[0][0]]}:{idx2words[similarDocs[0][0]]}")
        # '''

    # Compute ranks
    counter = Counter(ranks)
    # Define more counters
    cdef long rank100RightCnt = counter[0] + counter[1] + counter[2]
    cdef long acc = 0
    # Compute pct rank 4 to 10
    for idx in range(3, 10):
        acc += counter[idx]
    rank100RightCnt += acc
    rank4to10pct = (acc/docsCnt) * 100.

    # Count of prediction with ranks between 11 and 100
    acc = 0
    for idx in range(10, topnCnt):
        acc += counter[idx]
    rank100RightCnt += acc
    # rank10toHalfBestPct = (acc/docsCnt) * 100.
    # rankHalf2WorstPct = ((docsCnt - rank100RightCnt)/docsCnt) * 100.
    '''
    # Compute PCT of very wrong predictions
    acc = 0
    # NOTE: old way to do it
    # much slower but we can see the rank
    for idx in range(topnCnt, docsCnt):
        acc += counter[idx]
    rankHalf2WorstPct = (acc/docsCnt) * 100.
    '''

    # Return variables for rank pcts
    # Percentage of training samples ranked as best
    # rank1pct = (counter[0]/docsCnt) * 100. -> % of predicted as closest (correct prediction)
    # rank2pct = (counter[1]/docsCnt) * 100. -> % of predicted as 2nd best
    # rank3pct = (counter[2]/docsCnt) * 100. -> % of predicted as 3rd best

    # example: given 10000 documents
    # rank10toHalfBestPct contains the pct of predictions
    # ranked between 10 and 5000 best
    # cdef double rank10toHalfBestPct = 0.0
    # rankHalf2WorstPct contains the pct of predictions
    # ranked between 5001 and 10000 best
    # cdef double rankHalf2WorstPct = 0.0

    # return (rank1pct, rank2pct, rank3pct, rank4to10pct, rank10toHalfBestPct, rankHalf2WorstPct)
    # return ((counter[0]/docsCnt) * 100., (counter[1]/docsCnt) * 100., (counter[2]/docsCnt) * 100., rank4to10pct, rank10toHalfBestPct, rankHalf2WorstPct)
    return ((counter[0]/docsCnt) * 100., (counter[1]/docsCnt) * 100., (counter[2]/docsCnt) * 100., rank4to10pct, (acc/docsCnt) * 100., ((docsCnt - rank100RightCnt)/docsCnt) * 100.)


''' GRID SEARCH FOR THE MODEL
def grid_search_d2v_gensim(corpusPath: str, outDir: str, modelPrefix: str = "d2v_model", algorithm: int = 0, dbowWords: int = 1, evaluateModels: bool = True, threads: int = 4):
    """
    Train multiple models using different parameter settings.

    corpusPath (str): must be a file with documents separated by a single space (not a iterable)
    algorithm (int): Defines the training algorithm. If dm=1, ‘distributed memory’ (PV-DM) is used. Otherwise, PV-DBOW (using skip-gram) is employed.
    dbowWords (int): train also the word-verctors (only supported by PV-DBOW [algorithm=0])
    """

    logger.debug(f"""grid_search_d2v_gensim :: START
    Path to the corpus: {corpusPath}
    Output directory: {outDir}
    Model name prefix: {modelPrefix}
    Algorithm:\t{algorithm}
    dbow_words:\t{dbowWords}
    Evaluate models:\t{evaluateModels}
    Threads:\t{threads}""")

    # Fix the dbowWords values if discordant with
    # the selected model type
    # Algorithm set to 1 (PV-DM)
    # But also dbow_words set to 1
    if ((dbowWords + algorithm) == 2):
        logger.warning("dbowWords can only be set to 1 when algorithm is set to 0 (PV-DBOW).\nSetting dbowWords to 0")
        dbowWords = 0

    # Following are the main parameters used in the training:
    # dimensionality of feature vectors
    # higher is usually better but affects the model size and training time
    vectorSizes: list[int] = [100]
    # vectorSizes: list[int] = [50, 75, 100, 125, 150, 175, 200, 225, 250]
    # vectorSizes: list[int] = [50, 75, 100, 125, 150, 175]
    # vectorSizes: list[int] = [50, 75, 100]
    # vectorSizes: list[int] = [75, 100, 125]

    # The maximum distance between the current and predicted word within a sentence.
    # also this can have big impact on training and accuracy
    # NOTE: higher values did not imporve for DBOW_SG
    windowSizes: list[int] = [2]
    # windowSizes: list[int] = [2, 3, 5]
    # windowSizes: list[int] = [2, 5, 10]
    # windowSizes: list[int] = [2, 5, 8]

    # Ignores all words with total frequency lower than this
    # this affect the vocabulary size, hence model size and training time
    # When set to 1 all words are used regardless of their frequencies
    minWordCnts: list[int] = [1]
    # minWordCnts: list[int] = [1, 2, 3]
    # minWordCnts: list[int] = [1, 2]

    # Number of iterations (epochs) over the corpus. Defaults to 10 for Doc2Vec
    # epochs: list[int] = [20, 40]
    # epochs: list[int] = [100]
    # epochs: list[int] = [20, 40]
    # epochs: list[int] = [50, 60, 80, 90, 100]
    # epochs: list[int] = [50, 75, 100, 125]
    epochs: list[int] = [75, 100, 125]
    # epochs: list[int] = [50, 75, 100, 125, 150, 175, 200, 225, 250]

    # Compute the number of models that will be trained
    cdef long totModels = len(vectorSizes) * len(windowSizes) * len(minWordCnts) * len(epochs)
    cdef long vsize, wsize, mwcnt, epo

    # Set model type and model prefix
    # set some variables
    outTbl: str = "pv-dm_cbow"
    if algorithm == 0:
        # distributed bag of words (PV-DBOW) is employed
        outTbl = "pv-dbow_sg"
    if (algorithm == 0) and (dbowWords == 1):
        outTbl = f"{outTbl}.dboww1"
    # Add other information to output table name
    outTbl = f"gsearch.{modelPrefix}.{outTbl}.{totModels}models.{len(vectorSizes)}vecX{len(windowSizes)}winX{len(minWordCnts)}minwX{len(epochs)}epoch.{threads}cpus.tsv"
    outTbl = os.path.join(outDir, outTbl)
    ofd: TextIO = open(outTbl, "wt", buffering=1)
    # write the HDR
    ofd.write("model_type\tvector_size\twindow_size\tmin_word_count\tdbow_words\tepochs\tcpus\ttraining_docs_cnt\tvocab_size\ttraining_words_cnt\ttraining_time\tvocam_mem\tvectors_mem\ttot_mem\tfile_size\trank1_pct\trank2_pct\trank3_pct\trank4_10_pct\trank11_100_pct\trank_101_to_last_pct\n")

    # Set gensim logger to WARNING
    cdef long logPrevLevel = gensim.logger.getEffectiveLevel()
    set_gensim_logging_level(30)

    # Train the models
    modelPath: str = ""
    corpusTagsPath: str = ""
    cdef (double, double, double, double, double, double) modelTrainingRankings
    for vsize in vectorSizes:
        for wsize in windowSizes:
            for mwcnt in minWordCnts:
                for epo in epochs:
                    # print(vsize, wsize, mwcnt, epo)
                    modelPath = train_d2v_gensim(corpusPath=corpusPath, outDir=outDir, modelPrefix=modelPrefix, algorithm=algorithm, vectorSize=vsize, window=wsize, minCnt=mwcnt, useAllWords=True, threads=threads, epochs=epo , dbowWords=dbowWords)
                    modelInfoTpl = inspect_model_gensim(modelPath)
                    # print(f"\nTrained model:\t{os.path.basename(modelPath)}")

                    if evaluateModels:
                        corpusTagsPath = os.path.join(os.path.dirname(corpusPath), os.path.basename(corpusPath))
                        modelTrainingRankings = eval_model_on_training_samples(modelPath=modelPath, trainingDocsFilePath=corpusPath, docIdsFilePath=corpusTagsPath)
                        ofd.write(f"{modelInfoTpl[0]}\t{modelInfoTpl[1]:d}\t{modelInfoTpl[2]:d}\t{modelInfoTpl[3]:d}\t{modelInfoTpl[4]:d}\t{modelInfoTpl[5]:d}\t{modelInfoTpl[6]:d}\t{modelInfoTpl[7]:d}\t{modelInfoTpl[8]:d}\t{modelInfoTpl[9]:d}\t{modelInfoTpl[10]:.3f}\t{modelInfoTpl[11]:.3f}\t{modelInfoTpl[12]:.3f}\t{modelInfoTpl[13]:.3f}\t{modelInfoTpl[14]:.3f}\t{modelTrainingRankings[0]:.3f}\t{modelTrainingRankings[1]:.3f}\t{modelTrainingRankings[2]:.3f}\t{modelTrainingRankings[3]:.3f}\t{modelTrainingRankings[4]:.3f}\t{modelTrainingRankings[5]:.3f}\n")
                        continue

                    #  training_time vocam_mem vectors_mem tot_mem file_size
                    ofd.write(f"{modelInfoTpl[0]}\t{modelInfoTpl[1]:d}\t{modelInfoTpl[2]:d}\t{modelInfoTpl[3]:d}\t{modelInfoTpl[4]:d}\t{modelInfoTpl[5]:d}\t{modelInfoTpl[6]:d}\t{modelInfoTpl[7]:d}\t{modelInfoTpl[8]:d}\t{modelInfoTpl[9]:d}\t{modelInfoTpl[10]:.3f}\t{modelInfoTpl[11]:.3f}\t{modelInfoTpl[12]:.3f}\t{modelInfoTpl[13]:.3f}\t{modelInfoTpl[14]:.3f}\n")
    ofd.close()

    # Restore gensim logger level
    set_gensim_logging_level(logPrevLevel)
'''


''' USED IN GRID SEARCH
def inspect_model_gensim(modelPath: str) -> tuple[str, int, int, int, int, int, int, int, int, int, int, float, float, float, float]:
    """
    Extract multiple information from a doc2vec model trained using Gensim.
    """
    logger.debug(f"""inspect_model_gensim :: START
    Model path: {modelPath}""")

    # load the model
    model: gensim.models.doc2vec.Doc2Vec = gensim.models.Doc2Vec.load(modelPath)
    # set some variables
    dmStr: str = "pv-dm_cbow"
    # Skip-gram was used (dm=0)
    if not(model.dm):
        # distributed bag of words (PV-DBOW) is employed
        dmStr = "pv-dbow_sg"
        # check if dbow_words was used
        if model.dbow_words == 1:
            dmStr = "pv-dbow_sg.dboww1"

    # extract memory relate info
    memInfo: dict[str, int] = model.estimate_memory()
    cdef float vocabMem = memInfo["vocab"]/1000000
    cdef float vecMem = memInfo["vectors"]/1000000
    cdef float totMem = memInfo["total"]/1000000
    cdef float fileSize = os.stat(modelPath).st_size/1000000

    # return a tuple with different information on the trained model
    # content of the tuple is: tuple[str, int, int, int, int, int, int, int, int, int, int, float, float, float, float]
    # model.corpus_total_words -> total number of profiles (including uncovered used for training)
    # model.corpus_count -> number of documents (architectures used for training)
    # len(model.wv) -> vovabulary size
    return (dmStr, model.vector_size, model.window, model.min_count, model.dbow_words, model.epochs, model.workers, model.corpus_count, len(model.wv), model.corpus_total_words, model.total_train_time, vocabMem, vecMem, totMem, fileSize)
'''


# @cython.profile(False)
# def extract_documents(rawArchFile:str, mbsize:int, outDir: str, skipUnknown:bool=False) -> list[str]:
cdef inline list extract_documents(str rawArchFile, float minqcov, int mbsize, str outDir, bint skipUnknown=0):
    """
        Parses a string with a domain architecture and writes a space-separated line with simple words.
        The format can be used for training with different GenSim models (e.g., word2vec).
    """

    # Example of line with raw arch information
    # query qlen totqcov uniq_doms tot_doms missing_doms repeated_doms max_repeated_doms arch_size arch arch_types
    # 74.10 564 0.812 1 1 2 0 0 3 m:1-29,PF00343@CL0113:30-487,m:488-564 1
    # 74.100 399 0.910 3 3 1 0 1 4 PF00009@CL0023:10-206,m:207-229,PF03144@CL0575:230-299,PF03143:303-398 222

    '''
    # cdef bint debug = 1

    debugStr: str = f"""extract_documents :: START
    rawArchFile:\t{rawArchFile}
    Unknown bin size:\t{mbsize:d}
    Output directory: {outDir}
    Skip unknown interregions:\t{skipUnknown}"""
    logger.debug(debugStr)
    '''

    # Tmp vars
    cdef long rdCnt = 0
    cdef float tmpCov = 0.0
    # This will contain the length of uncovered regions encoded using mbsize
    # Ex.: if mbsize=5 missing domains are assigned the word ceil((end-start+1)/mbsize) ", default=5)
    # cdef double uncoveredEncoded
    # cdef int tmpLen = 0
    cdef long tmpDomsCnt = 0
    cdef long tmpArchSize = 0
    cdef long qstart = 0
    cdef long qend = 0
    cdef long idx = 0
    # Query ID represented using an integer
    cdef long queryInt
    cdef long interrigionType
    cdef cnp.ndarray[cnp.uint8_t] tmpRegState
    cdef cnp.ndarray[cnp.uint32_t] tmpRegLengths
    # Contains the index to the vocabulary
    # for a given domain
    cdef cnp.ndarray[cnp.uint32_t] emptyDomWvIdx = np.zeros(0, dtype=np.uint32)
    cdef cnp.ndarray[cnp.float32_t] emptyEmbedding = np.zeros(0, dtype=np.float32)
    flds: list[str] = []
    query: str = ""
    tmpDoc: str
    tmpDocWords: list[str] = []
    tmpW: str
    domDeque: deque[str] = deque()
    # Will contain the generated documents
    documents: list[str] = []
    # Will contain the Arch objects to be stored in the pckl
    # archDict: dict[str, Arch] = {}
    archDict: dict[int, Arch] = {}

    # define file names and file descriptor pointer in C
    cdef bytes filename_byte_string = rawArchFile.encode("UTF-8")
    cdef char* rawArchFile_c = filename_byte_string
    #file pointer
    cdef FILE* cfile
    # varibales for files and lines
    cdef char * line = NULL
    cdef size_t l = 0
    cdef ssize_t read

    #open the pairwise ortholog table
    cfile = fopen(rawArchFile_c, "rb")
    if cfile == NULL:
        raise FileNotFoundError(2, f"No such file or directory: {rawArchFile_c}")

    while True:
        read = getline(&line, &l, cfile)
        if read == -1:
            break

        # Skip the first line, which should be the header
        if rdCnt == 0:
            rdCnt += 1
            continue

        rdCnt += 1
        # split the arch string
        flds = line.rstrip(b"\n").split(b"\t", 10)
        tmpCov = atof(flds[2])
        # Skip the arch if the query coverage is below the threshold
        if tmpCov < minqcov:
            # print(f"{tmpCov}\t{minqcov}")
            continue
        query = flds[0].decode()
        queryInt = atol(flds[0].split(b".", 1)[1])
        tmpDomsCnt = atol(flds[4])
        tmpArchSize = atol(flds[8])
        # Set the arrays with the covered interregion positions
        # and the one with the interregion lengths
        tmpRegState = np.zeros(tmpArchSize, dtype=np.uint8)
        tmpRegLengths = np.zeros(tmpArchSize, dtype=np.uint32)
        domDeque.clear()
        domDeque = deque(maxlen=tmpArchSize)
        # Extract info from the architecture
        for regIdx, reg in enumerate(flds[9].decode().split(",", tmpArchSize - 1)):
            # print("\n", regIdx, reg)
            # uncovered domain
            if reg[0] == "m":
                # print("\nUncovered region")
                qstart, qend = [int(x) for x in reg[2:].split("-", 1)]
                # print(qstart, qend, qend - qstart)
                # store the length in the array
                tmpRegLengths[regIdx] = (qend - qstart) + 1
            else:
                # print(f"\nProfile: {reg}")
                tmpRegState[regIdx] = 1
                # extract start and end positions
                tmpRegion, tmpBoundaries = reg.rsplit(":", 1)
                qstart, qend = [int(x) for x in tmpBoundaries.split("-", 1)]
                tmpRegLengths[regIdx] = (qend - qstart) + 1
                # add the domain to the deque
                domDeque.append(tmpRegion)

        # Create the Arch object and add it a the output dictionary
        # NOTE: this could be a separate function if it grows too big
        # Use the information from :
        # name='48.893'
        # regState=array([1, 0, 1, 0, 1, 0], dtype=uint8)
        # regLengths=array([174, 50, 199, 24, 105, 34], dtype=uint16)
        # domains=array(['PF04675', 'PF01068@CL0078', 'PF04679@CL0021'], dtype='<U14')
        # Such information should give the following arch document
        # @48.893 PF04675 10 PF01068@CL0078 5 PF04679@CL0021 7

        tmpDoc = f"@{query}"
        tmpDocWords.clear()
        for idx in range(tmpArchSize):
            interrigionType = tmpRegState[idx]
            # If it is a domain
            if interrigionType == 1:
                tmpW = domDeque.popleft()
            else: # Then it is un uncovered interregion
                tmpW = f"{ceil(tmpRegLengths[idx]/mbsize):.0f}"
            tmpDoc = f"{tmpDoc} {tmpW}"
            tmpDocWords.append(tmpW)
        documents.append(f"{tmpDoc}\n")
        archDict[queryInt] = Arch(atoi(flds[1]), tmpCov, tmpArchSize, tmpDomsCnt, emptyDomWvIdx, tmpRegState, tmpRegLengths, np.array(tmpDocWords, dtype=np.str_), emptyEmbedding, atol(flds[10]))
        # print(archDict[queryInt])
        # break

    #close input file
    fclose(cfile)

    # Dump the dictionary into a pckl file
    pcklPath: str = os.path.basename(rawArchFile).replace(".tsv", "")
    # Append extra info to the pickle file name
    pcklPath = f"{pcklPath}.mbsize{mbsize}.pckl"

    if len(outDir) > 0:
        makedir(outDir)
        pcklPath = os.path.join(outDir, pcklPath)
    else:
        pcklPath = os.path.join(os.path.dirname(rawArchFile), pcklPath)
    # dump the dictionary
    with open(pcklPath, "wb") as ofd:
        dump(archDict, ofd, protocol=4)

    return documents



# NOTE: use only for debugging purposes
'''
# @cython.profile(False)
# def map_docs2protein_ids(spArchList: list[dict[Arch]], outVecDir: str, outSuffix: str) -> None:
cdef void map_docs2protein_ids(list spArchList, str outVecDir, str outSuffix):
    """
    Process dictionaries with Arch objects and generate:
    - doc -> protein id dictionary
    - sp2archDict -> to each proteome associate a dict with protein_id -> Arch object mapping

    Parameters:
    spArchList: list[str]: paths to pickles with Arch objects for a single proteome
    outVecDir (str): path to the directory in which the generate vectors will be stored
    outSuffix (str): suffix for output pickle file name

    Returns:
    void
    """

    # Output dictionaries
    doc2protId: dict[str, list[str]] = {}
    repeatedDoc2protId: dict[str, list[str]] = {}
    cdef unsigned short pcklCnt = len(spArchList)
    cdef unsigned int uniqDocs, nonUniqDocs
    cdef unsigned int totDocs = 0

    # Indexes to be used in for loops
    cdef int i, j
    cdef str tmpPath
    cdef str tmpDoc
    cdef int tmpDocCnt
    cdef unsigned short spId = 0
    # This protein ID must be the complete one
    # Which is a string which includes the species id (e.g., 3.478; where 3 is the proteome ID)
    cdef str tmpProtId
    tmpArch: Arch
    cdef list flds
    cdef list tmpList

    debugStr: str = f"""map_docs2protein_ids :: START
    Species to process:\t{pcklCnt:d}
    Output directory: {outVecDir}
    Output pfile suffix: {outSuffix}"""
    logger.debug(debugStr)

    cdef dict tmpPickle # dict[int, Arch]

    for i in range(pcklCnt):
        tmpPath = spArchList.pop()
        flds = tmpPath.rsplit("/", 1)
        spId = int(flds[1].split("-", 1)[0])
        # Load the pickle
        tmpPickle = load(open(tmpPath, "rb"))
        tmpDocCnt = len(tmpPickle)
        totDocs += tmpDocCnt
        for j, tmpArch in tmpPickle.items():
            # Extract the ID
            tmpDoc = " ".join(getattr(tmpArch, "phrase"))
            tmpProtId = f"{spId}.{j}"
            # Add the Document and associated ID
            # to the mapping dictionary
            if tmpDoc in doc2protId:
                doc2protId[tmpDoc].append(tmpProtId)
            else:
                doc2protId[tmpDoc] = [tmpProtId]

    tmpList = list(doc2protId.keys())
    tmpDocCnt = len(tmpList)
    # Separate repeated from uniq archs
    # for tmpDoc in tmpList:
    for i in range(tmpDocCnt):
        tmpDoc = tmpList.pop()
        flds = doc2protId[tmpDoc]
        if len(flds) > 1: # repeated doc
            del doc2protId[tmpDoc]
            repeatedDoc2protId[tmpDoc] = flds
    # Set the counters and write debug info
    uniqDocs = len(doc2protId)
    nonUniqDocs = len(repeatedDoc2protId)

    # Store pickle with uniq documents
    if len(outSuffix) > 0:
        tmpPath = os.path.join(outVecDir, f"doc2protein_id.uniq.{outSuffix}.pckl")
    else:
        tmpPath = os.path.join(outVecDir, f"doc2protein_id.uniq.{pcklCnt}.pckl")
    # dump the dictionary
    with open(tmpPath, "wb") as ofd:
        dump(doc2protId, ofd, protocol=4)

    # Store pickle with repeated documents
    if len(outSuffix) > 0:
        tmpPath = os.path.join(outVecDir, f"doc2protein_id.repeated.{outSuffix}.pckl")
    else:
        tmpPath = os.path.join(outVecDir, f"doc2protein_id.repeated.{pcklCnt}.pckl")
    # dump the dictionary
    with open(tmpPath, "wb") as ofd:
        dump(repeatedDoc2protId, ofd, protocol=4)

    # NOTE: the keys of repeatedDoc2protId and doc2protId
    # must be the same as the documents in the final training corpus
    debugStr: str = f"""Document mapping summary :: SUMMARY:
    Proteomes involved:\t{pcklCnt:d}
    Total documents:\t{totDocs:d}
    Uniq:\t{uniqDocs}
    Repeated:\t{nonUniqDocs}
    Corpus size (not repeated docs):\t{(nonUniqDocs + uniqDocs):d}"""
    logger.info(debugStr)
'''


# def process_corpus_gensim(docFilePath: str, outPckl: str, addTags: bool = True) -> None:
cdef void process_corpus_gensim(str docFilePath, str outPckl, bint addTags = 1):
    """
    Processes the input documents into tokens tokens, and stores them in a pickle.
    Returns a list with the tokens.
    """

    logger.info(f"""process_corpus_gensim :: START
    Documents: {docFilePath}
    Path to pickle file with corpus: {outPckl}
    Add tags to documents:\t{addTags}""")

    # process the corpus and store it to a pickle
    cdef list corpusTokens = list(tokenize_documents_gensim(docFilePath, addTags=addTags))
    # save the training corpus to a pickle file
    gensim.utils.pickle(corpusTokens, outPckl, protocol=4)


# def train_d2v_gensim(corpusPath: str, outDir: str = "", modelPrefix: str = "d2v_model", algorithm:int=1, vectorSize:int=100, window:int=5, minCnt:int=2, useAllWords:bool=False, threads:int=4, epochs:int=50 , dbowWords:int=0) -> str:
cdef str train_d2v_gensim(str corpusPath, str outDir, str modelPrefix = "d2v_model", unsigned int algorithm = 1, unsigned int vectorSize = 100, unsigned int window = 5, unsigned int minCnt = 2, bint useAllWords = 0, unsigned int threads = 4, unsigned int epochs = 50 , unsigned int dbowWords = 0):
    """
    Given a pckl file with Tagged documents, generate vocubulary, train doc2vec model, and save the model to disk.
    """

    # set some variables
    dmStr: str = "pv-dm_cbow"
    if algorithm == 0:
        # distributed bag of words (PV-DBOW) is employed
        dmStr = "pv-dbow_sg"

    logger.debug(f"""train_d2v_gensim :: START
    Corpus: {corpusPath}
    Output directory: {outDir}
    Model name prefix:\t{modelPrefix}
    Algorithm:\t{dmStr}
    Vector size:\t{vectorSize:d}
    Window size:\t{window}
    Min word count:\t{minCnt}
    Use all words:\t{useAllWords}
    Threads:\t{threads}
    Epochs:\t{epochs}
    DBow-words:\t{dbowWords}""")

    # For more details on gensim doc2vec implementation, visit:
    # https://radimrehurek.com/gensim/auto_examples/tutorials/run_doc2vec_lee.html
    # https://radimrehurek.com/gensim/apiref.html#api-reference

    # Parameters for the model
    # class gensim.models.doc2vec.Doc2Vec(documents=None, corpus_file=None, vector_size=100, dm_mean=None, dm=1, dbow_words=0, dm_concat=0, dm_tag_count=1, dv=None, dv_mapfile=None, comment=None, trim_rule=None, callbacks=(), window=5, epochs=10, **kwargs)

    # Relevant parameters for training
    # documents (iterable of list of TaggedDocument, optional) – Input corpus, can be simply a list of elements, but for larger corpora,consider an iterable that streams the documents directly from disk/network
    # corpus_file: train directly from file on disk (much faster in parallel)
    # dm ({1,0}, optional) – Defines the training algorithm. If dm=1, ‘distributed memory’ (PV-DM) is used. Otherwise, distributed bag of words (PV-DBOW) is employed.
    # vector_size (int, optional) – Dimensionality of the feature vectors.
    # window (int, optional) – The maximum distance between the current and predicted word within a sentence.
    # min_count (int, optional) – Ignores all words with total frequency lower than this.
    # workers (int, optional) – Use these many worker threads to train the model (=faster training with multicore machines).
    # epochs (int, optional) – Number of iterations (epochs) over the corpus. Defaults to 10 for Doc2Vec.
    # dbow_words ({1,0}, optional) – If set to 1 trains word-vectors (in skip-gram fashion) simultaneous with DBOW doc-vector training; If 0, only trains doc-vectors (faster).


    ''' NOTE: training should be done using a formatted text file, which is faster than using iterators
    # Load the tagged documents in corpus
    train_corpus = gensim.utils.unpickle(corpusPath)
    '''

    # NOTE: change the below value to control the logging
    # output from gensim
    # Set gensim logger to WARNING
    cdef long logPrevLevel = gensim.logger.getEffectiveLevel()
    set_gensim_logging_level(30)

    # NOTE: hs = 0, and negative=5 should more scalable
    # model = gensim.models.doc2vec.Doc2Vec(dm=algorithm, vector_size=vectorSize, window=window, min_count=minCnt, workers=threads, epochs=epochs, dbow_words=dbowWords, hs=1, negative=0, seed=1, max_vocab_size=None)
    model = gensim.models.doc2vec.Doc2Vec(dm=algorithm, vector_size=vectorSize, window=window, min_count=minCnt, workers=threads, epochs=epochs, dbow_words=dbowWords, hs=0, negative=5, seed=1, max_vocab_size=None)
    # build vocabulary from a text file containing the corpus
    model.build_vocab(corpus_file=corpusPath)

    # train the model
    modelName: str = f"{modelPrefix}.{dmStr}.vecsize{model.vector_size}.win{model.window}.mincnt{model.min_count}.ep{model.epochs}.thr{model.workers}"

    logger.info(f"""Training artificial neural network (ANN):
    Architectures:\t{model.corpus_count}
    Vocabulary size:\t{len(model.wv)}
    Total domains for training (including uncovered):\t{model.corpus_total_words}""")

    # dbow_words has effect only when pv-dbow_sg is used
    # hence when dm is set to 0
    if (algorithm == 0) and (dbowWords == 1):
        modelName = f"{modelName}.dboww{model.dbow_words}"

    if useAllWords:
        modelName = f"{modelName}.allw"
        # NOTE: compute_loss is not implemented in Gensim doc2vec
        model.train(corpus_file=corpusPath, total_examples=model.corpus_count, total_words=model.corpus_total_words, epochs=model.epochs, word_count=0, compute_loss=False)
    else:
        # NOTE: compute_loss is not implemented in Gensim doc2vec
        model.train(corpus_file=corpusPath, total_examples=model.corpus_count, total_words=model.corpus_total_words, epochs=model.epochs, compute_loss=False)

    # Restore gensim logging level
    set_gensim_logging_level(logPrevLevel)

    modelPath: str = os.path.join(outDir, modelName)
    # NOTE: there is a way to save the model to save some memory
    model.save(modelPath)

    # write some stats regarding the model to file
    cdef str modelStatsPath = os.path.join(outDir, f"stats.{modelPrefix}.tsv")
    ofd: TextIO = open(modelStatsPath, "wt")
    ofd.write(f"Architectures:\t{model.corpus_count}\n")
    ofd.write(f"Vocabulary size:\t{len(model.wv)}\n")
    ofd.write(f"Total words:\t{model.corpus_total_words}\n")
    ofd.write(f"Training time (seconds):\t{model.total_train_time:.2f}\n")
    ofd.close()

    # Write some info
    sys.stdout.write(f"\nElapsed time for training d2v (seconds):\t{model.total_train_time:.2f}\n")

    return modelPath



''' NOTE: this uses an Iterator for training, which is slower than plain text
# def train_d2v_gensim(corpusPath: str, outDir: str = "", modelPrefix: str = "d2v_model", algorithm:int=1, vectorSize:int=100, window:int=5, minCnt:int=2, useAllWords:bool=False, threads:int=4, epochs:int=50 , dbowWords:int=0) -> str:
cdef str train_d2v_tokenized(str corpusPath, str outDir, str modelPrefix = "d2v_model", unsigned short algorithm = 1, unsigned short vectorSize = 100, unsigned short window = 5, unsigned short minCnt = 2, bint useAllWords = 0, unsigned short threads = 4, unsigned short epochs = 50 , unsigned short dbowWords = 0):
    """
    Given a pckl file with Tagged documents, generate vocubulary, train doc2vec model, and save the model to disk.

    This version of the function performs the training using an iterator and not a text file
    """

    # set some variables
    dmStr: str = "pv-dm_cbow"
    if algorithm == 0:
        # distributed bag of words (PV-DBOW) is employed
        dmStr = "pv-dbow_sg"

    logger.info(f"""train_d2v_tokenized :: START
    Corpus: {corpusPath}
    Output directory: {outDir}
    Model name prefix:\t{modelPrefix}
    Algorithm:\t{dmStr}
    Vector size:\t{vectorSize:d}
    Window size:\t{window}
    Min word count:\t{minCnt}
    Use all words:\t{useAllWords}
    Threads:\t{threads}
    Epochs:\t{epochs}
    DBow-words:\t{dbowWords}""")

    # For more details on gensim doc2vec implementation, visit:
    # https://radimrehurek.com/gensim/auto_examples/tutorials/run_doc2vec_lee.html
    # https://radimrehurek.com/gensim/apiref.html#api-reference

    # Parameters for the model
    # class gensim.models.doc2vec.Doc2Vec(documents=None, corpus_file=None, vector_size=100, dm_mean=None, dm=1, dbow_words=0, dm_concat=0, dm_tag_count=1, dv=None, dv_mapfile=None, comment=None, trim_rule=None, callbacks=(), window=5, epochs=10, **kwargs)

    # Relevant parameters for training
    # documents (iterable of list of TaggedDocument, optional) – Input corpus, can be simply a list of elements, but for larger corpora,consider an iterable that streams the documents directly from disk/network
    # corpus_file: train directly from file on disk (much faster in parallel)
    # dm ({1,0}, optional) – Defines the training algorithm. If dm=1, ‘distributed memory’ (PV-DM) is used. Otherwise, distributed bag of words (PV-DBOW) is employed.
    # vector_size (int, optional) – Dimensionality of the feature vectors.
    # window (int, optional) – The maximum distance between the current and predicted word within a sentence.
    # min_count (int, optional) – Ignores all words with total frequency lower than this.
    # workers (int, optional) – Use these many worker threads to train the model (=faster training with multicore machines).
    # epochs (int, optional) – Number of iterations (epochs) over the corpus. Defaults to 10 for Doc2Vec.
    # dbow_words ({1,0}, optional) – If set to 1 trains word-vectors (in skip-gram fashion) simultaneous with DBOW doc-vector training; If 0, only trains doc-vectors (faster).

    # output from gensim
    # Set gensim logger to WARNING
    cdef int logPrevLevel = gensim.logger.getEffectiveLevel()
    set_gensim_logging_level(30)

    # Load the tagged documents in corpus
    # train_corpus = gensim.utils.unpickle(corpusPath)
    train_corpus = list(tokenize_documents_gensim(docFilePath=corpusPath, addTags=True))

    model = gensim.models.doc2vec.Doc2Vec(dm=algorithm, vector_size=vectorSize, window=window, min_count=minCnt, workers=threads, epochs=epochs, dbow_words=dbowWords, hs=1, negative=0, max_vocab_size=None)
    # build vocabulary
    # FIXME: use a file on disk instead (tags will be sequencial)
    model.build_vocab(corpus_iterable=train_corpus)

    # train the model
    modelName: str = f"{modelPrefix}.{dmStr}.vecsize{model.vector_size}.win{model.window}.mincnt{model.min_count}.ep{model.epochs}.thr{model.workers}"

    logger.info(f"""\nTraining artificial neural network (ANN):
    Architectures:\t{model.corpus_count}
    Vocabulary size:\t{len(model.wv)}
    Total domains for training (including uncovered):\t{model.corpus_total_words}""")

    # dbow_words has effect only when pv-dbow_sg is used
    # hence when dm is set to 0
    if (algorithm == 0) and (dbowWords == 1):
        modelName = f"{modelName}.dboww{model.dbow_words}"

    if useAllWords:
        modelName = f"{modelName}.allw"
        # NOTE: compute_loss is not implemented in Gensim doc2vec
        model.train(corpus_iterable=train_corpus, total_examples=model.corpus_count, total_words=model.corpus_total_words, epochs=model.epochs, word_count=0, compute_loss=False)
    else:
        # NOTE: compute_loss is not implemented in Gensim doc2vec
        model.train(corpus_iterable=train_corpus, total_examples=model.corpus_count, total_words=model.corpus_total_words, epochs=model.epochs, compute_loss=False)

    # sys.exit("DEBUG :: train_d2v_tokenized")

    # Restore gensim logging level
    set_gensim_logging_level(logPrevLevel)

    modelPath: str = os.path.join(outDir, modelName)
    # NOTE: there is a way to save the model to save some memory
    model.save(modelPath)

    # Write some info
    sys.stdout.write(f"\nElapsed time for training d2v using iterables (seconds):\t{model.total_train_time:.2f}\n")

    return modelPath
'''


cdef inline void set_gensim_logging_level(int level):
    """Set logging level for gensim logger."""
    # Information about logging and levels can be found at
    # https://docs.python.org/3/howto/logging.html
    # CRITICAL 50
    # ERROR 40
    # WARNING 30
    # INFO 20
    # DEBUG 10
    # NOTSET 0
    # By default Gensim logger is set to INFO which make it kind of verbose
    # Verbose would probably be the most appropriate
    gensim.logger.setLevel(level)



# NOTE: cdef does not support 'yeld' hence this function must be of 'def' type
def tokenize_documents_gensim(docFilePath: str, addTags: bool = True):
    """
    Reads a file with space-separated domains, and returns a corpus.
    """
    logger.info(f"""    Documents: {docFilePath}
    Add tags to documents:\t{addTags}""")

    import smart_open

    # Set temp variables
    tmpProtId: str = ""
    tmpArch: str = ""
    ln: str = ""
    cdef list flds # list[str]
    cdef list tokens # list[str]
    # Says if the document contains profile names or not
    cdef bint istagged = 0
    cdef long i = 0
    tokens: list[str] = []
    # Search for the protein ID in the first 2 lines
    with open (docFilePath, "rt") as ifd:
        while i < 2:
            if ifd.readline()[0] == "@":
                istagged = 1
                break
            i += 1
        i = 0

    # Reset the counter
    i = 0

    # We expect lines in the corpus to contain a protein ID
    # lines in the corpus should look as follows:
    # example: @P00163 4 PF00033@CL0328 12 PF00032 5
    # The string prefixed with '@' represents the protein id

    # Say if the vocabulary will be tagged or not
    if addTags:
        if istagged:
            logger.info("The corpus will include the protein IDs.")
        else:
            # print(f"ERROR: the file\n{docFilePath}\ndoes not contain protein IDs.")
            # print("Please generate regenerate the file with documents.")
            print(f"WARNING: the file\n{docFilePath}\ndoes not contain protein IDs.")
            print("Training documents will tagged with sequencial 0-indexed numeric IDs.")
            # sys.exit(-7)
    else:
        if istagged:
            # Skip the protein id
            logger.info("We are skipping the protein IDs in the corpus creation.")

    # add an id to the document if present
    with smart_open.open(docFilePath, encoding="iso-8859-1") as ifd:
        for i, ln in enumerate(ifd):
            if addTags == True:
                # The file has protein IDs
                if istagged:
                    flds = ln[:-1].split(" ", 1)
                    tmpProtId = flds[0]
                    tmpArch = flds[1]
                    # tmpProtId, tmpArch = ln[:-1].split(" ", 1)
                    # Tokens are simply a list of words extracted from the documents
                    # tokens = [w.strip(" ") for w in ln.rstrip("\n").split(" ")]
                    tokens = [w.strip(" ") for w in tmpArch.split(" ")]
                    yield gensim.models.doc2vec.TaggedDocument(tokens, [tmpProtId[1:]])
                else: # Simply use a sequencial ID as tag
                    # The documents has not protein IDs
                    tokens = [w.strip(" ") for w in ln.rstrip("\n").split(" ")]
                    yield gensim.models.doc2vec.TaggedDocument(tokens, [i])
            else:
                if istagged:
                    # Skip the protein id
                    # logger.info("We are skipping the protein IDs in the corpus creation.")
                    tokens = [w.strip(" ") for w in ln.rstrip("\n").split(" ")[1:]]
                    yield tokens
                else:
                    # The documents has not protein IDs
                    tokens = [w.strip(" ") for w in ln.rstrip("\n").split(" ")]
                    yield tokens



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



# @cython.profile(False)
# def set_logger(loggerName: str, lev: int, propagate: bool, customFmt: logging.Formatter = None) -> None:
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