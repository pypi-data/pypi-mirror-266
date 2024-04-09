# -*- coding: utf-8 -*-
"""
    Debug program to generates the training documents starting from the profile search results.
    The script performs the following steps:
    - extract architecuters in parallel from all the profile searches
    - Raw architectures are processed and document files
    - A file with raw documents is generated
    - Create the training corpus
"""

from __future__ import annotations

import os
import sys
import logging
import argparse
import time
from typing import TextIO, Any
import pickle
from itertools import combinations
import pkg_resources
import numpy as np

# Use this for profiling
# import pstats, cProfile

# IMPORT INTERNAL PACKAGES
# from sonicparanoid import dev_profile_search as psearch
# from sonicparanoid import dev_d2v as d2v
from sonicparanoid import dev_ortho_merger as merger
from sonicparanoid import sys_tools as systools
# from sonicparanoid import hdr_mapping as idmapper
# from sonicparanoid import workers



########### FUNCTIONS ############

# This logger will used for the main
logger: logging.Logger = logging.getLogger()


def get_params(softVersion):
    """Parse and analyse command line parameters."""
    # Help
    parser = argparse.ArgumentParser(description=f"SonicParanoid {softVersion} - debug program",  usage='%(prog)s -i <INPUT_DIRECTORY> -o <OUTPUT_DIRECTORY>[options]', prog="sonic-debug-profile-search")
    parser.add_argument("-god", "--graph-ortho-tbl-dir", type=str, required=True, help="Directory with graph-based ortholog tables\n", default=None)
    parser.add_argument("-aod", "--arch-ortho-tbl-dir", type=str, required=True, help="Directory with architecture-based ortholog tables\n", default=None)
    parser.add_argument("-r", "--run-dir", type=str, required=True, help="Directory in which SonicParanoid run files are stored. These include auxliary files with mapping dictionaries.\n", default=None)
    parser.add_argument("-o", "--output-dir", type=str, required=True, help="The directory in which the output will be stored.", default="")
    # parser.add_argument("-mbits", "--min-bitscore", type=int, required=False, help="Minimum bitscore for profiles hits to be considered.", default=30)
    parser.add_argument("--prefix", type=str, required=False, help="Prefix for output directory", default="archs")

    # Other parameters
    parser.add_argument("-t", "--threads", type=int, required=False, help="Maximum number of CPUs to be used. Default=4", default=1)
    parser.add_argument("-d", "--debug", required=False, help="Output debug information. (WARNING: extremely verbose)", default=False, action="store_true")
    # parse the arguments
    args = parser.parse_args()

    return (args, parser)



def get_arch_ortho_table_paths(inDir: str, spPairs: list[tuple[int, int]]) -> dict[tuple[int, int], str]:
    """Obtain paths arch-based ortholog tables."""
    logger.debug(f"""get_arch_ortho_table_paths :: START
        inDir: {inDir}
        Pairs:\t{len(spPairs)}""")

    tmpPath: str = ""
    tmpTblName: str = ""
    # associate a path to each file name
    outDict: dict[tuple[int, int], str] = {}
    pair: tuple[int, int] = (0, 0)
    pairsCnt: int = len(spPairs)
    # Check if the table files exist
    for pair in spPairs:
        # The file names should have the following pattern
        # <sp1>-<sp2>arch.ortho.tsv
        tmpTblName = f"{pair[0]}-{pair[1]}.arch.ortho.tsv"
        tmpPath = os.path.join(inDir, tmpTblName)
        if not os.path.isfile(tmpPath):
            logging.error(f"""The file for the arch-based table pair {pair} was not found!""")
            sys.exit(-5)
        else:
            outDict[pair] = tmpPath

    # Check that all tables where found
    if len(outDict) != pairsCnt:
        logging.error(f"""The number of table files found {len(outDict)} differs from the nummber of species combinations {pairsCnt}!""")
        sys.exit(-5)

    return outDict



