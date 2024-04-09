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
import pickle
from itertools import combinations
import pkg_resources
from shutil import rmtree

# Use this for profiling
# import pstats, cProfile

# IMPORT INTERNAL PACKAGES
from sonicparanoid import sys_tools as systools
from sonicparanoid import archortho



########### FUNCTIONS ############

# This logger will used for the main
logger: logging.Logger = logging.getLogger()


def get_params(softVersion):
    """Parse and analyse command line parameters."""
    # Help
    parser = argparse.ArgumentParser(description=f"SonicParanoid {softVersion} - debug program",  usage='%(prog)s -i <INPUT_DIRECTORY> -o <OUTPUT_DIRECTORY>[options]', prog="sonic-debug-infer-domain-orthologs")
    parser.add_argument("-i", "--input-dir", type=str, required=True, help="Input directory\n", default=None)
    parser.add_argument("-r", "--run-dir", type=str, required=True, help="Directory in which SonicParanoid run files are stored. These include auxliary files with mapping dictionaries.\n", default=None)
    parser.add_argument("-o", "--output-dir", type=str, required=True, help="The directory in which the output will be stored.", default="")
    # parser.add_argument("-db", "--seqs-db-dir", type=str, required=True, help="The directory in which the MMseqs database files will be stored.", default="")
    parser.add_argument("-p", "--prefix", type=str, required=False, help="Prefix for output directory", default="archs")

    # Other parameters
    parser.add_argument("-t", "--threads", type=int, required=False, help="Maximum number of CPUs to be used. Default=4", default=1)
    parser.add_argument("-c", "--clean", required=False, help="Remove directories and files that would not be used.", default=False, action="store_true")
    parser.add_argument("-d", "--debug", required=False, help="Output debug information. (WARNING: extremely verbose)", default=False, action="store_true")
    # parse the arguments
    args = parser.parse_args()

    return (args, parser)



def cleanup(inDir: str) -> None:
    """Remove directories and files that will not be used."""
    logger.debug(f"""cleanup :: START
        inDir: {inDir}""")

    tmpPath: str = ""
    dirsToRemove: list[str] = ["arch_mtx", "arch_orthologs", "documents", "architectures"]

    for dname in dirsToRemove:
        tmpPath = os.path.join(inDir, f"arch_orthology/{dname}")
        if os.path.isdir(tmpPath):
            rmtree(tmpPath)

    # Remove some files inside the model dir
    modelsDir: str = os.path.join(inDir, "arch_orthology/models")

    # Remove model files
    for f in os.listdir(modelsDir):
        if f == ".DS_Store":
            continue
        if (f.endswith(".allw")) or (f.endswith(".pckl")) or (f.endswith(".npy")):
            tmpPath = os.path.join(modelsDir, f)
            if os.path.isfile(tmpPath):
                os.remove(tmpPath)

    # Delete directory with MMseqs DB files
    mmseqsDb: str = os.path.join(inDir, "mmseqs_dbs")
    if os.path.isdir(mmseqsDb):
        rmtree(mmseqsDb)

    # Delete profile search files
    profSearchDir: str = os.path.join(inDir, "arch_orthology/profile_search")
    for f in os.listdir(profSearchDir):
        if f == ".DS_Store":
            continue
        if f.endswith("blast.tsv"):
            tmpPath = os.path.join(profSearchDir, f)
            if os.path.isfile(tmpPath):
                os.remove(tmpPath)



def get_input_paths(inDir: str) -> tuple[list[str], list[str]]:
    """Check that at least 2 files are provided."""
    debugStr: str = f"get_input_paths :: START\n\
        inDir: {inDir}"
    logger.debug(debugStr)

    tmpPath: str = ""
    # associate a path to each file name
    fname2path: dict[str, str] = {}
    for f in os.listdir(inDir):
        if f == ".DS_Store":
            continue
        # Raw search file should end with '.blast.tsv'
        tmpPath = os.path.join(inDir, f)
        if os.path.isfile(tmpPath):
            fname2path[f] = tmpPath

    # check that at least two input files were provided
    if len(fname2path) == 0:
        logger.error("The directory with the input files contains no proteome files.\n")
        sys.exit(-5)
    # sort the dictionary by key to avoid different sorting
    # on different systems due to os.listdir()
    sortedDict: dict[str, str] = dict(sorted(fname2path.items()))
    del fname2path
    return (list(sortedDict.keys()), list(sortedDict.values()))



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



