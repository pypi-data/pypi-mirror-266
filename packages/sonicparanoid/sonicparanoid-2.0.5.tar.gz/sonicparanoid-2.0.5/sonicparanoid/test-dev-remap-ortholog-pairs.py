# -*- coding: utf-8 -*-
"""
    Debug program to remap file with ortholog pairs with the internal id to the original protein id.
    The script performs the following steps:
    - Load run information
    - Load protein id mapping idctionaries
    - Read the file with pairs and write a new with the remapped IDs
"""

from __future__ import annotations

import os
import sys
import logging
import argparse
import time
import subprocess
from typing import TextIO
import pickle
import warnings
import pkg_resources


# IMPORT INTERNAL PACKAGES
from sonicparanoid import sys_tools as systools



########### FUNCTIONS ############

# This logger will used for the main
logger: logging.Logger = logging.getLogger()


def get_params(softVersion):
    """Parse and analyse command line parameters."""
    # Help
    parser = argparse.ArgumentParser(description=f"SonicParanoid {softVersion} - debug program",  usage='%(prog)s -i <INPUT_DIRECTORY> -o <OUTPUT_DIRECTORY>[options]', prog="test-dev-remap-ortholog-pairs")
    parser.add_argument("-i", "--input", type=str, required=True, help="File with ortholog pairs to remap.\n", default=None)
    parser.add_argument("-r", "--run-dir", type=str, required=True, help="Directory in which SonicParanoid run files are stored. These include auxliary files with mapping dictionaries.\n", default=None)
    parser.add_argument("-o", "--output-dir", type=str, required=True, help="The directory in which the output will be stored.", default="")
    parser.add_argument("--prefix", type=str, required=False, help="Prefix for output directory", default="archs")

    # Other parameters
    parser.add_argument("-t", "--threads", type=int, required=False, help="Maximum number of CPUs to be used. Default=4", default=1)
    parser.add_argument("-d", "--debug", required=False, help="Output debug information. (WARNING: extremely verbose)", default=False, action="store_true")
    # parse the arguments
    args = parser.parse_args()

    return (args, parser)



def load_mapping_pckls(inDir: str) -> dict[int, dict[str, str]]:
    """Load the pckl files with protein FASTA headers for re-mapping."""
    debugStr: str = f"load_mapping_pckls :: START\n\
        inDir: {inDir}"
    logger.debug(debugStr)

    tmpMappingDict: dict[str, str] = {}
    tmpPath: str = ""
    # Will contain the species name
    spId: int = 0
    # associate a path to each file name
    sp2mappingDict: dict[int, dict[str, str]] = {}
    for f in os.listdir(inDir):
        if f == ".DS_Store":
            continue
        # Mapping pckl files should be called simialr to 'hdr_42.pckl'
        if f.startswith("hdr_") and f.endswith(".pckl"):
            # Extract the species ID
            spId = int(f[4:-5])
            tmpPath = os.path.join(inDir, f)
            if os.path.isfile(tmpPath):
                # load the pickle
                tmpMappingDict = pickle.load(open(tmpPath, "rb"))
                sp2mappingDict[spId] = tmpMappingDict
    # check that at least two input files were provided
    if len(sp2mappingDict) == 0:
        logger.error("""The directory with the input files contains no valid mapping pckl files.
        \nPlease generate the pckl mapping files before continuing.\n""")
        sys.exit(-5)
    # sort the dictionary by key to avoid different sorting
    # on different systems due to os.listdir()
    sp2mappingDict = dict(sorted(sp2mappingDict.items()))
    return sp2mappingDict



def remap_pairs(inTbl: str, outTbl: str, spHdrMappingDicts: dict[int, dict[str, str]]) -> None:
    """Remapping ortholog pairs with the original FASTA headers."""
    debugStr: str = f"""remap_pairs :: START
        inTbl: {inTbl}
        outTbl: {outTbl}
        spHdrMappingDicts:\t{len(spHdrMappingDicts)}"""
    logger.debug(debugStr)

    # tmp variables
    pairsCnt: int = 0
    spIdInt: int = 0
    toRemap: str = ""
    flds: list[str] = []
    remappedSp2: str = ""
    remappedSp1: str = ""

    # open the output file
    ofd: TextIO = open(outTbl, "wt", encoding="utf8")

    # Start processing the input table
    with open(inTbl, "rt", encoding="utf8") as ifd:
        for ln in ifd:
            pairsCnt += 1
            flds = ln[:-1].split("\t", 1)
            # Remap the protein from sp1
            toRemap = flds[0]
            spIdInt = int(toRemap.split(".", 1)[0])
            remappedSp1 = spHdrMappingDicts[spIdInt][toRemap]
            # Remap the protein from sp2
            toRemap = flds[1]
            spIdInt = int(toRemap.split(".", 1)[0])
            remappedSp2 = spHdrMappingDicts[spIdInt][toRemap]
            ofd.write(f"{remappedSp1}\t{remappedSp2}\n")
            # break

    ofd.close()

    print(f"Remapped pairs:\t{pairsCnt}")



