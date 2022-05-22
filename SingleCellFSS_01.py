# Python Script, API Version = V21
import math

while GetRootPart().Components.Count > 0:
    GetRootPart().Components[0].Delete()
while GetRootPart().Bodies.Count > 0:
    GetRootPart().Bodies[0].Delete()
while GetRootPart().Curves.Count > 0:
    GetRootPart().Curves[0].Delete()
while GetRootPart().DatumPlanes.Count > 0:
    GetRootPart().DatumPlanes[0].Delete()
while GetRootPart().DatumPoints.Count > 0:
    GetRootPart().DatumPoints[0].Delete()
   
   
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
# End Parameters

def createBoundayCurves(radius, dEtch, hCr1, hEtch, width, hAu, hCr2):
    boundary = List[ITrimmedCurve]()
    boundary.Add( CurveSegment.Create(   Point.Create(MM(radius-dEtch),MM(0),MM(hCr1) ),                     Point.Create(MM(radius-dEtch),MM(0),MM(-hEtch) )                    ) ) #0-1
    boundary.Add( CurveSegment.Create(   Point.Create(MM(radius-dEtch),MM(0),MM(-hEtch) ),                   Point.Create(MM(radius+width+dEtch),MM(0),MM(-hEtch) )        ) ) #1-2
    boundary.Add( CurveSegment.Create(   Point.Create(MM(radius+width+dEtch),MM(0),MM(-hEtch) ),       Point.Create(MM(radius+dEtch+width),MM(0),MM(hCr1) )           ) ) #2-3
    boundary.Add( CurveSegment.Create(   Point.Create(MM(radius+width+dEtch),MM(0),MM(hCr1) ) ,         Point.Create(MM(radius+width),MM(0),MM(hCr1) )                     ) ) #3-4
    boundary.Add( CurveSegment.Create(   Point.Create(MM(radius+width),MM(0),MM(hCr1) ) ,                   Point.Create(MM(radius+width),MM(0),MM(hCr1+hAu+hCr2) )     ) ) #4-5
    boundary.Add( CurveSegment.Create(   Point.Create(MM(radius+width),MM(0),MM(hCr1+hAu+hCr2) ),   Point.Create(MM(radius),MM(0),MM(hCr1+hAu+hCr2) )               ) ) #5-6
    boundary.Add( CurveSegment.Create(   Point.Create(MM(radius),MM(0),MM(hCr1+hAu+hCr2) ),             Point.Create(MM(radius),MM(0),MM(hCr1) )                                ) ) #6-7
    boundary.Add( CurveSegment.Create(   Point.Create(MM(radius),MM(0),MM(hCr1) ),                              Point.Create(MM(radius-dEtch),MM(0),MM(hCr1) )                       ) ) #7-0
    return boundary

# Constructor MoveSurface Anda Revolve
def MoveSurfaceAndRevolveSymetrically(param, locationAngle, ringAngle):
    resultLarge = Move.Rotate(Selection.Create(plaBoReList[param].CreatedBody.Faces[0]) , Line.Create(Point.Origin, Direction.DirZ), DEG(locationAngle), MoveOptions())
    options = RevolveFaceOptions()
    options.PullSymmetric = True
    options.ExtrudeType = ExtrudeType.ForceCut
    RevolveFaces.Execute(Selection.Create(plaBoReList[param].CreatedBody.Faces[0]), Line.Create(Point.Origin, Direction.DirZ), ringAngle, options)
    
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

# Create List of Surfaces by the boundary
plaBoReList = List[PlanarBodyResult]()
t = 0
while t <2: #number of rings is 2 for now, thus wejust need to PlanarBodyResult
    plaBoReList.Add(PlanarBody.Create(Plane.PlaneZX, createBoundayCurves(radius, dEtch, hCr1, hEtch, width, hAu, hCr2))) 
    plaBoReList[t].CreatedBody.SetName(t.ToString())
    t = t + 1

ringAngleFirst = DEG(45)+angle # Location of first ring
ringAngleSecond = DEG(135)-angle-oangle  #Location of second ring
 
MoveSurfaceAndRevolveSymetrically(0, 45, ringAngleFirst)
MoveSurfaceAndRevolveSymetrically(1 ,225, ringAngleSecond)

gap = dEtch/radius*(180/math.pi)

def moreCutForAccurateUndercut(bo, fa):
    selection = FaceSelection.Create(GetRootPart().Bodies[bo].Faces[fa])
    axisSelection = Selection.Create(GetRootPart().CoordinateSystems[0].Axes[2])
    axis = RevolveFaces.GetAxisFromSelection(selection, axisSelection)
    options = RevolveFaceOptions()
    options.ExtrudeType = ExtrudeType.ForceCut
    result = RevolveFaces.Execute(selection, axis, DEG(gap), options)
    result = RevolveFaces.Execute(selection, axis, DEG(-gap), options)
    
moreCutForAccurateUndercut(0, 9)
moreCutForAccurateUndercut(0, 10)
moreCutForAccurateUndercut(0, 14)
moreCutForAccurateUndercut(0, 15)

moreCutForAccurateUndercut(1, 7)
moreCutForAccurateUndercut(1, 11)
moreCutForAccurateUndercut(1, 9)
moreCutForAccurateUndercut(1, 13)

# Round Edges to show edged region
selectFirstRing= EdgeSelection.Create(GetRootPart().Bodies[0].Faces[6].Edges)
result = ConstantRound.Execute(selectFirstRing, MM(hEtch), ConstantRoundOptions())
selectSecondRing = EdgeSelection.Create(GetRootPart().Bodies[0].Faces[7].Edges)
result2 = ConstantRound.Execute(selectSecondRing, MM(hEtch), ConstantRoundOptions())

######################################################################
# END OF REVOLVE WAY

# Set Section View and Zoom to Entity
#showLayersSeparated(0.1)
createPlane(Parameters.PlaneAngle)
result = ViewHelper.SetSectionPlane(Plane.PlaneYZ)
Selection.Clear()
ViewHelper.ZoomToEntity()
# EndBlock