# Python Script, API Version = V22 Beta
from SpaceClaim.Api.V22.Geometry import Point
import math

ClearAll()

# Get Input Parameters
per=Parameters.Periodicity/2
subThick=Parameters.SubsThickness
hCr1=Parameters.ChromiumForAdhesion
hAu=Parameters.GoldLayer
hCr2=Parameters.ChromiumForSurfacePassivation
radius=Parameters.Radius
width=Parameters.Width
angle=Parameters.Angle
oangle=Parameters.OpeningAngle
hEtch=Parameters.EtchHeight
dEtch=Parameters.EtchDepth
dnaT = Parameters.DNA
opRegion = Parameters.OpenRegion
# End Parameters

# Constructor Show Each Layer Seperately 
def showLayersSeparated(distance=0):
    t = 1    
    while t <4:
        GetRootPart().Bodies[t].Transform(Matrix.CreateTranslation(Vector.Create(0,0,distance)))
        distance+=distance
        t = t + 1
        
def createPlane(ang):
   if (ang != 0):      
       plane = DatumPlaneCreator.Create(Point.Origin, -Direction.DirZ, -Direction.DirX, False)
       selectionPlane = Selection.Create(GetRootPart().DatumPlanes[0])
       result = RenameObject.Execute(selectionPlane, (180*ang/math.pi).ToString()+' DegPlane')
       result = Move.Rotate(selectionPlane, Move.GetAxis(selectionPlane, HandleAxis.X), ang, MoveOptions())
       return result

# Create Substrate
result = BlockBody.Create(Point.Create(MM(-per), MM(-per), MM(0)), Point.Create(MM(per), MM(per), MM(-subThick)), ExtrudeType.ForceAdd)
body = result.CreatedBody.SetName('Substrate')
ColorHelper.SetColor(Selection.CreateByNames('Substrate'), Color.FromArgb(255, 128, 128, 255))
# EndBlock

# Create ChromiumForAdhesion
result = BlockBody.Create(Point.Create(MM(-per), MM(-per), MM(0)), Point.Create(MM(per), MM(per), MM(hCr1)), ExtrudeType.ForceIndependent)
body = result.CreatedBody.SetName('ChromiumForAdhesion')
ColorHelper.SetColor(Selection.CreateByNames('ChromiumForAdhesion'), Color.Gray)
# EndBlock

# Create GoldLayer
result = BlockBody.Create(Point.Create(MM(-per), MM(-per), MM(hCr1)), Point.Create(MM(per), MM(per), MM(hCr1+hAu)), ExtrudeType.ForceIndependent)
body = result.CreatedBody.SetName('Gold Layer')
ColorHelper.SetColor(Selection.CreateByNames('Gold Layer'), Color.Gold)
# EndBlock

# Create ChromiumForAdhesion
result = BlockBody.Create(Point.Create(MM(-per), MM(-per), MM(hCr1+hAu)), Point.Create(MM(per), MM(per), MM(hCr1+hAu+hCr2)), ExtrudeType.ForceIndependent)
body = result.CreatedBody.SetName('ChromiumForSurfacePassivation')
ColorHelper.SetColor(Selection.CreateByNames('ChromiumForSurfacePassivation'), Color.Gray)
# EndBlock
  
# Beginning of Face Cut   
######################################################################

gap = dEtch/radius*(180/math.pi)
dnaGap = dnaT/(radius)*(180/math.pi)
dnaGapUzakFar = dnaT/(radius + width - dnaT)*(180/math.pi)
    
def pointAllocateFirst( distP, angP):
    seloc =Selection.Create(DatumPointCreator.Create(Point.Create(0, MM(distP), 0)).CreatedPoint)
    move = Move.Rotate(seloc, Line.Create(Point.Origin, Direction.DirZ), angP-DEG(45), MoveOptions())
    
def pointAllocateSecond(distP,angP):
    seloc =Selection.Create(DatumPointCreator.Create(Point.Create(0, MM(distP), 0)).CreatedPoint)
    move = Move.Rotate(seloc, Line.Create(Point.Origin, Direction.DirZ), angP-DEG(45+180), MoveOptions())
    
