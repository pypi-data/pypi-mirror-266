"""Functions to map input FASTA header with internal IDs."""
import os
import sys
import multiprocessing as mp
from shutil import move, rmtree, copy
from typing import Dict, List, Tuple, Set, TextIO, BinaryIO, Deque
import pickle
import hashlib
from functools import partial

# internal modules
from sonicparanoid import sys_tools as systools



__module_name__ = 'Hdr mapping'
__source__ = 'hdr_mapping.py'
__author__ = 'Salvatore Cosentino'
__license__ = 'GPLv3'
__version__ = '0.6'
__maintainer__ = 'Cosentino Salvatore'
__email__ = 'salvo981@gmail.com'



### FUNCTIONS ####
def info() -> None:
    """Functions to map input FASTA header with internal IDs."""
    print('MODULE NAME:\t%s'%__module_name__)
    print('SOURCE FILE NAME:\t%s'%__source__)
    print('MODULE VERSION:\t%s'%__version__)
    print('LICENSE:\t%s'%__license__)
    print('AUTHOR:\t%s'%__author__)
    print('EMAIL:\t%s'%__email__)



### Worker functions (1 cpu) ###

def consume_compute_hash(jobs_queue, results_queue, algo: str, bits: int) -> None:
    """Compute hash digest for a file."""
    while True:
        current_input = jobs_queue.get(True, 1)
        if current_input is None:
            break
        # extract file name
        fileName = os.path.basename(current_input)
        # compute the hash
        digest = compute_hash(current_input, algo=algo, bits=bits, debug=False)
        results_queue.put((fileName, digest))



def consume_map_hdrs(jobs_queue, results_queue, mappedInputDir: str=os.getcwd(), outDir: str=os.getcwd()) -> None:
    """Map input headers and compute sequence lengths."""
    while True:
        current_input = jobs_queue.get(True, 1)
        if current_input is None:
            break
        # extract file name
        fPath, spId = current_input
        # map the headers
        protSize, seqCnt = map_hdrs(fPath, spId=spId, mappedInputDir=mappedInputDir, outDir=outDir)
        results_queue.put((spId, protSize, seqCnt))



### Job processing Functions

def compute_hash_parallel(inPaths, algo='sha256', bits=256, threads=4, debug=False) -> Tuple[Dict[str, str], List[Tuple[str, str, str]]]:
    """Compute hash digests in parallel."""
    if debug:
        print('\ncompute_hash_parallel :: START')
        print('Input paths:\t{:d}'.format(len(inPaths)))
        print('Hashing algorithm:{:s}'.format(algo))
        print('Bits:{:d}'.format(bits))
        print('Threads:{:d}'.format(threads))

    # output dictionary (a digest for each file name)
    digestDict: Dict[str, str] = {}
    repeatedDigests: List[Tuple[str, str, str]] = []
    # use to avoid that the same input file is given multiple times
    #controlDict = {}
    # create the queue and start adding
    calc_digest_queue: mp.queues.Queue = mp.Queue(maxsize=len(inPaths) + threads)

    # fill the queue with the file paths
    for fpath in inPaths:
        sys.stdout.flush()
        calc_digest_queue.put(fpath)

    # add flags for completed jobs
    for i in range(0, threads):
        sys.stdout.flush()
        calc_digest_queue.put(None)

    # Queue to contain the execution time
    results_queue: mp.queues.Queue = mp.Queue(maxsize=len(inPaths))

    # call the method inside workers
    runningJobs = [mp.Process(target=consume_compute_hash, args=(calc_digest_queue, results_queue, algo, bits)) for i_ in range(threads)]

    for proc in runningJobs:
        proc.start()

    while True:
        try:
            fname, digest = results_queue.get(False, 0.01)
            # check that the file is not in input multiple times
            if not digest in digestDict:
                # add digest to the dictionary
                digestDict[digest] = fname
                if debug:
                    sys.stdout.write('digest for {:s}:\t{:s}\n'.format(fname, digest))
            else:
                repTpl = (fname, digestDict[digest])
                sys.stderr.write(f"\nERROR: the same digest was found for the input files:\n{repTpl[0]}\t{repTpl[1]}\t{digest}\n")
                repeatedDigests.append((fname, digestDict[digest], digest))
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

    # this joins the processes after we got the results
    for proc in runningJobs:
        while proc.is_alive():
            proc.join()

    # return digests
    return (digestDict, repeatedDigests)