def get_graph_ortho_table_paths(inDir: str, spPairs: list[tuple[int, int]]) -> dict[tuple[int, int], str]:
    """Obtain paths graph-based ortholog tables."""
    logger.debug(f"""get_graph_ortho_table_paths :: START
        inDir: {inDir}
        Pairs:\t{len(spPairs)}""")

    tmpPath: str = ""
    tmpTblName: str = ""
    # associate a path to each file name
    outDict: dict[tuple[int, int], str] = {}
    pair: tuple[int, int] = (0, 0)
    pairsCnt: int = len(spPairs)
    sp1: int = 0
    # sp2: int = 0
    # Check if the table files exist
    for pair in spPairs:
        # print(pair)
        sp1, sp2 = pair
        # The file names should have the following pattern
        # <sp1>-<sp2>arch.ortho.tsv
        tmpTblName = f"table.{sp1}-{sp2}"
        tmpPath = os.path.join(inDir, f"{sp1}/{tmpTblName}")
        if not os.path.isfile(tmpPath):
            logging.error(f"""The file {tmpTblName} for the graph-based table pair {pair} was not found!""")
            sys.exit(-5)
        else:
            outDict[pair] = tmpPath

    # Check that all tables where found
    if len(outDict) != pairsCnt:
        logging.error(f"""The number of graph-based table files found {len(outDict)} differs from the nummber of species combinations {pairsCnt}!""")
        sys.exit(-5)

    return outDict



def get_ortho_table_paths(inDirGraphBased: str, inDirArchBased: str, spPairs: list[tuple[int, int]]) -> dict[tuple[int, int], tuple[str, str]]:
    """Obtain paths graph-based ortholog tables."""
    logger.debug(f"""get_ortho_table_paths :: START
        inDirGraphBased: {inDirGraphBased}
        inDirArchBased: {inDirArchBased}
        Pairs:\t{len(spPairs)}""")

    tmpPath: str = ""
    tmpTblName: str = ""
    # Extract the path of ortholog tables
    archBasedPaths: dict[tuple[int, int], str] = get_arch_ortho_table_paths(inDir=inDirArchBased, spPairs=spPairs)
    graphBasedPaths: dict[tuple[int, int], str] = get_graph_ortho_table_paths(inDir=inDirGraphBased, spPairs=spPairs)
    # Create a single dictionary with paths from both sources
    outDict: dict[tuple[int, int], tuple[str, str]] = {}
    i: int = 0
    pair: tuple[int, int] = (0, 0)
    pairsCnt: int = len(spPairs)
    gTblPath: str = ""
    aTblPath: str = ""
    for i in range(pairsCnt):
        # print(i)
        pair = spPairs.pop()
        # print(pair)
        gTblPath = graphBasedPaths[pair]
        aTblPath = archBasedPaths[pair]
        outDict[pair] = (gTblPath, aTblPath)

    # Check that all tables where found
    if len(outDict) != pairsCnt:
        logging.error(f"""The number of pairs of table files found {len(outDict)} differs from the nummber of species combinations {pairsCnt}!""")
        sys.exit(-5)

    return outDict



def filter_warnings(debug:bool=False):
    """Show warnings only in debug mode"""
    if not debug:
        import warnings
        warnings.filterwarnings("ignore")



def load_run_info(runDir: str) -> tuple[dict[str, int], dict[str, int]]:
    """Load information about the run"""
    debugStr: str = f"load_run_info :: START\n\
        runDir: {runDir}"
    logger.debug(debugStr)

    # Set tmp paths
    auxDir: str = os.path.join(runDir, "aux")
    logger.info(f"Dir with run aux files: {auxDir}")
    # load dictionary with protein counts
    seqCntsDict = pickle.load(open(os.path.join(auxDir, "protein_counts.pckl"), "rb"))
    # load dictionary with proteome sizes
    proteomeSizesDict = pickle.load(open(os.path.join(auxDir, "proteome_sizes.pckl"), "rb"))

    return (proteomeSizesDict, seqCntsDict)



