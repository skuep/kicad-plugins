import os
from .viafence_basedialogs import *

class MainDialog(MainDialogBase):
    def __init__(self, parent):
        MainDialogBase.__init__(self, parent)
        # Small workaround to fix the paths generated by wxFormBuilder
        self.bmpViafence.SetBitmap(wx.Bitmap( os.path.join(os.path.dirname(os.path.realpath(__file__)), "resources", "viafence.png") ) )

    def OnInitDialog(self, event):
        self.Layout()
        self.GetSizer().Fit(self)
        self.SetMinSize(self.GetSize())
        self.SetMaxSize(self.GetSize())

    def OnNetFilterCheckBox(self, event):
        self.txtNetFilter.Enable(event.IsChecked())

    def OnLayerCheckBox(self, event):
        self.lstLayer.Enable(event.IsChecked())

