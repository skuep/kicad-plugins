#!/usr/bin/env python2
import math
import pyclipper
from bisect import bisect_left

# Return a sub path from start index to end index using increasing indices only
# When endIdx is smaller then startIdx, len(path) will be added causing traversing
# a round trip in the list instead of reversing it (python list default)
def getSubPath(path, startIdx, endIdx):
    listModulus = len(path)
    if (endIdx < startIdx): endIdx += listModulus
    return [path[i % listModulus] for i in range(startIdx, endIdx+1)]

# Split a path at specific indices
def splitPath(path, splitIdxList):
    # Test splitIdxList wheter we use points or lines to split the path
    if type(splitIdxList[0]) == int:
        # We got a list of points for split operation
        idxSkip = 1
    elif type(splitIdxList[0]) == list:
        # We got a list of lines for split operation
        # Flatten the list and shift by one
        splitIdxList = [item for sublist in splitIdxList for item in sublist]
        splitIdxList = splitIdxList[1:] + splitIdxList[:1]
        idxSkip = 2

    # Generate subpaths by dividing the original path at split indices
    subPaths = []
    for splitIdxListIdx in range(0, len(splitIdxList)-1, idxSkip):
        start = splitIdxList[splitIdxListIdx]
        end = splitIdxList[splitIdxListIdx+1]
        subPaths += [getSubPath(path, start, end)]

    return subPaths

# Return a cumulative distance vector representing the distance travelled along
# the path at each path vertex
def getPathCumDist(path):
    previousVertex = path[0]
    cumDist = []
    distanceSum = 0.0

    for vertex in path:
        # calculate distance to previous vertex using pythagoras
        # sum up the new distance to the previous distance and store into vector
        distanceSum += math.hypot(vertex[0] - previousVertex[0], vertex[1] - previousVertex[1])
        cumDist += [distanceSum]
        previousVertex = vertex

    return cumDist

# Return a list of all vertex indices whose angle between connecting
# lines are within angleMin and angleMax in degrees
# This could be used to find vertices with acute angles for example
def getPathVertices(pathList, angleMin=0, angleMax=360):
    angleMin = angleMin * math.pi / 180
    angleMax = angleMax * math.pi / 180
    vertices = []

    # Look through all vertices except start and end vertex
    # Find the angle of the connecting lines of the vertex
    # And if it is satisfying the angle specification, store it
    for vertexIdx in range(1, len(pathList)-1):
        # Reduce three points to two position vectors (points)
        # Calculate dot product and line lengths and use them to calculate the angle
        ptA = [a-b for a,b in zip(pathList[vertexIdx-1], pathList[vertexIdx])]
        ptB = [a-b for a,b in zip(pathList[vertexIdx+1], pathList[vertexIdx])]

        dot = ptA[0] * ptB[0] + ptA[1] * ptB[1]
        lenA = math.hypot(ptA[0], ptA[1])
        lenB = math.hypot(ptB[0], ptB[1])
        angle = math.acos(dot/(lenA*lenB))

        if (angle >= angleMin) and (angle < angleMax):
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

# Returns a list of paths touching any item in a list of points
def getPathsTouchingPoints(path, pointList):
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

# Distribute Points along a path with equal spacing to each other
# When the path length is not evenly dividable by the minimumSpacing,
# the actual spacing will be larger, but still smaller than 2*minimumSpacing
# The function does not return the start and end vertex of the path
def distributeAlongPath(path, minimumSpacing):
    # Get cumulated distance vector for the path
    # and determine the number of points that can fit to the path
    # determine the final pitch by dividing the total path length
    # by the rounded down number of points
    fenceDistances = getPathCumDist(path)
    numberOfPoints = int(math.floor(fenceDistances[-1] / minimumSpacing))
    pointInterpolator = PathInterpolator(fenceDistances, path)
    pointPitch = fenceDistances[-1] / numberOfPoints
    points = []

    for pointIdx in range(1, numberOfPoints):
        points += [pointInterpolator(pointIdx*pointPitch)]

    return points

######################
def generateViaFence(tracks, viaOffset, viaPitch):
    # Use PyclipperOffset to generate a polygon that surrounds the original
    # paths with a constant offset all around
    co = pyclipper.PyclipperOffset()
    co.AddPaths(tracks, pyclipper.JT_ROUND, pyclipper.ET_OPENBUTT)
    offsetTrack = co.Execute(viaOffset)[0]

    # Since PyclipperOffset returns a closed path, we need to find
    # the butt lines in this closed path, i.e. the lines that are
    # perpendicular to the original tracks' start and end points
    # First collect all the start and end vertices of all input paths
    # Then check if any of those vertices are located on any of
    # the polygon line segments
    # If this is the case, we consider them a butt line
    leafVertexList = [track[idx] for idx in [0, -1] for track in tracks]
    buttLineIdxList = getPathsTouchingPoints(offsetTrack, leafVertexList)

    # The butt lines are used to split up the closed polygon into multiple
    # separate open paths to the left and the right of the original tracks
    fencePaths = splitPath(offsetTrack, buttLineIdxList)
    viaPoints = []

    # With the now separated open paths we perform via placement on each one of them
    for fencePath in fencePaths:
        # For a nice via fence placement, we find vertices having an included angle
        # satisfying a defined specification. This way non-smooth (i.e. non-arcs) are
        # identified in the fence path. We use these to place fixed vias on their positions
        # We also use start and end vertices of the fence path as fixed via locations
        fixPointIdxList = [0] + getPathVertices(fencePath, 0, 170) + [-1]
        viaPoints += [fencePath[idx] for idx in fixPointIdxList]

        # Then we autoplace vias between the fixed via locations by satisfying the
        # minimum via pitch given by the user
        for subPath in splitPath(fencePath, fixPointIdxList):
            # Now equally space the vias along the subpath using the given minimum pitch
            # Add the generated vias to the list
            viaPoints += distributeAlongPath(subPath, viaPitch)

    return viaPoints

if __name__ == "__main__":
    # Set some via parameters
    # generate some test paths and run
    viaOffset = 500
    viaPitch = 300

    tracks = [ [ [1000, 1000], [3000, 3000], [5000, 3000], [5000, 5000], [3000, 7000], [5000, 7000] ],
                [ [3000, 3000], [2000, 5000], [1000, 5000] ] ]

    viaPoints = generateViaFence(tracks, viaOffset, viaPitch)


    # This is just for plotting stuff
    import matplotlib.pyplot as plt
    import numpy as np

    def plotPaths(pathList, **kwargs):
        for path in pathList:
            plt.plot(np.array(path).T[0], np.array(path).T[1], **kwargs)
            plt.plot(path[0][0], path[0][1], '+', **kwargs)
            plt.plot(path[-1][0], path[-1][1], 'x', **kwargs)

    def plotPoints(points, **kwargs):
        plt.plot(np.array(points).T[0], np.array(points).T[1], 'o', **kwargs)



    # plot the result
    plotPaths(tracks, linewidth=5, markersize=10, markeredgewidth=2)
    plotPoints(viaPoints, markersize=10)

    plt.axes().set_aspect('equal','box')
    plt.xlim(0, 6000)
    plt.ylim(0, 8000)
    plt.savefig('via-fence-generator.png')
    plt.show()