def write_arch_based_clusters_to_file(aClstrDict: dict[int, any], outPath: str):
    """Write arch based clusters to file"""
    debugStr: str = f"write_arch_based_clusters_to_file :: START\n\
    Clusters:\t{len(aClstrDict)}\n\
    Output path:\t{outPath}"
    logger.debug(debugStr)

    # extract the species IDs from the output name
    sp1: int = 0
    sp2: int = 0
    sp1OrthoArr: np.ndarray = np.zeros(0, dtype=np.uint16)
    sp2OrthoArr: np.ndarray = np.zeros(0, dtype=np.uint16)
    cosineValues: list[np.ndarray] = []
    # Output name has the following pattern
    # 23-33.arch.ortho.tsv
    bname: str = os.path.basename(outPath)
    # print(bname.split(".", 1)[0].split())
    sp1, sp2 = [int(x) for x in bname.split(".", 1)[0].split("-", 1)]
    clstrIds: list[int] = list(aClstrDict.keys())
    tmpCluster: Any
    sp1OrthoStr: str = ""
    sp2OrthoStr: str = ""
    scoresStr: str = ""
    scoresStrList: list[str] = []
    tmpScores: list[str] = []

    # Create the output file
    ofd: TextIO = open(outPath, "wt", encoding="utf-8")

    # Start processing the clusters
    for cid in clstrIds:
        tmpCluster = aClstrDict[cid]
        sp1OrthoArr = getattr(tmpCluster, "sp1Ids")
        sp2OrthoArr = getattr(tmpCluster, "sp2Ids")
        cosineValues = getattr(tmpCluster, "cosineValues")

        scoresStrList.clear()
        scoresStr = ""
        # Generate the string with scores
        for scArr in cosineValues:
            tmpScores = [f"{x:.2f}" for x in scArr.tolist()]
            scoresStrList.append(",".join(tmpScores))
            # print(scoresStr)
            # break

        scoresStr = ":".join(scoresStrList)
        # print(scoresStr)
        # Create the string with ortho from the two species
        sp1OrthoStr = " ".join([f"{sp1}.{x:d}" for x in sp1OrthoArr.tolist()])
        sp2OrthoStr = " ".join([f"{sp2}.{x:d}" for x in sp2OrthoArr.tolist()])

        # Write the information to the output file
        ofd.write(f"{scoresStr}\t{sp1OrthoStr}\t{sp2OrthoStr}\n")

    ofd.close()



def write_arch_based_pairs_to_file(aClstrDict: dict[int, any], outPath: str) -> int:
    """Write arch based pairs to file"""
    debugStr: str = f"write_arch_based_pairs_to_file :: START\n\
    Clusters:\t{len(aClstrDict)}\n\
    Output path:\t{outPath}"
    logger.debug(debugStr)

    # extract the species IDs from the output name
    sp1: int = 0
    sp2: int = 0
    pairsCnt: int = 0
    sp1OrthoArr: np.ndarray = np.zeros(0, dtype=np.uint16)
    sp2OrthoArr: np.ndarray = np.zeros(0, dtype=np.uint16)
    # Output name has the following pattern
    # 23-33.arch.ortho.tsv
    bname: str = os.path.basename(outPath)
    # Remove 'pairs.' from the basename
    bname = bname.split("pairs.", 1)[1]
    # print(bname.split(".", 1)[0].split())
    sp1, sp2 = [int(x) for x in bname.split(".", 1)[0].split("-", 1)]
    clstrIds: list[int] = list(aClstrDict.keys())
    tmpCluster: Any
    sp1OrthoList: list[str] = []
    sp2OrthoList: list[str] = []
    # Create the output file
    ofd: TextIO = open(outPath, "wt", encoding="utf-8")

    # Start processing the clusters
    for cid in clstrIds:
        tmpCluster = aClstrDict[cid]
        sp1OrthoArr = getattr(tmpCluster, "sp1Ids")
        sp2OrthoArr = getattr(tmpCluster, "sp2Ids")

        # Create the string with ortho from the two species
        sp1OrthoList = [f"{sp1}.{x:d}" for x in sp1OrthoArr.tolist()]
        sp2OrthoList = [f"{sp2}.{x:d}" for x in sp2OrthoArr.tolist()]

        # Write the pairs to file
        for oSp1 in sp1OrthoList:
            for oSp2 in sp2OrthoList:
                ofd.write(f"{oSp1}\t{oSp2}\n")
                pairsCnt += 1
    ofd.close()

    # print(f"Ortholog pairs:\t{pairsCnt}")

    return pairsCnt



