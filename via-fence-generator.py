#!/usr/bin/env python2

import pyclipper
import matplotlib.pyplot as plt
import numpy as np

from math import *

def plotPath(path, **kwargs):
    plt.plot(np.array(path).T[0], np.array(path).T[1], **kwargs)
    plt.plot(path[0][0], path[0][1], '+')
    plt.plot(path[-1][0], path[-1][1], 'x')

def plotPoints(points, **kwargs):
    plt.plot(np.array(points).T[0], np.array(points).T[1], 'o', **kwargs)

# Uses the cross product to check if a point is on a line defined by two other points
def isPointOnLine(point, line):
    cross = (line[1][1] - point[1]) * (line[0][0] - point[0]) - (line[1][0] - point[0]) * (line[0][1] - point[1])
    if abs(cross) != 0: return False 
    return True

# Return a sub path from start index to end index using increasing indices only
# When endIdx is smaller then startIdx, len(path) will be added causing traversing
# a full round trip in the list instead of reversing it (python list default)
def getSubPath(pathList, startIdx, endIdx):
    listModulus = len(pathList)
    if (endIdx < startIdx): endIdx += listModulus
    return [pathList[i % listModulus] for i in range(startIdx, endIdx+1)]

# Return a cumulative distance vector representing the distance travelled along
# the path at each path vertex
def getPathCumDist(pathList):
    previousVertex = pathList[0]
    cumDist = []
    distanceSum = 0.0

    for vertex in pathList:
        # calculate distance to previous vertex using pythagoras
        # sum up the new distance to the previous distance and store into vector
        distance = sqrt(pow(vertex[0] - previousVertex[0], 2) + pow(vertex[1] - previousVertex[1], 2))
        distanceSum += distance
        cumDist += [distanceSum]
        previousVertex = vertex

    return cumDist

# Return a list of all vertex indices whose angle between connecting
# lines are within angleMin and angleMax in degrees
# This could be used to find vertices with acute angles for example
def getPathVertices(pathList, angleMin=0, angleMax=360):
    angleMin = angleMin * pi / 180
    angleMax = angleMax * pi / 180
    vertices = []

    # Look through all vertices except start and end vertex
    # Find the angle of the connecting lines of the vertex
    # And if it is satisfying the angle specification, store it
    for vertexIdx in range(1, len(pathList)-1):
        # Make two root vectors
        ptA = [a-b for a,b in zip(pathList[vertexIdx-1], pathList[vertexIdx])]
        ptB = [a-b for a,b in zip(pathList[vertexIdx+1], pathList[vertexIdx])]

        dot = ptA[0] * ptB[0] + ptA[1] * ptB[1]
        lenA = hypot(ptA[0], ptA[1])
        lenB = hypot(ptB[0], ptB[1])

        angle = acos(dot/(lenA*lenB))

        if (angle >= angleMin) and (angle < angleMax):
            vertices += [vertexIdx]

    return vertices

# A small linear interpolation class so we don't rely on scipy or numpy here
from bisect import bisect_left
class LinearInterpolator(object):
    def __init__(self, x_list, y_list):
        if any(y - x <= 0 for x, y in zip(x_list, x_list[1:])):
            raise ValueError("x_list must be in strictly ascending order!")
        x_list = self.x_list = map(float, x_list)
        y_list = self.y_list = map(float, y_list)
        intervals = zip(x_list, x_list[1:], y_list, y_list[1:])
        self.slopes = [(y2 - y1)/(x2 - x1) for x1, x2, y1, y2 in intervals]

    def __call__(self, x):
        i = bisect_left(self.x_list, x) - 1
        return self.y_list[i] + self.slopes[i] * (x - self.x_list[i])

# Interpolate a path with (x,y) vertices using a third parameter t
class PathInterpolator:
    def __init__(self, t, path):
        # Quick and dirty transpose path so we get two list with x and y coords
        x = [vertex[0] for vertex in path]
        y = [vertex[1] for vertex in path]

        # Set up two separate interpolators
        self.xInterp = LinearInterpolator(t, x)
        self.yInterp = LinearInterpolator(t, y)

    def __call__(self, t):
        # Return interpolated coordinates on the original path
        return [self.xInterp(t), self.yInterp(t)]

