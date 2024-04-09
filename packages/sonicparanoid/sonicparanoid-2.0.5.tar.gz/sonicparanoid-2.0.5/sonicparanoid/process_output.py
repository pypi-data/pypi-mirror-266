"""Functions to process the output from SonicParanoid."""
import os
import sys
from typing import Dict, List, Deque
from collections import deque
from Bio import SeqIO
#### IMPORT TO GENERATE PyPi package
from sonicparanoid import sys_tools as systools
####



__module_name__ = "Process output"
__source__ = "process_outpuy.py"
__author__ = "Salvatore Cosentino"
__license__ = "GPLv3"
__version__ = "0.7"
__maintainer__ = "Cosentino Salvatore"
__email__ = "salvo981@gmail.com"



### FUNCTIONS ####
def info() -> None:
    """This module contains functions for the detection of orthologs."""
    print(f"MODULE NAME:\t{__module_name__}")
    print(f"SOURCE FILE NAME:\t{__source__}")
    print(f"MODULE VERSION:\t{__version__}")
    print(f"LICENSE:\t{__license__}")
    print(f"AUTHOR:\t{__author__}")
    print(f"EMAIL:\t{__email__}")



def extract_fasta(clstrDict: Dict[str, Dict[str, List[str]]], fastaDir: str, outDir: str, multiFasta: bool = False, annotationDict: Dict[str, List[List[str]]] = {}, debug: bool = False) -> None:
    """Extract FASTA sequences for echa cluster."""
    if debug:
        print('\nextract_fasta :: START')
        print('Ortholog groups for which sequences will be extracted:\t{:d}'.format(len(clstrDict)))
        print('Directory with the original input FASTA files: {:s}'.format(fastaDir))
        print('Output directory: {:s}'.format(outDir))
        print('Output multiple FASTA files: {:s}'.format(str(multiFasta)))
        print('Length of annotation dictionary: {:d}'.format(len(annotationDict)))

    annotate: bool = False
    if len(annotationDict) > 0:
        annotate = True

    # check the directory with the fasta files exist
    if not os.path.isdir(fastaDir):
        sys.stderr.write('\nERROR (file not found): you must provide a valid path to the directory containig the species files.\n')
        sys.exit(-2)
    else: # make sure it is not empty
        tmpList: List[str] = os.listdir(fastaDir)
        if len(tmpList) < 2:
            sys.stderr.write('\nERROR: the directory containig the species files must contain at least two FASTA files.\n')
            sys.exit(-5)

    # will contain the species names that are actually required
    requSpDict: Dict[str, str] = {}

    # create the list with required species files
    for clstr, sp2geneDict in clstrDict.items():
        for sp, orthoList in sp2geneDict.items():
            # only process if required
            if sp in requSpDict:
                continue
            else:
                # make sure there is at least one ortholog for the current species
                if len(orthoList) == 1: # it could be empty
                    if orthoList[0][0] == '*': # then it is empty
                        continue
            # add the specis to the dictionary
            tmpPath: str = os.path.join(fastaDir, sp)
            requSpDict[sp] = tmpPath
            if not os.path.isfile(tmpPath):
                sys.stderr.write('\nERROR (file not found): the species file for {:s} was not found at\n{:s}\nplease provide a valid path.\n'.format(sp, tmpPath))
                sys.exit(-2)

    # load all the sequences in a dictionary
    # example, tvaginalis -> geneXAB -> ATGTAGGTA
    seqsDict: Dict[str, Dict[str, str]] = {}
    for spFile, fastaPath in requSpDict.items():
        spName: str = os.path.basename(spFile)
        seqsDict[spName] = load_seqs_in_dict(fastaPath=fastaPath, debug=debug)

    # queue to contain the paths of each single
    tmpDq: Deque[str]
    # now generate the output files
    # separated in directories separated by cluster id
    # and each file named clustersId-species_name
    for clstr, sp2geneDict in clstrDict.items():
        # create the output directory
        tmpClstrDir: str = os.path.join(outDir, 'group_{:s}/'.format(clstr))
        systools.makedir(tmpClstrDir)
        # now for each species extract the sequences
        if multiFasta: #write one fasta file for each species
            for sp, orthoList in sp2geneDict.items():
                # skip the creation of files if the cluster is empty
                if len(orthoList) == 1:
                    if orthoList[0][0] == '*':
                        continue
                tmpFastaName = 'group_{:s}-{:s}.faa'.format(clstr, sp)
                tmpOutPath = os.path.join(tmpClstrDir, tmpFastaName)
                ofd = open(tmpOutPath, 'w')
                # write the sequences
                for ortho in orthoList:
                    if annotate:
                        # create the header by merging the annotations
                        newHdr: str
                        if ortho in annotationDict: # sometimes no annotation is found!
                            annotLists = annotationDict[ortho]
                            newHdr = '|'.join([';'.join(l) for l in annotLists])
                            ofd.write('>{:s}\n'.format(newHdr))
                        else:
                            ofd.write('>{:s}\n'.format(ortho))
                    else:
                        ofd.write('>{:s}\n'.format(ortho))
                    # write the sequence
                    ofd.write('{:s}\n'.format(str(seqsDict[sp][ortho])))
                ofd.close()
        else: #write a single FASTA file
            tmpFastaName = "group_{:s}.faa".format(clstr)
            tmpOutPath = os.path.join(tmpClstrDir, tmpFastaName)
            ofd = open(tmpOutPath, 'w')
            for sp, orthoList in sp2geneDict.items():
                # skip the creation of files if the cluster is empty
                if len(orthoList) == 1:
                    if orthoList[0][0] == '*':
                        continue
                # write the sequences
                for ortho in orthoList:
                    if annotate:
                        # create the header by merging the annotations
                        newHdr: str
                        if ortho in annotationDict: # sometimes no annotation is found!
                            annotLists = annotationDict[ortho]
                            newHdr = '|'.join([';'.join(l) for l in annotLists])
                            ofd.write('>{:s}\n'.format(newHdr))
                        else:
                            ofd.write('>{:s}\n'.format(ortho))
                    else:
                        ofd.write('>{:s}\n'.format(ortho))
                    # write the sequence
                    ofd.write('{:s}\n'.format(str(seqsDict[sp][ortho])))
            ofd.close()



