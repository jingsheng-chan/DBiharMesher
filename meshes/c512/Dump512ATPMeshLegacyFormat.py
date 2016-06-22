# -*- coding: utf-8 -*-
"""
Write initial ATP Profile for an ECs Mesh in legacy VTK format as .vtk.
"""

import os
import sys

# Run in current directory.
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Relative import path for the DumpATPMeshToLegacyFormat script.
importPath = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../util'))
if not importPath in sys.path:
    sys.path.insert(1, importPath)
del importPath

import DumpATPMeshToLegacyFormat

# This is for the c512 mesh.
DumpATPMeshToLegacyFormat.numQuadsPerRing0 = 20
DumpATPMeshToLegacyFormat.taskMeshIn = "quadMeshFullc512.vtp"
DumpATPMeshToLegacyFormat.ecMeshIn = "quadMeshFullECc512.vtp"
DumpATPMeshToLegacyFormat.atpMeshIn = "quadMeshFullATPc512.vtp"

def main():
    DumpATPMeshToLegacyFormat.writeATPLegacyVTK()

if __name__ == '__main__':
    print "Starting", os.path.basename(__file__)
    main()
    print "Exiting", os.path.basename(__file__)
else:
    print __file__, "is to be run as main script."