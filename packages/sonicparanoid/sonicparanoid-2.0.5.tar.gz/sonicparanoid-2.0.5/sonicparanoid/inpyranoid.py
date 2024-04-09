"""
This module is used to perform orthology prediction from
alignment files formatted the way inparanoid does.
"""

import os
import sys
import copy
from math import pow
from timeit import default_timer as timer
from collections import OrderedDict
from typing import Dict, List, Set, Tuple, OrderedDict
from numpy import array
import multiprocessing as mp
import queue

# Local imports
from sonicparanoid import sys_tools as systools
# import Cython module for orthology inference
from sonicparanoid import inpyranoid_c



__module_name__ = "InPyranoid"
__source__ = "inpyranoid.py"
__author__ = "Salvatore Cosentino"
#__copyright__ = ""
__license__ = "GPL"
__version__ = "2.0"
__maintainer__ = "Cosentino Salvatore"
__email__ = "salvo981@gmail.com"


##### FUNCTIONS #####
def info():
    """This module is used to execute mmseqs and related tools it also include some functions to format the output output."""
    print("MODULE NAME:\t%s"%__module_name__)
    print("SOURCE FILE NAME:\t%s"%__source__)
    print("MODULE VERSION:\t%s"%__version__)
    print("LICENSE:\t%s"%__license__)
    print("AUTHOR:\t%s"%__author__)
    print("EMAIL:\t%s"%__email__)



def consume_alignment_preproc(jobs_queue, results_queue, alignDir, sharedWithinDict, covCoff=0.25, overlapCoff=0.5, minBitscore=40, compressed=False):
    """Preprocess a single alignment preproc step"""
    while True:
        sp = jobs_queue.get(block=True, timeout=None)
        if sp is None:
            break

        # In order to reduce the number of files stored in a single directory
        # each table should be stored in a directory named after the leftmost species in the pair
        # For example, given the tables 1-2, 1-3, 2-3 this will be stored as follows:
        # 1-2 and 1-3 are stored in '1', while 2-3 is stored in '2'
        # Will contain the directory in which the ortholog table should be stored
        tblPath: str = os.path.join(alignDir,  f"{sp}/{sp}-{sp}") # the leftmost species names the output dir
        # set the length dictionary to a new one for now
        lenDictA:Dict[str, int] = {}

        # preprocess the alignment file
        if compressed:
            preprocDict, lenDictA = inpyranoid_c.preprocess_within_align_compressed(tblPath, lenDictA, covCoff=covCoff, overlapCoff=overlapCoff, minBitscore=minBitscore, debug=False)
        else:
            preprocDict, lenDictA = inpyranoid_c.preprocess_within_align(tblPath, lenDictA, covCoff=covCoff, overlapCoff=overlapCoff, minBitscore=minBitscore, debug=False)

        # add the preprocessed information in the shared dictionary
        if not sp in sharedWithinDict:
            sys.exit(f"ERROR: the species {sp} must be in the shared dictionary")
        # return the dictionaries
        results_queue.put((sp, preprocDict, lenDictA))
        # sys.exit("DEBUG@inpyranoid::consume_alignment_preproc")



def cluster_orthologs(ortoCandAB: Dict[str, int], ortoA, hitsAinA: OrderedDict[str, OrderedDict[str, int]], scoresAA, lenDictA, bestscoreAB: OrderedDict[str, int], ortoB, hitsBinB: OrderedDict[str, OrderedDict[str, int]], scoresBB, lenDictB, bestscoreBA: OrderedDict[str, int], confCutoff: float = 0.05, lenDiffThr: float = 0.5, debug: bool = False) -> Tuple[Dict[str, Dict[str, OrderedDict[str, float]]], Dict[str, None], Dict[str, None]]:
    """Find paralogs and create final clusters."""
    if debug:
        print(f"\ncluster_orthologs :: START")
        print(f"Candidate ortholog pairs:\t{len(ortoCandAB)}")
        print(f"Hits of A in A:\t{len(hitsAinA)}")
        print(f"Scores for AA pairs:\t{len(scoresAA)}")
        print(f"Sequence lengths for A:\t{len(lenDictA)}")
        print(f"Best scores for AB pairs:\t{len(bestscoreAB)}")
        print(f"Hits of B in B:\t{len(hitsBinB)}")
        print(f"Scores for BB pairs:\t{len(scoresBB)}")
        print(f"Sequence lengths for B:\t{len(lenDictB)}")
        print(f"Best scores for BA pairs:\t{len(bestscoreBA)}")
        print(f"Paralog confidence cutoff:\t{str(confCutoff)}")
        print(f"Length difference filtering threshold:\t{str(lenDiffThr)}")

    # these are genes that are found with confidence 1.0 (the core orthologs)
    newOrtoA: Dict[str, None] = {}
    newOrtoB: Dict[str, None] = {}
    oA = oB = ""
    oScore: int = 0
    bestScPair: int = 0
    oPair: str = ""
    withinHitsAADict: OrderedDict[str, int] = OrderedDict()
    withinHitsBBDict: OrderedDict[str, int] = OrderedDict()
    # Output dictionary with clusters
    earlyClstrDict: Dict[str, Dict[str, OrderedDict[str, float]]] = {} # will contain a dictionary for A and B elements of the clusters
    # For example, for the pair oA1-oB1 it will contain a dictionary with orthologs and paralogs for both A and B
    # the dictionaries have scores as values so that they can be easily sorted in the final clustering steps
    #start reading the candindates
    # cntFindP = cntNoP = 0
    for oPair in ortoCandAB:
        # print(oPair)
        # print(type(ortoCandAB[oPair]))
        # print(ortoCandAB[oPair])
        oA, oB = oPair.split("!", 1)
        # extract score
        oScore = ortoCandAB[oPair]
        #get best score for the ortholog pair
        bestScPair = bestscoreAB[oPair]
        # Reset ordered dictionaries
        withinHitsAADict.clear()
        withinHitsBBDict.clear()
        # check first the withinhits are available
        if oA in hitsAinA:
            withinHitsAADict = hitsAinA[oA]
            # print(type(withinHitsAADict))
            # print(withinHitsAADict)
        if oB in hitsBinB:
            withinHitsBBDict = hitsBinB[oB]
            # print(type(withinHitsBBDict))
            # print(withinHitsBBDict)
        # add the ortholog pair to the clusters
        if not oPair in earlyClstrDict:
            earlyClstrDict[oPair] = {}
            earlyClstrDict[oPair][oA] = OrderedDict()
            earlyClstrDict[oPair][oB] = OrderedDict()
        else:
            sys.exit(f"Ortholog pair {oPair} was already in the cluster list")
        # search for orthologs only if the the within hits for AA and BB are available
        # if (len(withinHitsAADict)>0) and (len(withinHitsBBDict)>0):
        if (withinHitsAADict is not None) and (withinHitsBBDict is not None):
            # cntFindP += 1
            # search paralogs for A
            inpyranoid_c.find_paralogs(oA, withinHitsAADict, oScore, bestScPair, scoresAA, newOrtoA, ortoA, earlyClstrDict, oPair, lenDictX=lenDictA, confCutoff=confCutoff, lenDiffThr=lenDiffThr, debug=debug)
            # search paralogs for B
            inpyranoid_c.find_paralogs(oB, withinHitsBBDict, oScore, bestScPair, scoresBB, newOrtoB, ortoB, earlyClstrDict, oPair, lenDictX=lenDictB, confCutoff=confCutoff, lenDiffThr=lenDiffThr, debug=debug)
        else: # otherwise only the add the ortholog pair with confidence 1.0
            # cntNoP += 1
            #print("This is the simple case!")
            earlyClstrDict[oPair][oA] = OrderedDict([ (oA, 1.) ])
            earlyClstrDict[oPair][oB] = OrderedDict([ (oB, 1.) ])
    # print("cntNoP:", cntNoP)
    # print("cntFindP:", cntFindP)
    # sys.exit("DEBUG: ortholog clustering")
    return (earlyClstrDict, newOrtoA, newOrtoB)



