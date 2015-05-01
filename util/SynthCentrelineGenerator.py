#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# SynthCentrelineGenerator.py by Constantine Zakkaroff
#
# This scipt builds a centreline tree from a nested list representing the tree topology.
# The fist item in each list is the domain, followed by the left
# and right branches if any.
#
# Output centrelines are saved in VTK legacy format in the current working directory
# in a file "centreline.vtk".
#
# Parameters to control the generated tree points are to be set in this file.
# VTK visualisation of the tree is shown at the end.
# 
# Tree grows from (0,0,0) towards positive x-axis. Bifurcations occur at 45 degrees
# by defualt, or at a given angle if specfied.
#
# Domains are either given as a number, which represents the domain length, or a 
# tuple that represents (domain length, angle).
#
# All angles are measured clockwise from the positive y-axis, and are specified
# in degrees.
# Modified by: Stewart Dowding 15/12/14

# TODO:
# Name and location of the outputfile should be specified from keyboard input at runtime.

import sys
import vtk
import math

# Lists to be used as input. A specific list is passed as the argument to
# buildCentreline in main.

# Paremeters specifying the properties of the generated centrelines.

# Default branch angle if the angle por branch is not specified.
branchAngle = math.pi / 4.0

scaling = 1.0
step = 0.1
radiusDecreasing = True

segmentList0 = [20,  
               [(20,60),[(30,35),None,None],[(20,105),None,None]],   
               [(20,150),[(40,105),None,None],[(30,150),[(30,105),None,None],[(40,150),None,None]]]]
# radiusBase = 2.5

segmentList1 = [20,  
               [(20,60),[(20,15),       [(30,350),None,None],[(30,60),None,None]]          ,[(40,105),None,None]],   
               [(20,150),[(50,105),None,None],[(30,150),[(40,105),None,None],[(60,150),None,None]]]]
# radiusBase = 2.5

segmentList2 = [16,[8,[4,[2,None,None],[2,None,None]],None],[8,[4,None,None],None]]
segmentList3 = [20,[(20,60),[(20,80),None,None],[20,None,None]],[(20,135),None,None]]

# A centreline for a mesh with 216 cores.
segmentList4 = [1.7,[(1.7,60),None,None], [(1.7,120),None,None]]
# radiusBase = 0.382

# A centreline for a mesh with 4080 cores.
segmentList5 = [8.84,[(8.84,60),None,None], [(8.84,120),None,None]]
# radiusBase = 1.2732395447351628

# A centreline for a mesh with 4032 cores.
segmentList6 = [7.2,[(7.2,60),None,None], [(7.2,120),None,None]]
# radiusBase = 1.5278874536821951

# A centreline for a mesh with 8064 cores, 56x48
segmentList7 = [14.56,[(14.56,60),None,None], [(14.56,120),None,None]]
# radiusBase = 1.5278874536821951

# A centreline for a mesh with 8064 cores. 42x64
segmentList8 = [10.92,[(10.92,60),None,None], [(10.92,120),None,None]]
# radiusBase = 2.0371832715762603

# A centreline for a mesh with 16128 cores.
segmentList9 = [21.84,[(21.84,60),None,None], [(21.84,120),None,None]]
radiusBase = 2.5#2.0371832715762603

# If sphereRadius is set to None, the centreline is generated in the XY plane.
# Otherwise the centreline is wrapped on a sphere of the specified radius.
sphereRadius = None
points = vtk.vtkPoints()
lines = vtk.vtkCellArray()
radii = vtk.vtkDoubleArray()
radii.SetName("radiiScalars")
centreline = vtk.vtkPolyData()

