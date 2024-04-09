# -*- coding: utf-8 -*-
"""Debug program that generates an orhotlog table give the processed 4 alignment files."""
import os
import sys
import logging
import argparse
from shutil import copy, rmtree, move, which
# import subprocess
import time
from typing import Dict, List, Tuple, Set
import zipfile
# import numpy as np
import filetype
import pkg_resources

# IMPORT INTERNAL PACKAGES
from sonicparanoid import ortholog_detection as orthodetect
from sonicparanoid import inpyranoid
from sonicparanoid import orthogroups
from sonicparanoid import workers
from sonicparanoid import sys_tools as systools
from sonicparanoid import hdr_mapping as idmapper
# from sonicparanoid import remap_tables_c as remap
# from sonicparanoid import graph_c as graph
# from sonicparanoid import mcl_c as mcl


########### FUNCTIONS ############
def get_params(softVersion):
    """Parse and analyse command line parameters."""
    # Help
    parser = argparse.ArgumentParser(description=f"SonicParanoid {softVersion} - debug program",  usage='%(prog)s -i <INPUT_DIRECTORY> -o <OUTPUT_DIRECTORY>[options]', prog="sonic-debug-infer-ortho-table")
    # Mandatory arguments
    parser.add_argument("-i", "--aln-dir", type=str, required=True, help="Directory containing the processed alignment files (should follow the structure of SonicParanoid alignment directory).", default="")
    parser.add_argument("-o", "--output-directory", type=str, required=True, help="The directory in which the output will be stored.", default="")
    parser.add_argument("-a", "--aux-dir", type=str, required=True, help="Directory containing mapped input file and other sequence info files (should follow the structure of SonicParanoid aux directory).", default="")
    parser.add_argument("-p", "--pair", type=str, required=True, help="The pair to be analyzed (e.g., \"1-2\").", default="")

    # General run options
    parser.add_argument("-s", "--suffix", type=str, required=False, help="Suffix for the output orhtolog table.", default="")
    parser.add_argument("-t", "--threads", type=int, required=False, help="Maximum number of CPUs to be used. Default=4", default=1)
    parser.add_argument("-sm", "--skip-merge", required=False, help="Skip greedy merging of ortholog tables (as in Cosentino and Iwasaki, 2019).", default=False, action="store_true")
    parser.add_argument("-d", "--debug", required=False, help="Output debug information. (WARNING: extremely verbose)", default=False, action="store_true")

    # parse the arguments
    args = parser.parse_args()

    return (args, parser)



def count_grps(ogDir:str) -> Tuple[int, int]:
    """Extract number of created groups from stats file"""
    tmpPath: str = os.path.join(ogDir, "overall.stats.tsv")
    ogCnt: int = 0
    scCnt: int = 0
    tmpStr:str = ""
    # extract count of OGs
    if not os.path.isfile(tmpPath):
        sys.stderr.write("\nWARNING: the file with the OG stats was not found!\nMake sure the ortholog groups clustering was successful.")
    else:
        # extract count of OGs
        with open(tmpPath, "rt") as ifd:
            for ln in ifd:
                if ln[:3] == "OGs":
                    tmpStr = ln.rsplit("\t", 1)[-1]
                    ogCnt = int(tmpStr.rstrip("\n"))
                    break
    # extract count of OGs
    tmpPath = os.path.join(ogDir, "single-copy_groups.tsv")
    if not os.path.isfile(tmpPath):
        sys.stderr.write("\nWARNING: the file with the single-copy OGs was not found!\nMake sure the ortholog groups clustering was successful.")
    else:
        # extract count of single-copy OGs
        with open(tmpPath, "rt") as ifd:
            for ln in ifd:
                scCnt += 1
        scCnt -= 1 # this accounts for the header
    return (ogCnt, scCnt)



