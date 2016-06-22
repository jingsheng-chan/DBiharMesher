import os
import vtk
import h5py

quadScaleCirc = 1
quadScaleAxial = 1
ecMeshIn = ""
atpMeshIn = ""
taskMeshIn = ""
numECsPerCol = 4
numSMCsPerRow = 4
numECsPerRow = 20
numSMCsPerCol = 52

axialQuads = 0
circQuads = 0


# hdf5 files to write.
atpHdf5Files = [
"files/parent_atp.h5",
"files/left_daughter_atp.h5",
"files/right_daughter_atp.h5",
]

def writeHdf5():
    # This is where the data is for testing purposes.
    print "Current working directory:", os.getcwd()
    
    numQuadsPerRing = circQuads / 2
    
    # Sanity checking
    if quadScaleCirc > numQuadsPerRing or quadScaleAxial > axialQuads:
        exit("Error: Quad scale/s too large for mesh.")
        
    if axialQuads % quadScaleAxial != 0 or circQuads % numQuadsPerRing != 0:
        exit("Error: Quad scale/s inappropriate for task mesh dimensions.")
        

    
    numECsPerQuad = numECsPerRow * numECsPerCol
    numSMCsPerQuad = numSMCsPerCol * numSMCsPerRow
    
    print numECsPerQuad
    print numSMCsPerQuad

    taskMeshReader = vtk.vtkXMLPolyDataReader()
    taskMeshReader.SetFileName(taskMeshIn)
    taskMeshReader.Update()

    taskMesh = taskMeshReader.GetOutput()
    print taskMesh.GetNumberOfPoints()
    
    ecMeshReader = vtk.vtkXMLPolyDataReader()
    ecMeshReader.SetFileName(ecMeshIn)
    ecMeshReader.Update()
    
    ecMesh = ecMeshReader.GetOutput()
    print ecMesh.GetNumberOfPoints()
    
    # Get the range of branch labels.
    labelRange = [0, 0]
    taskMesh.GetCellData().GetScalars().GetRange(labelRange, 0)

    # Convert label range to a list of labels.
    labelRange = range(int(labelRange[0]), int(labelRange[1]) + 1)
    print "Labels found in task mesh:", labelRange

    # Store the number of rings for each label. 
    numRingsPerLabel = {}   
    print "Num quads per ring:",numQuadsPerRing

    # For every label in the range of labels we want to extract all cells/quads.
    for label in labelRange:
        
        # Use this filter to extract the cells for a given label value.
        branchSelector = vtk.vtkThreshold()
        branchSelector.SetInputData(taskMesh)
        branchSelector.ThresholdBetween(label,label);
        branchSelector.Update()

        taskMeshBranch = branchSelector.GetOutput()

        numQuadRowsPerBranch = taskMeshBranch.GetNumberOfCells() / numQuadsPerRing;
        numRingsPerLabel[label] = numQuadRowsPerBranch
        
        
    print numRingsPerLabel
    # Working with EC mesh only
    atpMeshReader = vtk.vtkXMLPolyDataReader()
    atpMeshReader.SetFileName(atpMeshIn)
    atpMeshReader.Update()

    # Original ECs mesh to work with.
    atpMesh = atpMeshReader.GetOutput()
    print "There are", atpMesh.GetNumberOfCells(), "ATP values in total ..."

    # Prepare h5 files  
    parentFile = h5py.File(atpHdf5Files[0], 'w')
    leftBranchFile = h5py.File(atpHdf5Files[1], 'w')
    rightBranchFile = h5py.File(atpHdf5Files[2], 'w')

    
    # For every label in the range of labels we want to extract all ECs.
    for label in labelRange:

        # Keep track of how many branches we need to skip.
        numECsPerLabel = numQuadsPerRing * numRingsPerLabel[label] * numECsPerQuad
        atpCellOffset = label * numECsPerLabel

        print "atpCellOffset", atpCellOffset

        # Collect cell ids to select.
        selectionIds = vtk.vtkIdTypeArray()
        for sId in range(0, numECsPerLabel):
            selectionIds.InsertNextValue(atpCellOffset + sId)

        # Create selecion node.
        selectionNode = vtk.vtkSelectionNode()
        selectionNode.SetFieldType(selectionNode.CELL)
        selectionNode.SetContentType(selectionNode.INDICES)
        selectionNode.SetSelectionList(selectionIds)

        # Create selection.
        selection = vtk.vtkSelection()
        selection.AddNode(selectionNode)

        # Use vtkSelection filter.
        selectionExtractor = vtk.vtkExtractSelection()
        selectionExtractor.SetInputData(0, atpMesh)
        selectionExtractor.SetInputData(1, selection)
        selectionExtractor.Update()

        extractedCells = selectionExtractor.GetOutput()

        # Ring ids list for traversal.
        ringIds = range(0, numRingsPerLabel[label])
        ringIds.reverse()

        # Number of ECs rows is the number of ECs per quad.
        rowIds = range(0, numECsPerCol)
        rowIds.reverse()
        
        reorderedATPArray = vtk.vtkDoubleArray()
        reorderedATPArray.SetName("initialATP")

        # Decide which hdf5 files to write to.
        pointsOf = ''
        
        if label == 0:
            pointsOf = parentFile
        elif label == 1:
            pointsOf = leftBranchFile
        elif label == 2:
            pointsOf = rightBranchFile

        print "Writing H5 file for ECs ATP:"
        print pointsOf
        
        dset = pointsOf.create_dataset("/atp", (numECsPerLabel,), 'f')
        
        # Include cell dimensions for only parent file.
        if label == 0:
            dset.attrs['numSMCsPerRow'] = numSMCsPerRow * quadScaleCirc
            dset.attrs['numSMCsPerCol'] = numSMCsPerCol * quadScaleAxial
            
            dset.attrs['numECsPerCol'] = numECsPerCol * quadScaleAxial
            dset.attrs['numECsPerRow'] = numECsPerRow * quadScaleCirc

        # Calculate which rows (circumferentially) required to be iterated over
        # given the quad scalling.
        ringsPerRow = circQuads / numQuadsPerRing
        requiredRings = []
        row = -1
        for ringId in range(len(ringIds)):
            if ringId % ringsPerRow == 0:
                row += 1
            if row % quadScaleAxial == 0:
                requiredRings.append(ringIds[ringId])
                
        for i in range(0, len(requiredRings), 2):
            j = i + 1
            requiredRings[i], requiredRings[j] = requiredRings[j], requiredRings[i]
            
        i = 0
        # Iterate over the rings in reverse order.
        for ringNum in requiredRings:

            # Iterate over the 'imaginary' quads of cells in normal order.
            for quadNum in range(0, numQuadsPerRing):
                    
                # Skip this quad, it was included in the
                # previous iteration according the the quad scaling.
                if quadNum % quadScaleCirc != 0:
                    continue
                
                # Iterate over the rows of cells in reverse order.
                # Calculate the 'real' id for the 'imaginary' quad.
                quadId = ringNum * numQuadsPerRing + quadNum

                # Iterate over rows of cells in reverse order.
                # Loop through extra rows based on quad scale.
                for extraAxial in range(0, quadScaleAxial): 
                
                    rowOffset = - extraAxial * numECsPerQuad * circQuads

                    # Iterate over the rows of cells in normal order.
                    for rowNum in rowIds:
                        # Loop through extra columns based on quad scale.
                        for extraCirc in range(0, quadScaleCirc):
                            quadOffset = extraCirc * (numECsPerQuad)
                            
                            for cellNum in range(0, numECsPerRow):
                                
                                # Calculate the 'real' ec cell id and get the corresponding cell.
                                realId = quadId * numECsPerQuad + rowNum * numECsPerRow + cellNum + quadOffset + rowOffset
                                
                                atpVal = extractedCells.GetCellData().GetArray("initialATP").GetValue(realId)
                                reorderedATPArray.InsertNextValue(atpVal)
                                
                                # Write the value to the hdf5 file.
                                dset[i] = atpVal
                                i += 1            
                        
    parentFile.close()
    leftBranchFile.close()
    rightBranchFile.close()

    print "All done ..."
    
def main():
    print "This script is to be run with global parameters (input, output files, etc.) set in the calling script."

if __name__ == '__main__':
    print "Starting", os.path.basename(__file__)
    main()
    print "Exiting", os.path.basename(__file__)