def infer_orthologs_shared_dict(pathA, pathB, alignDir=os.getcwd(), outDir=os.getcwd(), sharedWithinDict=None, minBitscore=40, confCutoff=0.05, lenDiffThr=0.5, compressed=False, debug=False):
    """
    Infer orthology for the two input proteomes.
    Shared dictionaries are used to save processing time.
    """
    if debug:
        print("\ninfer_orthologs_shared_dict :: START")
        print(f"Input proteome 1: {pathA}")
        print(f"Input proteome 2: {pathB}")
        print(f"Outdir: {outDir}")
        print(f"Alignments dir: {alignDir}")
        print(f"Species with shared info:\t{len(sharedWithinDict)}")
        print(f"Minimum bitscore:\t{minBitscore}")
        print(f"Confidence cutoff for paralogs:\t{confCutoff}")
        print(f"Length difference filtering threshold:\t{lenDiffThr}")
        print(f"Compressed alignment files:\t{compressed}")
    #sys.exit('DEBUG :: infer_orthologs_shared_dict :: START')
    # start timer
    start_time = timer()
    #check the existence of the input file
    if not os.path.isfile(pathA):
        sys.stderr.write(f"ERROR: The first input file ({pathA}) was not found, please provide the path to a valid file.\n")
        sys.exit(-2)
    if not os.path.isfile(pathB):
        sys.stderr.write(f"ERROR: The second input file ({pathB}) was not found, please provide the path to a valid file.\n")
        sys.exit(-2)
    #create the output file name
    species1 = os.path.basename(pathA)
    species2 = os.path.basename(pathB)
    # create path names
    pathAB = os.path.join(alignDir, f"{species1}/{species1}-{species2}")
    if not os.path.isfile(pathAB):
        sys.stderr.write(f"ERROR: the alignment file ({pathAB}) was not found, it is required to perform orthology inference.\n")
        sys.exit(-2)
    pathBA = os.path.join(alignDir, f"{species2}/{species2}-{species1}")
    if not os.path.isfile(pathBA):
        sys.stderr.write(f"ERROR: the alignment file ({pathBA}) was not found, it is required to perform orthology inference.\n")
        sys.exit(-2)
    if debug:
        print(f"AB:\t{pathAB}")
        print(f"BA:\t{pathBA}")
    # sys.exit("DEBUG :: infer_orthologs_shared_dict :: after alignments file check")

    # Match area should cover at least this much of longer sequence.
    # Match area is defined as length from the start of first segment to end of last segment
    # i.e segments 1-10, 20-25, and 80-90 gives a match length of 90.

    # This parameter have a big impact on the number of orthologs predicted
    # It could be relaxed but not too much
    # HACK: restore the oginal value if required
    # segOverlapCutoff: float = 0.50 # Original conservative value
    segOverlapCutoff: float = 0.20 # Original conservative value

    # The actual matching segments must cover this of this match of the matched sequence
	# For example for a matched sequence 70 bps long, segments 1-15 and 50-70 gives a total coverage of 35, which is 50% of total.
    # HACK: restore the oginal value if required
    # segCoverageCutoff: float = 0.25 # Original conservative value
    segCoverageCutoff: float = 0.20

    ####### LOAD BETWEEN PROTEOMES ALIGNMENTS ##########
    #start timer
    load_between_proteomes_scores_start = timer()
    if compressed:
        # Cython version (for compressed files)
        scoresAB, hitsAinB, scoresBA, hitsBinA, lenDictAbetween, lenDictBbetween = inpyranoid_c.load_between_proteomes_scores_compressed(pathAB, pathBA, covCoff=segCoverageCutoff, overlapCoff=segOverlapCutoff, minBitscore=minBitscore, debug=debug)
    else:
        # Cython version (for flat files)
        scoresAB, hitsAinB, scoresBA, hitsBinA, lenDictAbetween, lenDictBbetween = inpyranoid_c.load_between_proteomes_scores_fast(pathAB, pathBA, covCoff=segCoverageCutoff, overlapCoff=segOverlapCutoff, minBitscore=minBitscore, debug=debug)

    load_between_proteomes_scores_end = timer()
    if debug:
        print(f"\nExec time to load scores between proteomes:\t{round(load_between_proteomes_scores_end - load_between_proteomes_scores_start, 3)}\n")
    ##################################################
    # sys.exit("DEBUG :: infer_orthologs_shared_dict :: after loading between proteome scores.")
    #equalize between proteome scores
    #scoresAB, scoresBA = equalize_AB_and_BA_scores(scoresAB, scoresBA, debug=debug)
    #equalize fast mode
    scoresAB, scoresBA = inpyranoid_c.equalize_AB_and_BA_scores_fast(scoresAB, scoresBA, debug=debug)
    #print(len(scoresAB), len(scoresBA))
    equalize_timer_end = timer()
    if debug:
        print(f"\nequalize_AB_and_BA_scores exec time:\t{round(equalize_timer_end - load_between_proteomes_scores_end, 3)}\n")
    #load best hits for AB and BA
    bestscoreAB, bestscoreBA = load_besthits_between_proteomes(hitsAinB, hitsBinA, scoresAB, scoresBA, debug=debug)[2:]
    load_besthits_timer_end = timer()
    if debug:
        print(f"\nload_besthits_between_proteomes exec time:\t{round(load_besthits_timer_end - equalize_timer_end, 3)}\n")
    # sys.exit("DEBUG :: infer_orthologs_shared_dict :: after load_besthits_between_proteomes.")
    #find candidate orthologs
    ortoA, ortoB, ortoCandAB = find_orthologs_between_proteomes_bestscores(scoresAB, scoresBA, bestscoreAB, bestscoreBA, debug=debug)
    find_orthologs_timer_end = timer()
    if debug:
        print(f"\nfind_orthologs_between_proteomes_bestscores exec time:\t{round(find_orthologs_timer_end - load_besthits_timer_end, 3)}\n")
    # sys.exit("DEBUG :: infer_orthologs_shared_dict :: after find_orthologs_between_proteomes_bestscores.")

    # Use a single timer variable
    t0 = t1 = 0.
    t0 = find_orthologs_timer_end

    ####### LOAD WITHIN PROTEOMES ALIGNMENTS ##########
    # process AA within alignments
    preprocAADict = sharedWithinDict[species1][1]
    lenDictA = sharedWithinDict[species1][2]
    scoresAA, hitsAinA, lenDictA = postprocess_within_align(species1, preprocAADict, ortoA, lenDictA, lenDictAbetween, debug=False)

    # process BB within alignments
    preprocBBDict = sharedWithinDict[species2][1]
    lenDictB = sharedWithinDict[species2][2]
    scoresBB, hitsBinB, lenDictB = postprocess_within_align(species2, preprocBBDict, ortoB, lenDictB, lenDictBbetween, debug=False)
    if debug:
        t1 = timer()
        print(f"\nload within proteomes scores exec time:\t{round(t1 - t0, 3)}\n")
        t0 = t1
    # sys.exit('DEBUG :: infer_orthologs_shared_dict :: after postprocess_within_align BB ({:s})'.format(species2))

    #####################################################

    # NOTE: this only for testing
    '''
    #### write rejected inparalogs ####
    # set path to the file with rejected inparalogs
    rejctFileName = '{:s}-{:s}.difflen.tsv'.format(species1, species2)
    rejctFilePath = os.path.join(outDir, rejctFileName)
    #sys.exit('DEBUG :: inpyranoid :: infer_orthologs_shared_dict')

    orthoClstrs, coreOrtoA, coreOrtoB = cluster_orthologs_write_rejected(rejctFilePath, '{:s}_{:s}'.format(species1, species2), ortoCandAB, ortoA, hitsAinA, scoresAA, lenDictA, bestscoreAB, ortoB, hitsBinB, scoresBB, lenDictB, bestscoreBA, confCutoff=confCutoff, lenDiffThr=lenDiffThr, debug=debug)
    '''
    ##################

    #### ORIGINAL ####
    #search for paralogs and generate final clusters
    orthoClstrs, coreOrtoA, coreOrtoB = cluster_orthologs(ortoCandAB, ortoA, hitsAinA, scoresAA, lenDictA, bestscoreAB, ortoB, hitsBinB, scoresBB, lenDictB, bestscoreBA, confCutoff=confCutoff, lenDiffThr=lenDiffThr, debug=False)
    if debug:
        t1 = timer()
        print(f"\ncluster_orthologs exec time:\t{round(t1 - t0, 3)}\n")
        t0 = t1

    # sys.exit("DEBUG :: infer_orthologs_shared_dict :: after cluster_orthologs.")
    # output prefix
    outName = f"{species1}-{species2}.umerged"
    # write output files
    tblOutPath, repeatDict, mergeableClstrs = write_inpyranoid_output_simple(orthoClstrs, ortoCandAB, coreOrtoA, coreOrtoB, outName, outDir=outDir, debug=debug)
    if debug:
        t1 = timer()
        print(f"\nwrite_inpyranoid_output_simple exec time:\t{round(t1 - t0, 3)}\n")
        t0 = t1

    # remove not required data structures
    del orthoClstrs, ortoCandAB, coreOrtoA, coreOrtoB
    del scoresAA, hitsAinA, scoresBB, hitsBinB, scoresAB, scoresBA
    del hitsAinB, hitsBinA, lenDictAbetween, lenDictBbetween
    # call merge only when required
    repCnt: int = len(repeatDict)
    if repCnt > 0:
        merge_and_write_inpyranoid_output(tblOutPath, repeatDict, mergeableClstrs, debug=debug)
    else:
        # print("\nSkip merge...")
        # print(tblOutPath)
        # rename the output table to remove ".unmerged"
        os.rename(tblOutPath, tblOutPath.rsplit(".", 1)[0])
    # remove redundant objects
    del repeatDict, mergeableClstrs
    if debug:
        t1 = timer()
        print(f"\nmerge_and_write_inpyranoid_output exec time:\t{round(t1 - t0, 3)}")
        print(f"\ntotal execution time:\t{round(t1 - start_time, 3)}\n")
    # sys.exit("DEBUG :: infer_orthologs_shared_dict :: END.")



