from .viafence import *
import argparse

argParser = argparse.ArgumentParser()
argParser.add_argument("--dialog",      dest="dialog",      metavar="DIALOGNAME", help="Show Dialog with <DIALOGNAME>")
argParser.add_argument("--runtests",    dest="runtests",    action="store_true", default=0, help="Execute testing all json test files in 'tests' subdirectory")
argParser.add_argument("--test",        dest="test",        metavar="TESTNAME", help="Loads <TESTNAME> from 'tests' directory, runs it and shows/stores the result into the test file")

args = argParser.parse_args()

if (args.dialog):
    # Load and show dialog
    import wx
    import os
    from .viafence_dialogs import *
    os.chdir(os.path.dirname(os.path.realpath(__file__)))
    app = wx.App()
    className = globals()[args.dialog]
    className(None).Show()
    app.MainLoop()

elif (args.test):
    # Load a test file, run the algorithm and show/store the result for later testing
    import os
    import json
    import matplotlib.pyplot as plt
    import numpy as np

    testFile = args.test
    scriptDir = os.path.dirname(os.path.realpath(__file__))
    testDir = scriptDir + "/" + 'tests'

    with open(testDir+"/"+testFile+".json", 'r') as file:
        dict = json.load(file)

    viaOffset = dict['viaOffset']
    viaPitch = dict['viaPitch']
    pathList = dict['pathList']

    viaPoints = generateViaFence(pathList, viaOffset, viaPitch)

    with open(testDir+"/"+testFile+".json", 'w') as file:
        dict = {'pathList': pathList, 'viaOffset': viaOffset, 'viaPitch': viaPitch, 'viaPoints': viaPoints}
        json.dump(dict, file, indent=4)


    for path in pathList:
        plt.plot(np.array(path).T[0], np.array(path).T[1], linewidth=5)

    for via in viaPoints:
        plt.plot(via[0], via[1], 'o', markersize=10)

    plt.axes().set_aspect('equal','box')
    plt.ylim(plt.ylim()[::-1])
    plt.savefig(testDir+"/"+testFile+'.png')
    plt.show()
elif (args.runtests):
    # Run all tests in 'tests' subdirectory
    import os
    import json
    scriptDir = os.path.dirname(os.path.realpath(__file__))
    testDir = scriptDir + "/" + 'tests'
    testsPassed = 0
    testsTotal = 0

    for file in os.listdir(testDir):
        if file.endswith(".json"):
            with open(testDir+"/"+file, 'r') as file:
                dict = json.load(file)

            viaOffset = dict['viaOffset']
            viaPitch = dict['viaPitch']
            viaPoints = dict['viaPoints']
            pathList = dict['pathList']

            testViaPoints = generateViaFence(pathList, viaOffset, viaPitch)
            matched = [via for via in testViaPoints if via in viaPoints]
            hasPassed = True if len(testViaPoints) == len(viaPoints) == len(matched) else False
            passed = "PASSED" if hasPassed else "FAILED"
            print("{}: {} ({} Vias generated)".format(os.path.basename(file.name), passed, len(testViaPoints)))

            if hasPassed: testsPassed += 1
            testsTotal += 1

    print("----\n{}/{} tests PASSED".format(testsPassed, testsTotal))

    assert testsPassed == testsTotal

    if testsPassed == testsTotal: exit(0) 
    else: exit(1)
