# A simple setup script to create an executable using PyQt4. This also
# demonstrates the method for creating a Windows executable that does not have
# an associated console.
#
# PyQt4app.py is a very simple type of PyQt4 application
#
# Run the build process by running the command 'python setup.py build'
#
# If everything works well you should find a subdirectory in the build
# subdirectory that contains the files needed to run the application

import sys

from cx_Freeze import setup, Executable

import mcl
import requests.certs

base = None
if sys.platform == "win32":
    base = "Win32GUI"

setup(
        name = mcl.NAME,
        version = mcl.VERSION,
        description = mcl.DESCRIPTION,
        options = {
            "build_exe": {
                "include_files": [
                    (requests.certs.where(), 'cacert.pem')
                ]
            }
        },
        executables = [
            Executable(
                "bin/mcl.py",
                base=base,
                icon='mcl/gui/icons/MCL.ico'
            )
        ],
)