def extract_by_id(inTbl: str, idList: list[str] = [], outDir: str = os.getcwd(), minConf: float = 0.1, singleCopyOnly: bool = False, debug: bool = False) -> dict[str, dict[str, list[str]]]:
    """Extract clusters based on on the number of species of which they are composed."""
    if debug:
        print('\nextract_by_id :: START')
        print(f"Input groups table:\t{inTbl}")
        print(f"Number of clusters to be extracted:\t{len(idList):d}")
        print(f"IDs to be extracted:\t{idList}")
        print(f"Output directory: {outDir}")
        print(f"Minimum confidence for orthologs:\t{minConf:.2f}")
        print(f"Extract only single copy orthologs:\t{singleCopyOnly}")

    #check that the input directory is valid
    if not os.path.isfile(inTbl):
        sys.stderr.write('\nERROR (file not found): you must provide a valid path to the text file containig the ortholog groups table generated using SonicParanoid.\n')
        sys.exit(-2)
    # Check that ar least one id is in the list
    if len(idList) == 0:
        sys.stderr.write('\nERROR: you must provide at least one cluster ID to be extracted.\n')
        sys.exit(-5)

    # check that there are no repeated IDs in the ID list
    tmpDict: dict[str, None] = {}
    tmpList: list[str] = []
    for el in idList:
        if not el in tmpDict:
            tmpDict[el] = None
        else:
            tmpList.append(el)
    # remove the repeated IDs if required
    if len(tmpList) > 0:
        for el in tmpList:
            idList.remove(el)
        sys.stderr.write('\nWARNING: the following cluster IDs were repeated in the input ID list and were removed.')
        sys.stderr.write('\n{:s}'.format(str(tmpList)))
        sys.stderr.write('\nThe ID list now contains {:d} cluster IDs.\n\n'.format(len(idList)))
    # remove the tmp structure
    del tmpDict
    tmpList.clear()

    # start processing the ortholog groups
    fd = open(inTbl, 'r')
    # extract the header and check the validity of the input file
    hdr_columns: list[str] = fd.readline().rstrip('\n').split('\t')
    # print(hdr_columns)
    # check the hdr
    if not hdr_columns[0] == 'group_id':
        sys.stderr.write("\nERROR: {:s}\nis not a valid header.\n".format(hdr_columns[0]))
        sys.exit('Make sure that the ortholog groups file was generated using SonicParanoid.')
    # extract the species count
    spCntStr: str = str(len(hdr_columns[4:]))
    spCntStr = spCntStr.strip()
    # convert the string to int
    spCnt: int = int(spCntStr)
    # print(f"spCnt:\t{spCnt}")
    # extract the species list
    spList: list[str] = [] # will contain the species names
    for i, el in enumerate(hdr_columns[4:]):
        spList.append(el)

    # prepare the output file
    outPath: str = os.path.join(outDir, f"filtered_{os.path.basename(inTbl)}")
    # print(outPath)
    # create the output directory if required
    systools.makedir(outDir)
    ofd = open(outPath, 'w')
    # write the header
    ofd.write('{:s}\n'.format('\t'.join(hdr_columns)))

    # output dictionary and other variables
    # example: clst105 -> tvaginalis -> [g1, g4, g5]
    outDict: dict[str, dict[str, list[str]]] = {}
    clstrGenesDict: dict[str, list[str]] = dict()
    extractedClstrCnt: int = 0
    extractedGenesCnt: int = 0
    tmpExtractedGeneCnt: int = 0
    totCnt: int = 0
    tmpSp: str = ''
    flds: list[str] = []
    rejected: bool = False
    # start looping through the clusters
    for clstr in fd:
        flds = clstr.rstrip('\n').split('\t')
        totCnt += 1
        clstrId: str = flds[0]
        # extract the information from the cluster
        if clstrId in idList:
            # print(f"\nclstrId:\t{clstrId}")
            # keep only the usable fields
            flds = flds[4:]
            clstrGenesDict, tmpExtractedGeneCnt, rejected = extract_group(spOrthologs=flds, spList=spList, singleCopyOnly=singleCopyOnly, debug=debug)

            if not rejected:
                # write the filtered output file
                ofd.write(clstr)
                # add the id to output dictionary
                # outDict[clstrId] = {}
                outDict[clstrId] = clstrGenesDict
                # increase the count of extracted clusters
                extractedClstrCnt += tmpExtractedGeneCnt

            # remove the ID from the list
            idList.remove(clstrId)
            # sys.exit("DEBUG :: extract_by_id")

    fd.close()
    # close output file
    ofd.close()

    # print some debug line
    if debug:
        print('Extracted clusters:\t{:d}'.format(len(outDict)))
        if len(idList) > 0:
            print('(WARNING) The following clusters were not found: {:s}'.format(str(idList)))
        print('Extracted genes:\t{:d}'.format(extractedGenesCnt))
        print('Percentage of extracted clusters:\t{:.2f}'.format(round(float(extractedClstrCnt/totCnt) * 100., 2)))
    # for k, v in outDict.items():
    #     print(f"{k}\t{v}")
    # return the main dictionary
    return outDict



