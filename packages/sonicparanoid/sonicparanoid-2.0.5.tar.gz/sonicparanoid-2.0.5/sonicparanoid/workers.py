"""
 Contains function that will process queued jobs, among which alignments,
 and orthology inference.
"""

import os
import sys
import logging
import time
import subprocess
import multiprocessing as mp
import queue
import gc
import shutil
from filetype import is_archive
from typing import Dict, List, Any, Tuple, Set
from math import ceil
from tqdm import tqdm

from sonicparanoid import inpyranoid
from sonicparanoid import sys_tools as systools
from sonicparanoid import essentials_c as essentials
from sonicparanoid import mmseqs_parser_c as parser
from sonicparanoid import archiver


# Logger that will be used in this module
# It is child of the root logger and
# should be initialiazied using the function set_logger()
logger: logging.Logger = logging.getLogger()



__module_name__ = "Workers"
__source__ = "workers.py"
__author__ = "Salvatore Cosentino"
__license__ = "GPL"
__version__ = "2.9"
__maintainer__ = "Cosentino Salvatore"
__email__ = "salvo981@gmail.com"



def info():
    """
    Contains functions that will process queued jobs
    """
    print("MODULE NAME:\t%s"%__module_name__)
    print("SOURCE FILE NAME:\t%s"%__source__)
    print("MODULE VERSION:\t%s"%__version__)
    print("LICENSE:\t%s"%__license__)
    print("AUTHOR:\t%s"%__author__)
    print("EMAIL:\t%s"%__email__)



def assign_cores_to_job(sharedVals: List[int], lock, pair:str, debug: bool = False) -> int:
    """
    Modify shared variables and assign number of cores based on available resources
    """
    # sharedValues -> completedJob, requiredJobs, processing, waiting, cpusInUse, totCores
    if debug:
        print(f"\nassignCores ({pair}) :: START")

    # Set some variabales
    coresPerAln: int = 1
    with lock:
        # completedAln: int = sharedVals[0]
        remainingAln: int = sharedVals[1]
        processing: int = sharedVals[2]
        waiting: int = sharedVals[3]
        cpusInUse: int = sharedVals[4]
        totCores: int = sharedVals[5]
        # coresPerJob = ceil(totCores / remainingJobs)
        availCores: int = totCores - cpusInUse
        # coresPerAln = ceil(availCores / (remainingAln + processing + waiting))
        # coresPerAln = ceil(availCores / (remainingAln))
        coresPerAln = ceil(availCores / (remainingAln - processing))


        if coresPerAln <= 1:
            sharedVals[4] += 1
        else: # Assign an higher number of cores
            sharedVals[4] += coresPerAln

        if debug:
            print(f"availCores (before updating CPUs in use count):\t{availCores}")
            print(f"(remaining/processing/waiting):\t{remainingAln}\t{processing}\t{waiting}")
            print(f"remainingAln:\t{sharedVals[1]}")
            print(f"processing:\t{sharedVals[2]}")
            print(f"waiting:\t{sharedVals[3]}")
            print(f"cpusInUse:\t{sharedVals[4]}")
            print(f"Assigned CPUs:\t{coresPerAln}")

    # Return the number of assigned jobs
    return coresPerAln



# TODO: Diamond DB indexes are much smaller and depend on the input proteins
# Add 'Diamond mode' to the function and compute
def check_storage_for_db_indexing(outDir, reqSp=2, gbPerSpecies=0.95, debug=False):
    """Check that there is enough storage for the MMseqs2/Diamond DB index files."""
    if debug:
        print(f"\ncheck_storage_for_db_indexing :: START")
        print(f"Output directory: {outDir}")
        print(f"Number of databases to be created: {reqSp}")
        print(f"Required storage for index files: {(reqSp * gbPerSpecies):0.2f} gigabytes")
    availSpaceGb = round(shutil.disk_usage(outDir).free / 1024 ** 3, 2)
    requiredSpaceGb = round(reqSp * gbPerSpecies, 2)
    # set the output variable
    createIdxFiles = True
    if requiredSpaceGb >= availSpaceGb:
        createIdxFiles = False
        sys.stdout.write(f"\nINFO: {requiredSpaceGb:0.2f} gigabytes required to store the index files for MMseqs2.")
        sys.stderr.write(f"\nWARNING: only {availSpaceGb:0.2f} gigabytes avaliable, MMseqs/Diamond index files will not be created.")
        print("\nPlease consider freeing some disk space to take advantage of indexed DBs files.\n")
    if debug:
        print(f"Available storage in your system (Gigabytes): {availSpaceGb:0.2f}")
    #sys.exit('DEBUG :: check_storage_for_db_indexing')
    # return the boolean
    return createIdxFiles



def consume_blast_aln(jobs_queue, results_queue, runDir:str, dbDir:str, alnDir:str, keepAln:bool, minBitscore:int, compress:bool, complev:int, sharedValues: List[int], lock) -> None:
    """
    Perform essential or complete alignments for a pair of proteomes using BLAST.
    """
    while True:
        current_input = jobs_queue.get(True, 1)
        if current_input is None:
            break
        # extract job information
        pairTpl: Tuple[str, str] = ("", "")
        cntA: int = 0
        cntB: int = 0
        auxDir: str = os.path.join(runDir, "aux")
        inputSeqInfoDir: str = os.path.join(auxDir, "input_seq_info") 
        inDir: str = os.path.join(auxDir, "mapped_input")
        jobType: int = -1
        threads: int = 1
        pairTpl, jobType, cntA, cntB = current_input
        tmpA: str = ""
        tmpB: str = ""
        tmpA, tmpB = pairTpl
        pair: str = f"{tmpA}-{tmpB}"
        pairAlnDir: str = ""
        # time spent waiting  for the complete alignment to be completed
        wait_time: float = 0.
        sleepTime: float = 2.
        blastThr: int = 11 # default value for the Blastp word score to be considered
        # debug should be set only internally and should not be passed as a parameter
        debug: bool = False

        # will contain the results from the alignment job
        resList: List[Tuple[str, float, float, float, float, float, float, float, int]] = []
        # Given the pair A-B execute the alignments based on the following values
        # 0 -> Complete alignment
        # 1 -> Essentials alignment
        # execute the job based on the job type
        if jobType == 0: # Complete alignment
            if debug:
                print(f"\nComplete BLAST (FASTEST, or inter-proteome) alignment for pair {pair}")
            # Assign cores to the job
            threads = assign_cores_to_job(sharedValues, lock, pair, debug=False)
            # Updated shared variables
            with lock:
                sharedValues[2] += 1
            # create main directories and paths
            pairAlnDir = os.path.join(alnDir, tmpA)
            systools.makedir(pairAlnDir)
            inSeq = os.path.join(inDir, tmpA)
            dbSeq = os.path.join(inDir, tmpB)
            # Perfom the complete alignment
            parsedOutput, search_time, convert_time, parse_time = blast_1pass(inSeq, dbSeq, dbDir=dbDir, runDir=inputSeqInfoDir, outDir=pairAlnDir, keepAlign=keepAln, minBitscore=minBitscore, blastThr=blastThr, compress=compress, complev=complev, threads=threads, debug=False)[0:4]
            # exit if the BLAST formatted file generation was not successful
            if not os.path.isfile(parsedOutput):
                sys.stderr.write(f"\nERROR: the BLAST alignments for {pair} could not be created.\n")
                sys.exit(-2)
            # sharedValues -> completedAln, requiredAln, processing, waiting, cpusInUse, totCores
            # Updated shared variables
            with lock:
                sharedValues[0] += 1
                sharedValues[1] -= 1
                sharedValues[2] -= 1
                sharedValues[4] -= threads
            # add execution times to the output list
            resList.append((pair, search_time, convert_time, parse_time, wait_time, 100., 100., 0., threads))
            # sys.exit("DEBUG: @workers.consume_dmnd_aln_jobs. FIRST_COMPLETE_ALN")

        elif jobType == 1: # Essential alignments
            if debug:
                print(f"Essential BLAST alignment for pair {pair}")
            reductionDict: Dict[int, List[str]] = {}
            # output directory for the single run
            pairAlnDir = os.path.join(alnDir, tmpA)
            essentialFaDir: str = os.path.join(pairAlnDir, pair)
            refAlnDir: str = os.path.join(alnDir, tmpB)
            systools.makedir(pairAlnDir)
            systools.makedir(essentialFaDir)
            tmpRefAlnPath: str = os.path.join(refAlnDir, f"{tmpB}-{tmpA}")
            # if the reference alignment does not exist yet
            if not os.path.isfile(tmpRefAlnPath):
                # Updated shared variables
                with lock:
                    sharedValues[3] += 1
                # Increment the counter of waiting processes
                while not os.path.isfile(tmpRefAlnPath):
                    time.sleep(sleepTime)
                    wait_time += sleepTime
            # start timer for reduction files creation
            reductionTime: float = time.perf_counter()
            # create the subsets
            # Use different functions if the alignment files are compressed
            if compress:
                reductionDict, pctA, pctB = essentials.create_essential_stacks_from_archive(tmpRefAlnPath, cntB, cntA, debug=False)
            else:
                reductionDict, pctA, pctB = essentials.create_essential_stacks(tmpRefAlnPath, cntB, cntA, debug=False)
            del tmpRefAlnPath
            # extract sequences for A
            fastaPath: str = os.path.join(inDir, tmpA)
            reducedAPath: str = os.path.join(essentialFaDir, tmpA)
            essentials.extract_essential_proteins(fastaPath, reductionDict[int(tmpA)], reducedAPath, debug=False)
            # extract sequences for B
            fastaPath = os.path.join(inDir, tmpB)
            reducedBPath: str = os.path.join(essentialFaDir, tmpB)
            essentials.extract_essential_proteins(fastaPath, reductionDict[int(tmpB)], reducedBPath, debug=False)
            # create BLAST database files
            blast_createdb(reducedBPath, outDir=essentialFaDir, debug=False)
            reductionTime = round(time.perf_counter() - reductionTime, 3)
            # Assign cores to the job
            threads = assign_cores_to_job(sharedValues, lock, pair, debug=False)
            # Now the processing can start
            with lock:
                sharedValues[2] += 1
                if wait_time > 0: # Decrease if it actually waited...
                    # print(f"\njob {pair} Waited for {wait_time}!")
                    sharedValues[3] -= 1
            # perform the alignments
            parsedOutput, search_time, convert_time, parse_time = blast_1pass(reducedAPath, reducedBPath, dbDir=essentialFaDir, runDir=essentialFaDir, outDir=pairAlnDir, keepAlign=keepAln, minBitscore=minBitscore, blastThr=blastThr, compress=compress, complev=complev, threads=threads, debug=False)[0:4]
            # Updated shared variables
            with lock:
                sharedValues[0] += 1
                sharedValues[1] -= 1
                sharedValues[2] -= 1
                sharedValues[4] -= threads
            # add execution times to the output list
            resList.append((pair, search_time, convert_time, parse_time, wait_time, pctA, pctB, reductionTime, threads))
            # sys.exit("DEBUG: @workers.consume_blast_aln_jobs. ESSENTIAL_ALN")

        # add the results in the output queue
        results_queue.put(resList)



