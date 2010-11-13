#!/usr/bin/env python

# --------------------------------------------------------------------------------- #
# Pyfa's custom Notebook core python IMPLEMENTATION
#
# Darriele (homeworld using gmail point com) - 10/27/2010
# Updated: 11/11/2010
#
# --------------------------------------------------------------------------------- #

import wx
import copy
import time

class PFTabRenderer:
    def __init__(self, size = (36,24), text = wx.EmptyString, img = None, inclination = 6 , closeButton = True, fontSize = 8):

        # tab left/right zones inclination
        self.inclination = inclination
        self.text = text
        self.img = img
        self.tabSize = size
        self.closeButton = closeButton
        self.fontSize = fontSize
        self.selected = False
        self.closeBtnHovering = False
        self.tabBitmap = None
        self.cbSize = 5
        self.position = (0, 0) # Not used internaly for rendering - helper for tab container
        self.InitTab()

    def SetPosition(self, position):
        self.position = position

    def GetPosition(self):
        return self.position

    def GetSize(self):
        return self.tabSize

    def SetSize(self, size):
        otw,oth = self.tabSize
        self.tabSize = size
        w,h = self.tabSize
        if h != oth:
            self.InitTab(True)
        else:
            self.InitTab()

    def SetSelected(self, sel = True):
        self.selected = sel
        self.InitColors()
        self._Render()

    def GetSelected(self):
        return self.selected

    def IsSelected(self):
        return self.selected

    def ShowCloseButtonHovering(self, hover = True):
        if self.closeBtnHovering != hover:
            self.closeBtnHovering = hover
            self._Render()

    def GetCloseButtonHoverStatus(self):
        return self.closeBtnHovering

    def GetTabRegion(self):
        nregion = self.CopyRegion(self.tabRegion)
        nregion.SubtractRegion(self.closeBtnRegion) if self.closeButton else self.tabRegion
        return nregion

    def GetCloseButtonRegion(self):
        return self.CopyRegion(self.closeBtnRegion)

    def GetMinSize(self):
        ebmp = wx.EmptyBitmap(1,1)
        mdc = wx.MemoryDC()
        mdc.SelectObject(ebmp)
        mdc.SetFont(self.font)
        textSizeX, textSizeY = mdc.GetTextExtent(self.text)
        totalSize = self.lrZoneWidth * 2 + textSizeX + self.cbSize*2 if self.closeButton else 0
        mdc.SelectObject(wx.NullBitmap)
        return (totalSize, self.tabHeight)


    def CopyRegion(self, region):
        rect = region.GetBox()

        newRegion = wx.Region(rect.X, rect.Y, rect.Width, rect.Height)
        newRegion.IntersectRegion(region)

        return newRegion

    def InitTab(self, skipLRzones = False):
        self.tabWidth, self.tabHeight = self.tabSize

        # content width is tabWidth - (left+right) zones

        self.contentWidth = self.tabWidth - self.inclination * 6 - self.cbSize if self.closeButton else 0

        self.leftZoneSpline = []
        self.rightZoneSpline = []

        self.lrZoneWidth = self.inclination * 3
        if not skipLRzones:
            self.CreateLRZoneSplines()

            self.leftRegion = self.CreateLeftRegion()
            self.rightRegion = self.CreateRightRegion()

        self.contentRegion = wx.Region(0, 0, self.contentWidth, self.tabHeight)
        self.tabRegion = None
        self.closeBtnRegion = None
        self.font = wx.Font(self.fontSize, wx.SWISS, wx.NORMAL, wx.NORMAL, False)

        self.InitTabRegions()
        self.InitColors()
        self._Render()

    def InitColors(self):
        self.tabColor = wx.SystemSettings_GetColour(wx.SYS_COLOUR_WINDOW)
        self.leftColor = self.CalculateColor(self.tabColor, 0x2F)
        self.rightColor = self.CalculateColor(self.tabColor, 0x44)
        self.gradientStartColor = self.CalculateColor(self.tabColor, 0x17 if self.selected else 0x20)

    def CalculateColor(self, color, delta):
        bkR ,bkG , bkB = color
        if bkR + bkG + bkB > 127*3:
            scale = - delta
        else:
            scale = delta*2

        r = bkR + scale
        g = bkG + scale
        b = bkB + scale

        r = min(max(r,0),255)
        b = min(max(b,0),255)
        g = min(max(g,0),255)

        return wx.Colour(r,g,b)

    def InitTabRegions(self):
        self.tabRegion = wx.Region(0, 0, self.tabWidth, self.tabHeight)
        self.tabRegion.IntersectRegion(self.leftRegion)

        self.contentRegion.Offset(self.lrZoneWidth, 0)
        self.tabRegion.UnionRegion(self.contentRegion)

        self.rightRegion.Offset(self.tabWidth - self.lrZoneWidth, 0)
        self.tabRegion.UnionRegion(self.rightRegion)
        self.closeBtnRegion = wx.Region(self.tabWidth - self.lrZoneWidth - self.cbSize -2 , (self.tabHeight - self.cbSize) / 2 - 2, self.cbSize + 4, self.cbSize + 4)
        cbtRegion = wx.Region(self.tabWidth - self.lrZoneWidth - self.cbSize ,0, self.cbSize, self.tabHeight)
        self.tabRegion.UnionRegion(cbtRegion)

    def CreateLRZoneSplines(self):
        height = self.tabHeight
        inc = self.inclination

        self.leftZoneSpline = [wx.Point(0, height), wx.Point(inc * 2/3, height - inc/2), wx.Point(inc+inc/2, 2),
                 wx.Point(inc * 3, 0)]
        self.rightZoneSpline = [wx.Point(0, 0), wx.Point(inc+inc/2,2),wx.Point(inc*2 +inc*2/3,height-inc/2), wx.Point(inc*3,height) ]

    def CreateLeftRegion(self):

        width = self.lrZoneWidth + 1
        height = self.tabHeight + 1
        inc = self.inclination

        mdc = wx.MemoryDC()

        mbmp = wx.EmptyBitmap(width,height,24)
        mdc.SelectObject(mbmp)

        mdc.SetBackground( wx.Brush((123,123,123)))
        mdc.Clear()

        mdc.SetPen( wx.Pen("#000000", width = 1 ) )
        mdc.DrawSpline(self.leftZoneSpline)

        mdc.SetBrush(wx.Brush((255,255,0)))
        mdc.FloodFill(inc*2,height-inc, wx.Color(0,0,0), wx.FLOOD_BORDER)

        mdc.SelectObject(wx.NullBitmap)

        mbmp.SetMaskColour( (123, 123, 123) )

        region = wx.RegionFromBitmap(mbmp)
        region.Offset(-1,0)

        return region

    def CreateRightRegion(self):

        width = self.lrZoneWidth + 1
        height = self.tabHeight
        inc = self.inclination

        mdc = wx.MemoryDC()

        mbmp = wx.EmptyBitmap(width,height,24)
        mdc.SelectObject(mbmp)

        mdc.SetBackground( wx.Brush((123,123,123)))
        mdc.Clear()

        mdc.SetPen( wx.Pen("#000000", width = 1 ) )
        mdc.DrawSpline(self.rightZoneSpline)

        mdc.SetBrush(wx.Brush((255,255,0)))
        mdc.FloodFill(inc,height-inc, wx.Color(0,0,0), wx.FLOOD_BORDER)

        mdc.SelectObject(wx.NullBitmap)

        mbmp.SetMaskColour( (123, 123, 123) )

        region = wx.RegionFromBitmap(mbmp)

        return region

    def OffsetPointList(self, list , x, y):
        tlist = []
        for i in list:
            tlist.append(wx.Point(i.x + x, i.y + y))

        return tlist

    def Render(self):
        return self.tabBitmap

    def _Render(self):
        if self.tabBitmap:
            del self.tabBitmap

        inc = self.lrZoneWidth
        height = self.tabHeight
        width = self.tabWidth
        contentWidth = self.contentWidth + self.cbSize if self.closeButton else 0

        rect = wx.Rect(0,0,self.tabWidth, self.tabHeight)

        canvas = wx.EmptyBitmap(rect.width, rect.height)

        mdc = wx.MemoryDC()

        mdc.SelectObject(canvas)
        mdc.SetBackground(wx.Brush ((13,22,31)))
        mdc.Clear()
        mdc.DestroyClippingRegion()
        mdc.SetClippingRegionAsRegion(self.tabRegion)

        r = copy.copy(rect)
        r.top = r.left = 0
        r.height = height

        mdc.GradientFillLinear(r,self.gradientStartColor,self.tabColor,wx.SOUTH)
        mdc.SetPen( wx.Pen(self.leftColor, width = 1 ) )

        dpleft = self.OffsetPointList(self.leftZoneSpline, -1, 0)
        dpright = self.OffsetPointList(self.rightZoneSpline, inc + contentWidth, 0)

        mdc.DrawSpline(dpleft)
        mdc.SetPen( wx.Pen(self.rightColor, width = 1 ) )
        mdc.DrawSpline(dpright)

        lrect = wx.Rect()
        lrect.left=inc - 1
        lrect.top=0
        lrect.width = contentWidth+1
        lrect.height = 1
        mdc.GradientFillLinear(lrect,self.leftColor,self.rightColor, wx.EAST)
