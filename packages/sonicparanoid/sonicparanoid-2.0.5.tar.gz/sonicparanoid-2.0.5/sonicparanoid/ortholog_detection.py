"""This module contains wrapper functions for the detection of orthologs."""
import sys
import os
import time
import itertools
from collections import deque
import shutil
import numpy as np
import pickle
from scipy.sparse import dok_matrix, triu, save_npz, load_npz
from typing import Dict, List, Any, Tuple, Set, Deque
from subprocess import run, PIPE

# Internal modules
from sonicparanoid import sys_tools as systools
from sonicparanoid import inpyranoid
from sonicparanoid import workers
from sonicparanoid import essentials_c as essentials



__module_name__ = "Ortholog detection"
__source__ = "ortholog_detection.py"
__author__ = "Salvatore Cosentino"
#__copyright__ = ""
__license__ = "GPL"
__version__ = "2.9"
__maintainer__ = "Cosentino Salvatore"
__email__ = "salvo981@gmail.com"



def info():
    """This module contains functions for the detection of orthologs."""
    print(f"MODULE NAME:\t{__module_name__}")
    print(f"SOURCE FILE NAME:\t{__source__}")
    print(f"MODULE VERSION:\t{__version__}")
    print(f"LICENSE:\t{__license__}")
    print(f"AUTHOR:\t{__author__}")
    print(f"EMAIL:\t{__email__}")



def extract_ortholog_pairs(rootDir=os.getcwd(), outDir=os.getcwd(), outName=None, pairsFile=None, singleDir=False, tblPrefix="table", debug=False):
    """Create file containing all generated ortholog pairs."""
    if debug:
        print("\nextract_ortholog_pairs :: START")
        print(f"Root directory:\t{rootDir}")
        print(f"Output directory:\t{outDir}")
        print(f"Output file name:\t{outName}")
        print(f"Species pairs file:\t{pairsFile}")
        print(f"All tables in same directory:\t{singleDir}")
        print(f"Table file prefix:\t{tblPrefix}")
    #fetch result files tables
    tblList: List[str] = fetch_pairwise_tables(rootDir=rootDir, outDir=outDir, pairsFile=pairsFile, tblPrefix=tblPrefix, singleDir=singleDir, debug=debug)
    totRead: int = 0
    tblCnt: int = 0
    totUniqPairs: int = 0
    #extract the project name from the root
    projName: str = ""
    # NOTE: rtemove this since it not required
    if rootDir[-1] == "/":
        projName = rootDir.rsplit("/", 2)[-2]
    else:
        projName = rootDir.rsplit("/", 2)[-1]
    if outName is None:
        outName = f"{projName}_all_relations.tsv"
    #create output directory if required
    systools.makedir(outDir)
    #output file
    outTbl = os.path.join(outDir, outName)
    # this dictionary is to avoid repetition among the non-core pairs
    repeatTrap: Set[str] = set()
    ortho1All: List[str] = []
    ortho2All: List[str] = []
    print("\nCreating file with homolog pairs...")
    #create output file
    ofd = open(outTbl, "wt", encoding="utf-8")
    for path in tblList:
        if os.path.isfile(path):
            # if debug:
            #     print(path)
            if os.path.basename(path).startswith(tblPrefix) or singleDir:
                tblCnt += 1
                for clstr in open(path, "rt", encoding="utf-8"):
                    if (clstr[0] == "O") or (clstr[0] == "S"): # This handles case for both graph-only and merged
                        continue
                    totRead += 1
                    clusterID, score, orto1, orto2 = clstr.rstrip().split("\t")
                    del score, clusterID
                    #count the cases
                    ortho1All = orto1.rstrip().split(" ")
                    ortho2All = orto2.rstrip().split(" ")
                    #make lists with gene ids
                    ortho1list: List[str] = []
                    #extract genes for ortho1
                    for i, gene in enumerate(ortho1All):
                        if i % 2 == 0:
                            ortho1list.append(gene)
                    #extract genes for ortho2
                    ortho2list: List[str] = []
                    #extract genes for ortho1
                    for i, gene in enumerate(ortho2All):
                        if i % 2 == 0:
                            ortho2list.append(gene)
                    #write the pairs in the output file
                    for orto1gene in ortho1list:
                        for orto2gene in ortho2list:
                            tmpPair = f"{orto1gene}-{orto2gene}"
                            if not tmpPair in repeatTrap:
                                repeatTrap.add(tmpPair)
                                ofd.write(f"{orto1gene}\t{orto2gene}\n")
                                totUniqPairs += 1
        repeatTrap.clear()
    ofd.close()

    # remove not required data structures
    del ortho1All, ortho2All, ortho2list, ortho1list

    # Sort the pairs file only if the number of pairs is below 50M
    if totUniqPairs <= 30000000:
        tmpSortPath = os.path.join(outDir, "tmp_sorted_orthologs.tsv")
        # EXAMPLE: sort -o <output_sorted_path> <input_to_sort>
        sortCmd:str = f"sort -o {tmpSortPath} {outTbl}"
        if debug:
            print("Sorting homolog pairs...")
            print(f"sort CMD:\n{sortCmd}")
        run(sortCmd, shell=True, check=True)
        # remove the original ortholog pairs file
        os.remove(outTbl)
        # rename the sorted file to the original output name
        os.rename(tmpSortPath, outTbl)

    if debug:
        print(f"Processed ortholog tables:\t{tblCnt}")
        print(f"Total clusters read:\t{totRead}")
        print(f"Final ortholog pairs:\t{totUniqPairs}")

    # write the number of ortholog relations in created
    pout = run(f"wc -l {outTbl}", stdout=PIPE, check=True, shell=True)
    if debug:
        print(f"wc CMD:\n{pout.args}")
    if pout.returncode != 0:
        sys.stderr.write("\nERROR: the file with ortholog pairs could not be generated!\n")
        sys.exit(-7)
    else:
        pairsCnt:str = pout.stdout.decode().rsplit(" ", 1)[0]
        pairsCnt = pairsCnt.strip()
        print(f"Total orthologous relations\t{pairsCnt}")