# HACK: remove when optiomized job queueing has been implemented
'''
def consume_blast_aln_jobs(jobs_queue, results_queue, runDir:str, dbDir:str, alnDir:str, keepAln:bool, cutoff:int, compress:bool, complev:int) -> None:
    """
    Perform essential or complete alignments for a pair of proteomes using Diamond.
    Only one complete alignment is performed if it is intra-proteome alignment.
    """
    while True:
        current_input = jobs_queue.get(True, 1)
        if current_input is None:
            break
        # extract job information
        pairTpl: Tuple[str, str] = ("", "")
        cntA: int = 0
        cntB: int = 0
        sizeA: int = 0
        sizeB: int = 0
        tmpDbSize: int = 0
        auxDir: str = os.path.join(runDir, "aux")
        inputSeqInfoDir: str = os.path.join(auxDir, "input_seq_info") 
        inDir: str = os.path.join(auxDir, "mapped_input")
        jobType: int = -1
        threads: int = 1
        pairTpl, jobType, threads, cntA, cntB, sizeA, sizeB = current_input
        tmpA: str = ""
        tmpB: str = ""
        tmpA, tmpB = pairTpl
        pair: str = f"{tmpA}-{tmpB}"
        invPair: str = f"{tmpB}-{tmpA}"
        pairAlnDir: str = ""
        # debug should be set only internally and should not be passed as a parameter
        debug: bool = False

        # will contain the results from the alignment job
        resList: List[Tuple[str, float, float, float, float, float, float]] = []
        # Given the pair A-B execute the alignments based on the following values
        # 0 -> A-B
        # 1 -> B-A only (essentials)
        # 2 -> A-B and B-A (essentials)
        # 3 -> B-A only (complete)
        # 4 -> A-B and B-A (complete)
        # execute the job based on the job type
        if (jobType == 0) or (jobType == 2) or (jobType == 4): # The first complete alignment
            if debug:
                print(f"\nComplete BLAST (FASTEST) alignment for pair {pair}")
            # create main directories and paths
            pairAlnDir = os.path.join(alnDir, tmpA)
            systools.makedir(pairAlnDir)
            inSeq = os.path.join(inDir, tmpA)
            dbSeq = os.path.join(inDir, tmpB)
            tmpDbSize = sizeB
            # define the for the temporary directory
            # perfom the complete alignment

            # Check if the alignment is between the same proteomes
            # HACK the original version only uses BLAST
            # parsedOutput, search_time, convert_time, parse_time, tot_time = blast_1pass(inSeq, dbSeq, dbDir=dbDir, runDir=inputSeqInfoDir, outDir=pairAlnDir, keepAlign=keepAln, cutoff=cutoff, dbSize=tmpDbSize, compress=compress, complev=complev, threads=threads, debug=False)
            if tmpA != tmpB:
                parsedOutput, search_time, convert_time, parse_time, tot_time = blast_1pass(inSeq, dbSeq, dbDir=dbDir, runDir=inputSeqInfoDir, outDir=pairAlnDir, keepAlign=keepAln, cutoff=cutoff, dbSize=tmpDbSize, compress=compress, complev=complev, threads=threads, debug=False)
            else: # Use Diamond for intraproteome alignments
                parsedOutput, search_time, convert_time, parse_time, tot_time = dmnd_1pass(inSeq, dbSeq, dbDir=dbDir, runDir=inputSeqInfoDir, outDir=pairAlnDir, keepAlign=keepAln, sensitivity="ultra-sensitive", cutoff=cutoff, indexDB=False, dbSize=tmpDbSize, compress=compress, complev=complev, useBlastDb=True, cbstats=4, threads=threads, debug=False)
            # exit if the BLAST formatted file generation was not successful
            if not os.path.isfile(parsedOutput):
                sys.stderr.write(f"\nERROR: the Diamond alignments for {pair} could not be created.\n")
                sys.exit(-2)
            # add execution times to the output list
            resList.append((pair, search_time, convert_time, parse_time, 100., 100., 0.))
            # sys.exit("DEBUG: @workers.consume_blast_aln_jobs. FIRST_COMPLETE_ALN")

        # perform the essential alignments if required
        if (jobType == 3) or (jobType == 4): # Complete alignments
            if debug:
                print(f"Complete BLAST alignment for pair {invPair}")
            # create main directories and paths
            pairAlnDir = os.path.join(alnDir, tmpB)
            systools.makedir(pairAlnDir)
            inSeq = os.path.join(inDir, tmpB)
            dbSeq = os.path.join(inDir, tmpA)
            tmpDbSize = sizeA
            # define the for the temporary directory
            # perfom the complete alignment
            parsedOutput, search_time, convert_time, parse_time, tot_time = blast_1pass(inSeq, dbSeq, dbDir=dbDir, runDir=inputSeqInfoDir, outDir=pairAlnDir, keepAlign=keepAln, cutoff=cutoff, dbSize=tmpDbSize, compress=compress, complev=complev, threads=threads, debug=False)
            del tot_time
            # exit if the BLAST formatted file generation was not successful
            if not os.path.isfile(parsedOutput):
                sys.stderr.write(f"\nERROR: the BLAST alignments for {pair} could not be created.\n")
                sys.exit(-2)
            # add execution times to the output list
            resList.append((invPair, search_time, convert_time, parse_time, 100., 100., 0.))
            # sys.exit("DEBUG: @workers.consume_blast_aln_jobs. COMPLETE_ALN")
        elif (jobType == 1) or (jobType == 2): # Essential alignments
            if debug:
                print(f"Essential BLAST alignment for pair {invPair}")
            reductionDict: Dict[int, List[str]] = {}
            # output directory for the single run
            pairAlnDir = os.path.join(alnDir, tmpB)
            essentialFaDir: str = os.path.join(pairAlnDir, invPair)
            refAlnDir: str = os.path.join(alnDir, tmpA)
            systools.makedir(pairAlnDir)
            systools.makedir(essentialFaDir)
            tmpPathAB: str = os.path.join(refAlnDir, f"{tmpA}-{tmpB}")
            # if the reference alignment does not exist yet
            if not os.path.isfile(tmpPathAB):
                sys.stderr.write(f"\nERROR: the reference alignment for pair {os.path.basename(tmpPathAB)} does not exist.")
                sys.stderr.write(f"\nYou must create the alignment for {pair} before aligning the pair {invPair}.")
                sys.exit(-7)
                results_queue.put((pair, 0., 0., 0., 0., 0., 0.))
                continue
            # start timer for reduction files creation
            reductionTime: float = time.perf_counter()
            # create the subsets
            # Use different functions if the alignment files are compressed
            if compress:
                reductionDict, pctB, pctA = essentials.create_essential_stacks_from_archive(tmpPathAB, cntA, cntB, debug=False)
            else:
                reductionDict, pctB, pctA = essentials.create_essential_stacks(tmpPathAB, cntA, cntB, debug=False)
            del tmpPathAB
            # extract sequences for A
            fastaPath: str = os.path.join(inDir, tmpA)
            reducedAPath: str = os.path.join(essentialFaDir, tmpA)
            essentials.extract_essential_proteins(fastaPath, reductionDict[int(tmpA)], reducedAPath, debug=False)
            # extract sequences for B
            fastaPath = os.path.join(inDir, tmpB)
            reducedBPath: str = os.path.join(essentialFaDir, tmpB)
            essentials.extract_essential_proteins(fastaPath, reductionDict[int(tmpB)], reducedBPath, debug=False)
            # create mmseqs database files
            reducedDbAPath: str = blast_createdb(reducedAPath, outDir=essentialFaDir, debug=False)[-1]
            reductionTime = round(time.perf_counter() - reductionTime, 3)
            # perform the alignments
            tmpDbSize = sizeA
            parsedOutput, search_time, convert_time, parse_time, tot_time = blast_1pass(reducedBPath, reducedAPath, dbDir=essentialFaDir, runDir=essentialFaDir, outDir=pairAlnDir, keepAlign=keepAln, cutoff=cutoff, dbSize=tmpDbSize, compress=compress, complev=complev, threads=threads, debug=False)
            # sys.exit("DEBUG: @workers.consume_blast_aln_jobs. ESSENTIAL_ALN")

            # add execution times to the output list
            resList.append((invPair, search_time, convert_time, parse_time, pctA, pctB, reductionTime))

        # add the results in the output queue
        results_queue.put(resList)
'''


def consume_blast_createdb(jobs_queue, results_queue, inDir, dbDir):
    """Create a BLAST database for the species in input dir."""
    while True:
        current_sp = jobs_queue.get(True, 1)
        if current_sp is None:
            break
        # check the query db name
        inFastaPath = os.path.join(inDir, current_sp)
        if not os.path.isfile(inFastaPath):
            sys.stderr.write(f"ERROR: the input FASTA file \n{inFastaPath}\n was not found\n")
            sys.exit(-2)
        # Set path to the db path
        seqDBpath: str = os.path.join(dbDir, f"{current_sp}.dmnd")
        # create the database if does not exist yet
        if not os.path.isfile(seqDBpath):
            start_time = time.perf_counter()
            # BLAST DB creation example:
            # makeblastdb -input_type fasta -dbtype prot -in <myproteome> -out <dbs_blast/myproteome>
            blast_createdb(inFastaPath, outDir=dbDir, debug=False)
            end_time = time.perf_counter()
            # add the execution time to the results queue
            results_queue.put((current_sp, str(round(end_time - start_time, 2))))



def consume_dmnd_aln(jobs_queue, results_queue, runDir:str, dbDir:str, alnDir:str, create_idx:bool, keepAln:bool, sensitivity:str, minBitscore:int, compress:bool, complev:int, sharedValues: List[int], lock) -> None:
    """
    Perform essential or complete alignments for a pair of proteomes using Diamond.
    A single alignment is performed for each pair.
    """
    while True:
        current_input = jobs_queue.get(True, 1)
        if current_input is None:
            break
        # extract job information
        pairTpl: Tuple[str, str] = ("", "")
        cntA: int = 0
        cntB: int = 0
        auxDir: str = os.path.join(runDir, "aux")
        inputSeqInfoDir: str = os.path.join(auxDir, "input_seq_info") 
        inDir: str = os.path.join(auxDir, "mapped_input")
        jobType: int = -1
        threads: int = 1
        pairTpl, jobType, cntA, cntB = current_input
        tmpA: str = ""
        tmpB: str = ""
        tmpA, tmpB = pairTpl
        pair: str = f"{tmpA}-{tmpB}"
        pairAlnDir: str = ""
        # time spent waiting  for the complete alignment to be completed
        wait_time: float = 0.
        sleepTime: float = 2.
        # debug should be set only internally and should not be passed as a parameter
        debug: bool = False

        # will contain the results from the alignment job
        resList: List[Tuple[str, float, float, float, float, float, float, float, int]] = []
        # Given the pair A-B execute the alignments based on the following values
        # 0 -> Complete alignment
        # 1 -> Essentials alignment
        # execute the job based on the job type
        if jobType == 0: # Complete alignment
            if debug:
                print(f"\nComplete Diamond (FASTEST, or inter-proteome) alignment for pair {pair}")
            # Assign cores to the job
            threads = assign_cores_to_job(sharedValues, lock, pair, debug=False)
            # Updated shared variables
            with lock:
                sharedValues[2] += 1

            # create main directories and paths
            pairAlnDir = os.path.join(alnDir, tmpA)
            systools.makedir(pairAlnDir)
            inSeq = os.path.join(inDir, tmpA)
            dbSeq = os.path.join(inDir, tmpB)
            # perfom the complete alignment
            parsedOutput, search_time, convert_time, parse_time, tot_time = dmnd_1pass(inSeq, dbSeq, dbDir=dbDir, runDir=inputSeqInfoDir, outDir=pairAlnDir, keepAlign=keepAln, sensitivity=sensitivity, minBitscore=minBitscore, indexDB=create_idx, compress=compress, complev=complev, threads=threads, debug=False)
            del tot_time
            # exit if the BLAST formatted file generation was not successful
            if not os.path.isfile(parsedOutput):
                sys.stderr.write(f"\nERROR: the Diamond alignments for {pair} could not be created.\n")
                sys.exit(-2)
            # sharedValues -> completedAln, requiredAln, processing, waiting, cpusInUse, totCores
            # Updated shared variables
            with lock:
                sharedValues[0] += 1
                sharedValues[1] -= 1
                sharedValues[2] -= 1
                sharedValues[4] -= threads
                '''
                print(f"\nJob {pair} DONE!")
                print(f"Completed jobs:\t{sharedValues[0]}")
                print(f"Cores in use:\t{sharedValues[4]}")
                '''
            # add execution times to the output list
            resList.append((pair, search_time, convert_time, parse_time, wait_time, 100., 100., 0., threads))
            # sys.exit("DEBUG: @workers.consume_dmnd_aln_jobs. FIRST_COMPLETE_ALN")
        elif jobType == 1: # Essential alignments
            if debug:
                print(f"\nEssential Diamond alignment for pair {pair}")
            reductionDict: Dict[int, List[str]] = {}
            # output directory for the single run
            pairAlnDir = os.path.join(alnDir, tmpA)
            essentialFaDir: str = os.path.join(pairAlnDir, pair)
            refAlnDir: str = os.path.join(alnDir, tmpB)
            systools.makedir(pairAlnDir)
            systools.makedir(essentialFaDir)
            tmpRefAlnPath: str = os.path.join(refAlnDir, f"{tmpB}-{tmpA}")
            '''
            # print(f"tmpA/cntA/sizeA:\t{tmpA}\t{cntA}\t{sizeA}")
            # print(f"tmpB/cntB/sizeB:\t{tmpB}\t{cntB}\t{sizeB}")
            # print(f"essentialFaDir:\t{essentialFaDir}")
            # print(f"tmpRefAlnPath:\t{tmpRefAlnPath}")
            '''
            # if the reference alignment does not exist yet
            if not os.path.isfile(tmpRefAlnPath):
                # Updated shared variables
                # sharedValues -> completedAln, requiredAln, processing, waiting, cpusInUse, totCores
                with lock:
                    sharedValues[3] += 1
                    # print(f"\njob {pair} in Hold!")
                    # print(f"Completed aln:\t{sharedValues[0]}")
                    # print(f"Cores in use:\t{sharedValues[4]}")

                # Increment the counter of waiting processes
                while not os.path.isfile(tmpRefAlnPath):
                    time.sleep(sleepTime)
                    wait_time += sleepTime
                    # print(f"Waiting ({pair}) [{wait_time}\"] -> Cores in use:\t{sharedValues[4]}")

            # start timer for reduction files creation
            reductionTime: float = time.perf_counter()
            # create the subsets
            # Use different functions if the alignment files are compressed
            if compress:
                reductionDict, pctA, pctB = essentials.create_essential_stacks_from_archive(tmpRefAlnPath, cntB, cntA, debug=False)
            else:
                reductionDict, pctA, pctB = essentials.create_essential_stacks(tmpRefAlnPath, cntB, cntA, debug=False)
            del tmpRefAlnPath
            # extract sequences for A
            fastaPath: str = os.path.join(inDir, tmpA)
            reducedAPath: str = os.path.join(essentialFaDir, tmpA)
            essentials.extract_essential_proteins(fastaPath, reductionDict[int(tmpA)], reducedAPath, debug=False)
            # extract sequences for B
            fastaPath = os.path.join(inDir, tmpB)
            reducedBPath: str = os.path.join(essentialFaDir, tmpB)
            essentials.extract_essential_proteins(fastaPath, reductionDict[int(tmpB)], reducedBPath, debug=False)
            # create diamond database files
            dmnd_createdb(reducedBPath, outDir=essentialFaDir, threads=threads, debug=False)
            # HACK: The creation of the indexes is an overkill in most of the cases
            # if create_idx:
            #     dmnd_createindex(reducedDbBPath, sensitivity=sensitivity, threads=threads, debug=False)
            reductionTime = round(time.perf_counter() - reductionTime, 3)

            # Assign cores to the job and update counters
            threads = assign_cores_to_job(sharedValues, lock, pair, debug=False)
            # Now the processing can start
            with lock:
                sharedValues[2] += 1
                if wait_time > 0: # Decrease if it actually waited...
                    # print(f"\njob {pair} Waited for {wait_time}!")
                    sharedValues[3] -= 1

            # perform the alignments
            # parsedOutput, search_time, convert_time, parse_time, tot_time = dmnd_1pass(reducedBPath, reducedBPath, dbDir=essentialFaDir, runDir=essentialFaDir, outDir=pairAlnDir, keepAlign=keepAln, sensitivity=sensitivity, minBitscore=minBitscore, indexDB=create_idx, compress=compress, complev=complev, threads=threads, debug=False)
            # NOTE: Force the create_idx to False, as we are not using the IDX as it would be used only one time
            parsedOutput, search_time, convert_time, parse_time, tot_time = dmnd_1pass(reducedAPath, reducedBPath, dbDir=essentialFaDir, runDir=essentialFaDir, outDir=pairAlnDir, keepAlign=keepAln, sensitivity=sensitivity, minBitscore=minBitscore, indexDB=False, compress=compress, complev=complev, threads=threads, debug=False)

            # sharedValues -> completedAln, requiredAln, processing, waiting, cpusInUse, totCores
            # Updated shared variables
            with lock:
                sharedValues[0] += 1
                sharedValues[1] -= 1
                sharedValues[2] -= 1
                sharedValues[4] -= threads
                # print(f"\nJob {pair} [essential] DONE!")
                # print(f"Completed jobs:\t{sharedValues[0]}")
                # print(f"Cores in use:\t{sharedValues[4]}")

            # add execution times to the output list
            resList.append((pair, search_time, convert_time, parse_time, wait_time, pctA, pctB, reductionTime, threads))
            # sys.exit("DEBUG: @workers.consume_dmnd_aln_jobs. ESSENTIAL_ALN")

        # add the results in the output queue
        results_queue.put(resList)



