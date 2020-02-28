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
    if rel_tol < 0 or abs_tol < 0:
        raise ValueError("tolerances must be non-negative")

    if a == b:
        return True

    if math.isinf(a) or math.isinf(b):
        return False

    diff = math.fabs(b - a)
    result = (((diff <= math.fabs(rel_tol * b)) or
               (diff <= math.fabs(rel_tol * a))) or
              (diff <= abs_tol))
    return result

class res_SG(object):
    SG_COMPLETE = 1000
    SG_SPLINE_GROUP = 1001
    SG_SPLINE_X = 1002
    SG_SPLINE_Y = 1003
    SG_SPLINE_Z = 1004
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

    def GetDDescription(self, node, description, flags):
        # Before adding dynamic parameters, load the parameters from the description resource
        if not description.LoadDescription(node.GetType()): return False

        # Get description single ID
        singleID = description.GetSingleDescID()

        # Add Complete control
        completeID = c4d.DescID(c4d.DescLevel(res_SG.SG_COMPLETE, c4d.DTYPE_REAL))
        if singleID is None or completeID.IsPartOf(singleID)[0]:
            bc = c4d.GetCustomDataTypeDefault(c4d.DTYPE_REAL)
            bc.SetString(c4d.DESC_NAME, 'Complete')
            bc.SetString(c4d.DESC_SHORT_NAME, 'Complete')
            bc.SetInt32(c4d.DESC_UNIT, c4d.DESC_UNIT_PERCENT)
            bc.SetInt32(c4d.DESC_CUSTOMGUI, c4d.CUSTOMGUI_REALSLIDER)
            bc.SetFloat(c4d.DESC_DEFAULT, 1.0)
            bc.SetFloat(c4d.DESC_MIN, 0.0)
            bc.SetFloat(c4d.DESC_MAX, 1.0)
            bc.SetFloat(c4d.DESC_MINSLIDER, 0.0)
            bc.SetFloat(c4d.DESC_MAXSLIDER, 1.0)
            bc.SetFloat(c4d.DESC_STEP, 0.01)
            bc.SetBool(c4d.DESC_GUIOPEN, True)
            if not description.SetParameter(completeID, bc, c4d.ID_TAGPROPERTIES):
                return False

        # Add spline group
        splineGroupID = c4d.DescID(c4d.DescLevel(res_SG.SG_SPLINE_GROUP, c4d.DTYPE_GROUP))
        if singleID is None or splineGroupID.IsPartOf(singleID)[0]:
            bc = c4d.GetCustomDataTypeDefault(c4d.DTYPE_GROUP)
            bc.SetString(c4d.DESC_NAME, 'Time Ramps')
            bc.SetString(c4d.DESC_SHORT_NAME, 'Time Ramps')
            bc.SetBool(c4d.DESC_GUIOPEN, False)
            if not description.SetParameter(splineGroupID, bc, c4d.DESCID_ROOT):
                return False
        
        # Add x ramp control
        splineXID = c4d.DescID(c4d.DescLevel(res_SG.SG_SPLINE_X, c4d.CUSTOMDATATYPE_SPLINE))
        if singleID is None or splineXID.IsPartOf(singleID)[0]:
            bc = c4d.GetCustomDataTypeDefault(c4d.CUSTOMDATATYPE_SPLINE)
            bc.SetString(c4d.DESC_NAME, 'X Ramp')
            bc.SetString(c4d.DESC_SHORT_NAME, 'X Ramp')
            bc.SetBool(c4d.DESC_GUIOPEN, False)
            bc.SetFloat(c4d.SPLINECONTROL_X_MIN, 0.0)
            bc.SetFloat(c4d.SPLINECONTROL_X_MAX, 1.0)
            bc.SetFloat(c4d.SPLINECONTROL_Y_MIN, 0.0)
            bc.SetFloat(c4d.SPLINECONTROL_Y_MAX, 1.0)
            if not description.SetParameter(splineXID, bc, splineGroupID):
                return False
        
        # Add y ramp control
        splineYID = c4d.DescID(c4d.DescLevel(res_SG.SG_SPLINE_Y, c4d.CUSTOMDATATYPE_SPLINE))
        if singleID is None or splineYID.IsPartOf(singleID)[0]:
            bc = c4d.GetCustomDataTypeDefault(c4d.CUSTOMDATATYPE_SPLINE)
            bc.SetString(c4d.DESC_NAME, 'Y Ramp')
            bc.SetString(c4d.DESC_SHORT_NAME, 'Y Ramp')
            bc.SetBool(c4d.DESC_GUIOPEN, False)
            bc.SetFloat(c4d.SPLINECONTROL_X_MIN, 0.0)
            bc.SetFloat(c4d.SPLINECONTROL_X_MAX, 1.0)
            bc.SetFloat(c4d.SPLINECONTROL_Y_MIN, 0.0)
            bc.SetFloat(c4d.SPLINECONTROL_Y_MAX, 1.0)
            if not description.SetParameter(splineYID, bc, splineGroupID):
                return False

        # Add z ramp control
        splineZID = c4d.DescID(c4d.DescLevel(res_SG.SG_SPLINE_Z, c4d.CUSTOMDATATYPE_SPLINE))
        if singleID is None or splineZID.IsPartOf(singleID)[0]:
            bc = c4d.GetCustomDataTypeDefault(c4d.CUSTOMDATATYPE_SPLINE)
            bc.SetString(c4d.DESC_NAME, 'Z Ramp')
            bc.SetString(c4d.DESC_SHORT_NAME, 'Z Ramp')
            bc.SetBool(c4d.DESC_GUIOPEN, False)
            bc.SetFloat(c4d.SPLINECONTROL_X_MIN, 0.0)
            bc.SetFloat(c4d.SPLINECONTROL_X_MAX, 1.0)
            bc.SetFloat(c4d.SPLINECONTROL_Y_MIN, 0.0)
            bc.SetFloat(c4d.SPLINECONTROL_Y_MAX, 1.0)
            if not description.SetParameter(splineZID, bc, splineGroupID):
                return False

        # After parameters have been loaded and added successfully, return True and DESCFLAGS_DESC_LOADED with the input flags
        return (True, flags | c4d.DESCFLAGS_DESC_LOADED)

    def Init(self, node):
        self.InitAttr(node, float, res_SG.SG_COMPLETE)

        node[res_SG.SG_COMPLETE] = 100.0
        sd = c4d.SplineData()
        knots = sd.GetKnots()
        knots[0]['vPos'] = c4d.Vector(0)
        knots[0]['vTangentRight'] = c4d.Vector(0.25)
        knots[1]['vPos'] = c4d.Vector(1)
        knots[1]['vTangentLeft'] = c4d.Vector(-0.25)
        sd.SetKnot(
            0,
            knots[0]['vPos'],
            knots[0]['lFlagsSettings'],
            knots[0]['bSelect'],
            knots[0]['vTangentLeft'],
            knots[0]['vTangentRight'],
            knots[0]['interpol']
        )
        sd.SetKnot(
            1,
            knots[1]['vPos'],
            knots[1]['lFlagsSettings'],
            knots[1]['bSelect'],
            knots[1]['vTangentLeft'],
            knots[1]['vTangentRight'],
            knots[1]['interpol']
        )
        node[res_SG.SG_SPLINE_X] = sd
        node[res_SG.SG_SPLINE_Y] = sd
        node[res_SG.SG_SPLINE_Z] = sd
        
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
        rad = obj.GetRad()
        center = (obj.GetRelPos() * obj.GetUpMg()) + obj.GetMp()
        thisBlf = center - rad
        thisTrb = center + rad
        return { 'blf': thisBlf, 'trb': thisTrb }

    def GetCollectiveBBox(self, splines):
        initBbox = self.GetObjectBBox(splines[0])
        blf = initBbox['blf']
        trb = initBbox['trb']
        for x in range(1, len(splines)):
            bbox = self.GetObjectBBox(splines[x])
            blf = self.minVector(bbox['blf'], blf)
            trb = self.maxVector(bbox['trb'], trb)
        return { 'blf': blf, 'trb': trb }

    def GetCornersFromBBox(self, bbox):
        corners = [None] * 8
        corners[0] = bbox['blf']
        corners[1] = bbox['trb']
        corners[2] = c4d.Vector(corners[0].x, corners[0].y, corners[1].z)
        corners[3] = c4d.Vector(corners[0].x, corners[1].y, corners[0].z)
        corners[4] = c4d.Vector(corners[1].x, corners[0].y, corners[0].z)
        corners[5] = c4d.Vector(corners[1].x, corners[1].y, corners[0].z)
        corners[6] = c4d.Vector(corners[1].x, corners[0].y, corners[1].z)
        corners[7] = c4d.Vector(corners[0].x, corners[1].y, corners[1].z)
        return corners

    def MakesFarSides(self, spline, farCorner):
        x = False
        y = False
        z = False
        corners = self.GetCornersFromBBox(self.GetObjectBBox(spline))
        for corner in corners:
            if isclose(corner.x, farCorner.x): x = True
            if isclose(corner.y, farCorner.y): y = True
            if isclose(corner.z, farCorner.z): z = True
        return { 'x': x, 'y': y, 'z': z }
    
    def Execute(self, tag, doc, op, bt, priority, flags):
        parent = tag.GetObject()
        complete = tag[res_SG.SG_COMPLETE]
        xSpline = tag[res_SG.SG_SPLINE_X]
        ySpline = tag[res_SG.SG_SPLINE_Y]
        zSpline = tag[res_SG.SG_SPLINE_Z]

        # collect splines
        # if nothing in list, get children
        splines = parent.GetChildren()

        if splines is None: return c4d.EXECUTIONRESULT_OK
        
        # gather parent info so not to recalculate later
        parentRad = parent.GetRad()
        parentMg = parent.GetMg()
        parentAnchor = parentMg.off
        parentObjSpaceAnchor = (-parent.GetMp()) + parentRad
        
        parentCorners = self.GetCornersFromBBox(self.GetCollectiveBBox(splines))
        def DistFromAnchor(obj, anchor=parentAnchor):
            return (anchor - obj).GetLength()
        parentCorners.sort(key=DistFromAnchor)
        parentFarCorner = parentCorners[7]

        # calculate movements
        for spline in splines:
            if not spline[c4d.ID_BASEOBJECT_GENERATOR_FLAG]: continue

            splineRad = spline.GetRad()
            makesFarSides = self.MakesFarSides(spline, parentFarCorner)

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

            scaleOff = c4d.Vector(1.0)
            scaleOff.x = c4d.utils.RangeMap(complete, 1.0, 0.0, 1.0, maxScaleOff.x, False, xSpline)
            scaleOff.y = c4d.utils.RangeMap(complete, 1.0, 0.0, 1.0, maxScaleOff.y, False, ySpline)
            scaleOff.z = c4d.utils.RangeMap(complete, 1.0, 0.0, 1.0, maxScaleOff.z, False, zSpline)

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
            posOff.x = c4d.utils.RangeMap(complete, 1.0, 0.0, 0.0, maxPosOff.x, False, xSpline)
            posOff.y = c4d.utils.RangeMap(complete, 1.0, 0.0, 0.0, maxPosOff.y, False, ySpline)
            posOff.z = c4d.utils.RangeMap(complete, 1.0, 0.0, 0.0, maxPosOff.z, False, zSpline)

            # apply
            spline.SetFrozenPos(posOff)
            spline.SetFrozenScale(scaleOff)
            spline.Message(c4d.MSG_UPDATE)

        return c4d.EXECUTIONRESULT_OK


if __name__ == '__main__':
    SubdivideGrid.Register()