def map_hdrs_parallel(inPaths: List[str], outDir: str=os.getcwd(), digestDict: Dict[str, str]={}, idMapDict: Dict[int, Tuple[str, str]]={}, ignoredProteomes: Dict[int, Tuple[str, str, str]] = {}, threads: int=4, debug: bool=False) -> Tuple[str, str, List[str]]:
    """Map input files in parallel."""
    if debug:
        print(f"\nmap_hdrs_parallel :: START")
        print(f"Input paths:\t{len(inPaths)}")
        print(f"Output directory: {outDir}")
        print(f"File digests:\t{len(digestDict)}")
        print(f"Mapping info:\t{len(idMapDict)}")
        print(f"Species in database not considered:\t{len(ignoredProteomes)}")
        print(f"Threads:\t{threads}")

    # make sure that number of input paths
    # is same as the computed sha256 digests
    if len(digestDict) != len(inPaths):
        sys.stderr.write("ERROR: the number of SHA256 digests, must be same as the number of input paths.")
        sys.exit(4)

    # output dictionary (proteomes size in bases for each file name)
    protSizesDict = {}
    # output dictionary (proteomes counts in bases for each file name)
    protCntDict = {}
    # will contain information for each proteome
    tmpMappingDict = {}
    # create the queue and start adding
    map_hdr_queue: mp.queues.Queue = mp.Queue(maxsize=len(inPaths) + threads)

    # create the directory for the mapped input
    f2shaDict: Dict[str, str] = {}
    for sha, f in digestDict.items():
        f2shaDict[f] = sha
    # directory with the mapped input files
    mappedInputDir = os.path.join(outDir, "mapped_input")
    # otherwise remove its content
    if not os.path.isdir(mappedInputDir):
        systools.makedir(mappedInputDir)
    else: # remove its content
        for f in os.listdir(mappedInputDir):
            if f.startswith(".DS_"):
                continue
            # remove if the file exists
            tmpPath = os.path.join(mappedInputDir, f)
            if os.path.isfile(tmpPath):
                os.remove(tmpPath)

    # fill the queue with the file paths
    # Use the ids in dictionary if it an update
    if len(idMapDict) == 0:
        for i, fpath in enumerate(inPaths):
            sys.stdout.flush()
            idx = i + 1
            bname = os.path.basename(fpath)
            tmpMappingDict[idx] = (bname, f2shaDict[bname])
            map_hdr_queue.put((fpath, idx))
    else: # use the mapping information
        inDir = os.path.dirname(inPaths[0])
        for spId, tpl in idMapDict.items():
            bname, digest = tpl
            if debug:
                print("Update spId and name:", spId, bname)
            sys.stdout.flush()
            fpath = os.path.join(inDir, bname)
            tmpMappingDict[spId] = (bname, digest)
            map_hdr_queue.put((fpath, spId))

    # add flags for completed jobs
    for i in range(0, threads):
        sys.stdout.flush()
        map_hdr_queue.put(None)

    # Queue to contain the execution time
    results_queue: mp.queues.Queue = mp.Queue(maxsize=len(inPaths))
    # call the method inside workers
    runningJobs = [mp.Process(target=consume_map_hdrs, args=(map_hdr_queue, results_queue, mappedInputDir, outDir)) for i_ in range(threads)]

    for proc in runningJobs:
        proc.start()

    while True:
        try:
            spId, proteomeSize, seqCnt = results_queue.get(False, 0.01)
            # add proteom size to the dictionary
            protSizesDict[spId] = proteomeSize
            protCntDict[spId] = seqCnt
            if debug:
                sys.stdout.write("Proteome size for {:s}:\t{:d}\n".format(spId, proteomeSize))
                sys.stdout.write("Proteins in {:s}:\t{:d}\n".format(spId, seqCnt))

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

    # this joins the processes after we got the results
    for proc in runningJobs:
        while proc.is_alive():
            proc.join()

    # Write the species file
    # using the information in tmpMappingDict[spId]
    # and the proteome sizes
    spFilePath = os.path.join(outDir, "species.tsv")
    # pickle with proteome sizes and dictionary to be dumped
    protSizesPcklPath = os.path.join(outDir, "proteome_sizes.pckl")
    protSizePcklDict = {}
    # will contain the paths to the mapped FASTA files
    mappedInPaths: List[str] = []
    ofd = open(spFilePath, "w")
    for spId, tpl in tmpMappingDict.items():
        proteomeSize = protSizesDict[spId]
        ofd.write("{:d}\t{:s}\t{:s}\t{:d}\t{:d}\n".format(spId, tpl[0], tpl[1], protCntDict[spId], proteomeSize))
        protSizePcklDict[str(spId)] = proteomeSize
        mappedInPaths.append(os.path.join(mappedInputDir, str(spId)))
    ofd.close()

    # dump the pickle with proteome sizes
    with open(protSizesPcklPath, "wb") as pcklFd:
        pickle.dump(protSizePcklDict, pcklFd, protocol=4)

    # create and dump the dictionary with protein counts
    # sort the dictionary with protein counts
    protCntDict = dict(sorted(protCntDict.items()))
    protCntsPcklPath = os.path.join(outDir, "protein_counts.pckl")
    protCntsPcklDict = {}
    # fill the dictionary
    for k, val in protCntDict.items():
        protCntsPcklDict[str(k)] = val
    # dump the pickle with protein counts
    with open(protCntsPcklPath, "wb") as pcklFd:
        pickle.dump(protCntsPcklDict, pcklFd, protocol=4)

    # Proteomes that will not be considered
    ofd = open(os.path.join(outDir, "ignored_species.tsv"), "w")
    for spId, tpl in ignoredProteomes.items():
        ofd.write(f"{spId}\t{tpl[0]}\t{tpl[1]}\n")
    ofd.close()
    #sys.exit("DEBUG :: hdr_mapping :: map_hdrs_parallel")
    # return proteome sizes
    return (spFilePath, mappedInputDir, mappedInPaths)



