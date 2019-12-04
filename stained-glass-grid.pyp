# Copyright (C) 2019 Cody Sorgenfrey
import c4d
import os

class res_SGG(object):
    SGG_COMPLETE = 1000,
    SGG_HOR = 1001,
    SGG_VERT = 1002,
res_SGG = res_SGG()

def isclose(a, b, rel_tol=1e-09, abs_tol=0.0):
    return abs(a-b) <= max(rel_tol * max(abs(a), abs(b)), abs_tol)

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
        self.InitAttr(node, float, res_SGG.SGG_HOR)
        self.InitAttr(node, float, res_SGG.SGG_VERT)

        node[res_SGG.SGG_HOR] = 1.0
        node[res_SGG.SGG_VERT] = 1.0
        
        return True

    def MakeSpline(self, op):
        hor = float(op[res_SGG.SGG_HOR])
        vert = float(op[res_SGG.SGG_VERT])
        outObj = self.INPUT_SPLINE.GetClone(c4d.COPYFLAGS_NONE)
        size = self.INPUT_SPLINE.GetRad() * 2

        for x in range(outObj.GetPointCount()):
            p = outObj.GetPoint(x)
            if (not isclose(p.x, 0.0)) and (not isclose(abs(p.x), size.x)):
                p.x = c4d.utils.RangeMap(hor, 0.0, 1.0, 0.0, float(p.x), False)
            if (not isclose(p.y, 0.0)) and (not isclose(abs(p.y), size.y)):
                p.y = c4d.utils.RangeMap(vert, 0.0, 1.0, 0.0, float(p.y), False)
            if (not isclose(p.z, 0.0)) and (not isclose(abs(p.z), size.z)):
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

class res_SGGD(object):
    SGGD_COMPLETE = 1000,
    SGGD_OFF = 1001,
    SGGD_OFF_MULT = 1002,
res_SGGD = res_SGGD()

class StainedGlassGridDriver(c4d.plugins.TagData):
    PLUGIN_ID = 1054125
    PLUGIN_NAME = 'Stained Glass Grid Driver'
    PLUGIN_INFO = c4d.TAG_VISIBLE | c4d.TAG_EXPRESSION
    PLUGIN_DESC = 'Tstainedglassgriddriver'
    PLUGIN_ICON = load_bitmap('res/icons/stained glass grid.tiff')
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

    def RecursiveSetParams(self, tag, doc, obj, level):
        while obj:
            if obj.GetType() == StainedGlassGrid.PLUGIN_ID:
                curTime = doc.GetTime()
                timeOffStep = op[c4d.ID_USERDATA,4]
                timeStepMult = op[c4d.ID_USERDATA, 5]
                timeOff = c4d.BaseTime(timeOffStep.Get() * (level))
                newTime = curTime + timeOff

                doc.AnimateObject(op, newTime, c4d.ANIMATEFLAGS_NONE)
                obj[1000] = op[c4d.ID_USERDATA, 2]
                obj[1001] = op[c4d.ID_USERDATA, 3]

            child = obj.GetDown()
            if child:
                if child.GetType() == StainedGlassGrid.PLUGIN_ID:
                    level += 1
                self.RecursiveSetParams(tag, doc, child, level)
                
            obj = obj.GetNext()
    
    def Execute(self, tag, doc, op, bt, priority, flags):
        if op.GetType() == StainedGlassGrid.PLUGIN_ID:
            op[res_SGG.SGG_COMPLETE] = tag[res_SGGD.SGGD_COMPLETE]
            self.RecursiveSetParams(tag, doc, op.GetDown(), 0)

    

if __name__ == '__main__':
    StainedGlassGrid.Register()
    StainedGlassGridDriver.Register()