def find_orthologs_between_proteomes_bestscores(scoresAB, scoresBA, bestscoreAB, bestscoreBA, debug=False):
    """Find candidate orthologs and sort them by score and id."""
    if debug:
        print(f"\nfind_orthologs_between_proteomes_bestscores :: START")
        print(f"AB scores:\t{len(scoresAB)}")
        print(f"BA scores:\t{len(scoresBA)}")
        print(f"Best scores AB:\t{len(bestscoreAB)}")
        print(f"Best scores BA:\t{len(bestscoreBA)}")
    ortoCandAB = OrderedDict() # will contain the candidate orthologs for AB
    ortoA = {} # will contain the candidate orthologs for A
    ortoB = {} # will contain the candidate orthologs for B
    scAB = scBA = 0
    tmpQ = tmpM = kBA = ""
    # USE BEST SCORES
    ##### each hit is an ortholog if q and hit are best hits "have a best score" in both AB and BA #####
    for kAB in bestscoreAB:
        #print("QUERY:\t%s"%q)
        scAB = int(bestscoreAB[kAB])
        tmpQ, tmpM = kAB.split("!")
        kBA = f"{tmpM}!{tmpQ}"
        if kBA in bestscoreBA:
            scBA = int(bestscoreBA[kBA])
            if scBA == scAB:
                ortoCandAB[kAB] = scoresAB[kAB]
                ortoA[tmpQ] = None
                ortoB[tmpM] = None
            else:
                sys.stderr.write("\nERROR: Scores are different!")
                sys.exit(-8)
    #sort the candidate orthologs by score
    tplList = [(k, ortoCandAB[k]) for k in sorted(ortoCandAB, key=ortoCandAB.get, reverse=True)]
    ortoCandAB = OrderedDict() #reset the dictionary
    for tpl in tplList:
        ortoCandAB[tpl[0]] = tpl[1]
    # sort orthlogs for A by key
    ortoA = OrderedDict(sorted(ortoA.items()))
    ortoB = OrderedDict(sorted(ortoB.items()))
    if debug:
        print(f"Candidate orthologs for AB:\t{len(ortoCandAB)}")
        print(f"Candidate orthologs for A:\t{len(ortoA)}")
        print(f"Candidate orthologs for B:\t{len(ortoB)}")
    return (ortoA, ortoB, ortoCandAB)



