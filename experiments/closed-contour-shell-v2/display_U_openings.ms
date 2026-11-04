(
local wall=undefined
local guide=undefined
local tm=undefined
local out=""
local before=objects.count
try (
 if (getNodeByName "CCSV2_DEMO_U_openings") != undefined do throw "Probe name collision"
 local factor=units.decodeValue "1cm"
 local verts=#([0.0,0.0,0.0],[100.0,0.0,0.0],[200.0,0.0,0.0],[800.0,0.0,0.0],[800.0,600.0,0.0],[550.0,600.0,0.0],[550.0,500.0,0.0],[550.0,350.0,0.0],[550.0,250.0,0.0],[250.0,250.0,0.0],[250.0,340.0,0.0],[250.0,470.0,0.0],[250.0,600.0,0.0],[0.0,600.0,0.0],[0.0,0.0,80.0],[100.0,0.0,80.0],[200.0,0.0,80.0],[800.0,0.0,80.0],[800.0,600.0,80.0],[550.0,600.0,80.0],[550.0,500.0,80.0],[550.0,350.0,80.0],[550.0,250.0,80.0],[250.0,250.0,80.0],[250.0,340.0,80.0],[250.0,470.0,80.0],[250.0,600.0,80.0],[0.0,600.0,80.0],[0.0,0.0,100.0],[100.0,0.0,100.0],[200.0,0.0,100.0],[800.0,0.0,100.0],[800.0,600.0,100.0],[550.0,600.0,100.0],[550.0,500.0,100.0],[550.0,350.0,100.0],[550.0,250.0,100.0],[250.0,250.0,100.0],[250.0,340.0,100.0],[250.0,470.0,100.0],[250.0,600.0,100.0],[0.0,600.0,100.0],[0.0,0.0,210.0],[100.0,0.0,210.0],[200.0,0.0,210.0],[800.0,0.0,210.0],[800.0,600.0,210.0],[550.0,600.0,210.0],[550.0,500.0,210.0],[550.0,350.0,210.0],[550.0,250.0,210.0],[250.0,250.0,210.0],[250.0,340.0,210.0],[250.0,470.0,210.0],[250.0,600.0,210.0],[0.0,600.0,210.0],[0.0,0.0,220.0],[100.0,0.0,220.0],[200.0,0.0,220.0],[800.0,0.0,220.0],[800.0,600.0,220.0],[550.0,600.0,220.0],[550.0,500.0,220.0],[550.0,350.0,220.0],[550.0,250.0,220.0],[250.0,250.0,220.0],[250.0,340.0,220.0],[250.0,470.0,220.0],[250.0,600.0,220.0],[0.0,600.0,220.0],[0.0,0.0,230.0],[100.0,0.0,230.0],[200.0,0.0,230.0],[800.0,0.0,230.0],[800.0,600.0,230.0],[550.0,600.0,230.0],[550.0,500.0,230.0],[550.0,350.0,230.0],[550.0,250.0,230.0],[250.0,250.0,230.0],[250.0,340.0,230.0],[250.0,470.0,230.0],[250.0,600.0,230.0],[0.0,600.0,230.0],[0.0,0.0,300.0],[100.0,0.0,300.0],[200.0,0.0,300.0],[800.0,0.0,300.0],[800.0,600.0,300.0],[550.0,600.0,300.0],[550.0,500.0,300.0],[550.0,350.0,300.0],[550.0,250.0,300.0],[250.0,250.0,300.0],[250.0,340.0,300.0],[250.0,470.0,300.0],[250.0,600.0,300.0],[0.0,600.0,300.0])
 local polygons=#(#(1,2,16,15),#(2,3,17,16),#(3,4,18,17),#(4,5,19,18),#(5,6,20,19),#(6,7,21,20),#(7,8,22,21),#(8,9,23,22),#(9,10,24,23),#(10,11,25,24),#(11,12,26,25),#(12,13,27,26),#(13,14,28,27),#(14,1,15,28),#(15,16,30,29),#(16,17,31,30),#(17,18,32,31),#(18,19,33,32),#(19,20,34,33),#(20,21,35,34),#(21,22,36,35),#(22,23,37,36),#(23,24,38,37),#(24,25,39,38),#(25,26,40,39),#(26,27,41,40),#(27,28,42,41),#(28,15,29,42),#(29,30,44,43),#(30,31,45,44),#(31,32,46,45),#(32,33,47,46),#(33,34,48,47),#(34,35,49,48),#(35,36,50,49),#(36,37,51,50),#(37,38,52,51),#(38,39,53,52),#(39,40,54,53),#(40,41,55,54),#(41,42,56,55),#(42,29,43,56),#(43,44,58,57),#(44,45,59,58),#(45,46,60,59),#(46,47,61,60),#(47,48,62,61),#(48,49,63,62),#(49,50,64,63),#(50,51,65,64),#(51,52,66,65),#(52,53,67,66),#(53,54,68,67),#(54,55,69,68),#(55,56,70,69),#(56,43,57,70),#(57,58,72,71),#(58,59,73,72),#(59,60,74,73),#(60,61,75,74),#(61,62,76,75),#(62,63,77,76),#(63,64,78,77),#(64,65,79,78),#(65,66,80,79),#(66,67,81,80),#(67,68,82,81),#(68,69,83,82),#(69,70,84,83),#(70,57,71,84),#(71,72,86,85),#(72,73,87,86),#(73,74,88,87),#(74,75,89,88),#(75,76,90,89),#(76,77,91,90),#(77,78,92,91),#(78,79,93,92),#(79,80,94,93),#(80,81,95,94),#(81,82,96,95),#(82,83,97,96),#(83,84,98,97),#(84,71,85,98))
 guide=SplineShape name:"CCSV2_DEMO_U_openings_InnerSpline"
 addNewSpline guide
 for i=1 to 14 do addKnot guide 1 #corner #line (verts[i]*factor)
 close guide 1
 updateShape guide
 guide.isHidden=true
 wall=Editable_mesh name:"CCSV2_DEMO_U_openings"
 convertTo wall Editable_Poly
 for p in verts do polyop.createVert wall (p*factor)
 for indices in polygons do (
   local idx=polyop.createPolygon wall indices
   if idx == 0 do throw "createPolygon returned zero"
 )
 polyop.deleteFaces wall #{2,16,25,30,35,39,49,53,63} delIsoVerts:true
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
 out="CASE|id=U_openings|baseFaces="+(baseFaces as string)+"|mods="+(wall.modifiers.count as string)+"|straight="+(sh.straightenCorners as string)+"|normal1="+(normal1 as string)+"|open="+(openCount as string)+"|badValence="+(badValence as string)+"|degenerate="+(degenerate as string)+"|volume="+(signedVol as string)+"|min="+(minV as string)+"|max="+(maxV as string)+"|triangles="+(tm.numfaces as string)
) catch (out="ERROR|id=U_openings|message="+(getCurrentException()))
if tm != undefined do delete tm
if isValidNode wall do (wall.wirecolor=color 190 203 218; wall.allEdges=true)
if isValidNode guide do guide.wirecolor=color 255 180 50
out+"|before="+(before as string)+"|after="+(objects.count as string)
)