def extract_by_sp_cnt(inTbl: str, min: int = 2, max: int = 2, outDir: str = os.getcwd(), minConf: float = 0.1, singleCopyOnly: bool = False, debug: bool = False) -> dict[str, dict[str, list[str]]]:
    """Extract clusters based on on the number of species of which they are composed."""
    if debug:
        print('\nextract_by_sp_cnt :: START')
        print('Input groups table:\t{:s}'.format(inTbl))
        print('Minimum number of species in cluster:\t{:d}'.format(min))
        print('Maximum number of species in cluster:\t{:d}'.format(max))
        print('Output directory: {:s}'.format(outDir))
        print('Minimum confidence for orthologs:\t{:.2f}'.format(minConf))
        print(f"Extract only single copy orthologs:\t{singleCopyOnly}")
    #check that the input directory is valid
    if not os.path.isfile(inTbl):
        sys.stderr.write('\nERROR (file not found): you must provide a valid path to the text file containig the ortholog groups table generated using SonicParanoid.\n')
        sys.exit(-2)

    # check the minimum confidence value
    if not (0.05 <= minConf <= 1.):
        sys.stderr.write('\nWARNING: the ortholog confidence threshold must be set to a value between 0.05 and 1.0.\n')
        sys.stderr.write('It will now be set to 0.1.\n')
        min = max
    # start processing the ortholog groups
    fd = open(inTbl, 'r')
    # extract the head and check rthe validity of the input file
    hdr_columns: list[str] = fd.readline().rstrip('\n').split('\t')
    # check the hdr
    if not hdr_columns[0] == 'group_id':
        sys.stderr.write('\nERROR: {:s}\nis not a valid header.\n'.format(hdr_columns[0]))
        sys.exit('Make sure that the ortholog groups file was generated using SonicParanoid.')
    spCntStr: str = str(len(hdr_columns[4:]))
    spCntStr = spCntStr.strip()
    # check that the number of species is valid, for example not column was removed from the file
    # in thise case the diction must give a float with ending with '.0'
    # convert the string to int
    spCnt: int = int(spCntStr)
    # More species requested than those avaliable in the input clusters
    if min > spCnt:
        sys.stderr.write('\nWARNING: {:d} species were found in the input table header, hence clusters with {:d} species cannot exist!.\n'.format(spCnt, max))
        sys.stderr.write('Both minimum and maximum will be set to ({:d}).\n'.format(spCnt))
        min = spCnt
        max = spCnt
    # min should lower than max!
    if min > max:
        sys.stderr.write('\nWARNING: the minimum number of species ({:d}) is higher than the maximum number of species ({:d}).\n'.format(min, max))
        sys.stderr.write('Max will be set to the maximum number of species in the table ({:d}).\n'.format(spCnt))
        max = spCnt

    # extract the species list
    spList: list[str] = [] # will contain the species names
    for i, el in enumerate(hdr_columns[4:]):
        spList.append(el)
    print(spList)

    # prepare the output file
    outPath: str = os.path.join(outDir, 'filtered_min{:d}_max{:d}_{:s}'.format(min, max, os.path.basename(inTbl)))
    # create the output directory if required
    systools.makedir(outDir)
    ofd = open(outPath, 'w')
    # write the header
    ofd.write('{:s}\n'.format('\t'.join(hdr_columns)))

    # output dictionary
    # example: clst105 -> tvaginalis -> [g1, g4, g5]
    outDict: dict[str, dict[str, list[str]]] = {}
    extractedClstrCnt: int = 0
    extractedGenesCnt: int = 0
    tmpExtractedGeneCnt: int = 0
    totCnt: int = 0
    tmpSp: str = ''
    reject: bool = False
    # start looping through the clusters
    for clstr in fd:
        flds: List[str] = clstr.rstrip('\n').split('\t')
        totCnt += 1
        clstrId: str = flds[0]
        spSize: int = int(flds[2])
        # check if it contains all species
        if min <= spSize <= max:

            # print(f"\nclstrId:\t{clstrId}")
            # keep only the usable fields
            flds = flds[4:]
            clstrGenesDict, tmpExtractedGeneCnt, rejected = extract_group(spOrthologs=flds, spList=spList, singleCopyOnly=singleCopyOnly, debug=debug)

            if not rejected:
                # write the filtered output file
                ofd.write(clstr)
                # add the id to output dictionary
                # outDict[clstrId] = {}
                outDict[clstrId] = clstrGenesDict
                # increase the count of extracted clusters
                extractedClstrCnt += tmpExtractedGeneCnt
        # else:
        #     print(f"Skipping cluster {clstrId} as it involves only {spSize}")
    fd.close()
    # close output file
    ofd.close()
    # print some debug line
    if debug:
        print('Extracted clusters:\t{:d}'.format(len(outDict)))
        print('Extracted genes:\t{:d}'.format(extractedGenesCnt))
        print('Percentage of extracted clusters:\t{:.2f}'.format(round(float(extractedClstrCnt/totCnt) * 100., 2)))
    # return the main dictionary
    return outDict