def sort_pairs(inTbl: str) -> None:
    """Sort a file with ortholog pairs."""
    # The file must have only 2 columns separated by a TAB
    debugStr: str = f"""sort_pairs :: START
        Pairs file to sort: {inTbl}"""
    logger.debug(debugStr)

    if not os.path.isfile(inTbl):
        sys.stderr.write(f"ERROR: the file\n{inTbl}\nwas not found...")
        sys.exit(-2)
    outDir: str = os.path.dirname(inTbl)
    bname: str = os.path.basename(inTbl)
    sortPath: str = os.path.join(outDir, f"sorted.{bname}")

    ##### sort the output file #######
    sortCmd: str = f"sort -o {sortPath} -k1,1 -k2,2 {inTbl}"
    print(f"Sorting file with pairs:\n{sortCmd}")
    # use run (or call)
    runOut = subprocess.run(sortCmd, shell=True, check=True)
    if runOut.returncode != 0:
        logging.error("Something went wrong while sorting the output!")
        sys.exit(-10)

    # remove the unsorted output and rename
    os.remove(inTbl)
    os.rename(sortPath, inTbl)




def filter_warnings(debug:bool=False):
    """Show warnings only in debug mode"""
    if not debug:
        warnings.filterwarnings("ignore")



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

    # input pairs file
    inTbl: str = os.path.realpath(args.input)
    # Run dir
    runDir: str = os.path.realpath(args.run_dir)
    # output dir
    outDir: str = os.path.realpath(args.output_dir)
    outDirPrefix: str = args.prefix

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
    set_main_logger(loggerName="test-dev-remap-ortholog-pairs.py", lev=logLevel, propagate=False)

    infoStr: str = f"""Arch extraction and corpus creation settings:\n\
    Input directory: {inTbl}
    Run directory: {runDir}
    Output directory: {outDir}
    Out dir prefix:\t{outDirPrefix}
    Threads:\t{threads}"""
    logger.info(infoStr)

    # set the logger for each internal module
    # internalModuleNames: list[str] = ["dev_d2v", "dev_profile_search", "dev_domortho", "sys_tools", "workers"]
    internalModuleNames: list[str] = ["sys_tools"]
    set_loggers(rootLogger=logger, moduleNames=internalModuleNames)

    # create out dir
    systools.makedir(outDir)

    # Check that the input table exists
    if not os.path.isfile(inTbl):
        logger.error(f"The input file table could not be found!\n{inTbl}")
        sys.exit(-2)

    # Load the mapping pickles
    seqInfoDict: str = os.path.join(runDir, "aux/input_seq_info")
    print(seqInfoDict)
    spHdrMappingDicts: dict[int, dict[str, str]] = load_mapping_pckls(seqInfoDict)

    pairsBasename: str = os.path.basename(inTbl)
    print(pairsBasename)
    outTblName: str = f"{outDirPrefix}.{pairsBasename}.remapped.tsv"
    outTbl: str = os.path.join(outDir, outTblName)
    remap_pairs(inTbl=inTbl, outTbl=outTbl, spHdrMappingDicts=spHdrMappingDicts)

    sort_pairs(outTbl)

    '''
    # Merge the two sets if required
    outPath: str = ""
    ofd: TextIO = None
    if mergeSets:
        outPath = os.path.join(outDir, "merged.pairs.s1_s2.tsv")
        sortPath: str = os.path.join(outDir, "tmp.sorted.s1_s2.tsv")

        ##### sort the output file #######
        sortCmd: str = f"sort -o {sortPath} -k1,1 -k2,2 {outPath}"
        # use run (or call)
        runOut = subprocess.run(sortCmd, shell=True, check=True)
        if runOut.returncode != 0:
            logging.error("Something went wrong while sorting the output!")
            sys.exit(-10)

        if not os.path.isfile(outPath):
            sys.stderr.write(f"WARNING: the file\n{outPath}\nwas not found...")
        # remove the unsorted output and rename
        os.remove(outPath)
        os.rename(sortPath, outPath)
        ############################################
    '''

    ex_end = round(time.perf_counter() - ex_start, 3)
    sys.stdout.write(f"\nTotal elapsed time (seconds):\t{ex_end:.3f}\n")


if __name__ == "__main__":
    main()