def consume_dmnd_createdb(jobs_queue, results_queue, inDir, dbDir, create_idx=True, sensitivity="sensitive"):
    """Create a Diamond database for the species in input dir."""
    while True:
        current_sp = jobs_queue.get(True, 1)
        if current_sp is None:
            break
        # check the query db name
        inFastaPath = os.path.join(inDir, current_sp)
        if not os.path.isfile(inFastaPath):
            sys.stderr.write(f"ERROR: the input FASTA file \n{inFastaPath}\n was not found\n")
            sys.exit(-2)
        # Set path to the db path
        seqDBpath: str = os.path.join(dbDir, f"{current_sp}.dmnd")
        # create the database if does not exist yet
        if not os.path.isfile(seqDBpath):
            start_time = time.perf_counter()
            dmnd_createdb(inFastaPath, outDir=dbDir, threads=1, debug=False)
            if create_idx:
                dmnd_createindex(seqDBpath, sensitivity=sensitivity, threads=1, debug=False)
            end_time = time.perf_counter()
            # add the execution time to the results queue
            results_queue.put((current_sp, str(round(end_time - start_time, 2))))



def consume_mmseqs_createdb(jobs_queue, results_queue, inDir, dbDir, create_idx=True):
    """Create a a mmseqs2 database for the species in input dir."""
    while True:
        current_sp = jobs_queue.get(True, 1)
        if current_sp is None:
            break
        # check the query db name
        #queryDBname = os.path.basename(inFasta)
        inQueryPath = os.path.join(inDir, current_sp)
        if not os.path.isfile(inQueryPath):
            sys.stderr.write(f"ERROR: the input FASTA file \n{inQueryPath}\n was not found\n")
            sys.exit(-2)
        queryDBname = f"{current_sp}.mmseqs2db"
        queryDBpath = f"{dbDir}{queryDBname}"
        # create the database if does not exist yet
        if not os.path.isfile(queryDBpath):
            start_time = time.perf_counter()
            mmseqs_createdb(inQueryPath, outDir=dbDir, dbType=1, debug=False)
            if create_idx:
                mmseqs_createindex(queryDBpath, threads=2, debug=False)
            end_time = time.perf_counter()
            # add the execution time to the results queue
            results_queue.put((current_sp, str(round(end_time - start_time, 2))))



def consume_mmseqs_aln(jobs_queue, results_queue, runDir:str, dbDir:str, alnDir:str, keepAln:bool, sensitivity:float, minBitscore:float, pmtx:str, compress:bool, complev:int, sharedValues: List[int], lock) -> None:
    """
    Perform essential or complete alignments for a pair of proteomes using MMseqs2.
    """
    while True:
        current_input = jobs_queue.get(True, 1)
        if current_input is None:
            break
        # extract job information
        pairTpl: Tuple[str, str] = ("", "")
        cntA: int = 0
        cntB: int = 0
        auxDir: str = os.path.join(runDir, "aux")
        inputSeqInfoDir: str = os.path.join(auxDir, "input_seq_info") 
        inDir: str = os.path.join(auxDir, "mapped_input")
        jobType: int = -1
        threads: int = 1
        search_time: float = 0.
        convert_time: float = 0.
        parse_time: float = 0.
        pairTpl, jobType, cntA, cntB = current_input
        tmpA: str = ""
        tmpB: str = ""
        tmpA, tmpB = pairTpl
        pair: str = f"{tmpA}-{tmpB}"
        pairAlnDir: str = ""
        # time spent waiting  for the complete alignment to be completed
        wait_time: float = 0.
        sleepTime: float = 2.
        # debug should be set only internally and should not be passed as a parameter
        debug: bool = False

        # will contain the results from the alignment job
        resList: List[Tuple[str, float, float, float, float, float, float, float, int]] = []
        # Given the pair A-B execute the alignments based on the following values
        # 0 -> Complete alignment
        # 1 -> Essentials alignment
        # execute the job based on the job type
        if jobType == 0: # Complete alignment
            if debug:
                print(f"\nComplete (FASTEST) alignment for pair {pair}. jobType:\t{jobType}")
            # Assign cores to the job
            threads = assign_cores_to_job(sharedValues, lock, pair, debug=False)
            # Updated shared variables
            with lock:
                sharedValues[2] += 1
            # create main directories and paths
            pairAlnDir = os.path.join(alnDir, tmpA)
            systools.makedir(pairAlnDir)
            inSeq = os.path.join(inDir, tmpA)
            dbSeq = os.path.join(inDir, tmpB)
            # define the for the temporary directory
            tmpMMseqsDirName = f"tmp_{pair}"
            # perfom the complete alignment
            parsedOutput, search_time, convert_time, parse_time = mmseqs_1pass(inSeq, dbSeq, dbDir=dbDir, runDir=inputSeqInfoDir, outDir=pairAlnDir, tmpDirName=tmpMMseqsDirName, keepAlign=keepAln, sensitivity=sensitivity, evalue=1000, minBitscore=minBitscore, pmtx=pmtx, compress=compress, complev=complev, threads=threads, debug=False)[0:4]
            # exit if the BLAST formatted file generation was not successful
            if not os.path.isfile(parsedOutput):
                sys.stderr.write(f"\nERROR: the MMseqs2 raw alignments for {pair} could not be converted into the BLAST format.\n")
                sys.exit(-2)

            # Updated shared variables
            with lock:
                sharedValues[0] += 1
                sharedValues[1] -= 1
                sharedValues[2] -= 1
                sharedValues[4] -= threads
            # add execution times to the output list
            resList.append((pair, search_time, convert_time, parse_time, wait_time, 100., 100., 0., threads))
            # sys.exit("DEBUG: @workers.consume_mmseqs_aln. FIRST_COMPLETE_ALN")

        elif jobType == 1: # Essential alignments
            if debug:
                print(f"Essential alignment for pair {pair}. jobType: {jobType}")
            reductionDict: Dict[int, List[str]] = {}
            # output directory for the single run
            pairAlnDir = os.path.join(alnDir, tmpA)
            essentialFaDir: str = os.path.join(pairAlnDir, pair)
            refAlnDir: str = os.path.join(alnDir, tmpB)
            systools.makedir(pairAlnDir)
            systools.makedir(essentialFaDir)
            tmpRefAlnPath: str = os.path.join(refAlnDir, f"{tmpB}-{tmpA}")
            # if the reference alignment does not exist yet
            if not os.path.isfile(tmpRefAlnPath):
                # Updated shared variables
                with lock:
                    sharedValues[3] += 1
                # Increment the counter of waiting processes
                while not os.path.isfile(tmpRefAlnPath):
                    time.sleep(sleepTime)
                    wait_time += sleepTime
            # start timer for reduction files creation
            reductionTime: float = time.perf_counter()

            # create the subsets
            # Use different functions if the alignment files are compressed
            if compress:
                reductionDict, pctA, pctB = essentials.create_essential_stacks_from_archive(tmpRefAlnPath, cntB, cntA, debug=False)
            else:
                reductionDict, pctA, pctB = essentials.create_essential_stacks(tmpRefAlnPath, cntB, cntA, debug=False)
            del tmpRefAlnPath
            # extract sequences for A
            fastaPath: str = os.path.join(inDir, tmpA)
            reducedAPath: str = os.path.join(essentialFaDir, tmpA)
            essentials.extract_essential_proteins(fastaPath, reductionDict[int(tmpA)], reducedAPath, debug=False)
            # extract sequences for B
            fastaPath = os.path.join(inDir, tmpB)
            reducedBPath: str = os.path.join(essentialFaDir, tmpB)
            essentials.extract_essential_proteins(fastaPath, reductionDict[int(tmpB)], reducedBPath, debug=False)
            # create mmseqs database files
            mmseqs_createdb(reducedAPath, outDir=essentialFaDir, debug=False)
            mmseqs_createdb(reducedBPath, outDir=essentialFaDir, debug=False)
            reductionTime = round(time.perf_counter() - reductionTime, 3)
            # Assign cores to the job
            threads = assign_cores_to_job(sharedValues, lock, pair, debug=False)
            # Now the processing can start
            with lock:
                sharedValues[2] += 1
                if wait_time > 0: # Decrease if it actually waited...
                    # print(f"\njob {pair} Waited for {wait_time}!")
                    sharedValues[3] -= 1
            # perform the alignments
            parsedOutput, search_time, convert_time, parse_time = mmseqs_1pass(reducedAPath, reducedBPath, dbDir=essentialFaDir, runDir=essentialFaDir, outDir=pairAlnDir, tmpDirName=f"tmp_{pair}", keepAlign=keepAln, sensitivity=sensitivity, evalue=1000, minBitscore=minBitscore, pmtx=pmtx, compress=compress, complev=complev, threads=threads, debug=False)[0:4]
            # Updated shared variables
            with lock:
                sharedValues[0] += 1
                sharedValues[1] -= 1
                sharedValues[2] -= 1
                sharedValues[4] -= threads
            # add execution times to the output list
            resList.append((pair, search_time, convert_time, parse_time, wait_time, pctA, pctB, reductionTime, threads))
            # sys.exit("DEBUG: @workers.consume_mmseqs_aln. ESSENTIAL_ALN")

        # add the results in the output queue
        results_queue.put(resList)



# TODO: remove when optimized function for job queuing is complete
'''
def consume_mmseqs_aln_jobs(jobs_queue, results_queue, runDir:str, dbDir:str, alnDir:str, keepAln:bool, sensitivity:float, cutoff:float, pmtx:str, compress:bool, complev:int) -> None:
    """
    Perform essential or complete alignments for a pair of proteomes using MMseqs2.
    Only one complete alignment is performed if it is intra-proteome alignment.
    """
    while True:
        current_input = jobs_queue.get(True, 1)
        if current_input is None:
            break
        # extract job information
        pairTpl: Tuple[str, str] = ("", "")
        cntA: int = 0
        cntB: int = 0
        sizeA: int = 0
        sizeB: int = 0
        auxDir: str = os.path.join(runDir, "aux")
        inputSeqInfoDir: str = os.path.join(auxDir, "input_seq_info") 
        inDir: str = os.path.join(auxDir, "mapped_input")
        jobType: int = -1
        threads: int = 1
        search_time: float = 0.
        convert_time: float = 0.
        parse_time: float = 0.
        tot_time: float = 0.
        pairTpl, jobType, threads, cntA, cntB, sizeA, sizeB = current_input
        tmpA: str = ""
        tmpB: str = ""
        tmpA, tmpB = pairTpl
        pair: str = f"{tmpA}-{tmpB}"
        invPair: str = f"{tmpB}-{tmpA}"
        pairAlnDir: str = ""
        # debug should be set only internally and should not be passed as a parameter
        debug: bool = False

        # will contain the results from the alignment job
        resList: List[Tuple[str, float, float, float, float, float, float]] = []
        # Given the pair A-B execute the alignments based on the following values
        # 0 -> A-B
        # 1 -> B-A only (essentials)
        # 2 -> A-B and B-A (essentials)
        # 3 -> B-A only (complete)
        # 4 -> A-B and B-A (complete)
        # execute the job based on the job type
        if (jobType == 0) or (jobType == 2) or (jobType == 4): # The first complete alignment
            if debug:
                print(f"\nComplete (FASTEST) alignment for pair {pair}. jobType:\t{jobType}")
            # create main directories and paths
            pairAlnDir = os.path.join(alnDir, tmpA)
            systools.makedir(pairAlnDir)
            inSeq = os.path.join(inDir, tmpA)
            dbSeq = os.path.join(inDir, tmpB)
            # define the for the temporary directory
            tmpMMseqsDirName = f"tmp_{pair}"
            # perfom the complete alignment
            parsedOutput, search_time, convert_time, parse_time, tot_time = mmseqs_1pass(inSeq, dbSeq, dbDir=dbDir, runDir=inputSeqInfoDir, outDir=pairAlnDir, tmpDirName=tmpMMseqsDirName, keepAlign=keepAln, sensitivity=sensitivity, evalue=1000, cutoff=cutoff, pmtx=pmtx, compress=compress, complev=complev, threads=threads, debug=False)
            del tot_time
            # exit if the BLAST formatted file generation was not successful
            if not os.path.isfile(parsedOutput):
                sys.stderr.write(f"\nERROR: the MMseqs2 raw alignments for {pair} could not be converted into the BLAST format.\n")
                sys.exit(-2)
            # add execution times to the output list
            resList.append((pair, search_time, convert_time, parse_time, 100., 100., 0.))
            # sys.exit("DEBUG: @workers.consume_mmseqs_aln_jobs. FIRST_COMPLETE_ALN")

        # perform the essential alignments if required
        if (jobType == 3) or (jobType == 4): # Complete alignments
            if debug:
                print(f"Complete alignment for pair {invPair}. jobType:\t{jobType}")
            # create main directories and paths
            # pairAlnDir: str = os.path.join(alnDir, invPair)
            pairAlnDir = os.path.join(alnDir, tmpB)
            systools.makedir(pairAlnDir)
            inSeq = os.path.join(inDir, tmpB)
            dbSeq = os.path.join(inDir, tmpA)
            # define the for the temporary directory
            tmpMMseqsDirName = f"tmp_{invPair}"
            # perfom the complete alignment
            parsedOutput, search_time, convert_time, parse_time, tot_time = mmseqs_1pass(inSeq, dbSeq, dbDir=dbDir, runDir=inputSeqInfoDir, outDir=pairAlnDir, tmpDirName=tmpMMseqsDirName, keepAlign=keepAln, sensitivity=sensitivity, evalue=1000, cutoff=cutoff, pmtx=pmtx, compress=compress, complev=complev, threads=threads, debug=False)
            del tot_time
            # exit if the BLAST formatted file generation was not successful
            if not os.path.isfile(parsedOutput):
                sys.stderr.write(f"\nERROR: the MMseqs2 raw alignments for {invPair} could not be converted into the BLAST format.\n")
                sys.exit(-2)
            # add execution times to the output list
            resList.append((invPair, search_time, convert_time, parse_time, 100., 100., 0.))
            # sys.exit("DEBUG: @workers.consume_mmseqs_aln_jobs. COMPLETE_ALN")
        elif (jobType == 1) or (jobType == 2): # Essential alignments
            if debug:
                print(f"Essential alignment for pair {invPair}. jobType: {jobType}")
            reductionDict: Dict[int, List[str]] = {}
            # output directory for the single run
            pairAlnDir = os.path.join(alnDir, tmpB)
            essentialFaDir: str = os.path.join(pairAlnDir, invPair)
            refAlnDir: str = os.path.join(alnDir, tmpA)
            systools.makedir(pairAlnDir)
            systools.makedir(essentialFaDir)
            # tmpDir: str = os.path.join(runDir, "mapped_input")
            tmpPathAB: str = os.path.join(refAlnDir, f"{tmpA}-{tmpB}")
            # if the reference alignment does not exist yet
            if not os.path.isfile(tmpPathAB):
                sys.stderr.write(f"\nERROR: the reference alignment for pair {os.path.basename(tmpPathAB)} does not exist.")
                sys.stderr.write(f"\nYou must create the alignment for {pair} before aligning the pair {invPair}.")
                sys.exit(-7)
                results_queue.put((pair, 0., 0., 0., 0., 0., 0.))
                continue
            # start timer for reduction files creation
            reductionTime: float = time.perf_counter()
            # create the subsets
            # Use different functions if the alignment files are compressed
            if compress:
                reductionDict, pctB, pctA = essentials.create_essential_stacks_from_archive(tmpPathAB, cntA, cntB, debug=False)
            else:
                reductionDict, pctB, pctA = essentials.create_essential_stacks(tmpPathAB, cntA, cntB, debug=False)
            del tmpPathAB
            # extract sequences for A
            fastaPath: str = os.path.join(inDir, tmpA)
            reducedAPath: str = os.path.join(essentialFaDir, tmpA)
            essentials.extract_essential_proteins(fastaPath, reductionDict[int(tmpA)], reducedAPath, debug=False)
            # extract sequences for B
            fastaPath = os.path.join(inDir, tmpB)
            reducedBPath: str = os.path.join(essentialFaDir, tmpB)
            essentials.extract_essential_proteins(fastaPath, reductionDict[int(tmpB)], reducedBPath, debug=False)
            # create mmseqs database files
            mmseqs_createdb(reducedBPath, outDir=essentialFaDir, debug=False)
            mmseqs_createdb(reducedAPath, outDir=essentialFaDir, debug=False)[-1]
            reductionTime = round(time.perf_counter() - reductionTime, 3)
            # create temporary directory name
            tmpMMseqsDirName = f"tmp_{invPair}"
            # perform the alignments
            parsedOutput, search_time, convert_time, parse_time, tot_time = mmseqs_1pass(reducedBPath, reducedAPath, dbDir=essentialFaDir, runDir=essentialFaDir, outDir=pairAlnDir, tmpDirName=tmpMMseqsDirName, keepAlign=keepAln, sensitivity=sensitivity, evalue=1000, cutoff=cutoff, pmtx=pmtx, compress=compress, complev=complev, threads=threads, debug=False)
            # add execution times to the output list
            resList.append((invPair, search_time, convert_time, parse_time, pctA, pctB, reductionTime))
            # sys.exit("DEBUG: @workers.consume_mmseqs_aln_jobs. ESSENTIAL_ALN")

        # sys.exit("DEBUG :: consume_mmseqs_aln_jobs")

        # add the results in the output queue
        results_queue.put(resList)
'''