#        if not self.selected:
#            mdc.DrawLine(0,height - 1,width,height - 1)
        mdc.SetPen( wx.Pen(self.rightColor, width = 1 ) )
        if self.closeButton:
            cbsize = self.cbSize

            cbx = width - self.lrZoneWidth-cbsize
            cby = (height - cbsize)/2
            if self.closeBtnHovering:
                mdc.SetPen( wx.Pen( wx.Colour(255,22,22), 0))
                mdc.SetBrush(wx.Brush(wx.Colour(255,22,22)))
                mdc.DrawCircle(cbx + cbsize / 2 +1, cby + cbsize / 2 + 1, cbsize)
                selColor = self.CalculateColor(wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOWTEXT), 255)
                mdc.SetPen( wx.Pen( selColor, 1))

            mdc.DrawLine(cbx, cby, cbx + cbsize + 1 , cby + cbsize + 1 )
            mdc.DrawLine(cbx, cby + cbsize, cbx + cbsize + 1, cby - 1 )

        mdc.SetClippingRegionAsRegion(self.contentRegion)
        mdc.SetFont(self.font)
        text = self.text
        fnwidths = mdc.GetPartialTextExtents(text)
        count = 0
        maxsize = self.contentWidth - self.cbSize if self.closeButton else 0
        for i in fnwidths:
            if i <= maxsize:
                count +=1
            else:
                break

