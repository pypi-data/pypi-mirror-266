# -*- coding: utf-8 -*-
"""Debug program that creates a pfam profile db and performs profile searches."""
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
from sonicparanoid import dev_profile_search as psearch
from sonicparanoid import sys_tools as systools
from sonicparanoid import hdr_mapping as idmapper


########### FUNCTIONS ############
def get_params(softVersion):
    """Parse and analyse command line parameters."""
    # Help
    parser = argparse.ArgumentParser(description=f"SonicParanoid {softVersion} - debug program",  usage='%(prog)s -i <INPUT_DIRECTORY> -o <OUTPUT_DIRECTORY>[options]', prog="sonic-debug-profile-search")
    parser.add_argument("-dt", "--db-type", type=str, required=False, help="Type of PFamA DB to be created.", choices=["seed", "full"], default="seed")
    parser.add_argument("-o", "--output-dir", type=str, required=True, help="The directory in which the output will be stored.", default="")
    parser.add_argument("-p", "--precomputed", type=str, required=False, help="Path to precomputed profile archive.", default="")
    parser.add_argument("-k", "--kmer", type=int, required=False, help="Kmer for indexing the profile DB.", default=5)
    parser.add_argument("-s", "--sens", type=float, required=False, help="Sensitivity used in profile DB indexing. Default=7.0", default=7.0)
    parser.add_argument("-idx", "--index", required=False, help="Generate the ubdex files for the database", default=False, action="store_true")
    # parser.add_argument("-s", "--suffix", type=str, required=False, help="Suffix for the output orhtolog table.", default="")
    parser.add_argument("-t", "--threads", type=int, required=False, help="Maximum number of CPUs to be used. Default=4", default=1)
    parser.add_argument("-d", "--debug", required=False, help="Output debug information. (WARNING: extremely verbose)", default=False, action="store_true")

    # parse the arguments
    args = parser.parse_args()

    return (args, parser)


def filter_warnings(debug:bool=False):
    """Show warnings only in debug mode"""
    if not debug:
        import warnings
        warnings.filterwarnings("ignore")



def set_loggers(rootLogger: logging.Logger, moduleNames: List[str] = []):
    """Set loggers for each loaded module"""
    debugStr: str = f"set_loggers :: START\n\
    rootLogger:\t{rootLogger}\n\
    Module names:\t{moduleNames}"
    rootLogger.debug(debugStr)

    # At least one module name must be in the names list
    if len(moduleNames) == 0:
        sys.stdout.write(f"WARNING: no module names in the list.\nYou must provide at least one name of imported module.")

    # Set counters
    totModules: int = len(moduleNames)
    rootLoggingLev: int = rootLogger.level
    loadedCnt: int = 0
    invalidNames: List[str] = []
    # set the default formatters
    defaultInfoFmt: logging.Formatter = logging.Formatter("{levelname}:\n{message}", style="{")
    # defaultDebugFmt: logging.Formatter = logging.Formatter("{levelname} :: {name}:\n{message}", style="{")
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
    rootLogger.debug(debugStr)



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
    idx: bool = args.index
    # Set warning level
    filter_warnings(debug)

    # initialize the root logger
    logger = logging.getLogger()
    # output dir
    outDir: str = os.path.realpath(args.output_dir)
    # Extra parameters
    dbtype: str = args.db_type
    kmers: int = args.kmer
    sens: float = args.sens
    archivePath: str = args.precomputed
    threads: int = args.threads

    # Initialize root Logger
    if debug:
        logging.basicConfig(format='{levelname} :: {name}:\n{message}', style="{", level=logging.DEBUG)
    else:
        # logging.basicConfig(level=logging.INFO)
        logging.basicConfig(format='{levelname}:\n{message}', style="{", level=logging.INFO)

    infoStr: str = f"    PFamA type:\t{dbtype}\n\
    KMER:\t{kmers}\n\
    Sensitivity:\t{sens}\n\
    Output directory: {outDir}\n\
    Precomputed profile DB: {archivePath}\n\
    Threads:\t{threads}"
    logging.info(infoStr)
    # Check the imported modules
    imported = sys.modules.keys()

    # set the logger for each internal module
    internalModuleNames: List[str] = ["dev_profile_search", "sys_tools"]
    set_loggers(rootLogger=logger, moduleNames=internalModuleNames)


    # create out dir
    systools.makedir(outDir)

    # Extract the precomputed profile DB
    if os.path.isfile(archivePath):
        psearch.obtain_precomputed_profiles(archivePath=archivePath, outDir=outDir, kmer=kmers, sens=sens, threads=threads, index=idx, writeLog=True)
    else:
        # Create profile database
        psearch.create_mmseqs_pfam_profile_db(dbtype, outDir, kmer=kmers, sens=sens, threads=threads, delTmp=True, compressed=False, index=idx, writeLog=True)

    sys.exit("DEBUG")

    ex_end = round(time.perf_counter() - ex_start, 3)
    sys.stdout.write(f"\nTotal elapsed time (seconds):\t{ex_end:.3f}\n")


if __name__ == "__main__":
    main()