def fetch_pairwise_tables(rootDir=os.getcwd(), outDir=os.getcwd(), pairsFile=None, tblPrefix="table", singleDir=False, debug=False) -> List[str]:
    """Find the ortholog-table file for each proteome pair."""
    if debug:
        print("\nfetch_pairwise_tables :: START")
        print(f"Root directory:\t{rootDir}")
        print(f"Output directory:\t{outDir}")
        print(f"Species pairs file:\t{pairsFile}")
        print(f"Table prefix:\t{tblPrefix}")
        print(f"Pairwise table are stored all in the same directory:\t{singleDir}")

    #check that the input directory is valid
    if not os.path.isdir(rootDir):
        sys.stderr.write(f"ERROR: the directory containing the table files\n{rootDir}\n does not exist.\n")
        sys.exit(-2)
    if not os.path.isfile(pairsFile):
        sys.stderr.write("ERROR: you must provide a file containing all the species pairs\n")
        sys.exit(-2)
    #create the output directory if does not exist yet
    systools.makedir(outDir)
    # initialize tmp variables
    pairs: Set[str] = set()
    fileList: List[str] = []
    sp1: str = ""
    tblDir: str = ""
    tblPath: str = ""
    # Find the tables
    for pair in open(pairsFile, "rt", encoding="utf-8"):
        pair = pair[:-1]
        sp1 = pair.split("-", 1)[0]
        pairs.add(pair)
        # Set the table file path
        if singleDir:
            tblDir = rootDir
        else:
            # Tables are stored in subdirectories
            # EXAMPLE: 2-3 and 2-4 are stored under directory '2' and so on...
            tblDir = os.path.join(rootDir, sp1)
        # set the table name
        if len(tblPrefix) == 0:
            tblPath = os.path.join(tblDir, pair)
        else:
            tblPath = os.path.join(tblDir, f"{tblPrefix}.{pair}")
        if os.path.isfile(tblPath):
            fileList.append(tblPath)
    #check that the found tables and the species-pairs count are same
    if len(fileList) != len(pairs):
        sys.stderr.write(f"ERROR: the number of ortholog tables found ({len(fileList)}) and the number of species pairs ({len(pairs)}) must be the same.\n")
        if debug:
            # Print the missing pairs
            foundSet: Set[str] = set([os.path.basename(f) for f in fileList])
            print("\nThe ortholog tables for the following pairs are missing:")
            print(" ".join(sorted(pairs.difference(foundSet))))
        sys.exit(-4)
    if debug:
        print(f"Found tables:\t{len(fileList)}")
    #return the final list
    return fileList