### Other functions ####
def compare_digests(inPaths, oldSpFile, algo='sha256', bits=256,  threads=4, updateNames=False, removeOld=False, debug=False):
    """Compute hash for the input files and compare it with the old digests."""
    if debug:
        print('\ncompare_digests :: START')
        print('Input files:\t{:d}'.format(len(inPaths)))
        print('Old digest and species mapping file: {:s}'.format(oldSpFile))
        print('Hashing algorithm:\t{:s}'.format(algo))
        print('Number of bits for encryption:\t{:d}'.format(bits))
        print('Threads:\t{:d}'.format(threads))
        print('Update file names and alignments in case of name conflict:\t{:s}'.format(str(updateNames)))
        print('Remove obsolete ortholog tables and alignment files:\t{:s}'.format(str(removeOld)))

    # bool to identify runs on subsets
    isSubSetRun = False
    # load old digest file
    oldDigests = {}
    oldName2Id = {}
    oldId2Size = {}
    newName2Path = {}
    with open(oldSpFile, "r") as ifd:
        for ln in ifd:
            fid, fname, dgest, protsize = ln[:-1].split('\t', 3)
            oldDigests[dgest] = fname
            oldName2Id[fname] = int(fid)
            oldId2Size[int(fid)] = protsize
    # compute the digests for the new files
    digestDict, repeatedFiles = compute_hash_parallel(inPaths, algo=algo, bits=bits, threads=threads, debug=debug)
    del repeatedFiles

    # associate a path to each file name
    tmpPathsList = inPaths.copy()
    for d, f in digestDict.items():
        #tmpPath = ""
        tmpIdx = -1
        for i, path in enumerate(tmpPathsList):
            bname = os.path.basename(path)
            if bname == f: # matched the file name
                #tmpPath = path
                newName2Path[bname] = path
                tmpIdx = i
        # remove from the list if matched
        if tmpIdx > -1:
            del tmpPathsList[tmpIdx]

    # create sets for the two digests
    sOld: Set[str] = set(oldDigests.keys())
    sNew: Set[str] = set(digestDict.keys())
    newINTold = sNew.intersection(sOld)
    # new files
    newDIFFold = sNew.difference(sOld)
    # check if it is a proper subset
    # that is, sNew <= sOLd [all x in sNew are also in sOld] and sNew != sOld
    if sNew < sOld:
        isSubSetRun = True
    # files that should be skipped or removed
    oldDIFFnew = sOld.difference(sNew)
    # final input set
    inputSet = newINTold.union(newDIFFold)
    if debug:
        print("\nsNew:", sNew)
        print("sOld:", sOld)
        print("Intersection: ", newINTold)
        print("New-Old: ", newDIFFold)
        print("\nUnchanged files:")
    # Files from the previous run that will be reused
    toReuse: Dict[int, Tuple[str, str, str]] = {}
    # names that require update
    toRemove: Dict[int, str] = {}
    # names that need to be added
    toAdd: Dict[str, Tuple[str, str]] = {}
    oldName: str = ""
    newName: str = ""
    for el in newINTold:
        #print(el)
        # check that the file names have not been changed
        oldName = oldDigests[el]
        newName = digestDict[el]
        if debug:
            print(newName, oldName)
        if oldName != newName:
            if updateNames:
                if debug:
                    print("update file names and alignments: {:s} -> {:s}".format(oldName, newName))
                toRemove[oldName2Id[oldName]] = oldName
                toAdd[newName] = (el, newName2Path[newName])
            else:
                sys.stdout.write("\nERROR: the file {:s} is same as {:s} which has been already used in a previous run.".format(newName, oldName))
                sys.stdout.write("\nRename {:s} to {:s} to keep the previous results or use the --update-input-names option.".format(newName, oldName))
                sys.stdout.write("\nIf you use the --update-input-names option the alignments and tables related to {:s}\n will be removed and the database updated accordingly.".format(oldName))
                sys.exit(-4)
        else: # same digest and same name, just reuse it!
            toReuse[oldName2Id[oldName]] = (oldName, el, newName2Path[oldName])
    del oldName, newName

    if debug:
        print("\nNew files:")
    for newDgest in newDIFFold:
        newName = digestDict[newDgest]
        toAdd[newName] = (newDgest, newName2Path[newName])
        if debug:
            print("->\t", newName, newDgest)
        oldNames = list(oldDigests.values())
        # The file name is already in the DB, but the file has been modified
        if newName in oldNames:
            if updateNames:
                if debug:
                    print("update file names and alignments for {:s} {:d}".format(newName, oldName2Id[newName]))
                toRemove[oldName2Id[newName]] = newName
            else:
                sys.stdout.write("\nERROR: the file name {:s} was used in a previous run for a different file.".format(newName))
                sys.stdout.write("\nRename {:s} to a different name or use the --update-input-names option.".format(newName))
                sys.stdout.write("\nIf you use the --update-input-names option the alignments and tables related to the file named {:s}\n in the previous run will be removed and the run updated accordingly.".format(newName))
                sys.exit(-4)
    # files to be skipped
    if debug:
        print("\nFiles to skip or remove:")
    # names and IDs which alignment and pairwise table files need to be removed
    obsolete: Dict[int, str] = {}
    # names and IDs which alignment and pairwise table files should be kept
    toKeep: Dict[int, Tuple[str, str, str]] = {}
    if len(oldDIFFnew) > 0:
        sys.stdout.write("\nINFO: The following Species from a previous run will not be considered in this analysis:\n")
    for dgest in oldDIFFnew:
        oldName = oldDigests[dgest]
        oldId = oldName2Id[oldName]
        print("{:s}\t{:d}".format(oldName, oldId))
        if removeOld:
            sys.stdout.write("\n The tables and alignments related to {:s} will be removed...\n".format(oldName))
            # skip if it is already in the toRemove dictionary
            if not oldId in toRemove:
                obsolete[oldId] = oldName
        else:
            if not oldId in toRemove: # keep it
                toKeep[oldId] = (oldName, dgest, oldId2Size[oldId])
            sys.stdout.write("Use the --remove-old-species option if you want to remove the related tables and alignment files for the following species.\n")

    # final input set
    if debug:
        print("\nFinal input set:")
        for el in inputSet:
            print(el)
    #sys.exit("DEBUG :: hdr_mapping.py :: compare_digests")

    # RETURN
    # toRemove: Dict[int, str] = {}
    # example: 2:"ecoli"
    # contains file names and IDs which alignment files and pair-wise tables
    # should be removed from the database
    #
    # obsolete: Dict[int, str] = {}
    # example: 1:"ecoli"
    # contains names and IDs of files which alignments and pairwise
    # ortholog tables should be removed
    #
    # toKeep: Dict[int, Tuple[str, str, str]] = {}
    # example: 1:("ecoli", "aefdc6e98c92e4c6181720", "4570052")
    # contains names, IDs, sha, and proteome size of files which alignments and
    # pairwise orthologs will not be used but still should be kept
    #
    # toAdd: Dict[str, Tuple[str, str]] = {}
    # example: "ecoli":("aefdc6e98c92e4c6181720", "input_dir/ecoli")
    # contains file names and SHA256 of new files that should be added
    #
    # toReuse: Dict[int, Tuple[str, str, str]] = {}
    # example: 3:("hsapiens","aefdc6e98c92e4c6181720","input_dir/hsapiens")
    # contains file names and IDs which alignment files and pair-wise tables
    # should be re-used

    # OTHERS
    # newDIFFold: intersections between new and old digest sets
    # if this is emptyu then the input files have not been changed
    # note that the some file name could have been changed
    # Hence, if newDIFFold is empty and toRemove is empty
    # the input files are exactly the same
    # isSubSetRun: identifies runs on a proper subset of the orginal
    return(toRemove, obsolete, toKeep, toAdd, toReuse, digestDict, newDIFFold, isSubSetRun)