def consume_compress_jobs(jobs_queue, complev:int, removeSrc:bool):
    """Compress a file."""
    while True:
        current_paths = jobs_queue.get(True, 1)
        if current_paths is None:
            break
        # srcpath, outpath = current_paths
        archiver.compress_gzip(current_paths[0], current_paths[1], complev=complev, removeSrc=removeSrc, debug=False)



def consume_unarchive_jobs(jobs_queue, removeSrc:bool):
    """Extract archived file."""
    while True:
        current_paths = jobs_queue.get(True, 1)
        if current_paths is None:
            break
        # check the query db name
        archiver.extract_gzip(current_paths[0], current_paths[1], removeSrc=removeSrc, debug=False)


# TODO: Remove this function since it is not being used
'''
def consume_essential_alignments(jobs_queue, results_queue, runDir: str, alnDir: str, keepAln: bool, sensitivity: float, cutoff: float, pPath: str) -> None:
    """Perform single essential allignments."""
    while True:
        current_input = jobs_queue.get(True, 1)
        if current_input is None:
            break
        # extract job information
        pairTpl: Tuple[str, str] = ("", "")
        cntA: int = 0
        cntB: int = 0
        pairTpl, cntA, cntB = current_input
        tmpA: str = pairTpl[0]
        tmpB: str = pairTpl[1]
        reductionDict: Dict[int, List[str]] = {}

        # output directory for the single run
        pair: str = "{:s}-{:s}".format(tmpA, tmpB)
        pairAlnDir: str = os.path.join(alnDir, pair)
        systools.makedir(pairAlnDir)
        tmpDir: str = os.path.join(runDir, "mapped_input")
        tmpPathBA: str = os.path.join(alnDir, "{:s}-{:s}".format(tmpB, tmpA))
        # if the reference alignment does not exist yet
        if not os.path.isfile(tmpPathBA):
            sys.stderr.write("\nERROR: the reference alignment for pair {:s} does not exist.".format(os.path.basename(tmpPathBA)))
            sys.stderr.write("\nYou create the alignment for {:s} before aligning the pair {:s}.".format(os.path.basename(tmpPathBA), pair))
            results_queue.put((pair, 0., 0., 0., 0., 0., 0.))
            continue
        # start timer for reduction files creation
        reductionTime: float = time.perf_counter()
        # create the subsets
        reductionDict, pctB, pctA = essentials.create_essential_stacks(tmpPathBA, alnDir, cntB, cntA, debug=False)
        del tmpPathBA
        # extract sequences for A
        fastaPath: str = os.path.join(tmpDir, tmpA)
        reducedAPath: str = os.path.join(pairAlnDir, tmpA)
        essentials.extract_essential_proteins(fastaPath, reductionDict[int(tmpA)], reducedAPath, debug=False)
        # extract sequences for B
        fastaPath = os.path.join(tmpDir, tmpB)
        reducedBPath: str = os.path.join(pairAlnDir, tmpB)
        essentials.extract_essential_proteins(fastaPath, reductionDict[int(tmpB)], reducedBPath, debug=False)
        # create mmseqs database files
        mmseqs_createdb(reducedAPath, outDir=pairAlnDir, debug=False)
        dbPathB: str = mmseqs_createdb(reducedBPath, outDir=pairAlnDir, debug=False)[-1]
        mmseqs_createindex(dbPathB, debug=False)
        # end time for reduction files creation creation
        reductionTime = round(time.perf_counter() - reductionTime, 3)
        # create temporary directory name
        tmpMMseqsDirName = 'tmp_{:s}'.format(pair)
        # perform the alignments
        parsedOutput, search_time, convert_time, parse_time, tot_time = mmseqs_1pass(reducedAPath, reducedBPath, dbDir=pairAlnDir, runDir=pairAlnDir, outDir=alnDir, tmpDirName=tmpMMseqsDirName, keepAlign=keepAln, sensitivity=sensitivity, evalue=1000, cutoff=cutoff, threads=1, pythonPath=pPath, debug=False)
        del parsedOutput, tot_time
        # add results to the queue
        results_queue.put((pair, search_time, convert_time, parse_time, pctA, pctB, reductionTime))
'''


def consume_orthology_inference_sharedict(jobs_queue, results_queue, inDir, outDir=os.getcwd(), sharedDir=None, sharedWithinDict=None, minBitscore=40, confCutoff=0.05, lenDiffThr=0.5, threads=8, compressed=False):
    """Perform orthology inference in parallel."""
    while True:
        current_pair = jobs_queue.get(True, 1)
        if current_pair is None:
            break
        # create the output directory if needed
        # prepare the run
        sp1, sp2 = current_pair.split("-", 1)
        runDir = os.path.join(outDir, f"{sp1}/")
        systools.makedir(runDir)
        inSp1 = os.path.join(inDir, sp1)
        inSp2 = os.path.join(inDir, sp2)
        # check that the input files do exist
        if not os.path.isfile(inSp1):
            sys.stderr.write(f"ERROR: The input file for {sp1} was not found, please provide a valid path")
            sys.exit(-2)
        if not os.path.isfile(inSp2):
            sys.stderr.write(f"ERROR: The input file for {sp2} was not found, please provide a valid path")
            sys.exit(-2)
        # AB
        AB = f"{sp1}-{sp2}"
        shPathAB = os.path.join(sharedDir, f"{sp1}/{AB}")
        if not os.path.isfile(shPathAB):
            sys.stderr.write(f"ERROR: The alignment file for {AB} was not found, please generate the alignments first.\n")
            sys.exit(-2)
        # BA
        BA = f"{sp2}-{sp1}"
        shPathBA = os.path.join(sharedDir, f"{sp2}/{BA}")
        if not os.path.isfile(shPathBA):
            sys.stderr.write(f"ERROR: The alignment file for {BA} was not found, please generate the alignments first.\n")
            sys.exit(-2)

        # prepare paths for output tables
        outTable = os.path.join(runDir, f"table.{current_pair}")
        # infer orthologs
        # use perf_counter (includes time spent during sleep)
        orthology_prediction_start = time.perf_counter()
        # Perfom the prediction
        inpyranoid.infer_orthologs_shared_dict(inSp1, inSp2, alignDir=sharedDir, outDir=runDir, sharedWithinDict=sharedWithinDict, minBitscore=minBitscore, confCutoff=confCutoff, lenDiffThr=lenDiffThr, compressed=compressed, debug=False)

        #check that all the files have been created
        if not os.path.isfile(outTable):
            sys.stderr.write(f"WARNING: the ortholog table file {outTable} was not generated.")
            outTable = None
        #everything went ok!
        end_time = time.perf_counter()
        orthology_prediction_tot = round(end_time - orthology_prediction_start, 2)
        # add the execution time to the results queue
        results_queue.put((current_pair, str(orthology_prediction_tot)))

        # Debug should only be set manually
        debug:bool = False
        if debug:
            sys.stdout.write(f"\nOrthology prediction {current_pair} (seconds):\t{orthology_prediction_tot}\n")
        # sys.exit("DEBUG :: workers :: consume_orthology_inference_sharedict :: final part")



# DEBUG-FUNCTION: this should be removed in future releases
'''
def consume_orthology_inference(jobs_queue, results_queue, inDir, outDir=os.getcwd(), sharedDir=None, cutoff=40, confCutoff=0.05, lenDiffThr=0.5, threads=8, debug=False):
    """Perform orthology inference in parallel."""
    while True:
        current_pair = jobs_queue.get(True, 1)
        if current_pair is None:
            break
        # create the output directory iof needed
        # prepare the run
        sp1, sp2 = current_pair.split('-', 1)
        runDir = os.path.join(outDir, current_pair)
        systools.makedir(runDir)
        inSp1 = os.path.join(inDir, sp1)
        inSp2 = os.path.join(inDir, sp2)
        # check that the input files do exist
        if not os.path.isfile(inSp1):
            sys.stderr.write("ERROR: The input file for {:s} was not found, please provide a valid path.\n".format(sp1))
            sys.exit(-2)
        if not os.path.isfile(inSp2):
            sys.stderr.write("ERROR: The input file for {:s} was not found, please provide a valid path.\n".format(sp2))
            sys.exit(-2)
        # prepare the names of the required alignments
        # copy AA
        AA = '{:s}-{:s}'.format(sp1, sp1)
        shPathAA = os.path.join(sharedDir, AA)
        if not os.path.isfile(shPathAA):
            sys.stderr.write("ERROR: The alignment file for {:s} was not found, please generate the alignments first.\n".format(AA))
            sys.exit(-2)
        # copy BB
        BB = '{:s}-{:s}'.format(sp2, sp2)
        shPathBB = os.path.join(sharedDir, BB)
        if not os.path.isfile(shPathBB):
            sys.stderr.write("ERROR: The alignment file for {:s} was not found, please generate the alignments first.\n".format(BB))
            sys.exit(-2)
        # copy AB
        AB = '{:s}-{:s}'.format(sp1, sp2)
        shPathAB = os.path.join(sharedDir, AB)
        if not os.path.isfile(shPathAB):
            sys.stderr.write("ERROR: The alignment file for {:s} was not found, please generate the alignments first.\n".format(AB))
            sys.exit(-2)
        # copy BA
        BA = '{:s}-{:s}'.format(sp2, sp1)
        shPathBA = os.path.join(sharedDir, BA)
        if not os.path.isfile(shPathBA):
            sys.stderr.write("ERROR: The alignment file for {:s} was not found, please generate the alignments first.\n".format(BA))
            sys.exit(-2)
        #sys.exit('DEBUG :: workers :: consume_orthology_inference_jobs :: after files copy')

        # prepare paths for output tables
        outTable = os.path.join(runDir, 'table.{:s}'.format(current_pair))

        # infer orthologs
        # use perf_counter (includes time spent during sleep)
        orthology_prediction_start = time.perf_counter()
        inpyranoid.infer_orthologs(inSp1, inSp2, alignDir=sharedDir, outDir=runDir, confCutoff=confCutoff, lenDiffThr=lenDiffThr, debug=False)
        #check that all the files have been created
        if not os.path.isfile(outTable):
            sys.stderr.write('WARNING: the ortholog table file %s was not generated.'%outTable)
            outTable = None
        #everything went ok!
        # use perf_counter (includes time spent during sleep)
        end_time = time.perf_counter()
        orthology_prediction_tot = round(end_time - orthology_prediction_start, 2)
        # add the execution time to the results queue
        results_queue.put((current_pair, str(orthology_prediction_tot)))
        if debug:
            sys.stdout.write('\nOrthology prediction {:s} (seconds):\t{:s}\n'.format(current_pair, str(orthology_prediction_tot)))
'''


def get_blastp_path() -> str:
    """Return the path in which Blast binaries are stored."""
    import platform
    # Check if a CONDA or Mamba environment is being used
    condaRun: bool = systools.is_mamba_env()[0]
    # If not a Mamba env, check if it a Conda env
    if not condaRun:
        condaRun = systools.is_conda_env()[0]
    myOS: str = platform.system()
    blastPath: str = ""
    if condaRun:
        if not (shutil.which("blastp") == None):
            return str(shutil.which("blastp"))
    else:
        pySrcDir = os.path.dirname(os.path.abspath(__file__))
        if myOS == "Linux":
            blastPath = os.path.join(pySrcDir, "bin/blastp")
        elif myOS == "Darwin":
            # Make sur ethe program is installed system-wide
            if not (shutil.which("blastp") == None):
                sys.stderr.write(f"\nERROR: SonicParanoid should be installed using CONDA on MacOS.")
                sys.exit(-10)

    if not os.path.isfile(blastPath):
        sys.stderr.write("\nERROR: blastp was not found, please check the installation guide at\niwasakilab.k.u-tokyo.ac.jp/sonicparanoid")
        sys.exit(-5)
    # return the path
    return blastPath



