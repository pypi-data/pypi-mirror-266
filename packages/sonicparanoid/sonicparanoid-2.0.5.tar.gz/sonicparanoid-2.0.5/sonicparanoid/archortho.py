"""
 Contains function to perform domain-architecture-based orthology inference.
"""
from __future__ import annotations

import os
import sys
import logging
from time import perf_counter, sleep
from shutil import rmtree
from itertools import combinations
from pickle import load

# from sonicparanoid import inpyranoid
from sonicparanoid import sys_tools as systools
from sonicparanoid.profile_search import parallel_profile_search_1pass, obtain_precomputed_profiles
from sonicparanoid.d2v import compute_archs_and_embeddings
from sonicparanoid.domortho import parallel_infer_arch_orthologs
from sonicparanoid.ortho_merger import parallel_integrate_arch_ortho_into_gclstr


# Logger that will be used in this module
# It is child of the root logger and
# should be initialiazied using the function set_logger()
logger: logging.Logger = logging.getLogger()



__module_name__ = "Archortho"
__source__ = "archortho.py"
__author__ = "Salvatore Cosentino"
__license__ = "GPL"
__version__ = "0.4"
__maintainer__ = "Cosentino Salvatore"
__email__ = "salvo981@gmail.com"



def info():
    """
    Contains functions that will process queued jobs
    """
    print(f"MODULE NAME:\t{__module_name__}")
    print(f"SOURCE FILE NAME:\t{__source__}")
    print(f"MODULE VERSION:\t{__version__}")
    print(f"LICENSE:\t{__license__}")
    print(f"AUTHOR:\t{__author__}")
    print(f"EMAIL:\t{__email__}")


### Worker functions (1 cpu) ###



