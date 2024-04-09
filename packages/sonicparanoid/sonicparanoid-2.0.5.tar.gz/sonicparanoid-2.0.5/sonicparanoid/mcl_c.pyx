# -*- coding: utf-8 -*-
"""Functions to create graph and matrixes from ortholog tables."""
from libc.stdio cimport FILE
from libc.stdlib cimport atoi, atof

cdef extern from "stdio.h":
    FILE *fopen(const char *, const char *)
    int fclose(FILE *)
    ssize_t getline(char **, size_t *, FILE *)


import sys
import os
from typing import Dict, Tuple, Deque, TextIO
import numpy as np
from shutil import copyfileobj
from subprocess import run
from collections import deque
# import Cython module for graph and matrixes creation
from sonicparanoid.graph_c import write_per_species_mcl_graph_parallel, compute_offsets


__module_name__ = "MCL"
__source__ = "mcl_c.pyx"
__author__ = "Salvatore Cosentino"
__license__ = "GPLv3"
__version__ = "0.4"
__maintainer__ = "Cosentino Salvatore"
__email__ = "salvo981@gmail.com"



""" FUNCTIONS """
def info():
    """Functions to create a graph from ortholog tables."""
    print(f"MODULE NAME:\t{__module_name__}")
    print(f"SOURCE FILE NAME:\t{__source__}")
    print(f"MODULE VERSION:\t{__version__}")
    print(f"LICENSE:\t{__license__}")
    print(f"AUTHOR:\t{__author__}")
    print(f"EMAIL:\t{__email__}")



def concatenate_files(fPaths: Deque[str], removeProcessed: bool = False, chunkSize: int = 10, debug: bool = False):
  """Concatenate a multiple files into a single one"""
  if debug:
    print("\nconcatenate_files :: START")
    print(f"Files to be concatenated (sequencially):\t{len(fPaths)}")
    print(f"Remove merged files: {removeProcessed}")
    print(f"Write chunks of {chunkSize} Megabytes")
  # concatenate to the first file
  f1: str = fPaths.popleft()
  f: str = ""
  cdef int qLen = len(fPaths)
  # open in append mode
  with open(f1,'ab') as wfd:
      # while there are file to concatenate
      while len(fPaths) > 0:
          qLen = len(fPaths)
          f = fPaths.popleft()
          if not os.path.isfile(f):
            sys.stderr.write(f"\nERROR: {f}\nis not a valid file.\n")
            sys.exit(-2)
          if debug:
            print(f"Concatenating: {os.path.basename(f)}\tremaining files: {qLen}")
          with open(f,'rb') as fd:
              copyfileobj(fd, wfd, 1024*1024*chunkSize)
              if removeProcessed:
                os.remove(f)



def run_mcl(mclGraph: str, outPath: str, mclBinPath: str, inflation: float = 1.5, threads: int = 4, removeInput: bool = False, debug: bool = False):
  """Perform MCL clustering."""
  if debug:
    print("\nrun_mcl :: START")
    print(f"Input MCL graph: {mclGraph}")
    print(f"Output file with clusters: {outPath}")
    print(f"MCL binaries: {mclBinPath}")
    print(f"Inflation rate:\t{inflation:.2f}")
    print(f"Threads:\t{threads}")
    print(f"Remove input graph file:\t{removeInput}")
    print(os.path.join(os.path.dirname(os.path.abspath(__file__)), "mcl_package/bin/mcl"))
  if not os.path.isfile(mclGraph):
    sys.stderr.write(f"\nERROR: the MCL input file {mclGraph}\nwas not found.\n")
    sys.exit(-2)

  # file for the MCL log
  mclLogStderr = os.path.join(os.path.dirname(outPath), "mcl.stderr.txt")
  mclLogStdout = os.path.join(os.path.dirname(outPath), "mcl.stdout.txt")
  # Run MCL
  # MCL run example
  # mcl mcl_graph_1-4_species_test.txt -o mcl_4sp_out.txt -I 1.5 -te 8 -V all
  ### USE SYSTEM INSTALLATION ###
  # from sh import mcl
  ###############################

  # create the log files
  fdout = open(mclLogStdout, "w")
  fderr = open(mclLogStderr, "w")
  mclCmd: str = f"{mclBinPath} {mclGraph} -o {outPath} -I {inflation} -te {threads} -V all"
  if debug:
    print(f"\nMCL CMD:\n{mclCmd}")
  # use run from Subprocess module
  run(mclCmd, shell=True, stdout=fdout, stderr=fderr)
  # close the log files
  fdout.close()
  fderr.close()

  # make sure the output file was created
  if not os.path.isfile(outPath):
    sys.stderr.write("\nERROR: the MCL output file was not created, something went wrong.\n")
    sys.exit(-5)

  # remove the input graph if required
  if removeInput:
    os.remove(mclGraph)



