"""This module contains different utility making use of linux programs like awk, grep etc."""
import sys
import os
import subprocess
import logging
from shutil import copyfileobj
from filetype import guess_mime

__module_name__ = "System Tools"
__source__ = "sys_tools.py"
__author__ = "Salvatore Cosentino"
#__copyright__ = ""
__license__ = "GPL"
__version__ = "1.4"
__maintainer__ = "Cosentino Salvatore"
__email__ = "salvo981@gmail.com"



# Logger that will be used in this module
# It is child of the root logger and
# should be initialiazied using the function set_logger()
logger: logging.Logger = logging.getLogger()



def info():
    """This module contains different utility making use of linux programs like awk, grep etc."""
    print(f"MODULE NAME:\t{__module_name__}")
    print(f"SOURCE FILE NAME:\t{__source__}")
    print(f"MODULE VERSION:\t{__version__}")
    print(f"LICENSE:\t{__license__}")
    print(f"AUTHOR:\t{__author__}")
    print(f"EMAIL:\t{__email__}")



def bzip2(path, outDir=os.getcwd(), level=9, overwrite=False, keep=True, debug=False):
    """Use bzip2 to compress the input archive to the output directory."""
    import bz2
    if debug:
        print('Input file:\t%s'%path)
        print('Output dir:\t%s'%outDir)
        print('Compression level:\t%d'%level)
        print('Overwrite existing compressed file:\t%s'%overwrite)
        print('Keep original file:\t%s'%keep)
    #check if the zip file is valid
    if not os.path.isfile(path):
        sys.stderr.write('\nERROR: %s is not a valid file.'%path)
        sys.exit(-2)
    # create the output directory
    makedir(outDir)
    # create the new path
    newName = '%s.bz2'%os.path.basename(path)
    outPath = os.path.join(outDir, newName)
    # check that the output file does not already exist
    if os.path.isfile(outPath):
        if not overwrite:
            sys.stderr.write('\nERROR: the archive %s already exists.\nSet overwrite=True to overwrite.'%outPath)
            sys.exit(-2)
    # open output file
    # note that this would completely load the input file in memory
    new_file = bz2.BZ2File(outPath, mode='wb', compresslevel=level)
    # now write the data
    new_file.write(bz2.compress(open(path, 'rb').read(), compresslevel=9))
    if debug:
        print('\nThe archive\n%s\nwas compressed to\n%s'%(path, outPath))
    # keep/remove original
    if not keep:
        os.remove(path)
        if debug:
            print('\nThe original raw file \n%s\n has been removed.'%(path))
    #return the path to the extracted archive
    return outPath



def copy(src, dst, metaData=False, debug=False):
    """Copy src file/dir to dst."""
    if debug:
        print('copy :: START')
        print('SRC:\t%s'%src)
        print('DEST:\t%s'%dst)
        print('METADATA:\t%s'%metaData)
    #check the existence of the input file
    if not os.path.isfile(src):
        sys.stderr.write('The file %s was not found, please provide a valid file path'%src)
        sys.exit(-2)
    #if src and dst are same, do nothing...
    if src == dst:
        sys.stderr.write('\nWARNING: Source and destination files are the same, nothing will be done.\n')
        return False
    import shutil
    #let's execute commands
    if metaData: #then also copy the metadata
        try:
            shutil.copy2(src, dst)
        # eg. src and dest are the same file
        except shutil.Error as e:
            print('Error: %s' % e)
        # eg. source or destination doesn't exist
        except IOError as e:
            print('Error: %s' % e.strerror)
    else:
        try:
            shutil.copy(src, dst)
        # eg. src and dest are the same file
        except shutil.Error as e:
            print('shutil.Error: %s' % e)
        # eg. source or destination doesn't exist
        except IOError as e:
            print('IOError: %s' % e.strerror)
    return True



