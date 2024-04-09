# -*- coding: utf-8 -*-
"""A setuptools based setup module.
See:
https://packaging.python.org/en/latest/distributing.html
https://github.com/pypa/sampleproject
"""

import sys
import os
# needed to compile quickparanoid during the installation
import platform
import subprocess
# Always prefer setuptools over distutils
from setuptools import setup
from setuptools.extension import Extension
from setuptools.command.install import install
# from distutils.version import LooseVersion
from pkg_resources import packaging
#from Cython.Build import cythonize
# from shutil import move, rmtree
import numpy


#from os import path
#here = path.abspath(path.dirname(__file__))

_CYTHON_INSTALLED = False
MIN_CYTHON_VER = "0.29.32"
try:
    import Cython
    CVER = Cython.__version__

    _CYTHON_INSTALLED = packaging.version.parse(CVER) >= packaging.version.parse(MIN_CYTHON_VER)
    # _CYTHON_INSTALLED = ver >= LooseVersion(MIN_CYTHON_VER)
except ImportError:
    _CYTHON_INSTALLED = False
    raise ImportError(f"\nERROR: SonicParanoid requires a version of Cython equal or higher than {MIN_CYTHON_VER}:\npip install cython\n")

# exit with an error if Cython is not installed
if not _CYTHON_INSTALLED:
    sys.stderr.write(f"\nERROR: SonicParanoid requires a version of Cython equal or higher than {MIN_CYTHON_VER}:\npip install cython\n")

# load cythonize if cython has been installed
if _CYTHON_INSTALLED:
    from Cython.Build import cythonize
    import Cython.Compiler.Options
    Cython.Compiler.Options.docstrings = True
    # Cython.Compiler.Options.annotate = True

# Force to use the default version of gcc and g++
if platform.system() == "Linux":
    os.environ["CC"] = "gcc"
    os.environ["CXX"] = "g++"


def makedir(path):
    """Create a directory including the intermediate directories in the path if not existing."""
    try:
        os.makedirs(path)
    except OSError:
        if not os.path.isdir(path):
            raise



def untar(tarpath, outDir=os.getcwd(), debug=True):
    """Untar source code."""
    import tarfile
    if debug:
        print(f"Tar.gz path:\t{tarpath:s}")
        print(f"Output dir:\t{outDir:s}")
    #check if the tar file is valid
    if not tarfile.is_tarfile(tarpath):
        sys.stderr.write(f"\nERROR: {tarpath:s} is not a valid tar.gz file.")
        sys.exit(-2)
    #create the output directory if does not exist yet
    if outDir[-1] != '/':
        outDir += '/'
    #create output directory
    makedir(outDir)
    #change current directory
    cwd = os.getcwd()
    if os.path.dirname(outDir) != cwd:
        os.chdir(outDir)
    #open the tar file
    tar = tarfile.open(tarpath)
    tar.extractall()
    tar.close()
    #set the current directory to the starting one
    os.chdir(cwd)
    if debug:
        print(f"Extracted in {outDir}")



extensions = [
    Extension(
        "sonicparanoid.inpyranoid_c",
        ["sonicparanoid/inpyranoid_c.pyx"],
    ),
    Extension(
        "sonicparanoid.mmseqs_parser_c",
        ["sonicparanoid/mmseqs_parser_c.pyx"],
    ),
    Extension(
        "sonicparanoid.remap_tables_c",
        ["sonicparanoid/remap_tables_c.pyx"],
    ),
    Extension(
        "sonicparanoid.graph_c",
        ["sonicparanoid/graph_c.pyx"], include_dirs=[numpy.get_include()],
    ),
    Extension(
        "sonicparanoid.essentials_c",
        ["sonicparanoid/essentials_c.pyx"],
    ),
    Extension(
        "sonicparanoid.mcl_c",
        ["sonicparanoid/mcl_c.pyx"],
    ),
    Extension(
        "sonicparanoid.archiver",
        ["sonicparanoid/archiver.pyx"],
    ),
    Extension(
        "sonicparanoid.ortho_merger",
        ["sonicparanoid/ortho_merger.pyx"], include_dirs=[numpy.get_include()],
    ),
    Extension(
        "sonicparanoid.profile_search",
        ["sonicparanoid/profile_search.pyx"], include_dirs=[numpy.get_include()],
    ),
    Extension(
        "sonicparanoid.domortho",
        ["sonicparanoid/domortho.pyx"], include_dirs=[numpy.get_include()],
    ),
    Extension(
        "sonicparanoid.d2v",
        ["sonicparanoid/d2v.pyx"], include_dirs=[numpy.get_include()],
    ),
]

