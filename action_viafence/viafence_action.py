# Implementation of the action plugin derived from pcbnew.ActionPlugin
import pcbnew
import os
import sys
import re
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

    def getNetTracks(self, netId):
        netTracks = self.boardObj.TracksInNet(netId)
        return [ [[t.GetStart()[0], t.GetStart()[1]], [t.GetEnd()[0], t.GetEnd()[1]]] for t in netTracks ]

    def createNetFilterSuggestions(self):
        netList = [self.netMap[item].GetNetname() for item in self.netMap]
        netFilterList = ['*']
        diffMap = {'+': '-', 'P': 'N', '-': '+', 'N': 'P'}
        regexMap = {'+': '[+-]', '-': '[+-]', 'P': '[PN]', 'N': '[PN]'}
        invertDiffNet = lambda netName : netName[0:-1] + diffMap[netName[-1]]
        isDiffNet = lambda netName : True if netName[-1] in diffMap.keys() else False

        # Translate board nets into a filter list
        for netName in netList:
            if isDiffNet(netName) and invertDiffNet(netName) in netList:
                # If we have a +/- or P/N pair, we insert a regex entry once into the filter list
                filterText = netName[0:-1] + regexMap[netName[-1]]
                if (filterText not in netFilterList): netFilterList += [filterText] 

            netFilterList += [netName]

        return netFilterList

    def Run(self):
        self.prevcwd = os.getcwd()
        os.chdir(os.path.dirname(os.path.realpath(__file__)))

        self.boardObj = pcbnew.GetBoard()
        self.boardDesignSettingsObj = self.boardObj.GetDesignSettings()
        self.layerTable = self.getLayerTable()
        self.highlightedNetId = self.boardObj.GetHighLightNetCode()
        self.netMap = self.getNetMap()
        self.netFilterList = self.createNetFilterSuggestions()
        self.netFilter = self.netMap[self.highlightedNetId].GetNetname() if self.highlightedNetId != -1 else self.netFilterList[0]
        self.viaSize = self.boardDesignSettingsObj.GetCurrentViaSize()
        self.layerId = 0 #TODO: How to get currently selected layer?
        self.viaDrill = self.boardDesignSettingsObj.GetCurrentViaDrill()
        self.viaPitch = pcbnew.FromMM(1)
        self.viaOffset = pcbnew.FromMM(0.5)
        self.viaNet = "GND"
        self.isNetFilterChecked = 1
        self.isLayerChecked = 0
        self.isIncludeDrawingChecked = 0

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
        mainDlg.chkIncludeDrawing.SetValue(self.isIncludeDrawingChecked)

        if (mainDlg.ShowModal() == wx.ID_OK):
            self.netFilter = mainDlg.txtNetFilter.GetValue()
            self.layerId = mainDlg.lstLayer.GetSelection()
            self.viaOffset = pcbnew.FromMM(float(mainDlg.txtViaOffset.GetValue()))
            self.viaPitch = pcbnew.FromMM(float(mainDlg.txtViaPitch.GetValue()))
            self.viaDrill = pcbnew.FromMM(float(mainDlg.txtViaDrill.GetValue()))
            self.viaSize = pcbnew.FromMM(float(mainDlg.txtViaSize.GetValue()))
            self.viaNet = mainDlg.txtViaNet.GetValue()
            self.isNetFilterChecked = mainDlg.chkNetFilter.GetValue()
            self.isLayerChecked = mainDlg.chkLayer.GetValue()
            self.isIncludeDrawingChecked = mainDlg.chkIncludeDrawing.GetValue()

            # Assemble a list of pcbnew.BOARD_ITEMs that support GetStart/GetEnd and IsOnLayer
            trackObjects = []

            if (self.isNetFilterChecked):
                # Escape the entire filter string. Unescape and remap specific characters that we want to allow
                subsTable = {r'\[':'[', r'\]':']', r'\*':'.*'}
                netRegex = re.escape(self.netFilter)
                for subsFrom, subsTo in subsTable.items(): netRegex = netRegex.replace(subsFrom, subsTo)

                # Find nets that match the generated regular expression and add their tracks to the list
                for netId in self.netMap:
                    if re.match(netRegex, self.netMap[netId].GetNetname()):
                        for trackObject in self.boardObj.TracksInNet(netId):
                            trackObjects += [trackObject]

            if (self.isIncludeDrawingChecked):
                boardItem = self.boardObj.GetDrawings().GetFirst()
                while boardItem is not None:
                    if pcbnew.DRAWSEGMENT.ClassOf(boardItem):
                        # A drawing segment (not a text or something else)
                        drawingObj = boardItem.Cast()
                        if drawingObj.GetShape() == pcbnew.S_SEGMENT:
                            # A straight line
                            trackObjects += [drawingObj]

                    boardItem = boardItem.Next()


            if (self.isLayerChecked):
                # Filter by layer
                # TODO: Make layer selection also a regex
                trackObjects = [trackObject for trackObject in trackObjects if trackObject.IsOnLayer(self.layerId)]

            # Generate a track list from the board objects
            trackList = [[ [trackObject.GetStart()[0], trackObject.GetStart()[1]],
                           [trackObject.GetEnd()[0],   trackObject.GetEnd()[1]]   ]
                           for trackObject in trackObjects]

            viaPoints = generateViaFence(trackList, self.viaOffset, self.viaPitch)

            import numpy as np
            import matplotlib.pyplot as plt

            for track in trackList:
                plt.plot(np.array(track).T[0], np.array(track).T[1], linewidth=2)
            for via in viaPoints:
                plt.plot(via[0], via[1], 'o', markersize=10)


            plt.ylim(plt.ylim()[::-1])
            plt.axes().set_aspect('equal','box')
        #    plt.xlim(0, 6000)
        #    plt.ylim(0, 8000)
            plt.show()


            # TODO: Filter generated vias? (colliding vias, vias not in ground plane?)


        os.chdir(self.prevcwd)