def buildCentreline(segmentList, firstId = 0, firstPt = (0.0,0.0,0.0), direction = 0.0):
    print 'Processing centreline:', segmentList
    
    domain = None

    try:
        domain = segmentList[0]
    except IndexError:
        sys.exit("Missing domain length in list " + str(list) + ".")
        
    if isinstance(domain, tuple):
        domainLength = domain[0]
        angle = math.radians(domain[1])
    else:    
        if not isinstance(domain, (int, float, long)):
            sys.exit("Domain length should be a number, not a(an) " + str(type(domainLength)) + ".")
        angle = branchAngle
        domainLength = domain
    
    leftBranch = None
    try:
        leftBranch = segmentList[1]
    except IndexError:
        pass
    
    rightBranch = None
    try:
        rightBranch = segmentList[2]
    except IndexError:
        pass
    
    line = vtk.vtkPolyLine()
    
    if  direction < 0:
        angle = math.pi - angle
    
    for pId in range (0, int(domainLength / step) + 1):
            nextPt = ((firstPt[0] + (1.0 if direction == 0.0 else math.sin(angle)) * (step * pId)) * scaling, \
                        (firstPt[1] + (1.0 if direction == 0.0 else math.cos(angle)) * (step * pId) * direction) * scaling , \
                        firstPt[2] * scaling)
                        
            if sphereRadius != None:
                longitude = nextPt[0] / sphereRadius
                latitude = 2 * math.atan(math.exp(nextPt[1] / sphereRadius)) - math.pi / 2.0
                nextPtS = (sphereRadius * math.cos(latitude) * math.cos(longitude),\
                            sphereRadius * math.cos(latitude) * math.sin(longitude),\
                            sphereRadius * math.sin(latitude))
            
                if firstId == 0 or pId > 0:
                    nextId = points.InsertNextPoint(nextPtS)
                else:
                    nextId = firstId
            else:
                if firstId == 0 or pId > 0:
                    nextId = points.InsertNextPoint(nextPt)
                else:
                    nextId = firstId
            
            line.GetPointIds().InsertNextId(nextId)
            
    lines.InsertNextCell(line)
    
    if isinstance(leftBranch, list):
        buildCentreline(leftBranch, nextId, nextPt, 1.0)

    if isinstance(rightBranch, list):
        buildCentreline(rightBranch, nextId, nextPt, -1.0)
        
        
        
        
        
def treeTraversal(startingCell):
    
    branchesToExplore = vtk.vtkPriorityQueue()
    points1 = vtk.vtkGenericCell()
    cellIds = vtk.vtkIdList()
    priority = int(lines.GetNumberOfCells())
    
    path = [startingCell]
    paths = []
    traversal = []    
    
    lengths = [0] * int(lines.GetNumberOfCells())  
    branchesToExplore.Insert(priority, startingCell)
    priority -= 1
    
        
    centreline.GetCell(startingCell, points1)
    lengths[startingCell] = int(points1.GetNumberOfPoints() - 1)
    currentId = startingCell
    
    while branchesToExplore.GetNumberOfItems() != 0:
        points2 = vtk.vtkGenericCell()
   
        centreline.GetCell(currentId, points2)
        
        endPointId = int(points2.GetPointId(points2.GetNumberOfPoints() - 1))
        
        centreline.GetPointCells(endPointId, cellIds)
        
        if cellIds.GetNumberOfIds() > 1:
            for pos in range(1, cellIds.GetNumberOfIds()):
                branchesToExplore.Insert(priority, cellIds.GetId(pos))
                priority -= 1
                
                centreline.GetCell(cellIds.GetId(pos), points2)
                lengths[cellIds.GetId(pos)] = int(points2.GetNumberOfPoints() - 1 + lengths[currentId])

                paths.append(path[:] + [int(cellIds.GetId(pos))])
                
        else:
            traversal.append([path,lengths[currentId]])
            
        currentId = int(branchesToExplore.Pop())
        if len(paths) != 0:    
            path = paths.pop()
        
    traversal.sort(key = lambda x: x[1], reverse = True)
    
    return traversal
 
 
def murraysLaw(decreaseLength = 3):
    
    radii.SetNumberOfValues(points.GetNumberOfPoints())

    ids = vtk.vtkIdList()
    lines.InitTraversal()
    lines.GetNextCell(ids)
    
    decreaseLength /= step
    
    #assign trunk scalars indentically as radiusBase
    for pointId in range(ids.GetId(0), ids.GetNumberOfIds()):
        radii.SetValue(pointId, radiusBase)
        
        
        
    numLines = int(lines.GetNumberOfCells())
    # For each line (cell) in the tree
    for line in range (1, numLines):
        ids = vtk.vtkIdList()
        lines.GetNextCell(ids)
        
        start = ids.GetId(1)
        end = ids.GetNumberOfIds() + start - 1
        
        i = 1
        # With the DFS the previous value will always exist...?
        parentValue = radii.GetValue(ids.GetId(0)) # Can i assume this?
        childValue = ((parentValue ** 3) / 2) ** (1 / 3.0)
        
        distance = parentValue * decreaseLength
        if distance > ids.GetNumberOfIds():
            distance = ids.GetNumberOfIds()
       
        
        for pointId in range(start, end):  
            if i < distance:
                k = (math.log(childValue)-math.log(parentValue)) / distance
                x0 = math.exp(math.log(childValue) - k * distance)
                x = x0 * math.exp(k*i)   
                                
                radii.SetValue(pointId, x)
                i += 1
            else:
                radii.SetValue(pointId, childValue)
                

