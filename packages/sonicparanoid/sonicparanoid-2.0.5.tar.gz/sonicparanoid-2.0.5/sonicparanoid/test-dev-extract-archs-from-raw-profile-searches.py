# -*- coding: utf-8 -*-
"""Debug program to extract archs from profiles search results files."""
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

# IMPORT INTERNAL PACKAGES
from sonicparanoid import dev_profile_search as psearch
from sonicparanoid import dev_d2v as d2v
from sonicparanoid import sys_tools as systools
from sonicparanoid import hdr_mapping as idmapper
from sonicparanoid import workers



########### FUNCTIONS ############

# This logger will used for the main
logger: logging.Logger = logging.getLogger()
__module_name__: str = "test-dev_profile_search"


def get_params(softVersion):
    """Parse and analyse command line parameters."""
    # Help
    parser = argparse.ArgumentParser(description=f"SonicParanoid {softVersion} - debug program",  usage='%(prog)s -i <INPUT_DIRECTORY> -o <OUTPUT_DIRECTORY>[options]', prog="sonic-debug-profile-search")
    parser.add_argument("-i", "--input-dir", type=str, required=True, help="Input directory\n", default=None)
    parser.add_argument("-r", "--run-dir", type=str, required=True, help="Directory in which SonicParanoid run files are stored. These include auxliary files with mapping dictionaries.\n", default=None)
    parser.add_argument("-o", "--output-dir", type=str, required=True, help="The directory in which the output will be stored.", default="")
    parser.add_argument("-mbits", "--min-bitscore", type=int, required=False, help="Minimum bitscore for profiles hits to be considered.", default=30)
    parser.add_argument("-mtcov", "--min-tcov", type=float, required=False, help="Minimum profile coverage, for a profile hit to be considered.", default=0.75)
    parser.add_argument("-mtotqcov", "--min-total-query-cov", type=float, required=False, help="Minimum tota query coverage (e.g. considering all profile hits) for an architecture to be considered.", default=0.10)
    parser.add_argument("-mul", "--min-uncovered-len", type=int, required=False, help="Lenght of shortest uncovered region. Set to 5 by default as the shorted domain in PFamA is 7aa long", default=5)
    parser.add_argument("-mbsize", "--missing-bin-size", type=int, required=False, help="Size of bins for missing interregions. Ex.: if mbsize=5 missing domains are assigned the word ceil((end-start+1)/mbsize) ", default=5)
    parser.add_argument("--prefix", type=str, required=False, help="Prefix for output directory", default="archs")
    parser.add_argument("-t", "--threads", type=int, required=False, help="Maximum number of CPUs to be used. Default=4", default=1)
    parser.add_argument("-d", "--debug", required=False, help="Output debug information. (WARNING: extremely verbose)", default=False, action="store_true")
    # parse the arguments
    args = parser.parse_args()

    return (args, parser)



def get_input_paths(inDir: str) -> Tuple[List[str], List[str]]:
    """Check that at least 2 files are provided."""
    debugStr: str = f"get_input_paths :: START\n\
        inDir: {inDir}"
    logger.debug(debugStr)

    tmpPath: str = ""
    # associate a path to each file name
    fname2path: Dict[str, str] = {}
    for f in os.listdir(inDir):
        if f == ".DS_Store":
            continue
        # Raw search file should end with '.blast.tsv'
        if f.endswith(".blast.tsv"):
            tmpPath = os.path.join(inDir, f)
            if os.path.isfile(tmpPath):
                fname2path[f] = tmpPath
    # check that at least two input files were provided
    if len(fname2path) == 0:
        logger.error(f"The directory with the input files contains no valid raw profile search files.\nPlease generate the profile search files before continuing.\n")
        sys.exit(-5)
    # sort the dictionary by key to avoid different sorting
    # on different systems due to os.listdir()
    sortedDict: Dict[str, str] = dict(sorted(fname2path.items()))
    del fname2path
    return (list(sortedDict.keys()), list(sortedDict.values()))



def filter_warnings(debug:bool=False):
    """Show warnings only in debug mode"""
    if not debug:
        import warnings
        warnings.filterwarnings("ignore")



def load_run_info(runDir: str) -> Tuple[Dict[str, int], Dict[str, int]]:
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

    # input dir
    inDir: str = os.path.realpath(args.input_dir)
    # Run dir
    runDir: str = os.path.realpath(args.run_dir)
    # output dir
    outDir: str = os.path.realpath(args.output_dir)
    outDirPrefix: str = args.prefix
    # Extra parameters
    mbitscore: int = args.min_bitscore
    mtcov: int = args.min_tcov
    mtotqcov: int = args.min_total_query_cov
    mulen: int = args.min_uncovered_len
    mbsize: int = args.missing_bin_size
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
    set_main_logger(loggerName=__module_name__, lev=logLevel, propagate=False)

    infoStr: str = f"""Profile search settings:\n\
    Input directory: {inDir}
    Run directory: {runDir}
    Output directory: {outDir}
    Min bitscore for profiles:\t{mbitscore}
    Min target profile:\t{mtcov}
    Min total query coverage for architectures:\t{mtotqcov}
    Shortest uncovered interregion (aa):\t{mulen}
    Missing bin size:\t{mbsize}
    Out dir prefix:\t{outDirPrefix}
    Threads:\t{threads}"""
    logger.info(infoStr)
    # Check the imported modules
    imported = sys.modules.keys()

    logger.warning("Arch extraction is not parallelized, hence the --threads parameter will be ignored.")

    # set the logger for each internal module
    internalModuleNames: List[str] = ["dev_d2v", "dev_profile_search", "sys_tools", "workers"]
    set_loggers(rootLogger=logger, moduleNames=internalModuleNames)

    # create out dir
    systools.makedir(outDir)
    # obtain the input paths
    inPaths: List[str] = []
    speciesList: List[str] = []
    speciesList, inPaths = get_input_paths(inDir)

    # Load required information
    seqCntDict: Dict[str, str] = {}
    proteomeSizeDict: Dict[str, str] = {}
    proteomeSizeDict, seqCntDict = load_run_info(runDir)

    # Create a string qith the settings
    tmpParamStr: str = str(mtcov).replace(".", "")
    runSettingStr: str = f"{outDirPrefix}.bits{mbitscore}.tcov{tmpParamStr}.mulen{mulen}"
    tmpParamStr = str(mtotqcov).replace(".", "")
    runSettingStr: str = f"{runSettingStr}.qcov{tmpParamStr}.mbsize{mbsize}"
    archExtractionDir: str = os.path.join(outDir, runSettingStr)
    systools.makedir(archExtractionDir)
    print(archExtractionDir)

    # Start performing the extraction 1 file at time
    for fpath in inPaths:
        searchFileName = os.path.basename(fpath)
        spName = searchFileName.split("-", 1)[0]
        seqCnt = seqCntDict[spName]
        psearch.pfam_hits2architecture(blastResults=fpath, outDir=archExtractionDir, seqCnt=seqCnt, minbits=mbitscore, minUncovLen=mulen, mintcov=mtcov, minTotQueryCov=mtotqcov)
        # break


    sys.exit("DEBUG: Arch extraction completed!")

    ex_end = round(time.perf_counter() - ex_start, 3)
    sys.stdout.write(f"\nTotal elapsed time (seconds):\t{ex_end:.3f}\n")



if __name__ == "__main__":
    main()