def extract_single_copy_groups(grpTbl: str, grpFlatTbl: str, debug: bool = False) -> str:
    """Write a list with single copy ortholog groups."""
    if debug:
        print("extract_single_copy_groups :: START")
        print("Input groups table: {:s}".format(grpTbl))
        print("Input \"flast\" groups table: {:s}".format(grpFlatTbl))

    if not os.path.isfile(grpTbl):
        sys.stderr.write("\nERROR: the table with ortholog groups\n{:s}\nwas not found.\n".format(grpTbl))
        sys.exit(-2)
    if not os.path.isfile(grpFlatTbl):
        sys.stderr.write("\nERROR: the table with \"flat\" ortholog groups\n{:s}\nwas not found.\n".format(grpFlatTbl))
        sys.exit(-2)

    # counter for single-copy groups
    scogCnt: int = 0
    rdCnt: int = 0
    # load the first 3 columns only
    ifdFlat = open(grpFlatTbl, "rt")
    ifdGrps = open(grpTbl, "rt")
    # skip the headers
    ifdGrps.readline()
    flatHdr: str = ifdFlat.readline()

    # output paths
    outPath: str = os.path.join(os.path.join(os.path.dirname(grpTbl), "single-copy_groups.tsv"))
    # open output file and write the header
    ofd = open(outPath, "wt")
    ofd.write(flatHdr)

    # now search for single-copy ortholog groups
    # These are groups which a single ortholog for each species in the groups
    for ln in ifdGrps:
        rdCnt += 1
        clstrId, grpSize, spInGrp, d1 = ln.split("\t", 3)
        flatLn: str = ifdFlat.readline()
        del d1
        del clstrId
        if grpSize == spInGrp:
            # then this should be kept
            scogCnt += 1
            ofd.write(flatLn)
    ifdGrps.close()
    ifdFlat.close()
    ofd.close()

    # percentage of single copy ortholog groups
    scogPct: float = round((float(scogCnt)/float(rdCnt)) * 100., 2)
    if debug:
        print("Single-copy ortholog groups:\t{:d}".format(scogCnt))
        print("Percentage of single-copy ortholog groups:\t{:.2f}".format(scogPct))

    # return the output file
    return outPath



def filter_warnings(debug:bool=False):
    """Show warnings only in debug mode"""
    if not debug:
        import warnings
        warnings.filterwarnings("ignore")



def verify_aln_files(inDir: str, sp1: str, sp2: str) -> bool:
    """Check that the required alignment files are available."""
    debugStr: str = f'''    verify_aln_files :: START
    Alignment directory: {inDir}
    sp1:\t{sp1}
    sp2:\t{sp2}'''
    logging.debug(debugStr)

    # Following are the 4 files:
    # /inDir/sp1/sp1-sp1
    # /inDir/sp1/sp1-sp2
    # /inDir/sp2/sp2-sp2
    # /inDir/sp1/sp2-sp1
    tmpPath: str = os.path.join(inDir, f"{sp1}/{sp1}-{sp1}")
    if not os.path.isfile(tmpPath):
        logging.error(f"The processed alignment file was not found.\n{tmpPath}")
        sys.exit(-2)
    tmpPath = os.path.join(inDir, f"{sp1}/{sp1}-{sp2}")
    if not os.path.isfile(tmpPath):
        logging.error(f"The processed alignment file was not found.\n{tmpPath}")
        sys.exit(-2)
    tmpPath = os.path.join(inDir, f"{sp2}/{sp2}-{sp2}")
    if not os.path.isfile(tmpPath):
        logging.error(f"The processed alignment file was not found.\n{tmpPath}")
        sys.exit(-2)
    tmpPath = os.path.join(inDir, f"{sp2}/{sp2}-{sp1}")
    if not os.path.isfile(tmpPath):
        logging.error(f"The processed alignment file was not found.\n{tmpPath}")
        sys.exit(-2)

    return True