# To use a consistent encoding
from codecs import open
from os import path
from os import chdir

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README_PYPI.md'), encoding='utf-8') as f:
    long_description = f.read()

# constant variables to be used inside the setup function
LICENSE = 'GNU GENERAL PUBLIC LICENSE, Version 3.0 (GPLv3)'



class QuickParaCompile(install):
    def run(self):
        try:
            # note cwd - this makes the current directory
            # the one with the Makefile.
            prevDir = here
            cmpDir = path.join(here, 'sonicparanoid/quick_multi_paranoid/')
            chdir(cmpDir)
            # clean the directory from installations
            sys.stdout.write('\n-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-')
            print('\nCompiling the program for multi-species orthology...')
            print('Cleaning any previous installation...')
            cleanCmd = 'make clean'
            process = subprocess.Popen(cleanCmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout_val, stderr_val = process.communicate() #get stdout and stderr
            process.wait()
            del stdout_val, stderr_val
            # compile the source
            compileCmd = 'make qa'
            process = subprocess.Popen(compileCmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout_val, stderr_val = process.communicate() #get stdout and stderr
            process.wait()
            # reset the current directory
            chdir(prevDir)
            sys.stdout.write('-#-#-#-#-#-#- DONE -#-#-#-#-#-#-')

            '''
            sys.stdout.write('\n\n-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-\n')
            # clean the directory from installations
            # Now lets compile MCL
            prevDir = here
            cmpDir = os.path.join(here, 'sonicparanoid/mcl_package/')
            chdir(cmpDir)
            # remove old binaries if required
            mclBinDir = os.path.join(cmpDir, 'bin/')
            print(mclBinDir)
            if os.path.isdir(mclBinDir):
                print("Wiping MCL bin directory")
                # remove all its content
                rmtree(mclBinDir)
                makedir(mclBinDir)

            print('\nBuilding MCL clustering algorithm...')
            # check if the archive has been already decompressed
            confPath = os.path.join(cmpDir, "configure")
            if os.path.isfile(confPath):
                print('Cleaning any previous installation...')
                # clean configuration
                cleanCmd = 'make distclean'
                process = subprocess.Popen(cleanCmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                stdout_val, stderr_val = process.communicate() #get stdout and stderr
                process.wait()
                # remove binaries
                cleanCmd = 'make clean'
                process = subprocess.Popen(cleanCmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                stdout_val, stderr_val = process.communicate() #get stdout and stderr
                process.wait()
            else: # extract the archive
                archPath = os.path.join(cmpDir, "mcl_src_slim.tar.gz")
                if not os.path.isfile(archPath):
                    sys.stderr.write("ERROR: the archive the MCL source code is missing\n{:s}\nPlease try to download SonicParanoid again.".format(archPath))
                    sys.exit(-2)
                else:
                    untar(archPath, cmpDir, debug=False)
            # configure MCL
            print("\nConfiguring the MCL installation...")
            compileCmd = './configure --prefix={:s}'.format(cmpDir)
            process = subprocess.Popen(compileCmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout_val, stderr_val = process.communicate() #get stdout and stderr
            process.wait()

            # binary paths
            mclBin = os.path.join(cmpDir, "bin/mcl")
            if os.path.isfile(mclBin):
                print("Removing old MCL binaries...")
                os.remove(mclBin)

            # compile MCL
            compileCmd = 'make install'
            print("Building MCL...")
            process = subprocess.Popen(compileCmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout_val, stderr_val = process.communicate() #get stdout and stderr
            process.wait()

            if not os.path.isfile(mclBin):
                sys.stderr.write("ERROR: the MCL binaries could not be build.\n")
                sys.exit(-2)

            # reset the current directory
            chdir(prevDir)
            sys.stdout.write('-#-#-#-#-#-#- MCL compilation done -#-#-#-#-#-#-')
            '''

        except Exception as e:
            print(e)
            print("ERROR: failed to compile the program for multi-species orthology.")
            exit(-5)
        else:
            install.run(self)



# Arguments marked as "Required" below must be included for upload to PyPI.
# Fields marked as "Optional" may be commented out.

setup(
    # There are some restrictions on what makes a valid project name
    # specification here:
    # https://packaging.python.org/specifications/core-metadata/#name
    name='sonicparanoid',  # Required
    # Versions should comply with PEP 440:
    # https://www.python.org/dev/peps/pep-0440/
    #
    # For a discussion on single-sourcing the version across setup.py and the
    # project code, see
    # https://packaging.python.org/en/latest/single_source_version.html
    version = "2.0.5", # Required
    # This is a one-line description or tagline of what your project does. This
    # corresponds to the "Summary" metadata field:
    # https://packaging.python.org/specifications/core-metadata/#summary
    description="SonicParanoid: fast, accurate, and comprehensive orthology inference with machine learning and language models",  # Required
    long_description=long_description,  # Optional
    long_description_content_type="text/markdown",
    url='http://iwasakilab.k.u-tokyo.ac.jp/sonicparanoid',  # Optional
    # This should be your name or the name of the organization which owns the project.
    author="Salvatore Cosentino",  # Optional
    # This should be a valid email address corresponding to the author listed above.
    author_email="salvo981@gmail.com",  # Optional
    # license
    license=LICENSE,
    # Classifiers help users find your project by categorizing it.
    #
    # For a list of valid classifiers, see
    # https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[  # Optional
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Science/Research',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: POSIX',
        'Operating System :: Unix',
        'Topic :: Scientific/Engineering',
        'Topic :: Scientific/Engineering :: Bio-Informatics',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10'
    ],
    # compile multi-species orthology source files
    # cmdclass={'install': QuickParaCompile,},
    # Note that this is a string of words separated by whitespace, not a list.
    keywords='bioinformatics machine-learning language-models orthology-inference phylogeny evolution orthology',  # Optional
    #package_dir={'': 'sonicparanoid'},
    package_dir={'sonicparanoid': 'sonicparanoid/'},
    packages = ['sonicparanoid',],
    # required python version
    python_requires=">=3.8, <3.11",
    include_package_data=True,
    package_data={"sonicparanoid": ["example/test_output/*", "example/test_input/*", "software_packages/*", "bin/README.md",
            "bin/guess_fast_pair.pckl",
            "pfam_files/Pfam-A.hmm.dat.gz",
            "pfam_files/pfama-mmseqs.tar.gz",
            "pfam_files/pfam_db.info.md",
            "README_PYPI.md",
            ]},  # Optional
    # required packages
    install_requires=[ "biopython>=1.79", "cython==3.0.0a10", "filetype>=1.2.0", "gensim>=4.2.0", "mypy>=0.991", "numpy>=1.21.6", "pandas>=1.3.5", "pip>=22.3.1", "psutil>=5.9.4", "scikit-learn<=1.2.2", "scipy<=1.12.0", "smart-open>=6.2.0", "setuptools>=65.5.1", "tqdm>=4.64.1", "wheel>=0.38.4"], # specify minimum version

    # external to be compiled
    ext_modules = cythonize(extensions, compiler_directives={"language_level": 3}),
    # For example, the following would provide a command called `sample` which
    # executes the function `main` from this package when invoked:
    entry_points={  # Optional
        "console_scripts": [
            "sonicparanoid = sonicparanoid.sonic_paranoid:main",
            "sonicparanoid-get-test-data = sonicparanoid.get_test_data:main",
            "sonicparanoid-extract = sonicparanoid.sonic_paranoid_extract:main",
            "sonic-debug-infer-ortho-table = sonicparanoid.sonic_infer_ortho_table:main",
        ],
    },

    # List additional URLs that are relevant to your project as a dict.
    #
    # This field corresponds to the "Project-URL" metadata fields:
    # https://packaging.python.org/specifications/core-metadata/#project-url-multiple-use
    #
    # Examples listed include a pattern for specifying where the package tracks
    # issues, where the source is hosted, where to say thanks to the package
    # maintainers, and where to support the project financially. The key is
    # what's used to render the link text on PyPI.
    project_urls={  # Optional
        'Source': 'https://gitlab.com/salvo981/sonicparanoid2',
    },
)