### Job processing Functions
def check_pfama_profile_db(threads: int = 4) -> str:
    """Verifies that the profile database for PfamA exists"""
    pfamFilesDir: str = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pfam_files")
    pfamProfilesArchive: str = os.path.join(pfamFilesDir, "pfama-mmseqs.tar.gz")
    profileDbBname: str = "pfama.mmseqs"

    debugStr: str = f"""check_pfama_profile_db :: START
    Directory with PfamA files: {pfamFilesDir}
    Profile DB archive: {pfamProfilesArchive}
    """
    logger.debug(debugStr)

    # Variables used in case of error
    emailSC1: str = "salvo981@gmail.com"
    emailSC2: str = "salvocos@k.u-tokyo.ac.jp"
    emailWI1: str = "iwasaki@k.u-tokyo.ac.jp"
    webpage: str = "http://iwasakilab.k.u-tokyo.ac.jp/sonicparanoid/"
    # Variables to verify the exstance of the profile DB files
    fSuffixes: list[str] = [".dbtype", ".version", ".index", "_h", "_h.dbtype", "_h.index"]
    tmpPath: str = ""
    kmer: int = 5
    sens: float = 7.0
    index: int = 1
    writeLog: int = 1
    mainFilesOK: bool = True
    idxFilesOK: bool = True

    # If the archive file is missing then we should stop
    if not os.path.isfile(pfamProfilesArchive):
        logger.error(f"The archive with PfamA profiles could not be found at\n{pfamProfilesArchive}")
        print("Please check the instruction on how to obtain the Profile DB, or contact the authors.")
        print("\nINSTRUCTIONS:")
        print(f"Check the usage of SonicParanoid at\n{webpage}\n")

        print("\nCONTACT:")
        print(f"Salvatore Cosentino:\t{emailSC1}  or  {emailSC2}")
        print(f"Wataru Iwasaki:      \t{emailWI1}")
        return ""
    else:
        # Check if the profile DB has been installed and indexed
        profileDbDir: str = os.path.join(pfamFilesDir, "profile_db")
        profileDbPath: str = os.path.join(profileDbDir, profileDbBname)

        # Verify that the all the DB files are present
        for f in fSuffixes:
            tmpPath = f"{profileDbPath}{f}"
            if not os.path.isfile(tmpPath):
                # logger.warning(f"The profiles DB file\n{tmpPath}\nwas not found!\n\
                #     Please create the profile database before proceeding.")
                mainFilesOK = False
        if not os.path.isfile(profileDbPath):
            mainFilesOK = False
        # If any of the main files does not exist
        # 1) remove the directory where it was supposed to be (if it exists)
        # 2) Extract the archive and index the database
        if not mainFilesOK:
            logger.info("The PfamA profile DB was not found and will now be created.")
            # print(profileDbDir)
            if os.path.isdir(profileDbDir):
                # remove all its content
                # NOTE: rmtree crashes on Network attached file systems if the directory is not empty
                try:
                    rmtree(profileDbDir)
                except OSError:
                    sleep(1)
                    rmtree(profileDbDir, ignore_errors=True)  # solve shutil NFS bug, ignore errors, file removal is less important
            # Create the directory if needed
            systools.makedir(profileDbDir)
            # Extract and index the profile DB for PfamA
            print("\n###### PfamA profile DB ceation and indexing ######")
            logger.info("It might take a few minutes,\nand will be done only at the first run after the installation.")
            obtain_precomputed_profiles(archivePath=pfamProfilesArchive, outDir=profileDbDir, kmer=kmer, sens=sens, threads=threads, index=index, writeLog=writeLog)

            # Verify that the all the DB files are present
            mainFilesOK = True
            for f in fSuffixes:
                tmpPath = f"{profileDbPath}{f}"
                if not os.path.isfile(tmpPath):
                    logger.error(f"The profiles DB file\n{tmpPath}\nwas not found!\nPlease create the profile database before proceeding.")
                    mainFilesOK = False

        if mainFilesOK:
            logger.debug("All the required files for the PfamA profile DB were found! ")
    
        # Verify that all the indexing file for the profile DB are avaliable
        for f in [".idx.index", ".idx", ".idx.dbtype"]:
            tmpPath = f"{profileDbPath}{f}"
            if not os.path.isfile(tmpPath):
                logger.warning(f"The indexing file for the profiles DB\n{tmpPath}\nwas not found!")
                idxFilesOK = False

        if not idxFilesOK:
            # Remove all the indexing files if some of them exists
            for f in [".idx.index", ".idx", ".idx.dbtype"]:
                tmpPath = f"{profileDbPath}{f}"
                if os.path.isfile(tmpPath):
                    os.remove(tmpPath)
            # Extract and index profile Database
            if os.path.isdir(profileDbDir):
                # remove all its content
                # NOTE: rmtree crashes on Network attached file systems if the directory is not empty
                try:
                    rmtree(profileDbDir)
                except OSError:
                    sleep(1)
                    rmtree(profileDbDir, ignore_errors=True) # solve shutil NFS bug, ignore errors, file removal is less important

            # Create the directory if needed
            systools.makedir(profileDbDir)
            # Extract and index the profile DB for PfamA
            print("\n###### PfamA profile DB ceation and indexing ######")
            logger.info("It might take a few minutes,\nand will be done only at the first run after the installation.")
            obtain_precomputed_profiles(archivePath=pfamProfilesArchive, outDir=profileDbDir, kmer=kmer, sens=sens, threads=threads, index=index, writeLog=writeLog)
        # Verify the indexing files again
        idxFilesOK = True
        for f in [".idx.index", ".idx", ".idx.dbtype"]:
            tmpPath = f"{profileDbPath}{f}"
            if not os.path.isfile(tmpPath):
                logger.warning(f"The indexing file for the profiles DB\n{tmpPath}\nwas not found!")
                idxFilesOK = False

    if idxFilesOK and mainFilesOK:
        logger.debug(f"The PfamA profile DB is installed in\n{profileDbPath}")
    else:
        return ""

    # print(f"idxFilesOK:\t{idxFilesOK}")
    # print(f"mainFilesOK:\t{mainFilesOK}")

    return profileDbPath