def extract_group(spOrthologs: list[str], spList: list[str], singleCopyOnly: bool = False, debug: bool = False) -> tuple[dict[str, list[str]], int, bool]:
    """
    Process the orthologs for a single species in a ortholog group.
    Describe if it ia single copy or not (e.g. more than one orthologs for the species).
    The list has no elements if it contains "*"
    """
    if debug:
        print('\nextract_group :: START')
        print(f"Orthologs (cnt):\t{len(spOrthologs)}")
        print(f"Species (cnt):\t{len(spList)}")
        print(f"Extract only single copy orthologs:\t{singleCopyOnly}")

    # variables
    tmpSp: str = ""
    extractedGenesCnt: int = 0
    outDict: dict[str, list[str]] = dict()
    reject = False
    # print(spOrthologs)

    # Reject the cluster if is not single copy
    if singleCopyOnly:
        for genes in spOrthologs:
            # print(el)
            if "," in genes:
                reject = True
                break
        # ignore the cluster
        if reject:
            return (outDict, extractedGenesCnt, True)

    for i, genes in enumerate(spOrthologs):
        # extract the cluster
        # example of cluster
        # 2336_Q9X2I8,2336_Q9X172:0.159
        # create the list for the species
        tmpSp = spList[i]
        outDict[tmpSp] = []
        for ortho in genes.split(','):
            # print(ortho)
            outDict[tmpSp].append(ortho)
            # if tmpFlds[0][0] != '*':
            if ortho[0] != '*':
                extractedGenesCnt += 1
        # print(outDict[tmpSp])
        # print(outDict)
        # break

    # if debug:
    #     print(f"Extracted genes:\t{extractedGenesCnt}")

    # sys.exit("DEBUG :: extract_group")
    return (outDict, extractedGenesCnt, False)



