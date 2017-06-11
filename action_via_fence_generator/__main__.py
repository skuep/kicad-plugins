from .via_fence import *
import os
import json
import matplotlib.pyplot as plt
import numpy as np

# Load test dataset
scriptDir = os.path.dirname(os.path.realpath(__file__))
testDir = scriptDir + "/" + 'tests'
datasetFile = 'simple-test'

with open(testDir+"/"+datasetFile+".json", 'r') as file:
    dict = json.load(file)
viaOffset = dict['viaOffset']
viaPitch = dict['viaPitch']
pathList = dict['pathList']

for path in pathList:
    plt.plot(np.array(path).T[0], np.array(path).T[1], linewidth=5)


viaPoints = generateViaFence(pathList, viaOffset, viaPitch)

with open(testDir+"/"+datasetFile+".json", 'w') as file:
    dict = {'pathList': pathList, 'viaOffset': viaOffset, 'viaPitch': viaPitch, 'viaPoints': viaPoints}
    json.dump(dict, file, indent=4)

for via in viaPoints:
    plt.plot(via[0], via[1], 'o', markersize=10)

plt.axes().set_aspect('equal','box')
#    plt.xlim(0, 6000)
#    plt.ylim(0, 8000)
plt.ylim(plt.ylim()[::-1])
plt.savefig(testDir+"/"+datasetFile+'.png')
plt.show()