def compute_hash(inFile, algo='sha256', bits=256, debug=False):
    """Compute hash for the input file."""
    if debug:
        print('\ncompute_hash :: START')
        print('inFile: {:s}'.format(inFile))
        print('Hashing algorithm:\t{:s}'.format(algo))
        print('Number of bits for encryption:\t{:d}'.format(bits))
    # check for the existance of the input file
    if not os.path.isfile(inFile):
        print("ERROR: the input file does not exist\n{:s}\n".format(inFile))
        sys.exit(-2)
    # create the hash for the input file
    h = hashlib.new(algo)
    with open(inFile, mode='rb') as f:
        for buf in iter(partial(f.read, bits), b''):
            h.update(buf)
    # return the digest
    return h.hexdigest()



def load_mapping_dictionaries(runDir: str=os.getcwd(), debug: bool=False) -> Tuple[Dict[str, str], Dict[str, Dict[str, str]]]:
    """Load original and mapped headers for each species."""
    if debug:
        print("\nload_mapping_hdrs :: START")
        print(f"Directory with run info and mapping files: {runDir}")
    # load the species IDs mapping
    speciesFile = os.path.join(runDir, "species.tsv")
    id2SpDict: Dict[str, str] = {}
    for ln in open(speciesFile, "r"):
      mapId, spName, d1 = ln.split("\t", 2)
      if not mapId in id2SpDict:
        id2SpDict[mapId] = spName

    # load all mapping dictionaries
    new2OldHdrAllSp: Dict[str, Dict[str, str]] = {}

    # Set the directory with header files
    seqInfoFilesDir: str = os.path.join(runDir, "input_seq_info")
    # load the the original headers
    for spId in id2SpDict:
        # load the mapping dictionaries if necessary
        if spId not in new2OldHdrAllSp:
          # load the pickle
          tmpPickle = os.path.join(seqInfoFilesDir, f"hdr_{spId}.pckl")
          with open(tmpPickle, "br") as fd:
            new2OldHdrAllSp[spId] = pickle.load(fd)
    # return the 2 dictionaries
    return(id2SpDict, new2OldHdrAllSp)



def map_hdrs(inFasta: str, spId: int, mappedInputDir: str=os.getcwd(), outDir: str=os.getcwd(), debug: bool=False) -> Tuple[int, int]:
    """Map the headers in the input FASTA."""
    # Will contain the pickle files with headers, sequence lengths and other auxiliary files
    protAuxDir:str = os.path.join(outDir, "input_seq_info/")
    systools.makedir(protAuxDir)
    if debug:
        print(f"Input FASTA: {inFasta}")
        print(f"Species ID:\t{spId}")
        print(f"Directory with mapped input: {mappedInputDir}")
        print(f"Output directory: {outDir}")
        print(f"Directory with auxiliary pickle files: {protAuxDir}")
    # counters and dictionaries
    seqCnt = 0
    genomeSize = 0
    id2lenDict = {}
    new2OldHdr = {}
    idsList = [] # will contain the headers
    # make sure that a given hdr is not repeated in the input
    controlDict: Dict[str, None] = {}
    # generate the text file for the mapping
    spName = str(spId)
    mappingPath = os.path.join(protAuxDir, f"hdr_{spName}.tsv")
    mappingPickle = os.path.join(protAuxDir, f"hdr_{spName}.pckl")
    outPath = os.path.join(mappedInputDir, spName)
    seqLenPath = os.path.join(protAuxDir, f"{spName}.len")
    seq2lenPickl = os.path.join(protAuxDir, f"{spName}.len.pckl")
    idsPickl = os.path.join(protAuxDir, f"{spName}.ids.pckl")
    # create the output file
    ofd: TextIO = open(outPath, "w")
    if debug:
        lenfd = open(seqLenPath, "w")
        hdrfd = open(mappingPath, "w")

    # start reading the file
    from Bio import SeqIO
    for seq_record in SeqIO.parse(open(inFasta), 'fasta'):
        tmpLen = len(seq_record)
        hdr = seq_record.id
        sequence = str(seq_record.seq)
        seqCnt += 1
        genomeSize += tmpLen
        newHdr = f"{spId}.{seqCnt}"
        new2OldHdr[newHdr] = hdr
        id2lenDict[newHdr] = tmpLen
        ofd.write(f">{newHdr}\n{sequence}\n")
        if debug:
            hdrfd.write(f"{newHdr}\t{hdr}\n")
            lenfd.write(f"{newHdr}\t{tmpLen}\n")
        idsList.append(newHdr)
        # avoid repeated entries in input
        if not hdr in controlDict:
            controlDict[hdr] = None
        else:
            print(f"ERROR: the header\n{hdr}\nwas found multiple times in the input.")
            print("Please modify your input to have unique headers before proceeding.")
            sys.exit(-5)
    ofd.close()
    if debug:
        hdrfd.close()
        lenfd.close()
    # dump the dictionary into a picke
    with open(seq2lenPickl, "wb") as pcklFd:
        pickle.dump(id2lenDict, pcklFd, protocol=4)
    # dump the list into a pickel
    with open(idsPickl, "wb") as pcklFd:
        pickle.dump(idsList, pcklFd, protocol=4)
    # dump the dictionary into a pickel
    with open(mappingPickle, "wb") as pcklFd:
        pickle.dump(new2OldHdr, pcklFd, protocol=4)
    # return the genome size
    return (genomeSize, seqCnt)