def countLinesWc(inFile, debug=False):
    """Takes in input a text file and uses WC to count the number of lines."""
    if debug:
        print('countLinesWc :: START')
        print('INPUT:\n%s'%inFile)
    #check the existence of the input file
    if not os.path.isfile(inFile):
        sys.stderr.write('The file %s was not found, please provide a input path'%inFile)
        sys.exit(-2)
    #let's prepare and execute the command
    cmd = 'wc -l %s'%inFile
    tmp = subprocess.check_output(cmd, stderr=subprocess.PIPE, shell=True)
    inLines = int(tmp.split()[0])
    if debug:
        print('COUNT LINES CMD:\n%s'%cmd)
        print('COUNTED LINES:\t%d'%inLines)
    return inLines



def chopString(s, n, debug=False):
    """
    Chop strings to a given size.
    Produce (yield) \'n\'-character chunks from \'s\'.
    """
    if debug:
        print('chopString :: START')
        print('INPUT ::\t%s'%s)
        print('CHUNK LENGTH ::\t%d'%n)
        print('INPUT LENGTH ::\t%d'%len(s))
    for start in range(0, len(s), n):
        yield s[start:start+n]



def create_flogger(logPath: str, loggerName: str, lev: int = 10, mode: str = "a", propagate: bool = False) -> logging.Logger:
    """Create a logger that writes into a file"""
    # THIS CREATES THE GENERAL LOGGER
    logger: logging.Logger = logging.getLogger(loggerName)
    # set same level as the root
    logger.setLevel(lev)
    logger.propagate = propagate
    logFh: logging.FileHandler = logging.FileHandler(logPath, mode=mode)
    # This makes sure that the log file is created even if not in debug mode
    logFh.setLevel(lev)
    logFh.setFormatter(fmt=logging.Formatter('%(message)s'))
    logger.addHandler(logFh)

    return logger



def diff(f1, f2, outDir=os.getcwd(), outName=None, debug=True):
    """A wrapper for the unix diff program."""
    if debug:
        print('diff :: START')
        print('File 1:\n%s'%f1)
        print('File 2:\n%s'%f2)
        print('Output dir:\t%s'%outDir)
    #check the existence of the input files
    if not os.path.isfile(f1):
        sys.stderr.write('The file %s was not found, please provide a input path'%f1)
        sys.exit(-2)
    if not os.path.isfile(f2):
        sys.stderr.write('The file %s was not found, please provide a input path'%f2)
        sys.exit(-2)
    #create the output directory if does not exist yet
    if outDir[-1] != '/':
        outDir += '/'
    #create output directory
    makedir(outDir)
    #set the output name
    outputName = ''
    if outName is not None:
        if isinstance(outName) is str:
            outputName = outName.strip()
            #outputName = ''.join(outputName.split(' ')) #remove intenal spaces if any
            outputName = outputName.replace(' ', '') #remove intenal spaces if any
    else:
        outName = '%s-%s_diff.txt'%(os.path.basename(f1), os.path.basename(f2))
    #output file
    outPath = '%s%s'%(outDir, outName)
    #Unix diff example
    # diff <f1> <f2>
    cmd = 'diff %s %s > %s'%(f1, f2, outPath)
    process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout_val, stderr_val = process.communicate() #get stdout and stderr
    process.wait()
    if debug:
        print('Diff command:\n%s'%str(cmd))
    if debug:
        print('Diff STDOUT:\n%s'%stdout_val)
        print('Diff STDERR:\n%s'%stderr_val)
    #check the length of the diff file
    diffLen = countLinesWc(outPath, debug=debug)
    if diffLen == 0:
        return (False, outPath)
    else:
        return (True, outPath)



