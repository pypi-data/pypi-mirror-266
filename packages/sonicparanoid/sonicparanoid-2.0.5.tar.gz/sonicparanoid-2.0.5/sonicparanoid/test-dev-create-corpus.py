# -*- coding: utf-8 -*-
"""Debug program that extract documents from files with raw architectures."""
import os
import sys
import logging
import argparse
from shutil import copy, rmtree, move, which
import time
from typing import Dict, List, Tuple, Set
import zipfile
import filetype
import pkg_resources
import pickle

# Use this for profiling
import pstats, cProfile


# IMPORT INTERNAL PACKAGES
# from sonicparanoid import dev_profile_search as psearch
# from sonicparanoid import dev_domortho as domortho
from sonicparanoid import dev_d2v as d2v
from sonicparanoid import sys_tools as systools
from sonicparanoid import hdr_mapping as idmapper
from sonicparanoid import workers



########### FUNCTIONS ############

# This logger will used for the main
logger: logging.Logger = logging.getLogger()


def get_params(softVersion):
    """Parse and analyse command line parameters."""
    # Help
    parser = argparse.ArgumentParser(description=f"SonicParanoid {softVersion} - debug program",  usage='%(prog)s -i <INPUT_DIRECTORY> -o <OUTPUT_DIRECTORY>[options]', prog="sonic-debug-create-corpus-search")
    parser.add_argument("-i", "--input-raw-documents", type=str, required=True, help="File containing the documents to be filtered\n", default=None)
    parser.add_argument("-o", "--output-dir", type=str, required=True, help="The directory in which the output will be stored.", default="")
    parser.add_argument("-mrep", "--max-repeats", type=int, required=False, help="Max number of times an single document can be repeated (e.g. by default it is set to 1 to avoid bias).", default=1)
    parser.add_argument("-t", "--threads", type=int, required=False, help="Maximum number of CPUs to be used. Default=4", default=1)
    parser.add_argument("-at", "--add-tags", required=False, help="Add tags to the pickle file (this can be used to train gensim doc2vec using an iterator). It also implies --store-as-iterator", default=False, action="store_true")
    parser.add_argument("-si", "--store-as-iterator", required=False, help="Store the corpus as a Gensim iterator (Note: training could be slower, but protein IDs are include in the pickle)", default=False, action="store_true")
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
    # rootLogger.debug(debugStr)
    logger.debug(debugStr)

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
    """Main function processes documents and generates the vocabulary.
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
    addTags: bool = args.add_tags
    saveAsPickle: bool = args.store_as_iterator
    # Set warning level
    # filter_warnings(debug)
    filter_warnings(debug)

    # input file with all documents
    rawDocsPath: str = os.path.realpath(args.input_raw_documents)
    # output dir
    outDir: str = os.path.realpath(args.output_dir)
    # Extra parameters
    maxrep: int = args.max_repeats
    threads: int = args.threads
    logLevel: int = logging.INFO
    if debug:
        logLevel = logging.DEBUG
    # outSuffix: str = args.suffix

    # Initialize root Logger
    if debug:
        logging.basicConfig(format='{levelname} :: {name}:\n{message}', style="{", level=logging.DEBUG)
    else:
        # logging.basicConfig(level=logging.INFO)
        logging.basicConfig(format='{levelname}:\n{message}', style="{", level=logging.INFO)

    # Set the logger for the main
    set_main_logger(loggerName="test-dev-create-corpus", lev=logLevel, propagate=False)

    infoStr: str = f"""Profile search settings:\n\
    File with all documents: {rawDocsPath}
    Output directory: {outDir}
    Max number of repetition for a single document:\t{maxrep}
    Add query IDs to documents:\t{addTags}
    Save corpus as iterator in pickle:\t{saveAsPickle}
    Threads:\t{threads}"""
    logger.info(infoStr)
    # Check the imported modules
    imported = sys.modules.keys()

    # set the logger for each internal module
    internalModuleNames: List[str] = ["dev_d2v", "sys_tools", "workers"]
    set_loggers(rootLogger=logger, moduleNames=internalModuleNames)

    # create out dir
    systools.makedir(outDir)

    outFileName: str = "corpus"
    if not(addTags):
        outFileName = f"{outFileName}.no_tags"
    if maxrep > 1:
        outFileName = f"{outFileName}.reps{maxrep}"
    outFileName = f"{outFileName}.{os.path.basename(rawDocsPath)}"
    outFilePath: str = os.path.join(outDir, outFileName)
    d2v.create_corpus_file(rawDocFilePath=rawDocsPath, outDocFilePath=outFilePath, maxRep=maxrep, addTags=addTags, saveAsPickle=saveAsPickle)

    sys.exit("DEBUG: test-dev_create_corpus.py")

    ex_end = round(time.perf_counter() - ex_start, 3)
    sys.stdout.write(f"\nCorpus creation elapsed time (seconds):\t{ex_end:.3f}\n")


if __name__ == "__main__":
    main()
