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

def pointAllocateFirst( distP, angP):
    seloc =Selection.Create(DatumPointCreator.Create(Point.Create(0, MM(distP), 0)).CreatedPoint)
    move = Move.Rotate(seloc, Line.Create(Point.Origin, Direction.DirZ), angP-DEG(45), MoveOptions())
    
def pointAllocateSecond(distP,angP):
    seloc =Selection.Create(DatumPointCreator.Create(Point.Create(0, MM(distP), 0)).CreatedPoint)
    move = Move.Rotate(seloc, Line.Create(Point.Origin, Direction.DirZ), angP-DEG(45+180), MoveOptions())
    
def surfaceCutOperation(offset, extrudeDistance):   
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
    selection = Selection.Create(designBody1.Faces)
    options = ExtrudeFaceOptions()
    off = OffsetFaces.Execute(selection, offset, OffsetFaceOptions())
    options.ExtrudeType = ExtrudeType.ForceCut
    result = ExtrudeFaces.Execute(selection, extrudeDistance, options)
    
######################################################################
    
pointAllocateFirst( radius ,DEG(45)+angle)
pointAllocateFirst( radius, angle-angle-DEG(45)-angle)
pointAllocateFirst( radius+width, DEG(45)+angle)
pointAllocateFirst( radius+width, angle-angle-DEG(45)-angle)
    
designBody1 = surfaceCutOperation(hCr1, hAu+hCr2)
        
######################################################################
pointAllocateFirst( radius-dEtch, DEG(45)+angle+DEG(gap))
pointAllocateFirst( radius-dEtch, angle-angle-DEG(45)-angle-DEG(gap))
pointAllocateFirst( radius+width+dEtch, DEG(45)+angle+DEG(gap))
pointAllocateFirst( radius+width+dEtch, angle-angle-DEG(45)-angle-DEG(gap))
                
designBody2 = surfaceCutOperation(hCr1, -hCr1-hEtch)

######################################################################
######################################################################
######################################################################

pointAllocateSecond( radius, DEG(45)+DEG(90)-angle-oangle )
pointAllocateSecond( radius,-(DEG(45)+DEG(90)-angle-oangle ))
pointAllocateSecond( radius+width, DEG(45)+DEG(90)-angle-oangle)
pointAllocateSecond( radius+width, -(DEG(45)+DEG(90)-angle-oangle))
           
designBody3 = surfaceCutOperation(hCr1, hAu+hCr2)

######################################################################

pointAllocateSecond( radius-dEtch, DEG(45)+DEG(90)-angle+DEG(gap)-oangle)
pointAllocateSecond( radius-dEtch, -(DEG(45)+DEG(90)-angle+DEG(gap)-oangle))
pointAllocateSecond( radius+width+dEtch, DEG(45)+DEG(90)-angle+DEG(gap)-oangle)
pointAllocateSecond( radius+width+dEtch, -(DEG(45)+DEG(90)-angle+DEG(gap)-oangle))
           
designBody4 = surfaceCutOperation(hCr1, -hCr1-hEtch)
######################################################################

######################################################################

# Round Edges to show edged region
selectFirstRing= EdgeSelection.Create(GetRootPart().Bodies[0].Faces[8].Edges)
result = ConstantRound.Execute(selectFirstRing, MM(hEtch), ConstantRoundOptions())
selectSecondRing2 = EdgeSelection.Create(GetRootPart().Bodies[0].Faces[9].Edges)
result2 = ConstantRound.Execute(selectSecondRing2, MM(hEtch), ConstantRoundOptions())

######################################################################
# END OF SURFACE APPROACH

######################################################################

dnaGap = dnaT/radius*(180/math.pi)

def pointAllocateFirst( distP, angP):
    seloc =Selection.Create(DatumPointCreator.Create(Point.Create(0, MM(distP), 0)).CreatedPoint)
    move = Move.Rotate(seloc, Line.Create(Point.Origin, Direction.DirZ), angP-DEG(45), MoveOptions())
    