def infer_orthogroups_2_proteomes(orthoDbDir: str, outDir: str, sharedDir: str, outName: str, pairsDict: Dict[str, float], debug: bool=False):
    """Create ortholog groups for only 2 proteomes"""
    import pickle
    if debug:
        print("\ninfer_orthogroups_2_proteomes :: START")

    # sys.exit("DEBUG@sonicparanoid -> infer_orthogroups_2_proteomes")
    # reference species file
    sys.stdout.write("\nCreating ortholog groups for the 2 proteomes...\n")
    timer_start = time.perf_counter()
    # Aux dir
    auxDir: str = os.path.join(sharedDir, "aux")
    # set the output name
    outSonicGroups: str = os.path.join(outDir, outName)
    # extract the only pair
    sp1, sp2 = list(pairsDict.keys())[0].split("-", 1)
    tablePath: str = os.path.join(orthoDbDir, f"{sp1}/table.{sp1}-{sp2}")
    flatGrps, notGroupedPath = orthogroups.create_2_proteomes_groups(rawTable=tablePath, outPath=outSonicGroups, debug=debug)
    # load dictionary with protein counts
    seqCntsDict = pickle.load(open(os.path.join(auxDir, "protein_counts.pckl"), "rb"))
    # Remap the groups
    sys.stdout.write("\nGenerating final output files...")
    # load dictionary with proteome sizes
    genomeSizesDict = pickle.load(open(os.path.join(auxDir, "proteome_sizes.pckl"), "rb"))
    # compute stats
    grpsStatPaths = orthogroups.compute_groups_stats_no_conflict(inTbl=outSonicGroups, outDir=outDir, outNameSuffix="stats", seqCnts=seqCntsDict, proteomeSizes=genomeSizesDict, debug=False)
    # load the mapping information
    id2SpDict, new2oldHdrDict = idmapper.load_mapping_dictionaries(runDir=auxDir, debug=debug)
    # remap the genes in orthogroups
    idmapper.remap_orthogroups(inTbl=outSonicGroups, id2SpDict=id2SpDict, new2oldHdrDict=new2oldHdrDict, removeOld=True, hasConflict=False, debug=debug)
    # remap file with not grouped genes
    idmapper.remap_not_grouped_orthologs(inPath=notGroupedPath, id2SpDict=id2SpDict, new2oldHdrDict=new2oldHdrDict, removeOld=True, debug=debug)
    # remap stats
    idmapper.remap_group_stats(statPaths=grpsStatPaths, id2SpDict=id2SpDict, removeOld=True, debug=debug)
    # remap the flat multi-species table
    idmapper.remap_flat_orthogroups(inTbl=flatGrps, id2SpDict=id2SpDict, new2oldHdrDict=new2oldHdrDict, removeOld=True, debug=debug)
    # extract single-copy ortholog groups
    extract_single_copy_groups(grpTbl=outSonicGroups, grpFlatTbl=flatGrps, debug=debug)
    sys.stdout.write("\nOrtholog groups creation elapsed time (seconds):\t{:s}\n".format(str(round(time.perf_counter() - timer_start, 3))))
    ogCnt, scOgCnt = count_grps(os.path.dirname(flatGrps))
    sys.stdout.write(f"\nOrtholog groups:\t{ogCnt}\n")
    sys.stdout.write(f"Single-copy ortholog groups:\t{scOgCnt}\n")
    print(f"\nThe ortholog groups and related statistics are stored in the directory:\n{os.path.dirname(flatGrps)}")



