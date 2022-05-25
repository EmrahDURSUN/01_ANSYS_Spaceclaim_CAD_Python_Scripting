
# Python Script, API Version = V22 Beta
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

def pointAllocate(distP,angP):
    seloc =Selection.Create(DatumPointCreator.Create(Point.Create(0, MM(distP), 0)).CreatedPoint)
    move = Move.Rotate(seloc, Line.Create(Point.Origin, Direction.DirZ), angP-DEG(45), MoveOptions())
    
pointAllocate( radius-dEtch ,DEG(45)+angle+DEG(gap))
pointAllocate( radius-dEtch, angle-angle-DEG(45)-angle-DEG(gap))
pointAllocate( radius+width+dEtch ,DEG(45)+angle+DEG(gap))
pointAllocate( radius+width+dEtch, angle-angle-DEG(45)-angle-DEG(gap))

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
######################################################################
def pointAllocate(distP,angP):
    seloc =Selection.Create(DatumPointCreator.Create(Point.Create(0, MM(distP), 0)).CreatedPoint)
    move = Move.Rotate(seloc, Line.Create(Point.Origin, Direction.DirZ), angP-DEG(45+180), MoveOptions())
       
pointAllocate( radius-dEtch ,DEG(45)+DEG(90)-angle+DEG(gap)-oangle)
pointAllocate( radius-dEtch,-(DEG(45)+DEG(90)-angle+DEG(gap)-oangle))
pointAllocate( radius+width+dEtch ,DEG(45)+DEG(90)-angle+DEG(gap)-oangle)
pointAllocate( radius+width+dEtch, -(DEG(45)+DEG(90)-angle+DEG(gap)-oangle))

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
designBody2 = designResult.CreatedBody

# Cut substrate
selection = Selection.Create(designBody1.Faces)
options = ExtrudeFaceOptions()
off = OffsetFaces.Execute(selection, hCr1, OffsetFaceOptions())
options.ExtrudeType = ExtrudeType.ForceCut
result = ExtrudeFaces.Execute(selection, -hCr1-hEtch, options)

# Cut substrate
selection = Selection.Create(designBody2.Faces)
options = ExtrudeFaceOptions()
off = OffsetFaces.Execute(selection, hCr1, OffsetFaceOptions())
options.ExtrudeType = ExtrudeType.ForceCut
result = ExtrudeFaces.Execute(selection, -hCr1-hEtch, options)

######################################################################

######################################################################

def pointAllocate(distP,angP):
    seloc =Selection.Create(DatumPointCreator.Create(Point.Create(0, MM(distP), 0)).CreatedPoint)
    move = Move.Rotate(seloc, Line.Create(Point.Origin, Direction.DirZ), angP-DEG(45), MoveOptions())
    
pointAllocate( radius ,DEG(45)+angle)
pointAllocate( radius, angle-angle-DEG(45)-angle)
pointAllocate( radius+width,DEG(45)+angle)
pointAllocate( radius+width, angle-angle-DEG(45)-angle)

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
######################################################################
def pointAllocate(distP,angP):
    seloc =Selection.Create(DatumPointCreator.Create(Point.Create(0, MM(distP), 0)).CreatedPoint)
    move = Move.Rotate(seloc, Line.Create(Point.Origin, Direction.DirZ), angP-DEG(45+180), MoveOptions())
       
pointAllocate( radius ,DEG(45)+DEG(90)-angle-oangle)
pointAllocate( radius,-(DEG(45)+DEG(90)-angle-oangle))
pointAllocate( radius+width ,DEG(45)+DEG(90)-angle-oangle)
pointAllocate( radius+width, -(DEG(45)+DEG(90)-angle-oangle))

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
designBody2 = designResult.CreatedBody

##########################

# Cut substrate
selection = Selection.Create(designBody1.Faces)
options = ExtrudeFaceOptions()
off = OffsetFaces.Execute(selection, hCr1, OffsetFaceOptions())
options.ExtrudeType = ExtrudeType.ForceCut
result = ExtrudeFaces.Execute(selection, hAu+hCr2, options)

# Cut substrate
selection = Selection.Create(designBody2.Faces)
options = ExtrudeFaceOptions()
off = OffsetFaces.Execute(selection,hCr1, OffsetFaceOptions())
options.ExtrudeType = ExtrudeType.ForceCut
result = ExtrudeFaces.Execute(selection, hAu+hCr2, options)

######################################################################

# Round Edges to show edged region
selectFirstRing= EdgeSelection.Create(GetRootPart().Bodies[0].Faces[8].Edges)
result = ConstantRound.Execute(selectFirstRing, MM(hEtch), ConstantRoundOptions())
selectSecondRing2 = EdgeSelection.Create(GetRootPart().Bodies[0].Faces[9].Edges)
result2 = ConstantRound.Execute(selectSecondRing2, MM(hEtch), ConstantRoundOptions())

######################################################################
# END OF SURFACE APPROACH

# Set Section View and Zoom to Entity
# showLayersSeparated(0.1)
createPlane(Parameters.PlaneAngle)
# result = ViewHelper.SetSectionPlane(Plane.PlaneYZ)
Selection.Clear()
ViewHelper.ZoomToEntity()
# EndBlock

#######################################################################