def remap_mcl_groups(mclGrps: str, outPath: str, runDir: str = os.getcwd(), writeFlat: bool = False, debug: bool = False):
  """Create SonicParanoid groups from raw MCL clusters."""
  if debug:
    print("\nremap_mcl_groups :: START")
    print(f"Input MCL clusters: {mclGrps}")
    print(f"Output groups file: {outPath}")
    print(f"Run directory: {runDir}")
    print(f"Write file with flat groups:\t{writeFlat}")
  if not os.path.isfile(mclGrps):
    sys.stderr.write(f"\nERROR: the MCL cluster file\n{mclGrps}\nwas not found.\n")
    sys.exit(-2)
  # load the offsets and protein counts
  protCntPcklPath: str = os.path.join(runDir, "protein_counts.pckl")
  # compute the offsets
  offsetDict = compute_offsets(protCntPcklPath, debug=debug)[0]
  # create arrays with offsets and species
  spArray = np.array(list(offsetDict.keys()), dtype=np.uint16)
  offsetArray = np.array(list(offsetDict.values()), dtype=np.uint32)
  # create the output cluster and write the header
  ofd: TextIO = open(outPath, "wt")
  # create file with "flat" groups
  flatFd = None
  if writeFlat:
    flatName: str = f"flat.{os.path.basename(outPath)}"
    flatFd = open(os.path.join(os.path.dirname(outPath), flatName), "wt")
    # write the header
    flatFd.write("group_id\t")
    flatFd.write("{:s}\n".format("\t".join([str(x) for x in spArray])))
  # Write the HDR
  ofd.write('group_id\tgroup_size\tsp_in_grp\tseed_ortholog_cnt\t%s\n'%('\t'.join(str(x) for x in spArray)))

  # create the file with not clustered proteins
  soiltaryOutPath = os.path.join(os.path.dirname(outPath), f"not_assigned_genes.{os.path.basename(outPath)}")
  ofdNotAssigned: TextIO = open(soiltaryOutPath, "wt")
  # dictionary to map offsets to species ids
  offset2spDict = {val:k for k, val in offsetDict.items()}
  # buffer string
  tmpStr: str = ""
  # keep track of the species with non clustered proteins
  # that are being processed
  solitaryPara: str = ""
  grpStr: str = ""
  cdef int notClusteredSpId = 0
  cdef int loopCnt = 0
  # species count
  cdef int totSp = len(spArray)
  # will contain the genes to be added to the output table
  tmpSonicGrpDict: Dict[int, Dict[str, None]]
  # will contain protein that could not be clustered and its species id
  tmpNotAssigendTpl: Tuple[int, str]
  # contains the size of sonicpara groups
  cdef int grpSize = 0
  # contains the number of species in a given group
  spInGrpDict: Dict[int, None] = {}
  # flag to control the processing
  cdef bint process = 0
  # Other temp variables
  cdef int cnt = 0
  cdef int clstrCnt = 0
  cdef int currentNotAssignedSpId, tmpSpId, tmpOffset
  # start reading the input clusters
  ifd = open(mclGrps, "rt")
  # skip the first 7 lines
  for i in range(7):
    ifd.readline()
  for dln in ifd:
    cnt += 1
    if len(dln) == 2:
      break # end of the cluster file
    dln = dln[:-1] # remove the newline
    #print(dln)
    # check if it a single cluster or a new one
    if dln[0] != " ":
      # remove the orthogroup id
      tmpStr += dln.split(" ", 1)[-1].lstrip(" ")
      if tmpStr[-1] == "$":
        tmpStr = tmpStr[:-2]
        # process = True
        process = 1
      else:
        # process = False
        process = 0
        continue
    else:
    #   tmpStr = "%s %s" % (tmpStr, dln.lstrip(" "))
      tmpStr = f"{tmpStr} {dln.lstrip(' ')}"
      # check if it is the end of the cluster
      if tmpStr[-1] == "$":
        tmpStr = tmpStr[:-2]
        # process the clusters
        process = 1
        # process = True
    # process the cluster if required
    if process:
      # put the string in buckets based on the offsets
      tmpArray = np.array([int(x) for x in tmpStr.split(" ")], dtype=np.uint32)
      grpSize = len(tmpArray)
      spInGrpDict.clear()
      # initialize the dictionary with empty dictionaries
      tmpSonicGrpDict = {x:{} for x in spArray}
      # iterate throught the array and find the species
      for x in tmpArray:
        # get the offset by finding the rightmost index with True
        offsetIdx = (x >= offsetArray).nonzero()[0][-1]
        tmpOffset = offsetArray[offsetIdx]
        tmpSpId = spArray[offsetIdx]
        if not tmpSpId in spInGrpDict:
          spInGrpDict[tmpSpId] = None
        # compute species ID
        tmpId: str = f"{tmpSpId}.{x - tmpOffset + 1}"
        if debug:
          print(f"\nsearching species for {x} in {tmpArray}")
          print("Offsets:", offsetArray)
          print("Species:", spArray)
          print(x >= offsetArray)
          print(f"offsetIdx={offsetIdx} found_offset={tmpOffset}")
          print(f"species_from_array:\t{tmpSpId}")
          print(f"mapping:\t{x} -> {tmpId}")

        if len(tmpArray) == 1:
          tmpNotAssigendTpl = (tmpSpId, tmpId)
        else:
          # add the id to the proper species dictionary
          if not tmpId in tmpSonicGrpDict[tmpSpId]:
            tmpSonicGrpDict[tmpSpId][tmpId] = None
          else:
            sys.exit("\nMultiple protein in groups!!!\nImpossible!")
      # process the MCL group and write it in the output
      clstrCnt += 1
      # reset the string
      tmpStr = ""
      process = 0
      #process = False
      # NOTE: for now we do not write scores...
      if grpSize > 1:
        ofd.write(f"{clstrCnt}\t{grpSize}\t{len(spInGrpDict)}\t{grpSize}\t")
        if writeFlat:
          flatFd.write(f"{clstrCnt}\t")

        # now write orthologs by species
        loopCnt = 0
        for spParalogs in tmpSonicGrpDict.values():
          loopCnt += 1
          if len(spParalogs) == 0:
            ofd.write("*")
            if writeFlat:
              flatFd.write("*")
          else:
            # ofd.write("{:s}\t1".format(",".join(spParalogs)))
            grpStr = ",".join(spParalogs)
            ofd.write(grpStr)
            # ofd.write(",".join(spParalogs))
            if writeFlat:
              # flatFd.write("{:s}".format(",".join(spParalogs)))
              # flatFd.write(','.join(spParalogs))
              flatFd.write(grpStr)
          # terminate the cluster line
          if loopCnt == totSp:
            ofd.write("\n")
            if writeFlat:
              flatFd.write("\n")
          else:
            ofd.write("\t")
            if writeFlat:
              flatFd.write("\t")
      else: # write the gene in the file with not clustered paralogs
        currentNotAssignedSpId, solitaryPara = tmpNotAssigendTpl
        if notClusteredSpId == 0:
          ofdNotAssigned.write(f"#{currentNotAssignedSpId}\n")
          notClusteredSpId = currentNotAssignedSpId
        elif notClusteredSpId != currentNotAssignedSpId:
          ofdNotAssigned.write(f"\n#{currentNotAssignedSpId}\n")
          notClusteredSpId = currentNotAssignedSpId
        # write the protein id
        ofdNotAssigned.write(f"{solitaryPara}\n")
  # close output files
  ofdNotAssigned.close()
  ofd.close()
  if writeFlat:
    flatFd.close()

  if debug:
    print(f"\n#Processed clusters lines:\t{cnt}")
    print(f"#Single clusters:\t{clstrCnt}")
  # sys.exit("DEBUG: mcl_c.pyx -> remap_mcl_groups")


