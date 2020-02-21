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

    def CaclCollectiveBoundingBox(self, splines):
        blf = c4d.Vector(0)
        trb = c4d.Vector(0)
        for spline in splines:
            rad = spline.GetRad()
            center = spline.GetMp()
            ml = spline.GetMl()
            thisBlf = (center - rad) * ml
            thisTrb = (center + rad) * ml
            blf = self.minVector(thisBlf, blf)
            trb = self.maxVector(thisTrb, trb)
        
        return {'blf': blf, 'trb': trb}
    
    def Execute(self, tag, doc, op, bt, priority, flags):
        obj = tag.GetObject()
        complete = tag[res_SG.SG_COMPLETE]

        # collect splines
        splines = []
        child = obj.GetDown()
        while child:
            splines.append(child)
            child = child.GetNext()
        
        # calculate collective bounding box
        cbbox = self.CaclCollectiveBoundingBox(splines)

        # while child:
        #     posMult = c4d.utils.RangeMap(complete, 0.0, 1.0, -1.0, 0.0, False, None)
        #     newScale = c4d.utils.RangeMap(complete, 0.0, 1.0, 0.0, 1.0, False, None)

        #     child.SetFrozenScale(c4d.Vector(newScale))
        #     child.SetFrozenPos(child.GetRelPos() * posMult)

        #     child = child.GetNext()

        return c4d.EXECUTIONRESULT_OK


if __name__ == '__main__':
    SubdivideGrid.Register()
