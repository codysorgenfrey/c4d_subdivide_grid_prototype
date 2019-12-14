# Copyright (C) 2019 Cody Sorgenfrey
import c4d # pylint: disable=import-error
import os
import math

class res_SG(object):
    SG_COMPLETE = 1000
    SG_HOR = 1001
    SG_VERT = 1002
    SG_CAP = 1003
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

def GetObjectSpline(obj, doc):
    if obj.GetType() == c4d.Ospline:
        return obj
    
    if obj.GetType() == SubdivideGrid.PLUGIN_ID:
        return obj.GetRealSpline()
    
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

    if not (spline.GetInfo() & c4d.OBJECT_ISSPLINE):
        return None

    return spline

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
        self.InitAttr(node, bool, res_SG.SG_CAP)

        node[res_SG.SG_COMPLETE] = 100.0
        node[res_SG.SG_HOR] = 0.0
        node[res_SG.SG_VERT] = 0.0
        node[res_SG.SG_CAP] = False

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

    def MergeSplines(self, spline1, spline2):
        segCnt = spline1.GetSegmentCount()
        pntCnt = spline1.GetPointCount()
        tanCnt = spline1.GetTangentCount()
        segCnt2 = spline2.GetSegmentCount()
        pntCnt2 = spline2.GetPointCount()
        tanCnt2 = spline2.GetTangentCount()
        newPntCnt = pntCnt2 + pntCnt
        newSegCnt = segCnt2 + segCnt
        newTanCnt = tanCnt2 + tanCnt
        objMarr = spline2.GetMl()

        spline1.ResizeObject(newPntCnt, newSegCnt)
        for x in range(pntCnt2, newPntCnt):
            p = spline2.GetPoint(x - pntCnt2)
            spline1.SetPoint(x, objMarr * p)

        for x in range(tanCnt2, newTanCnt):
            tan = spline2.GetTangent(x - tanCnt2)
            spline1.SetTangent(x, tan['vl'], tan['vr'])

        for x in range(segCnt2, newSegCnt):
            if x - segCnt2 < 0: # for splines with no segments
                spline1.SetSegment(x, pntCnt, spline2.IsClosed())
            else:
                seg = spline2.GetSegment(x - segCnt2)
                spline1.SetSegment(x, seg['cnt'], seg['closed'])
        
        spline1.Message(c4d.MSG_UPDATE) # because we updated its points
        return spline1

    def RecursiveCollectInputs(self, op, doc, obj):
        inObj = c4d.SplineObject(0, c4d.SPLINETYPE_BEZIER)
        inObj[c4d.SPLINEOBJECT_CLOSED] = True

        while obj:
            if not obj[c4d.ID_BASEOBJECT_GENERATOR_FLAG]:
                obj = obj.GetNext()
                continue

            spline = GetObjectSpline(obj, doc)
            if spline is None:
                obj = obj.GetNext()
                continue

            inObj = self.MergeSplines(inObj, spline)

            # child = obj.GetDown()
            # if child is not None:
            #     if child.GetType() == c4d.Onull:
            #         childSpline = self.RecursiveCollectInputs(op, doc, child)
            #         inObj = self.MergeSplines(inObj, childSpline)

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

    def GetSegmentDims(self, obj, start, end):
        trb = obj.GetPoint(start)
        blf = obj.GetPoint(start)
        for x in range(start, end):
            p = obj.GetPoint(x)
            trb.x = max(trb.x, p.x)
            trb.y = max(trb.y, p.y)
            blf.x = min(blf.x, p.x)
            blf.y = min(blf.y, p.y)

        return [trb, blf]

    def PointMakesBorder(self, p, boundsMin, boundMax):
        makesBorder = c4d.Vector(0)
        if isclose(p.x, boundsMin.x) or isclose(abs(p.x), boundMax.x):
            makesBorder.x = 1
        if isclose(p.y, boundsMin.y) or isclose(abs(p.y), boundMax.y):
            makesBorder.y = 1
        return makesBorder

    def CompletionAtTime(self, obj, doc, time):
        cTrack = obj.FindCTrack(res_SGD.SGD_COMPLETE)
        if cTrack is None:
            return obj[res_SGD.SGD_COMPLETE]
        
        return cTrack.GetValue(doc, time, doc.GetFps())

    def AnimateGrid(self, doc, op, inSpline, outObj):
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
        size = inSpline.GetRad() * 2

        pointOff = 0
        segCount = inSpline.GetSegmentCount()
        for x in range(segCount):
            seg = inSpline.GetSegment(x)
            newPointOff = pointOff + seg['cnt']
            isRect = self.SegmentIsRect(inSpline, pointOff, newPointOff)
            dims = self.GetSegmentDims(inSpline, pointOff, newPointOff)
            scaledDims = [c4d.Vector(), c4d.Vector()]

            for y in range(len(dims)):
                locked = self.PointMakesBorder(dims[y], c4d.Vector(0), size)
                if not bool(locked.x):
                    scaledDims[y].x = c4d.utils.RangeMap(vert, 0.0, 1.0, 0.0, dims[y].x, False)
                else:
                    scaledDims[y].x = dims[y].x
                if not bool(locked.y):
                    scaledDims[y].y = c4d.utils.RangeMap(hor, 0.0, 1.0, 0.0, dims[y].y, False)
                else:
                    scaledDims[y].y = dims[y].y
            
            if not isRect:
                width = scaledDims[0].x - scaledDims[1].x
                height = scaledDims[0].y - scaledDims[1].y
                scale = min(width, height)
                locked = self.PointMakesBorder(scaledDims[0], c4d.Vector(), size)
                if not bool(locked.x):
                    scaledDims[0].x = scaledDims[1].x + scale
                if not bool(locked.y):
                    scaledDims[0].y = scaledDims[1].y + scale
                locked = self.PointMakesBorder(scaledDims[1], c4d.Vector(), size)
                if not bool(locked.x):
                    scaledDims[1].x = scaledDims[0].x - scale
                if not bool(locked.y):
                    scaledDims[1].y = scaledDims[0].y - scale

            for y in range(pointOff, newPointOff):
                p = inSpline.GetPoint(y)
                p.x = c4d.utils.RangeMap(p.x, dims[0].x, dims[1].x, scaledDims[0].x, scaledDims[1].x, False)
                p.y = c4d.utils.RangeMap(p.y, dims[0].y, dims[1].y, scaledDims[0].y, scaledDims[1].y, False)
                outObj.SetPoint(y, p)
            
            pointOff = newPointOff

        outObj.Message(c4d.MSG_UPDATE)
        return outObj        

    def GetCap(self, op, doc, inObj):
        splineHelp = c4d.utils.SplineHelp()
        splineHelp.InitSplineWith(inObj, c4d.SPLINEHELPFLAGS_GLOBALSPACE | c4d.SPLINEHELPFLAGS_CONTINUECURVE | c4d.SPLINEHELPFLAGS_RETAINLINEOBJECT)
        lineObj = splineHelp.GetLineObject()
        return lineObj.Triangulate(0.0)

    def CheckDirty(self, op, doc):
        frame = doc.GetTime().GetFrame(doc.GetFps())
        if self.LAST_FRAME != frame:
            self.LAST_FRAME = frame
            op.SetDirty(c4d.DIRTYFLAGS_DATA)

    def GetContour(self, op, doc, lod, bt):
        inObj = op.GetDown()
        if inObj is None: return None
        inSpline = self.RecursiveCollectInputs(op, doc, inObj)
        outObj = inSpline.GetClone()
        return self.AnimateGrid(doc, op, inSpline, outObj)

    def GetVirtualObjects(self, op, hh):
        doc = op.GetDocument()
        if doc is None: return None

        inObj = op.GetDown()
        if inObj is None: return None

        hClone = op.GetAndCheckHierarchyClone(hh, inObj, c4d.HIERARCHYCLONEFLAGS_ASSPLINE, True)
        if not hClone['dirty']: return hClone['clone']

        inSpline = self.RecursiveCollectInputs(op, doc, inObj)
        if inSpline is None: return None

        cap = op[res_SG.SG_CAP]
        if cap:
            outGeo = self.GetCap(op, doc, inSpline)
            phong = outGeo.GetTag(c4d.Tphong)
            phong[c4d.PHONGTAG_PHONG_ANGLELIMIT] = True
            phong[c4d.PHONGTAG_PHONG_ANGLE] = c4d.utils.DegToRad(89.0)
            phong[c4d.PHONGTAG_PHONG_USEEDGES] = False
        else:
            outGeo = inSpline.GetClone()

        return self.AnimateGrid(doc, op, inSpline, outGeo)