def remap_orthogroups(inTbl: str, id2SpDict: Dict[str, str]={}, new2oldHdrDict: Dict[str, Dict[str, str]]={}, removeOld: bool=False, hasConflict: bool=True, debug: bool=False) -> str:
    """Restore original headers in the multispecies table."""
    from collections import deque
    if debug:
        print("\nremap_orthogroups :: START")
        print(f"Multispecies table to be remapped: {inTbl}")
        print(f"Entries in species mapping dictionary:\t{len(id2SpDict)}")
        print(f"Entries in header mapping dictionary:\t{len(new2oldHdrDict)}")
        print(f"Remove old file and rename the new one:\t{removeOld}")
        print(f"Input table has conflict column:\t{hasConflict}")
    # make sure the dictionaries are not empty
    if len(id2SpDict) == 0:
        sys.stderr.write("\nERROR: the dictionary with species mapping cannot be empty!\n")
        sys.exit(5)
    if len(new2oldHdrDict) == 0:
        sys.stderr.write("\nERROR: the dictionary with header mapping info cannot be empty!\n")
        sys.exit(5)

    ### Remap main table ###
    # remapped table path (same directory of the original table)
    newTblPath = os.path.join(os.path.dirname(inTbl), f"remapped.{os.path.basename(inTbl)}")
    # open output and input tables
    ofd = open(newTblPath, "wt")
    ifd = open(inTbl, "rt")
    # remap table hdr
    oldHdrFlds: list[str] = []
    if hasConflict:
        oldHdrFlds = ifd.readline()[:-1].split("\t")[:-1]
    else:
        oldHdrFlds = ifd.readline()[:-1].split("\t")

    spIdList: List[str] = []
    tmpLen: int = len(oldHdrFlds)
    for i, col in enumerate(oldHdrFlds):
        if i > 3: # check that it is not the last column
            # insert in the list with species IDs
            spIdList.append(col)
            if i + 1 == tmpLen:
                ofd.write(f"{id2SpDict[col]}\n")
            else:
                ofd.write(f"{id2SpDict[col]}\t")
        # first 4 columns
        else:
            # this column should be just copied
            ofd.write(f"{col}\t")

    # remapped the gene headers
    splitsLimit: int = 0
    if hasConflict:
        splitsLimit = tmpLen
    else:
        splitsLimit = tmpLen - 1

    clstrCnt: int = 0
    tmpDq: Deque[str] = deque(maxlen=1)

    for ln in ifd:
        if hasConflict:
            grpFlds = ln[:-1].split("\t", splitsLimit)[:-1]
        else:
            grpFlds = ln[:-1].split("\t", splitsLimit)
        tmpLen = len(grpFlds)
        clstrCnt += 1
        # Write the first 4 columns
        ofd.write("{:s}\t".format("\t".join(grpFlds[0:4])))
        # Use a Deque to store the remapped ortholog names
        tmpDq = deque(maxlen=len(grpFlds[4:]))

        # Process the orthologs, and write the remapped version
        for i, ortho in enumerate(grpFlds[4:]):
            if ortho[0] == "*":
                tmpDq.append("*")
            else: # remap all the ortholog
                tmpDq.append(",".join([new2oldHdrDict[spIdList[i]][x] for x in ortho.split(",")]))

        # Write the final part of the rempped cluster
        ofd.write("{:s}\n".format("\t".join(tmpDq)))
        # if clstrCnt == 2:
        #    sys.exit("DEBUG :: loop limit reached!")

    # remove the old file and rename the new one
    ifd.close()
    ofd.close()
    if removeOld:
        os.remove(inTbl)
        move(newTblPath, inTbl)
        newTblPath = inTbl
    # sys.exit("DEBUG :: hdr_mapping.remap_orthogroups  :: after writing new files")
    # return the path of the remapped file
    return newTblPath



