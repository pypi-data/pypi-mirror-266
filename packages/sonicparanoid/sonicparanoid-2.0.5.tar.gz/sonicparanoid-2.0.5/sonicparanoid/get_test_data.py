# -*- coding: utf-8 -*-
"""Execute the SonicParanoid."""
# NOTE: remove when the lowest python version will be 3.9
from __future__ import annotations
import os
import sys
import shutil
from sonicparanoid import sys_tools as systools

########### FUNCTIONS ############
def get_params():
    """Parse and analyse command line parameters."""
    # create the possible values for sensitivity value
    # define the parameter list
    import argparse
    usage = "\nProvide the path to the directory in which the test data for SonicParanoid will be stored.\n"
    parser = argparse.ArgumentParser(description="Create a test directory with test input proteomes for SonicParanoid",  usage="%(prog)s -o <OUTPUT_DIRECTORY>[options]", prog="sonicparanoid-get-test-data")
    #start adding the command line options
    parser.add_argument("-o", "--output-directory", type=str, required=True, help="The directory in which the test data will be stored.", default=None)
    parser.add_argument("-d", "--debug", required=False, help="Output debug information.", default=False, action="store_true")
    args = parser.parse_args()
    return (args, parser)



def copytree(src, dst, symlinks=False, ignore=None) -> None:
    for item in os.listdir(src):
        s: str = os.path.join(src, item)
        d: str = os.path.join(dst, item)
        if os.path.isdir(s):
            shutil.copytree(s, d, symlinks, ignore)
        else:
            shutil.copy2(s, d)



########### MAIN ############

def main():

    # check that everything has been installed correctly
    root: str = os.path.dirname(os.path.abspath(__file__))

    #Get the parameters
    args = get_params()[0]
    #set the required variables
    # debug: bool = args.debug
    # output dir
    outDir: str = f"{os.path.realpath(args.output_directory)}/sonicparanoid_test/"

    # path to the source package
    testSrcDir: str = os.path.join(root, "example")

    # skip the extration if the directory already exists
    if os.path.isdir(outDir):
        print(f"WARNING: the directory\n{outDir}")
        print("already exists, if you want to extract the package,")
        print("please remove the above-mentioned directory.")
        print("\nEXIT: no file copied.")
        sys.exit(-2)
    # create the directory if it does not exist
    systools.makedir(outDir)

    # copy the test files
    print(outDir)
    copytree(testSrcDir, outDir, symlinks=False, ignore=None)
    #copytree(testSrcDir, outDir)
    if os.path.isdir(outDir):
        print(f"INFO: all test files were succesfully copied to\n{outDir:s}\n")
    # suggest the command to run
    print(f"Go inside the directory\n{outDir:s}\nand type\n")
    print("sonicparanoid -i ./test_input -o ./test_output --project-id my_first_run -t 4")