def infer_orthogroups_mcl(orthoDbDir: str, sharedDir: str, outName: str, pairsList: List[str], inflation: float = 1.5, threads: int=4, condaRun: bool=False, debug: bool=False):
    """Perform orthology inference using MCL"""
    import pickle
    delMclInputMtx: bool = True
    if debug:
        print("\ninfer_orthogroups_mcl :: START")
        delMclInputMtx = False

    # Set the path for the MCL binaries
    mclBinPath: str = ""
    if condaRun:
        if which("mcl") is None:
            sys.stderr.write(f"\nERROR: MCL could not be found, please install it using CONDA.")
            sys.exit(-5)
        else:
            mclBinPath = str(which("mcl"))
    # Use the binaries provided with the SonicParanoid package
    else:
        mclBinPath = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bin/mcl")
    # Check that the binaries exist
    if os.path.isfile(mclBinPath):
        if debug:
            sys.stdout.write(f"\nMCL is installed at:\n{mclBinPath}")
    else:
        sys.stderr.write("\nERROR: the MCL program was not found.\nPlease try to re-install SonicParanoid, or contact the developers.\n")
        sys.exit(-5)

    # sys.exit("DEBUG@sonicparanoid -> infer_orthogroups_mcl")
    auxDir: str = os.path.join(sharedDir, "aux")
    sys.stdout.write("\nCreating ortholog groups using MCL clustering...")
    timer_start = time.perf_counter()
    # compute ortholog matrixes
    mtxDir = os.path.join(os.path.dirname(orthoDbDir), "ortholog_matrixes")
    systools.makedir(mtxDir)
    # create matrixes
    graph.create_matrix_from_orthotbl_parallel(pairsList=pairsList, runDir=auxDir, orthoDbDir=orthoDbDir, outDir=mtxDir, threads=threads, debug=False)
    # call garbage collector
    gc.collect()
    # load dictionary with protein counts
    seqCntsDict = pickle.load(open(os.path.join(auxDir, "protein_counts.pckl"), "rb"))
    # path for the matrix with combination
    combMtxPath = os.path.join(auxDir, "combination_mtx.npz")
    # merge the inparalog matrixes
    spArray = np.array([int(x) for x in seqCntsDict.keys()], dtype=np.uint16)
    # start timer
    tmp_timer_start = time.perf_counter()
    sys.stdout.write("\nMerging inparalog matrixes...")
    graph.merge_inparalog_matrixes_parallel(spArray, combMtxPath, inDir=mtxDir, outDir=mtxDir, threads=threads, removeMerged=True, debug=False)
    sys.stdout.write("\nInparalogs merging elapsed time (seconds):\t{:s}\n".format(str(round(time.perf_counter() - tmp_timer_start, 3))))
    # create MCL output dir
    mclDir = os.path.join(sharedDir, "ortholog_groups")
    systools.makedir(mclDir)
    # Create MCL files
    # THIS NEEDS TO BE IMPLEMENTED FOR SUBGROUPS OF SPECIES
    emptyArray = np.array(np.arange(start=1, stop=1, step=1, dtype=np.int16))
    # create MCL matrix
    sys.stdout.write("\nCreating input matrix for MCL...")
    tmp_timer_start = time.perf_counter()
    mclMatrix = mcl.write_mcl_matrix(spArray, spSkipArray=emptyArray, runDir=auxDir, mtxDir=mtxDir, outDir=mclDir, threads=threads, removeProcessed=True, debug=False)
    sys.stdout.write(f"\nMCL graph creation elapsed time (seconds):\t{round(time.perf_counter() - tmp_timer_start, 3)}\n")
    # output paths
    rawMclGroupsPath = os.path.join(mclDir, f"raw_mcl_{outName}")
    # Run MCL
    sys.stdout.write("\nRunning MCL...")
    sys.stdout.flush()
    tmp_timer_start = time.perf_counter()
    mcl.run_mcl(mclGraph=mclMatrix, outPath=rawMclGroupsPath, mclBinPath=mclBinPath, inflation=inflation, threads=threads, removeInput=delMclInputMtx, debug=debug)
    sys.stdout.write(f"\nMCL execution elapsed time (seconds):\t{round(time.perf_counter() - tmp_timer_start, 3)}\n")
    # remap the orthogroups
    outSonicGroups = os.path.join(mclDir, outName)
    # Remap the groups
    sys.stdout.write("\nGenerating final output files...")
    tmp_timer_start = time.perf_counter()
    mcl.remap_mcl_groups(mclGrps=rawMclGroupsPath, outPath=outSonicGroups, runDir=auxDir, writeFlat=True, debug=debug)
    # load dictionary with proteome sizes
    genomeSizesDict = pickle.load(open(os.path.join(auxDir, "proteome_sizes.pckl"), "rb"))
    # compute stats
    grpsStatPaths = orthogroups.compute_groups_stats_no_conflict(inTbl=outSonicGroups, outDir=mclDir, outNameSuffix="stats", seqCnts=seqCntsDict, proteomeSizes=genomeSizesDict, debug=debug)
    # load the mapping information
    id2SpDict, new2oldHdrDict = idmapper.load_mapping_dictionaries(runDir=auxDir, debug=debug)
    # remap the genes in orthogroups
    idmapper.remap_orthogroups(inTbl=outSonicGroups, id2SpDict=id2SpDict, new2oldHdrDict=new2oldHdrDict, removeOld=True, hasConflict=False, debug=debug)
    # remap file with not grouped genes
    notGroupedPath = os.path.join(mclDir, f"not_assigned_genes.{outName}")
    idmapper.remap_not_grouped_orthologs(inPath=notGroupedPath, id2SpDict=id2SpDict, new2oldHdrDict=new2oldHdrDict, removeOld=True, debug=debug)
    # remap stats
    idmapper.remap_group_stats(statPaths=grpsStatPaths, id2SpDict=id2SpDict, removeOld=True, debug=debug)
    # remap the flat multi-species table
    flatGrps = os.path.join(mclDir, f"flat.{outName}")
    idmapper.remap_flat_orthogroups(inTbl=flatGrps, id2SpDict=id2SpDict, new2oldHdrDict=new2oldHdrDict, removeOld=True, debug=debug)
    # extract single-copy ortholog groups
    extract_single_copy_groups(grpTbl=outSonicGroups, grpFlatTbl=flatGrps, debug=debug)
    sys.stdout.write("\nElapsed time for the creation of final output (seconds):\t{:s}\n".format(str(round(time.perf_counter() - tmp_timer_start, 3))))
    del tmp_timer_start
    sys.stdout.write(f"Ortholog groups creation elapsed time (seconds):\t{round(time.perf_counter() - timer_start, 3)}\n")
    ogCnt, scOgCnt = count_grps(mclDir)
    sys.stdout.write(f"\nOrtholog groups:\t{ogCnt}\n")
    sys.stdout.write(f"Single-copy ortholog groups:\t{scOgCnt}\n")
    print(f"\nThe ortholog groups and related statistics are stored in the directory:\n{mclDir}")