def get_arch_file_paths(inDir: str, spCnt: int) -> list[str]:
    """Obtain paths to the arch files."""
    logger.debug(f"""get_arch_file_paths :: START
        inDir: {inDir}""")

    tmpPath: str = ""
    loadedPaths: int = 0
    # associate a path to each file name
    fpaths: list[str] = []
    for f in os.listdir(inDir):
        if f == ".DS_Store":
            continue
        # The file names should have the following pattern
        # <sp>-pfama.mmseqs.<run-settings>.tsv
        #or <sp>-pfama.mmseqs.archs.tsv
        if ("-pfama.mmseqs." in f) and f.endswith(".tsv"):
            tmpPath = os.path.join(inDir, f)
            if os.path.isfile(tmpPath):
                fpaths.append(tmpPath)

    loadedPaths = len(fpaths)

    # The number of loaded paths and species must be the same
    if loadedPaths != spCnt:
        logger.error(f"The directory with the architectures contains {loadedPaths} files when {spCnt} are expected.\nPlease generate the {spCnt} architecture files.\n")
        sys.exit(-5)

    # sort the list to avoid different sorting
    # on different systems due to os.listdir()
    return sorted(fpaths)



def infer_arch_based_orthologs(mappedInPaths: list[str], outDir: str, runDir: str, seqDbDir: str, modelPrefix: str, overwrite_all: bool, overwrite_tbls: bool, update_run: bool, compress: bool, complev: int, tblMergeThr: float = 0.75, threads: int = 4):
    """Infer ortholog comporaing the domain archiutectures of the input proteomes"""
    # Paths to mapped input files
    logger.info("infer_arch_based_orthologs :: START")

    # Check if the PFam profile DB exists
    pfamProfPath: str = check_pfama_profile_db(threads=threads)

    print(f"Main output directory: {outDir}")
    print(f"Run directory: {runDir}")
    print(f"DB directory: {seqDbDir}")
    print(f"PfamA profile DB: {pfamProfPath}")
    print(f"Table merging thr: {tblMergeThr:.2f}")

    # Set the main directory for arch orthology
    archOrthoDir: str = os.path.join(outDir, "arch_orthology")
    systools.makedir(archOrthoDir)
    profSearchOutDir: str = os.path.join(archOrthoDir, "profile_search")
    systools.makedir(profSearchOutDir)
    archsOutDir: str = os.path.join(archOrthoDir, "architectures")
    systools.makedir(archsOutDir)

    # Load protein counts
    spToSearchStr: list[str] = [os.path.basename(x) for x in mappedInPaths]
    spCnt: int = len(spToSearchStr)
    protCntDict: dict[str, int] = load(open(os.path.join(runDir, "aux/protein_counts.pckl"), "rb"))

    # Settings for profile search
    profSearchKmer: int = 5
    profSearchSens: float = 7.0
    minBitscore: int = 30
    # Minimum length in aa for a reagion to be considered as uncovered
    minUncovLen: int = 5
    # Minimum coverage for a profile hit to be kept
    minTargetCov: float = 0.75
    # Bin size of words representing uncovered regions
    missingBinSize: int = 1
    # Minimum query coverage for an architecture to be considered
    minTotQueryCov: float = 0.7

    # Start the time
    sys.stdout.write("\nStart domain architecture-based orthology inference.")
    timer_start = perf_counter()

    ##### Profile search #####
    parallel_profile_search_1pass(spToSearch=spToSearchStr, protCntDict=protCntDict, runDir=runDir, dbDir=seqDbDir, pfamProfPath=pfamProfPath, profSearchOutDir=profSearchOutDir, archsOutDir=archsOutDir, kmer=profSearchKmer, sens=profSearchSens, minBitscore=minBitscore, minUncovLen=minUncovLen, minTargetCov=minTargetCov, missingBinSize=missingBinSize, minTotQueryCov=minTotQueryCov, noArchs=False, compress=False, complev=5, threads=threads)

    #### Create the documents and train the neural network ####
    # obtain the input paths
    rawArchPaths: list[str] = get_arch_file_paths(inDir=archsOutDir, spCnt=spCnt)

    ##### Document extraction and ANN training #####

    # Parameters for the training data creation
    maxreps: int = 1 # Max repetition in training for each Arch
    # Parameters for the model
    algorithm: int = 0 # use pv-dbow skip gram
    vsize: int = 100
    wsize: int = 2
    mwcnt: int = 1
    dbowWords: int = 1 # Can be used only when algorithm=1
    epochs: int = 200
    storePerSpeciesArchPckl: bool = False

    # This function performs the model training
    # and assigns embeddings to the architectures
    compute_archs_and_embeddings(rawArchFilePaths=rawArchPaths, minqcov=minTotQueryCov, mbsize=missingBinSize, outDir=archOrthoDir, skipUnknown=False, maxRep=maxreps, addTags=False, saveAsPickle=False, modelPrefix=modelPrefix, algorithm=algorithm, vectorSize=vsize, window=wsize, minCnt=mwcnt, useAllWords=True, epochs=epochs , dbowWords=dbowWords, dumpArchDicts=storePerSpeciesArchPckl, threads=threads)
    ########################

    ##### Infer arch-orhtlogs #####
    modelsDir: str = os.path.join(archOrthoDir, "models")
    systools.makedir(modelsDir)
    # Contains the Archs for each species,
    # and each Arch is updated with the embeddings
    masterPcklPath: str = os.path.join(modelsDir, "master.archs.dict.pckl")
    # Load the dictionary
    # The dictionary associates to each speacies
    # and each gene an architecture and its embeddings
    archMasterDict: dict[int, dict[int, any]] = load(open(masterPcklPath, "rb"))

    # Compute the pairs
    spToSearchInt: list[int] = [int(x) for x in spToSearchStr]
    spPairs: list[tuple[int, int]] = list(combinations(spToSearchInt, r=2))

    # Output directories
    archMtxDir: str = os.path.join(archOrthoDir, "arch_mtx")
    systools.makedir(archMtxDir)
    archTblsDir: str = os.path.join(archOrthoDir, "arch_orthologs")
    systools.makedir(archTblsDir)

    # TODO: some of the below parameter
    # could be CLI parameters
    domCntDiffThr: float = 2.0
    maxCovDiff: float = 0.25
    lenDiffThr: float = 3.0
    minCosine: float = 0.5
    createMtxFiles: bool = False

    # Predict arch-based orthologs
    parallel_infer_arch_orthologs(spPairs=spPairs, archMasterDict=archMasterDict, seqCntDict=protCntDict, outDir=archOrthoDir, lenDiffThr=lenDiffThr, maxCovDiff=maxCovDiff, domCntDiffThr=domCntDiffThr, minCosine=minCosine, storeMtx=createMtxFiles,threads=threads)
    ########################

    ##### Merge ortholog tables #####
    # Directory with graph based predictions
    graphTblsDir: str = os.path.join(outDir, "orthologs_db")
    if not os.path.isdir(graphTblsDir):
        logger.error(f"The directory with the graph-based table could is not valid:\n{graphTblsDir}")
        sys.exit(-2)
    # Directory with merged tables
    mergedTblsDir: str = os.path.join(outDir, "merged_tables")
    systools.makedir(mergedTblsDir)
    # This can be used to control the sentivity
    # of the predictions when merging the tables
    # covThr: float = 0.80

    parallel_integrate_arch_ortho_into_gclstr(spPairs, inDirGraphBased=graphTblsDir, inDirArchBased=archTblsDir, archMasterDict=archMasterDict, outDir=mergedTblsDir, covThr=tblMergeThr, threads=threads)

    # sys.exit("DEBUG: archortho.py :: Cluster merging done!")
    ########################

    sys.stdout.write(f"Arch-based orthology inference elapsed time (seconds):\t{round(perf_counter() - timer_start, 3)}\n")

    # Return the directory in which the merged tables are stored
    return mergedTblsDir



def set_logger(loggerName: str, lev: int, propagate: bool, customFmt: logging.Formatter = None) -> None:
    """Set the global logger for this module"""
    global logger
    logger = logging.getLogger(loggerName)
    logger.setLevel(lev)
    logger.propagate = propagate
    # Create the handler and 
    clsLogger: logging.StreamHandler = logging.StreamHandler(stream=sys.stdout)
    # This makes sure that the log file is created even if not in debug mode
    clsLogger.setLevel(logger.level)
    # Set the formatter
    if customFmt is not None:
        clsLogger.setFormatter(customFmt)
    logger.addHandler(clsLogger)
    # write some log about it!
    logger.debug(f"General logger for {loggerName} loaded!")