(
local wall=undefined
local guide=undefined
local tm=undefined
local out=""
local before=objects.count
try (
 if (getNodeByName "CCSV2_DEMO_rectangle_blind") != undefined do throw "Probe name collision"
 local factor=units.decodeValue "1cm"
 local verts=#([0.0,0.0,0.0],[600.0,0.0,0.0],[600.0,400.0,0.0],[0.0,400.0,0.0],[0.0,0.0,300.0],[600.0,0.0,300.0],[600.0,400.0,300.0],[0.0,400.0,300.0])
 local polygons=#(#(1,2,6,5),#(2,3,7,6),#(3,4,8,7),#(4,1,5,8))
 guide=SplineShape name:"CCSV2_DEMO_rectangle_blind_InnerSpline"
 addNewSpline guide
 for i=1 to 4 do addKnot guide 1 #corner #line (verts[i]*factor)
 close guide 1
 updateShape guide
 guide.isHidden=true
 wall=Editable_mesh name:"CCSV2_DEMO_rectangle_blind"
 convertTo wall Editable_Poly
 for p in verts do polyop.createVert wall (p*factor)
 for indices in polygons do (
   local idx=polyop.createPolygon wall indices
   if idx == 0 do throw "createPolygon returned zero"
 )
 polyop.deleteFaces wall #{} delIsoVerts:true
 polyop.setFaceSmoothGroup wall #all 0
 local baseFaces=polyop.getNumFaces wall
 local normal1=polyop.getFaceNormal wall 1
 local sh=Shell innerAmount:0 outerAmount:(30*factor) straightenCorners:true segments:1 autoSmooth:false overrideMatID:true matID:3 overrideInnerMatID:true matInnerID:1 overrideOuterMatID:true matOuterID:2
 addModifier wall sh
 tm=snapshotAsMesh wall
 local openCount=(meshop.getOpenEdges tm).numberSet
 local signedVol=0.0 as double
 local degenerate=0
 local badValence=0
 local edgeUses=#()
 local minV=[1e9,1e9,1e9]
 local maxV=[-1e9,-1e9,-1e9]
 for i=1 to tm.numverts do (
   local p=(getVert tm i)/factor
   for k=1 to 3 do (minV[k]=amin minV[k] p[k]; maxV[k]=amax maxV[k] p[k])
 )
 for i=1 to tm.numfaces do (
   local fi=getFace tm i
   local a=(getVert tm fi.x)/factor
   local b=(getVert tm fi.y)/factor
   local c=(getVert tm fi.z)/factor
   if length (cross (b-a) (c-a)) < 0.00001 do degenerate+=1
   local ax=a.x as double; local ay=a.y as double; local az=a.z as double
   local bx=b.x as double; local byv=b.y as double; local bz=b.z as double
   local cx=c.x as double; local cy=c.y as double; local cz=c.z as double
   signedVol+=(ax*(byv*cz-bz*cy)+ay*(bz*cx-bx*cz)+az*(bx*cy-byv*cx))/6.0
   for pair in #([fi.x,fi.y],[fi.y,fi.z],[fi.z,fi.x]) do (
     local lo=amin pair.x pair.y; local hi=amax pair.x pair.y
     local key=[lo,hi]
     append edgeUses key
   )
 )
 local uniqueEdges=#()
 for key in edgeUses do appendIfUnique uniqueEdges key
 for key in uniqueEdges do (
   local uses=0
   for other in edgeUses where other == key do uses+=1
   if uses != 2 do badValence+=1
 )
 out="CASE|id=rectangle_blind|baseFaces="+(baseFaces as string)+"|mods="+(wall.modifiers.count as string)+"|straight="+(sh.straightenCorners as string)+"|normal1="+(normal1 as string)+"|open="+(openCount as string)+"|badValence="+(badValence as string)+"|degenerate="+(degenerate as string)+"|volume="+(signedVol as string)+"|min="+(minV as string)+"|max="+(maxV as string)+"|triangles="+(tm.numfaces as string)
) catch (out="ERROR|id=rectangle_blind|message="+(getCurrentException()))
if tm != undefined do delete tm
if isValidNode wall do (wall.wirecolor=color 190 203 218; wall.allEdges=true)
if isValidNode guide do guide.wirecolor=color 255 180 50
out+"|before="+(before as string)+"|after="+(objects.count as string)
)