# TO DO: implement the species skip properly
def write_mcl_matrix(spArray, spSkipArray, runDir: str = os.getcwd(), mtxDir: str = os.getcwd(), outDir: str = os.getcwd(), threads: int = 4, removeProcessed: bool = False, debug: bool = False):
  """Generate the input matrix for MCL."""
  if debug:
    print(f"\nwrite_mcl_matrix :: START")
    print(f"Species for which the MCL graph will created:\t{len(spArray)}")
    print(f"Species that will be skipped in the MCL graph creation:\t{len(spSkipArray)}")
    print(f"Run directory: {runDir}")
    print(f"Directory with ortholog matrixes: {mtxDir}")
    print(f"Output directory: {outDir}")
    print(f"Threads:{threads}")
    print(f"Remove merged subgraphs:\t{removeProcessed}")

  # check that the array with species is not empty
  if len(spArray) == 0:
    sys.stderr.write("ERROR: you must provide at least 3 species for which the graph must be created.")
    sys.exit(-6)
  # sys.exit("DEBUG@mcl_c.pyx -> write_mcl_matrix")

  # create the main output MCL graph
  mclGraphPath: str = os.path.join(outDir, "mcl_input_graph.txt")
  # compute offsets
  offsetDict, sizeDict = compute_offsets(os.path.join(runDir, "protein_counts.pckl"), debug=debug)
  mtxSize = sum(list(sizeDict.values()))

  ofd = open(mclGraphPath, "wt")
  # write the MCL graph header
  ofd.write(f"(mclheader\nmcltype matrix\ndimensions {mtxSize}x{mtxSize}\n)\n\n(mclmatrix\nbegin\n\n")
  ofd.close()
  # create the graph of each species
  subgraphsPaths = write_per_species_mcl_graph_parallel(spArray, runDir=runDir, mtxDir=mtxDir, outDir=outDir, threads=threads, debug=debug)
  # fill a deque with the keys
  subgraphsPaths = deque(subgraphsPaths.values(), maxlen=len(subgraphsPaths) + 1)
  # add the main matrix file to the left of the deque
  subgraphsPaths.appendleft(mclGraphPath)
  # now concatenate the subgraphs
  concatenate_files(subgraphsPaths, removeProcessed=removeProcessed, chunkSize=10, debug=debug)
  # close the MCL matrix file
  with open(mclGraphPath, "at") as ofd:
    ofd.write(")")
  # return the graph
  return mclGraphPath