def identify_required_aln_and_tbls(protCntDict: Dict[str, int], spSizeDict: Dict[str, int], runDir: str, alignDir: str, tblDir: str, owTbls: bool = False, owAll: bool = False, debug: bool = False) -> Tuple[int, int, int]:
    """Create matrixes with required (fast and slow) alignments and tables"""
    from math import log2
    if debug:
        print(f"\nidentify_required_aln_and_tbls :: START")
        print(f"Input proteomes:\t{len(protCntDict)}")
        print(f"Proteome sizes:\t{len(spSizeDict)}")
        print(f"Run directory: {runDir}")
        print(f"Directory with alignments: {alignDir}")
        print(f"Directory with pairwise-orthologs: {tblDir}")
        print(f"Overwrite ortholog tables:\t{owTbls}")
        print(f"Overwrite everything:\t{owAll}")
    # initialize some variables
    spList: List[int] = [int(x) for x in list(protCntDict.keys())]
    spList.sort()
    alnCntCicle1: int = 0
    alnCntCicle2: int = 0
    orthoTblsCnt: int = 0

    # set the overwite table if required
    if owAll:
        owTbls = True

    # load matrix with fast combinations
    fastMtxPath: str = os.path.join(runDir, "fast_aln_mtx.npz")
    tmpM = load_npz(fastMtxPath)
    refMtxShape: Tuple[int, int] = tmpM.shape

    # initialize the matrixes with required alignments
    dueCicle1Mtx = dok_matrix(refMtxShape, dtype=np.single)
    dueCicle2Mtx = dok_matrix(refMtxShape, dtype=np.single)

    # get indexes with non-zero values
    lM, cM = tmpM.nonzero()

    # tmp indexes for the matrix
    l: int = -1
    c: int = -1
    tmpW: float = 0.
    tmpA: str = ""
    tmpB: str = ""
    tmpPath: str = ""
    tmpFilePath: str = ""

    # fill the matrixes with required alignments
    for tpl in zip(lM, cM):
        l = tpl[0]
        c = tpl[1]
        tmpA = str(l + 1)
        tmpB = str(c + 1)
        # NOTE: change the directory to contain the query as a subdirectory
        # tmpPath = os.path.join(alignDir, f"{tmpA}-{tmpB}")
        tmpPath = os.path.join(alignDir, f"{tmpA}/{tmpA}-{tmpB}")
        # compute weight as follows
        # log2(avg_size(A, B) * avg_count(A, B))
        tmpW = round(log2(((protCntDict[tmpA] + protCntDict[tmpB]) * (spSizeDict[tmpA] + spSizeDict[tmpB])) / 4.), 6)

        if owAll: # perform the alignments regardless
            # whipe the directory with alignments
            # NOTE: using os.walk might be more efficient
            for f in os.listdir(alignDir):
                tmpFilePath = os.path.join(alignDir, f)
                try:
                    if os.path.isfile(tmpFilePath):
                        os.remove(tmpFilePath)
                    elif os.path.isdir(tmpFilePath):
                        shutil.rmtree(tmpFilePath)
                except Exception as e:
                    print(e)
            # add the elements to the 2 matrixes
            dueCicle1Mtx[l, c] = tmpW
            dueCicle2Mtx[c, l] = tmpW
        else: # perform only missing alignments
            # add element in matrix if the alignment does not exist (search also for the gz file)
            if os.path.isfile(tmpPath) or os.path.isfile(f"{tmpPath}.gz"):
                # do nothing
                pass
            else:
                # add the element in the matrix
                dueCicle1Mtx[l, c] = tmpW

            # check if the other pair alignment exists
            # NOTE: change the directory to contain the query as a subdirectory
            # tmpPath = os.path.join(alignDir, f"{tmpB}-{tmpA}")
            tmpPath = os.path.join(alignDir, f"{tmpB}/{tmpB}-{tmpA}")
            if os.path.isfile(tmpPath) or os.path.isfile(f"{tmpPath}.gz"):
                # do nothing
                pass
            else:
                # add the element in the matrix
                dueCicle2Mtx[c, l] = tmpW

    # add within alignments if required
    # Give 10% higher weights to within alignments
    for sp in spList:
        # NOTE: change the directory to contain the query as a subdirectory
        # tmpPath = os.path.join(alignDir, f"{sp}-{sp}")
        tmpPath = os.path.join(alignDir, f"{sp}/{sp}-{sp}")
        tmpA = str(sp)

        if owAll:  # perform the alignments regardless of their existance
            dueCicle1Mtx[sp-1, sp-1] = round(log2(protCntDict[tmpA] * spSizeDict[tmpA]) * 1.3, 6)
            # remove the alignment file if it exists
            try:
                if os.path.isfile(tmpFilePath):
                    os.remove(tmpFilePath)
                elif os.path.isdir(tmpFilePath):
                    shutil.rmtree(tmpFilePath)
            except Exception as e:
                print(e)
        else:
            if os.path.isfile(tmpPath) or os.path.isfile(f"{tmpPath}.gz"):
                # due nothing
                pass
            else:
                tmpA = str(sp)
                dueCicle1Mtx[sp-1, sp-1] = round(log2(protCntDict[tmpA] * spSizeDict[tmpA]) * 1.3, 6)

    # update the counters
    alnCntCicle1 = dueCicle1Mtx.nnz
    alnCntCicle2 = dueCicle2Mtx.nnz

    if debug:
        print("\nRequired alignments (Cicle1)")
        print(dueCicle1Mtx.todense())
        print("\nRequired alignments (Cicle2)")
        print(dueCicle2Mtx.todense())
        print("\nAll Fast alignments")
        print(tmpM.todense())

    # store the matrixes
    dueCicle1Mtx = dueCicle1Mtx.tocsr()
    save_npz(os.path.join(runDir, "due_aln_mtx1.npz"), dueCicle1Mtx, compressed=False)
    dueCicle2Mtx = dueCicle2Mtx.tocsr()
    save_npz(os.path.join(runDir, "due_aln_mtx2.npz"), dueCicle2Mtx, compressed=False)

    # remove the matrixes
    del tmpM
    del dueCicle1Mtx
    del dueCicle2Mtx

    # initialize the matrixes with required orthology inference
    dueOrthoMtx = dok_matrix(refMtxShape, dtype=np.single)

    # For each combination fill the matrix depending if the ortholog table exists or not
    for tpl in list(itertools.combinations(spList, r=2)):
        l = tpl[0]
        c = tpl[1]
        tmpA = str(l)
        tmpB = str(c)
        # Each pair should be stored in a directory taking the name from the
        # species on the left-side of the combination
        # For example, given the combinations 1-2, 1-3, and 2-3
        # 1-2 and 1-3 will be stored into the directory 1
        # 2-3 will be stored into the directory 2
        # hence the maximum number of tables a directory will contain is N-1,
        # while the biggest species (3 in our example) will not require a directory for itself
        # NOTE: remove later
        # tmpPath = os.path.join(tblDir, f"{tmpA}-{tmpB}/table.{tmpA}-{tmpB}")
        tmpPath = os.path.join(tblDir, f"{tmpA}/{tmpA}-{tmpB}/table.{tmpA}-{tmpB}")

        if owTbls:
            tmpW = round(log2(((protCntDict[tmpA] + protCntDict[tmpB]) * (spSizeDict[tmpA] + spSizeDict[tmpB])) / 4.), 6)
            dueOrthoMtx[l-1, c-1] = tmpW
        # add element in matrix if the alignment does not exist (search also for the gz file)
        elif not os.path.isfile(tmpPath):
            # compute weight as follows
            # log2(avg_size(A, B) * avg_count(A, B))
            tmpW = round(log2(((protCntDict[tmpA] + protCntDict[tmpB]) * (spSizeDict[tmpA] + spSizeDict[tmpB])) / 4.), 6)
            dueOrthoMtx[l-1, c-1] = tmpW

    # store the matrixes
    dueOrthoMtx = dueOrthoMtx.tocsr()
    save_npz(os.path.join(runDir, "due_orthology_inference_mtx.npz"), dueOrthoMtx, compressed=False)
    orthoTblsCnt = dueOrthoMtx.nnz

    if debug:
        print("\nRequired ortholog tables:")
        print(dueOrthoMtx.todense())

    if debug:
        sys.stdout.write(f"Alignments required (cicle2):\t{alnCntCicle1}\n")
        sys.stdout.write(f"Alignments required (cicle1):\t{alnCntCicle2}\n")
        sys.stdout.write(f"Total required alignments:\t{alnCntCicle2 + alnCntCicle1}\n")
        sys.stdout.write(f"Required ortholog tables:\t{orthoTblsCnt}\n")
    del dueOrthoMtx

    # return the count of alignments and tables required
    return (alnCntCicle1, alnCntCicle2, orthoTblsCnt)