#        text = "%s%s" % (text[:count],"." if len(text)>count else "")
        text = "%s" % text[:count]


        tx,ty = mdc.GetTextExtent(text)
        if self.selected:
            mdc.SetTextForeground(wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOWTEXT))
        else:
            color = self.CalculateColor(wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOWTEXT), 0x44)
            mdc.SetTextForeground(color)
        mdc.DrawText(text, inc, height / 2 - ty / 2)

        mdc.DestroyClippingRegion()

        mdc.SelectObject(wx.NullBitmap)
        canvas.SetMaskColour((13,22,31))
#        if not self.selected:
#            img = canvas.ConvertToImage()
#            img = img.AdjustChannels(1, 1, 1, 0.8)
#            canvas = wx.BitmapFromImage(img)
        self.tabBitmap = canvas

class PFAddRenderer:
    def __init__(self, size = (24,12)):
        self.width, self.height = size
        self.addBitmap = None
        self.spline = []
        self.inclination = 3
        self.region = None
        self.InitRenderer()

    def GetSize(self):
        return (self.width, self.height)

    def InitRenderer(self):
        self.CreateSpline()
        self.region = self.CreateRegion()
        self._Render()

    def CreateSpline(self):
        width = self.width
        height = self.height - 1
        inc = self.inclination

        self.spline = [wx.Point(0, 0), wx.Point(inc*3/2, height),wx.Point(inc*2 + inc*2/3, height), wx.Point(width, height), wx.Point(width, height),
                       wx.Point(width - inc, inc), wx.Point(width - inc*2, 0), wx.Point(0, 0), wx.Point(0, 0)]
    def CreateRegion(self):
        width = self.width
        height = self.height
        inc = self.inclination

        mdc = wx.MemoryDC()

        mbmp = wx.EmptyBitmap(width,height)
        mdc.SelectObject(mbmp)

        mdc.SetBackground( wx.Brush((255,255,255)))
        mdc.Clear()

        mdc.SetPen( wx.Pen("#000000", width = 1 ) )
        mdc.DrawSpline(self.spline)

        mdc.SetBrush(wx.Brush((255,255,0)))
        mdc.FloodFill(width/2,height/2, wx.Color(0,0,0), wx.FLOOD_BORDER)

        mdc.SelectObject(wx.NullBitmap)

        mbmp.SetMaskColour( (255, 255, 255) )

        region = wx.RegionFromBitmap(mbmp)
#        region.Offset(-1,0)

        return region

    def CalculateColor(self, color, delta):
        bkR ,bkG , bkB = color
        if bkR + bkG + bkB > 127*3:
            scale = - delta
        else:
            scale = delta*2

        r = bkR + scale
        g = bkG + scale
        b = bkB + scale

        r = min(max(r,0),255)
        b = min(max(b,0),255)
        g = min(max(g,0),255)

        return wx.Colour(r,b,g)

    def Render(self):
        return self.addBitmap

    def _Render(self):
        inc = self.inclination
        rect = wx.Rect(0 ,0 ,self.width, self.height)
        if self.addBitmap:
            del self.addBitmap

        canvas = wx.EmptyBitmap(self.width, self.height)

        mdc = wx.MemoryDC()
        mdc.SelectObject(canvas)

        mdc.SetBackground(wx.Brush ((13,22,31)))
        mdc.Clear()

        mdc.DestroyClippingRegion()
        mdc.SetClippingRegionAsRegion(self.region)