def set_loggers(rootLogger: logging.Logger, moduleNames: list[str]):
    """Set loggers for each loaded module"""
    debugStr: str = f"set_loggers :: START\n\
    rootLogger:\t{rootLogger}\n\
    Module names:\t{moduleNames}"
    # rootLogger.debug(debugStr)
    logger.debug(debugStr)

    # At least one module name must be in the names list
    if len(moduleNames) == 0:
        sys.stdout.write("WARNING: no module names in the list.\nYou must provide at least one name of imported module.")

    # Set counters
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
    """Main function that performs inference of an ortholog table.
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
    inDir: str = os.path.realpath(args.input_dir)
    # Run dir
    runDir: str = os.path.realpath(args.run_dir)
    # output dir
    outDir: str = os.path.realpath(args.output_dir)
    # MMseqs DB dir
    # dbDir: str = os.path.realpath(args.seqs_db_dir)
    dbDir: str = os.path.join(outDir, "mmseqs_dbs")
    outPrefix: str = args.prefix

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
    scriptName: str = "test-dev-infer-domain-orthologs.py"
    set_main_logger(loggerName=scriptName, lev=logLevel, propagate=False)

    infoStr: str = f"""Domain-based pipeline will be performed with the following settings:\n\
    Input directory: {inDir}
    Run directory: {runDir}
    Output directory: {outDir}
    MMseqs DB directory: {dbDir}
    Output prefix:\t{outPrefix}
    Threads:\t{threads}"""
    logger.info(infoStr)

    # Create some output directories
    systools.makedir(outDir)
    systools.makedir(dbDir)
    # Fake empty directory to fool the domain orthology inference method
    systools.makedir(os.path.join(outDir, "orthologs_db"))

    # set the logger for each internal module
    # internalModuleNames: list[str] = ["dev_d2v", "dev_profile_search", "dev_domortho", "sys_tools", "workers"]
    internalModuleNames: list[str] = ["archortho", "sys_tools"]
    set_loggers(rootLogger=logger, moduleNames=internalModuleNames)

    # Obtain input paths
    # tuple[list[str], list[str]]:
    protPathsMapping: tuple[list[str], list[str]] = get_input_paths(inDir = inDir)

    ''' Not needed for now
    # Obtain protein sequence counts
    proteomeInfoTpl: tuple[dict[str, int], dict[str, int]] = load_run_info(runDir = runDir)

    print(proteomeInfoTpl[0])

    print(protPathsMapping)
    print(protPathsMapping[0])

    # Remove all entries that are not in the dictionary and that we will not use
    for i in protPathsMapping[0]:
        print(f"Proteomes size sp {i}:\t{proteomeInfoTpl[0][i]}")
        print(f"Protein cnt sp {i}:\t{proteomeInfoTpl[1][i]}")
    '''

    pairwiseDbDir: str = archortho.infer_arch_based_orthologs(mappedInPaths=protPathsMapping[1], outDir=outDir, runDir=runDir, seqDbDir=dbDir, modelPrefix=outPrefix, overwrite_all=False, overwrite_tbls=False, update_run=False, compress=not(True), complev=5, tblMergeThr=0.75, threads=threads)

    ex_end = round(time.perf_counter() - ex_start, 3)
    sys.stdout.write(f"\nTotal elapsed time (seconds):\t{ex_end:.3f}\n")

    # Remove unnecessary files and dirs
    if args.clean:
        cleanup(outDir)

if __name__ == "__main__":
    main()
