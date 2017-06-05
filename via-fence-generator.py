#!/usr/bin/env python2
import pcbnew
import math
import pyclipper
import collections
from bisect import bisect_left
from itertools import cycle


import matplotlib.pyplot as plt
import numpy as np


def getLineSlope(line):
    return math.atan2(line[0][1]-line[1][1], line[0][0]-line[1][0])

def getLineLength(line):
    return math.hypot(line[0][0]-line[1][0], line[0][1]-line[1][1])

def getSubPath(path, pathSpec):
    listModulus = len(path)
    if (pathSpec[1] < pathSpec[0]): pathSpec[1] += listModulus
    return [path[i % listModulus] for i in range(pathSpec[0], pathSpec[1]+1)]

def getSubPaths(path, pathSpecList):
    return [getSubPath(path, pathSpec) for pathSpec in pathSpecList if (pathSpec[0] != pathSpec[1])]

def splitPathByPoints(path, splitList):
    pathSpecList = [[splitList[item], splitList[item+1]] for item in range(0, len(splitList)-1)]
    return getSubPaths(path, pathSpecList)

def splitPathByPaths(path, splitList):
    pathSpecList = [[splitList[item][-1], splitList[(item+1)%len(splitList)][0]] for item in range(0, len(splitList))]
    return getSubPaths(path, pathSpecList)

# Return a cumulative distance vector representing the distance travelled along
# the path at each path vertex
def getPathCumDist(path):
    cumDist = [0.0]
    for vertexId in range(1, len(path)):
        cumDist += [cumDist[-1] + getLineLength([path[vertexId], path[vertexId-1]])]

    return cumDist

# Return a list of all vertex indices where the angle between
# the two lines connected to the vertex deviate from a straight
# path more by the tolerance angle in degrees
# This function is used to find bends that are larger than a certain angle
def getPathVertices(pathList, angleTolerance):
    angleTolerance = angleTolerance * math.pi / 180
    vertices = []

    # Look through all vertices except start and end vertex
    # Calculate by how much the lines before and after the vertex
    # deviate from a straight path.
    # If the deviation angle exceeds the specification, store it
    for vertexIdx in range(1, len(pathList)-1):
        prevSlope = getLineSlope([pathList[vertexIdx+1], pathList[vertexIdx]])
        nextSlope = getLineSlope([pathList[vertexIdx-1], pathList[vertexIdx]])
        deviationAngle = abs(prevSlope - nextSlope) - math.pi
        if (abs(deviationAngle) > angleTolerance):
            vertices += [vertexIdx]

    return vertices

# Uses the cross product to check if a point is on a line defined by two other points
def isPointOnLine(point, line):
    cross = (line[1][1] - point[1]) * (line[0][0] - point[0]) - (line[1][0] - point[0]) * (line[0][1] - point[1])

    if  (   ((line[0][0] <= point[0] <= line[1][0]) or (line[1][0] <= point[0] <= line[0][0]))
        and ((line[0][1] <= point[1] <= line[1][1]) or (line[1][1] <= point[1] <= line[0][1]))
        and (cross == 0) ):
        return True
    return False

# Returns a list of path indices touching any item in a list of points
def getPathsThroughPoints(path, pointList):
    touchingPaths = []

    for vertexIdx in range(0, len(path)-1):
        # This is the current line segment to test
        line = [ path[vertexIdx], path[vertexIdx+1] ]

        # If a point in the pointList is located on this line, store the line
        for point in pointList:
            if isPointOnLine(point, line):
                touchingPaths += [[vertexIdx, vertexIdx+1]]
                break

    return touchingPaths

# A small linear interpolation class so we don't rely on scipy or numpy here
class LinearInterpolator(object):
    def __init__(self, x_list, y_list):
        self.x_list, self.y_list = x_list, y_list
        intervals = zip(x_list, x_list[1:], y_list, y_list[1:])
        self.slopes = [(y2 - y1)/(x2 - x1) for x1, x2, y1, y2 in intervals]
    def __call__(self, x):
        i = bisect_left(self.x_list, x) - 1
        return self.y_list[i] + self.slopes[i] * (x - self.x_list[i])

# Interpolate a path with (x,y) vertices using a third parameter t
class PathInterpolator:
    def __init__(self, t, path):
        # Quick and dirty transpose path so we get two list with x and y coords
        # And set up two separate interpolators for them
        x = [vertex[0] for vertex in path]
        y = [vertex[1] for vertex in path]
        self.xInterp = LinearInterpolator(t, x)
        self.yInterp = LinearInterpolator(t, y)
    def __call__(self, t):
        # Return interpolated coordinates on the original path
        return [self.xInterp(t), self.yInterp(t)]