def load_besthits_between_proteomes(hitsAB, hitsBA, scoresAB, scoresBA, debug=False):
    """Load best hits for each query from AB and BA alignments."""
    if debug:
        print("load_besthits_between_proteomes :: START")
        print(f"Hits A in B:\t{len(hitsAB)}")
        print(f"Hits B in A:\t{len(hitsBA)}")
        print(f"Scores AB:\t{len(scoresAB)}")
        print(f"Scores BA:\t{len(scoresBA)}")
    bestHitsAB = OrderedDict()
    bestHitsBA = OrderedDict()
    bestscoreAB = OrderedDict()
    bestscoreBA = OrderedDict()
    greyZone = 0
    babHitsCnt = bbaHitsCnt = 0
    #calculate best hits for AB
    for q in hitsAB:
        qMatches = hitsAB[q]
        matches = list(qMatches.keys())
        abHitId = f"{q}!{matches[0]}"
        bestScore = scoresAB[abHitId] #could be deleted!
        #### include both keys
        bestscoreAB[abHitId] = bestScore
        #add the match to the besthit dictionary for q
        bestHitsAB[q] = [matches[0]] #first match [the one with highest score]
        babHitsCnt += 1
        #start from the second hit in the matches list
        for i in range(1, len(matches)):
            tmpHitId = f"{q}!{matches[i]}"
            if (bestScore - scoresAB[tmpHitId] <= greyZone): #then add the correspondig match to the best matches
                bestHitsAB[q].append(matches[i])
                babHitsCnt += 1
            else: #otherwise exit the loop and go to next query
                break

    #calculate best hits for BA
    for q in hitsBA:
        qMatches = hitsBA[q]
        matches = list(qMatches.keys())
        # mScores = list(qMatches.values())
        baHitId = f"{q}!{matches[0]}"
        bestScore = scoresBA[baHitId]
        #### include both keys
        bestscoreBA[baHitId] = bestScore
        #add the match to the besthit dictionary for q
        bestHitsBA[q] = [matches[0]] #first match [the one with highest score]
        bbaHitsCnt += 1
        #start from the second hit in the matches list
        for i in range(1, len(matches)):
            tmpHitId = f"{q}!{matches[i]}"
            if (bestScore - scoresBA[tmpHitId] <= greyZone): #then add the correspondig match to the best matches
                bestHitsBA[q].append(matches[i])
                bbaHitsCnt += 1
            else: #otherwise exit the loop and go to next query
                break
    if debug:
        print(f"Best hits loaded for AB:\t{babHitsCnt}")
        print(f"Best hits loaded for BA:\t{bbaHitsCnt}")
        print(f"bestscoresAB:\t{len(bestscoreAB)}")
        print(f"bestscoresBA:\t{len(bestscoreBA)}")
    return (bestHitsAB, bestHitsBA, bestscoreAB, bestscoreBA)



