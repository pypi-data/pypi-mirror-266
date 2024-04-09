# -*- coding: utf-8 -*-
"""Execute the SonicParanoid."""
# NOTE: remove when the lowest python version will be 3.9
from __future__ import annotations
import os
import sys
import gc
import argparse
import platform
from shutil import copy, rmtree, move, which
import subprocess
import time
import zipfile
import numpy as np
import filetype
import pkg_resources
import logging

# IMPORT INTERNAL PACKAGES
from sonicparanoid import ortholog_detection as orthodetect
from sonicparanoid import orthogroups
from sonicparanoid import workers
from sonicparanoid import sys_tools as systools
from sonicparanoid import hdr_mapping as idmapper
from sonicparanoid import remap_tables_c as remap
from sonicparanoid import graph_c as graph
from sonicparanoid import mcl_c as mcl
from sonicparanoid import archortho

# This logger will used for the main
logger: logging.Logger = logging.getLogger()

########### FUNCTIONS ############
def get_params(softVersion):
    """Parse and analyse command line parameters."""
    # create the possible values for sensitivity value
    sensList: list[float] = []
    for i in range(1, 9):
        sensList.append(float(i))
        for j in range(1, 10):
            fval = float(i + float(j / 10.))
            if fval <= 7.5:
                sensList.append(fval)
    # define the parameter list
    parser = argparse.ArgumentParser(description=f"SonicParanoid {softVersion}",
        usage='%(prog)s -i <INPUT_DIRECTORY> -o <OUTPUT_DIRECTORY>[options]', prog="sonicparanoid")
    # Mandatory arguments
    parser.add_argument("-i", "--input-directory", type=str, required=True,
        help="Directory containing the proteomes (in FASTA format) of the species to be analyzed.",
            default="")
    parser.add_argument("-o", "--output-directory", type=str, required=True,
        help="The directory in which the results will be stored.",
            default="")
    # General run options
    parser.add_argument("-p", "--project-id",
        type=str,
        required=False,
        help="Name for the project reflecting the name of run. \
            If not specified it will be automatically generated using the current date and time.",
        default="")
    parser.add_argument("-sh", "--shared-directory",
        type=str,
        required=False,
        help="Directory in which the alignment files are stored. \
        If not specified it is created inside the main output directory.",
        default=None)
    parser.add_argument("-t", "--threads",
        type=int,
        required=False,
        help="Maximum number of CPUs to be used. Default=4",
        default=4)
    parser.add_argument("-at", "--force-all-threads",
        required=False,
        help="Force using all the requested threads.",
        action="store_true")
    parser.add_argument("-sm", "--skip-multi-species",
        required=False,
        help="Skip the creation of multi-species ortholog groups.",
        default=False,
        action="store_true")
    parser.add_argument("-d", "--debug",
        required=False,
        help="Show debug lines. WARNING: extremely verbose",
        default=False,
        action="store_true")
    parser.add_argument("-nc", "--no-compress",
        required=False,
        help="Skip the compression of processed alignment files.",
        default=False,
        action="store_true")
    parser.add_argument("-cl", "--compression-lev",
        type=int,
        required=False,
        help="Gzip compression level.\n Integer values between 1 and 9, \
with 9 and 1 being the highest lowest compression levels, respectively. Default=5",
        default=5)

    # pairwise orthology inference
    parser.add_argument("-m", "--mode",
        required=False,
        help="SonicParanoid execution mode. The default mode is suitable for most studies.\
        Use sensitive if the input proteomes are not closely related.",
        choices=["fast", "default", "sensitive"],
        default="default")
    parser.add_argument("-dmnd", "--diamond", required=False,
        help="Use Diamond with a custom sensitivity. This will bypass the -m (--mode) option.",
        choices=["fast", "mid-sensitive", "sensitive", "more-sensitive", "very-sensitive", "ultra-sensitive"],
        default="")
    parser.add_argument("-mmseqs", "--mmseqs", type=float, required=False,
        help="Use MMseqs2 with a custom sensitivity (between 1.0 and 7.5). This will bypass the -m (--mode) option.",
        default=0.)
    parser.add_argument("-blast", "--blast",
        required=False,
        help="Use Blastp for all-vs-all alignments. This will bypass the -m (--mode) option.",
        default=False,
        action="store_true")
    parser.add_argument("-ml", "--max-len-diff",
        type=float,
        required=False,
        help="Maximum allowed length-difference-ratio between main orthologs and canditate \
inparalogs.\nExample: 0.5 means one of the two sequences could be two times longer \
than the other\n 0 means no length difference allowed; 1 means any length difference allowed. \
Default=0.75",
        default=0.75)
    parser.add_argument("-db", "--seqs-dbs",
        type=str,
        required=False,
        help="The directory in which the database files created by the selectedlocal alignment \
tool will be stored. DEFAULT: automatically created inside the main output directory.",
        default=None)
    parser.add_argument("-idxdb", "--index-db",
        required=False,
        help="Index the MMSeqs2/Diamond databases. IMPORTANT: This will use more storage \
        but will be slighly faster (5~10%%) when processing many big proteomes with MMseqs2.\n\
        The results might also be sligthy different.",
        default=False,
        action="store_true")
    parser.add_argument("-op", "--output-pairs",
        required=False,\
        help="Output a text file with all the pairwise orthologous relationships.",
        default=False,
        action="store_true")
    parser.add_argument("-ka", "--keep-raw-alignments",
        required=False,
        help="Do not delete raw MMseqs2 alignment files. \
        NOTE: this will triple the space required for storing the results.",
        default=False,
        action="store_true")
    parser.add_argument("-bs", "--min-bitscore",
        type=int,
        required=False,
        help="Consider only alignments with bitscores above min-bitscore.\
            Increasing this value can be a good idea when comparing very closely related species.\
            Increasing this value will reduce the number of paralogs (and orthologs) generate.\
            WARNING: use only if you are sure of what you are doing.\n\
            INFO: higher min-bitscore values reduce the execution time for all-vs-all. \
            Default=40",
        default=40)
    parser.add_argument("-ca", "--complete-aln",
        required=False,
        help="Perform complete alignments (slower), rathen than essential ones.\n",
        default=False,
        action="store_true")

    # arch-based orthology inference
    parser.add_argument("-go", "--graph-only",
        required=False,
        help="Perform only graph-based orthology (skip architectures analysis).",
        default=False,
        action="store_true")
    parser.add_argument("--min-arch-merging-cov",
        type=float,
        required=False,
        help="When merging graph- and arch-based orhtologs consider only new-orthologs \
            with a protein coverage greater or equal than this value. Default=0.75",
        default=0.75)

    # Ortholog groups inference
    parser.add_argument("-I", "--inflation",
        type=float,
        required=False,
        help="Affects the granularity of ortholog groups. This value should be between \
            1.2 (very coarse) and 5 (fine grained clustering). Default=1.5",
        default=1.5)
    # parser.add_argument("-slc", "--single-linkage", required=False, help="Use single-linkage-clustering (MultiParanoid-like). NOTE: by default MCL clustering is used.", default=False, action="store_true")
    # parser.add_argument("-mgs", "--max-gene-per-sp", type=int, required=False, help="Limits the maximum number of genes per species in the multi-species output table. This option reduces the verbosity of the multi-species output and only affects single-linkage-clustering. Default=150", default=150)

    # Update runs
    parser.add_argument("-ot", "--overwrite-tables",
        required=False,
        help="This will force the re-computation of the ortholog tables. \
            Only missing alignment files will be re-computed.",
        default=False,
        action="store_true")
    parser.add_argument("-ow", "--overwrite",
        required=False,
        help="Overwrite previous runs and execute it again. \
            This can be useful to update a subset of the computed tables.",
        default=False,
        action="store_true")
    #parser.add_argument("-u", "--update", type=str, required=False, help="Update the ortholog tables database by adding or removing input proteomes. Performs only required alignments (if any) for new species pairs, and re-compute the ortholog groups.\nNOTE: an ID for the update must be provided.", default=None)
    parser.add_argument("-rs", "--remove-old-species",\
        required=False,
        help="(EXPERIMENTAL) Remove alignments and pairwise ortholog tables \
            related to species used in a previous run. This option should be used when \
            updating a run in which some input proteomes were modified or removed.",
        default=False,
        action="store_true")
    parser.add_argument("-un", "--update-input-names",
        required=False,
        help="(EXPERIMENTAL) Remove alignments and pairwise ortholog tables for an input \
            proteome used in a previous which file name conflicts with a newly added species. \
            This option should be used when updating a run in which some input proteomes \
            or their file names were modified.",
        default=False,
        action="store_true")
    # parse the arguments
    args = parser.parse_args()

    return (args, parser)



def check_hardware_settings(threads: int, minPerCoreMem: float, debug: bool = False) -> tuple[
int, float]:
    """Check that a given amount of memory is avaliable for each CPU."""
    if debug:
        print("\ncheck_hardware_settings::START")
        print(f"Threads:\t{threads}")
        print(f"Minimum memory per thread:\t{minPerCoreMem:.2f}")
    from psutil import virtual_memory, cpu_count
    # the hardware information
    availPhysCores: int = cpu_count(logical=False)
    availCores: int = os.cpu_count()
    threadsPerCore: int = int(availCores / availPhysCores)
    availMem: float = round(virtual_memory().total / 1073741824., 2)
    if debug:
        sys.stdout.write("\nSYSTEM INFORMATION:")
        sys.stdout.write(f"\nTotal physical cores:\t{availPhysCores:d}")
        sys.stdout.write(f"\nTotal logical CPUs:\t{availCores:d}")
        sys.stdout.write(f"\nThreads per core:\t{threadsPerCore:d}")
        sys.stdout.write(f"\nRequested threads:\t{threads:d}")
        sys.stdout.write(f"\nTotal physical memory:\t{availMem:.2f}")

    # adjust the number of threads is required
    if threads > availCores:
        sys.stderr.write(f"\nWARNING: the number of logical CPUs requested ({threads:d}) \
            is higher than the total available logical cores ({availCores:d})")
        sys.stderr.write(f"\nThe number of threads will be set (at best) to {availCores:d}\n")
        threads = availCores

    # adjust memory per cores
    memPerCore: float = round(availMem / threads, 2)

    # adjust the number of threads if required
    if memPerCore < minPerCoreMem:
        while True:
            threads -= 1
            memPerCore = round(availMem / threads, 2)
            if memPerCore >= minPerCoreMem:
                sys.stdout.write("\n\nINFO")
                sys.stdout.write(f"\nThe number of threads was set to {threads:d}")
                sys.stdout.write(f"\nThis allows {memPerCore:.2f} GBytes of memory per CPU core.")
                sys.stdout.write(f"\nThe suggested minimum memory per CPU core \
                    is {minPerCoreMem:.2f} Gigabytes.\n")
                sys.stdout.write("\nNOTE: To use the maximum number of threads \
                    regardless of the memory use the flag --force-all-threads\n")
                break
    # return tuple info
    return (threads, memPerCore)



# TODO: remove as it is redundant
'''
def check_gcc() -> tuple[
str, str, bool]:
    """Check that gcc is installed"""
    gccPath = which("gcc")
    gccMinVer: float = 5.0
    if gccPath is not None:
        rOut = subprocess.run("gcc -dumpversion", stdout=subprocess.PIPE,\
            stderr=subprocess.STDOUT, shell=True)
        dumpversion:str = rOut.stdout.decode().rstrip()
        # Make sure the version is lower than 9.3 and higher than 3
        # extract the first 2 digits
        tmpstr: list[str] = dumpversion.split(".", 2)[0:2]
        numver: float = float(".".join(tmpstr))
        if numver < 4:
            sys.stderr.write(f"\nERROR: you must install a version of GCC higher than \
                {gccMinVer} to use SonicParanoid.\n")
            sys.stderr.write(f"The version installed on your system is {dumpversion}.\n")
            sys.exit(-7)
        # now extract the complete version
        rOut = subprocess.run("gcc -dumpversion", stdout=subprocess.PIPE,\
            stderr=subprocess.STDOUT, shell=True)
        version:str = rOut.stdout.decode().rstrip()
        return (version, dumpversion, True)

    print(f"ERROR: the gcc compiler was not found on your system!\n\
        You must install GCC version {gccMinVer:.1f} or higher.")
    sys.exit(-7)
'''