def distributeAlongPath(path, minimumSpacing):
    fenceDistances = getPathCumDist(path)
    numberOfPoints = int(floor(fenceDistances[-1] / minimumSpacing))
    pointInterpolator = PathInterpolator(fenceDistances, path)
    pointPitch = fenceDistances[-1] / numberOfPoints
    points = []

    for pointIdx in range(1, numberOfPoints):
        points += [pointInterpolator(pointIdx*pointPitch)]

    return points

######################


def generateViaFence(track, viaOffset, viaPitch):

    # Use PyclipperOffset to generate a polygon that surrounds the original
    # path with a constant offset all around
    co = pyclipper.PyclipperOffset()
    co.AddPath(track, pyclipper.JT_ROUND, pyclipper.ET_OPENBUTT)
    offsetTrack = co.Execute(viaOffset)[0]

    # Since PyclipperOffset returns a closed path, we need to find
    # the butt lines in this closed path, i.e. the lines that are
    # perpendicular to the original track's start and end point
    buttLineIdx = []

    for vertexIdx in range(0, len(offsetTrack)-1):
        # This is the current line segment
        line = ( offsetTrack[vertexIdx], offsetTrack[vertexIdx+1] )

        # If start or end point of the original track are exactly colinear to the current
        # offseted line segment, we consider it a butt line and store the indices
        if isPointOnLine(track[0], line) or isPointOnLine(track[-1], line):
            buttLineIdx += [vertexIdx, vertexIdx+1]

    # When using a single input path, only two butt lines should (tm) have been
    # found, since a single input path only has two end points
    # The butt lines are then used to split up the offseted polygon into two
    # separate open paths to the left and the right of the original track
    # For easier processing, we shift the found indices by one, so index[0]
    # directly corresponds to the start of the first path
    buttLineIdx = buttLineIdx[1:] + buttLineIdx[:1]
    fencePaths = [  getSubPath(offsetTrack, buttLineIdx[0], buttLineIdx[1]),
                    getSubPath(offsetTrack, buttLineIdx[2], buttLineIdx[3]) ]


    viaPoints = []

    for fencePath in fencePaths:
        # For a nice via fence placement, we try to find non-smooth kinks in the fence path
        # and use these to place fixed vias that cannot be moved
        # Also use start and end vertices of the fence path as fixed via locations
        fixPointIdxList = [0] + getPathVertices(fencePath, 0, 170) + [-1]
        fixViaPoints = [fencePath[idx] for idx in fixPointIdxList]

        viaPoints += fixViaPoints

        for fixPointIdxIdx in range(0, len(fixPointIdxList)-1):
            # Generate subpaths from the fence path between the fixed via positions
            fixPointIdxStart = fixPointIdxList[fixPointIdxIdx]
            fixPointIdxEnd = fixPointIdxList[fixPointIdxIdx+1]
            subPath = getSubPath(fencePath, fixPointIdxStart, fixPointIdxEnd)

            # Now equally space the vias along the subpath using the given minimum pitch
            # Add the generated vias to the list
            generatedViaPoints = distributeAlongPath(subPath, viaPitch)
            viaPoints += generatedViaPoints

    return viaPoints

if __name__ == "__main__":
    # Set some via parameters
    # generate a test path and run
    viaOffset = 500
    viaPitch = 300

    track = ( (1000, 1000), (3000, 3000), (5000, 3000), (5000, 5000), (3000, 7000), (5000, 7000) )

    viaPoints = generateViaFence(track, viaOffset, viaPitch)

    # plot the result
    plotPath(track)
    plotPoints(viaPoints)

    plt.axes().set_aspect('equal','box')
    plt.xlim(0, 6000)
    plt.ylim(0, 8000)
    plt.savefig('via-fence-generator.png')
    plt.show()