def get_dmnd_path() -> str:
    """Return the path in which Diamond binaries are stored."""
    from platform import system
    # Check if a CONDA or Mamba environment is being used
    condaRun: bool = systools.is_mamba_env()[0]
    # If not a Mamba env, check if it a Conda env
    if not condaRun:
        condaRun = systools.is_conda_env()[0]
    myOS: str = system()
    dmndPath: str = ""
    if condaRun:
        if not (shutil.which("diamond") == None):
            return str(shutil.which("diamond"))
    else:
        pySrcDir = os.path.dirname(os.path.abspath(__file__))
        if myOS == "Linux":
            dmndPath = os.path.join(pySrcDir, "bin/diamond")
        elif myOS == "Darwin":
            # Make sur ethe program is installed system-wide
            if not (shutil.which("diamond") == None):
                sys.stderr.write(f"\nERROR: SonicParanoid should be installed using CONDA on MacOS.")
                sys.exit(-10)

    if not os.path.isfile(dmndPath):
        sys.stderr.write("\nERROR: Diamond was not found, please check the installation guide at\niwasakilab.k.u-tokyo.ac.jp/sonicparanoid")
        sys.exit(-5)
    # return the path
    return dmndPath



def get_makeblastdb_path() -> str:
    """Return the path in which Blast binaries are stored."""
    import platform
    # Check if a CONDA or Mamba environment is being used
    condaRun: bool = systools.is_mamba_env()[0]
    # If not a Mamba env, check if it a Conda env
    if not condaRun:
        condaRun = systools.is_conda_env()[0]
    myOS: str = platform.system()
    makeblastdbPath: str = ""
    if condaRun:
        if not (shutil.which("makeblastdb") == None):
            return str(shutil.which("makeblastdb"))
    else:
        pySrcDir = os.path.dirname(os.path.abspath(__file__))
        if myOS == "Linux":
            makeblastdbPath = os.path.join(pySrcDir, "bin/makeblastdb")
        elif myOS == "Darwin":
            # Make sur ethe program is installed system-wide
            if not (shutil.which("makeblastdb") == None):
                sys.stderr.write(f"\nERROR: SonicParanoid should be installed using CONDA on MacOS.")
                sys.exit(-10)

    if not os.path.isfile(makeblastdbPath):
        sys.stderr.write("\nERROR: makeblastdb was not found, please check the installation guide at\niwasakilab.k.u-tokyo.ac.jp/sonicparanoid")
        sys.exit(-5)
    # return the path
    return makeblastdbPath



def get_mmseqs_path() -> str:
    """Return the path in which MMseqs2 binaries are stored."""
    from platform import system
    # Check if a CONDA or Mamba environment is being used
    condaRun: bool = systools.is_mamba_env()[0]
    # If not a Mamba env, check if it a Conda env
    if not condaRun:
        condaRun = systools.is_conda_env()[0]
    myOS: str = system()
    mmseqsPath: str = ""
    if condaRun:
        if not (shutil.which("mmseqs") == None):
            return str(shutil.which("mmseqs"))
    else:
        pySrcDir = os.path.dirname(os.path.abspath(__file__))
        if myOS == "Linux":
            mmseqsPath = os.path.join(pySrcDir, "bin/mmseqs")
        elif myOS == "Darwin":
            # Make sur ethe program is installed system-wide
            if not (shutil.which("mmseqs") == None):
                sys.stderr.write(f"\nERROR: SonicParanoid should be installed using CONDA on MacOS.")
                sys.exit(-10)

    if not os.path.isfile(mmseqsPath):
        sys.stderr.write("\nERROR: MMseqs2 was not found, please check the installation guide at\niwasakilab.k.u-tokyo.ac.jp/sonicparanoid")
        sys.exit(-5)
    # return the path
    return mmseqsPath