def buildRadiiScalars():
    radii.SetNumberOfValues(points.GetNumberOfPoints())
    radii.InsertValue(0, radiusBase)
    alreadyBuilt = []
    bifurcationValues = dict()
    distanceCovered = 0
    traversal = treeTraversal(0)
    
    # For every path, starting from longest route.
    for path, length in traversal:
    
        distanceCovered = 0
        
        # For each cellId in path, check hasn't already been done.
        for cellId in path:
        
            connectedCellIds = vtk.vtkIdList()            
            ids = vtk.vtkGenericCell()
            centreline.GetCell(cellId, ids)
        
            newId = ids.GetPointId(0)
            centreline.GetPointCells(newId, connectedCellIds)
        
            if connectedCellIds.GetNumberOfIds() > 1:
                minCellId = connectedCellIds.GetId(0)
        
                for i in range(1, connectedCellIds.GetNumberOfIds()):
                    minCellId = min(minCellId, connectedCellIds.GetId(i))
                
                scalarValue = bifurcationValues[minCellId]
                
            else: # for first iteration (inlet)
                scalarValue = radiusBase
                
            if cellId not in alreadyBuilt:
                start = int(ids.GetPointId(1))
                end = int(ids.GetNumberOfPoints()) + start - 1

                p = length - distanceCovered
                i = 1
                
                for pointId in range(start, end):
                    k = (math.log(0.5)-math.log(scalarValue))/p
                    x0 = math.exp(math.log(0.5)-k*p)
                    x = x0 * math.exp(k*i)   
                                    
                    radii.SetValue(pointId, x)
                    i += 1
                    
                bifurcationValues[cellId] = x
                alreadyBuilt.append(cellId)
                
            distanceCovered += int(ids.GetNumberOfPoints() - 1)

def main():
    
    global centreline
    
    buildCentreline(segmentList1)

    
    print "Number of points in the centreline:", points.GetNumberOfPoints()
    centreline.SetPoints(points)    
    centreline.SetLines(lines)
    
    if radiusDecreasing:
        # Build decreasing radii. Use either buildRadiiScalars or murraysLaw
        #buildRadiiScalars()
        murraysLaw(3)
    else:
        # Constant radii for all points.
        rIdx = 0
        while rIdx < points.GetNumberOfPoints():
            radii.InsertNextValue(radiusBase)
            rIdx = rIdx + 1
    
    centreline.GetPointData().SetScalars(radii)

    if sphereRadius != None:
        origin = centreline.GetPoint(0)
        transform = vtk.vtkTransform()
        transform.Translate(-origin[0],-origin[1],-origin[2])
        transformFilter = vtk.vtkTransformPolyDataFilter()
        transformFilter.SetInput(centreline)
        transformFilter.SetTransform(transform)
        
        transformFilter.Update()
        centreline = transformFilter.GetOutput()
    
    writer = vtk.vtkPolyDataWriter()
    writer.SetInput(centreline)
    writer.SetFileName("centreline233.vtk")
    writer.SetFileTypeToASCII()
    writer.Write()
    
    mapper = vtk.vtkDataSetMapper()
    mapper.SetInput(centreline)
    
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    
    renderer = vtk.vtkRenderer()
    renderer.SetBackground(1,1,1)
    renderer.AddActor(actor)
    
    rendererWindow = vtk.vtkRenderWindow()
    rendererWindow.AddRenderer(renderer)
        
    interactor = vtk.vtkRenderWindowInteractor()
    style = vtk.vtkInteractorStyleTrackballCamera()
    interactor.SetInteractorStyle(style)
    interactor.SetRenderWindow(rendererWindow)
        
    interactor.Initialize()
    interactor.Start()
    
    rendererWindow.Finalize()
    interactor.TerminateApp()

if __name__ == '__main__':
    main()