def pointAllocateSecond(distP,angP):
    seloc =Selection.Create(DatumPointCreator.Create(Point.Create(0, MM(distP), 0)).CreatedPoint)
    move = Move.Rotate(seloc, Line.Create(Point.Origin, Direction.DirZ), angP-DEG(45+180), MoveOptions())
    
def dnaExtrudsion(offset, extrudeDistance):   
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
    selection = Selection.Create(designBody1.Faces)
    options = ExtrudeFaceOptions()    
    off = OffsetFaces.Execute(selection, offset, OffsetFaceOptions())
    options.ExtrudeType = ExtrudeType.ForceIndependent
    result = ExtrudeFaces.Execute(selection, extrudeDistance, options)

pointAllocateFirst( radius+dnaT, DEG(45)+angle)
pointAllocateFirst( radius+dnaT, angle-angle-DEG(45)-angle)
pointAllocateFirst( radius+width-dnaT, DEG(45)+angle)
pointAllocateFirst( radius+width-dnaT, angle-angle-DEG(45)-angle)

designBody1 = dnaExtrudsion(hCr1-dnaT, dnaT)

pointAllocateFirst( radius-dEtch, DEG(45)+angle+DEG(gap))
pointAllocateFirst( radius-dEtch, angle-angle-DEG(45)-angle-DEG(gap))
pointAllocateFirst( radius+width+dEtch, DEG(45)+angle+DEG(gap))
pointAllocateFirst( radius+width+dEtch, angle-angle-DEG(45)-angle-DEG(gap))
                
designBody2 = dnaExtrudsion(hCr1-dnaT, dnaT)


# Intersect Bodies
targets = BodySelection.Create(GetRootPart().Bodies[5])
tools =  BodySelection.Create(GetRootPart().Bodies[4])
options = MakeSolidsOptions()
options.KeepCutter = False
result = Combine.Intersect(targets, tools, options)
GetRootPart().Bodies[5].Delete()
# EndBlock

def dnaExtrudsionCut(offset, extrudeDistance):   
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
    selection = Selection.Create(designBody1.Faces)
    options = ExtrudeFaceOptions()    
    off = OffsetFaces.Execute(selection, offset, OffsetFaceOptions())
    options.ExtrudeType = ExtrudeType.ForceCut
    result = ExtrudeFaces.Execute(selection, extrudeDistance, options)

pointAllocateFirst( radius ,DEG(45)+angle)
pointAllocateFirst( radius, angle-angle-DEG(45)-angle)
pointAllocateFirst( radius+width, DEG(45)+angle)
pointAllocateFirst( radius+width, angle-angle-DEG(45)-angle)
    
designBody3 = dnaExtrudsion(hCr1-dnaT, hAu+dnaT)

pointAllocateFirst( radius+dnaT, DEG(45)+angle-DEG(dnaGap))
pointAllocateFirst( radius+dnaT, angle-angle-DEG(45)-angle+DEG(dnaGap))
pointAllocateFirst( radius+width-dnaT, DEG(45)+angle-DEG(dnaGap))
pointAllocateFirst( radius+width-dnaT, angle-angle-DEG(45)-angle+DEG(dnaGap))

designBody4 = dnaExtrudsionCut(hCr1-dnaT, hAu+dnaT)

# Merge Bodies
targets = BodySelection.Create([GetRootPart().Bodies[5],
    GetRootPart().Bodies[4]])
result = Combine.Merge(targets)
# EndBlock
######################################################################
######################################################################

# Set Section View and Zoom to Entity
# showLayersSeparated(0.1)
createPlane(Parameters.PlaneAngle)
result = ViewHelper.SetSectionPlane(Plane.PlaneYZ)
Selection.Clear()
ViewHelper.ZoomToEntity()
# EndBlock

#######################################################################