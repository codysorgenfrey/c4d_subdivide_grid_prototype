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

def roundOffVector(inVec):
    outVec = c4d.Vector()
    per = 10000
    outVec.x = math.floor(inVec.x * per + 0.5) / per
    outVec.y = math.floor(inVec.y * per + 0.5) / per
    outVec.z = math.floor(inVec.z * per + 0.5) / per
    return outVec

def MapRange(value, min_input, max_input, min_output, max_output, curve):
    inrange = max_input - min_input
    if isclose(inrange, 0.0):
        value = 0.0
    else:
        value = (value - min_input) / inrange

    if curve:
        value = curve.GetPoint(value).y

    return  min_output + (max_output - min_output) * value

class res_SG(object):
    SG_COMPLETE = 1000
    SG_SPLINE_GROUP = 1001
    SG_SPLINE_X = 1002
    SG_SPLINE_Y = 1003
    SG_SPLINE_Z = 1004
    SG_LIST = 1005
    SG_NONRECT = 1006
    SG_INOBJ = 1007
res_SG = res_SG()

class SubdivideGridBase(c4d.plugins.TagData):
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

        # Add Non Rectangle control
        nonRectID = c4d.DescID(c4d.DescLevel(res_SG.SG_NONRECT, c4d.DTYPE_BOOL))
        if singleID is None or nonRectID.IsPartOf(singleID)[0]:
            bc = c4d.GetCustomDataTypeDefault(c4d.DTYPE_BOOL)
            bc.SetString(c4d.DESC_NAME, 'Non-Rectangular')
            bc.SetString(c4d.DESC_SHORT_NAME, 'Non-Rectangular')
            bc.SetBool(c4d.DESC_DEFAULT, False)
            bc.SetBool(c4d.DESC_GUIOPEN, True)
            if not description.SetParameter(nonRectID, bc, c4d.ID_TAGPROPERTIES):
                return False

        # Add list control
        listID = c4d.DescID(c4d.DescLevel(res_SG.SG_LIST, c4d.CUSTOMDATATYPE_INEXCLUDE_LIST))
        if singleID is None or listID.IsPartOf(singleID)[0]:
            bc = c4d.GetCustomDataTypeDefault(c4d.CUSTOMDATATYPE_INEXCLUDE_LIST)
            bc.SetString(c4d.DESC_NAME, 'Splines')
            bc.SetString(c4d.DESC_SHORT_NAME, 'Splines')
            bc.SetBool(c4d.DESC_GUIOPEN, True)
            if not description.SetParameter(listID, bc, c4d.ID_TAGPROPERTIES):
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

    def GetDEnabling(self, node, desc, t_data, flags, itemdesc):
        myId = desc[0].id

        if myId == res_SG.SG_SPLINE_X and node[res_SG.SG_NONRECT]:
            return False
        
        if myId == res_SG.SG_SPLINE_Y and node[res_SG.SG_NONRECT]:
            return False

        if myId == res_SG.SG_SPLINE_Z and node[res_SG.SG_NONRECT]:
            return False
        
        return True

    def Init(self, node):
        self.InitAttr(node, float, res_SG.SG_COMPLETE)

        node[res_SG.SG_COMPLETE] = 100.0

        node[res_SG.SG_NONRECT] = False

        node[res_SG.SG_LIST] = c4d.InExcludeData()

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

    def GetGlobalRegPos(self, obj):
        pos = obj.GetRelPos()
        parent = obj.GetUp()
        while parent:
            pos += parent.GetRelPos()
            parent = parent.GetUp()
        return pos

    def GetObjectBBox(self, obj):
        rad = obj.GetRad()
        if isclose(rad.GetLength(), 0.0) and obj.GetDown():
            children = obj.GetChildren()
            return self.GetCollectiveBBox(children)
        center = self.GetGlobalRegPos(obj) + obj.GetMp()
        thisBlf = roundOffVector(center - rad)
        thisTrb = roundOffVector(center + rad)
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

    def GetRadFromBBox(self, bbox):
        rad = c4d.Vector()
        rad.x = abs(bbox['trb'].x - bbox['blf'].x) / 2
        rad.y = abs(bbox['trb'].y - bbox['blf'].y) / 2
        rad.z = abs(bbox['trb'].z - bbox['blf'].z) / 2
        return rad

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

    def MakesFarSides(self, splineBBox, farCorner):
        x = False
        y = False
        z = False
        corners = self.GetCornersFromBBox(splineBBox)
        for corner in corners:
            if isclose(corner.x, farCorner.x): x = True
            if isclose(corner.y, farCorner.y): y = True
            if isclose(corner.z, farCorner.z): z = True
        return { 'x': x, 'y': y, 'z': z }
    
    def Execute(self, tag, doc, op, bt, priority, flags):
        parent = tag.GetObject()
        complete = tag[res_SG.SG_COMPLETE]
        nonRect = tag[res_SG.SG_NONRECT]
        splineList = tag[res_SG.SG_LIST]
        xSpline = tag[res_SG.SG_SPLINE_X]
        ySpline = tag[res_SG.SG_SPLINE_Y]
        zSpline = tag[res_SG.SG_SPLINE_Z]
        if nonRect:
            complete *= 2.0
            xSpline = None
            ySpline = None
            zSpline = None

        # collect splines
        splines = []
        for x in range(splineList.GetObjectCount()):
            splines.append(splineList.ObjectFromIndex(doc, x))
        # if nothing in list, get children
        if len(splines) == 0:
            splines = parent.GetChildren()

        if len(splines) == 0: return c4d.EXECUTIONRESULT_OK
        
        # gather parent info so not to recalculate later
        parentAnchor = self.GetGlobalRegPos(parent)
        parentBBox = self.GetCollectiveBBox(splines)
        parentCorners = self.GetCornersFromBBox(parentBBox)
        def DistFromAnchor(obj, anchor=parentAnchor):
            return (anchor - obj).GetLength()
        parentCorners.sort(key=DistFromAnchor)
        parentFarCorner = parentCorners[7]
        parentRad = self.GetRadFromBBox(parentBBox)
        parentObjSpaceAnchor = parentAnchor - parentBBox['blf']

        # calculate movements
        for spline in splines:
            if not spline.GetDeformMode(): continue # spline is disabled

            splineAnchor = self.GetGlobalRegPos(spline)
            splineBBox = self.GetObjectBBox(spline)
            splineRad = self.GetRadFromBBox(splineBBox)
            makesFarSides = self.MakesFarSides(splineBBox, parentFarCorner)

            # scale
            maxScaleOff = c4d.Vector(0)
            if makesFarSides['x'] and not isclose(splineRad.x, 0.0): 
                maxScaleOff.x = parentRad.x / splineRad.x
            if makesFarSides['y'] and not isclose(splineRad.y, 0.0): 
                maxScaleOff.y = parentRad.y / splineRad.y
            if makesFarSides['z'] and not isclose(splineRad.z, 0.0): 
                maxScaleOff.z = parentRad.z / splineRad.z

            scaleOff = c4d.Vector(1.0)
            scaleOff.x = MapRange(complete, 0.0, 1.0, maxScaleOff.x, 1.0, xSpline)
            scaleOff.y = MapRange(complete, 0.0, 1.0, maxScaleOff.y, 1.0, ySpline)
            scaleOff.z = MapRange(complete, 0.0, 1.0, maxScaleOff.z, 1.0, zSpline)

            # position
            splineRelPos = -(parentAnchor - splineAnchor)
            maxPosOff = -splineRelPos
            splineObjSpaceAnchor = splineAnchor - splineBBox['blf']
            if makesFarSides['x'] and not isclose(splineRad.x, 0.0):
                origPosX = splineRelPos.x
                newSplineObjSpaceAnchorX = (splineObjSpaceAnchor.x / splineRad.x) * parentRad.x
                newPosX = newSplineObjSpaceAnchorX - parentObjSpaceAnchor.x
                maxPosOff.x = newPosX - origPosX
            if makesFarSides['y'] and not isclose(splineRad.y, 0.0):
                origPosY = splineRelPos.y
                newSplineObjSpaceAnchorY = (splineObjSpaceAnchor.y / splineRad.y) * parentRad.y
                newPosY = newSplineObjSpaceAnchorY - parentObjSpaceAnchor.y
                maxPosOff.y = newPosY - origPosY
            if makesFarSides['z'] and not isclose(splineRad.z, 0.0):
                origPosZ = splineRelPos.z
                newSplineObjSpaceAnchorZ = (splineObjSpaceAnchor.z / splineRad.z) * parentRad.z
                newPosZ = newSplineObjSpaceAnchorZ - parentObjSpaceAnchor.z
                maxPosOff.z = newPosZ - origPosZ

            posOff = c4d.Vector(0.0)
            posOff.x = MapRange(complete, 0.0, 1.0, maxPosOff.x, 0.0, xSpline)
            posOff.y = MapRange(complete, 0.0, 1.0, maxPosOff.y, 0.0, ySpline)
            posOff.z = MapRange(complete, 0.0, 1.0, maxPosOff.z, 0.0, zSpline)

            # apply
            spline.SetFrozenPos(posOff)
            spline.SetFrozenScale(scaleOff)
            spline.Message(c4d.MSG_UPDATE)

        return c4d.EXECUTIONRESULT_OK