def blast_createdb(inSeq: str, outDir: str = os.getcwd(), debug: bool = False):
    """Create a database file for Blast from the input sequence file."""
    if debug:
        print("blast_createdb :: START")
        print(f"Input FASTA file:\t{inSeq}")
        print(f"Outdir:\t{outDir}")
    #check that the input file and the database exist
    if not os.path.isfile(inSeq):
        sys.stderr.write(f"The file {inSeq} was not found, please provide the path to a valid FASTA file.")
        sys.exit(-2)
    # create dir if not already exists
    systools.makedir(outDir)
    # check the set db name
    dbName: str = os.path.basename(inSeq)
    dbPath: str = os.path.join(outDir, dbName)
    # command to be executed
    # EXAMPLE: makeblastdb -input_type fasta -dbtype prot -parse_seqids  -in <myproteome> -out <dbs_blast/myproteome>
    # -parse_seqids is needed in order for the Database files to be usable with Diamond
    # makeDbCmd: str = f"{get_makeblastdb_path()} -input_type fasta -dbtype prot -parse_seqids  -in {inSeq} -out {dbPath}"
    # HACK: removed -parse_seqid
    makeDbCmd: str = f"{get_makeblastdb_path()} -input_type fasta -dbtype prot  -in {inSeq} -out {dbPath}"
    if debug:
        print(f"Makeblastdb CMD:\n{makeDbCmd}")
    #execute the system call
    process = subprocess.Popen(makeDbCmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout_val, stderr_val = process.communicate() #get stdout and stderr
    process.wait()
    if debug:
        print(f"STDOUT:\n{stdout_val.decode()}\n")
        print(f"STDERR:\n{stderr_val.decode()}\n")

    #return a tuple with the results
    return(stdout_val, stderr_val, makeDbCmd, dbPath)



def blast_search(inSeq, dbSeq, dbDir: str, outDir: str, blastThr: int = 11, threads: int = 4, debug: bool = False) -> Tuple[str, float, float]:
    """Align protein sequences using blastp."""
    if debug:
        print("\nblast_search :: START")
        print(f"Input query FASTA file: {inSeq}")
        print(f"Input target FASTA file: {dbSeq}")
        print(f"BLAST database directory: {dbDir}")
        print(f"Output directory: {outDir}")
        print(f"Blastp (-threshold):\t{blastThr}")
        print(f"Threads:\t{threads}")

    #check that the input file and the database exist
    if not os.path.isfile(inSeq):
        sys.stderr.write(f"ERROR: The query FASTA file {inSeq}\nwas not found, please provide the path to a valid FASTA file")
        sys.exit(-2)
    if not os.path.isfile(dbSeq):
        sys.stderr.write(f"ERROR: The target file {dbSeq}\nwas not found, please provide the path to a valid FASTA file")
        sys.exit(-2)

    # create directory if not previously created
    systools.makedir(outDir)
    systools.makedir(dbDir)
    # check the target DB name
    targetDBpath: str = os.path.join(dbDir, f"{os.path.basename(dbSeq)}")

    # create the database if does not exist yet
    if not os.path.isfile(f"{targetDBpath}.psq"):
        sys.stderr.write(f"\nERROR [blast_search()]: the BLAST DB\n{targetDBpath}\nis missing.\nGenerate the DB before searching.")
        sys.exit(-2)

    # set output name
    pairName: str = f"{os.path.basename(inSeq)}-{os.path.basename(dbSeq)}"
    blastOutName: str = f"blastp.{pairName}"
    blastOutPath: str = os.path.join(outDir, blastOutName)
    # start measuring the execution time
    start_time = time.perf_counter()
    # Example of Diamond command
    # blastp -query <inSeq> -db <dbSeq> -out inSeq-vs-dbSeq.tsv -outfmt "6 qseqid sseqid qstart qend sstart send bitscore"
    # command to be executed
    searchCmd: str = f"{get_blastp_path()} -threshold {blastThr} -num_threads {threads} -query {inSeq} -db {targetDBpath} -out {blastOutPath} -outfmt \"6 qseqid sseqid qstart qend sstart send bitscore\" -seg yes"
    if debug:
        print(f"BLAST blastp CMD:\t{searchCmd}")
    # use run (or call)
    subprocess.run(searchCmd, shell=True)
    # output an error if the Alignment did not finish correctly
    if not os.path.isfile(blastOutPath):
        sys.stderr.write(f"\nERROR [blast_search()]: the BLAST alignment file\n{blastOutPath}\nwas not generated.\n")
        sys.exit(-2)
    # stop counter
    search_time: float = round(time.perf_counter() - start_time, 2)

    return (blastOutPath, search_time, 0.)



def blast_1pass(inSeq: str, dbSeq: str, dbDir: str, runDir: str, outDir: str, keepAlign: bool = False, minBitscore: int = 40, blastThr: int = 11, compress: bool = False, complev: int = 5, threads: int = 4, debug: bool = False):
    """Perform BLAST alignment and parse the results."""
    if debug:
        print("\nblast_1pass :: START")
        print(f"Input query FASTA file:\t{inSeq}")
        print(f"Input target FASTA file:\t{dbSeq}")
        print(f"BLAST database directory:\t{dbDir}")
        print(f"Directory with run supplementary files: {runDir}")
        print(f"Output directory:\t{outDir}")
        print(f"Do not remove alignment files:\t{keepAlign}")
        print(f"minimum bitscore:\t{minBitscore}")
        print(f"Blastp (-threshold):\t{blastThr}")
        print(f"Compress output:\t{compress}")
        print(f"Compression level:\t{complev}")
        print(f"Threads:\t{threads}")

    # create the directory in which the alignment will be performed
    pair: str = f"{os.path.basename(inSeq)}-{os.path.basename(dbSeq)}"
    pairAlnDir: str = os.path.join(outDir, pair)
    systools.makedir(pairAlnDir)

    # create Diamond alignment in tab-separated format
    blastLikeOutput, search_time, convert_time = blast_search(inSeq, dbSeq, dbDir=dbDir, outDir=pairAlnDir, blastThr=blastThr, threads=threads, debug=debug)

    # start timing the parsing
    # use perf_counter (includes time spent during sleep)
    start_time: float = time.perf_counter()
    # prepare now the parsing
    # EXAMPLE: python3 mmseqs_parser_cython.py --input mmseqs2blast.A-B --query A --db B --output A-B --cutoff 40
    parsedOutput: str = blastLikeOutput.rsplit(".", 1)[-1]
    parsedOutput = os.path.join(pairAlnDir, parsedOutput)
    # parse Blast-like output
    parse_blast_output(blastLikeOutput, inSeq, dbSeq, parsedOutput, runDir, minBitscore, compress, complev, dmndMode=True, debug=debug)
    # use perf_time (includes time spent during sleep)
    parse_time = round(time.perf_counter() - start_time, 2)
    tot_time = round(search_time + convert_time + parse_time, 2)
    if debug:
        sys.stdout.write(f"\nBLAST alignment and parsing elapsed time (seconds):\t{tot_time}\n")
    # Temporary final name
    tmpFinalPath: str = os.path.join(outDir, f"_{pair}")
    systools.copy(parsedOutput, tmpFinalPath)
    # remove the aligment directory if required
    if keepAlign:
        systools.move(blastLikeOutput, outDir)
    # remove directory content
    shutil.rmtree(pairAlnDir)
    parsedOutput = os.path.join(outDir, pair)
    os.rename(tmpFinalPath, parsedOutput)
    return (parsedOutput, search_time, convert_time, parse_time, tot_time)



def dmnd_createdb(inSeq: str, outDir: str = os.getcwd(), threads: int = 1, debug: bool = False):
    """Create a database file for Diamond from the input sequence file."""
    if debug:
        print("dmnd_createdb :: START")
        print(f"Input FASTA file:\t{inSeq}")
        print(f"Outdir:\t{outDir}")
        print(f"Threads:\t{threads}")
    #check that the input file and the database exist
    if not os.path.isfile(inSeq):
        sys.stderr.write(f"The file {inSeq} was not found, please provide the path to a valid FASTA file.")
        sys.exit(-2)
    #check if the database exists
    if outDir[-1] != "/":
        outDir += "/"
    # create dir if not already exists
    systools.makedir(outDir)
    # check the set db name
    dbName: str = os.path.basename(inSeq)
    dbName = f"{dbName}.dmnd"
    dbPath: str = os.path.join(outDir, dbName)
    # command to be executed
    # EXAMPLE: diamond makedb --in fasta --db /outdir/mydb -p 2 --quiet
    makeDbCmd = f"{get_dmnd_path()} makedb --in {inSeq} --db {dbPath} -p {threads} --quiet"
    if debug:
        print(f"Diamond createdb CMD:\n{makeDbCmd}")
    #execute the system call
    process = subprocess.Popen(makeDbCmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout_val, stderr_val = process.communicate() #get stdout and stderr
    process.wait()
    if debug:
        print(f"STDOUT:\n{stdout_val.decode()}\n")
        print(f"STDERR:\n{stderr_val.decode()}\n")
    #return a tuple with the results
    return(stdout_val, stderr_val, makeDbCmd, dbPath)



def dmnd_createindex(dbPath: str, sensitivity: str = "", threads: int = 1, debug: bool = False):
    """Create a index from a Diamond database file."""
    if debug:
        print("dmnd_createindex :: START")
        print(f"Input Diamond DB file:\t{dbPath}")
        print(f"Diamond sensitivity:\t{sensitivity}")
        print(f"Threads:\t{threads}")

    #check that the database file exist
    if not os.path.isfile(dbPath):
        sys.stderr.write(f"The file {dbPath} was not found, please provide the path to a Diamond database file")
        sys.exit(-2)

    # Make sure that the sensitivty setting is valid
    validSens: List[str] = ["", "mid-sensitive", "sensitive", "more-sensitive", "very-sensitive", "ultra-sensitive"]
    # check sensitivity
    if not sensitivity in validSens:
        sys.stderr.write(f"\nERROR: the sensitivity value for Diamond ({sensitivity}) is not valid.\nValid sensitivity values: {validSens}")
        sys.exit(-5)
    # Add dashes to the sensitivity string
    if len(sensitivity) != 0:
        sensitivity = f"--{sensitivity}"

    # Prepare file names and commands
    tmpBname: str = os.path.basename(dbPath)
    outDir: str = os.path.dirname(dbPath)
    # DB index files must bear the 'seed_idx' suffix
    dbIdxPath: str = os.path.join(outDir, f"{tmpBname}.seed_idx")
    # command to be executed
    # EXAMPLE: diamond makeidx  --db dbs/mydb.dmnd --out dbs/mydb -p 1 --quite --ultra-sensitive
    makeIdxCmd = f"{get_dmnd_path()} makeidx --db {dbPath} --out {dbPath} -p {threads} {sensitivity} --quiet"
    if debug:
        print(f"Diamond create index CMD:\n{makeIdxCmd}")
    #execute the system call
    process = subprocess.Popen(makeIdxCmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout_val, stderr_val = process.communicate() #get stdout and stderr
    process.wait()
    if debug:
        print(f"STDOUT:\n{stdout_val.decode()}\n")
        print(f"STDERR:\n{stderr_val.decode()}\n")
    # make sure that the index file was been properly created
    if not os.path.isfile(dbIdxPath):
        sys.stderr.write(f"The Diamond DB index file {dbIdxPath} could not be created.")
        sys.exit(-2)
    # return a output tuple
    return(stdout_val, stderr_val, makeIdxCmd)



def dmnd_search(inSeq, dbSeq, dbDir: str, outDir: str, sensitivity: str = "sensitive", indexDB: bool = False, useBlastDb: bool = False, cbstats: int = 1, threads: int = 4, debug: bool = False) -> Tuple[str, float, float]:
    """Align protein sequences using Diamond."""
    if debug:
        print("\ndmnd_search :: START")
        print(f"Input query FASTA file: {inSeq}")
        print(f"Input target FASTA file: {dbSeq}")
        print(f"Diamond database directory: {dbDir}")
        print(f"Output directory: {outDir}")
        print(f"Diamond sensitivity:\t{sensitivity}")
        print(f"Index DB:\t{indexDB}")
        print(f"Use a DB file created using BLAST:\t{useBlastDb}")
        print(f"Compositional based stats:\t{cbstats}")
        print(f"Threads:\t{threads}")

    # Compositional based stats must be an interger between 0 and 4
    # For more details visit https://github.com/bbuchfink/diamond/wiki
    # 0 -> off
    # 1 -> Hauser, 2016 (default in Diamond)
    # 2 -> Yu, 2005 (used in BLAST) and Hauser, 2016 based on sequence properties. This is 2X faster than 3
    # 3 -> Yu, 2005 (used in BLAST) and Hauser, 2016 based on sequence properties
    # 4 -> Compositional matrix adjust as described in (Yu, 2005), unconditionally. An adjusted matrix is computed for all alignments, which substantially reduces performance, but provides the highest accuracy. Supported since Diamond v2.0.6.

    if not (0 <= cbstats <= 4):
        sys.stderr.write(f"\nERROR: the compositional based stats parameter ({cbstats}) for Diamond must be a integer between 0 and 4.")
        sys.exit()

    #check that the input file and the database exist
    if not os.path.isfile(inSeq):
        sys.stderr.write(f"ERROR: The query FASTA file {inSeq}\nwas not found, please provide the path to a valid FASTA file")
        sys.exit(-2)
    if not os.path.isfile(dbSeq):
        sys.stderr.write(f"ERROR: The target file {dbSeq}\nwas not found, please provide the path to a valid FASTA file")
        sys.exit(-2)

    # Following are the possible sensititivities for Diamond
    validSens: List[str] = ["fast", "mid-sensitive", "sensitive", "more-sensitive", "very-sensitive", "ultra-sensitive"]
    # check sensitivity
    if not sensitivity in validSens:
        sys.stderr.write(f"\nERROR: the sensitivity value for Diamond ({sensitivity}) is not valid.\nValid sensitivity values: {validSens}")
        sys.exit(-5)
    # Add dashes to the sensitivity string
    if len(sensitivity) != 0:
        sensitivity = f"--{sensitivity}"

    # create directory if not previously created
    systools.makedir(outDir)
    systools.makedir(dbDir)
    # Set the target DB name
    targetDBpath: str = os.path.join(dbDir, f"{os.path.basename(dbSeq)}.dmnd")
    idxSettings: str = ""

    # create the database if does not exist yet
    if useBlastDb:
        targetDBpath = os.path.join(dbDir, f"{os.path.basename(dbSeq)}.acc")
        if not os.path.isfile(targetDBpath):
            sys.stderr.write(f"\nERROR [diamond_search()]: the BLAST to Diamond DB indexing file \n{targetDBpath}\nis missing.\nUse 'diamond prepdb {dbSeq}' one BLAST-generated DB before searching.")
            sys.exit(-2)
        # Set the final path to be used for Diamond
        targetDBpath = os.path.join(dbDir, f"{os.path.basename(dbSeq)}")
    else:
        if not os.path.isfile(targetDBpath):
            sys.stderr.write(f"\nERROR [diamond_search()]: the Diamond DB\n{targetDBpath}\nis missing.\nGenerate the DB before searching.")
            sys.exit(-2)
    # Create the index if required
    if indexDB:
        idxSettings = "--target-indexed -c1"
        targetDbIdxPath: str = f"{targetDBpath}.seed_idx"
        if not os.path.isfile(targetDbIdxPath):
            sys.stderr.write(f"\nERROR [diamond_search()]: the Diamond DB index\n{targetDbIdxPath}\nis missing.\nGenerate the DB index before searching.")
            sys.exit(-2)

    # set output name
    spA: str = os.path.basename(inSeq)
    spB: str = os.path.basename(dbSeq)
    # This is used to set multiple HSP hits only of for inter-proteome alignments
    # isIntraProtAln: bool = False
    # if spA == spB:
    #     isIntraProtAln = True
    pairName: str = f"{spA}-{spB}"
    blastOutName: str = f"dmnd_blast.{pairName}"
    blastOutPath: str = os.path.join(outDir, blastOutName)
    # start measuring the execution time
    start_time = time.perf_counter()
    # Example of Diamond command
    # diamond blastp --query input/mtuberculosis.fa --db dbs/ssclerotiorum.dmnd --target-indexed -c1 --out output/mtuberculosis-ssclerotiorum.tsv -p 1 --ultra-sensitive -f 6 qseqid sseqid qstart qend sstart send bitscore
    # command to be executed

    # Maximum number of HSPS per each single target sequence
    # maxHspsPerTarget: int = 20 # Default in Diamond is 1
    # HACK: restore if not working
    searchCmd: str = f"{get_dmnd_path()} blastp --query {inSeq} --db {targetDBpath} {idxSettings} --out {blastOutPath} -p {threads:d} {sensitivity} --comp-based-stats {cbstats} --quiet -f 6 qseqid sseqid qstart qend sstart send bitscore --algo 1 --freq-masking"
    # Add Multi-HSPs parameter if required
    # if isIntraProtAln:
        # Use frequency based masking
        # instead of complexity based masking (default from Diamond 2.0.12)
        # Complexity masking is considerably slow with QfO Benchmark dataset
        # Especially with complex proteomes like Tvaginalis
        # searchCmd = f"{searchCmd} --freq-masking"
    if debug:
        print(f"Diamond blastp CMD:\t{searchCmd}")
    # use run (or call)
    subprocess.run(searchCmd, shell=True)
    # output an error if the Alignment did not finish correctly
    if not os.path.isfile(blastOutPath):
        sys.stderr.write(f"\nERROR [diamond_search()]: the Diamond alignment file\n{blastOutPath}\nwas not generated.\n")
        sys.exit(-2)
    # stop counter
    search_time: float = round(time.perf_counter() - start_time, 2)

    return (blastOutPath, search_time, 0.)



def dmnd_1pass(inSeq: str, dbSeq: str, dbDir: str, runDir: str, outDir: str, keepAlign: bool = False, sensitivity: str = "very-sensitive", minBitscore: int = 40, indexDB: bool = False, compress: bool = False, complev: int = 5, useBlastDb: bool = False, cbstats: int = 1, threads: int = 4, debug: bool = False):
    """Perform Diamond alignment and parse the results."""
    if debug:
        print("\ndmnd_1pass :: START")
        print(f"Input query FASTA file:\t{inSeq}")
        print(f"Input target FASTA file:\t{dbSeq}")
        print(f"Diamond database directory:\t{dbDir}")
        print(f"Directory with run supplementary files: {runDir}")
        print(f"Output directory:\t{outDir}")
        print(f"Do not remove alignment files:\t{keepAlign}")
        print(f"Diamond sensitivity:\t{sensitivity}")
        print(f"Minimum bitscore:\t{minBitscore}")
        print(f"Index database files:\t{indexDB}")
        print(f"Compress output:\t{compress}")
        print(f"Compression level:\t{complev}")
        print(f"Use a DB file created using BLAST:\t{useBlastDb}")
        print(f"Compositional based stats:\t{cbstats}")
        print(f"Threads:\t{threads}")

    # create the directory in which the alignment will be performed
    pair: str = f"{os.path.basename(inSeq)}-{os.path.basename(dbSeq)}"
    pairAlnDir: str = os.path.join(outDir, pair)
    systools.makedir(pairAlnDir)

    # create Diamond alignment in tab-separated format
    blastLikeOutput, search_time, convert_time = dmnd_search(inSeq, dbSeq, dbDir=dbDir, outDir=pairAlnDir, sensitivity=sensitivity, indexDB=indexDB, useBlastDb=useBlastDb, cbstats=cbstats, threads=threads, debug=debug)

    # start timing the parsing
    # use perf_counter (includes time spent during sleep)
    start_time: float = time.perf_counter()
    # prepare now the parsing
    # EXAMPLE: python3 mmseqs_parser_cython.py --input mmseqs2blast.A-B --query A --db B --output A-B --cutoff 40
    parsedOutput: str = blastLikeOutput.rsplit(".", 1)[-1]
    parsedOutput = os.path.join(pairAlnDir, parsedOutput)
    # parse Blast-like output
    parse_blast_output(inBlastOut=blastLikeOutput, query=inSeq, target=dbSeq, outPath=parsedOutput, runDir=runDir, minBitscore=minBitscore, compress=compress, complev=complev, dmndMode=True, debug=False)
    # use perf_time (includes time spent during sleep)
    parse_time = round(time.perf_counter() - start_time, 2)
    tot_time = round(search_time + convert_time + parse_time, 2)
    if debug:
        sys.stdout.write(f"\nDiamond alignment and parsing elapsed time (seconds):\t{tot_time}\n")
    # Temporary final name
    tmpFinalPath: str = os.path.join(outDir, f"_{pair}")
    systools.copy(parsedOutput, tmpFinalPath)
    # remove the aligment directory if required
    if keepAlign:
        systools.move(blastLikeOutput, outDir)
    # remove directory content
    shutil.rmtree(pairAlnDir)
    parsedOutput = os.path.join(outDir, pair)
    os.rename(tmpFinalPath, parsedOutput)
    return (parsedOutput, search_time, convert_time, parse_time, tot_time)



def mmseqs_1pass(inSeq, dbSeq, dbDir=os.getcwd(), runDir=os.getcwd(), outDir=os.getcwd(), tmpDirName=None, keepAlign=False, sensitivity=4.0, evalue=1000, minBitscore=40, pmtx="blosum62", compress:bool=False, complev:int=5, threads:int=4, debug=False):
    """Perform MMseqs2 alignment and parse the results."""
    if debug:
        print("\nmmseqs_1pass :: START")
        print(f"Input query FASTA file:\t{inSeq}")
        print(f"Input target FASTA file:\t{dbSeq}")
        print(f"mmseqs2 database directory:\t{dbDir}")
        print(f"Directory with run supplementary files: {runDir}")
        print(f"Output directory:\t{outDir}")
        print(f"MMseqs2 tmp directory:\t{tmpDirName}")
        print(f"Do not remove alignment files:\t{keepAlign}")
        print(f"MMseqs2 sensitivity (-s):\t{sensitivity}")
        print(f"Minimum bitscore:\t{minBitscore}")
        print(f"MMseqs2 prefilter substitution matrix:\t{pmtx}")
        print(f"Compress output:\t{compress}")
        print(f"Compression level:\t{complev}")
        print(f"Threads:\t{threads}")

    # create the directory in which the alignment will be performed
    pair: str = f"{os.path.basename(inSeq)}-{os.path.basename(dbSeq)}"
    pairAlnDir: str = os.path.join(outDir, pair)
    systools.makedir(pairAlnDir)

    #start the timing which will also include the time for the index, database creation (if required) and parsing
    # create mmseqs alignment conveted into blastp tab-separated format
    blastLikeOutput, search_time, convert_time = mmseqs_search(inSeq, dbSeq, dbDir=dbDir, outDir=pairAlnDir, tmpDirName=tmpDirName, sensitivity=sensitivity, pmtx=pmtx, evalue=1000, threads=threads, cleanUp=False, debug=debug)

    # start timing the parsing
    # use perf_counter (includes time spent during sleep)
    start_time = time.perf_counter()
    # prepare now the parsing
    # EXAMPLE: python3 mmseqs_parser_cython.py --input mmseqs2blast.A-B --query A --db B --output A-B --cutoff 40
    parsedOutput: str = blastLikeOutput.rsplit(".", 1)[-1]
    parsedOutput = os.path.join(pairAlnDir, parsedOutput)
    # parse Blast-like output
    parse_blast_output(blastLikeOutput, inSeq, dbSeq, parsedOutput, runDir, minBitscore, compress, complev, dmndMode=False, debug=debug)

    # use perf_time (includes time spent during sleep)
    parse_time = round(time.perf_counter() - start_time, 2)
    tot_time = round(search_time + convert_time + parse_time, 2)
    if debug:
        sys.stdout.write(f"\nMMseqs2 alignment and parsing elapsed time (seconds):\t{tot_time}\n")
    # Temporary final name
    tmpFinalPath: str = os.path.join(outDir, f"_{pair}")
    systools.copy(parsedOutput, tmpFinalPath)
    # remove the aligment directory if required
    if keepAlign:
        for r, d, files in os.walk(pairAlnDir):
            for name in files:
                tPath = os.path.join(r, name)
                if os.path.isfile(tPath) and name[0] == "m":
                    systools.move(tPath, outDir)
            break
    # remove directory content
    shutil.rmtree(pairAlnDir)
    parsedOutput = os.path.join(outDir, pair)
    os.rename(tmpFinalPath, parsedOutput)
    # reset original working directory
    # os.chdir(prevDir) # TO REMOVE
    return (parsedOutput, search_time, convert_time, parse_time, tot_time)



def mmseqs_createdb(inSeq:str, outDir:str=os.getcwd(), dbType:int=1, debug:bool=False):
    """Create a database file for mmseqs2 from the input sequence file."""
    if debug:
        print(f"mmseqs_createdb :: START")
        print(f"Input FASTA file:\t{inSeq}")
        print(f"Database type:\t{dbType:d}")
        print(f"Outdir:\t{outDir}")
    #check that the input file and the database exist
    if not os.path.isfile(inSeq):
        sys.stderr.write(f"The file {inSeq} was not found, please provide the path to a valid FASTA file.")
        sys.exit(-2)
    #check if the database exists
    # create dir if not already exists
    systools.makedir(outDir)
    # check and set DB name
    dbName: str = f"{os.path.basename(inSeq)}.mmseqs2db"
    dbPath: str = os.path.join(outDir, dbName)
    # command to be executed
    # EXAMPLE; mmseqs createdb in.fasta /outdir/mydb
    makeDbCmd: str = f"{get_mmseqs_path()} createdb {inSeq} {dbPath} --dbtype {dbType} --write-lookup 0 -v 0"
    logger.debug(f"mmseqs2 createdb CMD:\n{makeDbCmd}")
    #execute the system call
    process: subprocess.Popen = subprocess.Popen(makeDbCmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout_val: bytes = bytes()
    stderr_val: bytes = bytes()
    stdout_val, stderr_val = process.communicate() #get stdout and stderr
    process.wait()
    if debug:
        print(f"STDOUT:\n{stdout_val.decode()}\n")
        print(f"STDERR:\n{stderr_val.decode()}\n")
    #return a tuple with the results
    return(stdout_val, stderr_val, makeDbCmd, dbPath)



def mmseqs_createindex(dbPath:str, threads:int=2, debug:bool=False):
    """Create a index from a mmseq2 database file."""
    if debug:
        print("mmseqs_createindex :: START")
        print(f"Input mmseqs2 db file:\t{dbPath}")
        print(f"Threads:\t{threads}")
    #check that the database file exist
    if not os.path.isfile(dbPath):
        sys.stderr.write(f"The file {dbPath} was not found, please provide the path to a mmseqs2 database file")
        sys.exit(-2)
    # Prepare file names and commands
    tmpBname = os.path.basename(dbPath)
    tmpDir = "{:s}/tmp_{:s}/".format(os.path.dirname(dbPath), os.path.basename(tmpBname.split(".", 1)[0]))
    systools.makedir(tmpDir)
    # command to be executed
    # EXAMPLE; mmseqs createindex in.mmseqs2_db
    makeIdxCmd = f"{get_mmseqs_path()} createindex {dbPath} {tmpDir} --threads {threads} --search-type 1 -v 0"
    if debug:
        print(f"mmseqs2 createindex CMD:\n{makeIdxCmd}")
    #execute the system call
    process = subprocess.Popen(makeIdxCmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout_val, stderr_val = process.communicate() #get stdout and stderr
    process.wait()
    if debug:
        print(f"STDOUT:\n{stdout_val.decode()}\n")
        print(f"STDERR:\n{stderr_val.decode()}\n")
    # make sure that the 3 idx files have been properly created
    idx1: str = f"{dbPath}.idx"
    if not os.path.isfile(idx1):
        sys.stderr.write(f"The MMseqs2 index file {idx1} could not be created.")
        sys.exit(-2)
    idx2: str = f"{dbPath}.idx.index"
    if not os.path.isfile(idx2):
        sys.stderr.write(f"\nWARNING: The MMseqs2 index file {idx2} could not be created.")
        sys.exit(-2)
    # remove the temporary directory
    shutil.rmtree(path=tmpDir)
    # return a output tuple
    return(stdout_val, stderr_val, makeIdxCmd, idx1, idx2)



def mmseqs_search(inSeq, dbSeq, dbDir=os.getcwd(), outDir=os.getcwd(), tmpDirName=None, sensitivity=4.0, pmtx="blosum62", evalue=1000, threads=4, cleanUp=False, debug=False):
    """Align protein sequences using MMseqs2."""
    if debug:
        print("\nmmseqs_search :: START")
        print(f"Input query FASTA file: {inSeq}")
        print(f"Input target FASTA file: {dbSeq}")
        print(f"mmseqs2 database directory: {dbDir}")
        print(f"Output directory: {outDir}")
        print(f"MMseqs2 tmp directory:\t{tmpDirName}")
        print(f"MMseqs2 sensitivity (-s):\t{sensitivity}")
        print(f"MMseqs2 prefilter substitution matrix:\t{pmtx}")
        print(f"Threads:\t{threads}")
        print(f"Remove temporary files:\t{cleanUp}")
    #check that the input file and the database exist
    if not os.path.isfile(inSeq):
        sys.stderr.write(f"ERROR: The query file {inSeq}\nwas not found, please provide the path to a valid FASTA file")
        sys.exit(-2)
    if not os.path.isfile(dbSeq):
        sys.stderr.write(f"ERROR: The target file {dbSeq}\nwas not found, please provide the path to a valid FASTA file")
        sys.exit(-2)
    # check sensitivity
    if (sensitivity < 1) or sensitivity > 7.5:
        sys.stderr.write("\nERROR: the sensitivity value for MMseqs2 must be a value between 1.0 and 7.5.\n")
        sys.exit(-5)
    # create directory if not previously created
    systools.makedir(outDir)
    systools.makedir(dbDir)
    # set the tmp dir
    tmpDir = None
    if tmpDirName is None:
        tmpDir = os.path.join(outDir, "tmp_mmseqs")
    else:
        tmpDir = os.path.join(outDir, tmpDirName)
    systools.makedir(tmpDir)
    # check the query db name
    queryDBname = os.path.basename(inSeq)
    queryDBname = queryDBname.split(".")[0] # take the left part of the file name
    queryDBname = f"{queryDBname}.mmseqs2db"
    queryDBpath = os.path.join(dbDir, queryDBname)
    # create the database if does not exist yet
    if not os.path.isfile(queryDBpath):
        mmseqs_createdb(inSeq, outDir=dbDir, debug=debug)
        mmseqs_createindex(queryDBpath, threads=threads, debug=debug)
    # check the target db name
    targetDBname = os.path.basename(dbSeq)
    targetDBname = targetDBname.split(".")[0] # take the left part of the file name
    targetDBname = f"{targetDBname}.mmseqs2db"
    targetDBpath = os.path.join(dbDir, targetDBname)
    # create the database if does not exist yet
    if not os.path.isfile(targetDBpath):
        mmseqs_createdb(dbSeq, outDir=dbDir, debug=debug)
        mmseqs_createindex(targetDBpath, threads=threads, debug=debug)
    # set output name
    pairName = f"{os.path.basename(inSeq)}-{os.path.basename(dbSeq)}"
    rawOutName = f"mmseqs2raw.{pairName}"
    rawOutPath = os.path.join(outDir, rawOutName)
    blastOutName = f"mmseqs2blast.{pairName}"
    blastOutPath = os.path.join(outDir, blastOutName)
    # start measuring the execution time
    # use perf_counter (includes time spent during sleep)
    start_time = time.perf_counter()
    # command to be executed
    minUngappedScore = 15
    mtxSettings:str = "--seed-sub-mat nucl:nucleotide.out,aa:blosum62.out"
    if pmtx != "blosum62":
        mtxSettings = "" # just use the default for MMseqs2
    # EXAMPLE: mmseqs search queryDBfile targetDBfile outputFile tmpDir -s 7.5 -e 100000 --theads threads
    # Maximum number of HSPS per each single target sequence
    maxHspsPerTarget: int = 20 # Default in Diamond is 1
    searchCmd: str = f"{get_mmseqs_path()} search {queryDBpath} {targetDBpath} {rawOutPath} {tmpDir} -s {str(sensitivity)} --threads {threads:d} -v 0 {mtxSettings} --min-ungapped-score {minUngappedScore} --alignment-mode 2 --alt-ali {maxHspsPerTarget} --search-type 1"
    # This prevents MMseqs2 to crush when running at high sensitivity
    if sensitivity > 6:
        searchCmd = f"{searchCmd} --db-load-mode 3"
    if debug:
        print(f"mmseqs2 search CMD:\t{searchCmd}")
    # use run (or call)
    subprocess.run(searchCmd, shell=True)

    # output an error if the Alignment did not finish correctly
    if threads > 1: # multiple raw files are generated
        if not os.path.isfile(f"{rawOutPath}.0"):
            sys.stderr.write(f"\nERROR [mmseqs_search()]: the MMseqs2 raw alignment file\n{rawOutPath}\nwas not generated.\n")
            sys.exit(-2)
    else: # a single raw file is created
        if not os.path.isfile(rawOutPath):
            sys.stderr.write(f"\nERROR [mmseqs_search()]: the MMseqs2 raw alignment file\n{rawOutPath}\nwas not generated.\n")
            sys.exit(-2)

    # stop counter
    # use perf_counter (includes time spent during sleep)
    end_search = time.perf_counter()
    search_time = round(end_search - start_time, 2)
    # convert the output to tab-separated BLAST output
    # EXAMPLE: mmseqs convertalis query.db target.db query_target_rawout query_target_blastout
    # Only output specific files in the BLAST-formatted output
    # query,target,qstart,qend,tstart,tend,bits
    columns: str = "query,target,qstart,qend,tstart,tend,bits"
    convertCmd = f"{get_mmseqs_path()} convertalis {queryDBpath} {targetDBpath} {rawOutPath} {blastOutPath} -v 0 --format-mode 0 --search-type 1 --format-output {columns} --threads {threads:d}"

    # perform the file conversion
    subprocess.run(convertCmd, shell=True)
    if debug:
        print(f"mmseqs2 convertalis CMD:\n{convertCmd}")
    # exec time conversion
    # use perf_counter (includes time spent during sleep)
    convert_time = round(time.perf_counter() - end_search, 2)
    # output an error if the Alignment could not be converted
    if not os.path.isfile(blastOutPath):
        sys.stderr.write(f"\nERROR: the MMseqs2 raw alignments could not be converted into the BLAST format.\n{blastOutPath}\n")
        sys.exit(-2)
    return (blastOutPath, search_time, convert_time)



def parallel_archive_processing(paths:List[Tuple[str, str]], complev:int=5, removeSrc:bool=False, threads:int=4, compress:bool=True, debug:bool=False) -> None:
    """Compress input files in parallel."""
    if debug:
        print("\nparallel_archive_processing :: START")
        if compress:
            print(f"Files to be compressed:\t{len(paths)}")
            print(f"Compression level:\t{complev}")
        else:
            print(f"Archives to be decompressed:\t{len(paths)}")
        print(f"Remove original file:\t{removeSrc}")
        print(f"Threads:\t{threads}")
        print(f"Compress:\t{compress}")

    # create the queue and start adding jobs
    jobs_queue: mp.queues.Queue = mp.Queue(maxsize=len(paths) + threads)
    # fill the queue with the file paths
    for tpl in paths:
        jobs_queue.put(tpl)

    # add flags for ended jobs
    for i in range(0, threads):
        sys.stdout.flush()
        jobs_queue.put(None)

    # execute the jobs
    if compress:
        # perform the file compression
        runningJobs = [mp.Process(target=consume_compress_jobs, args=(jobs_queue, complev, removeSrc)) for i_ in range(threads)]
    else:
        # perform the file compression
        runningJobs = [mp.Process(target=consume_unarchive_jobs, args=(jobs_queue, removeSrc)) for i_ in range(threads)]

    # execute the jobs
    for proc in runningJobs:
        proc.start()

    # calculate cpu-time for compression
    processing_start = time.perf_counter()
    # write some message...
    if compress:
        sys.stdout.write(f"\nArchiving {len(paths)} files...please be patient...")
    else:
        sys.stdout.write(f"\nExtracting {len(paths)} archived files...please be patient...")

    # this joins the processes after we got the results
    for proc in runningJobs:
        while proc.is_alive():
            proc.join()

    # stop the counter for the alignment time
    if compress:
        sys.stdout.write(f"\nCompression of {len(paths)} files compression elapsed time (seconds):\t{round(time.perf_counter() - processing_start, 3)}\n")
    else:
        sys.stdout.write(f"\nExtraction of {len(paths)} archives elapsed time (seconds):\t{round(time.perf_counter() - processing_start, 3)}\n")



def parse_blast_output(inBlastOut:str, query:str, target:str, outPath:str, runDir:str, minBitscore:int=40, compress:bool=False, complev:int=5, dmndMode: bool = False, debug: bool = False):
    """Parse BLAST-like output file and generate SonicParanoid alignment file"""
    if debug:
        print("\nparse_blast_output :: START")
        print(f"BLAST output to be parsed: {inBlastOut}")
        print(f"Query: {query}")
        print(f"Target: {target}")
        print(f"Parsed output: {outPath}")
        print(f"Directory with accessory files: {runDir}")
        print(f"Minimum bitscore:\t{minBitscore}")
        print(f"Compress output:\t{compress}")
        if compress:
            print(f"Compression level:\t{complev}")

    outName: str = os.path.basename(outPath)
    outDir: str = os.path.dirname(outPath)
    bsName: str = os.path.basename(inBlastOut)
    # use pickle files
    qSeqLenPath:str = os.path.join(runDir, f"{os.path.basename(query)}.len.pckl")
    tSeqLenPath:str = os.path.join(runDir, f"{os.path.basename(target)}.len.pckl")

    ########## sort the BLAST output ###########
    # sort blast_output -k1,1 -k2,2 -k12nr > sorted_output
    sortPath: str = os.path.join(outDir, f"sorted_{bsName}")

    ##### RESTORE THIS IF REQUIRED #####
    # ofd = open(sortPath, "w")
    #sort(inBlastOut, '-k1,1', '-k2,2', '-k12nr', _out=ofd)
    # sort(inBlastOut, '-k1,1', '-k2,2', '-k7nr', _out=ofd)
    # ofd.close()
    ###################################

    sortCmd: str = f"sort -o {sortPath} -k1,1 -k2,2 -k7nr {inBlastOut}"
    # use run (or call)
    subprocess.run(sortCmd, shell=True)

    if debug:
        print(f"Sort CMD:\n{sortCmd}")

    if not os.path.isfile(inBlastOut):
        sys.stderr.write(f"WARNING: the file\n{inBlastOut}\nwas not found...")
    # remove the unsorted output and rename
    os.remove(inBlastOut)
    os.rename(sortPath, inBlastOut)
    ############################################

    # Choose the parser for the aligner
    if dmndMode:
        # Parse the Diamond output
        parser.dmnd_parser(inBlastOut, qSeqLenPath, tSeqLenPath, outDir=outDir, outName=outName, minBitscore=minBitscore, compress=compress, complev=complev, debug=False)
    else:
        # Parse the MMseqs2 output
        parser.mmseqs_parser_7flds(inBlastOut, qSeqLenPath, tSeqLenPath, outDir=outDir, outName=outName, minBitscore=minBitscore, compress=compress, complev=complev, debug=False)



def parallel_dbs_creation(spList: List[str], inDir: str, dbDir: str, create_idx: bool = True, alnTool: str = "mmseqs", dmndSens: str = "sensitive", threads: int = 4, debug: bool = False):
    """Create MMseqs2, Diamond. BLAST databases in parallel"""

    # create the queue and start adding
    make_dbs_queue: mp.queues.Queue = mp.Queue(maxsize=len(spList) + threads)

    # fill the queue with the processes
    for sp in spList:
        sys.stdout.flush()
        make_dbs_queue.put(os.path.basename(sp))

    # add flags for completed jobs
    for i in range(0, threads):
        sys.stdout.flush()
        make_dbs_queue.put(None)

    # Queue to contain the execution time
    results_queue: mp.queues.Queue = mp.Queue(maxsize=len(spList))

    # call the method inside workers
    if alnTool == "diamond":
        runningJobs = [mp.Process(target=consume_dmnd_createdb, args=(make_dbs_queue, results_queue, inDir, dbDir, create_idx, dmndSens)) for i_ in range(threads)]
    elif alnTool == "mmseqs":
        runningJobs = [mp.Process(target=consume_mmseqs_createdb, args=(make_dbs_queue, results_queue, inDir, dbDir, create_idx)) for i_ in range(threads)]
    elif alnTool == "blast":
        runningJobs = [mp.Process(target=consume_blast_createdb, args=(make_dbs_queue, results_queue, inDir, dbDir)) for i_ in range(threads)]

    for proc in runningJobs:
        proc.start()

    while True:
        try:
            sp, tot_time = results_queue.get(False, 0.01)
            if debug:
                sys.stdout.write(f"Database for proteomes {sp} created:\t{tot_time}\n")
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



def perform_parallel_alignments(requiredAln: Dict[str, Tuple[float, int]], protCntDict:Dict[str, int], runDir:str, dbDir:str, alnDir:str, create_idx:bool=True, sensitivity:float=4.0, alnTool: str = "mmseqs", dmndSens:str="sensitive", minBitscore:int=40, pmtx:str="blosum62", essentialMode:bool=True, threads:int=4, keepAln:bool=False, compress:bool=False, complev:int=5, debug:bool=False) -> None:
    auxDir: str = os.path.join(runDir, "aux")
    """Create FASTA subsets in parallel."""
    if debug:
        print("\nperform_parallel_alignments :: START")
        print(f"Alignments jobs to be performed:\t{len(requiredAln)}")
        print(f"Proteomes:\t{len(protCntDict)}")
        print(f"Alignment tool:\t{alnTool}")
        print(f"Directory containing run files: {runDir}")
        print(f"Directory with auxiliary files: {auxDir}")
        print(f"Directory with shared MMseqs2 databases: {dbDir}")
        print(f"Directory with alignments: {alnDir}")
        print(f"Create MMseqs index files:\t{create_idx}")
        print(f"MMseqs sensitivity:\t{sensitivity:.2f}")
        print(f"Diamond sensitivity:\t{dmndSens}")
        print(f"Minimum bitscore:\t{minBitscore}")
        print(f"MMseqs2 prefilter substitution matrix:\t{pmtx}")
        print(f"Essential mode:\t{essentialMode}")
        print(f"Threads:\t{threads}")
        print(f"Keep alignment files:\t{keepAln}")
        print(f"Compress output:\t{compress}")
        print(f"Compression level:\t{complev}")

    # Set alignment tool name
    alnToolName: str = "MMseqs2"
    if alnTool == "diamond":
        alnToolName = "Diamond"
    elif alnTool == "blast":
        alnToolName = "BLAST"

    # identify the species for which the DB should be created
    # Consider only the job in COMPLETE mode
    # Given the pair A-B execute the job type has following values:
    # 0 -> Complete (e.g. slow inter-proteome, or intra-proteome alignment)
    # 1 -> essentials alignment
    reqSpSet: Set[int] = set()
    for pair, tpl in requiredAln.items():
        if tpl[1] == 0: # Complete or intra-proteome alignment
            sp1, sp2 = [int(x) for x in pair.split('-', 1)]
            if not sp1 in reqSpSet:
                reqSpSet.add(sp1)
            if not sp2 in reqSpSet:
                reqSpSet.add(sp2)
            # exit if all the possible species have been inserted
            if len(reqSpSet) == len(protCntDict):
                break

    if len(reqSpSet) > 0:
        fastaDir: str = os.path.join(auxDir, "mapped_input")
        # create the directory which will contain the databases
        systools.makedir(dbDir)
        # Make sure there is enough storage to crate the index files
        # overwrites the create_idx variable
        if create_idx:
            create_idx = check_storage_for_db_indexing(dbDir, reqSp=len(reqSpSet), gbPerSpecies=0.95, debug=debug)

        # create databases
        sys.stdout.write(f"\nCreating {len(reqSpSet)} {alnToolName} databases...\n")
        # timer for databases creation
        start_time: float = time.perf_counter()

        # create databases in parallel
        parallel_dbs_creation([str(x) for x in reqSpSet], fastaDir, dbDir, create_idx=create_idx, alnTool=alnTool, dmndSens=dmndSens, threads=threads, debug=debug)
        # end time for databases creation
        end_time: float = time.perf_counter()
        sys.stdout.write(f"\n{alnToolName} databases creation elapsed time (seconds):\t{round(end_time - start_time, 3)}\n")
        # delete timers
        del start_time, end_time

    # Set variables shared among processes
    # sharedValues -> completedJob, requiredJobs, processing, waiting, cpusInUse, totCores
    sharedValues: List[int] = mp.Array("i", [0, len(requiredAln), 0, 0, 0, threads])
    sharedValsLock: mp.synchronize.Lock = mp.Lock()

    # create the queue and start adding
    aln_queue: mp.queues.Queue = mp.Queue(maxsize=len(requiredAln) + threads)
    # directory with the original alignments
    originalAlnDir = os.path.join(os.path.dirname(os.path.dirname(runDir)), "alignments")
    if not os.path.isdir(originalAlnDir):
        sys.stderr.write("\nERROR: The directory with alignments was not found.")
        sys.exit(-2)
    # fill the queue with the file paths
    tmpA: str = ""
    tmpB: str = ""
    for pair, tpl in requiredAln.items():
        # tpl contains the following information
        # tpl[0]: float => job weight
        # tpl[1]: int => type of job (e.g, 0-> complete alignment, 1-> essential alignment)
        tmpA, tmpB = pair.split("-", 1)
        # proteome pair as tuple: e.g. "1-2" as ("1", "2")
        # and sequence counts  and proteome sizes for each proteome
        aln_queue.put(((tmpA, tmpB), tpl[1], protCntDict[tmpA], protCntDict[tmpB]))

    # add flags for ended jobs
    for i in range(0, threads):
        sys.stdout.flush()
        aln_queue.put(None)

    # Queue to contain the execution times
    results_queue: mp.queues.Queue = mp.Queue(maxsize=len(requiredAln))

    # List of running jobs
    runningJobs: List[Any] = []

    if alnTool == "diamond":
        runningJobs = [mp.Process(target=consume_dmnd_aln, args=(aln_queue, results_queue, runDir, dbDir, alnDir, create_idx, keepAln, dmndSens, minBitscore, compress, complev, sharedValues, sharedValsLock)) for i_ in range(threads)]
    elif alnTool == "mmseqs":
        runningJobs = [mp.Process(target=consume_mmseqs_aln, args=(aln_queue, results_queue, runDir, dbDir, alnDir, keepAln, sensitivity, minBitscore, pmtx, compress, complev, sharedValues, sharedValsLock)) for i_ in range(threads)]
    elif alnTool == "blast":
        runningJobs = [mp.Process(target=consume_blast_aln, args=(aln_queue, results_queue, runDir, dbDir, alnDir, keepAln, minBitscore, compress, complev, sharedValues, sharedValsLock)) for i_ in range(threads)]

    # execute the jobs
    for proc in runningJobs:
        proc.start()

    # open the file in which the time information will be stored
    # use the parent directory name of the database directory as suffix
    alnExTimeFileName: str = "aln_ex_times_{:s}_ra_{:s}.tsv".format(alnTool, os.path.basename(runDir.rstrip("/")))
    if not essentialMode:
        alnExTimeFileName = alnExTimeFileName.replace("_ra_", "_ca_")
    # Change the alignment tool to Diamond
    execTimeOutPath: str = os.path.join(alnDir, alnExTimeFileName)
    del alnExTimeFileName
    ofd = open(execTimeOutPath, "w", buffering=1)

    # calculate cpu-time for alignments
    align_start = time.perf_counter()
    # write some message...
    sys.stdout.write(f"\nPerforming {len(requiredAln)} alignment using {alnToolName}...")
    # will contain the results from an alignment job
    resList: List[Tuple[str, float, float, float, float, float]] = []

    # Create the status bar
    # Do not show the progress bar but shows the stastics and percentage
    # pbar: tqdm = tqdm(total=len(requiredAln), desc="all-vs-all alignments", unit="pairs", disable=None, smoothing=0.1, ncols = 0)
    # Show the progress bar
    pbar: tqdm = tqdm(total=len(requiredAln), desc="all-vs-all alignments", unit="pairs", disable=None, smoothing=0.3, ascii=False, miniters=1, mininterval=2.0, colour='red')


    # write output when available
    while True:
        try:
            resList = results_queue.get(False, 0.01)
            for resTpl in resList:
                ofd.write('{:s}\t{:.3f}\t{:.3f}\t{:.3f}\t{:.1f}\t{:.2f}\t{:.2f}\t{:.3f}\t{:d}\n'.format(*resTpl))
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
    sys.stdout.write(f"\nElapsed time for all-vs-all alignments using {alnToolName} (seconds):\t{round(time.perf_counter() - align_start, 3)}\n")
    # sys.exit("DEBUG: @workers.perform_parallel_alignments, after jobs completition")



def perform_parallel_orthology_inference_shared_dict(requiredPairsDict, inDir, outDir=os.getcwd(), sharedDir=None, sharedWithinDict=None, minBitscore=40, confCutoff=0.05, lenDiffThr=0.5, threads=8, compressed:bool=False, debug=False):
    """Execute orthology inference for the required pairs."""
    if debug:
        print("\nperform_parallel_orthology_inference_shared_dict :: START")
        print(f"Proteome pairs to be processed:\t{len(requiredPairsDict)}")
        print(f"Input directory: {inDir}")
        print(f"Outdir: {outDir}")
        print(f"Alignment directory: {sharedDir}")
        print(f"Shared within-align dictionaries:\t{len(sharedWithinDict)}")
        print(f"Minimum bitscore:\t{minBitscore}")
        print(f"Confidence cutoff for paralogs:\t{confCutoff}")
        print(f"Length difference filtering threshold:\t{lenDiffThr}")
        print(f"CPUs (for mmseqs):\t{threads}")
        print(f"Compressed alignment files:\t{compressed}")
    # make sure that the directory with alignments exists
    if not os.path.isdir(sharedDir):
        sys.stderr.write(f"ERROR: The directory with the alignment files\n{sharedDir}\nwas not found, please provide a valid path\n")
        sys.exit(-2)
    if not os.path.isdir(inDir):
        sys.stderr.write(f"ERROR: The directory with the input files\n{inDir}\nwas not found, please provide a valid path\n")
        sys.exit(-2)
    #create the output directory if does not exist yet
    if outDir != os.getcwd():
        if not os.path.isdir(outDir):
            systools.makedir(outDir)
    # check if the output directory differs from the input one
    if os.path.dirname(inDir) == os.path.dirname(outDir):
        sys.stderr.write(f"\nERROR: the output directory {outDir}\nmust be different from the one in which the input files are stored\n{inDir}\n")
        sys.exit(-2)

    # create the queue and start adding the jobs
    jobs_queue: mp.queues.Queue = mp.Queue(maxsize=len(requiredPairsDict)+threads)

    # fill the queue with the processes
    for pair in requiredPairsDict:
        jobs_queue.put(pair)
    # add flags for eneded jobs
    for i in range(0, threads):
        jobs_queue.put(None)

    # Queue to contain the execution time
    results_queue: mp.queues.Queue = mp.Queue(maxsize=len(requiredPairsDict))
    # call the method inside workers
    runningJobs = [mp.Process(target=consume_orthology_inference_sharedict, args=(jobs_queue, results_queue, inDir, outDir, sharedDir, sharedWithinDict, minBitscore, confCutoff, lenDiffThr, threads, compressed)) for i_ in range(threads)]

    for proc in runningJobs:
        proc.start()

    # open the file in which the time information will be stored
    execTimeOutPath = os.path.join(sharedDir, "orthology_ex_time_{:s}.tsv".format(os.path.basename(outDir.rstrip("/"))))
    ofd = open(execTimeOutPath, "w", buffering=1)

    # Create the status bar
    # Show the progress bars in ASCII
    # pbar: tqdm = tqdm(total=len(requiredPairsDict), desc="all-vs-all alignments", unit="pairs", disable=None, smoothing=0.1, ascii=True)
    # Show the progress bars in ASCII
    pbar: tqdm = tqdm(total=len(requiredPairsDict), desc="graph-based orthologs tables", unit="tables", disable=None, smoothing=0.3, ascii=False, miniters=1, mininterval=2.0, colour='green')

    # update the shared dictionary
    # and remove the shared dictionary if required
    # get the results from the queue without filling the Pipe buffer
    gcCallSentinel: int = 2 * threads
    whileCnt: int = 0
    wtCnt: int = 0
    gcCallCnt: int = 0
    while True:
        try:
            p, val = results_queue.get(False, 0.01)
            ofd.write("{:s}\t{:s}\n".format(p, str(val)))
            whileCnt += 1
            wtCnt += 1
            #'''
            sp1, sp2 = p.split("-", 1)
            # decrease the counters in the shared dictionaries
            sharedWithinDict[sp1][0] -= 1
            if sharedWithinDict[sp1][0] == 0:
                del sharedWithinDict[sp1]
                # call the garbage collector to free memory explicitly
                gc.collect()
                if debug:
                    print(f"Removed dictionary for {sp1}")
                    print(f"Remaining shared dictionaries:\t{len(sharedWithinDict)}")
            sharedWithinDict[sp2][0] -= 1
            if sharedWithinDict[sp2][0] == 0:
                del sharedWithinDict[sp2]
                gc.collect()
                if debug:
                    print(f"Removed dictionary for {sp2}")
                    print(f"Remaining shared dictionaries:\t{len(sharedWithinDict)}")
            # call the garbage collector if a given number ortholog tables
            # has been generated
            if whileCnt == gcCallSentinel:
                gc.collect()
                whileCnt = 0
                gcCallCnt += 1
                if debug:
                    print(f"\ngc.collect() call:\t{gcCallCnt}\nCompleted tables:\t{wtCnt}")

            # Update the status bar
            pbar.update(1)

        # except queue.Empty:
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

    for proc in runningJobs:
        while proc.is_alive():
            proc.join()



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