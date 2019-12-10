# Copyright (C) 2019 Cody Sorgenfrey
import c4d # pylint: disable=import-error
import os

class res_SG(object):
    SG_COMPLETE = 1000
    SG_HOR = 1001
    SG_VERT = 1002
res_SG = res_SG()

class res_SGD(object):
    SGD_COMPLETE = 1000
    SGD_OFF = 1001
    SGD_OFF_MULT = 1002
res_SGD = res_SGD()

def isclose(a, b, rel_tol=1e-09, abs_tol=0.0):
    return abs(a-b) <= max(rel_tol * max(abs(a), abs(b)), abs_tol)

def load_bitmap(path):
    path = os.path.join(os.path.dirname(__file__), path)
    bmp = c4d.bitmaps.BaseBitmap()
    if bmp.InitWith(path)[0] != c4d.IMAGERESULT_OK:
        bmp = None
    return bmp

class SubdivideGridDriver(c4d.plugins.TagData):
    PLUGIN_ID = 1054125
    PLUGIN_NAME = 'Subdivide Grid Driver'
    PLUGIN_INFO = c4d.TAG_VISIBLE | c4d.TAG_EXPRESSION
    PLUGIN_DESC = 'Tsubdividegriddriver'
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
        self.InitAttr(node, float, res_SGD.SGD_COMPLETE)
        self.InitAttr(node, float, res_SGD.SGD_OFF)
        self.InitAttr(node, float, res_SGD.SGD_OFF_MULT)

        node[res_SGD.SGD_COMPLETE] = 100.0
        node[res_SGD.SGD_OFF] = -12.0
        node[res_SGD.SGD_OFF_MULT] = 1.0
        
        return True

    def RecursiveSetDirty(self, obj):
        while obj:
            if obj.GetType() == SubdivideGrid.PLUGIN_ID:
                obj.GetRealSpline()

            child = obj.GetDown()
            if child:
                self.RecursiveSetDirty(child)
            
            obj = obj.GetNext()
    
    def Execute(self, tag, doc, op, bt, priority, flags):
        self.RecursiveSetDirty(op) # called to update objects on every frame for frame offsets
        return c4d.EXECUTIONRESULT_OK

