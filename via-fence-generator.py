#!/usr/bin/env python2
import pcbnew
import math
import pyclipper
from bisect import bisect_left

# Returns the slope of a line
def getLineSlope(line):
    return math.atan2(line[0][1]-line[1][1], line[0][0]-line[1][0])

# Returns the length of a line
def getLineLength(line):
    return math.hypot(line[0][0]-line[1][0], line[0][1]-line[1][1])

# Returns a sub paths in a path with a path specification (startIdx, stopIdx)
def getSubPath(path, pathSpec):
    listModulus = len(path)
    if (pathSpec[1] < pathSpec[0]): pathSpec[1] += listModulus
    return [path[i % listModulus] for i in range(pathSpec[0], pathSpec[1]+1)]

# Returns a list of subpaths with a list of path specifications
def getSubPaths(path, pathSpecList):
    return [getSubPath(path, pathSpec) for pathSpec in pathSpecList if (pathSpec[0] != pathSpec[1])]

# Splits a path using a list of indices representing points on the path
def splitPathByPoints(path, splitList):
    pathSpecList = [[splitList[item], splitList[item+1]] for item in range(0, len(splitList)-1)]
    return getSubPaths(path, pathSpecList)

# Splits a path around a list of list of indices representing a subpath within the original path
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
def getPathVertices(path, angleTolerance):
    angleTolerance = angleTolerance * math.pi / 180
    vertices = []

    # Look through all vertices except start and end vertex
    # Calculate by how much the lines before and after the vertex
    # deviate from a straight path.
    # If the deviation angle exceeds the specification, store it
    for vertexIdx in range(1, len(path)-1):
        prevSlope = getLineSlope([path[vertexIdx+1], path[vertexIdx]])
        nextSlope = getLineSlope([path[vertexIdx-1], path[vertexIdx]])
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

    for vertexIdx in range(0, len(path)):
        fromIdx = vertexIdx
        toIdx = (vertexIdx+1) % len(path)

        # If a point in the pointList is located on this line, store the line
        for point in pointList:
            if isPointOnLine(point, [ path[fromIdx], path[toIdx] ]):
                touchingPaths += [[fromIdx, toIdx]]
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

# A small pyclipper wrapper class to expand a line to a polygon with a given offset
def expandPathsToPolygons(pathList, offset):
    # Use PyclipperOffset to generate polygons that surround the original
    # paths with a constant offset all around
    co = pyclipper.PyclipperOffset()
    co.AddPaths(pathList, pyclipper.JT_ROUND, pyclipper.ET_OPENROUND)
    return co.Execute(offset)

# A small pyclipper wrapper to trim parts of a polygon using another polygon
def clipPolygonWithPolygons(path, clipPathList):
    pc = pyclipper.Pyclipper()
    pc.AddPath(path, pyclipper.PT_SUBJECT, True)
    pc.AddPaths(clipPathList, pyclipper.PT_CLIP, True)
    return pc.Execute(pyclipper.CT_DIFFERENCE)

def isPointInPolygon(point, path):
    return True if (pyclipper.PointInPolygon(point, path) == 1) else False

def getPathsInsidePolygon(pathList, polygon):
    filteredPathList = []

    for path in pathList:
        allVerticesInside = True
        for vertex in path:
            if not isPointInPolygon(vertex, polygon):
                allVerticesInside = False
                break
        if (allVerticesInside): filteredPathList += [path]

    return filteredPathList

# Distribute Points along a path with equal spacing to each other
# When the path length is not evenly dividable by the minimumSpacing,
# the actual spacing will be larger, but still smaller than 2*minimumSpacing
# The function does not return the start and end vertex of the path
def distributeAlongPath(path, minimumSpacing):
    # Get cumulated distance vector for the path
    # and determine the number of points that can fit to the path
    distList = getPathCumDist(path)
    nPoints = int(math.floor(distList[-1] / minimumSpacing))
    ptInterp = PathInterpolator(distList, path)
    return [ptInterp(ptIdx * distList[-1]/nPoints) for ptIdx in range(1, nPoints)]