def set_loggers(rootLogger: logging.Logger, moduleNames: list[str]):
    """Set loggers for each loaded module"""
    debugStr: str = f"set_loggers :: START\n\
    rootLogger:\t{rootLogger}\n\
    Module names:\t{moduleNames}"
    # rootLogger.debug(debugStr)
    logger.debug(debugStr)

    # At least one module name must be in the names list
    if len(moduleNames) == 0:
        sys.stdout.write(f"WARNING: no module names in the list.\nYou must provide at least one name of imported module.")

    # Set counters
    totModules: int = len(moduleNames)
    rootLoggingLev: int = rootLogger.level
    loadedCnt: int = 0
    invalidNames: list[str] = []
    # set the default formatters
    defaultInfoFmt: logging.Formatter = logging.Formatter("{levelname}:\n{message}", style="{")
    defaultDebugFmt: logging.Formatter = logging.Formatter("{levelname} :: {name} :: ln{lineno}:\n{message}", style="{")

    # Obtain loaded names
    loadedMods = sys.modules.keys()
    # internal module names have the format sonicparanoid.<module_name>
    tmpName: str = ""
    for name in moduleNames:
        tmpName = f"sonicparanoid.{name}"
        if tmpName in loadedMods:
            # Set the logger for the current module
            # NOTE: this way they are refencing the same formatter,
            # This might create problems if for example the formatter is modified by one module
            # a qui solution would be to directly create the formatters in the loop
            # Use the reference to the module to set the logger
            if rootLoggingLev == logging.DEBUG:
                sys.modules[tmpName].set_logger(loggerName=sys.modules[tmpName].__name__, lev=rootLoggingLev, propagate=False, customFmt = defaultDebugFmt)
            else:
                sys.modules[tmpName].set_logger(loggerName=sys.modules[tmpName].__name__, lev=rootLoggingLev, propagate=False, customFmt = defaultInfoFmt)
            loadedCnt += 1
        else:
            invalidNames.append(tmpName)

    debugStr = f"set_loggers :: REPORT\n\
    Total modules loaded in namespace:\t{len(loadedMods)}\n\
    Module loggers set:\t{loadedCnt}\n\
    Invalid module names:\t{invalidNames}"
    logger.debug(debugStr)



def set_main_logger(loggerName: str, lev: int, propagate: bool) -> None:
    """Set the logger for the main module"""
    global logger
    logger = logging.getLogger(loggerName)
    logger.setLevel(lev)
    logger.propagate = propagate
    # Create the handler and 
    clsLogger: logging.StreamHandler = logging.StreamHandler(stream=sys.stdout)
    # This makes sure that the log file is created even if not in debug mode
    clsLogger.setLevel(logger.level)
    # Set the formatter
    if lev == logging.DEBUG:
        clsLogger.setFormatter(logging.Formatter("{levelname} :: {name} :: ln{lineno}:\n{message}", style="{"))
    else:
        clsLogger.setFormatter(logging.Formatter("{levelname}:\n{message}", style="{"))
    # Add llogger
    logger.addHandler(clsLogger)
    # write some log about it!
    logger.debug(f"General logger for {loggerName} loaded!")



