# -*- coding: utf-8 -*-
"""
    Compare ortholog pairs generated from graph- and arch-based predictions.
    The script performs the following steps:
    - Compute stats on the 2 two sets
    - Merge the pairs into a single one
"""



from __future__ import annotations

import os
import sys
import argparse
import subprocess
from typing import TextIO
# from collections import Counter, namedtuple
import logging


# Now load the wanted module
from sonicparanoid import sys_tools as systools
# from sonicparanoid import domain_orthology as domortho
# from sonicparanoid import hdr_mapping as idmapper



########### FUNCTIONS ############
def get_params():
    """General test script."""
    parser_usage = "\nProvide the two prediction sets that should be compared.\n"
    parser = argparse.ArgumentParser(description="General test script.", usage=parser_usage)
    #start adding the command line options
    parser.add_argument("--set1", type=str, required=True, help="File the first set of predictions.\n", default="")
    parser.add_argument("--set2", type=str, required=True, help="File the second set of predictions.\n", default="")
    parser.add_argument("-o", "--output-dir", type=str, required=True, help="The directory in which the files (if any) will be stored.", default=None)
    parser.add_argument("-t", "--threads", type=int, required=False, help="Maximum number of CPUs to be used. Default=4", default=4)
    parser.add_argument("-m", "--merge", required=False, help="Output a file containing the union of the two sets.\nNOTE: this is not used when the input is STDIN.", default=False, action="store_true")
    parser.add_argument("-d", "--debug", required=False, help="Output debug information.\nNOTE: this is not used when the input is STDIN.", default=False, action="store_true")
    args = parser.parse_args()
    return (args, parser)





def load_set1(set1Path: str, outDir: str, debug: bool = False) -> Tuple[Set[Tuple[str, str]], int, int]:
    """
    Read the first file and perfom simple counts.
    """
    if debug:
        print(f"\nload_set1 :: START")
        print(f"Set1 path: {set1Path}")
        print(f"Output directory: {outDir}")

    # Tmp variables
    totPairs: int = 0
    p1: str = ""
    p2: str = ""
    tmpPair: tuple[str, str] = ("", "")
    tmpInv: tuple[str, str] = ("", "")
    bname: str = os.path.basename(set1Path)
    tmpPath: str = os.path.join(outDir, f"fixed.{bname}")

    # Output file descriptor
    ofd: TextIO = open(tmpPath, "wt", encoding="utf8")

    # Use sets to assure that the pairs from different species are on the same column
    sPairs: set[tuple[str, str]] = set()
    sProts: set[str] = set()

    # Write a file in which the pairs are inverted if required
    for ln in open(set1Path, "rt", encoding="utf8"):
        p1, p2 = ln.rstrip("\n").split("\t", 1)
        sProts.add(p1)
        sProts.add(p2)
        tmpPair = (p1, p2)
        tmpInv = (p2, p1)
        # Make sure it is not in the other set
        if (tmpPair not in sPairs) and (tmpInv not in sPairs):
            sPairs.add(tmpPair)
            totPairs += 1
        else:
            print(ln)
            logging.error(f"Pair {tmpPair} or {tmpInv} is repeated!")
            exit(-5)
    ofd.close()

    logging.info(f"Total pairs in set1 ({os.path.basename(set1Path)}):\t{totPairs}")
    logging.info(f"Uniq proteins in set1:\t{len(sProts)}")

    # return
    # Set with Tuple containing the uniq pairs
    # Count of uniq pairs
    # Count of uniq proteins
    return (sPairs, totPairs, len(sProts))



def load_set2_knowing_set1(set2Path: str, outDir: str, s1Pairs: tuple[set[tuple[str, str]], int, int], debug: bool = False) -> tuple[set[tuple[str, str]], int, int]:
    """
    Read the second file and invert pair names based on what found in set 1.
    """
    if debug:
        print(f"\nload_set2_knowing_set1 :: START")
        print(f"Set2 path: {set2Path}")
        print(f"Pairs from set 1:\t{len(s1Pairs)}")
        print(f"Output directory: {outDir}")

    # Tmp variables
    totPairs: int = 0
    p1: str = ""
    p2: str = ""
    tmpPair: tuple[str, str] = ("", "")
    tmpInv: tuple[str, str] = ("", "")
    repeatedPairsCnt: int = 0
    uniqPairsCnt: int = 0
    invertPairsCnt: int = 0
    bname: str = os.path.basename(set2Path)
    tmpPath: str = os.path.join(outDir, f"fixed.{bname}")
    # Output file descriptor
    ofd: TextIO = open(tmpPath, "wt", encoding="utf8")

    # Use sets to assure that the pairs from different species are on the same column
    s2Pairs: set[tuple[str, str]] = set()
    s2Prots: set[str] = set()

    # Write a file in which the pairs are inverted if required

    for ln in open(set2Path, "rt", encoding="utf8"):
        p1, p2 = ln.rstrip("\n").split("\t", 1)
        s2Prots.add(p1)
        s2Prots.add(p2)
        tmpPair = (p1, p2)
        tmpInv = (p2, p1)
        # First check if the pair was not in set 1
        if tmpPair in s1Pairs:
            repeatedPairsCnt += 1
            s2Pairs.add(tmpPair)
            ofd.write(ln)
        elif tmpInv in s1Pairs:
            repeatedPairsCnt += 1
            s2Pairs.add(tmpInv)
            # print(f"Invert found:\t{tmpInv}")
            ofd.write(f"{p2}\t{p1}\n")
            invertPairsCnt += 1
        # The the pair is uniq
        else:
            uniqPairsCnt += 1
            s2Pairs.add(tmpPair)
            ofd.write(ln)
        # increment main counter
        totPairs += 1

    ofd.close()

    debugStr: str = f"""load_set2_knowing_set1 :: REPORT
    Total pairs in set2 ({os.path.basename(set2Path)}):\t{totPairs}
    Uniq proteins in set2:\t{len(s2Prots)}
    Pct of shared pairs:\t{(repeatedPairsCnt/len(s2Pairs)) * 100.:.2f}
    Pairs that were inverted:\t{invertPairsCnt}"""
    logger.debug(debugStr)

    # return
    # Set with Tuple containing the uniq pairs
    # Count of uniq pairs
    # Count of uniq proteins
    return (s2Pairs, totPairs, len(s2Prots))



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