def load_annotations(annotFile: str, geneIdCol: int = -1, annotCols: List[int] = [], debug: bool = False) -> Dict[str, List[List[str]]]:
    """Load annotations from annotation file"""
    if debug:
        print('\nload_annotations :: START')
        print('Column with gene ids:\t{:d}'.format(geneIdCol))
        print('Columns with annotations for the new header:\t{:s}'.format(str(annotCols)))
    # check the gene id and annotation column positions have been set
    if geneIdCol < 0:
        sys.stderr.write('\nERROR: the column index must be a positive integer.\n')
        sys.exit(-5)
    if len(annotCols) == 0:
        sys.stderr.write('\nERROR: you must provide at least one positive integer as position of the column with the annotation.\n')
        sys.exit(-5)

    # output dictionary
    outDict: Dict[str, List[List[str]]] = {}
    for ln in open(annotFile, 'r'):
        flds: List[str] = ln.rstrip('\n').split('\t')
        geneId = flds[geneIdCol]
        # extract
        annotListTmp: List[str] = [flds[pos] for pos in annotCols]
        # add the annotations in the dictionary
        if not geneId in outDict:
            outDict[geneId] = []
            for annot in annotListTmp:
                outDict[geneId].append([annot])
        else: # the sequence onctains multiple domains
            for idx, annot in enumerate(annotListTmp):
                #print(outDict[geneId])
                outDict[geneId][idx].append(annot)
                #print(outDict[geneId])
    return outDict