def remap_flat_orthogroups(inTbl: str, id2SpDict: Dict[str, str]={}, new2oldHdrDict: Dict[str, Dict[str, str]]={}, removeOld: bool=False, debug: bool=False) -> str:
    """Restore original headers in the flat multispecies table."""
    if debug:
        print('\nremap_flat_orthogroups :: START')
        print("Multispecies table to be remapped: {:s}".format(inTbl))
        print("Entries in species mapping dictionary:\t{:d}".format(len(id2SpDict)))
        print("Entries in header mapping dictionary:\t{:d}".format(len(new2oldHdrDict)))
        print("Remove old file and rename the new one:\t{:s}".format(str(removeOld)))
    # make sure the dictionaries are not empty
    if len(id2SpDict) == 0:
        sys.stderr.write("\nERROR: the dictionary with species mapping cannot be empty!\n")
        sys.exit(5)
    if len(new2oldHdrDict) == 0:
        sys.stderr.write("\nERROR: the dictionary with header mapping info cannot be empty!\n")
        sys.exit(5)
    ### Remap flat groups file ###
    # remapped table path (same directory of the original table)
    newTblPath = os.path.join(os.path.dirname(inTbl), "remapped.{:s}".format(os.path.basename(inTbl)))
    # open output and input tables
    ofd = open(newTblPath, "w")
    ifd = open(inTbl, "r")
    # remap table hdr
    oldHdrFlds = ifd.readline()[:-1].split("\t")
    tmpLen: int = len(oldHdrFlds)
    for i, col in enumerate(oldHdrFlds):
        if i > 0: # check that it is not the last column
            if i + 1 == tmpLen:
                # last column
                ofd.write("{:s}\n".format(id2SpDict[col]))
            else:
                # remap
                ofd.write("{:s}\t".format(id2SpDict[col]))
        # first column
        else:
            # this column should be just copied
            ofd.write("{:s}\t".format(col))
    # remapped the gene headers
    for ln in ifd:
        orthoHdrFlds = ln[:-1].split("\t", tmpLen - 1)
        for i, ortho in enumerate(orthoHdrFlds):
            if i > 0: # check that it is not the last column
                # handle the case of empty cluster
                if len(ortho) == 1:
                    ofd.write("{:s}".format(ortho))
                    if i + 1 == tmpLen:
                        # last column
                        ofd.write("\n")
                    else:
                        ofd.write("\t")
                    continue
                # remap
                tmpHdrDict: Dict[str, str] = new2oldHdrDict[oldHdrFlds[i]]
                # split the cluster
                # example of cluster -> 2.1622,2.744
                # NOTE: the flat file contains no scores
                orthoFlds = ortho.split(",")
                # geneCnt = len(orthoFlds)
                # remap the genes to a new list
                tmpRemapList = [tmpHdrDict[gene] for gene in orthoFlds]
                ofd.write(",".join(tmpRemapList))
                if i + 1 == tmpLen:
                    # last column
                    ofd.write("\n")
                else:
                    ofd.write("\t")
            # first column
            else:
                # this column should be just copied
                ofd.write("{:s}\t".format(ortho))
    ifd.close()
    ofd.close()
    # remove the old file and rename the new one
    if removeOld:
        os.remove(inTbl)
        move(newTblPath, inTbl)
        newTblPath = inTbl
    # return the path of the remapped file
    return newTblPath



def remap_not_grouped_orthologs(inPath: str, id2SpDict: Dict[str, str]={}, new2oldHdrDict: Dict[str, Dict[str, str]]={}, removeOld: bool=False, debug: bool=False) -> str:
    """Restore original headers in the file with not grouped genes."""
    if debug:
        print('\nremap_not_grouped_orthologs :: START')
        print("File with not grouped ortholog genes: {:s}".format(inPath))
        print("Entries in species mapping dictionary:\t{:d}".format(len(id2SpDict)))
        print("Entries in header mapping dictionary:\t{:d}".format(len(new2oldHdrDict)))
        print("Remove old file and rename the new one:\t{:s}".format(str(removeOld)))
    # make sure the dictionaries are not empty
    if len(id2SpDict) == 0:
        sys.stderr.write("\nERROR: the dictionary with species mapping cannot be empty!\n")
        sys.exit(5)
    if len(new2oldHdrDict) == 0:
        sys.stderr.write("\nERROR: the dictionary with header mapping info cannot be empty!\n")
        sys.exit(5)
    # Remap the genes
    newTblPath = os.path.join(os.path.dirname(inPath), "remapped.{:s}".format(os.path.basename(inPath)))
    # keep track of the species
    currentSp: str = ""
    tmpHdrDict: Dict[str, str] = {}
    # open output and input tables
    ofd = open(newTblPath, "w")
    ifd = open(inPath, "r")
    # remap table hdr
    for ln in ifd:
        ln = ln[:-1]
        if len(ln) == 0:
            # empty line
            ofd.write("{:s}\n".format(ln))
        elif ln[0] == "#":
            # remap the species name
            currentSp = ln[1:]
            tmpHdrDict = new2oldHdrDict[currentSp]
            ofd.write("#{:s}\n".format(id2SpDict[currentSp]))
        else:
            # it is just a gene
            ofd.write("{:s}\n".format(tmpHdrDict[ln]))
    ifd.close()
    ofd.close()

    # remove the old file and rename the new one
    if removeOld:
        os.remove(inPath)
        move(newTblPath, inPath)
        newTblPath = inPath
    # return the path of the remapped file
    return newTblPath



