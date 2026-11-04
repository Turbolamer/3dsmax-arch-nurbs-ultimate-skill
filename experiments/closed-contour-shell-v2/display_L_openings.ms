(
local wall=undefined
local guide=undefined
local tm=undefined
local out=""
local before=objects.count
try (
 if (getNodeByName "CCSV2_DEMO_L_openings") != undefined do throw "Probe name collision"
 local factor=units.decodeValue "1cm"
 local verts=#([0.0,0.0,0.0],[100.0,0.0,0.0],[200.0,0.0,0.0],[600.0,0.0,0.0],[600.0,250.0,0.0],[350.0,250.0,0.0],[350.0,310.0,0.0],[350.0,430.0,0.0],[350.0,500.0,0.0],[0.0,500.0,0.0],[0.0,0.0,90.0],[100.0,0.0,90.0],[200.0,0.0,90.0],[600.0,0.0,90.0],[600.0,250.0,90.0],[350.0,250.0,90.0],[350.0,310.0,90.0],[350.0,430.0,90.0],[350.0,500.0,90.0],[0.0,500.0,90.0],[0.0,0.0,210.0],[100.0,0.0,210.0],[200.0,0.0,210.0],[600.0,0.0,210.0],[600.0,250.0,210.0],[350.0,250.0,210.0],[350.0,310.0,210.0],[350.0,430.0,210.0],[350.0,500.0,210.0],[0.0,500.0,210.0],[0.0,0.0,220.0],[100.0,0.0,220.0],[200.0,0.0,220.0],[600.0,0.0,220.0],[600.0,250.0,220.0],[350.0,250.0,220.0],[350.0,310.0,220.0],[350.0,430.0,220.0],[350.0,500.0,220.0],[0.0,500.0,220.0],[0.0,0.0,300.0],[100.0,0.0,300.0],[200.0,0.0,300.0],[600.0,0.0,300.0],[600.0,250.0,300.0],[350.0,250.0,300.0],[350.0,310.0,300.0],[350.0,430.0,300.0],[350.0,500.0,300.0],[0.0,500.0,300.0])
 local polygons=#(#(1,2,12,11),#(2,3,13,12),#(3,4,14,13),#(4,5,15,14),#(5,6,16,15),#(6,7,17,16),#(7,8,18,17),#(8,9,19,18),#(9,10,20,19),#(10,1,11,20),#(11,12,22,21),#(12,13,23,22),#(13,14,24,23),#(14,15,25,24),#(15,16,26,25),#(16,17,27,26),#(17,18,28,27),#(18,19,29,28),#(19,20,30,29),#(20,11,21,30),#(21,22,32,31),#(22,23,33,32),#(23,24,34,33),#(24,25,35,34),#(25,26,36,35),#(26,27,37,36),#(27,28,38,37),#(28,29,39,38),#(29,30,40,39),#(30,21,31,40),#(31,32,42,41),#(32,33,43,42),#(33,34,44,43),#(34,35,45,44),#(35,36,46,45),#(36,37,47,46),#(37,38,48,47),#(38,39,49,48),#(39,40,50,49),#(40,31,41,50))
 guide=SplineShape name:"CCSV2_DEMO_L_openings_InnerSpline"
 addNewSpline guide
 for i=1 to 10 do addKnot guide 1 #corner #line (verts[i]*factor)
 close guide 1
 updateShape guide
 guide.isHidden=true
 wall=Editable_mesh name:"CCSV2_DEMO_L_openings"
 convertTo wall Editable_Poly
 for p in verts do polyop.createVert wall (p*factor)
 for indices in polygons do (
   local idx=polyop.createPolygon wall indices
   if idx == 0 do throw "createPolygon returned zero"
 )
 polyop.deleteFaces wall #{2,12,17,27} delIsoVerts:true
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
 out="CASE|id=L_openings|baseFaces="+(baseFaces as string)+"|mods="+(wall.modifiers.count as string)+"|straight="+(sh.straightenCorners as string)+"|normal1="+(normal1 as string)+"|open="+(openCount as string)+"|badValence="+(badValence as string)+"|degenerate="+(degenerate as string)+"|volume="+(signedVol as string)+"|min="+(minV as string)+"|max="+(maxV as string)+"|triangles="+(tm.numfaces as string)
) catch (out="ERROR|id=L_openings|message="+(getCurrentException()))
if tm != undefined do delete tm
if isValidNode wall do (wall.wirecolor=color 190 203 218; wall.allEdges=true)
if isValidNode guide do guide.wirecolor=color 255 180 50
out+"|before="+(before as string)+"|after="+(objects.count as string)
)