def preprocess_within_alignments_parallel(withinPreprocDict, alignDir, threads=4, covCoff=0.25, overlapCoff=0.5, minBitscore=40, compressed:bool=False, debug:bool=False):
    """Preprocess the within alignments in parallel."""
    # withinPreprocDict contains dictionaries
    # with hits and scores for withing alignments

    # species names
    spList = list(withinPreprocDict.keys())
    # create the queue and start adding
    load_within_queue: mp.queues.Queue = mp.Queue(maxsize=len(spList) + threads)

    # fill the queue with the processes, as the species
    for sp in spList:
        sys.stdout.flush()
        load_within_queue.put(sp)

    # add flags for eneded jobs
    for i in range(0, threads):
        sys.stdout.flush()
        load_within_queue.put(None)

    # Queue to contain the execution time
    results_queue: mp.queues.Queue = mp.Queue(maxsize=len(spList))

    # call the method inside workers
    runningJobs = [mp.Process(target=consume_alignment_preproc, args=(load_within_queue, results_queue, alignDir, withinPreprocDict, covCoff, overlapCoff, minBitscore, compressed)) for i_ in range(threads)]

    for proc in runningJobs:
        proc.start()

    while True:
        try:
            spDone, preprocDictTmp, lenDictTmp = results_queue.get(False, 0.01)
            # add the information to the shared dictionary
            withinPreprocDict[spDone][1] = preprocDictTmp
            withinPreprocDict[spDone][2] = lenDictTmp
            if debug:
                sys.stdout.write(f"\nPreprocessing of within-alignment for {spDone} done!")
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



def postprocess_within_align(sp, preprocWithinDict, ortoA, lenDictA, lenDictAbetween, debug=False):
    """Postprocess within alignmets and create dictionary with scores and hits."""
    if debug:
        print("\npostprocess_within_align :: START")
        print(f"Within alignment for species:\t{sp}")
        print(f"Within align count\t{len(preprocWithinDict)}")
        print(f"Orthologs from {sp}:\t{len(ortoA)}")
        print(f"Sequence lengths in between alignments:\t{len(lenDictAbetween)}")

    #create the dictionaries to store the ids and scores
    scoreAA = OrderedDict()
    hitsAinA = OrderedDict()
    isNotOrtoA = okCntAA = tmpScore = 0
    q = s = ""

    # read the file and load hits for AA
    for hitid in preprocWithinDict:
        q, s = hitid.split("!", 1)
        #skip if there is an ortholog associated to the corresponding query sequence
        if q not in ortoA:
            isNotOrtoA += 1
            continue
        okCntAA += 1
        #now add the hit and its score to the corresponding dictionaries
        hitId = f"{q}!{s}"
        #save the score
        tmpScore = preprocWithinDict[hitid]
        scoreAA[hitId] = tmpScore
        if not q in lenDictAbetween:
            lenDictAbetween[q] = lenDictA[q]
        if s != q:
            if not s in lenDictAbetween:
                lenDictAbetween[s] = lenDictA[s]

        #add match and scores for each query sequence
        if not q in hitsAinA:
            hitsAinA[q] = OrderedDict()
        hitsAinA[q][s] = tmpScore

    #debug = True
    if debug:
        print(f"\nSequence lengths loaded for {sp}:\t{len(lenDictA)}")
        print(f"Sequence lengths to be used for {sp}:\t{len(lenDictAbetween)}")
        print(f"Loaded hits for {sp}-{sp}:\t{len(scoreAA)}")
        print(f"Not a ortholog:\t{isNotOrtoA}")
        print(f"OK alignments {sp}-{sp}:\t{okCntAA}")
        print(f"Queries from {sp} with hits in {sp}:\t{len(list(hitsAinA.keys()))}")
    #sys.exit('DEBUG :: inpyranoid :: postprocess_within_align')
    # return dictionaries
    return (scoreAA, hitsAinA, lenDictAbetween)



