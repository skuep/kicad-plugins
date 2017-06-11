# Implementation of the action plugin derived from pcbnew.ActionPlugin
import pcbnew
import matplotlib.pyplot as plt
import numpy as np

from .via_fence import *

class ActionViaFenceGenerator(pcbnew.ActionPlugin):
    def defaults(self):
        self.name = "Via Fence Generator"
        self.category = "Modify PCB"
        self.description = "Add a via fence to nets or tracks on the board"

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