#####  MAIN  #####
def main():
    """Main function that performs inference of an ortholog table.
    This function should only be used for debugging.
    """
    # get SonicParanoid version
    softVersion = pkg_resources.get_distribution("sonicparanoid").version
    # start measuring the execution time
    ex_start = time.perf_counter()
    #Get the parameters
    args, parser = get_params(softVersion)
    # start setting the needed variables
    debug: bool = args.debug
    # Set warning level
    filter_warnings(debug)
    # Set logging level
    if debug:
        logging.basicConfig(format='%(asctime)s : %(levelname)s:\n%(message)s', level=logging.DEBUG)
    else:
        # logging.basicConfig(level=logging.INFO)
        logging.basicConfig(format='%(levelname)s:\n%(message)s', level=logging.INFO)

    # Pair to be processed
    pair: str = args.pair
    if len(args.pair) == 0:
        sys.stderr.write("\nERROR: The pair name cannot be empty!\n")
        sys.exit(-5)

    # set main directories
    alnDir: str = ""
    if len(args.aln_dir) > 0:
        alnDir = f"{os.path.realpath(args.aln_dir)}"
    # check that the input directory has been provided
    if not os.path.isdir(alnDir):
        sys.stderr.write(f"\nERROR: the directory with processed alignments is not valid.\n{alnDir}\n")
        parser.print_help()
    auxDir: str = ""
    if len(args.aln_dir) > 0:
        auxDir = f"{os.path.realpath(args.aux_dir)}"
    # check that the aux directory has been provided
    if not os.path.isdir(auxDir):
        sys.stderr.write(f"\nERROR: the directory with aux files is not valid.\n{auxDir}\n")
        parser.print_help()
    # output dir
    outDir: str = os.path.realpath(args.output_directory)
    inputFastaDir: str = os.path.join(auxDir, "mapped_input")

    # Extra parameters
    outSuffix: str = args.suffix
    skipMerge: bool = args.skip_merge
    threads: int = args.threads

    # Write some debug using logging
    infoStr: str = f'''    Alignment directory: {alnDir}
    Aux directory: {auxDir}
    Output directory: {outDir}
    Pair:\t{pair}
    Suffix:\t{outSuffix}
    Skip merge:\t{skipMerge}
    Threads:\t{threads}'''
    logging.info(infoStr)
    # create out dir
    systools.makedir(outDir)
    # systools.makedir(tblDir)
    # set proteome names
    sp1: str = ""
    sp2: str = ""
    sp1, sp2 = pair.split("-", 1)

    # Verify input alignment files
    verify_aln_files(alnDir, sp1, sp2)

    # Perform the prediction
    # Pairs for which the ortholog table is missing
    requiredPairsDict: Dict[str, float] = {"1-2":1.0}
    # Preprocess within alignments
    withinAlignDict: Dict[str, List[Any]] = {sp1:[1, None, None], sp2:[1, None, None]}

    segOverlapCutoff: float = 0.20
    # The actual matching segments must cover this of this match of the matched sequence
    # For example for a matched sequence 70 bps long, segments 1-15 and 50-70 gives a total coverage of 35, which is 50% of total.
    # HACK: restore the oginal value if required
    segCoverageCutoff: float = 0.20
    # load the required within alignments in parallel
    inpyranoid.preprocess_within_alignments_parallel(withinAlignDict, alignDir=alnDir, threads=1, covCoff=segCoverageCutoff, overlapCoff=segOverlapCutoff, minBitscore=40, compressed=True, debug=debug)

    # print(withinAlignDict["1"][2])

    # Store the pickles with the protein lengths


    # Predict orthologs
    workers.perform_parallel_orthology_inference_shared_dict(requiredPairsDict, inputFastaDir, outDir=outDir, sharedDir=alnDir, sharedWithinDict=withinAlignDict, minBitscore=40, confCutoff=0.05, lenDiffThr=1.0, threads=threads, compressed=True, debug=debug)
    sys.exit(-10)


    '''
    # Predict orthologs
    workers.perform_parallel_orthology_inference_shared_dict(requiredPairsDict, inDir, outDir=tblDir, sharedDir=alignDir, sharedWithinDict=withinAlignDict, minBitscore=minBitscore, confCutoff=confCutoff, lenDiffThr=lenDiffThr, threads=threads, compressed=compress, debug=debug)
    '''


    ex_end = round(time.perf_counter() - ex_start, 3)
    sys.stdout.write(f"\nTotal elapsed time (seconds):\t{ex_end:.3f}\n")


if __name__ == "__main__":
    main()