def load_seqs_in_dict(fastaPath: str, debug: bool = False) -> Dict[str, str]:
    """Load sequences for in a dictionary."""
    if debug:
        print('\nload_seqs_in_dict :: START')
        print('Proteome/Genome:\t{:s}'.format(fastaPath))
    # variables
    seqCnt: int = 0
    # write a pkl file with the lengths
    seqsDict: Dict[str, str] = {}
    # open sequence file
    for seq_record in SeqIO.parse(open(fastaPath), 'fasta'):
        seqsDict[seq_record.id] = seq_record.seq
        seqCnt += 1
    if debug:
        print('Loaded sequences for {:s}:\t{:d}'.format(os.path.basename(fastaPath), seqCnt))
    # return sequences
    return seqsDict



def process_multisp_tbl(inTbl: str, outPath: str, debug: bool = False) -> None:
    """Check consistency of table with ortholog groups and extract main stats."""
    if debug:
        print("process_multisp_tbl :: START")
        print(f"Input ortholog groups table:\t{inTbl}")
        print(f"Output stats file:\t{outPath}")
    #check that the input directory is valid
    if not os.path.isfile(inTbl):
        sys.stderr.write("\nERROR (file not found): you must provide a valid path to the text file containing the ortholog groups table generated using SonicParanoid.\n")
        sys.exit(-2)

    # create the directory that will contain the output file if required
    systools.makedir(os.path.dirname(outPath))

    # start processing the ortholog groups
    fd = open(inTbl, "rt")
    # extract the head and check rthe validity of the input file
    hdr_columns: list[str] = fd.readline().rstrip('\n').split('\t')
    # print(hdr_columns)
    # check the hdr
    if not hdr_columns[0] == "group_id":
        sys.stderr.write("\nERROR: the header is not valid.\n")
        sys.exit("Make sure that the ortholog groups file was generated using SonicParanoid.")
    spCntStr: str = str(len(hdr_columns[4:]))
    # print(f"spCntStr:\t{spCntStr}")
    # convert the string to int
    spCnt: int = int(spCntStr)
    # print(f"spCnt:\t{spCnt}")
    # variables to store the counts
    totCnt: int = 0
    allSpCnt: int = 0
    twoSpCnt: int = 0
    mostSeedsId: str = "1"
    maxSeedsCnt: int = 0
    flds: list[str] = []
    # start looping through the clusters
    for clstr in fd:
        flds = clstr.rstrip('\n').split('\t')
        totCnt += 1
        # print(flds)
        clstrId: str = flds[0]
        # print(f"clstrId:\t{clstrId}")
        # check if it contains all species
        if int(flds[2]) == spCnt:
            allSpCnt += 1
        elif int(flds[2]) == 2:
            twoSpCnt += 1
        # find the cluster with the high amount of orthologs with confidence 1.0
        seedsCnt = int(flds[3])
        if seedsCnt > maxSeedsCnt:
            maxSeedsCnt = seedsCnt
            mostSeedsId = clstrId
    fd.close()
    # variables with allSp pct
    allSpPct: float = round(float(allSpCnt/totCnt) * 100., 2)
    twoSpPct: float = round(float(twoSpCnt/totCnt) * 100., 2)

    # open the output file
    ofd = open(outPath, 'w')
    ofd.write(f"Stats for the ortholog groups file:\n{inTbl}\n")
    ofd.write(f"\nClusters:\t{totCnt:d}")
    ofd.write(f"\nSpecies:\t{spCnt:d}")
    ofd.write(f"\nClusters with all species:\t{allSpCnt:d}")
    ofd.write(f"\nPercentage of clusters with all species:\t{allSpPct:.2f}")
    ofd.write(f"\nClusters with two species:\t{twoSpCnt:d}")
    ofd.write(f"\nPercentage of clusters with two species:\t{twoSpPct:.2f}")
    ofd.write(f"\nCluster with highest number of main orthologs:\t{mostSeedsId}")
    ofd.close()