#        mdc.GradientFillLinear(rect, (0x30,0x30,0x30), (0x6f,0x6f,0x6f), wx.SOUTH)
        mdc.FloodFill(self.width/2,self.height/2, wx.Color(13,22,31), wx.FLOOD_BORDER)
        mdc.DestroyClippingRegion()
        mdc.SetPen( wx.Pen( wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOWTEXT), 1))
        mdc.DrawSpline(self.spline)
        mdc.SelectObject(wx.NullBitmap)

        canvas.SetMaskColour((13,22,31))

        img = canvas.ConvertToImage()
        if not img.HasAlpha():
            img.InitAlpha()
        img = img.AdjustChannels(1, 1, 1, 0.6)
        img = img.Blur(1)
        bbmp = wx.BitmapFromImage(img)

        del mdc
        del canvas
        canvas = wx.EmptyBitmap(self.width, self.height)

        mdc = wx.MemoryDC()
        mdc.SelectObject(canvas)

        mdc.SetBackground(wx.Brush ((255,255,255 , 0)))
        mdc.Clear()

        mdc.DrawBitmap(bbmp,0,0,True)

        cx = self.width / 2 - 1
        cy = self.height / 2

        mdc.SetPen( wx.Pen( wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOWTEXT), 1))
        mdc.DrawLine(cx - inc + 1, cy, cx + inc + 1, cy)
        mdc.DrawLine(cx - inc + 1, cy-1, cx + inc + 1, cy-1)
        mdc.DrawLine(cx, cy - inc, cx, cy + inc )
        mdc.DrawLine(cx+1, cy - inc, cx+1, cy + inc )

        self.wColor = wx.SystemSettings_GetColour(wx.SYS_COLOUR_WINDOW)
        color = self.CalculateColor(self.wColor, 0x99)
        mdc.SetPen( wx.Pen( color, 1))

        mdc.DrawSpline(self.spline)

        mdc.SelectObject(wx.NullBitmap)
        canvas.SetMaskColour((255,255,255))

        img = canvas.ConvertToImage()
        if not img.HasAlpha():
            img.InitAlpha()
        img = img.AdjustChannels(1, 1, 1, 0.3)

        bbmp = wx.BitmapFromImage(img)
        self.addBitmap = bbmp


class PFTabsContainer(wx.Window):
    def __init__(self, parent, pos = (0,0), size = (100,27), id = wx.ID_ANY):
        wx.Window.__init__(self, parent, id , pos, size , style = 0)
        self.tabs = []
        width, height = size
        self.width  = width
        self.height = height - 3
        self.containerHeight = height
        self.startDrag = False
        self.dragging = False
        self.reserved = 48
        self.inclination = 6
        self.dragTrail = 3
        self.dragx = 0
        self.dragy = 0
        self.draggedTab = None
        self.dragTrigger = self.dragTrail

        self.tabContainerWidth = width - self.reserved
        self.tabMinWidth = width
        self.tabShadow = None

        self.addButton = PFAddRenderer()
        self.addBitmap = self.addButton.Render()

        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_ERASE_BACKGROUND, self.OnErase)
        self.Bind(wx.EVT_LEFT_DOWN, self.OnLeftDown)
        self.Bind(wx.EVT_LEFT_UP, self.OnLeftUp)
        self.Bind(wx.EVT_MOTION, self.OnMotion)
        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.tabShadow = PFTabRenderer((self.tabMinWidth, self.height + 1), inclination = self.inclination)

    def OnSize(self, event):
        self.UpdateSize()
        event.Skip()

    def UpdateSize(self):
        width, dummy = self.GetSize()
        if width != self.width:
            self.width = width
            self.tabContainerWidth = self.width - self.reserved
            self.AdjustTabsSize()

    def OnLeftDown(self, event):
        mposx,mposy = event.GetPosition()
        if not self.startDrag:
            tab = self.FindTabAtPos(mposx, mposy)
            if tab:
                self.CheckTabSelected(tab, mposx, mposy)
                self.startDrag = True
                tx,ty = tab.GetPosition()
                self.dragx = mposx - tx
                self.dragy = self.containerHeight - self.height
                self.Refresh()

            self.draggedTab = tab

    def OnLeftUp(self, event):
        mposx,mposy = event.GetPosition()
        if self.startDrag and self.dragging:
            self.dragging = False
            self.startDrag = False
            self.draggedTab = None
            self.dragTrigger = self.dragTrail
            self.UpdateTabsPosition()
            self.Refresh()
            if self.HasCapture():
                self.ReleaseMouse()
            return

        if self.startDrag:
            self.startDrag = False
            self.dragTrigger = self.dragTrail

        if self.GetTabsCount() == 0:
            return
        selTab = self.GetSelectedTab()

        if self.CheckTabClose(selTab, mposx, mposy):
            return

