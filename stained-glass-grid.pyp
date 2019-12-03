# Copyright (C) 2019 Cody Sorgenfrey
import c4d
import os

class res(object):
    SGG_HOR = 1000,
    SGG_VERT = 1001,
res = res()


def load_bitmap(path):
    path = os.path.join(os.path.dirname(__file__), path)
    bmp = c4d.bitmaps.BaseBitmap()
    if bmp.InitWith(path)[0] != c4d.IMAGERESULT_OK:
        bmp = None
    return bmp

class StainedGlassGrid(c4d.plugins.ObjectData):
    PLUGIN_ID = 1054108
    PLUGIN_NAME = 'Stained Glass Grid'
    PLUGIN_INFO = c4d.OBJECT_GENERATOR | c4d.OBJECT_INPUT | c4d.OBJECT_ISSPLINE
    PLUGIN_DESC = 'Ostainedglassgrid'
    PLUGIN_ICON = load_bitmap('res/icons/stained glass grid.tiff')
    PLUGIN_DISKLEVEL = 0
    INPUT_SPLINE = None

    @classmethod
    def Register(cls):
        return c4d.plugins.RegisterObjectPlugin(
            cls.PLUGIN_ID,
            cls.PLUGIN_NAME,
            cls,
            cls.PLUGIN_DESC,
            cls.PLUGIN_INFO,
            cls.PLUGIN_ICON,
            cls.PLUGIN_DISKLEVEL
        )

    def Init(self, node):
        self.InitAttr(node, float, res.SGG_HOR)
        self.InitAttr(node, float, res.SGG_VERT)

        node[res.SGG_HOR] = 1.0
        node[res.SGG_VERT] = 1.0
        
        return True

    def MakeSpline(self, op):
        hor = float(op[res.SGG_HOR])
        vert = float(op[res.SGG_VERT])
        outObj = self.INPUT_SPLINE.GetClone(c4d.COPYFLAGS_NONE)
        size = self.INPUT_SPLINE.GetRad() * 2

        for x in range(outObj.GetPointCount()):
            p = outObj.GetPoint(x)
            if p.x != 0.0 and p.x != size.x:
                p.x = c4d.utils.RangeMap(hor, 0.0, 1.0, 0.0, float(p.x), False)
            if -p.y != 0.0 and -p.y != size.y:
                p.y = c4d.utils.RangeMap(vert, 0.0, 1.0, 0.0, float(p.y), False)
            if -p.z != 0.0 and -p.z != size.z:
                p.z = c4d.utils.RangeMap(vert, 0.0, 1.0, 0.0, float(p.z), False)
            outObj.SetPoint(x, p)

        outObj.Message(c4d.MSG_UPDATE)
        return outObj

    def GetContour(self, op, doc, lod, bt):
        if self.INPUT_SPLINE is None: return None
        return self.MakeSpline(op)

    def GetVirtualObjects(self, op, hh):
        inObj = op.GetDown()
        if inObj is None: return None

        hClone = op.GetAndCheckHierarchyClone(hh, inObj, c4d.HIERARCHYCLONEFLAGS_ASSPLINE, False)

        if not hClone['dirty']: return hClone['clone']
        if hClone['clone'] is None: return None
        if not bool(hClone['clone'].GetInfo() & c4d.OBJECT_ISSPLINE):
            self.INPUT_SPLINE = None
            return None

        self.INPUT_SPLINE = hClone['clone']
        return self.MakeSpline(op)


if __name__ == '__main__':
    StainedGlassGrid.Register()