def prepare_orthology_jobs(mtxPath: str, threads: int=4, debug: bool=False) -> Dict[str, float]:
    """Load information on pairwise-orthology job from a matrix, and sort based on weights."""
    if debug:
        print("\nprepare_orthology_jobs :: START")
        print(f"Job-matrix path: {mtxPath}")
        print(f"Threads:\t{threads}")

    # accessory variables
    requiredSpSet: Set[int] = set()
    requiredJobsDict: Dict[str, float] = {}
    proteomes: int = -1
    tmpA: int = 0
    tmpB: int = 0
    tmpPair: str = ""
    tmpW: float = -1.
    jobsCnt: int = -1
    pairsCnt: int = -1
    n: int = 1

    # load the matrix with fast alignments
    tmpM = load_npz(mtxPath)
    proteomes = tmpM.shape[0]
    lM, cM = tmpM.nonzero()

    # add the entries in the dictionary with alignments
    if debug:
        print(f"Jobs to be performed:\t{len(lM)}")
    for tpl in zip(lM, cM):
        tmpA = tpl[0] + 1
        tmpB = tpl[1] + 1
        tmpW = tmpM[tpl]
        tmpPair = f"{tmpA}-{tmpB}"
        # fill the dictionary
        requiredJobsDict[tmpPair] = tmpW

        # fill the set with required species
        if len(requiredSpSet) < proteomes:
            if not tmpA in requiredSpSet:
                requiredSpSet.add(tmpA)
            if not tmpB in requiredSpSet:
                requiredSpSet.add(tmpB)

    pairsCnt = len(requiredJobsDict)
    del tmpM

    # add the job in chunks using triangular numbers
    if len(requiredJobsDict) > 0:
        # sort the alignments so that the biggest ones are performed first
        s: List[Tuple[str, float]] = [(k, requiredJobsDict[k]) for k in sorted(requiredJobsDict, key=requiredJobsDict.get, reverse=True)]
        # empty the dictionary and fill it again with the size-sorted one
        requiredJobsDict.clear()
        requiredJobsDict = {key: value for (key, value) in s}
        del s

        # fill the deque
        dqAlign: Deque[Tuple[str, float]] = deque(maxlen=pairsCnt)
        for p, w in requiredJobsDict.items():
            dqAlign.append((p, w))

        pairsCnt = len(requiredJobsDict)
        jobsCnt = 0
        n = 1
        triangularNum: int = 0
        chunkList: List[int] = []  # will contain the sizes of chunks that will fill the job queue
        # now create a list with the chunk sizes
        while jobsCnt < pairsCnt:
            n += 1
            triangularNum = int((n * (n + 1)) / 2.)
            jobsCnt += triangularNum
            chunkList.append(triangularNum)

        # sort the list of chunks in inverted order
        chunkList.sort(reverse=True)
        # remove the biggest chunk
        chunkList.pop(0)
        # invert the list with chunks
        chunkListInv: List[int] = []
        for el in chunkList:
            chunkListInv.append(el)
        chunkListInv.sort()

        # set the step to half of the cpus
        heavyChunkSize: int = int(threads / 2.)

        if heavyChunkSize == 0:
            heavyChunkSize = 1
        # update the alignments dictionary
        requiredJobsDict.clear()
        remainingJobs: int = pairsCnt

        while remainingJobs > 0:
            # add the chunk of jobs that require a lot of memory
            for i in range(0, heavyChunkSize):
                if len(dqAlign) > 0:
                    p, w = dqAlign.popleft()
                    requiredJobsDict[p] = w
                    remainingJobs -= 1  # decrement
                else:  # no more elements to be added
                    break

            # add a chunk of small jobs
            if len(chunkList) > 0:
                if len(dqAlign) > 0:
                    cSize = chunkList.pop(0)
                    for i in range(0, cSize):
                        if len(dqAlign) > 0:
                            p, w = dqAlign.pop()
                            requiredJobsDict[p] = w
                            remainingJobs -= 1  # decrement
                        else:  # no more elements to be added
                            break
            # add chunks of growing size
            elif len(chunkListInv) > 0:
                if len(dqAlign) > 0:
                    cSize = chunkListInv.pop(0)
                    for i in range(0, cSize):
                        if len(dqAlign) > 0:
                            p, w = dqAlign.pop()
                            requiredJobsDict[p] = w
                            remainingJobs -= 1  # decrement
                        else:  # no more elements to be added
                            break
    if debug:
        print(f"Pairwise-orthology inference jobs:\t{len(requiredJobsDict)}")
        print(f"Involved proteomes:\t{requiredSpSet}")
    return requiredJobsDict