def evalCpuNeeds(totLn, algorithm=None, debug=False):
    """
    Estimates the number of needed threads (cores) based on the total lines to be processed
    For the supported algorithms an estimation is given but should be updated when possible
    NOTES: it is very experimental and based on a very few samples
    """
    import multiprocessing
    maxCores = multiprocessing.cpu_count()
    buckets = [2, 4, 8, 12, 16, 24, 32, 48, 64, 96, 128]
    #input summary...
    if debug:
        print('\n evalCpuNeeds START:')
        print('TOT LINES ::\t%s'%str(totLn))
        print('ALGORITHM ::\t%s'%str(algorithm))
    chunkDict = {'bwa':720000, 'map_pct_calc':400000, 'avg':560000}
    #if all the arguments are NONE then we set bwa as algorithm
    if algorithm is None:
        algorithm = 'avg'
    chunkSize = chunkDict[algorithm]
    if chunkSize >= totLn:
        if debug:
            print('Chunk size is bigger than the line to be porcessed, 1 core will do just fine...')
        return 1
    cores = int(totLn/chunkSize)
    if debug:
        print('Selected Algorimth for Estimation:\t%s'%algorithm)
        print('CHUNK SIZE FOR %s ALGORITHM:\t%d'%(algorithm.upper(), chunkSize))
    if cores >= maxCores:
        return maxCores
    #selelct the bucket if needed
    if algorithm != 'map_pct_calc':
        for el in buckets:
            if float(cores/el) <= 1:
                return el
    return cores



def getCpuCount():
    """Get the number of cpu available in the system."""
    import multiprocessing
    return multiprocessing.cpu_count()



def getElapsedTime(f1, f2, timeStamps=False, debug=True):
    """Calculate the elapsed time between the creation of the first file and last access to the second."""
    if debug:
        print('getElapsedTime :: START')
        print(f"File 1:\n{f1}")
        print(f"File 2:\n{f2}")
        print('Timestamps:\n%s'%timeStamps)
        #if timeStamps is True then each file must contain a single unix timestamp
    #check the existence of the input files
    if not os.path.isfile(f1):
        sys.stderr.write('The file %s was not found, please provide a input path'%f1)
        sys.exit(-2)
    if not os.path.isfile(f2):
        sys.stderr.write('The file %s was not found, please provide a input path'%f2)
        sys.exit(-2)
    bf1 = os.path.basename(f1)
    bf2 = os.path.basename(f2)
    #Do in a different way depending if the files contain timestamps or not
    ts1_ct = ts2_mt = None
    if timeStamps:
        tmpFd = open(f1)
        ts1_ct = int(tmpFd.readline().strip()) #read the timestamp
        tmpFd.close()
        tmpFd = open(f2)
        ts2_mt = int(tmpFd.readline().strip()) #read the timestamp
        tmpFd.close()
    else: #then use os.stat
        import stat
        ts1_ct = os.stat(f1).st_ctime #get creation time
        #NOTE: if the file has been not accessed and has been copied with its original metadata, the time could be older than then ts1_ct
        ts2_mt = os.stat(f2).st_mtime #get latest access time
    #now convert them to using datetime
    import datetime as dt
    #t1 = dt.datetime.utcfromtimestamp(ts1_ct)
    #t2 = dt.datetime.utcfromtimestamp(ts2_mt)
    t1 = dt.datetime.fromtimestamp(ts1_ct)
    t2 = dt.datetime.fromtimestamp(ts2_mt)

    if debug:
        print('%s was created on %s'%(bf1, str(t1)))
        print('%s was last modified on %s'%(bf2, str(t2)))
    #no calculate the time difference
    delta = t2 - t1
    #following is the elapsed time between the creation of f1 and the last modification of f2
    sec = int(delta.total_seconds())
    minutes = round(sec/60., 2)
    hours = round(sec/3600., 2)
    days = round(sec/86400.656, 2)
    if debug:
        print('Elapsed time (%s - %s)'%(bf2, bf1))
        print('Seconds:\t%d'%sec)
        print('Minutes:\t%s'%str(minutes))
        print('Hours:\t%s'%str(hours))
        print('Days:\t%s'%str(days))
    return(sec, minutes, hours, days)



def getShell():
    """Get the shell type used by the system."""
    shellPath = os.environ["SHELL"]
    #check the shell type and return it
    if shellPath.endswith('csh'):
        return 'csh'
    elif shellPath.endswith('bash'):
        return 'bash'
    else: #add other shell types
        return None