#        if self.CheckTabSelected(selTab, mposx, mposy):
#            return

        for tab in self.tabs:

            if self.CheckTabClose(tab, mposx, mposy):
                return

#            if self.CheckTabSelected(tab, mposx, mposy):
#                return

    def GetSelectedTab(self):
        for tab in self.tabs:
            if tab.GetSelected():
                return tab
        return None

    def GetSelected(self):
        for tab in self.tabs:
            if tab.GetSelected():
                return self.tabs.index(tab)
        return None

    def CheckTabSelected(self,tab, mposx, mposy):

        oldSelTab = self.GetSelectedTab()
        if oldSelTab == tab:
            return True

        if self.TabHitTest(tab, mposx, mposy):
            tab.SetSelected(True)
            if tab != oldSelTab:
                oldSelTab.SetSelected(False)
            self.Refresh()
            print "Selected: %s" %tab.text

            selTab = self.tabs.index(tab)
            self.Parent.SetSelected(selTab)

            return True
        return False

    def CheckTabClose(self, tab, mposx, mposy):
        closeBtnReg = tab.GetCloseButtonRegion()
        tabPosX, tabPosY = tab.GetPosition()

        closeBtnReg.Offset(tabPosX,tabPosY)

        if closeBtnReg.Contains(mposx, mposy):
            print "Close tab: %s" % tab.text
            index = self.GetTabIndex(tab)
            self.DeleteTab(index)
            return True
        return False

    def CheckCloseButtons(self, mposx, mposy):
        dirty = False

        for tab in self.tabs:
            closeBtnReg = tab.GetCloseButtonRegion()
            tabPos = tab.GetPosition()
            tabPosX, tabPosY = tabPos
            closeBtnReg.Offset(tabPosX,tabPosY)
            if closeBtnReg.Contains(mposx,mposy):
                if not tab.GetCloseButtonHoverStatus():
                    tab.ShowCloseButtonHovering(True)
                    dirty = True
            else:
                if tab.GetCloseButtonHoverStatus():
                    tab.ShowCloseButtonHovering(False)
                    dirty = True
        if dirty:
            self.Refresh()

    def FindTabAtPos(self, x, y):
        if self.GetTabsCount() == 0:
            return None
        selTab = self.GetSelectedTab()
        if self.TabHitTest(selTab, x, y):
            return selTab

        for tab in self.tabs:
            if self.TabHitTest(tab, x, y):
                return tab
        return None

    def TabHitTest(self, tab, x, y):
        tabRegion = tab.GetTabRegion()
        tabPos = tab.GetPosition()
        tabPosX, tabPosY = tabPos
        tabRegion.Offset(tabPosX, tabPosY)
        if tabRegion.Contains(x, y):
            return True
        return False

    def GetTabAtLeft(self, tabIndex):
        if tabIndex>0:
            return self.tabs[tabIndex - 1]
        else:
            return None

    def GetTabAtRight(self, tabIndex):
        if tabIndex < self.GetTabsCount() - 1:
            return self.tabs[tabIndex + 1]
        else:
            return None

    def SwitchTabs(self, src, dest, draggedTab = None):
        self.tabs[src], self.tabs[dest] = self.tabs[dest], self.tabs[src]
        self.UpdateTabsPosition(draggedTab)

        self.Parent.SwitchPages(src,dest, True)

        self.Refresh()

    def GetTabIndex(self, tab):
        return self.tabs.index(tab)

    def OnMotion(self, event):
        mposx,mposy = event.GetPosition()
        if self.startDrag:
            if not self.dragging:
                if self.dragTrigger < 0:
                    self.dragging = True
                    self.dragTrigger = self.dragTrail
                    self.CaptureMouse()
                else:
                    self.dragTrigger -= 1
            if self.dragging:
                dtx = mposx - self.dragx
                w,h = self.draggedTab.GetSize()

                if dtx < 0:
                    dtx = 0
                if dtx + w > self.tabContainerWidth + self.inclination * 2:
                    dtx = self.tabContainerWidth - w + self.inclination * 2
                self.draggedTab.SetPosition( (dtx, self.dragy))

                index = self.GetTabIndex(self.draggedTab)

                leftTab = self.GetTabAtLeft(index)
                rightTab = self.GetTabAtRight(index)

                if leftTab:
                    lw,lh = leftTab.GetSize()
                    lx,ly = leftTab.GetPosition()

                    if lx + lw / 2 - self.inclination * 2 > dtx:
                        self.SwitchTabs(index - 1 , index, self.draggedTab)
                        return

                if rightTab:
                    rw,rh = rightTab.GetSize()
                    rx,ry = rightTab.GetPosition()

                    if rx + rw / 2 + self.inclination * 2 < dtx + w:
                        self.SwitchTabs(index + 1 , index, self.draggedTab)
                        return
                self.UpdateTabsPosition(self.draggedTab)
                self.Refresh()
                return
            return
        self.CheckCloseButtons(mposx, mposy)

        event.Skip()

    def OnPaint(self, event):
        rect = self.GetRect()
        canvas = wx.EmptyBitmap(rect.width, rect.height,24)
        mdc = wx.BufferedPaintDC(self)
        mdc.SelectObject(canvas)

        selected = 0

        mdc.SetBackground (wx.Brush(wx.SystemSettings_GetColour(wx.SYS_COLOUR_WINDOW)))