class SubdivideGrid(c4d.plugins.ObjectData):
    PLUGIN_ID = 1054108
    PLUGIN_NAME = 'Subdivide Grid'
    PLUGIN_INFO = c4d.OBJECT_GENERATOR | c4d.OBJECT_INPUT | c4d.OBJECT_ISSPLINE
    PLUGIN_DESC = 'Osubdividegrid'
    PLUGIN_ICON = load_bitmap('res/icons/subdivide grid.tiff')
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
        self.InitAttr(node, float, res_SG.SG_COMPLETE)
        self.InitAttr(node, float, res_SG.SG_HOR)
        self.InitAttr(node, float, res_SG.SG_VERT)

        node[res_SG.SG_COMPLETE] = 100.0
        node[res_SG.SG_HOR] = 0.0
        node[res_SG.SG_VERT] = 0.0

        if not hasattr(self, 'LAST_FRAME'):
            self.LAST_FRAME = -1
        if not hasattr(self, 'DRIVER'):
            self.DRIVER = None
        
        return True

    def GetDEnabling(self, node, id, t_data, flags, itemdesc):
        if self.DRIVER:
            paramID = id[0].id
            if paramID == res_SG.SG_COMPLETE:
                return False

        return True

    def RecursiveCollectInputs(self, op, doc, obj):
        inObj = c4d.SplineObject(0, c4d.SPLINETYPE_BEZIER)
        inObj[c4d.SPLINEOBJECT_CLOSED] = True

        while obj:
            if not obj[c4d.ID_BASEOBJECT_GENERATOR_FLAG]:
                obj = obj.GetNext()
                continue

            if obj.GetType() == c4d.Ospline:
                spline = obj
            elif obj.GetType() == SubdivideGrid.PLUGIN_ID:
                spline = obj.GetRealSpline()
            else:
                objClone = obj.GetClone()
                result = c4d.utils.SendModelingCommand(
                    c4d.MCOMMAND_CURRENTSTATETOOBJECT,
                    [objClone],
                    c4d.MODELINGCOMMANDMODE_ALL,
                    c4d.BaseContainer(),
                    doc,
                    c4d.MODELINGCOMMANDFLAGS_NONE,
                    )
                if result is not False:
                    spline = result[0]
                else:
                    spline = obj.GetRealSpline()

            if spline is None:
                obj = obj.GetNext()
                continue
            if not (spline.GetInfo() & c4d.OBJECT_ISSPLINE):
                obj = obj.GetNext()
                continue
            
            segCnt = spline.GetSegmentCount()
            pntCnt = spline.GetPointCount()
            tanCnt = spline.GetTangentCount()
            mySegCnt = inObj.GetSegmentCount()
            myPntCnt = inObj.GetPointCount()
            myTanCnt = inObj.GetTangentCount()
            newPntCnt = myPntCnt + pntCnt
            newSegCnt = mySegCnt + segCnt
            newTanCnt = myTanCnt + tanCnt
            objMarr = obj.GetMl()

            inObj.ResizeObject(newPntCnt, newSegCnt)
            for x in range(myPntCnt, newPntCnt):
                p = spline.GetPoint(x - myPntCnt)
                inObj.SetPoint(x, objMarr * p)

            for x in range(myTanCnt, newTanCnt):
                tan = spline.GetTangent(x - myTanCnt)
                inObj.SetTangent(x, tan['vl'], tan['vr'])

            for x in range(mySegCnt, newSegCnt):
                if x - mySegCnt < 0: # for splines with no segments
                    inObj.SetSegment(x, pntCnt, spline.IsClosed())
                else:
                    seg = spline.GetSegment(x - mySegCnt)
                    inObj.SetSegment(x, seg['cnt'], seg['closed'])
            
            inObj.Message(c4d.MSG_UPDATE) # because we updated its points
            obj = obj.GetNext()

        return inObj

    def SegmentIsRect(self, obj, start, end):
        isRect = True
        for x in range(start, end):
            ni = x + 1
            if ni >= end:
                ni = start
            pi = x - 1
            if pi < start:
                pi = end - 1
            pp = obj.GetPoint(pi)
            p = obj.GetPoint(x)
            np = obj.GetPoint(ni)

            pd = pp - p
            nd = p - np
            dot = pd.Dot(nd)

            isRect = isRect and dot == 0

        return isRect

    def PointMakesBorder(self, p, boundsMin, boundMax):
        makesBorder = c4d.Vector(0)
        if isclose(p.x, boundsMin.x) or isclose(abs(p.x), boundMax.x):
            makesBorder.x = 1
        if isclose(p.y, boundsMin.y) or isclose(abs(p.y), boundMax.y):
            makesBorder.y = 1
        if isclose(p.z, boundsMin.z) or isclose(abs(p.z), boundMax.z):
            makesBorder.z = 1
        return makesBorder

    def CompletionAtTime(self, obj, doc, time):
        cTrack = obj.FindCTrack(res_SGD.SGD_COMPLETE)
        if cTrack is None:
            return obj[res_SGD.SGD_COMPLETE]
        
        return cTrack.GetValue(doc, time, doc.GetFps())

    def MakeSpline(self, doc, op, inObj):
        curTime = doc.GetTime()
        fps = doc.GetFps()
        horOff = c4d.BaseTime(op[res_SG.SG_HOR], fps)
        vertOff = c4d.BaseTime(op[res_SG.SG_VERT], fps)

        parent = op.GetUp()
        tag = op.GetTag(SubdivideGridDriver.PLUGIN_ID)
        level = 0
        while parent and not tag:
            if parent.GetType() == SubdivideGrid.PLUGIN_ID:
                level += 1
            tag = parent.GetTag(SubdivideGridDriver.PLUGIN_ID)
            parent = parent.GetUp()

        driver = op.GetClone()
        self.DRIVER = False
        offsetStep = 0.0
        if tag is not None:
            driver = tag.GetClone()
            self.DRIVER = True
            offsetStep = tag[res_SGD.SGD_OFF]
            offsetMult = tag[res_SGD.SGD_OFF_MULT]
            offsetStep *= offsetMult

        levelOff = c4d.BaseTime(offsetStep * level, fps)
        hor = self.CompletionAtTime(driver, doc, curTime + horOff + levelOff)
        vert = self.CompletionAtTime(driver, doc, curTime + vertOff + levelOff)
        outObj = inObj.GetClone()
        size = inObj.GetRad() * 2

        pointOff = 0
        segCount = outObj.GetSegmentCount()
        for x in range(segCount):
            seg = outObj.GetSegment(x)
            newPointOff = pointOff + seg['cnt']
            isRect = self.SegmentIsRect(outObj, pointOff, newPointOff)
            if not isRect:
                scale = min(hor, vert)
                movePoint = outObj.GetPoint(pointOff)
                movedPoint = c4d.Vector()
                movedPoint.x = c4d.utils.RangeMap(vert, 0.0, 1.0, 0.0, movePoint.x, False)
                movedPoint.y = c4d.utils.RangeMap(hor, 0.0, 1.0, 0.0, movePoint.y, False)
                movedPoint.z = c4d.utils.RangeMap(hor, 0.0, 1.0, 0.0, movePoint.z, False)
                for y in range(pointOff, newPointOff):
                    p = outObj.GetPoint(y)
                    scaleDiff = p - movePoint
                    scaleOff = scaleDiff * scale
                    p = movedPoint + scaleOff
                    outObj.SetPoint(y, p)
            else:
                for y in range(pointOff, newPointOff):
                    p = outObj.GetPoint(y)
                    locked = self.PointMakesBorder(p, c4d.Vector(0), size)
                    if not bool(locked.x):
                        p.x = c4d.utils.RangeMap(vert, 0.0, 1.0, 0.0, p.x, False)
                    if not bool(locked.y):
                        p.y = c4d.utils.RangeMap(hor, 0.0, 1.0, 0.0, p.y, False)
                    if not bool(locked.z):
                        p.z = c4d.utils.RangeMap(hor, 0.0, 1.0, 0.0, p.z, False)
                    outObj.SetPoint(y, p)
            
            pointOff = newPointOff

        outObj.Message(c4d.MSG_UPDATE)
        return outObj

    def CheckDirty(self, op, doc):
        frame = doc.GetTime().GetFrame(doc.GetFps())
        if self.LAST_FRAME != frame:
            self.LAST_FRAME = frame
            op.SetDirty(c4d.DIRTYFLAGS_DATA)

    def GetContour(self, op, doc, lod, bt):
        inObj = op.GetDown()
        if inObj is None: return None
        inSpline = self.RecursiveCollectInputs(op, doc, inObj)
        return self.MakeSpline(doc, op, inSpline)

    def GetVirtualObjects(self, op, hh):
        doc = op.GetDocument()
        if doc is None: return None

        inObj = op.GetDown()
        if inObj is None: return None

        hClone = op.GetAndCheckHierarchyClone(hh, inObj, c4d.HIERARCHYCLONEFLAGS_ASSPLINE, True)
        if not hClone['dirty']: return hClone['clone']

        return self.GetContour(op, doc, None, None)

class SubdivideGridGroup(c4d.plugins.CommandData):
    PLUGIN_ID = 1054128
    PLUGIN_NAME = 'Subdivide Grid Group'
    PLUGIN_HELP = 'Group selected objects under a Subdivide Grid'
    PLUGIN_INFO = 0
    PLUGIN_ICON = load_bitmap('res/icons/subdivide grid.tiff')
    PLUGIN_DISKLEVEL = 0

    @classmethod
    def Register(cls):
        return c4d.plugins.RegisterCommandPlugin(
            cls.PLUGIN_ID,
            cls.PLUGIN_NAME,
            cls.PLUGIN_INFO,
            cls.PLUGIN_ICON,
            cls.PLUGIN_HELP,
            SubdivideGridGroup(),
        )

    def Execute(self, doc):
        # to be written
        return True

if __name__ == '__main__':
    SubdivideGrid.Register()
    SubdivideGridDriver.Register()
    SubdivideGridGroup.Register()