def prepare_aln_jobs(mtxPath: str, p1AlnCnt: int, p2AlnCnt: int, threads: int=4, essentialMode: bool=True, debug: bool=False) -> Dict[str, Tuple[float, int]]:
    """Load the alignments or values from a the matrix with fastest pairs, and sort based on weights."""
    if debug:
        print("\nprepare_aln_jobs :: START")
        print(f"Job-matrix path with Fast alignments and intra-alignments: {mtxPath}")
        print(f"Required fastest alignments:\t{p1AlnCnt}")
        print(f"Required slow alignments:\t{p2AlnCnt}")
        print(f"Threads:\t{threads}")
        print(f"Essential mode:\t{essentialMode}")

    # accessory variables
    requiredSpSet: Set[int] = set()
    # Each key contains a pair e.g. A-B originally belonging to the job Matrix
    # the value a Tuple(float, int)
    # the first value is the weight associated to the pair
    # the second encodes says if it essential or not
    # 0 -> complete, 1 -> essential
    requiredJobsDict: Dict[str, Tuple[float, int]] = {}
    proteomes: int = -1
    tmpA: int = 0
    tmpB: int = 0
    tmpPair: str = ""
    tmpRevPair: str = "" # reverse pair
    tmpW: float = -1.
    alnCnt: int = 0
    pairsCnt: int = -1
    # Counter for job chunks
    jobsCnt: int = -1
    n: int = -1 # a simple counter
    triangularNum: int = 0
    remainingJobs: int = 0

    # load the matrix with alignments
    tmpM = load_npz(mtxPath)
    proteomes = tmpM.shape[0]
    lM, cM = tmpM.nonzero()
    alnCnt += len(lM)
    jobType: int = 0
    if essentialMode:
        jobType = 1

    # add the entries in the dictionary with alignments
    if debug:
        print(f"Complete alignments to be performed:\t{len(lM)}")
    for tpl in zip(lM, cM):
        tmpA = tpl[0] + 1
        tmpB = tpl[1] + 1
        tmpW = tmpM[tpl]
        tmpPair = f"{tmpA}-{tmpB}"
        # set the code of the run
        # fill the dictionary
        requiredJobsDict[tmpPair] = (tmpW, jobType)
        # fill the set with required species
        if len(requiredSpSet) < proteomes:
            if not tmpA in requiredSpSet:
                requiredSpSet.add(tmpA)
            if not tmpB in requiredSpSet:
                requiredSpSet.add(tmpB)

    # remove some variables
    del tmpA, tmpB, tmpPair, tmpRevPair, tmpW
    del tmpM, lM, cM

    # If it is the essential mode, there is no need to resort the jobs
    if essentialMode:
        return requiredJobsDict

    # create a shallow copy of the original dictionary
    copyOfRequiredJobsDict: Dict[str, Tuple[float, int]] = requiredJobsDict.copy()
    pairsCnt = len(requiredJobsDict)

    # add the job in chunks using triangular numbers
    if pairsCnt > 0:
        # sort the alignments so that the biggest ones are performed first
        s: List[Tuple[str, Tuple[float, int]]] = [(k, requiredJobsDict[k]) for k in sorted(requiredJobsDict, key=requiredJobsDict.get, reverse=True)]
        # empty the dictionary and fill it again with the size-sorted one
        requiredJobsDict.clear()
        requiredJobsDict = {key: value for (key, value) in s}
        del s

        # fill the deque
        dqAlign: Deque[Tuple[str, float]] = deque(maxlen=pairsCnt)
        for p, tpl in requiredJobsDict.items():
            dqAlign.append((p, tpl[0]))
        jobsCnt = 0
        n = 1
        triangularNum = 0
        chunkList: List[int] = []  # will contain the sizes of chunks that will fill the job queue
        # now create a list with the chunk sizes
        while jobsCnt < pairsCnt:
            n += 1
            triangularNum = int((n * (n + 1)) / 2.)
            jobsCnt += triangularNum
            # print(n, triangularNum, jobsCnt)
            chunkList.append(triangularNum)

        # sort the list of chunks in inverted order
        chunkList.sort(reverse=True)
        # remove the biggest chunk
        chunkList.pop(0)
        # set the step to half of the cpus
        heavyChunkSize: int = int(0.80 * threads) # Use 80% of CPUs for heavy chunks
        # print(f"heavyChunkSize:\t{heavyChunkSize}")

        if heavyChunkSize == 0:
            heavyChunkSize = 1
        # update the alignments dictionary
        requiredJobsDict.clear()
        remainingJobs = pairsCnt
        while remainingJobs > 0:
            # add the chunk of jobs that require a lot of memory
            # print(f"remaining job:\t{remainingJobs}")
            for i in range(0, heavyChunkSize):
                if len(dqAlign) > 0:
                    p, w = dqAlign.popleft()
                    # print(f"adding heavy:\t{p}\t{w}")
                    requiredJobsDict[p] = copyOfRequiredJobsDict.pop(p)
                    remainingJobs -= 1  # decrement
                else:  # no more elements to be added
                    break
            # add a chunk of small jobs
            if len(chunkList) > 0:
                if len(dqAlign) > 0:
                    cSize = chunkList.pop(0)
                    # print(f"chunk:\t{cSize}")
                    for i in range(0, cSize):
                        if len(dqAlign) > 0:
                            p, w = dqAlign.pop()
                            # print(f"adding small:\t{p}\t{w}")
                            requiredJobsDict[p] = copyOfRequiredJobsDict.pop(p)
                            remainingJobs -= 1  # decrement
                        else:  # no more elements to be added
                            break

    # remove some variables
    del triangularNum, n, pairsCnt, copyOfRequiredJobsDict

    if debug:
        print(f"\nJobs to be performed:\t{len(requiredJobsDict)}")
        print(f"Alignments to be performed:\t{alnCnt}")
        print(f"Involved proteomes:\t{str(requiredSpSet)}")

    return requiredJobsDict