#        mdc.SetBackground (wx.Brush((66,113,202)))
        mdc.Clear()

        selected = None
        selpos = 0
        selWidth = selHeight = 0
        selColor = self.CalculateColor(wx.SystemSettings_GetColour(wx.SYS_COLOUR_WINDOW), 0x34)
        startColor = self.leftColor = self.CalculateColor(wx.SystemSettings_GetColour(wx.SYS_COLOUR_WINDOW), 0x2f)
        tabsWidth = 0


        for tab in self.tabs:
            tabsWidth += tab.tabWidth - self.inclination*2

        pos = tabsWidth

        mdc.DrawBitmap(self.addBitmap, round(tabsWidth) + self.inclination*2, self.containerHeight - self.height/2 - self.addBitmap.GetHeight()/2, True)

        for i in xrange(len(self.tabs) - 1, -1, -1):
            tab = self.tabs[i]
            width = tab.tabWidth - self.inclination*2
            posx, posy  = tab.GetPosition()
            if not tab.IsSelected():
#                mdc.DrawBitmap(self.efxBmp, posx, posy - 1, True )
#                img = tab.Render().ConvertToImage()
#                img = img.AdjustChannels(1, 1, 1, 0.8)
#                bmp = wx.BitmapFromImage(img)
                mdc.DrawBitmap(tab.Render(), posx, posy, True)
            else:
                selected = tab
        if selected:
            posx, posy  = selected.GetPosition()
#            mdc.DrawBitmap(self.efxBmp, posx, posy - 1, True)
            bmp = selected.Render()
#            if self.dragging:
#                img = bmp.ConvertToImage()
#                img = img.AdjustChannels(1.2, 1.2, 1.2, 0.7)
#                bmp = wx.BitmapFromImage(img)

            mdc.DrawBitmap(bmp, posx, posy, True)
            selpos = posx
            selWidth,selHeight = selected.GetSize()

        if selWidth%2:
            offset = 1
        else:
            offset = 0
        r1 = wx.Rect(0,self.containerHeight-1,selpos,1)
        r2 = wx.Rect(selpos + selWidth - offset, self.containerHeight -1, self.width - selpos - selWidth,1)
        mdc.GradientFillLinear(r1, startColor, selColor, wx.EAST)
        mdc.GradientFillLinear(r2, selColor, startColor, wx.EAST)

    def OnErase(self, event):
        pass

    def UpdateTabFX(self):
        w,h = self.tabShadow.GetSize()
        if w != self.tabMinWidth:
            self.tabShadow.SetSize((self.tabMinWidth, self.height + 1))
            fxBmp = self.tabShadow.Render()

            simg = fxBmp.ConvertToImage()
