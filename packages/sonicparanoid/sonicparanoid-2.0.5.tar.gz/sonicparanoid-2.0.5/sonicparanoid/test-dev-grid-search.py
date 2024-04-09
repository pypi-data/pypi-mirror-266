# -*- coding: utf-8 -*-
"""
    Debug program that performs the following steps:
    - Extract documents from files with raw architectures
    - Generate corpus and documents for training
    - Training and evaluate multiple doc2vec models
"""
import os
import sys
import logging
import argparse
from shutil import copy, rmtree, move, which
import time
from typing import Dict, List, Tuple, Set
import filetype
import pkg_resources
import pickle

# Use this for profiling
# import pstats, cProfile


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
    parser = argparse.ArgumentParser(description=f"SonicParanoid {softVersion} - debug program",  usage='%(prog)s -i <INPUT_DIRECTORY> -o <OUTPUT_DIRECTORY>[options]', prog="sonic-debug-profile-search")
    parser.add_argument("-i", "--input-dir", type=str, required=True, help="Input directory\n", default=None)
    parser.add_argument("-o", "--output-dir", type=str, required=True, help="The directory in which the output will be stored.", default="")
    parser.add_argument("-p", "--prefix", type=str, required=False, help="Prefix for the output file with documents\n", default="documents")
    parser.add_argument("-mtotqcov", "--min-total-query-cov", type=float, required=False, help="Minimum total query coverage (e.g. considering all profile hits) for an architecture to be considered.", default=0.10)
    parser.add_argument("-mbsize", "--missing-bin-size", type=int, required=False, help="Size of bins for missing interregions. Ex.: if mbsize=5 missing domains are assigned the word ceil((end-start+1)/mbsize)", default=5)

    # Corpus creation related options
    parser.add_argument("-mrep", "--max-repeats", type=int, required=False, help="Max number of times an single document can be repeated in corpus (e.g. by default it is set to 1 to avoid bias).", default=1)
    parser.add_argument("-at", "--add-tags", required=False, help="Add tags to the pickle file (this can be used to train gensim doc2vec using an iterator). It also implies --store-as-iterator", default=False, action="store_true")
    # NOTE: the following feature is not suggested since gensim training is much faster when using a plain text file
    parser.add_argument("-si", "--store-as-iterator", required=False, help="Store the corpus as a Gensim iterator (Note: training could be slower, but protein IDs are include in the pickle)", default=False, action="store_true")

    # Grid search options
    parser.add_argument("-a", "--algorithm", required=True, type=int, help="doc2vec model type. If algorithm=1, ‘distributed memory’ (PV-DM) is used. Otherwise, PV-DBOW (using skip-gram) is employed.", choices=[0, 1], default=0)
    parser.add_argument("-dbw", "--dbow-words", required=False, type=int, help="Train also the word-verctors (only supported by PV-DBOW [algorithm=0].", choices=[0, 1], default=0)

    parser.add_argument("-t", "--threads", type=int, required=False, help="Maximum number of CPUs to be used. Default=4", default=1)
    parser.add_argument("-d", "--debug", required=False, help="Output debug information. (WARNING: extremely verbose)", default=False, action="store_true")
    # parse the arguments
    args = parser.parse_args()

    return (args, parser)



