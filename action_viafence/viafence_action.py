# Implementation of the action plugin derived from pcbnew.ActionPlugin
import pcbnew
import matplotlib.pyplot as plt
import numpy as np
import os
import sys
from collections import OrderedDict
from .viafence import *
from .viafence_dialogs import *

class MainDialog(MainDialogBase):
    def __init__(self, parent):
        MainDialogBase.__init__(self, parent)

    def OnNetFilterCheckBox(self, event):
        self.txtNetFilter.Enable(event.IsChecked())

    def OnLayerCheckBox(self, event):
        self.lstLayer.Enable(event.IsChecked())


class ViaFenceAction(pcbnew.ActionPlugin):
    def defaults(self):
        self.name = "Via Fence Generator"
        self.category = "Modify PCB"
        self.description = "Add a via fence to nets or tracks on the board"


    def getLayerTable(self):
        layerTable = []
        for i in range(pcbnew.PCB_LAYER_ID_COUNT):
            layerTable += [self.boardObj.GetLayerName(i)]

        return layerTable

    def getNetMap(self):
        netMap = OrderedDict(self.boardObj.GetNetsByNetcode())
        netMap.pop(0) # TODO: What is Net 0?
        return netMap

    def createNetFilterList(self):
        # TODO Generate Wildcard object from differential traces
        netFilterList = ['*'] + [self.netMap[item].GetNetname() for item in self.netMap]

        return netFilterList

    def Run(self):
        self.prevcwd = os.getcwd()
        os.chdir(os.path.dirname(os.path.realpath(__file__)))

        self.boardObj = pcbnew.GetBoard()
        self.boardDesignSettingsObj = self.boardObj.GetDesignSettings()
        self.layerTable = self.getLayerTable()
        self.highlightedNetId = self.boardObj.GetHighLightNetCode()
        self.netMap = self.getNetMap()
        self.netFilterList = self.createNetFilterList()
        self.netFilter = self.netMap[self.highlightedNetId].GetNetname() if self.highlightedNetId != -1 else self.netFilterList[0]
        self.viaSize = self.boardDesignSettingsObj.GetCurrentViaSize()
        self.layerId = 0 #TODO: How to get currently selected layer?
        self.viaDrill = self.boardDesignSettingsObj.GetCurrentViaDrill()
        self.viaPitch = pcbnew.FromMM(1)
        self.viaOffset = pcbnew.FromMM(0.5)
        self.viaNet = "GND"
        self.isNetFilterChecked = 1
        self.isLayerChecked = 0
        self.isIncludeLinesPolygonsChecked = 0

        mainDlg = MainDialog(None)
        mainDlg.lstLayer.SetItems(self.layerTable)
        mainDlg.lstLayer.SetSelection(self.layerId)
        mainDlg.txtNetFilter.SetItems(self.netFilterList)
        mainDlg.txtNetFilter.SetSelection(self.netFilterList.index(self.netFilter))
        mainDlg.txtViaOffset.SetValue(str(pcbnew.ToMM(self.viaOffset)))
        mainDlg.txtViaPitch.SetValue(str(pcbnew.ToMM(self.viaPitch)))
        mainDlg.txtViaDrill.SetValue(str(pcbnew.ToMM(self.viaDrill)))
        mainDlg.txtViaSize.SetValue(str(pcbnew.ToMM(self.viaSize)))
        mainDlg.txtViaNet.SetValue(self.viaNet)
        mainDlg.chkNetFilter.SetValue(self.isNetFilterChecked)
        mainDlg.txtNetFilter.Enable(self.isNetFilterChecked)
        mainDlg.chkLayer.SetValue(self.isLayerChecked)
        mainDlg.lstLayer.Enable(self.isLayerChecked)
        mainDlg.chkIncludeLinesPolygons.SetValue(self.isIncludeLinesPolygonsChecked)

        if (mainDlg.ShowModal() == wx.ID_OK):
            self.netFilter = mainDlg.txtNetFilter.GetValue()
            self.layerId = mainDlg.lstLayer.GetPosition()
            self.viaOffset = pcbnew.FromMM(float(mainDlg.txtViaOffset.GetValue()))
            self.viaPitch = pcbnew.FromMM(float(mainDlg.txtViaPitch.GetValue()))
            self.viaDrill = pcbnew.FromMM(float(mainDlg.txtViaDrill.GetValue()))
            self.viaSize = pcbnew.FromMM(float(mainDlg.txtViaSize.GetValue()))
            self.viaNet = mainDlg.txtViaNet.GetValue()
            self.isNetFilterChecked = mainDlg.chkNetFilter.GetValue()
            self.isLayerChecked = mainDlg.chkLayer.GetValue()
            self.isIncludeLinesPolygonsChecked = mainDlg.chkIncludeLinesPolygons.GetValue()

            # TODO: Grab all the tracks according to dialog settings

            # TODO: Start Via Generation

            # TODO: Filter generated vias? (colliding vias, vias not in ground plane?)

#        if (netId != -1):
#            netTracks = pcbObj.TracksInNet(netId)
#            trackList = [ [[t.GetStart()[0], t.GetStart()[1]], [t.GetEnd()[0], t.GetEnd()[1]]] for t in netTracks ]


#            viaPoints = generateViaFence(trackList, viaOffset, viaPitch)


#            for track in trackList:
#                plt.plot(np.array(track).T[0], np.array(track).T[1], linewidth=1)
#            for via in viaPoints:
#                plt.plot(via[0], via[1], 'o', markersize=10)


#            plt.ylim(plt.ylim()[::-1])
#            plt.axes().set_aspect('equal','box')
        #    plt.xlim(0, 6000)
        #    plt.ylim(0, 8000)
#            plt.show()



        os.chdir(self.prevcwd)