def is_conda_env() -> tuple[bool, str]:
    """
    Check if a CONDA environment is being used.
    """
    # The identification is done based on the path of the python binaries
    # Possible paths are chosen based on conda documentation
    # https://docs.anaconda.com/anaconda/user-guide/tasks/integration/python-path
    condaTypes: list[str] = ["conda", "anaconda", "anaconda2", "anaconda3", "anaconda4", "miniconda", "miniconda2", "miniconda3", "miniconda4"]
    # Extract the path with the binaries
    pyBinPrefix: str = sys.exec_prefix
    # Check if the prefix contains one of the anaconda path keywords
    for kwrd in condaTypes:
        if f"/{kwrd}/" in pyBinPrefix:
            logger.debug(f"A CONDA environment ({kwrd}) is being used.")
            return (True, kwrd)
    return (False, "Python")



def is_mamba_env() -> tuple[bool, str]:
    """
    Check if a Mamba environment is being used.
    """
    # The identification is done based on the path of the python binaries
    # Possible paths are chosen based on conda documentation
    # https://docs.anaconda.com/anaconda/user-guide/tasks/integration/python-path
    mambaTypes: list[str] = ["mamba", "micromamba"]
    # Extract the path with the binaries
    pyBinPrefix: str = sys.exec_prefix
    # Check if the prefix contains one of the anaconda path keywords
    for kwrd in mambaTypes:
        if f"/{kwrd}/" in pyBinPrefix:
            logger.debug(f"A Mamba environment ({kwrd}) is being used.")
            return (True, kwrd)
    return (False, "Python")



def makedir(path):
    """Create a directory including the intermediate directories in the path if not existing."""
    # check the file or dir does not already exist
    if os.path.isfile(path):
        sys.stderr.write("\nWARNING: {:s}\nalready exists as a file, and the directory cannot be created.\n".format(path))
    try:
        os.makedirs(path)
    except OSError:
        if not os.path.isdir(path):
            raise



def move(src, dst, debug=False):
    """Recursively moves src to dst."""
    if debug:
        print('move :: START')
        print('SRC:\n%s'%src)
        print('DEST:\n%s'%dst)
    #check the existence of the input file
    if not os.path.exists(src):
        sys.stderr.write('%s was not found, please provide a valid path'%src)
        sys.exit(-2)
    import shutil
    #let's execute command
    if os.path.exists(dst): #then we should use copy
        #copy and remove the source file
        copy(src, dst, True, debug)
        os.remove(src)
    else:
        shutil.move(src, dst)



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