def run_sonicparanoid2_multiproc_essentials(inPaths: List[str], outDir:str, tblDir:str, threads:int=4, alignDir:str="", seqDbDir:str="", sensitivity=4.0, create_idx=True, alnTool: str = "mmseqs", dmndSens: str = "sensitive", minBitscore=40, confCutoff=0.05, pmtx:str="blosum62", lenDiffThr=0.5, overwrite_all=False, overwrite_tbls=False, update_run=False, keepAlign=False, essentialMode=True, compress:bool=False, complev:int=5, debug=False) -> Tuple[str, str, Dict[str, float]]:
    """Execute sonicparanoid, using MMseqs2 or Diamond if required for all the proteomes in the input directory."""
    import copy
    from math import log2
    # set the path to aux directory
    auxDir:str = os.path.join(outDir, "aux/")
    if debug:
        print("\nrun_sonicparanoid2_multiproc_essentials :: START")
        print(f"Input paths:\t{len(inPaths)}")
        print(f"Alignment tool:\t{alnTool}")
        print(f"Run directory: {outDir}")
        print(f"Directory with auxiliary files: {auxDir}")
        print(f"Pairwise-ortholog directory: {tblDir}")
        print(f"CPUs:\t{threads}")
        print(f"Directory with alignment: {alignDir}")
        print(f"MMseqs2 database directory: {seqDbDir}")
        print(f"MMseqs2 sensitivity (-s):\t{sensitivity}")
        print(f"Index MMseqs2 databases:\t{create_idx}")
        print(f"Diamond sensitivity:\t{dmndSens}")
        print(f"MMseqs2 prefilter substitution matrix:\t{pmtx}")
        print(f"Minimum bitcore:\t{minBitscore}")
        print(f"Confidence cutoff for paralogs:\t{confCutoff}")
        print(f"Length difference filtering threshold:\t{lenDiffThr}")
        print(f"Overwrite existing ortholog tables:\t{overwrite_tbls}")
        print(f"Overwrite everything:\t{overwrite_all}")
        print(f"Update an existing run:\t{update_run}")
        print(f"Keep raw MMseqs2 alignments:\t{keepAlign}")
        print(f"Essential mode:\t{essentialMode}")
        print(f"Compress output:\t{compress}")
        print(f"Compression level:\t{complev}")

    # Set alignment tool name
    alnToolName: str = "MMseqs2"
    if alnTool == "diamond":
        alnToolName = "Diamond"
    elif alnTool == "blast":
        alnToolName = "BLAST"

    # directory with the input files
    inDir: str = os.path.dirname(inPaths[0])

    # accessory variables
    reqAln1Cnt: int = 0
    reqAln2Cnt: int = 0
    reqOrthoTblsCnt: int = 0
    # check that file with info on input file exists
    spFile = os.path.join(auxDir, "species.tsv")
    if not os.path.isfile(spFile):
        sys.stderr.write(f"\nERROR: the species file ({os.path.basename(spFile)}) could not be found.")
        sys.stderr.write("\nMake sure the species file is created before proceeding.\n")
        sys.exit(-2)

    # load proteomes sizes and protein lengths
    spSizeDict: Dict[str, int] = {}
    with open(os.path.join(auxDir, "proteome_sizes.pckl"), "rb") as fd:
        spSizeDict = pickle.load(fd)
    protCntDict: Dict[str, int] = {}
    with open(os.path.join(auxDir, "protein_counts.pckl"), "rb") as fd:
        protCntDict = pickle.load(fd)

    # generate the combinations
    spList: List[str] = list(spSizeDict.keys())
    spPairsFile = os.path.join(auxDir, "species_pairs.tsv")
    spPairs: List[Tuple[str, str]] = list(itertools.combinations(spList, r=2))

    # create a matrix that contains the combinations
    # this will be used as a control to decide if the master matrix can be created
    spListInt: List[int] = [int(x) for x in spList]  # convert the strings to integers
    spListInt.sort()
    maxSp: int = max(spListInt)
    M = dok_matrix((maxSp, maxSp), dtype=np.int8)
    # generate the combinations
    tplsList: List[Tuple[int, int]] = list(itertools.combinations(spListInt, r=2))
    # Fill the matrix
    for tplInt in tplsList:
        M[tplInt[0]-1, tplInt[1]-1] = 1
    # store to a npz file
    M = M.tocsr()
    M = triu(M, k=0, format="csr")
    combMtxPath = os.path.join(auxDir, "combination_mtx.npz")
    save_npz(combMtxPath, M, compressed=False)
    del M
    del spListInt

    #check that the file with genome pairs has not been created yet
    dashedPairs: List[str] = [f"{tpl[0]}-{tpl[1]}" for tpl in spPairs]
    if os.path.isfile(spPairsFile):
        sys.stderr.write(f"\nWARNING: the species file\n{spPairsFile}\nalready exists already you are probably overwriting a previous run...")
    else:
        with open(spPairsFile, "w") as ofd:
            [ofd.write(f"{tmpPair}\n") for tmpPair in dashedPairs]

    # Predict the fastest pairs
    # Create the matrixes and add the weights for each job
    essentials.predict_fastest_pairs(outDir=auxDir, pairs=dashedPairs, protCnts=protCntDict, protSizes=spSizeDict, debug=debug)
    #give some information about the combinations
    print(f"\nFor the {len(spList)} input species {len(spPairs)} combinations are possible.")

    # Pairs for which the ortholog table is missing
    requiredPairsDict: Dict[str, float] = {}
    # Will contain the required alignments
    requiredAlignDict: Dict[str, Tuple[float, int]] = {}

    # identify the alignments and ortholog inference runs that will be performed
    reqAln1Cnt, reqAln2Cnt, reqOrthoTblsCnt = identify_required_aln_and_tbls(protCntDict, spSizeDict, auxDir, alignDir, tblDir, overwrite_tbls, overwrite_all, debug)

    # Perform required alignments
    if (reqAln1Cnt + reqAln2Cnt) > 0:
        # Process matrixes separately. One job performs a single alignment
        requiredAlignDict = prepare_aln_jobs(os.path.join(auxDir, "due_aln_mtx1.npz"), reqAln1Cnt, reqAln2Cnt, threads=threads, essentialMode=False, debug=debug)
        requiredEssentialAlignDict: Dict[str, Tuple[float, int]] = prepare_aln_jobs(os.path.join(auxDir, "due_aln_mtx2.npz"), reqAln1Cnt, reqAln2Cnt, threads=threads, essentialMode=essentialMode, debug=debug)
        # Add all the jobs from the second dictionary to the first one

        # NOTE: The second chunk of jobs (essentials) are queued in a way that minizes the chances of bottlenecks
        tmpPairsList: list[str] = list(requiredAlignDict.keys())
        for p in tmpPairsList:
            sp1, sp2 = p.split("-", 1)
            if sp1 == sp2:
                continue
            else:
                tmpInterProt = f"{sp2}-{sp1}"
                if tmpInterProt in requiredEssentialAlignDict:
                    requiredAlignDict[tmpInterProt] = requiredEssentialAlignDict.pop(tmpInterProt)
        # Make sure all the essential jobs had been added
        tmpPairsList = list(requiredEssentialAlignDict.keys())
        if len(tmpPairsList) > 0:
            for p in tmpPairsList:
                requiredAlignDict[p] = requiredEssentialAlignDict.pop(p)

        # remove the the second dictionary
        del requiredEssentialAlignDict, tmpPairsList
        # Set number of threads per job
        if len(requiredAlignDict) > 0:
            # perform the alignments
            sys.stdout.write(f"\n{reqAln1Cnt + reqAln2Cnt} {alnToolName} alignments will be performed...")
            workers.perform_parallel_alignments(requiredAln=requiredAlignDict, protCntDict=protCntDict, runDir=outDir, dbDir=seqDbDir, alnDir=alignDir, create_idx=create_idx, sensitivity=sensitivity, alnTool=alnTool, dmndSens=dmndSens, minBitscore=minBitscore, pmtx=pmtx, essentialMode=essentialMode, threads=threads, keepAln=keepAlign, compress=compress, complev=complev, debug=debug)

        # sys.exit("DEBUG: ortholog_detection.run_sonicparanoid2_multiproc_essentials")

    # Wipe the directory with the old ortholog table files
    if overwrite_tbls:
        shutil.rmtree(tblDir, ignore_errors=True)
    # Infer required ortholog tables
    if reqOrthoTblsCnt > 0:
        systools.makedir(tblDir)
        requiredPairsDict = prepare_orthology_jobs(os.path.join(auxDir, "due_orthology_inference_mtx.npz"), threads, debug)
        tmpA: str = ""
        tmpB: str = ""
        tmpW: float = 0.
        withinAlignDict: Dict[str, List[Any]] = {}
        # initialize the dictionary with within
        for pair in requiredPairsDict.keys():
            tmpA, tmpB = pair.split("-", 1)
            if not tmpA in withinAlignDict:
                tmpW = round(log2((protCntDict[tmpA] * spSizeDict[tmpA])), 6)
                withinAlignDict[tmpA] = [tmpW, None, None]
            if not tmpB in withinAlignDict:
                tmpW = round(log2((protCntDict[tmpB] * spSizeDict[tmpB])), 6)
                withinAlignDict[tmpB] = [tmpW, None, None]
            if len(withinAlignDict) == maxSp:
                break

        # refill the dictionary by sorting by value
        s = [(k, withinAlignDict[k]) for k in sorted(withinAlignDict, key=withinAlignDict.get, reverse=True)]
        # empty the dictionary and fill it again with the size-sorted one
        withinAlignDict.clear()
        withinAlignDict = {tpl[0]: tpl[1] for tpl in s}
        del s

        # set counters to 0
        for sp in withinAlignDict:
            withinAlignDict[sp] = [0, None, None]

        # fill the dict with required species
        for pair in requiredPairsDict:
            tmpA, tmpB = pair.split("-", 1)
            # increment the counters
            withinAlignDict[tmpA][0] += 1
            withinAlignDict[tmpB][0] += 1

        sys.stdout.write(f"\nPredicting {len(requiredPairsDict)} ortholog tables...")
        # calculate cpu-time for orthology inference
        orthology_start = time.perf_counter()

        ##### USE PREPROCESSING ####
        # This parameter have a big impact on the number of orthologs predicted
        # It could be relaxed but not too much
        # HACK: restore the oginal value if required
        # segOverlapCutoff: float = 0.50 # Original conservative value
        segOverlapCutoff: float = 0.20

        # The actual matching segments must cover this of this match of the matched sequence
        # For example for a matched sequence 70 bps long, segments 1-15 and 50-70 gives a total coverage of 35, which is 50% of total.
        # HACK: restore the oginal value if required
        # segCoverageCutoff: float = 0.25 # Original conservative value
        segCoverageCutoff: float = 0.20
        # load the required within alignments in parallel
        inpyranoid.preprocess_within_alignments_parallel(withinAlignDict, alignDir=alignDir, threads=threads, covCoff=segCoverageCutoff, overlapCoff=segOverlapCutoff, minBitscore=minBitscore, compressed=compress, debug=debug)
        # Predict orthologs
        workers.perform_parallel_orthology_inference_shared_dict(requiredPairsDict, inDir, outDir=tblDir, sharedDir=alignDir, sharedWithinDict=withinAlignDict, minBitscore=minBitscore, confCutoff=confCutoff, lenDiffThr=lenDiffThr, threads=threads, compressed=compress, debug=debug)
        sys.stdout.write(f"\nOrtholog tables creation elapsed time (seconds):\t{round(time.perf_counter() - orthology_start, 3)}\n")
    # return the paths for species and pairs files
    # sys.exit("DEBUG: ortholog_detection.run_sonicparanoid2_multiproc_essentials")
    return (spFile, spPairsFile, requiredPairsDict)