''' # Remove in future releases
def write_inpyranoid_output(pairClstrDict, ortoScoreDict, coreOrtoA, coreOrtoB, outName, outDir=os.getcwd(), writeTbl=True, writeRelations=False, debug=False):
    """Write output clusters for proteome pairs."""
    if debug:
        print('\nwrite_inpyranoid_output :: START')
        print('Proteome pair clusters: %s'%len(pairClstrDict))
        print('Dictionary with ortholog scores: %s'%len(ortoScoreDict))
        print('CORE ortholog for A: %s'%len(coreOrtoA))
        print('CORE ortholog for B: %s'%len(coreOrtoB))
        print('Ouput name suffix:\t%s'%outName)
        print('Ouput directory:\t%s'%outDir)
        print('Write table:\t%s'%writeTbl)
        print('Write relations:\t%s'%writeRelations)
    # check that the output name is in the correct format
    if not '-' in outName:
        print('ERROR: the output name must be a string in the format species1-species2\n')
        sys.exit(-3)
    #extract species names
    sp1, sp2 = outName.split('-', 1)
    # set output paths
    # table output
    outTblPath = outTblFd = None
    if writeTbl:
        outTblPath = os.path.join(outDir, 'table.{:s}'.format(outName))
        outTblFd = open(outTblPath, 'w')
        outTblFd.write('OrtoId\tScore\tOrtoA\tOrtoB\n')
    # relations
    outRelPath = outRelFd = None
    if writeRelations:
        outRelPath = os.path.join(outDir, 'relations.{:s}'.format(outName))
        outRelFd = open(outRelPath, 'w')
    # sql
    outSqlPath = os.path.join(outDir, 'sqltable.{:s}'.format(outName))
    outSqlFd = open(outSqlPath, 'w')

    # write the files
    clstrCnt = 0
    for gPair in pairClstrDict:
        clstrCnt += 1
        clstrScore = ortoScoreDict[gPair]
        gA, gB = gPair.split('!', 1)
        tmpStr = ''
        # out line start (will be used for both table and sql output formats)
        outLnStart = '%d\t%d\t'%(clstrCnt, clstrScore)

        # write first part
        for gene, conf in pairClstrDict[gPair][gA].items():
            # NOTE: Maybe this never happens
            if conf < 1:
                if gene in coreOrtoA: # skip fake paralogs
                    continue
            if outTblFd:
                tmpStr += '%s %s '%(gene, str(conf))
            # write the sql file
            outSqlFd.write('%s%s\t%s\t%s\n'%(outLnStart, sp1, str(conf), gene))
        if outTblFd:
            outTblFd.write('%s%s\t'%(outLnStart, tmpStr[:-1]))
        # write the second part of the cluster
        tmpStr = ''
        for gene, conf in pairClstrDict[gPair][gB].items():
            if conf < 1:
                if gene in coreOrtoB: # skip fake paralogs
                    continue
            if outTblFd:
                tmpStr += '%s %s '%(gene, str(conf))
            # write the sql file
            outSqlFd.write('%s%s\t%s\t%s\n'%(outLnStart, sp2, str(conf), gene))
        if outTblFd:
            outTblFd.write('%s\n'%(tmpStr[:-1]))

    # close files
    outSqlFd.close()
    if outTblFd:
        outTblFd.close()
    if outRelFd:
        outRelFd.close()
'''



def write_inpyranoid_output_simple(pairClstrDict: Dict[str, Dict[str, OrderedDict[str, float]]], ortoScoreDict: Dict[str, int], coreOrtoA: Dict[str, None], coreOrtoB: Dict[str, None], outName: str, outDir: str, debug: bool = False):
    """Write output clusters for proteome pairs."""
    if debug:
        print(f"\nwrite_inpyranoid_output_simple :: START")
        # Contains the clusters for each pair of orhtologs
        # including the inparalogs
        # 1.479!2.2700 -> {'1.479': OrderedDict([('1.479', 1.0)]), '2.2700': OrderedDict([('2.2700', 1.0), ('2.2805', 0.05)])}
        print(f"Proteome pair clusters:\t{len(pairClstrDict)}")
        # Contains the score for each cluster,
        # 1.284!2.2391 -> 210
        print(f"Dictionary with ortholog scores:\t{len(ortoScoreDict)}")
        print(f"CORE ortholog for A:\t{len(coreOrtoA)}")
        print(f"CORE ortholog for B:\t{len(coreOrtoB)}")
        print(f"Ouput name suffix:\t{outName}")
        print(f"Ouput directory: {outDir}")
    # check that the output name is in the correct format
    if not "-" in outName:
        print('ERROR: the output name must be a string in the format species1-species2\n')
        sys.exit(-3)

    # catch repetitions
    # will contain gene ids that where repeated
    # and will associate to each the set of cluster ids with the repetitions
    repeatDict: Dict[str, Set[str]] = {}
    # will contain genes from A and B, to find repetitions
    # sys.exit("DEBUG: inpayranoid::write_inpyranoid_output_simple")
    aDict: Dict[str, str] = {}
    bDict: Dict[str, str] = {}
    # will have clstr ids as keys and the A, and B parts as values
    mergeableClstrs: Dict[str, List[str]] = {}

    # set output paths
    # table output
    outTblPath: str = os.path.join(outDir, f"table.{outName}")
    outTblFd = open(outTblPath, "w")
    outTblFd.write("OrtoId\tScore\tOrtoA\tOrtoB\n")
    
    # write the files
    clstrScore: int = 0
    clstrCnt: int = 0
    tmpStr: str = ""
    clstrId: str = ""
    for gPair in pairClstrDict:
        clstrCnt += 1
        clstrScore = ortoScoreDict[gPair]
        gA, gB = gPair.split("!", 1)
        tmpStr = ""
        # out line start (will be used for both table and sql output formats)
        outLnStart: str = f"{clstrCnt}\t{clstrScore}\t"
        # convert to string
        clstrId = str(clstrCnt)

        # write first part
        for gene, conf in pairClstrDict[gPair][gA].items():
            if conf < 1:
                # TO DO: check if it ok to skip these paralogs
                if gene in coreOrtoA: # skip fake paralogs
                    continue
            tmpStr += f"{gene} {conf} "
            # make sure the ortholog is not repeated
            if gene in aDict:
                if not gene in repeatDict:
                    repeatDict[gene] = {aDict[gene], clstrId}
                else:
                    repeatDict[gene].add(clstrId)
            else:
                aDict[gene] = clstrId

        # This cluster will be filtered later
        mergeableClstrs[clstrId] = [str(clstrScore), tmpStr[:-1]]

        outTblFd.write(f"{outLnStart}{tmpStr[:-1]}\t")
        # write the second part of the cluster
        tmpStr = ""
        for gene, conf in pairClstrDict[gPair][gB].items():
            if conf < 1:
                if gene in coreOrtoB: # skip fake paralogs
                    continue
            tmpStr += f"{gene} {conf} "
            # make sure the ortholog is not repeated
            if gene in bDict:
                if not gene in repeatDict:
                    repeatDict[gene] = {bDict[gene], clstrId}
                else:
                    repeatDict[gene].add(clstrId)
            else:
                bDict[gene] = clstrId

        # Add the right part of the cluster to the cluster list
        mergeableClstrs[clstrId].append(tmpStr[:-1])
        # Finish writing the cluster and add new line
        outTblFd.write(f"{tmpStr[:-1]}\n")

    # close files
    outTblFd.close()
    # retun the path to the output file
    return (outTblPath, repeatDict, mergeableClstrs)



