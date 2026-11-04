(
-- ============================================================================
-- Wall Surface Builder v2 (closed_inner_contour_shell_v2)
-- Emitted by scripts/build_wall_v2.py
-- Project: pavilion-01
-- Namespace: WS
-- Targeted rebuild: deletes strictly owned nodes from ownership manifest.
-- Preserves all foreign nodes and sentinels.
-- ============================================================================

local ownedNodeNames = #(
    "WS_storey_1",
    "WS_storey_1_InnerSpline"
)

for nm in ownedNodeNames do (
    local nd = getNodeByName nm
    if nd != undefined and isValidNode nd do (
        delete nd
    )
)

local factor = units.decodeValue "1cm"

-- Storey: storey_1
(
    local guideVerts = #(
        [0.0,0.0,0.0], [100.0,0.0,0.0], [200.0,0.0,0.0], [320.0,0.0,0.0], [500.0,0.0,0.0],
        [600.0,0.0,0.0], [600.0,100.0,0.0], [600.0,300.0,0.0], [600.0,400.0,0.0], [0.0,400.0,0.0]
    )
    local guide = SplineShape name:"WS_storey_1_InnerSpline"
    addNewSpline guide
    for p in guideVerts do addKnot guide 1 #corner #line (p * factor)
    close guide 1
    updateShape guide
    guide.isHidden = true

    local wallVerts = #(
        [0.0,0.0,0.0], [100.0,0.0,0.0], [200.0,0.0,0.0], [320.0,0.0,0.0], [500.0,0.0,0.0],
        [600.0,0.0,0.0], [600.0,100.0,0.0], [600.0,300.0,0.0], [600.0,400.0,0.0], [0.0,400.0,0.0],
        [0.0,0.0,90.0], [100.0,0.0,90.0], [200.0,0.0,90.0], [320.0,0.0,90.0], [500.0,0.0,90.0],
        [600.0,0.0,90.0], [600.0,100.0,90.0], [600.0,300.0,90.0], [600.0,400.0,90.0], [0.0,400.0,90.0],
        [0.0,0.0,110.0], [100.0,0.0,110.0], [200.0,0.0,110.0], [320.0,0.0,110.0], [500.0,0.0,110.0],
        [600.0,0.0,110.0], [600.0,100.0,110.0], [600.0,300.0,110.0], [600.0,400.0,110.0], [0.0,400.0,110.0],
        [0.0,0.0,210.0], [100.0,0.0,210.0], [200.0,0.0,210.0], [320.0,0.0,210.0], [500.0,0.0,210.0],
        [600.0,0.0,210.0], [600.0,100.0,210.0], [600.0,300.0,210.0], [600.0,400.0,210.0], [0.0,400.0,210.0],
        [0.0,0.0,240.0], [100.0,0.0,240.0], [200.0,0.0,240.0], [320.0,0.0,240.0], [500.0,0.0,240.0],
        [600.0,0.0,240.0], [600.0,100.0,240.0], [600.0,300.0,240.0], [600.0,400.0,240.0], [0.0,400.0,240.0],
        [0.0,0.0,300.0], [100.0,0.0,300.0], [200.0,0.0,300.0], [320.0,0.0,300.0], [500.0,0.0,300.0],
        [600.0,0.0,300.0], [600.0,100.0,300.0], [600.0,300.0,300.0], [600.0,400.0,300.0], [0.0,400.0,300.0]
    )

    local wallPolygons = #(
        #(1,2,12,11), #(2,3,13,12), #(3,4,14,13), #(4,5,15,14), #(5,6,16,15),
        #(6,7,17,16), #(7,8,18,17), #(8,9,19,18), #(9,10,20,19), #(10,1,11,20),
        #(11,12,22,21), #(12,13,23,22), #(13,14,24,23), #(14,15,25,24), #(15,16,26,25),
        #(16,17,27,26), #(17,18,28,27), #(18,19,29,28), #(19,20,30,29), #(20,11,21,30),
        #(21,22,32,31), #(22,23,33,32), #(23,24,34,33), #(24,25,35,34), #(25,26,36,35),
        #(26,27,37,36), #(27,28,38,37), #(28,29,39,38), #(29,30,40,39), #(30,21,31,40),
        #(31,32,42,41), #(32,33,43,42), #(33,34,44,43), #(34,35,45,44), #(35,36,46,45),
        #(36,37,47,46), #(37,38,48,47), #(38,39,49,48), #(39,40,50,49), #(40,31,41,50),
        #(41,42,52,51), #(42,43,53,52), #(43,44,54,53), #(44,45,55,54), #(45,46,56,55),
        #(46,47,57,56), #(47,48,58,57), #(48,49,59,58), #(49,50,60,59), #(50,41,51,60)
    )

    local wall = Editable_mesh name:"WS_storey_1"
    convertTo wall Editable_Poly
    for p in wallVerts do polyop.createVert wall (p * factor)
    for indices in wallPolygons do (
        polyop.createPolygon wall indices
    )
    local delFaces = #{2,12,14,22,24,27,37}
    if delFaces.numberSet > 0 do (
        polyop.deleteFaces wall delFaces delIsoVerts:true
    )
    polyop.setFaceSmoothGroup wall #all 0

    local sh = Shell innerAmount:0.0 outerAmount:(30.0 * factor) straightenCorners:true segments:1 autoSmooth:false overrideMatID:true matID:3 overrideInnerMatID:true matInnerID:1 overrideOuterMatID:true matOuterID:2
    addModifier wall sh
)

OK
)
