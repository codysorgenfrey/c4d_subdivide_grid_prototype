# Copyright (C) 2019 Cody Sorgenfrey
import c4d # pylint: disable=import-error
import os

class res_SGG(object):
    SGG_COMPLETE = 1000,
    SGG_HOR = 1001,
    SGG_VERT = 1002,
res_SGG = res_SGG()

class res_SGGD(object):
    SGGD_COMPLETE = 1000,
    SGGD_OFF = 1001,
    SGGD_OFF_MULT = 1002,
res_SGGD = res_SGGD()

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
        self.InitAttr(node, float, res_SGG.SGG_COMPLETE)
        self.InitAttr(node, float, res_SGG.SGG_HOR)
        self.InitAttr(node, float, res_SGG.SGG_VERT)

        node[res_SGG.SGG_COMPLETE] = 100.0
        node[res_SGG.SGG_HOR] = 0.0
        node[res_SGG.SGG_VERT] = 0.0
        
        return True

    def MakeSpline(self, op):
        par = op.GetUp()
        tag = op.GetTag(StainedGlassGridDriver.PLUGIN_ID)
        while par:
            tag = par.GetTag(StainedGlassGridDriver.PLUGIN_ID)
            par = par.GetUp()

        driver = op
        if tag is not None:
            driver = tag

        doc = op.GetDocument()
        curTime = doc.GetTime()
        horOff = c4d.BaseTime(op[res_SGG.SGG_HOR], doc.GetFps())
        vertOff = c4d.BaseTime(op[res_SGG.SGG_VERT], doc.GetFps())
        doc.AnimateObject(driver, curTime + horOff, c4d.ANIMATEFLAGS_NONE)
        hor = driver[res_SGG.SGG_COMPLETE]
        doc.AnimateObject(driver, curTime + vertOff, c4d.ANIMATEFLAGS_NONE)
        vert = driver[res_SGG.SGG_COMPLETE]
        outObj = self.INPUT_SPLINE.GetClone(c4d.COPYFLAGS_NONE)
        size = self.INPUT_SPLINE.GetRad() * 2

        for x in range(outObj.GetPointCount()):
            p = outObj.GetPoint(x)
            if (not isclose(p.x, 0.0)) and (not isclose(abs(p.x), size.x)):
                p.x = c4d.utils.RangeMap(vert, 0.0, 1.0, 0.0, p.x, False)
            if (not isclose(p.y, 0.0)) and (not isclose(abs(p.y), size.y)):
                p.y = c4d.utils.RangeMap(hor, 0.0, 1.0, 0.0, p.y, False)
            if (not isclose(p.z, 0.0)) and (not isclose(abs(p.z), size.z)):
                p.z = c4d.utils.RangeMap(hor, 0.0, 1.0, 0.0, p.z, False)
            outObj.SetPoint(x, p)

        outObj.Message(c4d.MSG_UPDATE)
        return outObj

    def GetContour(self, op, doc, lod, bt):
        if self.INPUT_SPLINE is None: return None
        return self.MakeSpline(op)

    def GetVirtualObjects(self, op, hh):
        inObj = op.GetDown()
        if inObj is None:
            self.INPUT_SPLINE = None
            return None

        hClone = op.GetAndCheckHierarchyClone(hh, inObj, c4d.HIERARCHYCLONEFLAGS_ASSPLINE, False)

        if not hClone['dirty']: return hClone['clone']
        if hClone['clone'] is None: return None
        if not bool(hClone['clone'].GetInfo() & c4d.OBJECT_ISSPLINE):
            self.INPUT_SPLINE = None
            return None

        self.INPUT_SPLINE = hClone['clone']
        return self.MakeSpline(op)

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

    def Init(self, node):
        self.InitAttr(node, float, res_SGGD.SGGD_COMPLETE)
        self.InitAttr(node, float, res_SGGD.SGGD_OFF)
        self.InitAttr(node, float, res_SGGD.SGGD_OFF_MULT)

        node[res_SGGD.SGGD_COMPLETE] = 100.0
        node[res_SGGD.SGGD_OFF] = -12.0
        node[res_SGGD.SGGD_OFF_MULT] = 1.0
        
        return True

    def RecursiveSetParams(self, tag, doc, obj, level):
        while obj:
            if obj.GetType() == StainedGlassGrid.PLUGIN_ID:
                curTime = doc.GetTime()
                timeOffStep = c4d.BaseTime(tag[res_SGGD.SGGD_OFF], doc.GetFps())
                timeStepMult = tag[res_SGGD.SGGD_OFF_MULT]
                timeOff = c4d.BaseTime(timeOffStep.Get() * (level))
                newTime = curTime + timeOff

                doc.AnimateObject(tag, newTime, c4d.ANIMATEFLAGS_NONE)
                obj[res_SGG.SGG_COMPLETE] = tag[res_SGGD.SGGD_COMPLETE]

            child = obj.GetDown()
            if child:
                if child.GetType() == StainedGlassGrid.PLUGIN_ID:
                    level += 1
                self.RecursiveSetParams(tag, doc, child, level)
                
            obj = obj.GetNext()
    
    def Execute(self, tag, doc, op, bt, priority, flags):
        # if op.GetType() == StainedGlassGrid.PLUGIN_ID:
        #     op[res_SGG.SGG_COMPLETE] = tag[res_SGGD.SGGD_COMPLETE]
        #     self.RecursiveSetParams(tag, doc, op.GetDown(), 0)
        
        return c4d.EXECUTIONRESULT_OK

    

if __name__ == '__main__':
    StainedGlassGrid.Register()
    StainedGlassGridDriver.Register()