def check_blast_installation(root, debug=False) -> None:
    """Check if blastp and makeblastdb were installed installed."""
    correctVer: str = "2.12.0+" # as of SonicParanoid 1.3.6
    binDir: str = os.path.join(root, "bin/")
    binPath: str = os.path.join(binDir, "blastp")
    currentVer: str = ""
    # Show info about current version
    if debug:
        print(f"\nINFO: Current required blastp version is {correctVer}")
    # copy the zip file if required
    if not os.path.isfile(binPath):
        copy_blast(root, "blastp", debug)
    else:
        # Check the version
        blastCmd = f"{binPath} -version"
        process = subprocess.Popen(blastCmd, shell=True,\
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout_val, stderr_val = process.communicate() #get stdout and stderr
        process.wait()
        del stderr_val

        # extract the version
        # The output when printing the version has the following format
        # blastp: 2.12.0+
        # Package: blast 2.12.0, build Jun  4 2021 03:22:54
        # currentVer: str = stdout_val.decode().rsplit(" ", 1)[1][:-1]
        currentVer = stdout_val.decode().split("\n", 1)[0]
        currentVer = currentVer.split(" ", 1)[1]

        if debug:
            print(f"BLASTP {currentVer} found in\n{binPath}")
        # Overwrite the file if the version does not match
        if correctVer != currentVer:
            print("\nINFO: a wrong BLASTP version is installed, \
                it will be replaced with the appropriate one.")
            # copy the correct binaries
            copy_blast(root, "blastp", debug)

    # Check makeblastdb installation
    binPath = os.path.join(binDir, "makeblastdb")
    # Show info about current version
    if debug:
        print(f"\nINFO: Current required makeblastdb version is {correctVer}")
    # copy the zip file if required
    if not os.path.isfile(binPath):
        copy_blast(root, "makeblastdb", debug)
    else:
        # Check the version
        blastCmd = f"{binPath} -version"
        process = subprocess.Popen(blastCmd, shell=True,\
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout_val, stderr_val = process.communicate() #get stdout and stderr
        process.wait()

        # extract the version
        # The output when printing the version has the following format
        # makeblastdb: 2.12.0+
        # Package: blast 2.12.0, build Jun  4 2021 03:22:54
        # currentVer: str = stdout_val.decode().rsplit(" ", 1)[1][:-1]
        currentVer = stdout_val.decode().split("\n", 1)[0]
        currentVer = currentVer.split(" ", 1)[1]

        if debug:
            print(f"makeblastdb {currentVer} found in\n{binPath}")
        # Overwrite the file if the version does not match
        if correctVer != currentVer:
            print("\nINFO: a wrong makeblastdb version is installed, \
                it will be replaced with the appropriate one.")
            # copy the correct binaries
            copy_blast(root, "makeblastdb", debug)



def check_dmnd_installation(root, debug=False) -> None:
    """Check if Diamond has been installed."""
    correctVer: str = "2.0.12" # as of SonicParanoid 1.3.6
    binDir: str = os.path.join(root, "bin/")
    dmndPath: str = os.path.join(binDir, "diamond")
    # Show info about current version
    if debug:
        print(f"\nINFO: Current required Diamond version is {correctVer}")
    # copy the zip file if required
    if not os.path.isfile(dmndPath):
        copy_dmnd(root, debug)
    else:
        # Check the version
        dmndCmd = f"{dmndPath} --version"
        process = subprocess.Popen(dmndCmd, shell=True,\
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout_val, stderr_val = process.communicate() #get stdout and stderr
        process.wait()
        del stderr_val

        # extract the version
        currentVer: str = stdout_val.decode().rsplit(" ", 1)[1][:-1]
        if debug:
            print(f"Diamond {currentVer} found in\n{dmndPath}")
        # Overwrite the file if the version does not match
        if correctVer != currentVer:
            print("\nINFO: a wrong Diamond version is installed, \
                it will be replaced with the appropriate one.")
            # copy the correct binaries
            copy_dmnd(root, debug)



def check_mmseqs_installation(root, debug=False) -> None:
    """Check if mmseqs has been installed."""
    correctVer: str = "45111b641859ed0ddd875b94d6fd1aef1a675b7e" # as of SonicParanoid 1.3.6
    binDir: str = os.path.join(root, "bin/")
    mmseqsPath: str = os.path.join(binDir, "mmseqs")
    # Show info about current version
    if debug:
        print(f"\nINFO: Current required MMseqs2 version is {correctVer}")
    # copy the zip file if required
    if not os.path.isfile(mmseqsPath):
        copy_mmseqs(root, debug)
    else:
        currentVer: str = ""
        # Check the version
        mmseqsCmd = mmseqsPath
        process = subprocess.Popen(mmseqsCmd, shell=True,\
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout_val = process.communicate()[0] #get stdout
        process.wait()

        # extract the version
        for ln in stdout_val.decode().split("\n", 7)[:7]:
            if ln[:2] == "MM":
                if ln.startswith("MMseqs2 Ver"):
                    currentVer = ln.rsplit(" ", 1)[-1]
        if debug:
            print(f"MMseqs2 {currentVer} found in\n{mmseqsPath}")
        # Overwrite the file if the version does not match
        if correctVer != currentVer:
            print("\nINFO: a wrong MMseqs2 version is installed, \
                it will be replaced with the appropriate one.")
            # copy the correct binaries
            copy_mmseqs(root, debug)



def copy_blast(root: str, program: str, debug: bool=False):
    """Install the BLAST binaries"""
    if debug:
        print("copy_blast :: START")
        print(f"Root: {root}")
        print(f"Program:\t{program}")
    binDir: str = os.path.join(root, "bin/")
    pckgsDir: str = os.path.join(root, "software_packages/")
    if not program in ["blastp", "makeblastdb"]:
        print(f"\nERROR: {program} is not a valid programs.\nValid programs: blastp | makeblastdb.")
        sys.exit(-5)
    binPath: str = os.path.join(binDir, program)
    # Remove current binaries if already exist
    if os.path.isfile(binPath):
        os.remove(binPath)
        print("Removing previous BLAST binaries...")

    ### Install BLAST ###
    # check operative system
    myOS: str = platform.system()
    isDarwin: bool = True
    if myOS == "Linux":
        isDarwin = False
    elif myOS == "Darwin":
        isDarwin = True
    sys.stdout.write("\n\n-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-")
    print(f"\nInstalling {program} binaries for {myOS} system...")
    archivePath: str = ""
    archiveName: str = ""
    if isDarwin:
        sys.exit(f"\nINFO: {program} must be installed using Bioconda")
    else:
        archiveName = f"{program}.xz"
        archivePath = os.path.join(pckgsDir, archiveName)

    # uncompress the file
    systools.unxz(path=archivePath, outDir=binDir, debug=debug)
    # change the permission
    os.chmod(binPath, 0o751)
    # Check if the binaries are supported
    testBinCmd = f"{binPath} -version"
    process = subprocess.Popen(testBinCmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout_val, stderr_val = process.communicate() #get stdout and stderr
    # del stdout_val
    process.wait()
    # check if an error happened
    if len(stderr_val.decode()) > 0:
        print(f"INFO: The {program} binaries are not working properly on the system.")
        print(f"{stderr_val.decode()}")
        sys.exit("ERROR: in copying the Diamond binaries")
    binVersion: str = stdout_val.decode().rsplit(" ", 1)[1][:-1]
    # write the final info
    print(f"The {program} ({binVersion}) binaries were installed in\n{binPath}")
    sys.stdout.write("-#-#-#-#-#-#- DONE -#-#-#-#-#-#-\n\n")



def copy_dmnd(root: str, debug: bool=False):
    """Install the Diamond binaries"""
    if debug:
        print("copy_dmnd :: START")
        print(f"Root: {root}")
    binDir: str = os.path.join(root, "bin/")
    pckgsDir: str = os.path.join(root, "software_packages/")
    dmndPath: str = os.path.join(binDir, "diamond")
    # Remove current binaries if already exist
    if os.path.isfile(dmndPath):
        os.remove(dmndPath)
        print("Removing previous Diamond binaries...")

    ### Install Diamond ###
    # check operative system
    myOS: str = platform.system()
    isDarwin: bool = True
    if myOS == "Linux":
        isDarwin = False
    elif myOS == "Darwin":
        isDarwin = True
    sys.stdout.write("\n\n-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-")
    print(f"\nInstalling Diamond binaries for {myOS} system...")
    xzPath: str = ""
    xzName: str = ""
    if isDarwin:
        sys.exit("Diamond must be installed using Bioconda")
    else:
        xzName = "diamond.xz"
        xzPath = os.path.join(pckgsDir, xzName)

    # uncompress the file
    systools.unxz(path=xzPath, outDir=binDir, debug=debug)
    # change the permission
    os.chmod(dmndPath, 0o751)
    # Check if the binaries are supported
    dmndCmd = f"{dmndPath} --version"
    process = subprocess.Popen(dmndCmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout_val, stderr_val = process.communicate() #get stdout and stderr
    # del stdout_val
    process.wait()
    # check if an error happened
    if len(stderr_val.decode()) > 0:
        print("INFO: The Diamond binaries are not working properly on the system.")
        print(f"{stderr_val.decode()}")
        sys.exit("ERROR: in copying the Diamond binaries")
    dmndVersion: str = stdout_val.decode().rsplit(" ", 1)[1][:-1]
    # write the final info
    print(f"The Diamond ({dmndVersion}) binaries were installed in\n{dmndPath}")
    sys.stdout.write("-#-#-#-#-#-#- DONE -#-#-#-#-#-#-\n\n")



def copy_mmseqs(root: str, debug: bool=False):
    """Install the proper MMseqs2 binaries"""
    if debug:
        print("copy_mmseqs :: START")
        print(f"Root: {root}")
    binDir: str = os.path.join(root, "bin/")
    pckgsDir: str = os.path.join(root, "software_packages/")
    mmseqsPath: str = os.path.join(binDir, "mmseqs")
    # Remove current binaries if already exist
    if os.path.isfile(mmseqsPath):
        os.remove(mmseqsPath)
        print("Removing previous MMseqs2 binaries...")

    ### Install MMseqs2 ###
    # check operative system
    myOS: str = platform.system()
    isDarwin: bool = True
    if myOS == "Linux":
        isDarwin = False
    elif myOS == "Darwin":
        isDarwin = True
    sys.stdout.write("\n\n-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-")
    print(f"\nInstalling MMseqs2 binaries for {myOS} system...")
    print("Try the AVX2 version...")
    xzPath: str = ""
    xzName: str = ""
    unarchivedPath: str = ""
    if isDarwin: # For MacOS a single binary works with all supported systems
        xzName = "mmseqs_macos.xz"
        xzPath = os.path.join(pckgsDir, xzName)
    else:
        xzName = "mmseqs_linux_avx2.xz"
        xzPath = os.path.join(pckgsDir, xzName)

    # uncompress the file
    unarchivedPath = systools.unxz(path=xzPath, outDir=binDir, debug=debug)
    # change the permission
    os.chmod(unarchivedPath, 0o751)
    # rename binary file to 'mmseqs'
    os.rename(unarchivedPath, mmseqsPath)
    # Check if AVX2 is supported
    mmseqsCmd = mmseqsPath
    process = subprocess.Popen(mmseqsCmd, shell=True,\
        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout_val, stderr_val = process.communicate() #get stdout and stderr
    del stdout_val
    process.wait()
    # check if an error happened
    mmseqsVersion = "AVX2"
    if len(stderr_val.decode()) > 0:
        print("INFO: Your system does not support the AVX2 instruction set, \
            the SEE4.1 version of MMseqs will be installed...")
        mmseqsVersion = "SSE4.1"
        xzPath = ""
        if not isDarwin: # We are on a Linux system
            xzName = "mmseqs_linux_sse41.xz"
            xzPath = os.path.join(pckgsDir, xzName)

        # uncompress the file
        unarchivedPath = systools.unxz(path=xzPath, outDir=binDir, debug=debug)
        # change the permission
        os.chmod(mmseqsPath, 0o751)
        # rename binary file to 'mmseqs'
        os.rename(unarchivedPath, mmseqsPath)

    # write the final info
    print(f"The MMseqs2 ({mmseqsVersion}) binaries were installed in\n{mmseqsPath}")
    sys.stdout.write("-#-#-#-#-#-#- DONE -#-#-#-#-#-#-\n\n")



def check_mcl_installation(currentDir:str, debug=False) -> bool:
    """Copy or build MCL binaries if required."""
    sonicRoot: str = os.path.dirname(os.path.abspath(__file__))
    if debug:
        print("\ncheck_mcl_installation: START")
        print(f"Running directory: {currentDir}")
        print(f"SonicParanoid root: {sonicRoot}")
    mclroot: str = os.path.join(sonicRoot, "software_packages")
    binDir: str = os.path.join(sonicRoot, "bin/")
    url: str = "https://iwasakilab.k.u-tokyo.ac.jp/sonicparanoid"
    systools.makedir(binDir)
    mclTargetPath: str = os.path.join(binDir, "mcl")
    # copy the zip file if required
    if not os.path.isfile(mclTargetPath):
        # First try copying the precompiled binaries
        precompiledOk: bool = copy_precompiled_mcl(mclroot, binDir, debug)
        if precompiledOk:
            return True
        ### Install MCL ###
        # check operative system
        myOS = platform.system()
        sys.stdout.write("\n\n-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-")
        print(f"\nBuilding MCL binaries for {myOS} system...")
        mclTargetPath = compile_mcl(sonicRoot, debug=debug)
        os.chdir(currentDir)
        if not os.path.isfile(mclTargetPath):
            sys.stderr.write("ERROR: the MCL binaries could not be build.\n")
            print(f"Please contact the developers of SonicParanoid\n{url:s}\nor \
                copy the working MCL binaries('mcl') in\n{binDir:s}")
            print("More information on MCL can be found at \nhttps://micans.org/mcl/index.html")
            sys.exit(-5)
        else:
            # Copy the compiled binaries into the bin directory
            runout = subprocess.run(f"{mclTargetPath} --version", shell=True)
            if runout.returncode == 0:
                sys.stderr.write(f"\nINFO: MCL installed in\n{mclTargetPath}")
                sys.stdout.write("\n-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-")
                return True

            print("INFO: something went wrong with the MCL installation.")
            print(f"ERROR code:\t{runout.returncode}")
            print(f"Please contact the developers of SonicParanoid\n{url:s}\nor \
                copy working MCL binaries ('mcl') in\n{binDir:s}")
            print("More information on MCL can be found at \nhttps://micans.org/mcl/index.html")
            sys.exit(-5)
    else: # check if it is working
        process = subprocess.Popen(mclTargetPath, shell=True,\
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stderr_val = process.communicate()[1] #get stdout and stderr
        process.wait()
        # check if an error happened
        stdErrOut: str = stderr_val.decode()
        if stdErrOut[:5] == "[mcl]":
            if debug:
                print(f"MCL binaries found in\n{mclTargetPath}")
            return True

        # remove the existing binaries
        if os.path.isfile(mclTargetPath):
            os.remove(mclTargetPath)
        # and call the same function to try to copy or build
        os.chdir(currentDir)
        check_mcl_installation(currentDir, debug=debug)

    # The installtion was not succefull
    return False



def copy_precompiled_mcl(mclRoot: str, targetDir: str, debug: bool=False) -> bool:
    """Copy precompiled MCL binaries to the target directory."""
    if debug:
        print("\ncopy_precompiled_mcl: START")
        print(f"Directory with MCL binaries: {mclRoot}")
        print(f"Target directory: {targetDir}")

    copyOk: bool = False
    systools.makedir(targetDir)
    # Copy the binaries based on the system
    myOS = platform.system()
    sys.stdout.write("\n-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-")
    sys.stdout.write(f"\nCopying MCL binaries for {myOS} system...")
    # Check if the precompike binaries work
    mclTargetPath: str = os.path.join(targetDir, "mcl")
    binaryNames: list[str] = ["mcl_linux"]
    mclFileName: str = ""
    if myOS == "Darwin":
        # mclFileName = "mcl_macos"
        binaryNames = ["mcl_darwin_llvm9_clang1103", "mcl_darwin_brew"]
    mclSrcPath: str = ""

    # Test each binary avaliable for the given system
    for mclFileName in binaryNames:
        mclSrcPath = os.path.join(mclRoot, mclFileName)
        # change the permission
        os.chmod(mclSrcPath, 0o751)

        runout = subprocess.run(f"{mclSrcPath} --version", shell=True)
        if runout.returncode != 0:
            sys.stderr.write(f"\nWARNING: the precompile MCL binaries\n{mclSrcPath}\ndo \
                not work on this system.")
            sys.stderr.write(f"\nExit code:\t{runout.returncode}")
            sys.stderr.write(f"\nCMD: {runout.args}\n")
            sys.stdout.write("\n-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-")
            copyOk = False
        else:
            # Remove older binaries if already exist
            if os.path.isfile(mclTargetPath):
                os.remove(mclTargetPath)
            # copy the binaries in the target directory
            copy(mclSrcPath, mclTargetPath)
            # change the permission
            os.chmod(mclTargetPath, 0o751)
            # check again that the copy was successfull
            runout = subprocess.run(f"{mclTargetPath} --version", shell=True)
            if runout.returncode == 0:
                sys.stderr.write(f"\nINFO: MCL binaries copied in\n{mclTargetPath}")
                sys.stderr.write("\n-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-\n")
                copyOk = True
            else:
                sys.stderr.write(f"\nERROR: something went wrong while copying \
                    the MCL binaries in\n{mclTargetPath}\n")
                copyOk = False
    # Return boolean flag
    return copyOk



def count_grps(ogDir:str) -> tuple[
int, int]:
    """Extract number of created groups from stats file"""
    tmpPath: str = os.path.join(ogDir, "overall.stats.tsv")
    ogCnt: int = 0
    scCnt: int = 0
    tmpStr:str = ""
    # extract count of OGs
    if not os.path.isfile(tmpPath):
        sys.stderr.write("\nWARNING: the file with the OG stats was not found!\n\
            Make sure the ortholog groups clustering was successful.")
    else:
        # extract count of OGs
        with open(tmpPath, "rt", encoding='utf-8') as ifd:
            for ln in ifd:
                if ln[:3] == "OGs":
                    tmpStr = ln.rsplit("\t", 1)[-1]
                    ogCnt = int(tmpStr.rstrip("\n"))
                    break
    # extract count of OGs
    tmpPath = os.path.join(ogDir, "single-copy_groups.tsv")
    if not os.path.isfile(tmpPath):
        sys.stderr.write("\nWARNING: the file with the single-copy OGs was not found!\n\
            Make sure the ortholog groups clustering was successful.")
    else:
        # extract count of single-copy OGs
        with open(tmpPath, "rt", encoding='utf-8') as ifd:
            for ln in ifd:
                scCnt += 1
        scCnt -= 1 # this accounts for the header
    return (ogCnt, scCnt)



def compile_mcl(sonicRoot, debug=False):
    """Build MCL binaries"""
    if debug:
        print("compile_mcl :: START")
        print(f"sonicRoot:\t{sonicRoot}")
    # clean the directory from installations
    # Now lets compile MCL
    mclRoot = os.path.join(sonicRoot, "mcl_package")
    buildDir = os.path.join(mclRoot, "mcl_build")
    print("Cleaning up build directory...")
    if os.path.isdir(buildDir):
        rmtree(buildDir)
    systools.makedir(buildDir)
    os.chdir(buildDir)

    # remove old binaries if required
    mclBinDir = os.path.join(buildDir, "bin/")
    if os.path.isdir(mclBinDir):
        print("Cleaning MCL bin directory")
        # remove all its content
        rmtree(mclBinDir)
        systools.makedir(mclBinDir)

    print('\nBuilding MCL clustering algorithm...')
    # check if the archive has been already decompressed
    confPath = os.path.join(buildDir, "configure")
    if os.path.isfile(confPath):
        print('Cleaning any previous installation...')
        # clean configuration
        cleanCmd = 'make distclean'
        process = subprocess.Popen(cleanCmd, shell=True,\
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        process.communicate() #get stdout and stderr
        process.wait()
        # remove binaries
        cleanCmd = 'make clean'
        process = subprocess.Popen(cleanCmd, shell=True,\
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        process.communicate() #get stdout and stderr
        process.wait()
    else: # extract the archive
        archPath: str = os.path.join(mclRoot, "mcl_src_slim.tar.gz")
        if not os.path.isfile(archPath):
            sys.stderr.write(f"ERROR: the archive with the MCL source code is missing\n{archPath}\n\
                Please try to download SonicParanoid again.")
            sys.exit(-2)
        else:
            systools.untar(archPath, buildDir)
    # configure MCL
    print("\nConfiguring the MCL installation...")
    compileCmd = f"./configure --prefix={buildDir}"
    print(compileCmd)
    process = subprocess.Popen(compileCmd, shell=True,\
        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    process.communicate() #get stdout and stderr
    process.wait()

    # binary paths
    mclBin = os.path.join(buildDir, "bin/mcl")
    if os.path.isfile(mclBin):
        print("Removing old MCL binaries...")
        os.remove(mclBin)

    # compile MCL
    compileCmd = 'make install'
    print("Building MCL...")
    print(compileCmd)
    process = subprocess.Popen(compileCmd, shell=True,\
        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    process.communicate() #get stdout and stderr
    process.wait()

    print("\nOutput directories info:")
    print("buildDir", buildDir)
    print("mclBinDir", mclBinDir)
    print("mclBin", mclBin)

    if not os.path.isfile(mclBin):
        sys.stderr.write("ERROR: the MCL binaries could not be build.\n")
        sys.exit(-2)

    # reset the current directory
    os.chdir(sonicRoot)
    # Move the binaries to the final target directory
    # Remove older binaries if already exist
    mclTargetPath: str = os.path.join(sonicRoot, "bin/mcl")
    if os.path.isfile(mclTargetPath):
        os.remove(mclTargetPath)
    # copy the binaries in the target directory
    copy(mclBin, mclTargetPath)
    # change the permission
    os.chmod(mclTargetPath, 0o751)
    # remove the build directory
    print("Cleaning up build directory...")
    if os.path.isdir(buildDir):
        rmtree(buildDir)
    sys.stdout.write('-#-#-#-#-#-#- MCL compilation done -#-#-#-#-#-#-\n')
    # reset the current directory
    return mclTargetPath



def extract_single_copy_groups(grpTbl: str, grpFlatTbl: str, debug: bool = False) -> str:
    """Write a list with single copy ortholog groups."""
    if debug:
        print("extract_single_copy_groups :: START")
        print(f"Input groups table: {grpTbl:s}")
        print(f"Input \"flast\" groups table: {grpFlatTbl:s}")

    if not os.path.isfile(grpTbl):
        sys.stderr.write(f"\nERROR: the table with ortholog groups\n{grpTbl:s}\nwas not found.\n")
        sys.exit(-2)
    if not os.path.isfile(grpFlatTbl):
        sys.stderr.write(f"\nERROR: the table with \"flat\" \
            ortholog groups\n{grpFlatTbl:s}\nwas not found.\n")
        sys.exit(-2)

    # counter for single-copy groups
    scogCnt: int = 0
    rdCnt: int = 0
    # load the first 3 columns only
    ifdFlat = open(grpFlatTbl, "rt", encoding='utf-8')
    ifdGrps = open(grpTbl, "rt", encoding='utf-8')
    # skip the headers
    ifdGrps.readline()
    flatHdr: str = ifdFlat.readline()

    # output paths
    outPath: str = os.path.join(os.path.join(os.path.dirname(grpTbl), "single-copy_groups.tsv"))
    # open output file and write the header
    ofd = open(outPath, "wt", encoding='utf-8')
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
        print(f"Single-copy ortholog groups:\t{scogCnt:d}")
        print(f"Percentage of single-copy ortholog groups:\t{scogPct:.2f}")

    # return the output file
    return outPath



def filter_warnings(debug:bool=False):
    """Show warnings only in debug mode"""
    if not debug:
        import warnings
        warnings.filterwarnings("ignore")



def get_input_paths(inDir, debug=False):
    """Check that at least 2 files are provided."""
    if debug:
        print("get_input_paths :: START")
    # associate a path to each file name
    fname2path = {}
    for f in os.listdir(inDir):
        if f == '.DS_Store':
            continue

        tmpPath = os.path.join(inDir, f)
        if os.path.isfile(tmpPath):
            fname2path[f] = tmpPath
    # check that at least two input files were provided
    if len(fname2path) < 2:
        sys.stderr.write('ERROR: the directory with the input files \
            only contains {:d} ({:s}) files\nPlease provide at \
                least 2 proteomes.\n'.format(len(fname2path), '\n'.join(list(fname2path.keys()))))
        sys.exit(-5)
    # sort the dictionary by key to avoid different sorting
    # on different systems due to os.listdir()
    sortedDict = dict(sorted(fname2path.items()))
    del fname2path
    return list(sortedDict.values())



def infer_orthogroups_2_proteomes(orthoDbDir: str, outDir: str, sharedDir: str, outName: str, pairsDict: dict[
str, float], mergedTables: bool=False, debug: bool=False):
    """Create ortholog groups for only 2 proteomes"""
    import pickle
    if debug:
        print("\ninfer_orthogroups_2_proteomes :: START")

    # sys.exit("DEBUG@sonicparanoid -> infer_orthogroups_2_proteomes")
    # reference species file
    sys.stdout.write('\nCreating ortholog groups for the 2 proteomes...\n')
    timer_start = time.perf_counter()
    # Aux dir
    auxDir: str = os.path.join(sharedDir, "aux")
    # set the output name
    outSonicGroups: str = os.path.join(outDir, outName)
    # extract the only pair
    sp1, sp2 = list(pairsDict.keys())[0].split("-", 1)
    tblType: str = ""
    # Set a different name depending if the table is merged with arch-based predictions
    # or only contains graph-based ones
    if mergedTables:
        tblType = "mtable"
    else:
        tblType = "table"
    tablePath: str = os.path.join(orthoDbDir, f"{sp1}/{tblType}.{sp1}-{sp2}")
    flatGrps, notGroupedPath = orthogroups.create_2_proteomes_groups(rawTable=tablePath, outPath=outSonicGroups, debug=debug)
    # load dictionary with protein counts
    seqCntsDict = pickle.load(open(os.path.join(auxDir, 'protein_counts.pckl'), 'rb'))
    # Remap the groups
    sys.stdout.write("\nGenerating final output files...")
    # load dictionary with proteome sizes
    genomeSizesDict = pickle.load(open(os.path.join(auxDir, 'proteome_sizes.pckl'), 'rb'))
    # compute stats
    grpsStatPaths = orthogroups.compute_groups_stats_no_conflict(inTbl=outSonicGroups,\
        outDir=outDir, outNameSuffix="stats", seqCnts=seqCntsDict, proteomeSizes=genomeSizesDict,\
            debug=False)
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
    sys.stdout.write(f"\nOrtholog groups creation elapsed time (seconds):\
        \t{(time.perf_counter() - timer_start):.3f}\n")
    ogCnt, scOgCnt = count_grps(os.path.dirname(flatGrps))
    sys.stdout.write(f"\nOrtholog groups:\t{ogCnt}\n")
    sys.stdout.write(f"Single-copy ortholog groups:\t{scOgCnt}\n")
    print(f"\nThe ortholog groups and related statistics are stored \
        in the directory:\n{os.path.dirname(flatGrps)}")



''' TODO: remove in future releases
def infer_orthogroups_qp(orthoDbDir: str, outDir: str, sharedDir: str, sqlTblDir: str, outName: str, pairsList: list[str], maxGenePerSp: int, threads: int=4, debug: bool=False):
    """Perform orthology inference using QuickParanoid."""
    if debug:
        print("\ninfer_orthogroups_qp :: START")
    # reference species file
    sys.stdout.write("\nCreating ortholog groups using single-linkage clustering...")
    multisp_start = time.perf_counter()
    auxDir: str = os.path.join(sharedDir, "aux")
    # seqInfoFilesDir: str = os.path.join(auxDir, "input_seq_info")
    multiParaRunDir: str = os.path.join(outDir, "multiparanoid_run")
    systools.makedir(multiParaRunDir)
    # sys.exit("DEBUG@sonicparanoid -> infer_orthogroups_qp (sql tables creation)")
    # Create SQL tables
    sqlCnt: int = orthogroups.create_sql_tables(orthoDbDir=orthoDbDir, outSqlDir=multiParaRunDir, pairsList=pairsList, threads=threads,  debug=False)
    print(f"{sqlCnt} SQL tables created.")
    quickparaRoot = orthogroups.get_quick_multiparanoid_src_dir()
    #create the multi-species clusters
    orthoGrps, grpsStatPaths = orthogroups.run_quickparanoid(tblList=pairsList, sqlTblDir=multiParaRunDir, outDir=multiParaRunDir, sharedDir=auxDir, srcDir=quickparaRoot, outName=outName, maxGenePerSp=40, debug=False)
    # Move files to the main output directory
    for k, fpath in grpsStatPaths.items():
        move(fpath, outDir)
        grpsStatPaths[k] = os.path.join(outDir, os.path.basename(fpath))
    move(orthoGrps, outDir)
    ogsFileName = os.path.basename(orthoGrps)
    move(os.path.join(os.path.dirname(orthoGrps), f"flat.{ogsFileName}"), outDir)
    move(os.path.join(os.path.dirname(orthoGrps), f"not_assigned_genes.{ogsFileName}"), outDir)
    orthoGrps = os.path.join(outDir, ogsFileName)
    rmtree(multiParaRunDir, ignore_errors=True)
    # load the mapping information
    id2SpDict, new2oldHdrDict = idmapper.load_mapping_dictionaries(runDir=auxDir, debug=debug)
    # remap the genes in orthogroups
    idmapper.remap_orthogroups(inTbl=orthoGrps, id2SpDict=id2SpDict, new2oldHdrDict=new2oldHdrDict, removeOld=True, hasConflict=True, debug=debug)
    # remap the flat multi-species table
    flatGrps = os.path.join(outDir, f"flat.{ogsFileName}")
    idmapper.remap_flat_orthogroups(inTbl=flatGrps, id2SpDict=id2SpDict, new2oldHdrDict=new2oldHdrDict, removeOld=True, debug=debug)
    # remap file with not grouped genes
    notGroupedPath = os.path.join(outDir, f"not_assigned_genes.{ogsFileName}")
    idmapper.remap_not_grouped_orthologs(inPath=notGroupedPath, id2SpDict=id2SpDict, new2oldHdrDict=new2oldHdrDict, removeOld=True, debug=debug)
    # remap stats
    idmapper.remap_group_stats(statPaths=grpsStatPaths, id2SpDict=id2SpDict, removeOld=True, debug=debug)
    # extract single-copy ortholog groups
    extract_single_copy_groups(grpTbl=orthoGrps, grpFlatTbl=flatGrps, debug=debug)
    sys.stdout.write(f"Ortholog groups creation elapsed time (seconds):\t{round(time.perf_counter() - multisp_start, 3)}\n")
    ogCnt, scOgCnt = count_grps(os.path.dirname(outDir))
    sys.stdout.write(f"\nOrtholog groups:\t{ogCnt}\n")
    sys.stdout.write(f"Single-copy ortholog groups:\t{scOgCnt}\n")
    print(f"\nThe ortholog groups and related statistics are stored in the directory:\n{outDir}")
'''



def infer_orthogroups_mcl(orthoDbDir: str, sharedDir: str, outName: str, pairsList: list[str], inflation: float = 1.5, threads: int=4, condaRun: bool=False, mergedTables: bool=False, debug: bool=False):
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
            sys.stderr.write("\nERROR: MCL could not be found, please install it using CONDA/Mamba.")
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
        sys.stderr.write("\nERROR: the MCL program was not found.\nPlease try to re-install \
            SonicParanoid, or contact the developers.\n")
        sys.exit(-5)

    # sys.exit("DEBUG@sonicparanoid -> infer_orthogroups_mcl")
    auxDir: str = os.path.join(sharedDir, "aux")
    sys.stdout.write("\nCreating ortholog groups using MCL clustering...")
    timer_start = time.perf_counter()
    # compute ortholog matrixes
    mtxDir = os.path.join(os.path.dirname(orthoDbDir), "ortholog_matrixes")
    systools.makedir(mtxDir)
    # create matrixes
    graph.create_matrix_from_orthotbl_parallel(pairsList=pairsList, runDir=auxDir, orthoDbDir=orthoDbDir, outDir=mtxDir, threads=threads, mergedTables=mergedTables, debug=False)
    # sys.exit("DEBUG :: infer_orthogroups_mcl")
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
    sys.stdout.write(f"\nInparalogs merging elapsed time (seconds):\t\
{(time.perf_counter() - tmp_timer_start):.3f}\n")
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
    sys.stdout.write(f"\nMCL graph creation elapsed time (seconds):\t\
{(time.perf_counter() - tmp_timer_start):.3f}\n")
    # output paths
    rawMclGroupsPath = os.path.join(mclDir, f"raw_mcl_{outName}")
    # Run MCL
    sys.stdout.write("\nRunning MCL...")
    sys.stdout.flush()
    tmp_timer_start = time.perf_counter()
    mcl.run_mcl(mclGraph=mclMatrix, outPath=rawMclGroupsPath, mclBinPath=mclBinPath, inflation=inflation, threads=threads, removeInput=delMclInputMtx, debug=debug)
    sys.stdout.write(f"\nMCL execution elapsed time (seconds):\t\
{(time.perf_counter() - tmp_timer_start):.3f}\n")
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
    sys.stdout.write(f"\nElapsed time for the creation of final output (seconds):\t\
{(time.perf_counter() - tmp_timer_start):.3f}\n")
    del tmp_timer_start
    sys.stdout.write(f"Ortholog groups creation elapsed time (seconds):\t\
{(time.perf_counter() - timer_start):.3f}\n")
    ogCnt, scOgCnt = count_grps(mclDir)
    sys.stdout.write(f"\nOrtholog groups:\t{ogCnt}\n")
    sys.stdout.write(f"Single-copy ortholog groups:\t{scOgCnt}\n")
    print(f"\nThe ortholog groups and related statistics are stored in the directory:\n{mclDir}")



def map_mode2sensitivity(args: argparse.Namespace, debug: bool = False) -> tuple[
str, str, str, float]:
    """Map selected mode and sensitivity value for both MMseqs and Diamond"""

    # Legacy setting mapping, until SonicParanoid 1.3.8
    # MMseqs #
    # Fast -> 2.5
    # Default -> 4.0
    # Sensitive -> 6.0
    # Most-Sensitive -> 7.5
    # Diamond #
    # Fast -> mid-sensitive
    # Default -> sensitive
    # Sensitive -> very-sensitive
    # Most-Sensitive -> ultra-sensitive

    # Set the alignment tool if needed
    runMode: str = args.mode
    customDmndSens: str = args.diamond
    customMMseqsSens: float = args.mmseqs
    useBlastp: bool = args.blast

    if debug:
        print("\nmap_mode2sensitivity :: START")
        print(f"Mode:\t{runMode}")
        print(f"Custom MMseqs sensitivity (-s):\t{customMMseqsSens}")
        print(f"Custom Diamond sensitivity:\t{customDmndSens}")
        print(f"Use Blastp:\t{useBlastp}")

    # set the sensitivity value for MMseqs2
    mmseqsSens: float = 0.
    dmndSens: str = ""
    blastpSens: str = "blastp_default"
    alnTool: str = ""
    customMMseqs: bool = False
    customDmnd: bool = False
    customAligner: bool = False
    # make sure both custom modes are not set at the same time
    if customMMseqsSens > 0.:
        customMMseqs = True
    if len(customDmndSens) > 0:
        customDmnd = True
    # Prevent setting multiple alignment tools
    if (customDmnd + customMMseqs + useBlastp) > 1:
        sys.stderr.write(f"\nERROR: you are trying to use multiple \
alignment tools, and this is not possible.\
please only set one: --mmseqs-sens or --diamond-sens or --blast\n")
        if debug:
            print(f"--mmseqs-sens:\t{customMMseqs}")
            print(f"--dmnd-sens:\t{customDmnd}")
            print(f"--blast:\t{useBlastp}")
        sys.exit(-5)

    ''' These were used up to MMseqs 1.3.8
    # Set the sentivity value and run modes
    mmseqsSens = 0.
    if runMode == "fast":
        mmseqsSens = 2.5
        dmndSens = "mid-sensitive"
    elif runMode == "default":
        mmseqsSens = 4.0
        dmndSens = "sensitive" # NOTE: Maybe too similar to 'mid-sensitive'
    elif runMode == "sensitive":
        mmseqsSens = 6.0
        dmndSens = "very-sensitive"
    else: # runMode == "most-sensitive"
        mmseqsSens = 7.5
        dmndSens = "ultra-sensitive"
    '''

    # Set the sentivity value and run modes
    # based on the SonicPAranoid2 presets
    if runMode == "fast":
        dmndSens = "mid-sensitive"
        alnTool = "diamond"
    elif runMode == "default":
        dmndSens = "very-sensitive" # NOTE: Maybe too similar to 'mid-sensitive'
        alnTool = "diamond"
    elif runMode == "sensitive":
        mmseqsSens = 7.5
        alnTool = "mmseqs"

    # Return the tuple earlier if no custom settings were used
    if (customDmnd or customMMseqs or useBlastp) == False:
        return (runMode, alnTool, dmndSens, mmseqsSens)

    # Ignore the custom mode if same as preset
    if customDmnd:
        alnTool = "diamond"
        mmseqsSens = 0.
        if customDmndSens == "mid-sensitive":
            dmndSens = customDmndSens
            runMode = "fast"
            print(f"INFO: run mode forcely set to {runMode}")
        elif customDmndSens == "very-sensitive":
            dmndSens = customDmndSens
            runMode = "default"
            print(f"INFO: run mode forcely set to {runMode}")
        if customDmndSens == dmndSens:
            print(f"INFO: the custom setting for Diamond \
will be ignored as it corresponds to the {runMode} preset.")
            customDmnd = False
    if customMMseqs:
        alnTool = "mmseqs"
        dmndSens = ""
        if customMMseqsSens == 7.5:
            mmseqsSens = customMMseqsSens
            runMode = "sensitive"
            print(f"INFO: run mode forcely set to {runMode}")
            print(f"INFO: the custom setting for MMseqs \
will be ignored as it corresponds to the {runMode} preset.")
            customMMseqs = False

    formattedSens: str = ""
    # set sensitivity for MMseqs using a user spcified value
    if customMMseqs:
        if 1. <= customMMseqsSens <= 7.5:
            mmseqsSens = round(customMMseqsSens, 1)
            print(f"WARNING: the run mode \'{runMode}\' will be overwritten \
with the custom MMseqs sensitivity value of {mmseqsSens}.")
            # update the run mode accordingly
            formattedSens = "".join(str(mmseqsSens).split(".", 1))
            runMode = f"custom_mmseqs_s{formattedSens}"
            print(f"Run mode set to \'{runMode}\' (MMseqs2 sensitivity={customMMseqsSens:.2f})\n")
            alnTool = "mmseqs"
            dmndSens = ""
        else:
            sys.stderr.write('\nERROR: the sensitivity parameter for MMseqs\
                must have a value between 1.0 and 7.5\n')
            sys.exit(-6)
    # set sensitivity for Diamond using a user spcified value
    elif customDmnd:
        dmndSens = customDmndSens
        print(f"WARNING: the run mode \'{runMode}\' will be overwritten \
with the custom Diamond sensitivity value of {dmndSens}.")
        # update the run mode accordingly
        formattedSens = dmndSens.replace("-", "_")
        runMode = f"custom_dmnd_{formattedSens}"
        print(f"Run mode set to \'{runMode}\' (Diamond sensitivity = --{dmndSens:s})\n")
        alnTool = "diamond"
        mmseqsSens = 0.
    # set the required parameters for the use of Blastp
    elif useBlastp:
        print(f"WARNING: the run mode \'{runMode}\' will be overwritten \
with the custom mode using blastp with default settings.")
        # update the run mode accordingly
        runMode = f"custom_{blastpSens}"
        print(f"Run mode set to \'{runMode}\'\n")
        alnTool = "blast"
        mmseqsSens = 0.
        dmndSens = ""

    # Add the 'g' suffix if only graph-based ortohlogs will be inferred
    if args.graph_only:
        runMode = f"{runMode}_g"

    if debug:
        print("\nSensitivity settings:")
        print(f"RunMode:\t{runMode}")
        print(f"mmseqsSens:\t{mmseqsSens}")
        print(f"customMMseqs:\t{customMMseqs}")
        print(f"customMMseqsSens:\t{customMMseqsSens:.2f}")
        print(f"dmndSens:\t{dmndSens}")
        print(f"customDmnd:\t{customDmnd}")
        print(f"customDmndSens:\t{customDmndSens:s}")
        print(f"useBlastp:\t{useBlastp}")
        print(f"alnTool:\t{alnTool}")

    # Output the mapped variables
    return (runMode, alnTool, dmndSens, mmseqsSens)



def validate_species_file(spFilePath: str) -> None:
    """Make sure that there is not file with 0 proteins or proteome size 0"""
    spId: str = ""
    spName: str = ""
    strCnt: str = ""
    strSize: str = ""
    tmpCnt: int = 0
    tmpSize: int = 0
    # Example line in sp file
    # 1 chlamydia_trachomatis aefdc6e98c92e4c6181720c5576f034a14ebf056bbdb073b319b394d91 917 315378
    with open(spFilePath, "r", encoding='utf-8') as ifd:
        for ln in ifd:
            spId, spName, d1, strCnt, strSize = ln.rstrip("\n").split("\t", 4)
            del d1
            tmpCnt = int(strCnt)
            tmpSize = int(strSize)
            # Check that none of the values is 0
            if tmpSize == 0:
                print(f"ERROR: The file {spName} (ID:{spId}) contains no aminoacids \
                    or it is not a valid FASTA file!\nPlease remove it.\n")
                sys.exit(-5)
            elif tmpCnt == 0:
                print(f"ERROR: The file {spName} (ID:{spId}) contains not FASTA sequences!\n\
                    Please remove it.\n")
                sys.exit(-5)



def write_run_info_file(infoDir, infoDict, debug=False) -> str:
    """Write a file summarizing the run settings."""
    if debug:
        print("\nwrite_run_info_file :: START")
        print(f"Directory with run info: {infoDir}")
    infoFile: str = os.path.join(infoDir, "run_info.txt")
    ofd = open(infoFile, "w", encoding='utf-8')
    for info, val in infoDict.items():
        if info == "Version":
            ofd.write(f"SonicParanoid {val}\n")
        else:
            ofd.write(f"{info}\t{val}\n")
    ofd.close()
    return infoFile



def citation_and_help():
    """Print citation info"""
    print("\nCITATION INFO:")
    print("Cosentino Salvatore & Wataru Iwasaki. (2023),\n\
bioRxiv. 2023.05.14.540736.\n\
DOI: https://doi.org/10.1101/2023.05.14.540736\n")

    print("Cosentino Salvatore & Wataru Iwasaki. (2019),\n\
Bioinformatics. Volume 35, Issue 1, 01 January 2019, Pages 149–151.\n\
DOI: https://doi.org/10.1093/bioinformatics/bty631\n")
    emailSC1: str = "salvo981@gmail.com"
    emailSC2: str = "salvocos@k.u-tokyo.ac.jp"
    emailWI1: str = "iwasaki@k.u-tokyo.ac.jp"
    webpage: str = "http://iwasakilab.k.u-tokyo.ac.jp/sonicparanoid/"
    print("\nINSTRUCTIONS:")
    print(f"Find the user manual for SonicParanoid at\n{webpage}\n")

    print("\nCONTACT:")
    print(f"Salvatore Cosentino:\t{emailSC1}  or  {emailSC2}")
    print(f"Wataru Iwasaki:\t{emailWI1}")



def sanity_check(infoDict: dict[
str, str], alnTool: str = "mmseqs", debug: bool = False) -> bool:
    """
    Make sure there are no uncompleted alignments from previous runs.
    Avoid runs using different sensitivity settings.
    Compress/extract alignment files before starting the run.
    """
    updateRun: str = infoDict["Update run:"]
    completeOw: str = infoDict["Complete overwrite:"]
    if debug:
        print("\nsanity_check :: START")
        print(f"Alignment tool:\t{alnTool}")
        print(f"Update run:\t{updateRun}")
        print(f"Complete overwrite:\t{completeOw}")

    if updateRun == "False":
        return True
    # Just return True as no everything will be overwritten anyway
    if completeOw == "True":
        return True

    # Extract information from previous run
    # and check for inconstencies in parameters
    outRoot: str = infoDict["Main output directory:"]
    prevRunFile:str = os.path.join(outRoot, "last_run_info.txt")
    threads: int = int(infoDict["Threads:"])
    compress: bool = False if (infoDict["Compress alignments:"] == "False") else True
    complev:int = 5 if (not compress) else int(infoDict["Compression level:"])

    if not os.path.isfile(prevRunFile):
        sys.stderr.write(f"\nERROR: the file with info on previous run\n{prevRunFile}\nwas \
            not found.\nThe run cannot be updated, as it would generate uncosistent results!.\n")
        sys.stderr.write("Use the '-ow' parameter to start \
            a new run with the desired tool and sensitivity.\n")
        sys.stderr.write("Be aware that this would overwrite \
            the previously generated all-vs-alignments.\n")
        sys.stderr.flush()
        sys.exit(-4)
    else:
        # Extract the name of the tool used in previous Run
        prevTool: str = ""
        with open(prevRunFile, "rt", encoding="utf-8") as ifd:
            for ln in ifd:
                # extract from 'Diamond sensitivity'
                if ln[0:4] == "Alig":
                    # Example of line with alignment tool info
                    # Alignment tool: blast
                    prevTool = ln[:-1].rsplit("\t", 1)[1]
                    if prevTool == "blast":
                        prevTool = "BLAST"
                    elif prevTool == "mmseqs":
                        prevTool = "MMSeqs2"
                    elif prevTool == "diamond":
                        prevTool = "Diamond"
                    else:
                        print(f"The tool {prevTool} is not valid!")
                        sys.exit(-7)
                    break

        currentTool: str = "MMSeqs2"
        if alnTool == "diamond":
            currentTool = "Diamond"
        elif alnTool == "blast":
            currentTool = "BLAST"
        # Diamond selected but previous run done with MMSeqs2
        if currentTool != prevTool:
        # if dmndMode and (prevTool == "MMSeqs2"):
            sys.stderr.write(f"\nERROR: {currentTool} was selected for the current run, \
                while the previous run was perfomed using {prevTool}.\n")
            sys.stderr.write(f"This is not allowed as it would generate unconsistent results.\n\
                Set the same alignment tool used in the previous run ({prevTool}) or use the '-ow' \
                    parameter to start a new run with the desired tool and sensitivity.\n")
            sys.stderr.write("Be aware that this will overwrite \
                the previously generated all-vs-alignments.\n")
            sys.stderr.flush()
            sys.exit(-4)

        # Extract current selected sensitivity
        currentSens: str = ""
        if currentTool == "Diamond":
            currentSens = infoDict["Diamond sensitivity:"]
        elif currentTool == "MMSeqs2":
            currentSens = infoDict["MMseqs sensitivity:"]
        elif currentTool == "BLAST":
            currentSens = "default"
        currentMl: str = infoDict["Max length difference for in-paralogs:"]
        currentInfl: str = infoDict["MCL inflation:"]
        currentBscore: str = infoDict["Minimum bitscore:"]
        prevVal: str = ""

        if debug:
            print(f"prevTool:\t{prevTool}")
            print(f"currentTool:\t{currentTool}")
            print(f"currentSens:\t{currentSens}")
            print(f"currentBitscore:\t{currentBscore}")

        # Check that the bitscore is the same as previous run
        with open(prevRunFile, "rt", encoding="utf-8") as ifd:
            for ln in ifd:
                # Extract previous minimum bitscore
                if ln[0:10] == "Minimum bi":
                    prevVal = ln.rsplit("\t", 1)[-1].rstrip("\n")
                    if prevVal != currentBscore:
                        sys.stderr.write(f"\nERROR: the current value for the \
                            '--min-bitscore' parameter ({currentBscore}) is different from \
                                the one used in the previous run ({prevVal}).\n")
                        sys.stderr.write(f"This is not allowed \
                            as it would generate unconsistent results.\n\
                                Set the same --min-bitscore ({prevVal}) or use the '-ow' parameter to start a new run \
                                    with the desired minimum bitscore ({currentBscore}).\n")
                        sys.stderr.write("Be aware that this will overwrite \
                            the previously generated all-vs-all alignments \
                                (but not the orthologs groups).\n")
                        sys.stderr.flush()
                        sys.exit(-4)
                # extract from 'Max length difference for in-paralogs'
                elif ln[0:5] == "Max l":
                    prevVal = ln.rsplit("\t", 1)[-1].rstrip("\n")
                    if prevVal != currentMl:
                        sys.stdout.write(f"\nWARNING: the current '-ml' parameter ({currentMl}) \
is different from the one used in the previous run ({prevVal}).\n\
This might generate slighty different results.\n")
                # extract from 'MCL inflation'
                elif ln[0:5] == "MCL in":
                    prevVal = ln.rsplit("\t", 1)[-1].rstrip("\n")
                    if prevVal != currentInfl:
                        sys.stdout.write(f"\nINFO: the current MCL inflation parameter \
'-I' ({currentInfl}) is different from the one used in the previous run ({prevVal}).\n\
This might generate slighty different orthologgroups.\n")

        # parse and extract info from the run info file
        if prevTool == "Diamond":
            with open(prevRunFile, "rt", encoding="utf-8") as ifd:
                for ln in ifd:
                    # extract from 'Diamond sensitivity'
                    if ln[0:4] == "Diam":
                        prevVal = ln.rsplit("\t", 1)[-1].rstrip("\n")
                        if prevVal != currentSens:
                            sys.stderr.write(f"\nERROR: the Diamond sensitivity ({currentSens}) \
is different from the one used in the previous run ({prevVal}).\n")
                            sys.stderr.write(f"This is not allowed as it would generate \
unconsistent results.\nSet the same Diamond sensitivity ({prevVal}) \
or use the '-ow' parameter to start a new run \
with the desired sensitivity ({currentSens}).\n")
                            sys.stderr.write("Be aware that this would overwrite the previously \
generated all-vs-all alignments (but not the orthologs groups).\n")
                            sys.stderr.flush()
                            sys.exit(-4)
                # sys.exit("DEBUG: sanity_check :: Diamond mode")
        elif prevTool == "MMSeqs2": # MMSeqs2 was used
            with open(prevRunFile, "rt", encoding="utf-8") as ifd:
                for ln in ifd:
                    # extract from 'MMseqs sensitivity'
                    if ln[0:8] == "MMseqs s":
                        prevVal = ln.rsplit("\t", 1)[-1].rstrip("\n")
                        if prevVal != currentSens:
                            sys.stderr.write(f"\nERROR: the MMseqs sensitivity ({currentSens}) is \
                                different from the one used in the previous run ({prevVal}).\n")
                            sys.stderr.write(f"This is not allowed as it would generate unconsistent results.\n\
Set the same MMseqs sensitivity ({prevVal}) or use the '-ow' parameter \
to start a new run with the desired sensitivity ({currentSens}).\n")
                            sys.stderr.write("Be aware that this would overwrite \
the previously generated all-vs-all alignments (but not the orthologs groups).\n")
                            sys.stderr.flush()
                            sys.exit(-4)
                # sys.exit("DEBUG: sanity_check :: MMseqs2 mode")

    # Obtain some required information
    ortoDbDir: str = infoDict["Pairwise tables DB directory:"]
    alnDir: str = infoDict["Alignment directory:"]
    tmpAlnSpDir: str = ""
    # Paths used for compression/extraction
    tmpAlnPath: str = ""
    tmpSanityPath: str = ""
    sanityDir: str = os.path.join(alnDir, "tmp_sanity_check")
    tmpSanityDir: str = ""
    # remove the directory if already exists, and create it again
    if os.path.isdir(sanityDir):
        rmtree(sanityDir)
    systools.makedir(sanityDir)
    # will contains the path for which compression or decompression is required
    archivingJobs: list[tuple[
str, str]] = []
    spFile: str = os.path.join(infoDict["Run directory:"], "aux/species.tsv")
    spList: list[str] = []
    rmPairSet: set[str] = set()
    # counter for removed alignments
    rmDirCnt = rmFileCnt = 0
    # itertools.combinations(spList, r=2)
    # read the species IDs and generate the cobinations
    with open(spFile, "rt", encoding="utf-8") as ifd:
        spList = [ln.split("\t", 1)[0] for ln in ifd]

    # Simplified version using os.walk()
    for sp in spList:
        tmpAlnSpDir = os.path.join(alnDir, str(sp))
        for r, dirs, files in os.walk(tmpAlnSpDir, topdown=True):
            # remove directories
            for tmpDir in dirs:
                rmtree(os.path.join(r, tmpDir))
                rmPairSet.add(tmpDir)
                rmDirCnt += 1
            # remove alignments files or compress decompress alignment files
            for tmpName in files:
                tmpAlnPath = os.path.join(r, tmpName)
                # remove alignments files before the renaiming e.g., '_1-2'
                if tmpName[0] == "_":
                    os.remove(tmpAlnPath)
                    rmPairSet.add(tmpName[1:])
                    rmFileCnt += 1
                # add compress/extract jobs depending on the matched condition
                elif (compress and (not filetype.is_archive(tmpAlnPath))) or ((not compress) and filetype.is_archive(tmpAlnPath)):
                    # print(tmpAlnPath)
                    tmpSanityDir = os.path.join(sanityDir, sp)
                    systools.makedir(tmpSanityDir)
                    tmpSanityPath = os.path.join(tmpSanityDir, tmpName)
                    # move the file, and add the compress job
                    move(tmpAlnPath, tmpSanityDir)
                    archivingJobs.append((tmpSanityPath, tmpAlnPath))
            break

    # perform the compression\extraction jobs
    if len(archivingJobs) > 0:
        # [print(el) for el in archivingJobs]
        workers.parallel_archive_processing(archivingJobs, complev=complev, removeSrc=True, threads=threads, compress=compress, debug=debug)

    # Remove directory with tmp sanity check files
    if os.path.isdir(os.path.join(ortoDbDir, "matrixes")):
        rmtree(os.path.join(ortoDbDir, "matrixes"))

    # Remove directory with ortholog matrixes
    if os.path.isdir(sanityDir):
        rmtree(sanityDir)

    # show some debug
    if debug:
        print(f"\nChecked alignments for {len(spList)} species")
        print(f"Removed alignment directories:\t{rmDirCnt}")
        print(f"Removed alignment files before renaming:\t{rmFileCnt}")
        print(f"Pairs with imcomplete alignment runs:\t{len(rmPairSet)}")
        print(f"Compressed/extracted files:\t{len(archivingJobs)}")
    # sys.exit("DEBUG: sanity_check :: After Alignment tool check")
    return True



def set_project_id(rId: str, runsDir: str, runMode: str, alnTool: str, args: argparse.Namespace, debug: bool = False):
    """Generates a run ID if required."""
    if debug:
        print("\nset_project_id :: START")
        print(f"Run name:\t{rId}")
        print(f"Runs directory: {runsDir}")
        print(f"Runs mode: {runMode}")
        print(f"Alignment tool: {alnTool}")
    if not os.path.isdir(runsDir):
        sys.stderr.write('\nERROR: the directory with the runs does not exist.\n')
        sys.exit(-2)
    # create the runid if required
    if len(rId) == 0:
        ltime = time.localtime(time.time())
        # the id should include:
        # day of the month: tm_mday
        # month of the year: tm_mon
        # 2-digits year: tm_year
        # hours: tm_hour
        # minutes: tm_min
        # seconds: tm_sec
        startTime = f"{ltime.tm_mday}{ltime.tm_mon}{str(ltime.tm_year)[2:]}\
{ltime.tm_hour}{ltime.tm_min}{ltime.tm_sec}"
        rId = f"sp2_{startTime}"
        # Add other info the run name
        rId = f"{rId}_{runMode}_{args.threads}\
cpus_ml{''.join(str(args.max_len_diff).split('.', 1))}"
        # add other extra info in the naming
        if args.index_db:
            rId = f"{rId}_idxdb"
        if args.overwrite:
            rId = f"{rId}_ow"
        if args.overwrite_tables:
            if not args.overwrite:
                rId = f"{rId}_ot"
        if args.output_pairs:
            rId = f"{rId}_op"
        if args.skip_multi_species:
            rId = f"{rId}_sm"
        if args.debug:
            rId = f"{rId}_d"
    else: # check that the ID was not previously used
        for f in os.listdir(runsDir):
            if f.startswith('.DS_'):
                continue
            tmpPath = os.path.join(runsDir, f)
            if os.path.isdir(tmpPath):
                if f == rId:
                    sys.stderr.write(f"\nERROR: the run ID {f} was used in a previous run.\n")
                    sys.stderr.write("Remove the previous run or choose a different run ID.\n")
                    sys.exit(-5)
    return rId



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
    """Main function executing SonicParanoid"""
    # Extract info about GCC compiler
    # gccInfoTpl = check_gcc()
    # check that everything was installed correctly
    root = os.path.dirname(os.path.abspath(__file__))
    # get SonicParanoid version
    softVersion = pkg_resources.get_distribution("sonicparanoid").version
    # settings for the hashing algorithm
    hashAlgo = "sha256"
    hashBits = 256
    # Will contain information to be printed in the info file
    infoDict: dict[
str, str] = {}
    # start measuring the execution time
    ex_start = time.perf_counter()
    #Get the parameters
    args, parser = get_params(softVersion)
    # start setting the needed variables
    debug: bool = args.debug
    # Initialize the main logger
    logLevel: int = logging.INFO
    if debug:
        logLevel = logging.DEBUG

    # Initialize root Logger
    if debug:
        logging.basicConfig(format='{levelname} :: {name}:\n{message}', style="{", level=logging.DEBUG)
    else:
        # logging.basicConfig(level=logging.INFO)
        logging.basicConfig(format='{levelname}:\n{message}', style="{", level=logging.INFO)

    # compression settings
    noCompress: bool = args.no_compress
    complev: int = args.compression_lev # Filter warnings
    # Check compression level
    if (complev < 1) or (complev > 9):
        sys.stderr.write(f"\nWARNING: The complev parameter must be \
            between 1 and 9 while it was set to {complev}\n")
        sys.stderr.write("It will be set to the default [complev=5].\n")
        complev = 5
    # Set warning level
    filter_warnings(debug)
    # perform normal alignments
    complete_aln: bool = args.complete_aln
    # Check if a CONDA or Mamba environment is being used
    condaType: str = ""
    condaRun: bool = False
    # Check if a Mamba environment is being used
    condaRun, condaType = systools.is_mamba_env()
    # If not a Mamba env, check if it a Conda env
    if not condaRun:
        condaRun, condaType = systools.is_conda_env()
    # in case of Mamba or Conda env use the binaries installed
    # in those specific environments
    if condaRun:
        for toolName in ["blastp", "diamond", "mmseqs", "mcl"]:
            if which(toolName) is None:
                sys.stderr.write(f"\nERROR: {toolName} could not be found, \
                    please install it using {condaType}.")
                sys.exit(-10)
    # Check that the binaries are were installed
    # in the traditional way (not CONDA)
    else:
        # check BLAST installation
        check_blast_installation(root, debug=debug)
        # check Diamond installation
        check_dmnd_installation(root, debug=debug)
        # check MMseqs2 installation
        check_mmseqs_installation(root, debug=debug)
        # check MCL installation
        check_mcl_installation(os.getcwd(), debug=debug)

    # set main directories
    inDir: str = ""
    if len(args.input_directory) > 0:
        inDir = f"{os.path.realpath(args.input_directory)}"
    # check that the input directory has been provided
    if not os.path.isdir(inDir):
        sys.stderr.write(f"\nERROR: the directory with input proteomes is not valid.\n{inDir}\n")
        parser.print_help()
    # output dir
    outDir: str = os.path.realpath(args.output_directory)
    # obtain input paths
    inPaths = get_input_paths(inDir, debug=debug)

    # Pair-wise tables directory
    pairwiseDbDir = os.path.join(outDir, "orthologs_db")
    systools.makedir(pairwiseDbDir)
    # Runs directory
    runsDir = os.path.join(outDir, "runs/")
    systools.makedir(runsDir)
    # set the update variable
    update_run = False
    # check that the snapshot file exists
    snapshotFile = os.path.join(outDir, "snapshot.tsv")
    if update_run:
        # check that it is not the first run
        if not os.path.isfile(snapshotFile):
            sys.stderr.write("\nWARNING: no snapshot file found. \
                The run will considered as the first one.\n")
            update_run = False
    else:
        # force the variable to true if a snapshot exists
        if os.path.isfile(snapshotFile):
            update_run = True

    # Optional directories setup
    alignDir = None
    if args.shared_directory is not None:
        alignDir = os.path.realpath(args.shared_directory)
    else:
        alignDir = os.path.join(outDir, "alignments/")
        systools.makedir(alignDir)
    dbDirectory = None
    if args.seqs_dbs is not None:
        dbDirectory = os.path.realpath(args.mmseqs_dbs)
    else:
        dbDirectory = os.path.join(outDir, "seqs_dbs/")
    threads: int = args.threads
    minBitscore: int = args.min_bitscore
    # Make sure the bitscore is not too low or too high
    if minBitscore < 35:
        sys.stderr.write(f"\tWARNING: the minimum bitscore ({minBitscore}) should not be \
            lower than 35 (default is 40). It will be set to 35.")
        minBitscore = 35
    elif minBitscore > 200:
        sys.stderr.write(f"\tWARNING: the minimum bitscore ({minBitscore}) should not be \
            higher than 200 (default is 40). This might cause only very recent orthologs to be identified. \
                The value will be automatically set 200")
        minBitscore = 200
    # Minimu query coverage to integrate new arch based orthologs
    tblMergeThr: float = args.min_arch_merging_cov
    # Make sure the bitscore is not too low or too high
    if tblMergeThr < 0.75:
        sys.stderr.write(f"\tWARNING: the minimum merging coverage ({tblMergeThr}) should not be \
            lower than 0.75 (default is 0.75). It will be set to 0.75.")
        tblMergeThr = 0.75
    elif tblMergeThr > 1:
        sys.stderr.write(f"\tWARNING: the minimum merging coverage ({tblMergeThr}) cannot be \
            higher than 1 (default is 0.75). The value will be automatically set 1")
        tblMergeThr = 1.0

    owOrthoTbls: str = args.overwrite_tables
    skipMulti: str = args.skip_multi_species
    graphOnlyOrthology: str = args.graph_only
    # Check the PFamA DB if arch-based predictions will be performed
    if not graphOnlyOrthology:
        archortho.check_pfama_profile_db(threads=threads)

    ''' TODO: remove (legacy code)
    slc: bool = args.single_linkage
    maxGenePerSp = args.max_gene_per_sp
    '''
    overwrite = args.overwrite
    if overwrite:
        owOrthoTbls = True
        # remove all the mmseqs2 index files
        if os.path.isdir(dbDirectory):
            for f in os.listdir(dbDirectory):
                fpath = os.path.join(dbDirectory, f)
                try:
                    if os.path.isfile(fpath):
                        os.unlink(fpath)
                    elif os.path.isdir(fpath):
                        rmtree(fpath)
                except Exception as e:
                    print(e)

    # Set aligner, sensitivity, mode
    runMode: str = args.mode
    alnTool: str = ""
    dmndSensitivity: str = "" # This is the fastest mode possible
    mmseqsSensitivity: float = 4.0
    runMode, alnTool, dmndSensitivity, mmseqsSensitivity = map_mode2sensitivity(args=args, debug=debug)

    # set the maximum length difference allowed if difference from default
    if args.max_len_diff != 0.5:
        if not 0. <= args.max_len_diff <= 1.0:
            sys.stderr.write('\nERROR: the length difference ratio must \
                have a value between 0 and 1.\n')
            sys.exit(-6)
    # set the variable to control the creation of orthologous pairs
    output_relations = args.output_pairs
    # set the variable for MMseqs2 database indexing
    idx_dbs: bool = False
    if args.index_db:
        idx_dbs = True

    # Set some values do the use of BLAST
    if alnTool == "blast":
        sys.stdout.write("INFO: blastp is executed with default parameters.")
        if idx_dbs:
            idx_dbs = False
            sys.stdout.write("\nINFO: blastp does not support DB indexing.\n\
The --index-db parameter was set to False.\n")
    elif alnTool == "diamond":
        if idx_dbs:
            idx_dbs = False
            sys.stdout.write("\nINFO: at present DB indexing with Diamond \
is not supported in SonicParanoid.\n\
The --index-db parameter was set to False.\n")

    # set the minimum memory required per thread
    minPerCoreMem: float = 1.25
    # Reduce memory requirement when using diamond
    if (alnTool == "diamond") or (alnTool == "blast"):
        minPerCoreMem = 1.0
    # adjust the number of threads if required
    newThreads: int = os.cpu_count()
    memPerCore: float = 0.
    if not args.force_all_threads:
        newThreads, memPerCore = check_hardware_settings(threads, minPerCoreMem, debug=debug)
        threads = newThreads
    else: # make sure that the requested threads is not higher than the available
        from psutil import virtual_memory, cpu_count
        if threads > newThreads:
            sys.stderr.write(f"\nWARNING: the number of requested threads ({threads}) \
is higher than the available ({newThreads})")
            sys.stderr.write(f"\nThe number of threads will be set to {newThreads}")
            threads = newThreads
        # now compute the memory per thread
        availMem: float = round(virtual_memory().total / 1073741824., 2)
        memPerCore = round(availMem / threads, 2)
    del newThreads

    # directory with header and species names mapping
    runID = set_project_id(rId=args.project_id, runsDir=runsDir, runMode=runMode, alnTool=alnTool, args=args, debug=debug)
    runDir = os.path.join(runsDir, runID)
    # Will contains auxiliary files, like the prediction matrixes or pckl files
    auxDir = os.path.join(runDir, "aux/")
    systools.makedir(auxDir)
    # Pair-wise tables directory
    tblDir = os.path.join(runDir, "pairwise_orthologs/")
    systools.makedir(tblDir)
    # Directory with ortholog groups
    multiOutDir = os.path.join(runDir, 'ortholog_groups/')
    systools.makedir(multiOutDir)
    # variable ued in the update of input files
    updateInputNames = args.update_input_names
    removeOldSpecies = args.remove_old_species
    # name for multispecies groups
    multiSpeciesClstrNameAll = 'ortholog_groups.tsv'

    # set the MCL inflation rate
    inflation: float = args.inflation
    if (inflation < 1.2) or (inflation > 5):
        sys.stderr.write(f"\nWARNING: The inflation rate parameter must be \
            between 1.2 and 5.0 while it was set to {inflation:.2f}\n")
        sys.stderr.write("It will be automatically set to 1.5\n")
        inflation = 1.5

    # Set the prefilter matrix for MMseqs prefilter
    pmtx:str = "vtml80"
    print(f"\nRun START:\t{str(time.asctime(time.localtime(time.time())))}")
    print(f"SonicParanoid {softVersion} will be executed with the following parameters:")
    print(f"Run ID:\t{runID}")
    print(f"Input directory: {inDir}")
    print(f"Main output directory: {outDir}")
    print(f"Run directory: {runDir}")
    print(f"Input proteomes:\t{len(inPaths)}")
    print(f"Alignment tool:\t{alnTool}")
    if alnTool == "diamond":
        print(f"Run mode:\t{runMode} (Diamond [--{dmndSensitivity}])")
    elif alnTool == "mmseqs":
        print(f"Run mode:\t{runMode} (MMseqs2 s={mmseqsSensitivity:.2f})")
        print(f"Prefilter matrix (MMsesq2):\t{pmtx}")
    else:
        print(f"Run mode:\t{runMode} (Blast)")
    print(f"Threads:\t{threads}")
    print(f"Minimum bitscore:\t{minBitscore}")
    print(f"Max length difference for in-paralogs:\t{args.max_len_diff:.2f}")
    print(f"Ortholog merging threshold:\t{tblMergeThr:.2f}")
    print(f"MCL inflation:\t{inflation:.2f}")
    # Output directories
    print(f"Alignments directory: {alignDir}")
    print(f"Pairwise tables directory: {tblDir}")
    print(f"Directory with ortholog groups: {multiOutDir}")
    print(f"Pairwise tables database directory: {pairwiseDbDir}")
    # Other general settings
    print(f"Perfom only graph-based orthology:\t{graphOnlyOrthology}")
    print(f"Update run:\t{str(update_run)}")
    print(f"Create query database indexes:\t{str(idx_dbs)}")
    print(f"Complete overwrite:\t{overwrite}")
    print(f"Re-create ortholog tables:\t{owOrthoTbls}")
    print(f"Memory per thread (Gigabytes):\t{memPerCore:.2f}")
    print(f"Minimum memory per thread (Gigabytes):\t{minPerCoreMem:.2f}")
    print(f"Compress alignments:\t{not(noCompress)}")
    if not noCompress:
        print(f"Compression level:\t{complev}")
    print(f"SonicParanoid installation directory: {os.path.dirname(__file__)}")
    print(f"Installation type:\t{condaType}")
    print(f"Python version: {sys.version}")
    print(f"Python executables: {sys.executable}")
    # print(f"GCC version: {gccInfoTpl[1]}")

    # Populate the info dictionary
    infoDict["Date:"] = time.asctime(time.localtime(time.time()))
    infoDict["Version"] = softVersion
    infoDict["Run ID:"] = runID
    infoDict["Input directory:"] = inDir
    infoDict["Main output directory:"] = outDir
    infoDict["Run directory:"] = runDir
    infoDict["Input proteomes:"] = str(len(inPaths))
    infoDict["Run mode:"] = runMode
    infoDict["Alignment tool:"] = alnTool
    if alnTool == "diamond":
        infoDict["Diamond sensitivity:"] = dmndSensitivity
    elif alnTool == "mmseqs":
        infoDict["MMseqs sensitivity:"] = f"{mmseqsSensitivity:.2f}"
        infoDict["MMseqs prefilter matrix:"] = pmtx
    infoDict["Threads:"] = str(threads)
    infoDict["Minimum bitscore:"] = str(minBitscore)
    infoDict["Max length difference for in-paralogs:"] = str(args.max_len_diff)
    infoDict["Ortholog tables-merging threshold:"] = f"{tblMergeThr:.2f}"
    infoDict["MCL inflation:"] = str(args.inflation)
    # Output directories
    infoDict["Sequence DB directory:"] = str(dbDirectory)
    infoDict["Alignment directory:"] = str(alignDir)
    infoDict["Pairwise tables DB directory:"] = str(pairwiseDbDir)
    infoDict["Directory with pairwise orthologs:"] = str(tblDir)
    infoDict["Directory with ortholog groups:"] = str(multiOutDir)
    infoDict["Memory per threads (Gigabytes):"] = str(memPerCore)
    infoDict["Minimum memory per threads (Gigabytes):"] = str(minPerCoreMem)
    # Other general settings
    infoDict["Perfom only graph-based orthology:"] = str(graphOnlyOrthology)
    infoDict["Update run:"] = str(update_run)
    infoDict["Create query database indexes:"] = str(idx_dbs)
    infoDict["Complete alignments:"] = str(complete_aln)
    infoDict["Overwrite pair-wise ortholog tables:"] = str(args.overwrite_tables)
    infoDict["Complete overwrite:"] = str(args.overwrite)
    infoDict["Skip creation of ortholog groups:"] = str(args.skip_multi_species)
    infoDict["Compress alignments:"] = str(not noCompress)
    if not noCompress:
        infoDict["Compression level:"] = str(complev)
    else:
        infoDict["Compression level:"] = "0"
    # if not args.single_linkage:
    ''' TODO: legacy code to be removed
    if debug:
        infoDict["Directory with SonicParanoid runs:"] = str(runsDir)
        if args.single_linkage:
            infoDict["Maximum gene per species in groups:"] = str(args.max_gene_per_sp)
    '''
    infoDict["SonicParanoid installation:"] = os.path.dirname(__file__)
    # This the default python environment (Not Conda or Mamba)
    infoDict["Installation type:"] = condaType
    infoDict["Python version:"] = sys.version
    infoDict["Python executables:"] = sys.executable
    # infoDict["GCC version:"] = gccInfoTpl[1]
    # Check if the run already exists
    spFile = pairsFile = None

    # New run
    if not update_run:
        if debug:
            print("First run!")
        # write the file with information on the first run
        infoFile = write_run_info_file(runDir, infoDict, debug)
        copy(infoFile, os.path.join(infoDict["Main output directory:"], "last_run_info.txt"))
        print(f"runID:\t{runID}")

        # Compute digests
        digestDict, repeatedFiles = idmapper.compute_hash_parallel(inPaths, algo=hashAlgo, bits=hashBits, threads=threads, debug=debug)
        spFile, mappedInputDir, mappedInPaths = idmapper.map_hdrs_parallel(inPaths, outDir=auxDir, digestDict=digestDict, idMapDict={}, threads=threads, debug=debug)
        # Make sure there is no file in the input with no sequences
        validate_species_file(spFile)
        del digestDict
        del repeatedFiles
        del mappedInputDir
        # create the snapshot file
        copy(spFile, snapshotFile)

        # Perform alignments and predict orthologs
        spFile, pairsFile, requiredPairsDict = orthodetect.run_sonicparanoid2_multiproc_essentials(mappedInPaths, outDir=runDir, tblDir=pairwiseDbDir, threads=threads, alignDir=alignDir, seqDbDir=dbDirectory, sensitivity=mmseqsSensitivity, create_idx=idx_dbs, alnTool=alnTool, dmndSens=dmndSensitivity, minBitscore=minBitscore, confCutoff=0.05, pmtx=pmtx, lenDiffThr=args.max_len_diff, overwrite_all=overwrite, overwrite_tbls=owOrthoTbls, update_run=update_run, keepAlign=args.keep_raw_alignments, essentialMode=not(complete_aln), compress=not(noCompress), complev=complev, debug=debug)

        # Perfom arch-based orthology
        if not graphOnlyOrthology:
            pairwiseDbDir = archortho.infer_arch_based_orthologs(mappedInPaths=mappedInPaths, outDir=outDir, runDir=runDir, seqDbDir=dbDirectory, modelPrefix=runID, overwrite_all=overwrite, overwrite_tbls=owOrthoTbls, update_run=update_run, compress=not(noCompress), complev=complev, tblMergeThr=tblMergeThr, threads=threads)

        # predict pairwise orthology
        # HACK: restore this if it does not work
        # spFile, pairsFile, requiredPairsDict = orthodetect.run_sonicparanoid2_multiproc_essentials(mappedInPaths, outDir=runDir, tblDir=pairwiseDbDir, threads=threads, alignDir=alignDir, seqDbDir=dbDirectory, create_idx=idx_dbs, sensitivity=mmseqsSensitivity, cutoff=minBitscore, confCutoff=0.05, pmtx=pmtx, lenDiffThr=args.max_len_diff, overwrite_all=overwrite, overwrite_tbls=owOrthoTbls, update_run=update_run, keepAlign=args.keep_raw_alignments, essentialMode=not(complete_aln), compress=not(noCompress), complev=complev, debug=debug)
        # remap the pairwise relations
        remap.remap_pairwise_relations_parallel(pairsFile, runDir=runDir, orthoDbDir=pairwiseDbDir, mergedTables=not(graphOnlyOrthology), threads=threads, debug=debug)
        gc.collect()
        # sys.exit("DEBUG@sonicparanoid: [FIRST RUN] after remap.remap_pairwise_relations_parallel")

    # Update Run
    else:
        if debug:
            print("Update run!")
        # update the run info
        spFile, mappedInputDir, mappedInPaths = idmapper.update_run_info(inPaths=inPaths, outDir=auxDir, oldSpFile=snapshotFile, algo="sha256", bits=256, threads=threads,  updateNames=updateInputNames, removeOld=removeOldSpecies, overwrite=(overwrite or owOrthoTbls), debug=debug)
        # Make sure there is no file in the input with no sequences
        validate_species_file(spFile)
        # perfom the sanity check
        sanity_check(infoDict, alnTool=alnTool, debug=debug)
        # sys.exit("DEBUG@sonicparanoid: [RUN_UPDATE] after sanity check")

        # write the file with information on the update run
        infoFile = write_run_info_file(runDir, infoDict, debug)
        # update info file for the last run
        copy(infoFile, os.path.join(infoDict["Main output directory:"], "last_run_info.txt"))

        # Perform alignments and predict orthologs
        spFile, pairsFile, requiredPairsDict = orthodetect.run_sonicparanoid2_multiproc_essentials(mappedInPaths, outDir=runDir, tblDir=pairwiseDbDir, threads=threads, alignDir=alignDir, seqDbDir=dbDirectory, sensitivity=mmseqsSensitivity, create_idx=idx_dbs, alnTool=alnTool, dmndSens=dmndSensitivity, minBitscore=minBitscore, confCutoff=0.05, pmtx=pmtx, lenDiffThr=args.max_len_diff, overwrite_all=overwrite, overwrite_tbls=owOrthoTbls, update_run=update_run, keepAlign=args.keep_raw_alignments, essentialMode=not(complete_aln), compress=not(noCompress), complev=complev, debug=debug)

        # Perfom arch-based orthology
        if not graphOnlyOrthology:
            minCosine: float = 0.50
            pairwiseDbDir = archortho.infer_arch_based_orthologs(mappedInPaths=mappedInPaths, outDir=outDir, runDir=runDir, seqDbDir=dbDirectory, modelPrefix=runID, overwrite_all=overwrite, overwrite_tbls=owOrthoTbls, update_run=update_run, compress=not(noCompress), tblMergeThr=tblMergeThr, complev=complev, threads=threads)
        # sys.exit("\nDEBUG:: sonicparanoid :: update-run :: write_run_info_file")

        # remap the pairwise relations
        remap.remap_pairwise_relations_parallel(pairsFile, runDir=runDir, orthoDbDir=pairwiseDbDir, mergedTables=not(graphOnlyOrthology), threads=threads, debug=debug)
        gc.collect()
        # sys.exit("DEBUG@sonicparanoid: [RUN_UPDATE] after remap.remap_pairwise_relations_parallel")

    # infer ortholog groups
    if not skipMulti:
        if len(inPaths) > 2:
            infer_orthogroups_mcl(orthoDbDir=pairwiseDbDir, sharedDir=runDir, outName=multiSpeciesClstrNameAll, pairsList=requiredPairsDict, inflation=inflation, threads=threads, condaRun=condaRun, mergedTables=not(graphOnlyOrthology), debug=debug)
        elif len(inPaths) == 2:
            infer_orthogroups_2_proteomes(orthoDbDir=pairwiseDbDir, outDir=multiOutDir,sharedDir=runDir, outName=multiSpeciesClstrNameAll, pairsDict=requiredPairsDict, mergedTables=not(graphOnlyOrthology), debug=debug)

    # remap species pairs file
    # load the mapping info
    id2SpDict, new2oldHdrDict = idmapper.load_mapping_dictionaries(runDir=auxDir, debug=debug)
    del new2oldHdrDict
    # create the pairs file with the original species names
    pairsFileRemapped = os.path.join(auxDir, "species_pairs_remapped.txt")
    with open(pairsFileRemapped, "w") as ofd:
        with open(pairsFile, "r") as ifd:
            for ln in ifd:
                sp1, sp2 = ln[:-1].split("-", 1)
                ofd.write(f"{id2SpDict[sp1]}-{id2SpDict[sp2]}\n")

    # generate file with pairwise relations
    if output_relations:
        # output directory for ortholog realtions
        relDict = os.path.join(runDir, "ortholog_relations")
        systools.makedir(relDict)
        # ALL
        orthoRelName = f"ortholog_pairs.{runID}.tsv"
        # Extract pairs
        timer_start: float = time.perf_counter()
        orthodetect.extract_ortholog_pairs(rootDir=os.path.join(runDir, "pairwise_orthologs"), outDir=relDict, outName=orthoRelName, pairsFile=pairsFileRemapped, singleDir=False, tblPrefix="", debug=debug)
        sys.stdout.write(f"Ortholog-pairs (benchmark file) creation time (seconds):\t\
{time.perf_counter() - timer_start:.3f}\n")
        del timer_start

    ex_end = round(time.perf_counter() - ex_start, 3)
    sys.stdout.write(f"\nTotal elapsed time (seconds):\t{ex_end:.3f}\n")

    # remove Aux files (mapped input files and job matrixes)
    rmtree(os.path.join(runDir, "aux"))
    # cleanup MMseqs2 DB files
    if os.path.isdir(dbDirectory):
        rmtree(dbDirectory)
    # remove matrix files
    mtxDir = os.path.join(outDir, "ortholog_matrixes")
    if os.path.isdir(mtxDir):
        # remove all its content
        rmtree(mtxDir)

    citation_and_help()



if __name__ == "__main__":
    main()