def surfaceCutOperation(ring, nearPoint, farPoint, rotation, offset, extrudeDistance):
    if (ring == 1 or ring == 3):
        pointAllocateFirst( nearPoint, rotation)
        pointAllocateFirst( nearPoint, -rotation)
        pointAllocateFirst( farPoint, rotation)
        pointAllocateFirst( farPoint, -rotation)
    if (ring == 2 or ring ==  4 or ring ==  5):
        pointAllocateSecond( nearPoint, rotation)
        pointAllocateSecond( nearPoint, -rotation)
        pointAllocateSecond( farPoint, rotation)
        pointAllocateSecond( farPoint, -rotation)
       
    start1 =(GetRootPart().DatumPoints[0]).Position
    end1 = (GetRootPart().DatumPoints[1]).Position
    start2 =(GetRootPart().DatumPoints[2]).Position
    end2 = (GetRootPart().DatumPoints[3]).Position
    
    while GetRootPart().DatumPoints.Count > 0:
        GetRootPart().DatumPoints[0].Delete()
        
    curves = List[ITrimmedCurve]()
    curves.Add(CurveSegment.CreateArc(Point.Origin,start1,end1, -Direction.DirZ))
    curves.Add(CurveSegment.CreateArc(Point.Origin,start2,end2, -Direction.DirZ))
    curves.Add(CurveSegment.Create(start1,start2))
    curves.Add(CurveSegment.Create(end1,end2))
        
    designResult = PlanarBody.Create(Plane.PlaneXY, curves)
    designBody1 = designResult.CreatedBody
        
    # Cut substrate
    if (ring == 1 or ring == 2 or ring == 4):
        selection = Selection.Create(designBody1.Faces)
        options = ExtrudeFaceOptions()
        off = OffsetFaces.Execute(selection, offset, OffsetFaceOptions())
        options.ExtrudeType = ExtrudeType.ForceCut
        result = ExtrudeFaces.Execute(selection, extrudeDistance, options)   # ForceCut
    if (ring == 3 or ring == 5):
        selection = Selection.Create(designBody1.Faces)
        options = ExtrudeFaceOptions()
        off = OffsetFaces.Execute(selection, offset, OffsetFaceOptions())
        options.ExtrudeType = ExtrudeType.ForceIndependent
        result = ExtrudeFaces.Execute(selection, extrudeDistance, options)   # ForceCut
        
    
######################################################################
# Cut Operations
#surfaceCutOperation(ring, nearPoint,     farPoint,                            rotation,                                              offset,       extrudeDistance)
surfaceCutOperation( 1, radius,             radius+width,                    DEG(45)+angle,                                        hCr1,     hAu+hCr2)  #Cut Up
surfaceCutOperation( 1, radius - dEtch,  radius + width + dEtch,      DEG(45)+angle +DEG(gap),                      hCr1,     -hCr1 - hEtch)  #Cut Down
surfaceCutOperation( 2, radius,             radius+width,                    DEG(135) - angle - oangle,                         hCr1,     hAu+hCr2)  #Cut Up
surfaceCutOperation( 2, radius - dEtch,  radius + width + dEtch,      DEG(135) - angle - oangle +DEG(gap),       hCr1,    -hCr1-hEtch)  #Cut Down
#######################################################################

# Round Edges to show edged region
selectFirstRing= EdgeSelection.Create(GetRootPart().Bodies[0].Faces[8].Edges)
result = ConstantRound.Execute(selectFirstRing, MM(hEtch), ConstantRoundOptions())
selectSecondRing2 = EdgeSelection.Create(GetRootPart().Bodies[0].Faces[9].Edges)
result2 = ConstantRound.Execute(selectSecondRing2, MM(hEtch), ConstantRoundOptions())

#######################################################################
## END OF SURFACE APPROACH



#######################################################################

## DNA LAYER

## FIRST RING
#surfaceCutOperation(ring, nearPoint,     farPoint,                            rotation,                                              offset,       extrudeDistance)
surfaceCutOperation( 3, radius - dEtch,        radius + width + dEtch,       DEG(45) + angle + DEG(dnaGap),       hCr1,           -dnaT)  #First Ring Build Down
surfaceCutOperation( 1, radius + dnaT,        radius + width - dnaT,         DEG(45) + angle,                              hCr1,            -dnaT)  #First Ring Cut Down # BOTTOM Section completed

