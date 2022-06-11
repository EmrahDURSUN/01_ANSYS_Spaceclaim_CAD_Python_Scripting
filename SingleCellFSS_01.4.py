# Python Script, API Version = V22 Beta
from SpaceClaim.Api.V22.Geometry import Point
import math

ClearAll()
Layers.Create("Base")
selection = Selection.Create(Layers.GetAllLayers())
Delete.Execute(selection)
Layers.Create("Base")

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
    return result


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
re1 = surfaceCutOperation( 3, radius - dEtch,        radius + width + dEtch,       DEG(45) + angle + DEG(dnaGap),       hCr1,           -dnaT)  #First Ring Build Down
re2 = surfaceCutOperation( 1, radius + dnaT,        radius + width - dnaT,         DEG(45) + angle,                              hCr1,            -dnaT)  #First Ring Cut Down # BOTTOM Section completed

re3 = surfaceCutOperation( 3, radius,                   radius + width,                    DEG(45) + angle,                              hCr1-dnaT,    hAu + dnaT) #First Ring Build Up
re4 = surfaceCutOperation( 1, radius + dnaT,        radius + width - dnaT,         DEG(45) + angle - DEG(dnaGap),        hCr1-dnaT,    hAu + dnaT)  #First Ring Cut Down    # UPPER Section completed

# Merge Bodies = Merge two seperated DNA solid layers into one
#objectsL = List[IDocObject]()
#objectsL.Add(re1.GetCreated[DocObject]())
#objectsL.Add(re2)
#objectsL.Add(re3)
#objectsL.Add(re4)

targets = BodySelection.Create([GetRootPart().Bodies[5],
    GetRootPart().Bodies[4]])
result = Combine.Merge(targets)
# EndBlock
GetRootPart().Bodies[4].SetName("DNA Large Ring")
######################################################################

## SECOND RING 
#surfaceCutOperation(ring, nearPoint,     farPoint,                            rotation,                                              offset,       extrudeDistance)
result =surfaceCutOperation( 5, radius - dEtch,        radius + width + dEtch,       DEG(135) - angle - oangle + DEG(dnaGap),             hCr1,           -dnaT)  #Second Ring BuildDown
result = surfaceCutOperation( 4, radius + dnaT,        radius + width - dnaT,         DEG(135) - angle - oangle,                              hCr1,            -dnaT)  #Second Ring CutDown       # BOTTOM Section completed


surfaceCutOperation( 5, radius,                   radius + width,                    DEG(135) - angle - oangle,                              hCr1-dnaT,    hAu + dnaT) #Second Ring Build Up
surfaceCutOperation( 4, radius + dnaT,        radius + width - dnaT,         DEG(135) - angle - oangle - DEG(dnaGap),            hCr1-dnaT,    hAu + dnaT)  #Second Cut Down    # UPPER Section completed

# Merge Bodies = Merge two seperated DNA solid layers into one
targets = BodySelection.CreateByObjects([GetRootPart().Bodies[5],
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
result.CreatedBody.SetName('Region')


selection = BodySelection.Create(GetRootPart().Bodies[6])
options = SetColorOptions()
options.FaceColorTarget = FaceColorTarget.Body
ColorHelper.SetColor(selection, options, ColorHelper.Red)
ColorHelper.SetFillStyle(selection, FillStyle.Transparent)
# EndBlock

# Change Object Visibility
selection = Selection.CreateByNames('Region')
visibility = VisibilityType.Hide
inSelectedView = False
faceLevel = False
ViewHelper.SetObjectVisibility(selection, visibility, inSelectedView, faceLevel)
# EndBlock

###############################################################

# Fix 2 Interferences
#selection = Selection.CreateByNames('Substrate','ChromiumForAdhesion','Gold Layer','ChromiumForSurfacePassivation',"DNA Large Ring","DNA Small Ring")
options = FixInterferenceOptions()
options.CutSmallerBody = True
result = FixInterference.FindAndFix(options)
# EndBlock

# Change Object Visibility
selection = Selection.CreateByNames('Region')
visibility = VisibilityType.Show
ViewHelper.SetObjectVisibility(selection,visibility,False,False)

###############################################################

# Set Section View and Zoom to Entity
# showLayersSeparated(0.1)
createPlane(Parameters.PlaneAngle)
#ViewHelper.SetSectionPlane(Selection.Create(GetRootPart().DatumPlanes[0]), None)
#ViewHelper.SetSectionPlane(Plane.PlaneYZ)
Selection.Clear()
#ViewHelper.ZoomToEntity()

###############################################################

## Move All Bodies to New Component and Rename it
#selection = BodySelection.Create(GetRootPart().GetAllBodies())
#result = ComponentHelper.MoveBodiesToComponent(selection, None)
## Rename 'Component1' to 'Single_Cell'
#selection = PartSelection.Create(GetRootPart().Components[0].Content)
#result = RenameObject.Execute(selection,"Single_Cell")
## EndBlock

###############################################################

# Create Pattern
selection = BodySelection.Create(GetRootPart().GetAllBodies())
data = LinearPatternData()
data.PatternDimension = PatternDimensionType.Two
data.LinearDirection = Selection.Create(GetRootPart().CoordinateSystems[0].Axes[1])
data.CountX = 5
data.PitchX = UM(416)
data.CountY = 5
data.PitchY = UM(416)
result = Pattern.CreateLinear(selection, data, None)
# EndBlock

## Create Pattern
#selection = FaceSelection.Create([GetRootPart().Bodies[7].Faces[4],
#   GetRootPart().Bodies[7].Faces[5],
#   GetRootPart().Bodies[7].Faces[6],
#   GetRootPart().Bodies[7].Faces[7]])
#data = FillPatternData()
#data.LinearDirection = EdgeSelection.Create(GetRootPart().Bodies[7].Edges[6])
#data.FillPatternType = FillPatternType.Offset
#data.XSpacing = UM(450)
#data.YSpacing = UM(500)
#data.Margin = UM(55)
#result = Pattern.CreateFill(selection, data, None)
## EndBlock

selection=BodySelection.CreateByNames("Substrate")
Combine.Merge(selection)
selection=BodySelection.CreateByNames("ChromiumForAdhesion")
Combine.Merge(selection)
selection=BodySelection.CreateByNames("Gold Layer")
Combine.Merge(selection)
selection=BodySelection.CreateByNames("ChromiumForSurfacePassivation")
Combine.Merge(selection)
selection=BodySelection.CreateByNames("DNA Large Ring")
result = ComponentHelper.MoveBodiesToComponent(selection, None)

selection=BodySelection.CreateByNames("DNA Small Ring")
result = ComponentHelper.MoveBodiesToComponent(selection, None)

selection=BodySelection.CreateByNames("Region")
Combine.Merge(selection)

# Create New Layer
selection = ComponentSelection.Create(GetRootPart().Components[4])
result = Layers.Create(selection, None)
# EndBlock

selection=ComponentSelection.Create([GetRootPart().Components[6],
    GetRootPart().Components[0],
    GetRootPart().Components[1],
    GetRootPart().Components[2],
    GetRootPart().Components[3],
    GetRootPart().Components[4],
    GetRootPart().Components[5]])
Delete.Execute(selection)
Layers.Create("Substrate")
# Move Objects to Layer: Substrate
selection = BodySelection.Create(GetRootPart().Bodies[0])
layerName = r"Substrate"
result = Layers.MoveTo(selection, layerName)
# EndBlock
