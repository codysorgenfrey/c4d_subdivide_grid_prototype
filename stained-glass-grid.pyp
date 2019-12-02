# Copyright (C) 2019 Cody Sorgenfrey
import c4d
import os

class res(object):
    QUANTIZE_SPLINE_GROUP = 1000
    QUANTIZE_SPLINE_ORDER = 1002
    QUANTIZE_SPLINE_ORDER_XYZ = 1
    QUANTIZE_SPLINE_ORDER_XZY = 2
    QUANTIZE_SPLINE_ORDER_YXZ = 3
    QUANTIZE_SPLINE_ORDER_YZX = 4
    QUANTIZE_SPLINE_ORDER_ZYX = 5
    QUANTIZE_SPLINE_ORDER_ZXY = 6
res = res()


def load_bitmap(path):
    path = os.path.join(os.path.dirname(__file__), path)
    bmp = c4d.bitmaps.BaseBitmap()
    if bmp.InitWith(path)[0] != c4d.IMAGERESULT_OK:
        bmp = None
    return bmp

class StainedGlassGrid(c4d.plugins.ObjectData):
    PLUGIN_ID = 1054108
    PLUGIN_NAME = 'Quantize Spline'
    PLUGIN_INFO = c4d.OBJECT_GENERATOR | c4d.OBJECT_INPUT
    PLUGIN_DESC = 'Ostainedglassgrid'
    PLUGIN_ICON = load_bitmap('res/icons/stained glass grid.tiff')
    PLUGIN_DISKLEVEL = 0

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
        self.InitAttr(node, int, [res.QUANTIZE_SPLINE_ORDER])

        node[res.QUANTIZE_SPLINE_ORDER] = 1
        
        return True

    def GetVirtualObjects(self, op, hh):
        inObj = op.GetDown()
        if inObj is None: return None

        hClone = op.GetAndCheckHierarchyClone(hh, inObj, c4d.HIERARCHYCLONEFLAGS_ASSPLINE, False)

        if not hClone['dirty']: return hClone['clone']
        if hClone['clone'] is None: return None

        return hClone['clone']


if __name__ == '__main__':
    StainedGlassGrid.Register()