surfaceCutOperation( 3, radius,                   radius + width,                    DEG(45) + angle,                              hCr1-dnaT,    hAu + dnaT) #First Ring Build Up
surfaceCutOperation( 1, radius + dnaT,        radius + width - dnaT,         DEG(45) + angle - DEG(dnaGap),        hCr1-dnaT,    hAu + dnaT)  #First Ring Cut Down    # UPPER Section completed

# Merge Bodies = Merge two seperated DNA solid layers into one
targets = BodySelection.Create([GetRootPart().Bodies[5],
    GetRootPart().Bodies[4]])
result = Combine.Merge(targets)
# EndBlock
GetRootPart().Bodies[4].SetName("DNA Large Ring")
######################################################################

## SECOND RING 
#surfaceCutOperation(ring, nearPoint,     farPoint,                            rotation,                                              offset,       extrudeDistance)
surfaceCutOperation( 5, radius - dEtch,        radius + width + dEtch,       DEG(135) - angle - oangle + DEG(dnaGap),             hCr1,           -dnaT)  #Second Ring BuildDown
surfaceCutOperation( 4, radius + dnaT,        radius + width - dnaT,         DEG(135) - angle - oangle,                              hCr1,            -dnaT)  #Second Ring CutDown       # BOTTOM Section completed
surfaceCutOperation( 5, radius,                   radius + width,                    DEG(135) - angle - oangle,                              hCr1-dnaT,    hAu + dnaT) #Second Ring Build Up
surfaceCutOperation( 4, radius + dnaT,        radius + width - dnaT,         DEG(135) - angle - oangle - DEG(dnaGap),            hCr1-dnaT,    hAu + dnaT)  #Second Cut Down    # UPPER Section completed

# Merge Bodies = Merge two seperated DNA solid layers into one
targets = BodySelection.Create([GetRootPart().Bodies[5],
    GetRootPart().Bodies[6]])
result = Combine.Merge(targets)
# EndBlock
GetRootPart().Bodies[5].SetName("DNA Small Ring")
######################################################################


######################################################################

# Create Radiation Region
upperFace =( (opRegion - subThick) / 2 ) + hCr1 + hCr2 + hAu
lowerFace = opRegion - upperFace + hCr1 + hCr2 + hAu
result = BlockBody.Create(Point.Create(MM(-per), MM(-per), MM(upperFace)), Point.Create(MM(per), MM(per), MM(-lowerFace)), ExtrudeType.ForceIndependent)
GetRootPart().Bodies[6].SetName("Region")

selection = BodySelection.Create(GetRootPart().Bodies[6])
options = SetColorOptions()
options.FaceColorTarget = FaceColorTarget.Body
ColorHelper.SetColor(selection, options, ColorHelper.Red)
ColorHelper.SetFillStyle(selection, FillStyle.Transparent)
# EndBlock


# Set Section View and Zoom to Entity
# showLayersSeparated(0.1)
createPlane(Parameters.PlaneAngle)
#ViewHelper.SetSectionPlane(Selection.Create(GetRootPart().DatumPlanes[0]), None)
#ViewHelper.SetSectionPlane(Plane.PlaneYZ)
Selection.Clear()
#ViewHelper.ZoomToEntity()
# EndBlock


###############################################################''''''''''''''''''''''''''''''''''''''''

# Change Object Visibility


selection = BodySelection.Create(GetRootPart().Bodies[6])
visibility = VisibilityType.Hide
inSelectedView = False
faceLevel = False
ViewHelper.SetObjectVisibility(selection, visibility, inSelectedView, faceLevel)
# EndBlock

# Fix 2 Interferences

#selection = Selection.CreateByNames('Substrate','ChromiumForAdhesion','Gold Layer','ChromiumForSurfacePassivation',"DNA Large Ring","DNA Small Ring")
options = FixInterferenceOptions()
options.CutSmallerBody = True
result = FixInterference.FindAndFix(options)
# EndBlock