def filter_mergeable_sets(repeatDict: Dict[str, Set[str]], mergeCandidateDict: Dict[str, List[str]], debug: bool = False) -> Tuple[List[Set[int]], Dict[str, List[str]], Dict[str, None]]:
    """
    Merge sets to dictionaries.
    mergeCandidateDict contains cluster ids as keys,
    and as values, a list with, cluster score, part A, and part B of the cluster.
    """
    # create string representations sets of clusters
    # and associate the size to each string repr
    setsDict: Dict[str, int] = {}
    tmpList: List[int] = []
    tmpStr: str = ""

    #  HACK: The change below solves the problem with inconsistent number of OGs
    for k, val in repeatDict.items():
        tmpList = [int(x) for x in val]
        tmpStr = '_'.join([str(x) for x in sorted(tmpList)])
        setsDict[tmpStr] = len(tmpList)

    # SORT the dictionary by VALUE
    s = [(k, setsDict[k]) for k in sorted(setsDict, key=setsDict.get, reverse=True)]
    #setsDict.clear()
    del setsDict, tmpList
    setsList: List[Set[int]] = []
    for k, v in s:
        # convert to a set of integers
        setsList.append(set([int(x) for x in k.split('_')]))
    del s
    debug = False
    # if debug:
    #     print("\n##### Mergeable sets ####")
    #     print(setsList)

    # list to contain the sets
    toMerge: List[Set[int]] = []
    notMerged: List[Set[int]] = []
    tmpSet: Set[int] = set()
    # case in which only a set of cluster is avaliable
    # we just merge these clusters
    if len(setsList) == 1:
        toMerge.append(setsList[0])
    else:
        # first set (the biggest in size)
        while len(setsList) > 1:
            notMerged.clear()
            firstSet = setsList[0]
            toMerge.append(firstSet)
            #print(toMerge)
            for tmpSet in setsList[1:]:
                # convert to set
                if not tmpSet.issubset(firstSet):
                    notMerged.append(tmpSet)
            # update setsList with the set of not merged sets
            setsList.clear()
            setsList = list(notMerged)
            #print(len(setsList))

    # Add the last set from notMerged
    # NOTE: this allows the last set to also be added,
    # while previously it was lost causing some orthologs to
    # appear on different clusters
    if len(notMerged) == 1:
        toMerge.append(notMerged[0])

    if debug:
        print("##### BEFORE PRUNING #####")
        print(f"toMerge len:\t{len(toMerge)}")
        # print(f"toMerge:\t{toMerge}")
        # print(f"notMerged:\t{notMerged}")
        print("##########################")
    notMerged.clear()

    # now process the sets to be merged
    # and make sure that intersections between the sets are empty
    setsList.clear()
    setsList = list(toMerge)

    #sys.exit('DEBUG :: filter_mergeable_sets')
    # contains a set as key and the interesction with another set as value
    intersectDict: Dict[str, Set[int]] = {}
    # will contain idx in toMerge list of possible new subsets
    newSubSets: Dict[int, None] = {}
    iterCnt: int = 0
    if debug:
        print("##### START PRUNING #####")
    while len(setsList) > 1:
        iterCnt += 1
        firstSet = setsList[0]
        if debug:
            print(f"len(setsList):\t{len(setsList)}")
            print(f"Iteration:\t{iterCnt}")
            print(f"First set:\t{firstSet}")
        #toMerge.append(firstSet)
        #print(toMerge)
        #sys.exit('DEBUG')
        for idx, tmpSet in enumerate(setsList[1:]):
            # print("pruning internal loop:", tmpSet)
            if len(firstSet) == 1:
                if debug:
                    print("Skip this set...first set is one...")
                break
            elif len(tmpSet) == 1:
                if debug:
                    print("Skip this 1-element set comparison...go to next set...")
                continue

            # calculate the intersections
            intersection = tmpSet.intersection(firstSet)
            # check if there are common elements
            if len(intersection) > 0:
                if tmpSet.issubset(firstSet):
                    if debug:
                        print(f"Skip this set {tmpSet}...is a subset of a bigger set...")
                    newSubIdx = iterCnt + idx
                    newSubSets[newSubIdx] = None
                    continue

                # create a string repr of the set
                sStr = '_'.join([str(x) for x in tmpSet])
                if not sStr in intersectDict:
                    intersectDict[sStr] = intersection
                    # find the index in the toMerge list
                    toMergeIdx = iterCnt + idx
                    #print('\n{:d}\t{:s}\t{:s}'.format(toMergeIdx, sStr, str(intersectDict[sStr])))
                    # remove the cluster with intersections
                    if debug:
                        print(f"Set before updated:\t{toMerge[toMergeIdx]}")
                    toMerge[toMergeIdx] = toMerge[toMergeIdx].difference(intersection)
                    if debug:
                        print(f"Updated set:\t{toMerge[toMergeIdx]}")
                else:
                    if debug:
                        print(f"WARNING: The set {tmpSet} was found to have multiple intersections")
                        print("it will be skipped...")
                    skipIdx = iterCnt + idx
                    newSubSets[skipIdx] = None

        # update setsList with the set of not merged sets
        setsList.clear()
        setsList = list(toMerge[iterCnt:])
        '''
        if debug:
            print(f"\nRemaining iterations:\t{len(setsList)}")
            print("#####################")
        '''

    if debug:
        print("\n########## PRUNING DONE ###########")
        print(f"\ntoMerge before removing single element sets:\t{len(toMerge)}")

    # remove the element with a single cluster from the merge list
    # clusters which could not be merged with other...
    # maybe remove these????
    skipDict: Dict[str, None] = {}
    for i, tmpSet in enumerate(list(toMerge)):
        if len(tmpSet) == 1:
            #skipList.append(tmpSet)
            for clstrId in tmpSet:
                if not str(clstrId) in skipDict:
                    skipDict[str(clstrId)] = None
            # remove from toMerge
            toMerge.remove(tmpSet)
        elif i in newSubSets:
            #skipList.append(el)
            for clstrId in tmpSet:
                if not str(clstrId) in skipDict:
                    skipDict[str(clstrId)] = None
            # remove from toMerge
            toMerge.remove(tmpSet)

    if debug:
        print(f"\ntoMerge final:\t{len(toMerge)}")
        print(f"toMerge:\t{toMerge}")
        print(f"Clusters to be removed:\t{len(skipDict)}\n")

    # will contain a subset of the mergeCandidateDict
    mergeableFinal: Dict[str, List[str]] = {}
    # make sure that all the mergeable clusters appear only one time
    tmpDict: Dict[int, None] = {}
    # just an extra check, but should never happen!
    for tmpSet in toMerge:
        for tmpIntId in tmpSet:
            if not tmpIntId in tmpDict:
                tmpDict[tmpIntId] = None
                # add cluster to the final dictionary with mergeable clusters
                tmpClstrId = str(tmpIntId)
                mergeableFinal[tmpClstrId] = mergeCandidateDict[tmpClstrId]
            else:
                print(f"ERROR: The cluster ID {tmpIntId} was found multiple times in the sets to be merged")
                sys.exit(-5)
    #sys.exit('debug :: filter_mergeable_sets')

    return (toMerge, mergeableFinal, skipDict)



