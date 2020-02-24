# Copyright (C) 2019 Cody Sorgenfrey
import c4d # pylint: disable=import-error
import os
import math

def load_bitmap(path):
    path = os.path.join(os.path.dirname(__file__), path)
    bmp = c4d.bitmaps.BaseBitmap()
    if bmp.InitWith(path)[0] != c4d.IMAGERESULT_OK:
        bmp = None
    return bmp

def isclose(a, b, rel_tol=1e-09, abs_tol=0.0):
    return abs(a-b) <= max(rel_tol * max(abs(a), abs(b)), abs_tol)

class res_SG(object):
    SG_COMPLETE = 1000
res_SG = res_SG()

class SubdivideGrid(c4d.plugins.TagData):
    PLUGIN_ID = 1054125
    PLUGIN_NAME = 'Subdivide Grid'
    PLUGIN_INFO = c4d.TAG_VISIBLE | c4d.TAG_EXPRESSION
    PLUGIN_DESC = 'Tsubdividegrid'
    PLUGIN_ICON = load_bitmap('res/icons/subdivide grid.tiff')
    PLUGIN_DISKLEVEL = 0

    @classmethod
    def Register(cls):
        return c4d.plugins.RegisterTagPlugin(
            cls.PLUGIN_ID,
            cls.PLUGIN_NAME,
            cls.PLUGIN_INFO,
            cls,
            cls.PLUGIN_DESC,
            cls.PLUGIN_ICON,
            cls.PLUGIN_DISKLEVEL,
        )

    def Init(self, node):
        self.InitAttr(node, float, res_SG.SG_COMPLETE)

        node[res_SG.SG_COMPLETE] = 100.0
        
        return True

    def CalcObjectBBox(self, obj):
        if (obj.GetType() == c4d.Onull):
            children = obj.GetChildren()
            return self.GetCollectiveBBox(children)
        rad = obj.GetRad()
        center = obj.GetMp()
        mg = obj.GetMg()
        thisBlf = (center - rad) * mg
        thisTrb = (center + rad) * mg
        return { 'blf': thisBlf, 'trb': thisTrb }

    def maxVector(self, a, b):
        newVec = c4d.Vector()
        newVec.x = max(a.x, b.x)
        newVec.y = max(a.y, b.y)
        newVec.z = max(a.z, b.z)
        return newVec

    def minVector(self, a, b):
        newVec = c4d.Vector()
        newVec.x = min(a.x, b.x)
        newVec.y = min(a.y, b.y)
        newVec.z = min(a.z, b.z)
        return newVec

    def CaclCollectiveBBox(self, splines):
        blf = c4d.Vector(0)
        trb = c4d.Vector(0)
        for spline in splines:
            bbox = self.CalcObjectBBox(spline)
            blf = self.minVector(bbox['blf'], blf)
            trb = self.maxVector(bbox['trb'], trb)
        
        return { 'blf': blf, 'trb': trb }

    def GetFarthestCorner(self, corners, anchor):
        
        return None

    def GetClosestCorner(self, corners, anchor):

        return None

    def MakesCloseSides(self, spline, corner):
        x = False
        y = False
        z = False
        return { 'x': x, 'y': y, 'z': z }

    def MakesFarSides(self, spline, corner):
        x = True
        y = True
        z = True
        return { 'x': x, 'y': y, 'z': z }
    
    def Execute(self, tag, doc, op, bt, priority, flags):
        obj = tag.GetObject()
        complete = tag[res_SG.SG_COMPLETE]

        # collect splines
        # if nothing in list, get children
        splines = obj.GetChildren()
        
        # calculate collective bounding box
        cbbox = self.CaclCollectiveBBox(splines)
        # calculate corners
        corners = [c4d.Vector()] * 8
        corners[0] = cbbox['blf']
        corners[1] = cbbox['trb']
        corners[2] = c4d.Vector(corners[0].x, corners[0].y, corners[1].z)
        corners[3] = c4d.Vector(corners[0].x, corners[1].y, corners[0].z)
        corners[4] = c4d.Vector(corners[1].x, corners[0].y, corners[0].z)
        corners[5] = c4d.Vector(corners[1].x, corners[1].y, corners[0].z)
        corners[6] = c4d.Vector(corners[1].x, corners[0].y, corners[1].z)
        corners[7] = c4d.Vector(corners[0].x, corners[1].y, corners[1].z)
        def DistFromAnchor(obj, anchor=obj.GetAbsPos()):
            return (anchor - obj).GetLength()
        corners.sort(key=DistFromAnchor)
        # farthest and closest corners
        closestCorner = corners[0]
        farthestCorner = corners[7]

        for spline in splines:
            frozenPos = c4d.Vector(0)
            frozenScale = c4d.Vector(1)
            makesCloseSides = self.MakesCloseSides(spline, closestCorner)
            makesFarSides = self.MakesFarSides(spline, farthestCorner)

            spline.SetFrozenPos(frozenPos)
            spline.SetFrozenScale(frozenScale)
            spline.Message(c4d.MSG_UPDATE)

        return c4d.EXECUTIONRESULT_OK


if __name__ == '__main__':
    SubdivideGrid.Register()