# Find the leaf vertices in a list of paths,
# additionally it calculates the slope of the line connected to the leaf vertex
def getLeafVertices(pathList):
    allVertices = [vertex for path in pathList for vertex in path]
    leafVertices = []
    leafVertexSlopes = []

    for path in pathList:
        for vertexIdx in [0,-1]:
            if (allVertices.count(path[vertexIdx]) == 1):
                # vertex appears only once in entire path list, store away
                # Get neighbour vertex and also calculate the slope
                leafVertex = path[vertexIdx]
                neighbourVertex = path[ [1,-2][vertexIdx] ]
                leafVertices += [leafVertex]
                leafVertexSlopes += [getLineSlope([neighbourVertex, leafVertex])]

    return leafVertices, leafVertexSlopes

# Rotate and Translate a list of vertices using a given angle and offset
def transformVertices(vertexList, offset, angle):
    return [ [ offset[0] + math.cos(angle) * vertex[0] - math.sin(angle) * vertex[1],
               offset[1] + math.sin(angle) * vertex[0] + math.cos(angle) * vertex[1] ]
           for vertex in vertexList]

# Trims a polygon flush around the given vertices
def trimFlushPolygonAtVertices(path, vertexList, vertexSlopes, extent):
    trimRect = [ [0, -extent], [0, 0], [0, extent], [-extent, extent], [-extent, -extent] ]
    trimPolys = [transformVertices(trimRect, vertexPos, vertexSlope)
        for vertexPos, vertexSlope in zip(vertexList, vertexSlopes)]
    return clipPolygonWithPolygons(path, trimPolys)


######################
def generateViaFence(pathList, viaOffset, viaPitch):
    viaPoints = []

    # Expand the paths given as a parameter into one or more polygons
    # using the offset parameter
    offsetPaths = expandPathsToPolygons(pathList, viaOffset)
    for offsetPath in offsetPaths:
        # Filter the input path to only include paths inside this polygon
        # Find all leaf vertices and use them to trim the expanded polygon
        # around the leaf vertices so that we get a flush, flat end
        # These butt lines are then found using the leaf vertices
        # and used to split open the polygon into multiple separate open
        # paths that envelop the original path
        localPathList = getPathsInsidePolygon(pathList, offsetPath)
        leafVertexList, leafVertexAngles = getLeafVertices(localPathList)
        offsetPath = trimFlushPolygonAtVertices(offsetPath, leafVertexList, leafVertexAngles, 1.5*viaOffset)[0]
        buttLineIdxList = getPathsThroughPoints(offsetPath, leafVertexList)
        fencePaths = splitPathByPaths(offsetPath, buttLineIdxList)

        # With the now separated open paths we perform via placement on each one of them
        for fencePath in fencePaths:
            # For a nice via fence placement, we identify vertices that differ from a straight
            # line by more than 10 degrees so we find all non-arc edges
            # We combine these points with the start and end point of the path and use
            # them to place fixed vias on their positions
            fixPointIdxList = [0] + getPathVertices(fencePath, 10) + [-1]
            viaPoints += [fencePath[idx] for idx in fixPointIdxList]

            # Then we autoplace vias between the fixed via locations by satisfying the
            # minimum via pitch given by the user
            for subPath in splitPathByPoints(fencePath, fixPointIdxList):
                viaPoints += distributeAlongPath(subPath, viaPitch)

    return viaPoints


import json
import matplotlib.pyplot as plt
import numpy as np

if __name__ == "__main__":
    # Load test dataset
    datasetFile = 'via-fence-generator-test.json'

    with open(datasetFile, 'rb') as file:
        dict = json.load(file)
    viaOffset = dict['viaOffset']
    viaPitch = dict['viaPitch']
    pathList = dict['pathList']

    for path in pathList:
        plt.plot(np.array(path).T[0], np.array(path).T[1], linewidth=5)


    viaPoints = generateViaFence(pathList, viaOffset, viaPitch)

    with open(datasetFile, 'wb') as file:
        dict = {'pathList': pathList, 'viaOffset': viaOffset, 'viaPitch': viaPitch, 'viaPoints': viaPoints}
        json.dump(dict, file, indent=4)


    for via in viaPoints:
        plt.plot(via[0], via[1], 'o', markersize=10)

    plt.axes().set_aspect('equal','box')
#    plt.xlim(0, 6000)
#    plt.ylim(0, 8000)
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
        viaOffset = pcbnew.FromMM(0.5)
        viaPitch =  pcbnew.FromMM(1)
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