#            if not simg.HasAlpha():
#                simg.InitAlpha()
#            simg = simg.Blur(2)
#            simg = simg.AdjustChannels(0.2,0.2,0.2,0.3)

            self.efxBmp = wx.BitmapFromImage(simg)

    def AddTab(self, title = wx.EmptyString, img = None):
        self.ClearTabsSelected()

        tabRenderer = PFTabRenderer( (120,self.height), title, img, self.inclination)
        tabRenderer.SetSelected(True)

        self.tabs.append( tabRenderer )
        self.AdjustTabsSize()
        self.Refresh()

    def ClearTabsSelected(self):
        for tab in self.tabs:
            tab.SetSelected(False)

    def DeleteTab(self, tab):
        tabRenderer = self.tabs[tab]
        wasSelected = tabRenderer.GetSelected()
        self.tabs.remove(tabRenderer)

        if tabRenderer:
            del tabRenderer

        if wasSelected and self.GetTabsCount() > 0:
            if tab > self.GetTabsCount() -1:
                self.tabs[self.GetTabsCount() - 1].SetSelected(True)
            else:
                self.tabs[tab].SetSelected(True)

        self.Parent.DeletePage(tab, True)

        self.AdjustTabsSize()
        self.Refresh()

    def GetTabsCount(self):
        return len(self.tabs)

    def AdjustTabsSize(self):

        tabMinWidth = 9000000 # Really, it should be over 9000

        for tab in self.tabs:
            mw,mh = tab.GetMinSize()
            if tabMinWidth > mw:
               tabMinWidth = mw

        if self.GetTabsCount() >0:
            if (self.GetTabsCount()) * (tabMinWidth - self.inclination * 2) > self.tabContainerWidth:
                self.tabMinWidth = float(self.tabContainerWidth) / float(self.GetTabsCount()) + self.inclination * 2
            else:
                self.tabMinWidth = tabMinWidth
        if self.tabMinWidth <1:
            self.tabMinWidth = 1
        for tab in self.tabs:
            w,h = tab.GetSize()
            if w != self.tabMinWidth:
                tab.SetSize( (self.tabMinWidth, self.height) )

        if self.GetTabsCount() > 0:
            self.UpdateTabFX()

        self.UpdateTabsPosition()

    def UpdateTabsPosition(self, skipTab = None):
        tabsWidth = 0
        for tab in self.tabs:
            tabsWidth += tab.tabWidth - self.inclination*2

        pos = tabsWidth
        selected = None
        for i in xrange(len(self.tabs) - 1, -1, -1):
            tab = self.tabs[i]
            width = tab.tabWidth - self.inclination*2
            pos -= width
            if not tab.IsSelected():
                tab.SetPosition((pos, self.containerHeight - self.height))
            else:
                selected = tab
                selpos = pos
        if selected is not skipTab:
            selected.SetPosition((selpos, self.containerHeight - self.height))


    def CalculateColor(self, color, delta):
        bkR ,bkG , bkB = color
        if bkR + bkG + bkB > 127*3:
            scale = - delta
        else:
            scale = delta*2

        r = bkR + scale
        g = bkG + scale
        b = bkB + scale

        r = min(max(r,0),255)
        g = min(max(g,0),255)
        b = min(max(b,0),255)

        return wx.Colour(r,g,b)

class PFNotebook(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, wx.ID_ANY,size = (-1,-1))

        self.pages = []
        self.activePage = None

        mainSizer = wx.BoxSizer( wx.VERTICAL )

        tabsSizer = wx.BoxSizer( wx.VERTICAL )

        self.tabsContainer = PFTabsContainer(self)
        tabsSizer.Add( self.tabsContainer, 0, wx.EXPAND )

        mainSizer.Add( tabsSizer, 0, wx.EXPAND, 5 )

        contentSizer = wx.BoxSizer( wx.VERTICAL )
        self.pageContainer = wx.Panel(self)
        contentSizer.Add( self.pageContainer, 1, wx.EXPAND, 5 )

        mainSizer.Add( contentSizer, 1, wx.EXPAND, 5 )

        self.SetSizer( mainSizer )
        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.Layout()
#        for i in xrange(10):
#            self.tabsContainer.AddTab("Pyfa TAB #%d Aw" % i)

    def AddPage(self, tabWnd, tabTitle = wx.EmptyString, tabImage = None):
        if self.activePage:
            self.activePage.Hide()

        tabWnd.Reparent(self.pageContainer)
        self.pageContainer.Layout()

        self.pages.append(tabWnd)
        self.tabsContainer.AddTab(tabTitle, tabImage)

        self.activePage = tabWnd

    def SetSelected(self, page):
        oldsel = self.pages.index(self.activePage)
        if oldsel != page:
            self.activePage.Hide()
            self.activePage = self.pages[page]
            self.ShowActive()

    def DeletePage(self, n, internal = False):
        page = self.pages[n]

        self.pages.remove(page)
        page.Hide()
        page.Destroy()

        if not internal:
            self.tabsContainer.DeleteTab(n)
        sel = self.tabsContainer.GetSelected()
        if sel is not None:
            self.activePage = self.pages[sel]
            self.ShowActive()

    def SwitchPages(self, src, dest, internal = False):
        self.pages[src], self.pages[dest] = self.pages[dest], self.pages[src]

    def ShowActive(self):
        self.activePage.SetSize(self.pageContainer.GetSize())
        self.activePage.Show()
        self.Layout()
    def OnSize(self, event):
        w,h= self.GetSize()
        self.tabsContainer.SetSize((w, -1))
        self.tabsContainer.UpdateSize()
        self.tabsContainer.Refresh()
        self.Layout()
        size = self.pageContainer.GetSize()
        if self.activePage:
            self.activePage.SetSize(size)
        event.Skip()

class MiniFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, -1, 'MEGA Frame',
                size=(1000, 200))
        self.Bind(wx.EVT_CLOSE, self.OnCloseWindow)
#        self.Bind(wx.EVT_SIZE, self.OnSize)
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        self.nb = PFNotebook(self)

        self.nb.AddPage(TestPanel(self),"TEST 1")
        self.nb.AddPage(TestPanel(self),"TEST 2")
        self.nb.AddPage(TestPanel(self),"TEST 3")
        self.nb.AddPage(TestPanel(self),"TEST 4")
        self.nb.AddPage(TestPanel(self),"TEST 5")
        self.nb.AddPage(TestPanel(self),"TEST 6")

        mainSizer.Add(self.nb,1,wx.EXPAND)
        self.SetSizer(mainSizer)
        self.Layout()

#    def OnSize(self, event):
#        size = self.GetRect()
#        self.tabContainer.SetSize((size.width, -1))
#        self.tabContainer.UpdateSize()
#        self.tabContainer.Refresh()
#        event.Skip()
#    def OnLeftDown(self, event):
#        event.Skip()
#
#    def OnErase(self, event):
#        pass
    def OnCloseWindow(self, event):
        self.Destroy()


#    def OnPaint(self, event):
#        rect = self.GetRect()
#        canvas = wx.EmptyBitmap(rect.width, rect.height)
#        mdc = wx.BufferedPaintDC(self)
#        mdc.SelectObject(canvas)
#
#        mdc.SetBackground (wx.Brush(wx.SystemSettings_GetColour(wx.SYS_COLOUR_WINDOW)))
#        mdc.Clear()
#
#        selected = None
#        selpos = 0
#        tabsWidth = 0
#        offset = 10
#
#        for tab in self.tabs:
#            tabsWidth += tab.tabWidth - tab.lrZoneWidth/2
#
#        pos = tabsWidth
#
#        for i in xrange(len(self.tabs) - 1, -1, -1):
#            tab = self.tabs[i]
#            width = tab.tabWidth - tab.lrZoneWidth/2
#            pos -= width
#            if not tab.IsSelected():
#                mdc.DrawBitmap(tab.Render(),pos+offset,10, True)
#                tab.SetPosition((pos + offset, 10))
#            else:
#                selected = tab
#                selpos = pos + offset
#        if selected:
#            mdc.DrawBitmap(selected.Render(), selpos,10,True)
#            selected.SetPosition((selpos, 10))
#
#        mdc.SetPen( wx.Pen("#D0D0D0", width = 1 ) )
#        mdc.DrawLine(10,34,10,100)
#        mdc.DrawLine(10,100,tabsWidth + 18,100)
#        mdc.DrawLine(tabsWidth+18,100,tabsWidth+18,33)

class TestPanel ( wx.Panel ):

    def __init__( self, parent ):
        wx.Panel.__init__ ( self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, size = wx.Size( -1,-1 ), style = wx.TAB_TRAVERSAL )

        bSizer4 = wx.BoxSizer( wx.VERTICAL )

        self.m_staticText3 = wx.StaticText( self, wx.ID_ANY, u"TESSSSSSSSSST %s" % time.time(), wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_CENTRE )
        self.m_staticText3.Wrap( -1 )
        bSizer4.Add( self.m_staticText3, 1, wx.ALL|wx.EXPAND, 5 )

        self.m_button1 = wx.Button( self, wx.ID_ANY, u"MyButton", wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer4.Add( self.m_button1, 0, wx.ALL, 5 )

        self.m_textCtrl1 = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer4.Add( self.m_textCtrl1, 0, wx.ALL, 5 )

        self.m_staticline1 = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
        bSizer4.Add( self.m_staticline1, 0, wx.EXPAND |wx.ALL, 5 )

        self.m_gauge1 = wx.Gauge( self, wx.ID_ANY, 100, wx.DefaultPosition, wx.DefaultSize, wx.GA_HORIZONTAL )
        bSizer4.Add( self.m_gauge1, 0, wx.ALL, 5 )
        self.SetSizer( bSizer4 )
        self.Layout()

    def __del__( self ):
        pass


if __name__ == '__main__':
    app = wx.PySimpleApp()
    MiniFrame().Show()
    app.MainLoop()
