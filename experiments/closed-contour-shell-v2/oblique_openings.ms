(
local wall=undefined
local guide=undefined
local tm=undefined
local out=""
local before=objects.count
try (
 if (getNodeByName "CCSV2_PROBE_oblique_openings") != undefined do throw "Probe name collision"
 local factor=units.decodeValue "1cm"
 local verts=#([0.0,0.0,0.0],[100.0,0.0,0.0],[200.0,0.0,0.0],[600.0,0.0,0.0],[575.7464374963668,97.01425001453319,0.0],[539.3660937409168,242.53562503633296,0.0],[500.0,400.0,0.0],[100.0,400.0,0.0],[0.0,0.0,90.0],[100.0,0.0,90.0],[200.0,0.0,90.0],[600.0,0.0,90.0],[575.7464374963668,97.01425001453319,90.0],[539.3660937409168,242.53562503633296,90.0],[500.0,400.0,90.0],[100.0,400.0,90.0],[0.0,0.0,210.0],[100.0,0.0,210.0],[200.0,0.0,210.0],[600.0,0.0,210.0],[575.7464374963668,97.01425001453319,210.0],[539.3660937409168,242.53562503633296,210.0],[500.0,400.0,210.0],[100.0,400.0,210.0],[0.0,0.0,220.0],[100.0,0.0,220.0],[200.0,0.0,220.0],[600.0,0.0,220.0],[575.7464374963668,97.01425001453319,220.0],[539.3660937409168,242.53562503633296,220.0],[500.0,400.0,220.0],[100.0,400.0,220.0],[0.0,0.0,300.0],[100.0,0.0,300.0],[200.0,0.0,300.0],[600.0,0.0,300.0],[575.7464374963668,97.01425001453319,300.0],[539.3660937409168,242.53562503633296,300.0],[500.0,400.0,300.0],[100.0,400.0,300.0])
 local polygons=#(#(1,2,10,9),#(2,3,11,10),#(3,4,12,11),#(4,5,13,12),#(5,6,14,13),#(6,7,15,14),#(7,8,16,15),#(8,1,9,16),#(9,10,18,17),#(10,11,19,18),#(11,12,20,19),#(12,13,21,20),#(13,14,22,21),#(14,15,23,22),#(15,16,24,23),#(16,9,17,24),#(17,18,26,25),#(18,19,27,26),#(19,20,28,27),#(20,21,29,28),#(21,22,30,29),#(22,23,31,30),#(23,24,32,31),#(24,17,25,32),#(25,26,34,33),#(26,27,35,34),#(27,28,36,35),#(28,29,37,36),#(29,30,38,37),#(30,31,39,38),#(31,32,40,39),#(32,25,33,40))
 guide=SplineShape name:"CCSV2_PROBE_oblique_openings_InnerSpline"
 addNewSpline guide
 for i=1 to 8 do addKnot guide 1 #corner #line (verts[i]*factor)
 close guide 1
 updateShape guide
 guide.isHidden=true
 wall=Editable_mesh name:"CCSV2_PROBE_oblique_openings"
 convertTo wall Editable_Poly
 for p in verts do polyop.createVert wall (p*factor)
 for indices in polygons do (
   local idx=polyop.createPolygon wall indices
   if idx == 0 do throw "createPolygon returned zero"
 )
 polyop.deleteFaces wall #{2,10,13,21} delIsoVerts:true
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
 out="CASE|id=oblique_openings|baseFaces="+(baseFaces as string)+"|mods="+(wall.modifiers.count as string)+"|straight="+(sh.straightenCorners as string)+"|normal1="+(normal1 as string)+"|open="+(openCount as string)+"|badValence="+(badValence as string)+"|degenerate="+(degenerate as string)+"|volume="+(signedVol as string)+"|min="+(minV as string)+"|max="+(maxV as string)+"|triangles="+(tm.numfaces as string)
) catch (out="ERROR|id=oblique_openings|message="+(getCurrentException()))
if tm != undefined do delete tm
if isValidNode wall do delete wall
if isValidNode guide do delete guide
out+"|before="+(before as string)+"|after="+(objects.count as string)
)
