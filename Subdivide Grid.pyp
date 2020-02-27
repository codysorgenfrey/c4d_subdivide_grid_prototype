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

    def GetObjectBBox(self, obj):
        rad = obj.GetRad() * obj.GetAbsScale()
        center = obj.GetAbsPos() + obj.GetMp()
        thisBlf = center - rad
        thisTrb = center + rad
        return { 'blf': thisBlf, 'trb': thisTrb }

    def GetCollectiveBBox(self, splines):
        initBbox = self.GetObjectBBox(splines[0])
        blf = initBbox['blf']
        trb = initBbox['trb']
        for spline in splines:
            bbox = self.GetObjectBBox(spline)
            blf = self.minVector(bbox['blf'], blf)
            trb = self.maxVector(bbox['trb'], trb)
        
        return { 'blf': blf, 'trb': trb }

    def GetAbsRad(self, obj):
        bbox = self.GetObjectBBox(obj)
        return (bbox['trb'] - bbox['blf']) * 0.5

    def MakesFarSides(self, spline, corner):
        x = False
        y = False
        z = False
        if spline.GetName() == 'Rectangle':
            x = True
            y = True
            z = True
        if spline.GetName() == 'Rectangle.3':
            x = True
            y = False
            z = True
        if spline.GetName() == 'Rectangle.4':
            x = False
            y = True
            z = True
        return { 'x': x, 'y': y, 'z': z }
    
    def Execute(self, tag, doc, op, bt, priority, flags):
        obj = tag.GetObject()
        complete = tag[res_SG.SG_COMPLETE]

        # collect splines
        # if nothing in list, get children
        splines = obj.GetChildren()

        if splines is None: return c4d.EXECUTIONRESULT_OK
        
        # calculate collective bounding box
        cbbox = self.GetCollectiveBBox(splines)
        parentRad = obj.GetRad()
        parentMg = obj.GetMg()
        parentAnchor = parentMg.off
        parentObjSpaceAnchor = (-obj.GetMp()) + parentRad
        
        # calculate corners
        corners = [None] * 8
        corners[0] = cbbox['blf']
        corners[1] = cbbox['trb']
        corners[2] = c4d.Vector(corners[0].x, corners[0].y, corners[1].z)
        corners[3] = c4d.Vector(corners[0].x, corners[1].y, corners[0].z)
        corners[4] = c4d.Vector(corners[1].x, corners[0].y, corners[0].z)
        corners[5] = c4d.Vector(corners[1].x, corners[1].y, corners[0].z)
        corners[6] = c4d.Vector(corners[1].x, corners[0].y, corners[1].z)
        corners[7] = c4d.Vector(corners[0].x, corners[1].y, corners[1].z)
        def DistFromAnchor(obj, anchor=parentAnchor):
            return (anchor - obj).GetLength()
        corners.sort(key=DistFromAnchor)
        farthestCorner = corners[7]

        # calculate movements
        for spline in splines:
            if not spline[c4d.ID_BASEOBJECT_GENERATOR_FLAG]: continue

            splineRad = spline.GetRad()
            makesFarSides = self.MakesFarSides(spline, farthestCorner)

            # scale
            maxScaleOff = c4d.Vector(0.0001) # cannot be 0 or else connect object freaks out
            if makesFarSides['x']:
                if splineRad.x != 0: 
                    maxScaleOff.x = parentRad.x / splineRad.x
            if makesFarSides['y']:
                if splineRad.y != 0: 
                    maxScaleOff.y = parentRad.y / splineRad.y
            if makesFarSides['z']:
                if splineRad.z != 0: 
                    maxScaleOff.z = parentRad.z / splineRad.z

            scaleOff = c4d.Vector(1)
            scaleOff.x = c4d.utils.RangeMap(complete, 1.0, 0.0, 1.0, maxScaleOff.x, False, None)
            scaleOff.y = c4d.utils.RangeMap(complete, 1.0, 0.0, 1.0, maxScaleOff.y, False, None)
            scaleOff.z = c4d.utils.RangeMap(complete, 1.0, 0.0, 1.0, maxScaleOff.z, False, None)

            # position
            splineRelPos = spline.GetRelPos()
            maxPosOff = -splineRelPos
            splineObjSpaceAnchor = (-spline.GetMp()) + splineRad
            if makesFarSides['x']:
                if splineRad.x != 0:
                    origPosX = splineRelPos.x
                    newSplineObjSpaceAnchorX = (splineObjSpaceAnchor.x / splineRad.x) * parentRad.x
                    newPosX = newSplineObjSpaceAnchorX - parentObjSpaceAnchor.x
                    maxPosOff.x = newPosX - origPosX
            if makesFarSides['y']:
                if splineRad.y != 0:
                    origPosY = splineRelPos.y
                    newSplineObjSpaceAnchorY = (splineObjSpaceAnchor.y / splineRad.y) * parentRad.y
                    newPosY = newSplineObjSpaceAnchorY - parentObjSpaceAnchor.y
                    maxPosOff.y = newPosY - origPosY
            if makesFarSides['z']:
                if splineRad.z != 0:
                    origPosZ = splineRelPos.z
                    newSplineObjSpaceAnchorZ = (splineObjSpaceAnchor.z / splineRad.z) * parentRad.z
                    newPosZ = newSplineObjSpaceAnchorZ - parentObjSpaceAnchor.z
                    maxPosOff.z = newPosZ - origPosZ

            posOff = c4d.Vector(0)
            posOff.x = c4d.utils.RangeMap(complete, 1.0, 0.0, 0.0, maxPosOff.x, False, None)
            posOff.y = c4d.utils.RangeMap(complete, 1.0, 0.0, 0.0, maxPosOff.y, False, None)
            posOff.z = c4d.utils.RangeMap(complete, 1.0, 0.0, 0.0, maxPosOff.z, False, None)

            # apply
            spline.SetFrozenPos(posOff)
            spline.SetFrozenScale(scaleOff)
            spline.Message(c4d.MSG_UPDATE)

        return c4d.EXECUTIONRESULT_OK


if __name__ == '__main__':
    SubdivideGrid.Register()
