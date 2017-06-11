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
		wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = wx.EmptyString, pos = wx.DefaultPosition, size = wx.Size( 400,400 ), style = wx.DEFAULT_DIALOG_STYLE )
		
		self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
		
		bSizer2 = wx.BoxSizer( wx.VERTICAL )
		
		gSizer2 = wx.GridSizer( 2, 2, 0, 0 )
		
		sbSizer2 = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"label" ), wx.VERTICAL )
		
		self.m_button1 = wx.Button( sbSizer2.GetStaticBox(), wx.ID_ANY, u"MyButton", wx.DefaultPosition, wx.DefaultSize, 0 )
		sbSizer2.Add( self.m_button1, 0, wx.ALL, 5 )
		
		self.m_staticline1 = wx.StaticLine( sbSizer2.GetStaticBox(), wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
		sbSizer2.Add( self.m_staticline1, 0, wx.EXPAND |wx.ALL, 5 )
		
		self.m_panel1 = wx.Panel( sbSizer2.GetStaticBox(), wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		bSizer3 = wx.BoxSizer( wx.VERTICAL )
		
		self.m_button3 = wx.Button( self.m_panel1, wx.ID_ANY, u"MyButton", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer3.Add( self.m_button3, 0, wx.ALL, 5 )
		
		
		self.m_panel1.SetSizer( bSizer3 )
		self.m_panel1.Layout()
		bSizer3.Fit( self.m_panel1 )
		sbSizer2.Add( self.m_panel1, 1, wx.EXPAND |wx.ALL, 5 )
		
		
		gSizer2.Add( sbSizer2, 1, wx.ALL|wx.EXPAND, 5 )
		
		
		bSizer2.Add( gSizer2, 1, wx.EXPAND, 5 )
		
		m_sdbSizer1 = wx.StdDialogButtonSizer()
		self.m_sdbSizer1OK = wx.Button( self, wx.ID_OK )
		m_sdbSizer1.AddButton( self.m_sdbSizer1OK )
		self.m_sdbSizer1Cancel = wx.Button( self, wx.ID_CANCEL )
		m_sdbSizer1.AddButton( self.m_sdbSizer1Cancel )
		m_sdbSizer1.Realize();
		
		bSizer2.Add( m_sdbSizer1, 0, wx.BOTTOM|wx.EXPAND, 5 )
		
		
		self.SetSizer( bSizer2 )
		self.Layout()
		
		self.Centre( wx.BOTH )
	
	def __del__( self ):
		pass
	