def remap_group_stats(statPaths: Dict[str, str], id2SpDict: Dict[str, str]={}, removeOld: bool=False, debug: bool=False) -> None:
    """Substitute original headers in the multispecies stats files."""
    if debug:
        print('\nremap_group_stats :: START')
        print("Files to be remapped: {:d}".format(len(statPaths)))
        print("Entries in species mapping dictionary:\t{:d}".format(len(id2SpDict)))
        print("Remove old file and rename the new one:\t{:s}".format(str(removeOld)))
    # make sure the dictionaries are not empty
    if len(id2SpDict) == 0:
        sys.stderr.write("\nERROR: the dictionary with species mapping cannot be empty!\n")
        sys.exit(5)
    if len(statPaths) == 0:
        sys.stderr.write("\nERROR: No file to be remapped!\n")
        sys.exit(5)

    ### Remap files with species in main header ###
    # overall stats file
    tmpInPath = statPaths["overall"]
    tmpOutPath = os.path.join(os.path.dirname(tmpInPath), "remapped.{:s}".format(os.path.basename(tmpInPath)))
    # open output and input tables
    ofd = open(tmpOutPath, "w")
    ifd = open(tmpInPath, "r")
    # remap table hdr
    oldHdrFlds = ifd.readline()[:-1].split("\t")
    # remap headers
    remappedHdrs = [id2SpDict[x] for x in oldHdrFlds[1:-1]]
    # write the new header
    ofd.write("{:s}\t{:s}\t{:s}\n".format(oldHdrFlds[0], "\t".join(remappedHdrs), oldHdrFlds[-1]))
    # write the remaining lines as they are
    for ln in ifd:
        ofd.write(ln)
    ifd.close()
    ofd.close()
    # remove the old file and rename the new one
    if removeOld:
        os.remove(tmpInPath)
        move(tmpOutPath, tmpInPath)
        tmpOutPath = tmpInPath
    ###

    # count stats file
    tmpInPath = statPaths["counts"]
    tmpOutPath = os.path.join(os.path.dirname(tmpInPath), "remapped.{:s}".format(os.path.basename(tmpInPath)))

    # open output and input tables
    ofd = open(tmpOutPath, "w")
    ifd = open(tmpInPath, "r")
    # remap table hdr
    oldHdrFlds = ifd.readline()[:-1].split("\t")
    # remap headers
    remappedHdrs = [id2SpDict[x] for x in oldHdrFlds[1:-1]]
    # write the new header
    ofd.write("{:s}\t{:s}\t{:s}\n".format(oldHdrFlds[0], "\t".join(remappedHdrs), oldHdrFlds[-1]))
    # write the remaining lines as they are
    for ln in ifd:
        ofd.write(ln)
    ifd.close()
    ofd.close()
    # remove the old file and rename the new one
    if removeOld:
        os.remove(tmpInPath)
        move(tmpOutPath, tmpInPath)
        tmpOutPath = tmpInPath

    ### Remap files with species in main header ###
    # binning stats file
    tmpInPath = statPaths["bins"]
    tmpOutPath = os.path.join(os.path.dirname(tmpInPath), "remapped.{:s}".format(os.path.basename(tmpInPath)))

    # open output and input tables
    ofd = open(tmpOutPath, "w")
    ifd = open(tmpInPath, "r")
    # skip the first line
    ofd.write(ifd.readline())
    for ln in ifd:
        spId, rxPart = ln.split("\t", 1)
        # remap the species name
        ofd.write("{:s}\t{:s}\n".format(id2SpDict[spId], rxPart))
    ifd.close()
    ofd.close()
    # remove the old file and rename the new one
    if removeOld:
        os.remove(tmpInPath)
        move(tmpOutPath, tmpInPath)
        tmpOutPath = tmpInPath



def remove_alignments_and_ortholog_tables(rootDir: str="", spId: str="", debug: bool=False):
    """Remove alignments and ortholog tables of a given species."""
    if debug:
        print('\nremove_alignments_and_ortholog_tables :: START')
        print("Main output directory: {:s}".format(rootDir))
        print("Species to be removed: {:s}".format(spId))
    # check that the directories exist
    alignDir = os.path.join(rootDir, "alignments")
    if not os.path.isdir(alignDir):
        sys.stderr.write("\nERROR: the directory with alignments was not found.")
        sys.exit(-2)
    orthoDir = os.path.join(rootDir, "orthologs_db")
    if not os.path.isdir(orthoDir):
        sys.stderr.write("\nERROR: the directory with ortholog tables was not found.")
        sys.exit(-2)
    # directory with matrixes
    # mtxDir = os.path.join(orthoDir, "matrixes")

    # remove the alignments first
    with os.scandir(alignDir) as scDir:
        if debug:
            print("Directory with alignments: {:s}".format(alignDir))
        for f in scDir:
            if not f.name.startswith('.') and f.is_file():
                flds =  f.name.split("-", 1)
                if len(flds) > 1:
                    sp1 = flds[0]
                    sp2 = flds[1]
                    if (sp1 == spId) or (sp2 == spId):
                        try:
                            os.remove(f.path)
                        except OSError as e:
                            print(e)
            elif f.is_dir():
                sys.stderr.write("\nERROR: the directory with alignments should contain no directories.")
                sys.stderr.write("\nMake sure that all alignments were completed with no errors.")
                sys.exit(-3)

    # remove the ortholog pairs
    with os.scandir(orthoDir) as scDir:
        if debug:
            print("Directory with otholog tables: {:s}".format(orthoDir))
        for f in scDir:
            if not f.name.startswith('.') and f.is_dir():
                flds = f.name.split("-", 1)
                if len(flds) == 2:
                    sp1 = flds[0]
                    sp2 = flds[1]
                    if (sp1 == spId) or (sp2 == spId):
                        rmtree(f.path, ignore_errors=True)



def remove_obsolete_results(rootDir: str="", toRemove: Dict[int, str] = {}, obsolete: Dict[int, str] = {}, debug: bool=False) -> None:
    """Modify the ortholog database, remonving ortholog tables where necessary."""
    if debug:
        print('\nremove_obsolete_results :: START')
        print("Main output directory: {:s}".format(rootDir))
        print("Species to be removed: {:d}".format(len(toRemove)))
        print("Species with obsolete results: {:d}".format(len(obsolete)))
    # start removing the species
    for spId, spName in toRemove.items():
        sys.stdout.write("\nRemoving tables and alignments related to {:s} ({:d}).\n".format(spName, spId))
        remove_alignments_and_ortholog_tables(rootDir=rootDir, spId=str(spId), debug=debug)
    for spId, spName in obsolete.items():
        sys.stdout.write("\nRemoving tables and alignments related to {:s} ({:d}).\n".format(spName, spId))
        remove_alignments_and_ortholog_tables(rootDir=rootDir, spId=str(spId), debug=debug)