class SubdivideGridNonRect(SubdivideGridBase):
    def Init(self, node):
        super(SubdivideGridNonRect, self).Init(node)

        node[res_SG.SG_NONRECT] = True

        node[res_SG.SG_COMPLETE] = 0.5

        return True

class SubdivideGridInstance(c4d.plugins.ObjectData):
    LAST_FRAME = -1

    def GetDDescription(self, node, description, flags):
        # Before adding dynamic parameters, load the parameters from the description resource
        if not description.LoadDescription(node.GetType()): return False

        # Get description single ID
        singleID = description.GetSingleDescID()

        # Add link control
        linkId = c4d.DescID(c4d.DescLevel(res_SG.SG_INOBJ, c4d.DTYPE_BASELISTLINK))
        if singleID is None or linkId.IsPartOf(singleID)[0]:
            bc = c4d.GetCustomDataTypeDefault(c4d.DTYPE_BASELISTLINK)
            bc.SetString(c4d.DESC_NAME, 'Input')
            bc.SetString(c4d.DESC_SHORT_NAME, 'Input')
            if not description.SetParameter(linkId, bc, c4d.ID_OBJECTPROPERTIES):
                return False

        # After parameters have been loaded and added successfully, return True and DESCFLAGS_DESC_LOADED with the input flags
        return (True, flags | c4d.DESCFLAGS_DESC_LOADED)      

    def CheckDirty(self, op, doc):
        frame = doc.GetTime().GetFrame(doc.GetFps())
        if self.LAST_FRAME != frame:
            self.LAST_FRAME = frame
            op.SetDirty(c4d.DIRTYFLAGS_DATA)

    def GetContour(self, op, doc, lod, bt):
        inObj = op[res_SG.SG_INOBJ]
        if inObj is None: return None
        
        if inObj.GetType() == c4d.Ospline:
            spline = inObj.GetClone()
        else:
            objClone = inObj.GetClone()
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
                realSpline = inObj.GetRealSpline()
                if realSpline:
                    spline = realSpline.GetClone()
                else: 
                    spline = None
        
        if spline.GetType() != c4d.Ospline:
            return None

        mg = inObj.GetMg()

        for x in range(spline.GetPointCount()):
            p = spline.GetPoint(x)
            p = mg * p
            spline.SetPoint(x, p)

        spline.Message(c4d.MSG_UPDATE)

        return spline

if __name__ == '__main__':
    c4d.plugins.RegisterTagPlugin(
            1054125,
            '#$0 Subdivide Grid',
            c4d.TAG_VISIBLE | c4d.TAG_EXPRESSION,
            SubdivideGridBase,
            'Tsubdividegrid',
            load_bitmap('res/icons/subdivide grid.tiff'),
            0,
        )
    c4d.plugins.RegisterTagPlugin(
            1054108,
            '#$1 Subdivide Grid (Non-Rect)',
            c4d.TAG_VISIBLE | c4d.TAG_EXPRESSION,
            SubdivideGridNonRect,
            'Tsubdividegridnonrect',
            load_bitmap('res/icons/subdivide grid.tiff'),
            0,
        )
    c4d.plugins.RegisterObjectPlugin(
            1054128,
            "Instance",
            SubdivideGridInstance,
            "Osubdividegridinstance",
            c4d.OBJECT_GENERATOR | c4d.OBJECT_ISSPLINE,
            load_bitmap('res/icons/subdivide grid.tiff'),
            0
        )
