# -*- coding: utf-8 -*-
"""
Created on Tue Mar 31 17:09:57 2015

This script converts output from WrapDbihar code to be suitabl for the
legacy Coupled Cells code.

The code reorders cells and produces the required files in TXT format.
VTK files are written out for visual verification.
"""

import os
import vtk

numQuadsPerRing0 = 12
numECsPerCol = 4
numSMCsPerRow = 4

meshSet0 = [
"quadMeshFullc216.vtp",
"quadMeshFullECc216.vtp",
"quadMeshFullSMCc216.vtp"
]

numECsPerRow = numSMCsPerRow * 5
numSMCsPerCol = numECsPerCol * 13

numECsPerQuad = numECsPerRow * numECsPerCol
numSMCsPerQuad = numSMCsPerCol * numSMCsPerRow

# VTK files to write.
taskVTKFiles = [
"vtk/parent.vtp",
"vtk/left_daughter.vtp",
"vtk/right_daughter.vtp",
]

ecCentroidVTKFiles = [
"vtk/ec_centeroid_parent.vtp",
"vtk/ec_centeroid_left_daughter.vtp",
"vtk/ec_centeroid_right_daughter.vtp",
]

ecVTKFiles = [
"vtk/ec_mesh_parent.vtp",
"vtk/ec_mesh_left_daughter.vtp",
"vtk/ec_mesh_right_daughter.vtp",
]

smcVTKFiles = [
"vtk/smc_mesh_parent.vtp",
"vtk/smc_mesh_left_daughter.vtp",
"vtk/smc_mesh_right_daughter.vtp"
]

taskTXTFiles = [
"txt/parent_points.txt",
"txt/parent_cells.txt",
"txt/left_daughter_points.txt",
"txt/left_daughter_cells.txt",
"txt/right_daughter_points.txt",
"txt/right_daughter_cells.txt"
]

ecCentroidTXTFiles = [
"txt/parent_ec_centeroid_points.txt",
"txt/parent_ec_centeroid_cells.txt",
"txt/left_daughter_ec_centeroid_points.txt",
"txt/left_daughter_ec_centeroid_cells.txt",
"txt/right_daughter_ec_centeroid_points.txt",
"txt/right_daughter_ec_centeroid_cells.txt"
]

ecTXTFiles = [
"txt/parent_ec_mesh_points.txt",
"txt/parent_ec_mesh_cells.txt",
"txt/left_daughter_ec_mesh_points.txt",
"txt/left_daughter_ec_mesh_cells.txt",
"txt/right_daughter_ec_mesh_points.txt",
"txt/right_daughter_ec_mesh_cells.txt"
]

smcTXTFiles = [
"txt/parent_smc_mesh_points.txt",
"txt/parent_smc_mesh_cells.txt",
"txt/left_daughter_smc_mesh_points.txt",
"txt/left_daughter_smc_mesh_cells.txt",
"txt/right_daughter_smc_mesh_points.txt",
"txt/right_daughter_smc_mesh_cells.txt"
]