class SubdivideGridExtrude(c4d.plugins.ObjectData):
    PLUGIN_ID = 1054128
    PLUGIN_NAME = 'Subdivide Grid Extrude'
    PLUGIN_INFO = c4d.OBJECT_GENERATOR | c4d.OBJECT_INPUT
    PLUGIN_DESC = 'Osubdividegridextrude'
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
        return True

    def GetVirtualObjects(self, op, hh):
        doc = op.GetDocument()
        if doc is None: return None

        inObj = op.GetDown()
        if inObj is None: return None

        hClone = op.GetAndCheckHierarchyClone(hh, inObj, c4d.HIERARCHYCLONEFLAGS_ASSPLINE, False)
        if not hClone['dirty']: return hClone['clone']

        inSpline = GetObjectSpline(inObj, doc)
        if inSpline is None: return None

        movement = c4d.Vector(0, 0, -10)

        inPointCount = inSpline.GetPointCount()
        points = []
        polys = []
        segCount = inSpline.GetSegmentCount()
        if segCount == 0:
            inSpline.ResizeObject(inPointCount, 1)
            inSpline.SetSegment(0, inPointCount, inSpline.IsClosed())
            segCount = 1
        pointOff = 0
        inMarr = inSpline.GetMl()

        # points
        for x in range(segCount):
            seg = inSpline.GetSegment(x)
            newPointOff = pointOff + seg['cnt']
            for y in range(pointOff, newPointOff):
                p = inSpline.GetPoint(y) * inMarr
                points.append(p)
                points.append(p + movement)
            pointOff = newPointOff

        # polys
        pointOff = 0
        for x in range(segCount):
            seg = inSpline.GetSegment(x)
            newPointOff = pointOff + (seg['cnt'] * 2)
            for y in range(pointOff, newPointOff, 2):
                p1 = y
                p2 = p1 + 1
                p3 = p2 + 1
                if p3 >= newPointOff: p3 = pointOff
                p4 = p3 + 1
                polys.append(c4d.CPolygon(p1, p2, p4, p3))
            pointOff = newPointOff

        # caps
        # pointOff = 0
        # for x in range(segCount):
        #     seg = inSpline.GetSegment(x)
        #     newPointOff = pointOff + (seg['cnt'] * 2)
        #     numTris = (seg['cnt'] - 2) * 2
        #     for y in range(numTris):
        #         evenOdd = y % 2
        #         p1 = pointOff + evenOdd
        #         p2 = y + evenOdd + pointOff + (2 - evenOdd)
        #         p3 = p2 + 2
        #         if evenOdd == 0:
        #             polys.append(c4d.CPolygon(p1, p2, p3))
        #         else:
        #             polys.append(c4d.CPolygon(p3, p2, p1))
        #     pointOff = newPointOff

        outObj = c4d.PolygonObject(len(points), len(polys))
        outObj.SetAllPoints(points)
        for x, poly in enumerate(polys):
            outObj.SetPolygon(x, poly)
        outObj.Message(c4d.MSG_UPDATE)

        return outObj

if __name__ == '__main__':
    SubdivideGrid.Register()
    SubdivideGridDriver.Register()
    SubdivideGridExtrude.Register()