def merge_clusters(toMergeSetList: List[Set[int]], mergeableClusters: Dict[str, List[str]]):
    """Generate strings representing the merged clusters"""
    # will contain the merged clusters
    mergedStack: List[str] = []
    # will contain the ids of the merged clusters
    mergedClstrList: List[str] = []
    clstrIdStr: str = ""
    avgStr: str = ""
    strA: str = ""
    strB: str = ""
    tmpGenes: List[str] = []

    for clstrIdSet in toMergeSetList:
        # for each cluster the genes from A and B will loaded
        # in dictionaries, that will be sorted by max score
        # the average cluster score will be computed
        scList: List[int] = []
        tmpA: Dict[str, float] = {}
        tmpB: Dict[str, float] = {}
        for clstrId in clstrIdSet:
            clstrIdStr = str(clstrId)
            mergedClstrList.append(clstrIdStr)
            sc, a, b = mergeableClusters[clstrIdStr]
            scList.append(int(sc))
            # split the A part and add the elements in tmpA dict
            tmpGenes = a.split(" ")
            for i, gene in enumerate(tmpGenes):
                if i % 2 == 0:
                    # add the gene in the dictionary
                    if not gene in tmpA:
                        tmpA[gene] = round(float(tmpGenes[i + 1]), 3)
            # split the B part and add the elements in tmpB dict
            tmpGenes = b.split(" ")
            for i, gene in enumerate(tmpGenes):
                if i % 2 == 0:
                    # add the gene in the dictionary
                    if not gene in tmpB:
                        tmpB[gene] = round(float(tmpGenes[i + 1]), 3)
        # print info about the merged clusters
        avgSc = str(int(array(scList).mean()))

        # sort the dictionary by value
        tmpSort = [(k, tmpA[k]) for k in sorted(tmpA, key=tmpA.get, reverse=True)]
        tmpA.clear()
        strA = ""
        for k, v in tmpSort:
            strA += f"{k} {v} "
        del tmpSort

        # sort the dictionary by value
        tmpSort = [(k, tmpB[k]) for k in sorted(tmpB, key=tmpB.get, reverse=True)]
        tmpB.clear()
        strB = ""
        for k, v in tmpSort:
            strB += f"{k} {v} "
        del tmpSort

        # remove the final space
        strA = strA[:-1]
        strB = strB[:-1]

        # mergedStack.append('{:s}\t{:s}\t{:s}\n'.format(avgSc, strA, strB))
        mergedStack.append(f"{avgSc}\t{strA}\t{strB}\n")
    return (mergedStack, mergedClstrList)



def merge_and_write_inpyranoid_output(inTbl, repeatDict: Dict[str, Set[str]], mergeableDict: Dict[str, List[str]], debug=False):
    # reduce sets of mergeable clusters
    # print(f"\n### Merging orthologs for table:\t {os.path.basename(inTbl)} ###")
    toMergeSetList, mergeableFinalDict, skipDict = filter_mergeable_sets(repeatDict, mergeableDict, debug=debug)
    del mergeableDict # not needed anymore
    # merge the clusters
    mergedStack, mergedIds = merge_clusters(toMergeSetList, mergeableFinalDict)
    # rewrite cluster table (if required)
    inTbl = inpyranoid_c.rewrite_clusters_c(inTbl=inTbl, mergedClstrs=mergedStack, mergedIds=mergedIds, skipDict=skipDict, debug=False)
