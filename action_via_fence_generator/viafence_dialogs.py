# -*- coding: utf-8 -*- 

###########################################################################
## Python code generated with wxFormBuilder (version Feb 16 2016)
## http://www.wxformbuilder.org/
##
## PLEASE DO "NOT" EDIT THIS FILE!
###########################################################################

import wx
import wx.xrc

###########################################################################
## Class MainDialog
###########################################################################

class MainDialog ( wx.Dialog ):
	
	def __init__( self, parent ):
		wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = u"Via Fence Generator", pos = wx.DefaultPosition, size = wx.Size( -1,-1 ), style = wx.DEFAULT_DIALOG_STYLE )
		
		self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
		
		bSizer2 = wx.BoxSizer( wx.VERTICAL )
		
		gbSizer4 = wx.GridBagSizer( 0, 0 )
		gbSizer4.SetFlexibleDirection( wx.BOTH )
		gbSizer4.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		bSizer23 = wx.BoxSizer( wx.VERTICAL )
		
		sbSizer2 = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"Via Settings" ), wx.VERTICAL )
		
		fgSizer4 = wx.FlexGridSizer( 8, 2, 0, 10 )
		fgSizer4.AddGrowableCol( 1 )
		fgSizer4.SetFlexibleDirection( wx.BOTH )
		fgSizer4.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_staticText11 = wx.StaticText( sbSizer2.GetStaticBox(), wx.ID_ANY, u"Offset (mm):", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText11.Wrap( -1 )
		fgSizer4.Add( self.m_staticText11, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		self.m_textCtrl11 = wx.TextCtrl( sbSizer2.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer4.Add( self.m_textCtrl11, 0, wx.ALL|wx.EXPAND, 5 )
		
		self.m_staticText21 = wx.StaticText( sbSizer2.GetStaticBox(), wx.ID_ANY, u"Pitch (mm):", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText21.Wrap( -1 )
		fgSizer4.Add( self.m_staticText21, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		self.m_textCtrl21 = wx.TextCtrl( sbSizer2.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer4.Add( self.m_textCtrl21, 0, wx.ALL|wx.EXPAND, 5 )
		
		self.m_staticText13 = wx.StaticText( sbSizer2.GetStaticBox(), wx.ID_ANY, u"Drill Dia. (mm):", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText13.Wrap( -1 )
		fgSizer4.Add( self.m_staticText13, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		self.m_textCtrl111 = wx.TextCtrl( sbSizer2.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer4.Add( self.m_textCtrl111, 0, wx.ALL|wx.EXPAND, 5 )
		
		self.m_staticText14 = wx.StaticText( sbSizer2.GetStaticBox(), wx.ID_ANY, u"Via Dia. (mm):", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText14.Wrap( -1 )
		fgSizer4.Add( self.m_staticText14, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		self.m_textCtrl12 = wx.TextCtrl( sbSizer2.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer4.Add( self.m_textCtrl12, 0, wx.ALL|wx.EXPAND, 5 )
		
		self.m_staticText23 = wx.StaticText( sbSizer2.GetStaticBox(), wx.ID_ANY, u"Via Net:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText23.Wrap( -1 )
		fgSizer4.Add( self.m_staticText23, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		self.m_textCtrl17 = wx.TextCtrl( sbSizer2.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer4.Add( self.m_textCtrl17, 0, wx.ALL|wx.EXPAND, 5 )
		
		
		sbSizer2.Add( fgSizer4, 1, wx.EXPAND, 5 )
		
		
		bSizer23.Add( sbSizer2, 1, wx.ALL|wx.EXPAND, 5 )
		
		
		gbSizer4.Add( bSizer23, wx.GBPosition( 0, 0 ), wx.GBSpan( 1, 1 ), wx.EXPAND, 5 )
		
		bSizer21 = wx.BoxSizer( wx.VERTICAL )
		
		self.m_panel11 = wx.Panel( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.SIMPLE_BORDER|wx.TAB_TRAVERSAL )
		bSizer24 = wx.BoxSizer( wx.VERTICAL )
		
		self.m_bitmap2 = wx.StaticBitmap( self.m_panel11, wx.ID_ANY, wx.Bitmap( u"resources/viafence.png", wx.BITMAP_TYPE_ANY ), wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer24.Add( self.m_bitmap2, 1, wx.EXPAND, 0 )
		
		
		self.m_panel11.SetSizer( bSizer24 )
		self.m_panel11.Layout()
		bSizer24.Fit( self.m_panel11 )
		bSizer21.Add( self.m_panel11, 0, wx.EXPAND|wx.ALL, 5 )
		
		
		gbSizer4.Add( bSizer21, wx.GBPosition( 0, 1 ), wx.GBSpan( 1, 1 ), wx.EXPAND|wx.ALL, 5 )
		
		sbSizer411 = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"Input Tracks" ), wx.VERTICAL )
		
		gSizer4 = wx.GridSizer( 1, 2, 0, 0 )
		
		fgSizer31 = wx.FlexGridSizer( 2, 2, 0, 10 )
		fgSizer31.AddGrowableCol( 1 )
		fgSizer31.SetFlexibleDirection( wx.BOTH )
		fgSizer31.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_staticText51 = wx.StaticText( sbSizer411.GetStaticBox(), wx.ID_ANY, u"Layer:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText51.Wrap( -1 )
		fgSizer31.Add( self.m_staticText51, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		m_choice21Choices = []
		self.m_choice21 = wx.Choice( sbSizer411.GetStaticBox(), wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, m_choice21Choices, 0 )
		self.m_choice21.SetSelection( 0 )
		fgSizer31.Add( self.m_choice21, 0, wx.ALL|wx.EXPAND, 5 )
		
		
		gSizer4.Add( fgSizer31, 1, wx.EXPAND, 5 )
		
		fgSizer311 = wx.FlexGridSizer( 2, 2, 0, 10 )
		fgSizer311.AddGrowableCol( 1 )
		fgSizer311.SetFlexibleDirection( wx.BOTH )
		fgSizer311.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_staticText611 = wx.StaticText( sbSizer411.GetStaticBox(), wx.ID_ANY, u"Net(s):", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText611.Wrap( -1 )
		fgSizer311.Add( self.m_staticText611, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		self.m_textCtrl411 = wx.TextCtrl( sbSizer411.GetStaticBox(), wx.ID_ANY, u"*", wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer311.Add( self.m_textCtrl411, 0, wx.ALL|wx.EXPAND, 5 )
		
		
		gSizer4.Add( fgSizer311, 1, wx.EXPAND, 5 )
		
		
		sbSizer411.Add( gSizer4, 1, wx.EXPAND, 5 )
		
		
		gbSizer4.Add( sbSizer411, wx.GBPosition( 1, 0 ), wx.GBSpan( 1, 2 ), wx.ALL|wx.EXPAND, 5 )
		
		
		gbSizer4.AddGrowableCol( 0 )
		
		bSizer2.Add( gbSizer4, 1, wx.EXPAND, 5 )
		
		m_sdbSizer1 = wx.StdDialogButtonSizer()
		self.m_sdbSizer1OK = wx.Button( self, wx.ID_OK )
		m_sdbSizer1.AddButton( self.m_sdbSizer1OK )
		self.m_sdbSizer1Cancel = wx.Button( self, wx.ID_CANCEL )
		m_sdbSizer1.AddButton( self.m_sdbSizer1Cancel )
		m_sdbSizer1.Realize();
		
		bSizer2.Add( m_sdbSizer1, 0, wx.BOTTOM|wx.EXPAND, 5 )
		
		
		self.SetSizer( bSizer2 )
		self.Layout()
		bSizer2.Fit( self )
		
		self.Centre( wx.BOTH )
	
	def __del__( self ):
		pass
	