def main():
    # This is where the data is for testing purposes.
    os.chdir("/home/cza14/BlueFern/LocalData/c216")
    print "Current working directory:", os.getcwd()    

    # Working with the task mesh.
    # Working with the task mesh.
    # Working with the task mesh.
    taskMeshReader = vtk.vtkXMLPolyDataReader()
    taskMeshReader.SetFileName(meshSet0[0])
    taskMeshReader.Update()

    taskMesh = taskMeshReader.GetOutput()

    # Get the range of branch labels.
    labelRange = [0, 0]
    taskMesh.GetCellData().GetScalars().GetRange(labelRange, 0)

    # Convert label range to a list of labels.
    labelRange = range(int(labelRange[0]), int(labelRange[1]) + 1)    
    print "Labels found in task mesh:", labelRange

    # Prepare the stupid TXT files for output.
    parentPointsFile = open(taskTXTFiles[0], 'w')
    parentCellsFile = open(taskTXTFiles[1], 'w')

    leftPointsFile = open(taskTXTFiles[2], 'w')
    leftCellsFile = open(taskTXTFiles[3], 'w')

    rightPointsFile = open(taskTXTFiles[4], 'w')
    rightCellsFile = open(taskTXTFiles[5], 'w')

    # Store the number of rings for each label. 
    numRingsPerLabel = {}   

    # For every label in the range of labels we want to extract all cells/quads.
    for label in labelRange:
        # Use this filter to extract the cells for a given label value.
        branchSelector = vtk.vtkThreshold()
        branchSelector.SetInput(taskMesh)
        branchSelector.ThresholdBetween(label,label);
        branchSelector.Update()

        taskMeshBranch = branchSelector.GetOutput()

        print "There are", taskMeshBranch.GetNumberOfCells(), \
        "cells for label", label, "..."

        # Create new vtkPolyData object for the new reordered mesh.
        reorderedTaskMeshBranch = vtk.vtkPolyData()
        # Use the old points.
        reorderedTaskMeshBranch.SetPoints(taskMeshBranch.GetPoints())

        # New vtkCellArray for storing reordeced cells.
        reorderedCellArray = vtk.vtkCellArray()
        numQuadRowsPerBranch = taskMeshBranch.GetNumberOfCells() / numQuadsPerRing0;
        numRingsPerLabel[label] = numQuadRowsPerBranch
        ringIds = range(0, numQuadRowsPerBranch);
        ringIds.reverse()

        # Decide which TXT files to write to.
        pointsOf = ''
        cellsOf = ''
        if label == 0:
            pointsOf = parentPointsFile
            cellsOf = parentCellsFile
        elif label == 1:
            pointsOf = leftPointsFile
            cellsOf = leftCellsFile
        elif label == 2:
            pointsOf = rightPointsFile
            cellsOf = rightCellsFile

        print "Writing TXT files for task mesh:"
        print pointsOf
        print cellsOf

        # Iterate over the rings in reverse order.
        for ringNum in ringIds:
            # Iterate over the cells in normal order.
            for cellNum in range(0, numQuadsPerRing0):
                # Calculate the 'real' cell id and get the corresponding cell.
                cellId = ringNum * numQuadsPerRing0 + cellNum
                cell = taskMeshBranch.GetCell(cellId)
                reorderedCellArray.InsertNextCell(cell)

                # The ids to be written to the TXT file.
                pointIdList = [cell.GetNumberOfPoints()]
                for pPos in range(0, cell.GetNumberOfPoints()):
                    pointIdList.append(cell.GetPointId(pPos))

                # Write the ids to the TXT file.
                pointIdListStr = ' '.join(str(i) for i in pointIdList)
                cellsOf.write(pointIdListStr + '\n')

                # Write the appropriate points to TXT file.
                for pPos in range(0, cell.GetNumberOfPoints()):
                    writePoint = False
                    if ringNum == ringIds[0]:
                        if cellNum == 0:
                            writePoint = True
                        elif pPos == 1 or pPos == 2:
                            writePoint = True
                    else:
                        if cellNum == 0:
                            if pPos == 0 or pPos == 1:
                                writePoint = True
                        else:
                            if pPos == 1:
                                writePoint = True
                    if writePoint == True:
                        # print pPos,
                        point = taskMeshBranch.GetPoint(cell.GetPointId(pPos))
                        pointStr = ' '.join(format(i , '.6f') for i in point)
                        pointsOf.write(pointStr + '\n')
        # print '\n'

        # Put the reordered cells into the reordered mesh.
        reorderedTaskMeshBranch.SetPolys(reorderedCellArray)

        # Write the VTK file.
        reorderedMeshWriter = vtk.vtkXMLPolyDataWriter()
        reorderedMeshWriter.SetInput(reorderedTaskMeshBranch)
        reorderedMeshWriter.SetFileName(taskVTKFiles[label])
        reorderedMeshWriter.Update()

    parentPointsFile.close()
    parentCellsFile.close()

    leftPointsFile.close()
    leftCellsFile.close()

    rightPointsFile.close()
    rightCellsFile.close()

    print "Rings per label:", numRingsPerLabel, "..."
    ringsPerLabelVals = numRingsPerLabel.values()    
    
    # Check all rings per label values are the same.
    if ringsPerLabelVals[1:] != ringsPerLabelVals[:-1]:
        print "ERROR: All values of rings per label must be identical ..."
    else:
        print "OK: All values of rings per label are identical ..."

    # Working with EC mesh.
    # Working with EC mesh.
    # Working with EC mesh.
    ecMeshReader = vtk.vtkXMLPolyDataReader()
    ecMeshReader.SetFileName(meshSet0[1])
    ecMeshReader.Update()

    # Original ECs mesh to work with.
    ecMesh = ecMeshReader.GetOutput()
    print "There are", ecMesh.GetNumberOfCells(), "ECs in total ..."

    # Prepare the stupid TXT files for output.    
    parentPointsFile = open(ecTXTFiles[0], 'w')
    parentCellsFile = open(ecTXTFiles[1], 'w')
    parentCentroidPointsFile = open(ecCentroidTXTFiles[0], 'w')
    parentCentroidCellsFile = open(ecCentroidTXTFiles[1], 'w')

    leftPointsFile = open(ecTXTFiles[2], 'w')
    leftCellsFile = open(ecTXTFiles[3], 'w')
    leftCentroidPointsFile = open(ecCentroidTXTFiles[2], 'w')
    leftCentroidCellsFile = open(ecCentroidTXTFiles[3], 'w')

    rightPointsFile = open(ecTXTFiles[4], 'w')
    rightCellsFile = open(ecTXTFiles[5], 'w')
    rightCentroidPointsFile = open(ecCentroidTXTFiles[4], 'w')
    rightCentroidCellsFile = open(ecCentroidTXTFiles[5], 'w')

    # For every label in the range of labels we want to extract all ECs.
    for label in labelRange:
        # Can not use vtkThreshold filter to extract the cells because they are not labelled.

        # Ring ids list for traversal.
        ringIds = range(0, numRingsPerLabel[label])
        ringIds.reverse()

        # Number of ECs rows is the number of ECs per quad.
        rowIds = range(0, numECsPerCol)
        rowIds.reverse()

        # The ECs are organised in rings of blocks of cells.
        # New vtkCellArray for storing reordeced cells.
        reorderedCellArray = vtk.vtkCellArray()

        # Create new vtkPolyData object for the new reordered mesh.
        reorderedECMeshBranch = vtk.vtkPolyData()
        # Use the old points.
        # We are cheating here, because we are using all points,
        # but only the ones participating in reordered cells will show
        # and only they will be written out to the stupid TXT files.
        reorderedECMeshBranch.SetPoints(ecMesh.GetPoints())

        # Extracting the cells on the basis of the index.
        # We only want cells that correspond to the quads withthe given label
        # in the task mesh.

        # Keep track of how many branches we need to skip.
        ecCellOffset = label * numQuadsPerRing0 * numRingsPerLabel[label] * \
        numECsPerQuad

        print "ecCellOffset", ecCellOffset

        # Iterate over the rings in reverse order.
        for ringNum in ringIds:
            # Iterate over the 'imaginary' quads of cells in normal order.
            for quadNum in range(0, numQuadsPerRing0):
                # Iterate over the rows of cells in reverse order.
                # Calculate the 'real' id for the 'imaginary' quad.
                quadId = ringNum * numQuadsPerRing0 + quadNum
                # Iterate over rows of cells in reverse order.
                for rowNum in rowIds:
                    # Iterate over the rows of cells in normal order.
                    for ecNum in range(0, numECsPerRow):
                        # Calculate the 'real' ec cell id and get the corresponding cell.
                        ecId = quadId * numECsPerQuad + rowNum * numECsPerRow + ecNum
                        ecId = ecCellOffset + ecId
                        ecCell = ecMesh.GetCell(ecId)
                        reorderedCellArray.InsertNextCell(ecCell)

        # Set the reordered cells to the reordered ECs mesh.
        reorderedECMeshBranch.SetPolys(reorderedCellArray)

        print "There are", reorderedECMeshBranch.GetNumberOfCells(), \
        "ECs for label", label, "..."

        # Decide which TXT files to write to.
        pointsOf = ''
        cellsOf = ''
        centPointsOf = ''
        centCellsOf = ''

        if label == 0:
            pointsOf = parentPointsFile
            cellsOf = parentCellsFile
            centPointsOf = parentCentroidPointsFile
            centCellsOf = parentCentroidCellsFile
        elif label == 1:
            pointsOf = leftPointsFile
            cellsOf = leftCellsFile
            centPointsOf = leftCentroidPointsFile
            centCellsOf = leftCentroidCellsFile
        elif label == 2:
            pointsOf = rightPointsFile
            cellsOf = rightCellsFile
            centPointsOf = rightCentroidPointsFile
            centCellsOf = rightCentroidCellsFile

        print "Writing TXT files for ECs:"
        print pointsOf
        print cellsOf
        print centPointsOf
        print centCellsOf

        # Iterate over quads in normal order because they have been reordered.
        for quadNum in range(0, numRingsPerLabel[label] * numQuadsPerRing0):
            # Iterate over rows in normal order because they have been reordered.
            for rowNum in range(0, numECsPerCol):
                # Iterate over the ECs in the row in normal order.
                for ecNum in range(0, numECsPerRow):
                    # Calculate the 'real' ec cell id and get the corresponding cell.
                    ecId = quadNum * numECsPerQuad + rowNum * numECsPerRow + ecNum
                    ecCell = reorderedECMeshBranch.GetCell(ecId)

                    # The ids to be written to the TXT file.
                    pointIdList = [ecCell.GetNumberOfPoints()]
                    for pPos in range(0, ecCell.GetNumberOfPoints()):
                        pointIdList.append(ecCell.GetPointId(pPos))

                    # Write the ids to the TXT file.
                    pointIdListStr = ' '.join(str(i) for i in pointIdList)
                    cellsOf.write(pointIdListStr + '\n')

                    # Write the appropriate points to the TXT file.
                    for pPos in range(0, ecCell.GetNumberOfPoints()):
                        writePoint = False
                        if rowNum == 0:
                            if ecNum == 0:
                                writePoint = True
                            elif pPos == 1 or pPos == 2:
                                writePoint = True
                        else:
                            if ecNum == 0:
                                if pPos == 0 or pPos == 1:
                                    writePoint = True
                            else:
                                if pPos == 1:
                                    writePoint = True
                        if writePoint == True:
                            # print pPos,
                            point = reorderedECMeshBranch.GetPoint(ecCell.GetPointId(pPos))
                            pointStr = ' '.join(format(i , '.6f') for i in point)
                            pointsOf.write(pointStr + '\n')
            # print '\n'

        # Write the VTK EC mesh file.
        reorderedMeshWriter = vtk.vtkXMLPolyDataWriter()
        reorderedMeshWriter.SetInput(reorderedECMeshBranch)
        reorderedMeshWriter.SetFileName(ecVTKFiles[label])
        reorderedMeshWriter.Update()

        # Use VTK centroid filter to get the centroids in the right order
        # from the reorderedECMeshBranch.
        centroidFilter = vtk.vtkCellCenters()
        centroidFilter.SetInput(reorderedECMeshBranch)
        centroidFilter.Update()

        # Create a vertex for each point.
        pointsToVerticesFilter = vtk.vtkVertexGlyphFilter()
        pointsToVerticesFilter.SetInput(centroidFilter.GetOutput())
        pointsToVerticesFilter.Update()

        reorderedCentroidBranch = pointsToVerticesFilter.GetOutput()

        # Write the VTK EC centrouid file.
        centroidWriter = vtk.vtkXMLPolyDataWriter()
        centroidWriter.SetInput(reorderedCentroidBranch)
        centroidWriter.SetFileName(ecCentroidVTKFiles[label])
        centroidWriter.Update()

        # Write the centroids to the TXT points and cells files.
        for cId in range(0, reorderedCentroidBranch.GetNumberOfCells()):
            centCell = reorderedCentroidBranch.GetCell(cId)
            centIds = [centCell.GetNumberOfPoints()]

            # Write centroid ids.            
            ptId = centCell.GetPointId(0)
            centIds.append(ptId)
            centIdsStr = ' '.join(str(i) for i in centIds)
            centCellsOf.write(centIdsStr + '\n')

            # Write centroid points.
            point = reorderedCentroidBranch.GetPoint(ptId)
            pointStr = ' '.join(format(i , '.6f') for i in point)
            centPointsOf.write(pointStr + '\n')

    parentPointsFile.close()
    parentCellsFile.close()
    parentCentroidPointsFile.close()
    parentCentroidCellsFile.close()

    leftPointsFile.close()
    leftCellsFile.close()
    leftCentroidPointsFile.close()
    leftCentroidCellsFile.close()

    rightPointsFile.close()
    rightCellsFile.close()    
    rightCentroidPointsFile.close()
    rightCentroidCellsFile.close()

    # Working with SMC mesh.
    # Working with SMC mesh.
    # Working with SMC mesh.
    smcMeshReader = vtk.vtkXMLPolyDataReader()
    smcMeshReader.SetFileName(meshSet0[2])
    smcMeshReader.Update()

    # Original SMCs mesh to work with.
    smcMesh = smcMeshReader.GetOutput()
    print "There are", smcMesh.GetNumberOfCells(), "SMCs in total ..."

    # Prepare the stupid TXT files for output.    
    parentPointsFile = open(smcTXTFiles[0], 'w')
    parentCellsFile = open(smcTXTFiles[1], 'w')
    
    leftPointsFile = open(smcTXTFiles[2], 'w')
    leftCellsFile = open(smcTXTFiles[3], 'w')

    rightPointsFile = open(smcTXTFiles[4], 'w')
    rightCellsFile = open(smcTXTFiles[5], 'w')

    # For every label in the range of labels we want to extract all SMCs.
    for label in labelRange:
        # Can not use vtkThreshold filter to extract the cells because they are not labelled.

        # Ring ids list for traversal.
        ringIds = range(0, numRingsPerLabel[label])
        ringIds.reverse()

        # Number of SMCs rows is the number of ECs per quad times 13.
        rowIds = range(0, numSMCsPerCol)
        rowIds.reverse()

        # The SMCs are organised in rings of blocks of cells.
        # New vtkCellArray for storing reordeced cells.
        reorderedCellArray = vtk.vtkCellArray()

        # Create new vtkPolyData object for the new reordered mesh.
        reorderedSMCMeshBranch = vtk.vtkPolyData()
        # Use the old points.
        # We are cheating here, because we are using all points,
        # but only the ones participating in reordered cells will show
        # and only they will be written out to the stupid TXT files.
        reorderedSMCMeshBranch.SetPoints(smcMesh.GetPoints())

        # Extracting the cells on the basis of the index.
        # We only want cells that correspond to the quads withthe given label
        # in the task mesh.

        # Keep track of how many branches we need to skip.
        smcCellOffset = label * numQuadsPerRing0 * numRingsPerLabel[label] * \
        numSMCsPerQuad

        print "smcCellOffset", smcCellOffset

        # Iterate over the rings in reverse order.
        for ringNum in ringIds:
            # Iterate over the 'imaginary' quads of cells in normal order.
            for quadNum in range(0, numQuadsPerRing0):
                # Iterate over the rows of cells in reverse order.
                # Calculate the 'real' id for the 'imaginary' quad.
                quadId = ringNum * numQuadsPerRing0 + quadNum
                # Iterate over rows of cells in reverse order.
                for rowNum in rowIds:
                    # Iterate over the rows of cells in normal order.
                    for smcNum in range(0, numSMCsPerRow):
                        # Calculate the 'real' smc cell id and get the corresponding cell.
                        smcId = quadId * numSMCsPerQuad + rowNum * numSMCsPerRow + smcNum
                        smcId = smcCellOffset + smcId
                        smcCell = smcMesh.GetCell(smcId)
                        reorderedCellArray.InsertNextCell(smcCell)

        # Set the reordered cells to the reordered SMCs mesh.
        reorderedSMCMeshBranch.SetPolys(reorderedCellArray)

        print "There are", reorderedSMCMeshBranch.GetNumberOfCells(), \
        "SMCs for label", label, "..."

        # Decide which TXT files to write to.
        pointsOf = ''
        cellsOf = ''
        centPointsOf = ''
        centCellsOf = ''

        if label == 0:
            pointsOf = parentPointsFile
            cellsOf = parentCellsFile
        elif label == 1:
            pointsOf = leftPointsFile
            cellsOf = leftCellsFile
        elif label == 2:
            pointsOf = rightPointsFile
            cellsOf = rightCellsFile

        print "Writing TXT files for SMCs:"
        print pointsOf
        print cellsOf

        # Iterate over quads in normal order because they have been reordered.
        for quadNum in range(0, numRingsPerLabel[label] * numQuadsPerRing0):
            # Iterate over rows in normal order because they have been reordered.
            for rowNum in range(0, numSMCsPerCol):
                # Iterate over the SMCs in the row in normal order.
                for smcNum in range(0, numSMCsPerRow):
                    # Calculate the 'real' smc cell id and get the corresponding cell.
                    smcId = quadNum * numSMCsPerQuad + rowNum * numSMCsPerRow + smcNum
                    smcCell = reorderedSMCMeshBranch.GetCell(smcId)

                    # The ids to be written to the TXT file.
                    pointIdList = [smcCell.GetNumberOfPoints()]
                    for pPos in range(0, smcCell.GetNumberOfPoints()):
                        pointIdList.append(smcCell.GetPointId(pPos))
                    
                    # Write the ids to the TXT file.
                    pointIdListStr = ' '.join(str(i) for i in pointIdList)
                    cellsOf.write(pointIdListStr + '\n')

                    # Write the appropriate points to the TXT file.
                    for pPos in range(0, smcCell.GetNumberOfPoints()):
                        writePoint = False
                        if rowNum == 0:
                            if smcNum == 0:
                                writePoint = True
                            elif pPos == 1 or pPos == 2:
                                writePoint = True
                        else:
                            if smcNum == 0:
                                if pPos == 0 or pPos == 1:
                                    writePoint = True
                            else:
                                if pPos == 1:
                                    writePoint = True
                        if writePoint == True:
                            # print pPos,
                            point = reorderedSMCMeshBranch.GetPoint(smcCell.GetPointId(pPos))
                            pointStr = ' '.join(format(i , '.6f') for i in point)
                            pointsOf.write(pointStr + '\n')
            # print '\n'

        # Write the VTK SMC mesh file.
        reorderedMeshWriter = vtk.vtkXMLPolyDataWriter()
        reorderedMeshWriter.SetInput(reorderedSMCMeshBranch)
        reorderedMeshWriter.SetFileName(smcVTKFiles[label])
        reorderedMeshWriter.Update()
        
    parentPointsFile.close()
    parentCellsFile.close()
    
    leftPointsFile.close()
    leftCellsFile.close()
    
    rightPointsFile.close()
    rightCellsFile.close()

    print "All done ..."
    print "... Except the last configuration_info.txt file ..."

    configFile = open("txt/configuration_info.txt", 'w')
    configFile.write("Processors information\n")
    configFile.write("Total number of points per branch (vtk points) = %d\t\tm = %d n = %d\n" \
    % ((numQuadsPerRing0 + 1) * (numRingsPerLabel[0] + 1), (numQuadsPerRing0 + 1), (numRingsPerLabel[0] + 1)))
    configFile.write("Total number of cells per branch (vtk cells) = %d\t\tm = %d n = %d\n" \
    % (numQuadsPerRing0 * numRingsPerLabel[0], numQuadsPerRing0, numRingsPerLabel[0]))
    configFile.write("Total number of SMC mesh points per processor mesh (vtk points) = %d\t\tm = %d n = %d\n" \
    % ((numSMCsPerCol + 1) * (numSMCsPerRow + 1), (numSMCsPerCol + 1), (numSMCsPerRow + 1)))
    configFile.write("Total number of SMC mesh cells per processor mesh (vtk cells) = %d\t\tm = %d n = %d\n" \
    % (numSMCsPerCol * numSMCsPerRow, numSMCsPerCol, numSMCsPerRow))
    configFile.write("Total number of EC mesh points per processor mesh (vtk points) = %d\t\tm = %d n = %d\n" \
    % ((numECsPerCol + 1) * (numECsPerRow + 1), (numECsPerCol + 1), (numECsPerRow + 1)))
    configFile.write("Total number of EC mesh cells per processor mesh (vtk cells) = %d\t\tm = %d n = %d\n" \
    % (numECsPerCol *numECsPerRow, numECsPerCol, numECsPerRow))
    configFile.write("Total number of EC mesh centeroid points per processor mesh (vtk points) = %d\t\tm = %d n = %d\n" \
    % (numECsPerCol *numECsPerRow, numECsPerCol, numECsPerRow))
    configFile.write("Total number of EC mesh centeroid cells per processor mesh (vtk cells) = %d\t\tm = %d n = %d\n" \
    % (numECsPerCol *numECsPerRow, numECsPerCol, numECsPerRow))

    configFile.close()
    
    print "Now it is all done for real ..."

if __name__ == '__main__':
    print "Starting", os.path.basename(__file__)
    main()
    print "Exiting", os.path.basename(__file__)