#####  MAIN  #####
def main():
    """Main function that merges ortholog tables inferred from architecture and alignment score graphs.
    This function should only be used for debugging.
    """
    # get SonicParanoid version
    softVersion = pkg_resources.get_distribution("sonicparanoid").version
    # start measuring the execution time
    ex_start = time.perf_counter()
    #Get the parameters
    args, parser = get_params(softVersion)
    del parser
    # start setting the needed variables
    debug: bool = args.debug
    # Set warning level
    filter_warnings(debug)

    # input dir
    graphTblsDir: str = os.path.realpath(args.graph_ortho_tbl_dir)
    archTblsDir: str = os.path.realpath(args.arch_ortho_tbl_dir)

    # Run dir
    runDir: str = os.path.realpath(args.run_dir)
    # output dir
    outDir: str = os.path.realpath(args.output_dir)
    outDirPrefix: str = args.prefix

    # Others
    threads: int = args.threads
    logLevel: int = logging.INFO
    if debug:
        logLevel = logging.DEBUG

    # Initialize root Logger
    if debug:
        logging.basicConfig(format='{levelname} :: {name}:\n{message}', style="{", level=logging.DEBUG)
    else:
        # logging.basicConfig(level=logging.INFO)
        logging.basicConfig(format='{levelname}:\n{message}', style="{", level=logging.INFO)

    # Set the logger for the main
    set_main_logger(loggerName="test-dev-merge-arch-and-graph-based-orthologs.py", lev=logLevel, propagate=False)

    infoStr: str = f"""Orthologs will be merged using the following settings settings:\n\
    Graph-based tables: {graphTblsDir}
    Arch-based tables: {archTblsDir}
    Run directory: {runDir}
    Output directory: {outDir}
    Out dir prefix:\t{outDirPrefix}
    Threads:\t{threads}"""
    logger.info(infoStr)
    # Check the imported modules
    imported = sys.modules.keys()

    # set the logger for each internal module
    internalModuleNames: list[str] = ["dev_cluster_merge", "sys_tools", "workers", "archortho"]
    set_loggers(rootLogger=logger, moduleNames=internalModuleNames)

    # create out dir
    systools.makedir(outDir)
    # obtain the input paths

    # FIXME: This should be provided as parameter
    masterArchDictPath: str = "/home/salvocos/Desktop/sonicparanoid-arch-analysis/test-directory/domainoid-hand-check/models/master.archs.dict.hs0n5.qcov070.pckl"
    # load the master dictionary
    # NOTE; check d2v.pyx for more info on the content of the master dict
    print("Loading master arch dictionary...")
    archMasterDict: dict[int, dict[int, Arch]] = pickle.load(open(masterArchDictPath, "rb"))

    # Load required information
    seqCntDict: dict[str, int] = {}
    proteomeSizeDict: dict[str, int] = {}
    proteomeSizeDict, seqCntDict = load_run_info(runDir)
    # Compute the species combinations
    spListInt: list[int] = [int(x) for x in list(seqCntDict.keys())]
    spPairs: list[tuple[int, int]] = list(combinations(spListInt, r=2))

    print(f"Species pairs:\t{len(spPairs)}")
    # print(spPairs[:4])
    # print(spListInt)

    # Extract the path of ortholog tables
    # pair2Paths: dict[tuple[int, int], tuple[str, str]] = get_ortho_table_paths(inDirGraphBased=graphTblsDir, inDirArchBased=archTblsDir, spPairs=copy(spPairs))
    # for p, paths in pair2Paths.items():
    #     print(f"{p}:\n{paths[0]}\n{paths[1]}")
    #     break

    # FIXME: this is hardcoded
    gPath: str = ""
    aPath: str = ""
    sp1: int = 0
    sp2: int = 0

    # tuple[dict[int, MergedClstr], dict[int, tuple[int, float]], dict[int, tuple[int, float]]]
    # initiliaze the datastructure that will contain the info on graph-based clusters
    mClstrDict: dict[int, any] = {} # these might ultimately contain the merged clusters
    graphSp1Ortho2info: dict[int, tuple[int, float]] = {}
    graphSp2Ortho2info: dict[int, tuple[int, float]] = {}
    aClstrDict: dict[int, any] = {}

    totPairs: int = 0
    tmpOutPath: str = ""
    tmpPairsFilePath: str = ""

    totPairs: int = 0

    # spPairs = [(23, 33)] # Ecoli-Hsapiens
    # spPairs = [(2, 50)]
    # spPairs = [(1, 2)]
    # spPairs = [(6, 49)]
    # spPairs = [(2, 21)] # Agambiae-Drerio
    # spPairs = [(1, 11)]
    # spPairs = [(8, 26)] # Btaurus-Gorilla
    # spPairs = [(7, 43)]
    # print(spPairs)

    # Coverage ofr arch-based orthologs
    covThr: float = 0.75

    # FIXME: hardcoded!
    '''
    archOrthoMtxPath: str = "/home/salvocos/Desktop/sonicparanoid-arch-analysis/test-directory/arch-based-predictions/qfo20-from-raw-prof-searches/tmp-arch-orthologs-predictions/arch_mtx/8-26.1to1.ortho.mtx.npz"
    # Load the Matrix
    archOrthoMtx: csr_matrix = load_npz(archOrthoMtxPath)
    archClsuterOutDir: str = "/home/salvocos/Desktop/sonicparanoid-arch-analysis/test-directory/arch-based-predictions/qfo20-from-raw-prof-searches/tmp-arch-orthologs-predictions/arch_orthologs/"
    domortho.cluster_arch_orthologs(sp1=8, sp2=26, M=archOrthoMtx, outDir=archClsuterOutDir, writePairs=False)

    # test arch-clstr loading from pickle
    pcklsDir: str = "/home/salvocos/Desktop/sonicparanoid-arch-analysis/test-directory/graph-arch-orto-merging/input-clusters/arch-based/cluster-files-pckl"
    pcklPath: str = os.path.join(pcklsDir, "8-26.arch.ortho.pckl")
    merger.load_arch_ortho_pckl(pcklPath)
    '''

    merger.parallel_integrate_arch_ortho_into_gclstr(spPairs, inDirGraphBased=graphTblsDir, inDirArchBased=archTblsDir, archMasterDict=archMasterDict, outDir=outDir, covThr=covThr, threads=threads)
    sys.exit("DEBUG: Cluster merging done!")



    # Prune all arch based clusters and write to file
    for p in spPairs:
        sp1, sp2 = p
        gPath, aPath = pair2Paths[p]
        # print(f"\nSpecies pair:\t{sp1}-{sp2}\n")

        # print(gPath)
        # print(aPath)
        # Load graph based orthologs
        mClstrDict, graphSp1Ortho2info, graphSp2Ortho2info = merger.load_graph_orto_tbl(tblPath=gPath)
        # Load arch based orthologs
        aClstrDict = merger.load_arch_orto_tbl(tblPath=aPath)
        # print(len(aClstrDict))
        # Write the clusters to output files
        tmpOutPath = os.path.join(outDir, os.path.basename(aPath))
        write_arch_based_clusters_to_file(aClstrDict, tmpOutPath)
        # tmpPairsFilePath = os.path.join(outDir, f"pairs.{os.path.basename(aPath)}")
        # totPairs += write_arch_based_pairs_to_file(aClstrDict, tmpPairsFilePath)

        # Integrate Arcj based clusters into Graph-based clusters
        merger.integrate_arch_ortho_into_gclstr(aClstrDict=aClstrDict, mClstrDict=mClstrDict, graphSp1Ortho2info=graphSp1Ortho2info, graphSp2Ortho2info=graphSp2Ortho2info, sp1Id=sp1, sp2Id=sp2, archMasterDict=archMasterDict)


    # print(f"Tot. arch based pairs:\t{totPairs}")
    # print(f"Clusters from Arch predictions:\t{len(aClstrDict)}")
    # Write clusters to file
    # print(aPath)
    # print(outDir)

    sys.exit("DEBUG: Cluster merging done!")


    '''
    # Create a string with the settings
    tmpParamStr: str = str(mtcov).replace(".", "")
    runSettingStr: str = f"{outDirPrefix}.bits{mbitscore}.tcov{tmpParamStr}.mulen{mulen}"
    tmpParamStr = str(mtotqcov).replace(".", "")
    runSettingStr: str = f"{runSettingStr}.qcov{tmpParamStr}.mbsize{mbsize}"
    archExtractionDir: str = os.path.join(outDir, f"archs.{runSettingStr}")
    systools.makedir(archExtractionDir)
    '''

    ex_end = round(time.perf_counter() - ex_start, 3)
    sys.stdout.write(f"\nTotal elapsed time (seconds):\t{ex_end:.3f}\n")


if __name__ == "__main__":
    main()