def expandPathsToPolygons(pathList, offset):
    # Use PyclipperOffset to generate polygons that surround the original
    # paths with a constant offset all around
    co = pyclipper.PyclipperOffset()
    co.AddPaths(pathList, pyclipper.JT_ROUND, pyclipper.ET_OPENROUND)
    return co.Execute(offset)

# Distribute Points along a path with equal spacing to each other
# When the path length is not evenly dividable by the minimumSpacing,
# the actual spacing will be larger, but still smaller than 2*minimumSpacing
# The function does not return the start and end vertex of the path
def distributeAlongPath(path, minimumSpacing):
    # Get cumulated distance vector for the path
    # and determine the number of points that can fit to the path
    # determine the final pitch by dividing the total path length
    # by the rounded down number of points
    distList = getPathCumDist(path)
    nPoints = int(math.floor(distList[-1] / minimumSpacing))
    ptInterp = PathInterpolator(distList, path)
    return [ptInterp(ptIdx * distList[-1]/nPoints) for ptIdx in range(1, nPoints)]

def getLeafVertices(tracks):
    leafVertices = []
    leafVertexNeighbours = []
    leafVertexAngles = []

    for trackA in tracks:
        for vertexIdxA in [0,-1]:
            vertexA = trackA[vertexIdxA]
            vertexOccurences = 0
            for trackB in tracks:
                for vertexB in trackB:
                    if (vertexA[0] == vertexB[0]) and (vertexA[1] == vertexB[1]):
                        vertexOccurences += 1
            if (vertexOccurences == 1):
                # vertex appears only once in total
                leafVertices += [vertexA]
                # Get neighbour vertex
                if (vertexIdxA == 0): neighbourVertex = trackA[1]
                elif (vertexIdxA == -1): neighbourVertex = trackA[-2]
                leafVertexAngles += [getLineSlope([neighbourVertex, vertexA])]

    return leafVertices, leafVertexAngles

def transformVertices(vertexList, offset, angle):
    newVertexList = []
    for vertex in vertexList:
        newVertexList += [[ offset[0] + math.cos(angle) * vertex[0] - math.sin(angle) * vertex[1],
                            offset[1] + math.sin(angle) * vertex[0] + math.cos(angle) * vertex[1] ]]
    return newVertexList

######################
def generateViaFence(pathList, viaOffset, viaPitch):
    offsetTrack = expandPathsToPolygons(pathList, viaOffset)[0]


# TODO: multiple paths

#    pc1 = pyclipper.Pyclipper()
#    test = pc1.AddPaths(tracks, pyclipper.PT_SUBJECT, False)
#    bla = pc1.Execute2(pyclipper.CT_UNION)

#    tracks=(pyclipper.OpenPathsFromPolyTree(bla))

    # Since PyclipperOffset returns a closed path, we need to find
    # the butt lines in this closed path, i.e. the lines that are
    # perpendicular to the original tracks' start and end points
    # First collect all the start and end vertices of all input paths
    # Then check if any of those vertices are located on any of
    # the polygon line segments
    # If this is the case, we consider them a butt line
    leafVertexList, leafVertexAngles = getLeafVertices(pathList)

#    allVertices = [track for subTracks in tracks for track in subTracks]
#    startEndVertexList = [track[idx] for idx in [0, -1] for track in tracks]
#    leafVertexList = getVerticesUniqueIn(startEndVertexList, allVertices) # leafVertices are unique

    # how to get the slope of leafVertex?
    # Maybe make class Vertex inherit from namedtuple with x,y,prev,next,unique?
    # let getVerticesUniqueIn return lines?
    # how to find the point connected to leavVertex? search for it?
    # Can we get indexes from getVerticesUniqueIn? has to be hierachical: LineIdx, pointIdx
    # Rotate the cutRect to match the end style thing
    # pyclipper.clip(not) it
    for idx in range(0, len(leafVertexList)):
        plt.text(leafVertexList[idx][0], leafVertexList[idx][1], leafVertexAngles[idx])


    cutRect = [ [0, -1.5*viaOffset], [0, 0], [0, 1.5*viaOffset], [-1.5*viaOffset, 1.5*viaOffset], [-1.5*viaOffset, -1.5*viaOffset] ]

    cutRects = []
    for vertexPos, vertexAngle in zip(leafVertexList, leafVertexAngles):
        newRect = transformVertices(cutRect, vertexPos, vertexAngle)
        cutRects += [newRect]