########### MAIN ############
def main():
    """Compare sets of orthologs from graph- and arch-based predictions"""
    #Get the parameters
    args = get_params()[0]
    debug: bool = args.debug
    # Prediction files
    set1Path = os.path.realpath(args.set1)
    set2Path = os.path.realpath(args.set2)
    outDir = os.path.realpath(args.output_dir)
    mergeSets: bool = args.merge
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
    set_main_logger(loggerName="test-dev-compare-and-merge-predicted-pairs.py", lev=logLevel, propagate=False)

    # Show some info
    infoStr: str = f"""Set comparison parameters:\n\
    Prediction set 1: {set1Path}
    Prediction set 2: {set2Path}
    Output directory: {outDir}
    Merge sets:\t{mergeSets}
    Threads:\t{threads}"""
    logger.info(infoStr)


    # Check that the required files exist
    if not os.path.isfile(set1Path):
        logging.error(f"The file with predictions \n{set1Path} is not valid!")
        sys.exit(-2)
    if not os.path.isfile(set2Path):
        logging.error(f"The file with predictions \n{set2Path} is not valid!")
        sys.exit(-2)

    # set the logger for each internal module
    internalModuleNames: list[str] = ["sys_tools"]
    set_loggers(rootLogger=logger, moduleNames=internalModuleNames)

    # create out dir
    systools.makedir(outDir)

    # Load the first set
    s1Pairs: Set[Tuple[str, str]] = set()
    s2Pairs: Set[Tuple[str, str]] = set()
    s1PairsCnt: int = 0
    s2PairsCnt: int = 0
    s1Prots: int = 0
    s2Prots: int = 0

    # Load the two sets
    s1Pairs, s1PairsCnt, s1Prots = load_set1(set1Path, outDir=outDir, debug=debug)
    s2Pairs, s2PairsCnt, s2Prots = load_set2_knowing_set1(set2Path, outDir, s1Pairs, debug=debug)

    print(len(s1Pairs), len(s2Pairs))

    # Start doing set operations
    # tmpSet: Set[Tuple[str, str]] = set()

    # Find shared pairs
    # print(f"Union:\t{len(s1Pairs.union(s2Pairs))}")
    intersectCnt = len(s1Pairs.intersection(s2Pairs))
    print(len(s2Pairs.intersection(s1Pairs)))
    logging.info(f"Pct of S2 in S1:\t{(intersectCnt/len(s2Pairs)) * 100.:.2f}")
    print(f"Intersection:\t{intersectCnt}")


    # Merge the two sets if required
    outPath: str = ""
    ofd: TextIO = None
    if mergeSets:
        outPath = os.path.join(outDir, "merged.pairs.s1_s2.tsv")
        sortPath: str = os.path.join(outDir, "tmp.sorted.s1_s2.tsv")
        ofd = open(outPath, "wt", encoding="utf8")
        for p1, p2 in s1Pairs.union(s2Pairs):
            ofd.write(f"{p1}\t{p2}\n")
        ofd.close()

        ##### sort the output file #######
        sortCmd: str = f"sort -o {sortPath} -k1,1 -k2,2 {outPath}"
        print(f"Sorting file with pairs:\n{sortCmd}")
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




    # print(f"Difference (Set1 - Set2):\t{len(s1Pairs.difference(s2Pairs))}")
    # print(f"Difference (Set2 - Set1):\t{len(s2Pairs.difference(s1Pairs))}")
    # print(f"Elements not shared between Set1 and Set 2:\t{len(s1Pairs ^ s2Pairs)}")

if __name__ == "__main__":
    main()