def get_input_paths(inDir: str) -> List[str]:
    """Check that the is at least 1 file."""
    logger.debug(f"""get_input_paths :: START
        inDir: {inDir}""")

    tmpPath: str = ""
    # associate a path to each file name
    fpaths: List[str] = []
    for f in os.listdir(inDir):
        if f == ".DS_Store":
            continue
        tmpPath = os.path.join(inDir, f)
        if os.path.isfile(tmpPath):
            fpaths.append(tmpPath)
    # check that at least two input files were provided
    if len(fpaths) < 1:
        fnamesStr: str = '\n'.join(fpaths)
        logger.error(f"The directory with the input files only contains {len(fpaths)} ({fnamesStr}) files.\nPlease provide at least 1 file with raw architectures.\n")
        sys.exit(-5)
    # sort the dictionary by key to avoid different sorting
    # on different systems due to os.listdir()
    return (sorted(fpaths))



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
    """Main function that processes files with raw arch information.
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
    algorithm: int = args.algorithm
    dbowWords: int = args.dbow_words

    # Set warning level
    filter_warnings(debug)

    # input file
    inDir: str = os.path.realpath(args.input_dir)
    # output dir
    outDir: str = os.path.realpath(args.output_dir)
    # Extra parameters
    mtotqcov: int = args.min_total_query_cov
    mbsize: int = args.missing_bin_size
    maxreps: int = args.max_repeats
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
    set_main_logger(loggerName="test-dev-grid-search", lev=logLevel, propagate=False)

    infoStr: str = f"""Profile search settings:\n\
    Input directory: {inDir}
    Output directory: {outDir}
    Min total query coverage for architectures:\t{mtotqcov}
    Missing bin size:\t{mbsize}
    Max number of repetition for a single document:\t{maxreps}
    Add query IDs to documents:\t{addTags}
    Save corpus as iterator in pickle:\t{saveAsPickle}
    Algorithm:\t{algorithm}
    Train word vector for PV-DBOW_SG:\t{dbowWords}
    Threads:\t{threads}"""
    logger.info(infoStr)
    # Check the imported modules
    imported = sys.modules.keys()

    # set the logger for each internal module
    internalModuleNames: List[str] = ["dev_d2v", "sys_tools", "workers"]
    set_loggers(rootLogger=logger, moduleNames=internalModuleNames)

    # create out dir
    systools.makedir(outDir)

    # obtain the input paths
    inPaths: List[str] = get_input_paths(inDir=inDir)
    mtotqcovStr: str = str(mtotqcov).replace(".", "")
    outRawDocsFileBasename: str = f"{args.prefix}.mqcov{mtotqcovStr}.mbsize{mbsize}"
    outRawDocsPath: str = os.path.join(outDir, f"{outRawDocsFileBasename}.txt")

    '''
    # Profile execution time
    profileFilePath: str = os.path.join(outDir, "Profile.prof")
    # cProfile.runctx("d2v.extract_documents(rawArchFile=testInRawFilePath, mbsize=mbsize, ofd=ofd, outDir=outDir, skipUnknown=False)", globals(), locals(), profileFilePath)
    cProfile.runctx("d2v.parallel_extract_documents(rawArchFilePaths=inPaths, mbsize=mbsize, outDocFilePath=outRawDocsPath, outDir=outDir, skipUnknown=False, threads=threads)", globals(), locals(), profileFilePath)
    s = pstats.Stats(profileFilePath)
    s.strip_dirs().sort_stats("time").print_stats()
    '''

    d2v.parallel_extract_documents(rawArchFilePaths=inPaths, minqcov=mtotqcov, mbsize=mbsize, outDocFilePath=outRawDocsPath, outDir=outDir, skipUnknown=False, threads=threads)
    # sys.exit("DEBUG: test-dev-grid-search.py :: grid-search (document extraction completed)")

    # Prepare directories and path for corpus files
    trainingDocumentsDir: str = os.path.join(outDir, "training-files")
    systools.makedir(trainingDocumentsDir)
    corpusFileName: str = "corpus"
    if not(addTags):
        corpusFileName = f"{corpusFileName}.no_tags"
    if maxreps > 1:
        corpusFileName = f"{corpusFileName}.reps{maxreps}"
    corpusFileName = f"{corpusFileName}.{os.path.basename(outRawDocsPath)}"
    corpusFilePath: str = os.path.join(trainingDocumentsDir, corpusFileName)
    d2v.create_corpus_file(rawDocFilePath=outRawDocsPath, outDocFilePath=corpusFilePath, maxRep=maxreps, addTags=addTags, saveAsPickle=saveAsPickle)
    # sys.exit("DEBUG: test-dev-grid-search.py :: grid-search (compus created)")

    modelDir: str = os.path.join(outDir, "models")
    systools.makedir(modelDir)
    # FIXME: hard coded
    # corpusFilePath = "/home/salvocos/Desktop/sonicparanoid-arch-analysis/test-directory/arch-extraction/extraction-and-training/training-files/corpus.no_tags.qfo20.tcov050.mqcov075.mbsize5.2k.txt"
    # corpusFilePath = "/home/salvocos/Desktop/sonicparanoid-arch-analysis/test-directory/arch-extraction/extraction-and-training/training-files/corpus.no_tags.qfo20.tcov050.mqcov075.mbsize5.txt"
    # corpusFilePath = "/home/salvocos/Desktop/sonicparanoid-arch-analysis/test-directory/arch-extraction/extraction-and-training/training-files/corpus.no_tags.qfo20.tcov075.mqcov075.mbsize5.txt"
    # corpusFilePath = "/home/salvocos/Desktop/sonicparanoid-arch-analysis/test-directory/arch-extraction/extraction-and-training/training-files/corpus.no_tags.qfo20.tcov075.mqcov075.mbsize5.5K.txt"
    modelPrefix: str = os.path.basename(corpusFilePath).rstrip(".txt")
    modelPrefix = f'{modelPrefix.lstrip("corpus.no_tags.")}'
    print(corpusFilePath)
    print(modelPrefix)
    # sys.exit("DEBUG: test-dev-grid-search.py :: corpus creation completed")

    evalModels: bool = True
    d2v.grid_search_d2v_gensim(corpusPath=corpusFilePath, outDir=modelDir, modelPrefix=modelPrefix, algorithm=algorithm, dbowWords=dbowWords, evaluateModels=evalModels, threads=threads)
    # sys.exit("DEBUG: test-dev-grid-search.py :: grid-search completed")

    ex_end = round(time.perf_counter() - ex_start, 3)
    sys.stdout.write(f"\nTotal elapsed time (seconds):\t{ex_end:.3f}\n")


if __name__ == "__main__":
    main()
