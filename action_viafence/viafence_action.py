# Implementation of the action plugin derived from pcbnew.ActionPlugin
import pcbnew
import os
import sys
import re
import time
import json
from collections import OrderedDict
from .viafence import *
from .viafence_dialogs import *


class ViaFenceAction(pcbnew.ActionPlugin):
    # ActionPlugin descriptive information
    def defaults(self):
        self.name = "Via Fence Generator"
        self.category = "Modify PCB"
        self.description = "Add a via fence to nets or tracks on the board"
        self.icon_file_name = os.path.join(os.path.dirname(__file__), "resources/fencing-vias.png")
        self.show_toolbar_button = True

    def dumpJSON(self, file):
        dict = {
            'pathList': self.pathList, 
            'viaOffset': self.viaOffset, 
            'viaPitch': self.viaPitch, 
            'viaPoints': self.viaPoints if hasattr(self, 'viaPoints') else []
        }
        with open(file, 'w') as file:
            json.dump(dict, file, indent=4, sort_keys=True)

    # Return an ordered {layerId: layerName} dict of enabled layers
    def getLayerMap(self):
        layerMap = []
        for i in list(range(pcbnew.PCB_LAYER_ID_COUNT)):
            #wx.LogMessage(str(i))
            #wx.LogMessage(str(self.boardObj.IsLayerEnabled(i)))
            if self.boardObj.IsLayerEnabled(i):
                layerMap += [[i, self.boardObj.GetLayerName(i)]]
                #layerMap.append([i, self.boardObj.GetLayerName(i)])
        #wx.LogMessage(str(layerMap))
        #od = OrderedDict(layerMap)
        #wx.LogMessage(str(od))
        return OrderedDict(layerMap)

    # Return an ordered {netCode: netName} dict of nets in the board
    def getNetMap(self):
        netMap = OrderedDict(self.boardObj.GetNetsByNetcode())
        netMap.pop(0) # TODO: What is Net 0?
        return netMap

    # Generates a list of net filter phrases using the local netMap
    # Currently all nets are included as filter phrases
    # Additionally, differential Nets get a special filter phrase
    def createNetFilterSuggestions(self):
        netFilterList = ['*']
        netList = [self.netMap[item].GetNetname() for item in self.netMap]
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

            # Append every net to the filter list
            netFilterList += [netName]

        return netFilterList

    # Generates a RegEx string from a SimpleEx (which is a proprietary invention ;-))
    # The SimpleEx only supports [...] with single chars and * used as a wildcard
    def regExFromSimpleEx(self, simpleEx):
        # Escape the entire filter string. Unescape and remap specific characters that we want to allow
        subsTable = {r'\[':'[', r'\]':']', r'\*':'.*'}
        regEx = re.escape(simpleEx)
        for subsFrom, subsTo in subsTable.items(): regEx = regEx.replace(subsFrom, subsTo)
        return regEx

    def createVias(self, viaPoints, viaDrill, viaSize, netCode):
        newVias = []
        for viaPoint in viaPoints:
            newVia = pcbnew.VIA(self.boardObj)
            self.boardObj.Add(newVia)

            newVia.SetPosition(pcbnew.wxPoint(viaPoint[0], viaPoint[1]))
            newVia.SetWidth(viaSize)
            newVia.SetDrill(viaDrill)
            newVia.SetViaType(pcbnew.VIA_THROUGH)
            newVia.SetNetCode(netCode)
            newVias += [newVia]

        return newVias

    def selfToMainDialog(self):
        #wx.LogMessage(str(self.layerMap.values()))
        #wx.LogMessage(str(list(self.layerMap.values())))
        self.mainDlg.lstLayer.SetItems(list(self.layerMap.values()))  #maui
        self.mainDlg.lstLayer.SetSelection(self.layerId)
        self.mainDlg.txtNetFilter.SetItems(self.netFilterList)
        self.mainDlg.txtNetFilter.SetSelection(self.netFilterList.index(self.netFilter))
        self.mainDlg.txtViaOffset.SetValue(str(pcbnew.ToMM(self.viaOffset)))
        self.mainDlg.txtViaPitch.SetValue(str(pcbnew.ToMM(self.viaPitch)))
        self.mainDlg.txtViaDrill.SetValue(str(pcbnew.ToMM(self.viaDrill)))
        self.mainDlg.txtViaSize.SetValue(str(pcbnew.ToMM(self.viaSize)))
        self.mainDlg.lstViaNet.SetItems([item.GetNetname() for item in self.netMap.values()])
        self.mainDlg.lstViaNet.SetSelection(0)
        self.mainDlg.chkNetFilter.SetValue(self.isNetFilterChecked)
        self.mainDlg.txtNetFilter.Enable(self.isNetFilterChecked)
        self.mainDlg.chkLayer.SetValue(self.isLayerChecked)
        self.mainDlg.lstLayer.Enable(self.isLayerChecked)
        self.mainDlg.chkIncludeDrawing.SetValue(self.isIncludeDrawingChecked)
        self.mainDlg.chkDebugDump.SetValue(self.isDebugDumpChecked)
        self.mainDlg.chkRemoveViasWithClearanceViolation.SetValue(self.isRemoveViasWithClearanceViolationChecked)
        self.mainDlg.chkSameNetZoneViasOnly.SetValue(self.isSameNetZoneViasOnlyChecked)

    def mainDialogToSelf(self):
        self.netFilter = self.mainDlg.txtNetFilter.GetValue()
        self.layerId = list(self.layerMap.keys())[self.mainDlg.lstLayer.GetSelection()]   #maui
        self.viaOffset = pcbnew.FromMM(float(self.mainDlg.txtViaOffset.GetValue()))
        self.viaPitch = pcbnew.FromMM(float(self.mainDlg.txtViaPitch.GetValue()))
        self.viaDrill = pcbnew.FromMM(float(self.mainDlg.txtViaDrill.GetValue()))
        self.viaSize = pcbnew.FromMM(float(self.mainDlg.txtViaSize.GetValue()))
        self.viaNetId = list(self.netMap.keys())[self.mainDlg.lstViaNet.GetSelection()]   #maui
        self.isNetFilterChecked = self.mainDlg.chkNetFilter.GetValue()
        self.isLayerChecked = self.mainDlg.chkLayer.GetValue()
        self.isIncludeDrawingChecked = self.mainDlg.chkIncludeDrawing.GetValue()
        self.isDebugDumpChecked = self.mainDlg.chkDebugDump.GetValue()
        self.isSameNetZoneViasOnlyChecked = self.mainDlg.chkSameNetZoneViasOnly.GetValue()
        self.isRemoveViasWithClearanceViolationChecked = self.mainDlg.chkRemoveViasWithClearanceViolation.GetValue()

    def Run(self):
        #check for pyclipper lib
        pyclip = False
        try:
            import pyclipper
            pyclip = True
        except:
            wdlg = wx.MessageDialog(None, u"\u2718 ERROR Missing KiCAD \'pyclipper\' python module",'ERROR message',wx.OK | wx.ICON_ERROR)
            result = wdlg.ShowModal()
        if pyclip:
            self.boardObj = pcbnew.GetBoard()
            self.boardDesignSettingsObj = self.boardObj.GetDesignSettings()
            self.boardPath = os.path.dirname(os.path.realpath(self.boardObj.GetFileName()))
            self.layerMap = self.getLayerMap()
            self.highlightedNetId = self.boardObj.GetHighLightNetCode()
            self.netMap = self.getNetMap()
            self.netFilterList = self.createNetFilterSuggestions()
            self.netFilter = self.netMap[self.highlightedNetId].GetNetname() if self.highlightedNetId != -1 else self.netFilterList[0]
            self.viaSize = self.boardDesignSettingsObj.GetCurrentViaSize()
            self.layerId = 0 #TODO: How to get currently selected layer?
            self.viaDrill = self.boardDesignSettingsObj.GetCurrentViaDrill()
            self.viaPitch = pcbnew.FromMM(1)
            self.viaOffset = pcbnew.FromMM(1)
            self.viaNetId = 0 #TODO: Maybe a better init value here. Try to find "GND" maybe?
            self.isNetFilterChecked = 1 if self.highlightedNetId != -1 else 0
            self.isLayerChecked = 0
            self.isIncludeDrawingChecked = 0
            self.isDebugDumpChecked = 0
            self.isRemoveViasWithClearanceViolationChecked = 1
            self.isSameNetZoneViasOnlyChecked = 0
    
            self.mainDlg = MainDialog(None)
            self.selfToMainDialog()
    
            if (self.mainDlg.ShowModal() == wx.ID_OK):
                # User pressed OK.
                # Assemble a list of pcbnew.BOARD_ITEMs derived objects that support GetStart/GetEnd and IsOnLayer
                self.mainDialogToSelf()
                lineObjects = []
    
                # Do we want to include net tracks?
                if (self.isNetFilterChecked):
                    # Find nets that match the generated regular expression and add their tracks to the list
                    netRegex = self.regExFromSimpleEx(self.netFilter)
                    for netId in self.netMap:
                        if re.match(netRegex, self.netMap[netId].GetNetname()):
                            for trackObject in self.boardObj.TracksInNet(netId):
                                lineObjects += [trackObject]
    
                # Do we want to include drawing segments?
                if (self.isIncludeDrawingChecked):
                    boardItem = self.boardObj.GetDrawings().GetFirst()
                    while boardItem is not None:
                        if pcbnew.DRAWSEGMENT.ClassOf(boardItem):
                            # A drawing segment (not a text or something else)
                            drawingObject = boardItem.Cast()
                            if drawingObject.GetShape() == pcbnew.S_SEGMENT:
                                # A straight line
                                lineObjects += [drawingObject]
    
                        boardItem = boardItem.Next()
    
                # Do we want to filter the generated lines by layer?
                if (self.isLayerChecked):
                    # Filter by layer
                    # TODO: Make layer selection also a regex
                    lineObjects = [lineObject for lineObject in lineObjects if lineObject.IsOnLayer(self.layerId)]
    
                # Generate a path list from the pcbnew.BOARD_ITEM objects
                self.pathList =  [[ [lineObject.GetStart()[0], lineObject.GetStart()[1]],
                                    [lineObject.GetEnd()[0],   lineObject.GetEnd()[1]]   ]
                                    for lineObject in lineObjects]
    
                # Generate via fence
                try:
                    viaPoints = generateViaFence(self.pathList, self.viaOffset, self.viaPitch)
                except:
                    viaPoints = []
    
                if (self.isDebugDumpChecked):
                    self.dumpJSON(os.path.join(self.boardPath, time.strftime("viafence-%Y%m%d-%H%M%S.json")))
    
                viaObjList = self.createVias(viaPoints, self.viaDrill, self.viaSize, self.viaNetId)
    
            self.mainDlg.Destroy()  #the Dlg needs to be destroyed to release pcbnew

# TODO: Implement
#            if (self.isRemoveViasWithClearanceViolationChecked):
#                # Remove Vias that violate clearance to other things
#                # Check against other tracks
#                for viaObj in viaObjList:
#                    for track in self.boardObj.GetTracks():
#                        clearance = track.GetClearance(viaObj)
#                        if track.HitTest(False, clearance):
#                            self.boardObj.RemoveNative(viaObj)

# TODO: Implement
#            if (self.isSameNetZoneViasOnlyChecked):
#                # Keep via only if it is in a filled zone with the same net

#            import numpy as np
#            import matplotlib.pyplot as plt

#            for path in self.pathList:
#                plt.plot(np.array(path).T[0], np.array(path).T[1], linewidth=2)
#            for via in viaPoints:
#                plt.plot(via[0], via[1], 'o', markersize=10)


#            plt.ylim(plt.ylim()[::-1])
#            plt.axes().set_aspect('equal','box')
#            plt.show()