#        plt.plot(np.array(newRect).T[0], np.array(newRect).T[1])

    pc = pyclipper.Pyclipper()
    pc.AddPath(offsetTrack, pyclipper.PT_SUBJECT, True)
    pc.AddPaths(cutRects, pyclipper.PT_CLIP, True)
    offsetTrack = pc.Execute(pyclipper.CT_DIFFERENCE)[0]

 #   plt.plot(np.array(offsetTrack).T[0], np.array(offsetTrack).T[1])


    buttLineIdxList = getPathsThroughPoints(offsetTrack, leafVertexList)
    print(buttLineIdxList)
    for buttLineIdx in buttLineIdxList:
        buttLine = [ offsetTrack[buttLineIdx[0]], offsetTrack[buttLineIdx[1]] ]
#        plt.plot(np.array(buttLine).T[0], np.array(buttLine).T[1])
#        plt.plot(buttLine[0][0], buttLine[0][1], '+', markersize=10)
#        plt.plot(buttLine[1][0], buttLine[1][1], 'x', markersize=10)

    # The butt lines are used to split up the closed polygon into multiple
    # separate open paths to the left and the right of the original tracks
    fencePaths = splitPathByPaths(offsetTrack, buttLineIdxList)
    viaPoints = []

    for path in fencePaths:
        pass
#        plt.plot(np.array(path).T[0], np.array(path).T[1])
#        plt.plot(path[0][0], path[0][1], '+', markersize=10, markeredgewidth=2)
#        plt.plot(path[-1][0], path[-1][1], 'x', markersize=10, markeredgewidth=2)


    # With the now separated open paths we perform via placement on each one of them
    for fencePath in fencePaths:
        # For a nice via fence placement, we find vertices having an included angle
        # satisfying a defined specification. This way non-smooth (i.e. non-arcs) are
        # identified in the fence path. We use these to place fixed vias on their positions
        # We also use start and end vertices of the fence path as fixed via locations
        fixPointIdxList = [0] + getPathVertices(fencePath, 10) + [-1]
        viaPoints += [fencePath[idx] for idx in fixPointIdxList]

#        continue
        # Then we autoplace vias between the fixed via locations by satisfying the
        # minimum via pitch given by the user
        for subPath in splitPathByPoints(fencePath, fixPointIdxList):
            # Now equally space the vias along the subpath using the given minimum pitch
            # Add the generated vias to the list
            viaPoints += distributeAlongPath(subPath, viaPitch)
            plt.plot(np.array(subPath).T[0], np.array(subPath).T[1])
            pass

    return viaPoints



if __name__ == "__main__":
    import csv

    def readPath(stream):
        pathList = []
        for row in csv.reader(stream, delimiter=','):
            vertices = [field.split(';') for field in row]
            pathList += [ [ [int(xy) for xy in vertex] for vertex in vertices ] ]
        return pathList

    # Set some via parameters
    # generate some test paths and run
    viaOffset = 500
    viaPitch = 300

    with open('via-fence-generator-track.csv', 'rb') as file:
        pathList = readPath(file)

    viaPoints = generateViaFence(pathList, viaOffset, viaPitch)

    for path in pathList:
        plt.plot(np.array(path).T[0], np.array(path).T[1], linewidth=5)
    for via in viaPoints:
        plt.plot(via[0], via[1], 'o', markersize=10)

    plt.axes().set_aspect('equal','box')
    plt.xlim(0, 6000)
    plt.ylim(0, 8000)
    plt.ylim(plt.ylim()[::-1])
    plt.savefig('via-fence-generator.png')
    plt.show()

    exit(0)


# Python plugin stuff
class ViaFenceGenerator(pcbnew.ActionPlugin):
    def defaults(self):
        self.name = "Add a via fence to the PCB"
        self.category = "Modify PCB"
        self.description = "Automatically add a via fence to a net or tracks on the PCB"

    def Run(self):
        pcbObj = pcbnew.GetBoard()

        netName = 'Net-(U1-Pad2)'
        viaOffset = pcbnew.FromMM(0.5)
        viaPitch =  pcbnew.FromMM(1)

#        netId = pcbObj.FindNet(netName).GetNet()
        netId = pcbObj.GetHighLightNetCode()

        if (netId != -1):
            netTracks = pcbObj.TracksInNet(netId)

            trackList = [ [[t.GetStart()[0], t.GetStart()[1]], [t.GetEnd()[0], t.GetEnd()[1]]] for t in netTracks ]
            viaPoints = generateViaFence(trackList, viaOffset, viaPitch)


            for track in trackList:
                plt.plot(np.array(track).T[0], np.array(track).T[1], linewidth=1)
            for via in viaPoints:
                plt.plot(via[0], via[1], 'o', markersize=10)


            plt.ylim(plt.ylim()[::-1])
            plt.axes().set_aspect('equal','box')
        #    plt.xlim(0, 6000)
        #    plt.ylim(0, 8000)
            plt.show()







ViaFenceGenerator().register()