def update_run_info(inPaths: List=[], outDir: str=os.getcwd(), oldSpFile: str="", algo: str='sha256', bits: int=256, threads: int=4,  updateNames: bool=False, removeOld: bool=False, overwrite: bool=False, debug: bool=False):
    """Create updated info of a run and map the input files."""
    # root directory
    rootDir, d1, d2 = outDir.rsplit("/", 2)
    del d1, d2
    if debug:
        print('\nupdate_run_info :: START')
        print("Paths to the input proteomes: {:d}".format(len(inPaths)))
        print("Root directory: {:s}".format(rootDir))
        print("Output directory: {:s}".format(outDir))
        print("Previous Species mapping file: {:s}".format(oldSpFile))
        print('Hashing algorithm:\t{:s}'.format(algo))
        print('Number of bits for encryption:\t{:d}'.format(bits))
        print('Threads:{:d}'.format(threads))
        print('Update file names and alignments in case of name conflict:\t{:s}'.format(str(updateNames)))
        print('Remove obsolete ortholog tables and alignment files:\t{:s}'.format(str(removeOld)))
        print('Overwrite the complete run or only the pairwise orthologs:\t{:s}'.format(str(overwrite)))
        # main input dir
    inDir: str = os.path.dirname(inPaths[0])
    # compare new and old input files;
    # identify what to remove, keep, or reuse
    toRemove, obsolete, toKeep, toAdd, toReuse, newDigestDict, newDIFFoldSet, isSubSetRun = compare_digests(inPaths, oldSpFile=oldSpFile, algo=algo, bits=bits, threads=threads, updateNames=updateNames, removeOld=removeOld, debug=debug)

    # if newDIFFoldSet is empty and toRemove is empty
    # then the input set has not been modified
    # suggest to use overwrite tables
    # or a complete overwrite
    if ((len(newDIFFoldSet) + len(toRemove)) == 0) and (not overwrite):
           if not isSubSetRun:
               sys.stderr.write("\nWARNING: the input is the same as the one used in the last run, hence this run should bring no changes.")
               sys.stderr.write("\nUse the \"'--overwrite-tables\", or \"'--overwrite\" options to recompute the results.\n")
               sys.exit(-5)
    if debug:
        print("toRemove:\t", toRemove)
        print("obsolete:\t", obsolete)

        # toKeep: Dict[int, Tuple[str, str, str]] = {}
        # example: 1:("ecoli", "aefdc6e98c92e4c6181720", "4570052")
        print("toKeep:\t", toKeep)
        print("toAdd:\t", toAdd)
        print("toReuse:\t", toReuse)

    # tmp variables
    bname: str = ""
    digest: str = ""
    path: str = ""
    # create the dictionary for the species mapping file
    spMapDict: Dict[int, Tuple[str, str]] = {}
    # file paths
    newInPaths: List[str] = []
    # first the reusable
    for spId, tpl in toReuse.items():
        bname, digest, path = tpl
        spMapDict[spId] = (bname, digest)
        newInPaths.append(os.path.join(inDir, bname))
    del bname, digest, path

    # give a sequencial ID to each new file
    idCnt: int = 0
    for bname, tpl in toAdd.items():
        idCnt += 1
        digest, path = tpl
        # increment until the next not used ID
        while (idCnt in spMapDict) or (idCnt in toKeep):
            idCnt += 1
        if (not idCnt in spMapDict) and (not idCnt in toKeep):
            spMapDict[idCnt] = (bname, digest)
            newInPaths.append(os.path.join(inDir, bname))
    # final dictionary
    spMapFinal = dict(sorted(spMapDict.items()))
    del spMapDict
    if debug:
        for spId, tpl in spMapFinal.items():
            print(spId, tpl)

    spFile, mappedInputDir, mappedInPaths = map_hdrs_parallel(inPaths=newInPaths, outDir=outDir, digestDict=newDigestDict, idMapDict=spMapFinal, ignoredProteomes=toKeep, threads=threads, debug=debug)

    # remove obsolete results
    remove_obsolete_results(rootDir=rootDir, toRemove=toRemove, obsolete=obsolete, debug=debug)

    # update the snapshot file if required
    if (len(toRemove) + len(obsolete) + len(toAdd)) > 0:
        copy(spFile, oldSpFile)
        # add the entries that should be kept if any
        tmpOfd = open(oldSpFile, "a")
        for keepId, keepTpl in toKeep.items():
            tmpOfd.write("{:s}\t{:s}\n".format(str(keepId), "\t".join(keepTpl)))
        tmpOfd.close()
        # sort the file
        tmpPath = os.path.join(os.path.dirname(oldSpFile), "sorted.{:s}".format(os.path.basename(oldSpFile)))
        tmpInfoDict: Dict[int, str] = {}
        with open(oldSpFile, "r") as tmpIfd:
            for ln in tmpIfd:
                keepId, keepInfo = ln.split("\t", 1)
                intId = int(keepId)
                if not intId in tmpInfoDict:
                    tmpInfoDict[intId] = keepInfo
                else:
                    sys.stderr.write(f"\nERROR: the id {intId} was found multiple times.\n")
                    sys.exit(-4)
        # sort the dictionary by numeric id
        tmpInfoDict = dict(sorted(tmpInfoDict.items()))
        with open(tmpPath, "w") as tmpOfd:
            for keepId, keepInfo in tmpInfoDict.items():
                tmpOfd.write("{:d}\t{:s}".format(keepId, keepInfo))
        # overwrite the snapshot file
        os.remove(oldSpFile)
        move(tmpPath, oldSpFile)

    # return
    return(spFile, mappedInputDir, mappedInPaths)