def splitTxtFileAwk(inFile, outDir=os.getcwd(), inLines=None, chunks=2, suffix=None, debug=False):
    """Takes in input a text file and uses AWK to split the in n (chunks) part of almost the same size."""
    if debug:
        print('splitTxtFileAwk :: START')
        print('INPUT:\n%s'%inFile)
        print('OUT DIR ::\t%s'%outDir)
        print('INPUT LINES ::\t%s'%str(inLines))
        print('CHUNKS ::\t%d'%chunks)
        print('OUTPUT SUFFIX ::\t%s'%str(suffix))
    #check the existence of the input file
    if not os.path.isfile(inFile):
        sys.stderr.write('The file %s was not found, please provide a input path'%inFile)
        sys.exit(-2)
    if not os.path.isdir(outDir):
        sys.stderr.write('ERROR: the output directory %s does not exist'%outDir)
        sys.exit(-2)
    #check that the number of chunk is at least 2
    if chunks < 2:
        sys.stderr.write('WARNING: the chunks parameter must be at least 2 nothing will be done for the input file')
        sys.exit(-3)
    #count the number of lines if needed
    if inLines == None:
        cmd = 'wc -l %s'%inFile
        tmp = subprocess.check_output(cmd, stderr=subprocess.PIPE, shell=True)
        inLines = int(tmp.split()[0])
        if debug:
            print('COUNT LINES CMD:\n%s'%cmd)
            print('COUNTED LINES:\t%d'%inLines)
    if suffix == None:
        suffix = '_part'
    outPartName = os.path.basename(inFile)
    flds = outPartName.split('.')
    outPartName = flds[0]
    del flds
    outPartName = outPartName + suffix
    #estimate the size of each chunk
    chunkSize = 0
    while True:
        #if debug:
            #print('%d * %d = %d'%(chunkSize, chunks, chunkSize*chunks))
        if chunkSize*chunks < inLines:
            chunkSize += 1
        else:
            break
    if debug:
        print('CHUNK SIZE:%d'%chunkSize)
    #AWK SPLIT EXAMPLE
    #awk 'NR%3000==1{x="sam_chunk_"++i;}{print > x}' stool_ion_nsf001_se_mapped_bwa_mapped.sam
    splitCmd = 'awk \'NR%%%d==1{x="%s"++i;}{print > x}\' %s'%(chunkSize, outDir + outPartName, inFile)
    if debug:
        print('AWK SPLIT CMD:\n%s'%splitCmd)
    #execute the system call
    process = subprocess.Popen(splitCmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout_val, stderr_val = process.communicate() #get stdout and stderr
    process.wait()
    if debug:
        print('\nSTDOUT:\n%s'%repr(stdout_val))
        print('\nSTDERR:\n%s'%repr(stderr_val))
    #check that all the parts have been created
    partsList = []
    for i in range(1, chunks+1):
        path = outDir + outPartName + str(i)
        if os.path.isfile(path):
            partsList.append(path)
        else:
            sys.stderr.write('ERROR: not all the file parts were successfully created...')
            if debug:
                print(path)
            sys.exit(-1)
    if debug:
        print('created files:\t%d'%len(partsList))
        #print(str(partsList))
    return partsList



def unxz(path: str, outDir: str = os.getcwd(), debug: bool = False) -> str:
    """Decompress an xz or lzma archive created using the lzma compression algorithm."""
    import lzma
    if debug:
        print("\nunzx :: START")
        print(f"xz/lzma file path:\t{path}")
        print(f"Output dir:\t{outDir}")

    # Try to guess the type of archive using filetype
    guessedMime = guess_mime(path)
    if guessedMime is None:
        sys.stderr.write(f"\nERROR: the format of\n{path}\n could not be guessed.")
        sys.exit(-2)
    else:
        # make sure it is XZ
        if (guessedMime != "application/x-xz") and (guessedMime != "application/x-lzma"):
            sys.stderr.write(f"\nERROR: {path} is not a valid xz/lzma archive.")
            sys.exit(-2)

    # Create output dir
    makedir(outDir)
    # Remove extension from output file if needed
    archiveExtension: str = ""
    archiveBname: str = os.path.basename(path)
    unarchivedPath: str = os.path.join(outDir, archiveBname)
    if archiveBname.endswith(".xz"):
        unarchivedPath = unarchivedPath[:-3]
        archiveExtension = "xz"
    elif path.endswith(".lzma"):
        unarchivedPath = unarchivedPath[:-5]
        archiveExtension = "lzma"

    # Make sure input and output paths differ
    if unarchivedPath == path:
        sys.stderr.write(f"\nERROR: the input\n{path}\nand output\n {unarchivedPath}\nmust be different.")
        sys.exit(-2)

    # Write decompress the file
    # NOTE: copyfileobj is used to avoid
    # opening the compressed file in completely in memory
    # and to read and write in small chunks instead
    with lzma.open(path, mode="rb") as srcfile:
        with open(unarchivedPath, mode="wb") as dstfile:
            copyfileobj(srcfile, dstfile)

    # NOTE: XZ only compresses single files. Directories must be first packaged using tar.
    if not os.path.isfile(unarchivedPath):
        sys.stderr.write("\nERROR: the archive extraction went wrong.")
        sys.stderr.write(f"\nThe uncompressed file/directory\n{unarchivedPath} does not exist.")
        sys.exit(-3)

    if debug:
        print(f"\nThe archive\n{path}\nwas succesfully extracted to\n{unarchivedPath}")
    #return the path to the extracted archive
    return unarchivedPath



def untar(tarpath, outDir=os.getcwd()):
    import tarfile
    """Extract all files in tar archive to the specified directory"""
    logger.debug(f"Tar.gz path: {tarpath}\n\
    Output dir: {outDir}")
    #check if the tar file is valid
    if not tarfile.is_tarfile(tarpath):
        sys.stderr.write(f"\nERROR: {tarpath} is not a valid tar.gz file.")
        sys.exit(-2)
    #create output directory
    makedir(outDir)
    #change current directory
    cwd = os.getcwd()
    if os.path.dirname(outDir) != cwd:
        os.chdir(outDir)
    #open the tar file
    tar = tarfile.open(tarpath, mode="r")
    # print(tar.list(verbose=True))
    for member in tar.getmembers():
        tar.extract(member, path=outDir)
    tar.close()
    #set the current directory to the starting one
    os.chdir(cwd)
    logger.debug(f"Extracted in\n{outDir}")



def unzip(path, outDir=os.getcwd(), debug=False):
    """Unzip the input archive to the output directory."""
    import zipfile
    if debug:
        print('Zip path:\t%s'%path)
        print('Output dir:\t%s'%outDir)
    #check if the zip file is valid
    if not zipfile.is_zipfile(path):
        sys.stderr.write('\nERROR: %s is not a valid zip file.'%path)
        sys.exit(-2)
    # Create a ZipFile Object Instance
    archive = zipfile.ZipFile(path, 'r')
    zipInfo = archive.infolist()
    #get the root directory name
    zipRootName = zipInfo[0].filename
    cwd = os.getcwd()
    if os.path.dirname(outDir) != cwd:
        os.chdir(outDir)
    unarchivedPath = '%s%s'%(outDir, zipRootName)
    if os.path.isdir(unarchivedPath):
        sys.stderr.write('\nWARNING: the directory %s already exists! Its content will be overwritten.'%unarchivedPath)
    #list files in the archive
    archive.extractall(outDir)
    archive.close()
    if not os.path.isdir(unarchivedPath):
        sys.stderr.write('\nERROR: the archive extraction went wrong.')
        sys.stderr.write('\nThe uncompressed directory %s does not exist.'%unarchivedPath)
        sys.exit(-3)
    #set the current directory to the starting one
    os.chdir(cwd)
    if debug:
        print('\nThe archive\n%s\nwas succesfully extracted to\n%s'%(path, unarchivedPath))
    #return the path to the extracted archive
    return unarchivedPath



def test_bzip2(debug=False):
    """Test the function to bzip2 an archive."""
    archiveDir = '/home/salvocos/tmp/test_sys_tools/input/'
    inRaw = '%smmseqs_qfo_S40_avx2_core_relations.tsv'%(archiveDir)
    outDir = '/home/salvocos/tmp/'
    overwrite = True
    keep = False
    lev = 9
    #unarchive
    bzip2(inRaw, outDir=outDir, level=lev, overwrite=overwrite, keep=keep, debug=debug)



def test_chopString(debug=True):
    """Chop strings to a given size."""
    inStr = 'abcderfghailmnopurst'
    chunksGen = chopString(inStr, 5, debug)
    for el in chunksGen:
        print(el)



def test_copy(debug=True):
    """Test the copy of files."""
    src = '/user/gen-info/salvocos/projects/pathogenFinder2/gold_data/test_gbk_conversion/209915368.gbk'
    outTestDir = '/user/gen-info/salvocos/projects/pathogenFinder2/gold_data/test_gbk_conversion/fasta/'
    #to dir
    #copy(src, outTestDir, False, debug)
    #to dir (metadata)
    #copy(src, outTestDir, True, debug)
    #to complete target (metadata)
    #copy(src, outTestDir+'minchia_meta.gbk', True, debug)
    #to complete target
    copy(src, outTestDir+os.path.basename(src), False, debug)



def test_countLinesWc(debug=False):
    """Test the function to count lines."""
    #input
    inFile = '/user/gen-info/salvocos/test_directory/samtools/stool_ion_nsf001_se_mapped_bwa.sam'
    #no input lines
    countLinesWc(inFile, debug)



def test_diff(debug=False):
    """Test the function to execute the UNIX diff."""
    #DEFINTION: diff(f1, f2, outDir=os.getcwd(), outName=None, debug=True):
    root = '/home/salvocos/tmp/test_sys_tools/'
    f1 = '%sinput/a.txt'%(root)
    f2 = '%sinput/b.txt'%(root)
    f3 = '%sinput/c.txt'%(root)
    outDir = '%sdiff/'%root
    #f1 != f2
    differ, diffPath = diff(f1, f2, outDir=outDir, outName=None, debug=debug)
    if debug:
        print('The input file are different:\t%s'%differ)
        print('Diff output file path:\t%s'%diffPath)
    #f2 == f3
    differ, diffPath = diff(f2, f3, outDir=outDir, outName='f2-f3.diff.txt', debug=debug)
    if debug:
        print('The input file are different:\t%s'%differ)
        print('Diff output file path:\t%s'%diffPath)



def test_evalCpuNeeds(debug=False):
    """Test the function to evaluate the number of needed cpus."""
    #EXAMPLE
    #evalCpuNeeds(totLn, algorithm=None, debug=False)
    #50M reads with BWA
    cores = evalCpuNeeds(50000000, 'bwa', debug)
    print('SUGGESTED NUMBER OF THREADS:\t%d'%cores)
    #5M reads, no algorithm
    cores = evalCpuNeeds(5000000, None, debug)
    print('SUGGESTED NUMBER OF THREADS:\t%d'%cores)



def test_getElapsedTime(debug=True):
    """Test estimation of elpsed time between creation and modification of 2 files."""
    #DEFINTION: getElapsedTime(f1, f2, debug=True)
    inputDir = '/home/salvocos/projects/fungal_genomes_riken/data/inparanoid_runs/ortholog_search/jcm_3685-jcm_9195/'
    f1 = '%sBLOSUM80'%(inputDir)
    #f2 = '%sOutput.jcm_3601-jcm_11330'%(inputDir)
    logFile = '%sinparanoid.log'%(inputDir)
    getElapsedTime(f1, logFile, timeStamps=False, debug=debug)
    #latest blastrun vs inparalog.log -> run_inparalog time
    lastBlast = '%sjcm_9195-jcm_3685'%(inputDir)
    getElapsedTime(lastBlast, logFile, timeStamps=False, debug=debug)
    #Use timestamps
    root = '/home/salvocos/tmp/test_sys_tools/'
    f1 = '%sinput/start_blast_normal'%(root)
    f2 = '%sinput/end_blast_normal_aa'%(root)
    getElapsedTime(f1, f2, timeStamps=True, debug=debug)



def test_getShell(debug=True):
    """test the function that returns the system shell type"""
    print(getShell())



def test_splitTxtFileAwk(debug=False):
    """Test the function split a file."""
    #EXAMPLE: splitTxtFileAwk(inFile, outDir=os.getcwd(), inLines=None, chunks=2, suffix= '_part', debug=False)
    inFile = '/user/gen-info/salvocos/test_directory/samtools/stool_ion_nsf001_se_mapped_bwa.sam'
    outDir = '/user/gen-info/salvocos/test_directory/samtools/tmp_stats/'
    #no input lines
    splitTxtFileAwk(inFile, outDir, None, 64, None, debug)



def test_unzip(debug=False):
    """Test the function to unzip an archive."""
    #DEFINTION: unzip(path, outDir=os.getcwd(), debug=False):
    archivesDir = '/home/salvocos/projects/fungal_genomes_riken/data/original_from_jcm/archives/'
    inZip = '%sJCM_9478.zip'%(archivesDir)
    outDir = '/home/salvocos/tmp/'
    #unarchive
    unzip(inZip, outDir=outDir, debug=debug)



def test_untar(debug=False):
    """Test the function to untar an archive."""
    #DEFINTION: untar(path, outDir=os.getcwd(), debug=True)
    root = '/home/salvocos/tmp/test_sys_tools/'
    inTargz = '%sinput/inparanoid_salvo_mod.tar.gz'%(root)
    outDir = root + 'input/'
    #unarchive
    untar(inTargz, outDir=outDir, debug=debug)
