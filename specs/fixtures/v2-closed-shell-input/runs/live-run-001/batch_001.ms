-- Batch batch_001 for QA run live-run-001
global __qa_last_batch_result = (
    local __qa_out = stringStream ""
    format "START_BATCH batch_id=%\n" "batch_001" to:__qa_out
    local sysType = (units.SystemType as string)
    local sysScale = (units.SystemScale as string)
    format "GUARD units.SystemType=% units.SystemScale=%\n" sysType sysScale to:__qa_out
    -- Observation O79666e0ca53fff52293a1d4a61c190ee8a8553bc0d25e2da14c25d83c6cf1a1 (CHK_SOLID)
    local nd = getNodeByName "WS_storey_1"
    if nd != undefined then (
        local p = nd.pos
        local bMin = nd.min
        local bMax = nd.max
        local modCount = nd.modifiers.count
        local isHidden = (nd.isHidden as string)
        local baseCls = if isProperty nd #baseObject and nd.baseObject != undefined then (classOf nd.baseObject as string) else (classOf nd as string)
        local mod1Cls = if modCount > 0 then (classOf nd.modifiers[1] as string) else "none"
        local innerAmt = 0.0d0; local outerAmt = 0.0d0; local segs = 0
        local straightenCorners = false
        if modCount > 0 and (classOf nd.modifiers[1]) == Shell do (
            local sm = nd.modifiers[1]
            try ( innerAmt = sm.innerAmount as double ) catch ()
            try ( outerAmt = sm.outerAmount as double ) catch ()
            try ( segs = sm.segments as integer ) catch ()
            try ( straightenCorners = sm.straightenCorners as booleanClass ) catch ()
        )
        local guideNd = getNodeByName (nd.name + "_InnerSpline")
        local guideKnots = #()
        if guideNd != undefined and (classOf guideNd) == SplineShape do (
            local nK = numKnots guideNd 1
            guideKnots = for k = 1 to nK collect (getKnotPoint guideNd 1 k)
        )
        local maxYDev = 0.0d0
        local nVerts = 0; local nEdges = 0; local dupVerts = 0; local seamValenceErr = 0; local tJunctions = 0
        try (
            if (classOf nd.baseObject) == Editable_Poly do (
                nVerts = polyop.getNumVerts nd.baseObject
                nEdges = polyop.getNumEdges nd.baseObject
                for vi = 1 to nVerts do (
                    local vp = polyop.getVert nd.baseObject vi
                    local dev = 0.0d0
                    if guideKnots.count > 0 then (
                        local minD = 1e9
                        local p2d = [vp.x, vp.y, 0]
                        for kp in guideKnots do (
                            local d = distance p2d [kp.x, kp.y, 0]
                            if d < minD do minD = d
                        )
                        dev = minD
                    ) else (
                        dev = abs (vp.y as double)
                    )
                    if dev > maxYDev do maxYDev = dev
                )
                if nVerts <= 1000 do (
                    for vi = 1 to (nVerts - 1) do (
                        local pvi = polyop.getVert nd.baseObject vi
                        for vj = (vi + 1) to nVerts do (
                            local pvj = polyop.getVert nd.baseObject vj
                            if (distance pvi pvj) < 0.001 do dupVerts += 1
                        )
                    )
                )
                for ei = 1 to nEdges do (
                    local ev = polyop.getEdgeVerts nd.baseObject ei
                    local p1 = polyop.getVert nd.baseObject ev[1]
                    local p2 = polyop.getVert nd.baseObject ev[2]
                    local ef = polyop.getEdgeFaces nd.baseObject ei
                    if ef.count > 2 do tJunctions += 1
                    if (abs (p1.x - p2.x) < 0.01) and (abs (p1.y - p2.y) < 0.01) and (abs (p1.z - p2.z) > 0.01) do (
                        local isSeam = true
                        if guideKnots.count >= 3 do (
                            isSeam = false
                            for ki = 1 to guideKnots.count do (
                                local kp = guideKnots[ki]
                                if (distance [p1.x, p1.y, 0] [kp.x, kp.y, 0]) < 0.01 do (
                                    local prevK = if ki == 1 then guideKnots[guideKnots.count] else guideKnots[ki-1]
                                    local nextK = if ki == guideKnots.count then guideKnots[1] else guideKnots[ki+1]
                                    local vPrev = normalize ([kp.x - prevK.x, kp.y - prevK.y, 0])
                                    local vNext = normalize ([nextK.x - kp.x, nextK.y - kp.y, 0])
                                    if (abs (dot vPrev vNext)) < 0.999 do isSeam = true
                                )
                            )
                        )
                        if isSeam do (
                            if ef.count != 2 do seamValenceErr += 1
                        )
                    )
                )
            )
        ) catch ()
        local evalVol = 0.0d0
        local openEdges = 0
        local tmpMesh = undefined
        try (
            in coordsys world (tmpMesh = snapshotAsMesh nd)
            if tmpMesh != undefined do (
                local nf = tmpMesh.numFaces
                if nf > 0 do (
                    local v1 = getVert tmpMesh 1
                    for f = 1 to nf do (
                        local f3 = getFace tmpMesh f
                        local a = getVert tmpMesh (f3.x as integer)
                        local b_v = getVert tmpMesh (f3.y as integer)
                        local c = getVert tmpMesh (f3.z as integer)
                        local ax = (a.x as double) - (v1.x as double)
                        local ay = (a.y as double) - (v1.y as double)
                        local az = (a.z as double) - (v1.z as double)
                        local bx = (b_v.x as double) - (v1.x as double)
                        local b_y = (b_v.y as double) - (v1.y as double)
                        local bz = (b_v.z as double) - (v1.z as double)
                        local cx = (c.x as double) - (v1.x as double)
                        local cy = (c.y as double) - (v1.y as double)
                        local cz = (c.z as double) - (v1.z as double)
                        evalVol += (ax * (b_y * cz - bz * cy) + ay * (bz * cx - bx * cz) + az * (bx * cy - b_y * cx)) / 6.0
                    )
                    try ( openEdges = (meshop.getOpenEdges tmpMesh).numberSet ) catch ()
                )
                delete tmpMesh; tmpMesh = undefined
            )
        ) catch ( if tmpMesh != undefined do try ( delete tmpMesh ) catch () )
        format "ROW observation_id=% check_id=% target_id=% sample_id=% status=OK exists=true isHidden=% pos=[%,%,%] min=[%,%,%] max=[%,%,%] modCount=% baseCls=% mod1Cls=% innerAmt=% outerAmt=% segs=% straightenCorners=% nVerts=% nEdges=% dupVerts=% seamValenceErr=% tJunctions=% openEdges=% maxYDev=% vol=% signedVol=%\n" \
            "O79666e0ca53fff52293a1d4a61c190ee8a8553bc0d25e2da14c25d83c6cf1a1" "CHK_SOLID" "WS_storey_1" "S5986dcbe78a502f0743490cc51280d95c7064fe5c233bc09255f825f03a64a1" isHidden (p.x as string) (p.y as string) (p.z as string) \
            (bMin.x as string) (bMin.y as string) (bMin.z as string) (bMax.x as string) (bMax.y as string) (bMax.z as string) \
            (modCount as string) baseCls mod1Cls (innerAmt as string) (outerAmt as string) (segs as string) (straightenCorners as string) (nVerts as string) (nEdges as string) (dupVerts as string) (seamValenceErr as string) (tJunctions as string) (openEdges as string) (maxYDev as string) ((abs evalVol) as string) (evalVol as string) to:__qa_out
    ) else (
        format "ROW observation_id=% check_id=% target_id=% sample_id=% status=NOT_FOUND exists=false\n" \
            "O79666e0ca53fff52293a1d4a61c190ee8a8553bc0d25e2da14c25d83c6cf1a1" "CHK_SOLID" "WS_storey_1" "S5986dcbe78a502f0743490cc51280d95c7064fe5c233bc09255f825f03a64a1" to:__qa_out
    )
    -- Observation O582f7ca5d0d26e45416a8bb39c586d05e99d60112dc4bbccbd7a72879f717a4 (CHK_TOPOLOGY)
    local nd = getNodeByName "WS_storey_1"
    if nd != undefined then (
        local p = nd.pos
        local bMin = nd.min
        local bMax = nd.max
        local modCount = nd.modifiers.count
        local isHidden = (nd.isHidden as string)
        local baseCls = if isProperty nd #baseObject and nd.baseObject != undefined then (classOf nd.baseObject as string) else (classOf nd as string)
        local mod1Cls = if modCount > 0 then (classOf nd.modifiers[1] as string) else "none"
        local innerAmt = 0.0d0; local outerAmt = 0.0d0; local segs = 0
        local straightenCorners = false
        if modCount > 0 and (classOf nd.modifiers[1]) == Shell do (
            local sm = nd.modifiers[1]
            try ( innerAmt = sm.innerAmount as double ) catch ()
            try ( outerAmt = sm.outerAmount as double ) catch ()
            try ( segs = sm.segments as integer ) catch ()
            try ( straightenCorners = sm.straightenCorners as booleanClass ) catch ()
        )
        local guideNd = getNodeByName (nd.name + "_InnerSpline")
        local guideKnots = #()
        if guideNd != undefined and (classOf guideNd) == SplineShape do (
            local nK = numKnots guideNd 1
            guideKnots = for k = 1 to nK collect (getKnotPoint guideNd 1 k)
        )
        local maxYDev = 0.0d0
        local nVerts = 0; local nEdges = 0; local dupVerts = 0; local seamValenceErr = 0; local tJunctions = 0
        try (
            if (classOf nd.baseObject) == Editable_Poly do (
                nVerts = polyop.getNumVerts nd.baseObject
                nEdges = polyop.getNumEdges nd.baseObject
                for vi = 1 to nVerts do (
                    local vp = polyop.getVert nd.baseObject vi
                    local dev = 0.0d0
                    if guideKnots.count > 0 then (
                        local minD = 1e9
                        local p2d = [vp.x, vp.y, 0]
                        for kp in guideKnots do (
                            local d = distance p2d [kp.x, kp.y, 0]
                            if d < minD do minD = d
                        )
                        dev = minD
                    ) else (
                        dev = abs (vp.y as double)
                    )
                    if dev > maxYDev do maxYDev = dev
                )
                if nVerts <= 1000 do (
                    for vi = 1 to (nVerts - 1) do (
                        local pvi = polyop.getVert nd.baseObject vi
                        for vj = (vi + 1) to nVerts do (
                            local pvj = polyop.getVert nd.baseObject vj
                            if (distance pvi pvj) < 0.001 do dupVerts += 1
                        )
                    )
                )
                for ei = 1 to nEdges do (
                    local ev = polyop.getEdgeVerts nd.baseObject ei
                    local p1 = polyop.getVert nd.baseObject ev[1]
                    local p2 = polyop.getVert nd.baseObject ev[2]
                    local ef = polyop.getEdgeFaces nd.baseObject ei
                    if ef.count > 2 do tJunctions += 1
                    if (abs (p1.x - p2.x) < 0.01) and (abs (p1.y - p2.y) < 0.01) and (abs (p1.z - p2.z) > 0.01) do (
                        local isSeam = true
                        if guideKnots.count >= 3 do (
                            isSeam = false
                            for ki = 1 to guideKnots.count do (
                                local kp = guideKnots[ki]
                                if (distance [p1.x, p1.y, 0] [kp.x, kp.y, 0]) < 0.01 do (
                                    local prevK = if ki == 1 then guideKnots[guideKnots.count] else guideKnots[ki-1]
                                    local nextK = if ki == guideKnots.count then guideKnots[1] else guideKnots[ki+1]
                                    local vPrev = normalize ([kp.x - prevK.x, kp.y - prevK.y, 0])
                                    local vNext = normalize ([nextK.x - kp.x, nextK.y - kp.y, 0])
                                    if (abs (dot vPrev vNext)) < 0.999 do isSeam = true
                                )
                            )
                        )
                        if isSeam do (
                            if ef.count != 2 do seamValenceErr += 1
                        )
                    )
                )
            )
        ) catch ()
        local evalVol = 0.0d0
        local openEdges = 0
        local tmpMesh = undefined
        try (
            in coordsys world (tmpMesh = snapshotAsMesh nd)
            if tmpMesh != undefined do (
                local nf = tmpMesh.numFaces
                if nf > 0 do (
                    local v1 = getVert tmpMesh 1
                    for f = 1 to nf do (
                        local f3 = getFace tmpMesh f
                        local a = getVert tmpMesh (f3.x as integer)
                        local b_v = getVert tmpMesh (f3.y as integer)
                        local c = getVert tmpMesh (f3.z as integer)
                        local ax = (a.x as double) - (v1.x as double)
                        local ay = (a.y as double) - (v1.y as double)
                        local az = (a.z as double) - (v1.z as double)
                        local bx = (b_v.x as double) - (v1.x as double)
                        local b_y = (b_v.y as double) - (v1.y as double)
                        local bz = (b_v.z as double) - (v1.z as double)
                        local cx = (c.x as double) - (v1.x as double)
                        local cy = (c.y as double) - (v1.y as double)
                        local cz = (c.z as double) - (v1.z as double)
                        evalVol += (ax * (b_y * cz - bz * cy) + ay * (bz * cx - bx * cz) + az * (bx * cy - b_y * cx)) / 6.0
                    )
                    try ( openEdges = (meshop.getOpenEdges tmpMesh).numberSet ) catch ()
                )
                delete tmpMesh; tmpMesh = undefined
            )
        ) catch ( if tmpMesh != undefined do try ( delete tmpMesh ) catch () )
        format "ROW observation_id=% check_id=% target_id=% sample_id=% status=OK exists=true isHidden=% pos=[%,%,%] min=[%,%,%] max=[%,%,%] modCount=% baseCls=% mod1Cls=% innerAmt=% outerAmt=% segs=% straightenCorners=% nVerts=% nEdges=% dupVerts=% seamValenceErr=% tJunctions=% openEdges=% maxYDev=% vol=% signedVol=%\n" \
            "O582f7ca5d0d26e45416a8bb39c586d05e99d60112dc4bbccbd7a72879f717a4" "CHK_TOPOLOGY" "WS_storey_1" "S158b65594b1eb55a2fdec2ac65e0c92971ce1dcb3870fcdf873c18f97951f7a" isHidden (p.x as string) (p.y as string) (p.z as string) \
            (bMin.x as string) (bMin.y as string) (bMin.z as string) (bMax.x as string) (bMax.y as string) (bMax.z as string) \
            (modCount as string) baseCls mod1Cls (innerAmt as string) (outerAmt as string) (segs as string) (straightenCorners as string) (nVerts as string) (nEdges as string) (dupVerts as string) (seamValenceErr as string) (tJunctions as string) (openEdges as string) (maxYDev as string) ((abs evalVol) as string) (evalVol as string) to:__qa_out
    ) else (
        format "ROW observation_id=% check_id=% target_id=% sample_id=% status=NOT_FOUND exists=false\n" \
            "O582f7ca5d0d26e45416a8bb39c586d05e99d60112dc4bbccbd7a72879f717a4" "CHK_TOPOLOGY" "WS_storey_1" "S158b65594b1eb55a2fdec2ac65e0c92971ce1dcb3870fcdf873c18f97951f7a" to:__qa_out
    )
    -- Observation O965c6da7e95d493177c52848790d6e09e0ec0e9198d1dd5336a0a28e93c5de7 (CHK_SURFACE)
    local nd = getNodeByName "WS_storey_1"
    if nd != undefined then (
        local p = nd.pos
        local bMin = nd.min
        local bMax = nd.max
        local modCount = nd.modifiers.count
        local isHidden = (nd.isHidden as string)
        local baseCls = if isProperty nd #baseObject and nd.baseObject != undefined then (classOf nd.baseObject as string) else (classOf nd as string)
        local mod1Cls = if modCount > 0 then (classOf nd.modifiers[1] as string) else "none"
        local innerAmt = 0.0d0; local outerAmt = 0.0d0; local segs = 0
        local straightenCorners = false
        if modCount > 0 and (classOf nd.modifiers[1]) == Shell do (
            local sm = nd.modifiers[1]
            try ( innerAmt = sm.innerAmount as double ) catch ()
            try ( outerAmt = sm.outerAmount as double ) catch ()
            try ( segs = sm.segments as integer ) catch ()
            try ( straightenCorners = sm.straightenCorners as booleanClass ) catch ()
        )
        local guideNd = getNodeByName (nd.name + "_InnerSpline")
        local guideKnots = #()
        if guideNd != undefined and (classOf guideNd) == SplineShape do (
            local nK = numKnots guideNd 1
            guideKnots = for k = 1 to nK collect (getKnotPoint guideNd 1 k)
        )
        local maxYDev = 0.0d0
        local nVerts = 0; local nEdges = 0; local dupVerts = 0; local seamValenceErr = 0; local tJunctions = 0
        try (
            if (classOf nd.baseObject) == Editable_Poly do (
                nVerts = polyop.getNumVerts nd.baseObject
                nEdges = polyop.getNumEdges nd.baseObject
                for vi = 1 to nVerts do (
                    local vp = polyop.getVert nd.baseObject vi
                    local dev = 0.0d0
                    if guideKnots.count > 0 then (
                        local minD = 1e9
                        local p2d = [vp.x, vp.y, 0]
                        for kp in guideKnots do (
                            local d = distance p2d [kp.x, kp.y, 0]
                            if d < minD do minD = d
                        )
                        dev = minD
                    ) else (
                        dev = abs (vp.y as double)
                    )
                    if dev > maxYDev do maxYDev = dev
                )
                if nVerts <= 1000 do (
                    for vi = 1 to (nVerts - 1) do (
                        local pvi = polyop.getVert nd.baseObject vi
                        for vj = (vi + 1) to nVerts do (
                            local pvj = polyop.getVert nd.baseObject vj
                            if (distance pvi pvj) < 0.001 do dupVerts += 1
                        )
                    )
                )
                for ei = 1 to nEdges do (
                    local ev = polyop.getEdgeVerts nd.baseObject ei
                    local p1 = polyop.getVert nd.baseObject ev[1]
                    local p2 = polyop.getVert nd.baseObject ev[2]
                    local ef = polyop.getEdgeFaces nd.baseObject ei
                    if ef.count > 2 do tJunctions += 1
                    if (abs (p1.x - p2.x) < 0.01) and (abs (p1.y - p2.y) < 0.01) and (abs (p1.z - p2.z) > 0.01) do (
                        local isSeam = true
                        if guideKnots.count >= 3 do (
                            isSeam = false
                            for ki = 1 to guideKnots.count do (
                                local kp = guideKnots[ki]
                                if (distance [p1.x, p1.y, 0] [kp.x, kp.y, 0]) < 0.01 do (
                                    local prevK = if ki == 1 then guideKnots[guideKnots.count] else guideKnots[ki-1]
                                    local nextK = if ki == guideKnots.count then guideKnots[1] else guideKnots[ki+1]
                                    local vPrev = normalize ([kp.x - prevK.x, kp.y - prevK.y, 0])
                                    local vNext = normalize ([nextK.x - kp.x, nextK.y - kp.y, 0])
                                    if (abs (dot vPrev vNext)) < 0.999 do isSeam = true
                                )
                            )
                        )
                        if isSeam do (
                            if ef.count != 2 do seamValenceErr += 1
                        )
                    )
                )
            )
        ) catch ()
        local evalVol = 0.0d0
        local openEdges = 0
        local tmpMesh = undefined
        try (
            in coordsys world (tmpMesh = snapshotAsMesh nd)
            if tmpMesh != undefined do (
                local nf = tmpMesh.numFaces
                if nf > 0 do (
                    local v1 = getVert tmpMesh 1
                    for f = 1 to nf do (
                        local f3 = getFace tmpMesh f
                        local a = getVert tmpMesh (f3.x as integer)
                        local b_v = getVert tmpMesh (f3.y as integer)
                        local c = getVert tmpMesh (f3.z as integer)
                        local ax = (a.x as double) - (v1.x as double)
                        local ay = (a.y as double) - (v1.y as double)
                        local az = (a.z as double) - (v1.z as double)
                        local bx = (b_v.x as double) - (v1.x as double)
                        local b_y = (b_v.y as double) - (v1.y as double)
                        local bz = (b_v.z as double) - (v1.z as double)
                        local cx = (c.x as double) - (v1.x as double)
                        local cy = (c.y as double) - (v1.y as double)
                        local cz = (c.z as double) - (v1.z as double)
                        evalVol += (ax * (b_y * cz - bz * cy) + ay * (bz * cx - bx * cz) + az * (bx * cy - b_y * cx)) / 6.0
                    )
                    try ( openEdges = (meshop.getOpenEdges tmpMesh).numberSet ) catch ()
                )
                delete tmpMesh; tmpMesh = undefined
            )
        ) catch ( if tmpMesh != undefined do try ( delete tmpMesh ) catch () )
        format "ROW observation_id=% check_id=% target_id=% sample_id=% status=OK exists=true isHidden=% pos=[%,%,%] min=[%,%,%] max=[%,%,%] modCount=% baseCls=% mod1Cls=% innerAmt=% outerAmt=% segs=% straightenCorners=% nVerts=% nEdges=% dupVerts=% seamValenceErr=% tJunctions=% openEdges=% maxYDev=% vol=% signedVol=%\n" \
            "O965c6da7e95d493177c52848790d6e09e0ec0e9198d1dd5336a0a28e93c5de7" "CHK_SURFACE" "WS_storey_1" "S695aae7c83731cfe2741253686be339d7ab06aae51c15ba5fb00c710c5da17c" isHidden (p.x as string) (p.y as string) (p.z as string) \
            (bMin.x as string) (bMin.y as string) (bMin.z as string) (bMax.x as string) (bMax.y as string) (bMax.z as string) \
            (modCount as string) baseCls mod1Cls (innerAmt as string) (outerAmt as string) (segs as string) (straightenCorners as string) (nVerts as string) (nEdges as string) (dupVerts as string) (seamValenceErr as string) (tJunctions as string) (openEdges as string) (maxYDev as string) ((abs evalVol) as string) (evalVol as string) to:__qa_out
    ) else (
        format "ROW observation_id=% check_id=% target_id=% sample_id=% status=NOT_FOUND exists=false\n" \
            "O965c6da7e95d493177c52848790d6e09e0ec0e9198d1dd5336a0a28e93c5de7" "CHK_SURFACE" "WS_storey_1" "S695aae7c83731cfe2741253686be339d7ab06aae51c15ba5fb00c710c5da17c" to:__qa_out
    )
    -- Observation O792151e50b3b2006a56db3afd47a5912347fef48dfb749aec4ae9cb2ba901c4 (CHK_APERTURE_01)
    local nd = getNodeByName "PLC_001"
    if nd != undefined then (
        local p = nd.pos
        local bMin = nd.min
        local bMax = nd.max
        local modCount = nd.modifiers.count
        local isHidden = (nd.isHidden as string)
        local baseCls = if isProperty nd #baseObject and nd.baseObject != undefined then (classOf nd.baseObject as string) else (classOf nd as string)
        local mod1Cls = if modCount > 0 then (classOf nd.modifiers[1] as string) else "none"
        local innerAmt = 0.0d0; local outerAmt = 0.0d0; local segs = 0
        local straightenCorners = false
        if modCount > 0 and (classOf nd.modifiers[1]) == Shell do (
            local sm = nd.modifiers[1]
            try ( innerAmt = sm.innerAmount as double ) catch ()
            try ( outerAmt = sm.outerAmount as double ) catch ()
            try ( segs = sm.segments as integer ) catch ()
            try ( straightenCorners = sm.straightenCorners as booleanClass ) catch ()
        )
        local guideNd = getNodeByName (nd.name + "_InnerSpline")
        local guideKnots = #()
        if guideNd != undefined and (classOf guideNd) == SplineShape do (
            local nK = numKnots guideNd 1
            guideKnots = for k = 1 to nK collect (getKnotPoint guideNd 1 k)
        )
        local maxYDev = 0.0d0
        local nVerts = 0; local nEdges = 0; local dupVerts = 0; local seamValenceErr = 0; local tJunctions = 0
        try (
            if (classOf nd.baseObject) == Editable_Poly do (
                nVerts = polyop.getNumVerts nd.baseObject
                nEdges = polyop.getNumEdges nd.baseObject
                for vi = 1 to nVerts do (
                    local vp = polyop.getVert nd.baseObject vi
                    local dev = 0.0d0
                    if guideKnots.count > 0 then (
                        local minD = 1e9
                        local p2d = [vp.x, vp.y, 0]
                        for kp in guideKnots do (
                            local d = distance p2d [kp.x, kp.y, 0]
                            if d < minD do minD = d
                        )
                        dev = minD
                    ) else (
                        dev = abs (vp.y as double)
                    )
                    if dev > maxYDev do maxYDev = dev
                )
                if nVerts <= 1000 do (
                    for vi = 1 to (nVerts - 1) do (
                        local pvi = polyop.getVert nd.baseObject vi
                        for vj = (vi + 1) to nVerts do (
                            local pvj = polyop.getVert nd.baseObject vj
                            if (distance pvi pvj) < 0.001 do dupVerts += 1
                        )
                    )
                )
                for ei = 1 to nEdges do (
                    local ev = polyop.getEdgeVerts nd.baseObject ei
                    local p1 = polyop.getVert nd.baseObject ev[1]
                    local p2 = polyop.getVert nd.baseObject ev[2]
                    local ef = polyop.getEdgeFaces nd.baseObject ei
                    if ef.count > 2 do tJunctions += 1
                    if (abs (p1.x - p2.x) < 0.01) and (abs (p1.y - p2.y) < 0.01) and (abs (p1.z - p2.z) > 0.01) do (
                        local isSeam = true
                        if guideKnots.count >= 3 do (
                            isSeam = false
                            for ki = 1 to guideKnots.count do (
                                local kp = guideKnots[ki]
                                if (distance [p1.x, p1.y, 0] [kp.x, kp.y, 0]) < 0.01 do (
                                    local prevK = if ki == 1 then guideKnots[guideKnots.count] else guideKnots[ki-1]
                                    local nextK = if ki == guideKnots.count then guideKnots[1] else guideKnots[ki+1]
                                    local vPrev = normalize ([kp.x - prevK.x, kp.y - prevK.y, 0])
                                    local vNext = normalize ([nextK.x - kp.x, nextK.y - kp.y, 0])
                                    if (abs (dot vPrev vNext)) < 0.999 do isSeam = true
                                )
                            )
                        )
                        if isSeam do (
                            if ef.count != 2 do seamValenceErr += 1
                        )
                    )
                )
            )
        ) catch ()
        local evalVol = 0.0d0
        local openEdges = 0
        local tmpMesh = undefined
        try (
            in coordsys world (tmpMesh = snapshotAsMesh nd)
            if tmpMesh != undefined do (
                local nf = tmpMesh.numFaces
                if nf > 0 do (
                    local v1 = getVert tmpMesh 1
                    for f = 1 to nf do (
                        local f3 = getFace tmpMesh f
                        local a = getVert tmpMesh (f3.x as integer)
                        local b_v = getVert tmpMesh (f3.y as integer)
                        local c = getVert tmpMesh (f3.z as integer)
                        local ax = (a.x as double) - (v1.x as double)
                        local ay = (a.y as double) - (v1.y as double)
                        local az = (a.z as double) - (v1.z as double)
                        local bx = (b_v.x as double) - (v1.x as double)
                        local b_y = (b_v.y as double) - (v1.y as double)
                        local bz = (b_v.z as double) - (v1.z as double)
                        local cx = (c.x as double) - (v1.x as double)
                        local cy = (c.y as double) - (v1.y as double)
                        local cz = (c.z as double) - (v1.z as double)
                        evalVol += (ax * (b_y * cz - bz * cy) + ay * (bz * cx - bx * cz) + az * (bx * cy - b_y * cx)) / 6.0
                    )
                    try ( openEdges = (meshop.getOpenEdges tmpMesh).numberSet ) catch ()
                )
                delete tmpMesh; tmpMesh = undefined
            )
        ) catch ( if tmpMesh != undefined do try ( delete tmpMesh ) catch () )
        format "ROW observation_id=% check_id=% target_id=% sample_id=% status=OK exists=true isHidden=% pos=[%,%,%] min=[%,%,%] max=[%,%,%] modCount=% baseCls=% mod1Cls=% innerAmt=% outerAmt=% segs=% straightenCorners=% nVerts=% nEdges=% dupVerts=% seamValenceErr=% tJunctions=% openEdges=% maxYDev=% vol=% signedVol=%\n" \
            "O792151e50b3b2006a56db3afd47a5912347fef48dfb749aec4ae9cb2ba901c4" "CHK_APERTURE_01" "PLC_001" "Saa12beec3285285e5111900e94ba5c3eba65428551b7e475d366459e834cf94" isHidden (p.x as string) (p.y as string) (p.z as string) \
            (bMin.x as string) (bMin.y as string) (bMin.z as string) (bMax.x as string) (bMax.y as string) (bMax.z as string) \
            (modCount as string) baseCls mod1Cls (innerAmt as string) (outerAmt as string) (segs as string) (straightenCorners as string) (nVerts as string) (nEdges as string) (dupVerts as string) (seamValenceErr as string) (tJunctions as string) (openEdges as string) (maxYDev as string) ((abs evalVol) as string) (evalVol as string) to:__qa_out
    ) else (
        format "ROW observation_id=% check_id=% target_id=% sample_id=% status=NOT_FOUND exists=false\n" \
            "O792151e50b3b2006a56db3afd47a5912347fef48dfb749aec4ae9cb2ba901c4" "CHK_APERTURE_01" "PLC_001" "Saa12beec3285285e5111900e94ba5c3eba65428551b7e475d366459e834cf94" to:__qa_out
    )
    -- Observation O10b1bb8508a7ba291ad32d371ecbb907eb3952bb51de0fcc7867d976f0e4fdd (CHK_APERTURE_02)
    local nd = getNodeByName "PLC_002"
    if nd != undefined then (
        local p = nd.pos
        local bMin = nd.min
        local bMax = nd.max
        local modCount = nd.modifiers.count
        local isHidden = (nd.isHidden as string)
        local baseCls = if isProperty nd #baseObject and nd.baseObject != undefined then (classOf nd.baseObject as string) else (classOf nd as string)
        local mod1Cls = if modCount > 0 then (classOf nd.modifiers[1] as string) else "none"
        local innerAmt = 0.0d0; local outerAmt = 0.0d0; local segs = 0
        local straightenCorners = false
        if modCount > 0 and (classOf nd.modifiers[1]) == Shell do (
            local sm = nd.modifiers[1]
            try ( innerAmt = sm.innerAmount as double ) catch ()
            try ( outerAmt = sm.outerAmount as double ) catch ()
            try ( segs = sm.segments as integer ) catch ()
            try ( straightenCorners = sm.straightenCorners as booleanClass ) catch ()
        )
        local guideNd = getNodeByName (nd.name + "_InnerSpline")
        local guideKnots = #()
        if guideNd != undefined and (classOf guideNd) == SplineShape do (
            local nK = numKnots guideNd 1
            guideKnots = for k = 1 to nK collect (getKnotPoint guideNd 1 k)
        )
        local maxYDev = 0.0d0
        local nVerts = 0; local nEdges = 0; local dupVerts = 0; local seamValenceErr = 0; local tJunctions = 0
        try (
            if (classOf nd.baseObject) == Editable_Poly do (
                nVerts = polyop.getNumVerts nd.baseObject
                nEdges = polyop.getNumEdges nd.baseObject
                for vi = 1 to nVerts do (
                    local vp = polyop.getVert nd.baseObject vi
                    local dev = 0.0d0
                    if guideKnots.count > 0 then (
                        local minD = 1e9
                        local p2d = [vp.x, vp.y, 0]
                        for kp in guideKnots do (
                            local d = distance p2d [kp.x, kp.y, 0]
                            if d < minD do minD = d
                        )
                        dev = minD
                    ) else (
                        dev = abs (vp.y as double)
                    )
                    if dev > maxYDev do maxYDev = dev
                )
                if nVerts <= 1000 do (
                    for vi = 1 to (nVerts - 1) do (
                        local pvi = polyop.getVert nd.baseObject vi
                        for vj = (vi + 1) to nVerts do (
                            local pvj = polyop.getVert nd.baseObject vj
                            if (distance pvi pvj) < 0.001 do dupVerts += 1
                        )
                    )
                )
                for ei = 1 to nEdges do (
                    local ev = polyop.getEdgeVerts nd.baseObject ei
                    local p1 = polyop.getVert nd.baseObject ev[1]
                    local p2 = polyop.getVert nd.baseObject ev[2]
                    local ef = polyop.getEdgeFaces nd.baseObject ei
                    if ef.count > 2 do tJunctions += 1
                    if (abs (p1.x - p2.x) < 0.01) and (abs (p1.y - p2.y) < 0.01) and (abs (p1.z - p2.z) > 0.01) do (
                        local isSeam = true
                        if guideKnots.count >= 3 do (
                            isSeam = false
                            for ki = 1 to guideKnots.count do (
                                local kp = guideKnots[ki]
                                if (distance [p1.x, p1.y, 0] [kp.x, kp.y, 0]) < 0.01 do (
                                    local prevK = if ki == 1 then guideKnots[guideKnots.count] else guideKnots[ki-1]
                                    local nextK = if ki == guideKnots.count then guideKnots[1] else guideKnots[ki+1]
                                    local vPrev = normalize ([kp.x - prevK.x, kp.y - prevK.y, 0])
                                    local vNext = normalize ([nextK.x - kp.x, nextK.y - kp.y, 0])
                                    if (abs (dot vPrev vNext)) < 0.999 do isSeam = true
                                )
                            )
                        )
                        if isSeam do (
                            if ef.count != 2 do seamValenceErr += 1
                        )
                    )
                )
            )
        ) catch ()
        local evalVol = 0.0d0
        local openEdges = 0
        local tmpMesh = undefined
        try (
            in coordsys world (tmpMesh = snapshotAsMesh nd)
            if tmpMesh != undefined do (
                local nf = tmpMesh.numFaces
                if nf > 0 do (
                    local v1 = getVert tmpMesh 1
                    for f = 1 to nf do (
                        local f3 = getFace tmpMesh f
                        local a = getVert tmpMesh (f3.x as integer)
                        local b_v = getVert tmpMesh (f3.y as integer)
                        local c = getVert tmpMesh (f3.z as integer)
                        local ax = (a.x as double) - (v1.x as double)
                        local ay = (a.y as double) - (v1.y as double)
                        local az = (a.z as double) - (v1.z as double)
                        local bx = (b_v.x as double) - (v1.x as double)
                        local b_y = (b_v.y as double) - (v1.y as double)
                        local bz = (b_v.z as double) - (v1.z as double)
                        local cx = (c.x as double) - (v1.x as double)
                        local cy = (c.y as double) - (v1.y as double)
                        local cz = (c.z as double) - (v1.z as double)
                        evalVol += (ax * (b_y * cz - bz * cy) + ay * (bz * cx - bx * cz) + az * (bx * cy - b_y * cx)) / 6.0
                    )
                    try ( openEdges = (meshop.getOpenEdges tmpMesh).numberSet ) catch ()
                )
                delete tmpMesh; tmpMesh = undefined
            )
        ) catch ( if tmpMesh != undefined do try ( delete tmpMesh ) catch () )
        format "ROW observation_id=% check_id=% target_id=% sample_id=% status=OK exists=true isHidden=% pos=[%,%,%] min=[%,%,%] max=[%,%,%] modCount=% baseCls=% mod1Cls=% innerAmt=% outerAmt=% segs=% straightenCorners=% nVerts=% nEdges=% dupVerts=% seamValenceErr=% tJunctions=% openEdges=% maxYDev=% vol=% signedVol=%\n" \
            "O10b1bb8508a7ba291ad32d371ecbb907eb3952bb51de0fcc7867d976f0e4fdd" "CHK_APERTURE_02" "PLC_002" "S2428b1df7e9a1aeabeb37c04ac81188b31e8441de12aaacef2fc103f42007a3" isHidden (p.x as string) (p.y as string) (p.z as string) \
            (bMin.x as string) (bMin.y as string) (bMin.z as string) (bMax.x as string) (bMax.y as string) (bMax.z as string) \
            (modCount as string) baseCls mod1Cls (innerAmt as string) (outerAmt as string) (segs as string) (straightenCorners as string) (nVerts as string) (nEdges as string) (dupVerts as string) (seamValenceErr as string) (tJunctions as string) (openEdges as string) (maxYDev as string) ((abs evalVol) as string) (evalVol as string) to:__qa_out
    ) else (
        format "ROW observation_id=% check_id=% target_id=% sample_id=% status=NOT_FOUND exists=false\n" \
            "O10b1bb8508a7ba291ad32d371ecbb907eb3952bb51de0fcc7867d976f0e4fdd" "CHK_APERTURE_02" "PLC_002" "S2428b1df7e9a1aeabeb37c04ac81188b31e8441de12aaacef2fc103f42007a3" to:__qa_out
    )
    -- Observation Od26ef76f52982b8879d597101a3475224629ca6829baa1e648ea8a6059bf640 (CHK_APERTURE_03)
    local nd = getNodeByName "PLC_003"
    if nd != undefined then (
        local p = nd.pos
        local bMin = nd.min
        local bMax = nd.max
        local modCount = nd.modifiers.count
        local isHidden = (nd.isHidden as string)
        local baseCls = if isProperty nd #baseObject and nd.baseObject != undefined then (classOf nd.baseObject as string) else (classOf nd as string)
        local mod1Cls = if modCount > 0 then (classOf nd.modifiers[1] as string) else "none"
        local innerAmt = 0.0d0; local outerAmt = 0.0d0; local segs = 0
        local straightenCorners = false
        if modCount > 0 and (classOf nd.modifiers[1]) == Shell do (
            local sm = nd.modifiers[1]
            try ( innerAmt = sm.innerAmount as double ) catch ()
            try ( outerAmt = sm.outerAmount as double ) catch ()
            try ( segs = sm.segments as integer ) catch ()
            try ( straightenCorners = sm.straightenCorners as booleanClass ) catch ()
        )
        local guideNd = getNodeByName (nd.name + "_InnerSpline")
        local guideKnots = #()
        if guideNd != undefined and (classOf guideNd) == SplineShape do (
            local nK = numKnots guideNd 1
            guideKnots = for k = 1 to nK collect (getKnotPoint guideNd 1 k)
        )
        local maxYDev = 0.0d0
        local nVerts = 0; local nEdges = 0; local dupVerts = 0; local seamValenceErr = 0; local tJunctions = 0
        try (
            if (classOf nd.baseObject) == Editable_Poly do (
                nVerts = polyop.getNumVerts nd.baseObject
                nEdges = polyop.getNumEdges nd.baseObject
                for vi = 1 to nVerts do (
                    local vp = polyop.getVert nd.baseObject vi
                    local dev = 0.0d0
                    if guideKnots.count > 0 then (
                        local minD = 1e9
                        local p2d = [vp.x, vp.y, 0]
                        for kp in guideKnots do (
                            local d = distance p2d [kp.x, kp.y, 0]
                            if d < minD do minD = d
                        )
                        dev = minD
                    ) else (
                        dev = abs (vp.y as double)
                    )
                    if dev > maxYDev do maxYDev = dev
                )
                if nVerts <= 1000 do (
                    for vi = 1 to (nVerts - 1) do (
                        local pvi = polyop.getVert nd.baseObject vi
                        for vj = (vi + 1) to nVerts do (
                            local pvj = polyop.getVert nd.baseObject vj
                            if (distance pvi pvj) < 0.001 do dupVerts += 1
                        )
                    )
                )
                for ei = 1 to nEdges do (
                    local ev = polyop.getEdgeVerts nd.baseObject ei
                    local p1 = polyop.getVert nd.baseObject ev[1]
                    local p2 = polyop.getVert nd.baseObject ev[2]
                    local ef = polyop.getEdgeFaces nd.baseObject ei
                    if ef.count > 2 do tJunctions += 1
                    if (abs (p1.x - p2.x) < 0.01) and (abs (p1.y - p2.y) < 0.01) and (abs (p1.z - p2.z) > 0.01) do (
                        local isSeam = true
                        if guideKnots.count >= 3 do (
                            isSeam = false
                            for ki = 1 to guideKnots.count do (
                                local kp = guideKnots[ki]
                                if (distance [p1.x, p1.y, 0] [kp.x, kp.y, 0]) < 0.01 do (
                                    local prevK = if ki == 1 then guideKnots[guideKnots.count] else guideKnots[ki-1]
                                    local nextK = if ki == guideKnots.count then guideKnots[1] else guideKnots[ki+1]
                                    local vPrev = normalize ([kp.x - prevK.x, kp.y - prevK.y, 0])
                                    local vNext = normalize ([nextK.x - kp.x, nextK.y - kp.y, 0])
                                    if (abs (dot vPrev vNext)) < 0.999 do isSeam = true
                                )
                            )
                        )
                        if isSeam do (
                            if ef.count != 2 do seamValenceErr += 1
                        )
                    )
                )
            )
        ) catch ()
        local evalVol = 0.0d0
        local openEdges = 0
        local tmpMesh = undefined
        try (
            in coordsys world (tmpMesh = snapshotAsMesh nd)
            if tmpMesh != undefined do (
                local nf = tmpMesh.numFaces
                if nf > 0 do (
                    local v1 = getVert tmpMesh 1
                    for f = 1 to nf do (
                        local f3 = getFace tmpMesh f
                        local a = getVert tmpMesh (f3.x as integer)
                        local b_v = getVert tmpMesh (f3.y as integer)
                        local c = getVert tmpMesh (f3.z as integer)
                        local ax = (a.x as double) - (v1.x as double)
                        local ay = (a.y as double) - (v1.y as double)
                        local az = (a.z as double) - (v1.z as double)
                        local bx = (b_v.x as double) - (v1.x as double)
                        local b_y = (b_v.y as double) - (v1.y as double)
                        local bz = (b_v.z as double) - (v1.z as double)
                        local cx = (c.x as double) - (v1.x as double)
                        local cy = (c.y as double) - (v1.y as double)
                        local cz = (c.z as double) - (v1.z as double)
                        evalVol += (ax * (b_y * cz - bz * cy) + ay * (bz * cx - bx * cz) + az * (bx * cy - b_y * cx)) / 6.0
                    )
                    try ( openEdges = (meshop.getOpenEdges tmpMesh).numberSet ) catch ()
                )
                delete tmpMesh; tmpMesh = undefined
            )
        ) catch ( if tmpMesh != undefined do try ( delete tmpMesh ) catch () )
        format "ROW observation_id=% check_id=% target_id=% sample_id=% status=OK exists=true isHidden=% pos=[%,%,%] min=[%,%,%] max=[%,%,%] modCount=% baseCls=% mod1Cls=% innerAmt=% outerAmt=% segs=% straightenCorners=% nVerts=% nEdges=% dupVerts=% seamValenceErr=% tJunctions=% openEdges=% maxYDev=% vol=% signedVol=%\n" \
            "Od26ef76f52982b8879d597101a3475224629ca6829baa1e648ea8a6059bf640" "CHK_APERTURE_03" "PLC_003" "Sb729969f43a2db1eb2c61cb1672f91cd827da3632683e6cc9b9f704fcddf26f" isHidden (p.x as string) (p.y as string) (p.z as string) \
            (bMin.x as string) (bMin.y as string) (bMin.z as string) (bMax.x as string) (bMax.y as string) (bMax.z as string) \
            (modCount as string) baseCls mod1Cls (innerAmt as string) (outerAmt as string) (segs as string) (straightenCorners as string) (nVerts as string) (nEdges as string) (dupVerts as string) (seamValenceErr as string) (tJunctions as string) (openEdges as string) (maxYDev as string) ((abs evalVol) as string) (evalVol as string) to:__qa_out
    ) else (
        format "ROW observation_id=% check_id=% target_id=% sample_id=% status=NOT_FOUND exists=false\n" \
            "Od26ef76f52982b8879d597101a3475224629ca6829baa1e648ea8a6059bf640" "CHK_APERTURE_03" "PLC_003" "Sb729969f43a2db1eb2c61cb1672f91cd827da3632683e6cc9b9f704fcddf26f" to:__qa_out
    )
    -- Observation O94fc22d10018d2660b2229a63443a89ea826084220c6c9f22e1fe4aa7acdaaa (CHK_PLACEMENT_01)
    local nd = getNodeByName "PLC_001"
    if nd != undefined then (
        local p = nd.pos
        local bMin = nd.min
        local bMax = nd.max
        local modCount = nd.modifiers.count
        local isHidden = (nd.isHidden as string)
        local baseCls = if isProperty nd #baseObject and nd.baseObject != undefined then (classOf nd.baseObject as string) else (classOf nd as string)
        local mod1Cls = if modCount > 0 then (classOf nd.modifiers[1] as string) else "none"
        local innerAmt = 0.0d0; local outerAmt = 0.0d0; local segs = 0
        local straightenCorners = false
        if modCount > 0 and (classOf nd.modifiers[1]) == Shell do (
            local sm = nd.modifiers[1]
            try ( innerAmt = sm.innerAmount as double ) catch ()
            try ( outerAmt = sm.outerAmount as double ) catch ()
            try ( segs = sm.segments as integer ) catch ()
            try ( straightenCorners = sm.straightenCorners as booleanClass ) catch ()
        )
        local guideNd = getNodeByName (nd.name + "_InnerSpline")
        local guideKnots = #()
        if guideNd != undefined and (classOf guideNd) == SplineShape do (
            local nK = numKnots guideNd 1
            guideKnots = for k = 1 to nK collect (getKnotPoint guideNd 1 k)
        )
        local maxYDev = 0.0d0
        local nVerts = 0; local nEdges = 0; local dupVerts = 0; local seamValenceErr = 0; local tJunctions = 0
        try (
            if (classOf nd.baseObject) == Editable_Poly do (
                nVerts = polyop.getNumVerts nd.baseObject
                nEdges = polyop.getNumEdges nd.baseObject
                for vi = 1 to nVerts do (
                    local vp = polyop.getVert nd.baseObject vi
                    local dev = 0.0d0
                    if guideKnots.count > 0 then (
                        local minD = 1e9
                        local p2d = [vp.x, vp.y, 0]
                        for kp in guideKnots do (
                            local d = distance p2d [kp.x, kp.y, 0]
                            if d < minD do minD = d
                        )
                        dev = minD
                    ) else (
                        dev = abs (vp.y as double)
                    )
                    if dev > maxYDev do maxYDev = dev
                )
                if nVerts <= 1000 do (
                    for vi = 1 to (nVerts - 1) do (
                        local pvi = polyop.getVert nd.baseObject vi
                        for vj = (vi + 1) to nVerts do (
                            local pvj = polyop.getVert nd.baseObject vj
                            if (distance pvi pvj) < 0.001 do dupVerts += 1
                        )
                    )
                )
                for ei = 1 to nEdges do (
                    local ev = polyop.getEdgeVerts nd.baseObject ei
                    local p1 = polyop.getVert nd.baseObject ev[1]
                    local p2 = polyop.getVert nd.baseObject ev[2]
                    local ef = polyop.getEdgeFaces nd.baseObject ei
                    if ef.count > 2 do tJunctions += 1
                    if (abs (p1.x - p2.x) < 0.01) and (abs (p1.y - p2.y) < 0.01) and (abs (p1.z - p2.z) > 0.01) do (
                        local isSeam = true
                        if guideKnots.count >= 3 do (
                            isSeam = false
                            for ki = 1 to guideKnots.count do (
                                local kp = guideKnots[ki]
                                if (distance [p1.x, p1.y, 0] [kp.x, kp.y, 0]) < 0.01 do (
                                    local prevK = if ki == 1 then guideKnots[guideKnots.count] else guideKnots[ki-1]
                                    local nextK = if ki == guideKnots.count then guideKnots[1] else guideKnots[ki+1]
                                    local vPrev = normalize ([kp.x - prevK.x, kp.y - prevK.y, 0])
                                    local vNext = normalize ([nextK.x - kp.x, nextK.y - kp.y, 0])
                                    if (abs (dot vPrev vNext)) < 0.999 do isSeam = true
                                )
                            )
                        )
                        if isSeam do (
                            if ef.count != 2 do seamValenceErr += 1
                        )
                    )
                )
            )
        ) catch ()
        local evalVol = 0.0d0
        local openEdges = 0
        local tmpMesh = undefined
        try (
            in coordsys world (tmpMesh = snapshotAsMesh nd)
            if tmpMesh != undefined do (
                local nf = tmpMesh.numFaces
                if nf > 0 do (
                    local v1 = getVert tmpMesh 1
                    for f = 1 to nf do (
                        local f3 = getFace tmpMesh f
                        local a = getVert tmpMesh (f3.x as integer)
                        local b_v = getVert tmpMesh (f3.y as integer)
                        local c = getVert tmpMesh (f3.z as integer)
                        local ax = (a.x as double) - (v1.x as double)
                        local ay = (a.y as double) - (v1.y as double)
                        local az = (a.z as double) - (v1.z as double)
                        local bx = (b_v.x as double) - (v1.x as double)
                        local b_y = (b_v.y as double) - (v1.y as double)
                        local bz = (b_v.z as double) - (v1.z as double)
                        local cx = (c.x as double) - (v1.x as double)
                        local cy = (c.y as double) - (v1.y as double)
                        local cz = (c.z as double) - (v1.z as double)
                        evalVol += (ax * (b_y * cz - bz * cy) + ay * (bz * cx - bx * cz) + az * (bx * cy - b_y * cx)) / 6.0
                    )
                    try ( openEdges = (meshop.getOpenEdges tmpMesh).numberSet ) catch ()
                )
                delete tmpMesh; tmpMesh = undefined
            )
        ) catch ( if tmpMesh != undefined do try ( delete tmpMesh ) catch () )
        format "ROW observation_id=% check_id=% target_id=% sample_id=% status=OK exists=true isHidden=% pos=[%,%,%] min=[%,%,%] max=[%,%,%] modCount=% baseCls=% mod1Cls=% innerAmt=% outerAmt=% segs=% straightenCorners=% nVerts=% nEdges=% dupVerts=% seamValenceErr=% tJunctions=% openEdges=% maxYDev=% vol=% signedVol=%\n" \
            "O94fc22d10018d2660b2229a63443a89ea826084220c6c9f22e1fe4aa7acdaaa" "CHK_PLACEMENT_01" "PLC_001" "S8d4fdc410d784ec6024764fdec3fd50e78f7d9917fac5d8100ba05c72e5f124" isHidden (p.x as string) (p.y as string) (p.z as string) \
            (bMin.x as string) (bMin.y as string) (bMin.z as string) (bMax.x as string) (bMax.y as string) (bMax.z as string) \
            (modCount as string) baseCls mod1Cls (innerAmt as string) (outerAmt as string) (segs as string) (straightenCorners as string) (nVerts as string) (nEdges as string) (dupVerts as string) (seamValenceErr as string) (tJunctions as string) (openEdges as string) (maxYDev as string) ((abs evalVol) as string) (evalVol as string) to:__qa_out
    ) else (
        format "ROW observation_id=% check_id=% target_id=% sample_id=% status=NOT_FOUND exists=false\n" \
            "O94fc22d10018d2660b2229a63443a89ea826084220c6c9f22e1fe4aa7acdaaa" "CHK_PLACEMENT_01" "PLC_001" "S8d4fdc410d784ec6024764fdec3fd50e78f7d9917fac5d8100ba05c72e5f124" to:__qa_out
    )
    -- Observation Of9c519f098f68d1ded037a09aff4aa71f6ac3c236d652eae58381a32acf0316 (CHK_PLACEMENT_02)
    local nd = getNodeByName "PLC_002"
    if nd != undefined then (
        local p = nd.pos
        local bMin = nd.min
        local bMax = nd.max
        local modCount = nd.modifiers.count
        local isHidden = (nd.isHidden as string)
        local baseCls = if isProperty nd #baseObject and nd.baseObject != undefined then (classOf nd.baseObject as string) else (classOf nd as string)
        local mod1Cls = if modCount > 0 then (classOf nd.modifiers[1] as string) else "none"
        local innerAmt = 0.0d0; local outerAmt = 0.0d0; local segs = 0
        local straightenCorners = false
        if modCount > 0 and (classOf nd.modifiers[1]) == Shell do (
            local sm = nd.modifiers[1]
            try ( innerAmt = sm.innerAmount as double ) catch ()
            try ( outerAmt = sm.outerAmount as double ) catch ()
            try ( segs = sm.segments as integer ) catch ()
            try ( straightenCorners = sm.straightenCorners as booleanClass ) catch ()
        )
        local guideNd = getNodeByName (nd.name + "_InnerSpline")
        local guideKnots = #()
        if guideNd != undefined and (classOf guideNd) == SplineShape do (
            local nK = numKnots guideNd 1
            guideKnots = for k = 1 to nK collect (getKnotPoint guideNd 1 k)
        )
        local maxYDev = 0.0d0
        local nVerts = 0; local nEdges = 0; local dupVerts = 0; local seamValenceErr = 0; local tJunctions = 0
        try (
            if (classOf nd.baseObject) == Editable_Poly do (
                nVerts = polyop.getNumVerts nd.baseObject
                nEdges = polyop.getNumEdges nd.baseObject
                for vi = 1 to nVerts do (
                    local vp = polyop.getVert nd.baseObject vi
                    local dev = 0.0d0
                    if guideKnots.count > 0 then (
                        local minD = 1e9
                        local p2d = [vp.x, vp.y, 0]
                        for kp in guideKnots do (
                            local d = distance p2d [kp.x, kp.y, 0]
                            if d < minD do minD = d
                        )
                        dev = minD
                    ) else (
                        dev = abs (vp.y as double)
                    )
                    if dev > maxYDev do maxYDev = dev
                )
                if nVerts <= 1000 do (
                    for vi = 1 to (nVerts - 1) do (
                        local pvi = polyop.getVert nd.baseObject vi
                        for vj = (vi + 1) to nVerts do (
                            local pvj = polyop.getVert nd.baseObject vj
                            if (distance pvi pvj) < 0.001 do dupVerts += 1
                        )
                    )
                )
                for ei = 1 to nEdges do (
                    local ev = polyop.getEdgeVerts nd.baseObject ei
                    local p1 = polyop.getVert nd.baseObject ev[1]
                    local p2 = polyop.getVert nd.baseObject ev[2]
                    local ef = polyop.getEdgeFaces nd.baseObject ei
                    if ef.count > 2 do tJunctions += 1
                    if (abs (p1.x - p2.x) < 0.01) and (abs (p1.y - p2.y) < 0.01) and (abs (p1.z - p2.z) > 0.01) do (
                        local isSeam = true
                        if guideKnots.count >= 3 do (
                            isSeam = false
                            for ki = 1 to guideKnots.count do (
                                local kp = guideKnots[ki]
                                if (distance [p1.x, p1.y, 0] [kp.x, kp.y, 0]) < 0.01 do (
                                    local prevK = if ki == 1 then guideKnots[guideKnots.count] else guideKnots[ki-1]
                                    local nextK = if ki == guideKnots.count then guideKnots[1] else guideKnots[ki+1]
                                    local vPrev = normalize ([kp.x - prevK.x, kp.y - prevK.y, 0])
                                    local vNext = normalize ([nextK.x - kp.x, nextK.y - kp.y, 0])
                                    if (abs (dot vPrev vNext)) < 0.999 do isSeam = true
                                )
                            )
                        )
                        if isSeam do (
                            if ef.count != 2 do seamValenceErr += 1
                        )
                    )
                )
            )
        ) catch ()
        local evalVol = 0.0d0
        local openEdges = 0
        local tmpMesh = undefined
        try (
            in coordsys world (tmpMesh = snapshotAsMesh nd)
            if tmpMesh != undefined do (
                local nf = tmpMesh.numFaces
                if nf > 0 do (
                    local v1 = getVert tmpMesh 1
                    for f = 1 to nf do (
                        local f3 = getFace tmpMesh f
                        local a = getVert tmpMesh (f3.x as integer)
                        local b_v = getVert tmpMesh (f3.y as integer)
                        local c = getVert tmpMesh (f3.z as integer)
                        local ax = (a.x as double) - (v1.x as double)
                        local ay = (a.y as double) - (v1.y as double)
                        local az = (a.z as double) - (v1.z as double)
                        local bx = (b_v.x as double) - (v1.x as double)
                        local b_y = (b_v.y as double) - (v1.y as double)
                        local bz = (b_v.z as double) - (v1.z as double)
                        local cx = (c.x as double) - (v1.x as double)
                        local cy = (c.y as double) - (v1.y as double)
                        local cz = (c.z as double) - (v1.z as double)
                        evalVol += (ax * (b_y * cz - bz * cy) + ay * (bz * cx - bx * cz) + az * (bx * cy - b_y * cx)) / 6.0
                    )
                    try ( openEdges = (meshop.getOpenEdges tmpMesh).numberSet ) catch ()
                )
                delete tmpMesh; tmpMesh = undefined
            )
        ) catch ( if tmpMesh != undefined do try ( delete tmpMesh ) catch () )
        format "ROW observation_id=% check_id=% target_id=% sample_id=% status=OK exists=true isHidden=% pos=[%,%,%] min=[%,%,%] max=[%,%,%] modCount=% baseCls=% mod1Cls=% innerAmt=% outerAmt=% segs=% straightenCorners=% nVerts=% nEdges=% dupVerts=% seamValenceErr=% tJunctions=% openEdges=% maxYDev=% vol=% signedVol=%\n" \
            "Of9c519f098f68d1ded037a09aff4aa71f6ac3c236d652eae58381a32acf0316" "CHK_PLACEMENT_02" "PLC_002" "Se79496a55f46d5b2cc24f99499efb22aa63519a1ab8becf8a9bac971705e365" isHidden (p.x as string) (p.y as string) (p.z as string) \
            (bMin.x as string) (bMin.y as string) (bMin.z as string) (bMax.x as string) (bMax.y as string) (bMax.z as string) \
            (modCount as string) baseCls mod1Cls (innerAmt as string) (outerAmt as string) (segs as string) (straightenCorners as string) (nVerts as string) (nEdges as string) (dupVerts as string) (seamValenceErr as string) (tJunctions as string) (openEdges as string) (maxYDev as string) ((abs evalVol) as string) (evalVol as string) to:__qa_out
    ) else (
        format "ROW observation_id=% check_id=% target_id=% sample_id=% status=NOT_FOUND exists=false\n" \
            "Of9c519f098f68d1ded037a09aff4aa71f6ac3c236d652eae58381a32acf0316" "CHK_PLACEMENT_02" "PLC_002" "Se79496a55f46d5b2cc24f99499efb22aa63519a1ab8becf8a9bac971705e365" to:__qa_out
    )
    -- Observation O4917f92238699614af532e62a8815c7b977ded33a9b92c952182eec8b466a7a (CHK_PLACEMENT_03)
    local nd = getNodeByName "PLC_003"
    if nd != undefined then (
        local p = nd.pos
        local bMin = nd.min
        local bMax = nd.max
        local modCount = nd.modifiers.count
        local isHidden = (nd.isHidden as string)
        local baseCls = if isProperty nd #baseObject and nd.baseObject != undefined then (classOf nd.baseObject as string) else (classOf nd as string)
        local mod1Cls = if modCount > 0 then (classOf nd.modifiers[1] as string) else "none"
        local innerAmt = 0.0d0; local outerAmt = 0.0d0; local segs = 0
        local straightenCorners = false
        if modCount > 0 and (classOf nd.modifiers[1]) == Shell do (
            local sm = nd.modifiers[1]
            try ( innerAmt = sm.innerAmount as double ) catch ()
            try ( outerAmt = sm.outerAmount as double ) catch ()
            try ( segs = sm.segments as integer ) catch ()
            try ( straightenCorners = sm.straightenCorners as booleanClass ) catch ()
        )
        local guideNd = getNodeByName (nd.name + "_InnerSpline")
        local guideKnots = #()
        if guideNd != undefined and (classOf guideNd) == SplineShape do (
            local nK = numKnots guideNd 1
            guideKnots = for k = 1 to nK collect (getKnotPoint guideNd 1 k)
        )
        local maxYDev = 0.0d0
        local nVerts = 0; local nEdges = 0; local dupVerts = 0; local seamValenceErr = 0; local tJunctions = 0
        try (
            if (classOf nd.baseObject) == Editable_Poly do (
                nVerts = polyop.getNumVerts nd.baseObject
                nEdges = polyop.getNumEdges nd.baseObject
                for vi = 1 to nVerts do (
                    local vp = polyop.getVert nd.baseObject vi
                    local dev = 0.0d0
                    if guideKnots.count > 0 then (
                        local minD = 1e9
                        local p2d = [vp.x, vp.y, 0]
                        for kp in guideKnots do (
                            local d = distance p2d [kp.x, kp.y, 0]
                            if d < minD do minD = d
                        )
                        dev = minD
                    ) else (
                        dev = abs (vp.y as double)
                    )
                    if dev > maxYDev do maxYDev = dev
                )
                if nVerts <= 1000 do (
                    for vi = 1 to (nVerts - 1) do (
                        local pvi = polyop.getVert nd.baseObject vi
                        for vj = (vi + 1) to nVerts do (
                            local pvj = polyop.getVert nd.baseObject vj
                            if (distance pvi pvj) < 0.001 do dupVerts += 1
                        )
                    )
                )
                for ei = 1 to nEdges do (
                    local ev = polyop.getEdgeVerts nd.baseObject ei
                    local p1 = polyop.getVert nd.baseObject ev[1]
                    local p2 = polyop.getVert nd.baseObject ev[2]
                    local ef = polyop.getEdgeFaces nd.baseObject ei
                    if ef.count > 2 do tJunctions += 1
                    if (abs (p1.x - p2.x) < 0.01) and (abs (p1.y - p2.y) < 0.01) and (abs (p1.z - p2.z) > 0.01) do (
                        local isSeam = true
                        if guideKnots.count >= 3 do (
                            isSeam = false
                            for ki = 1 to guideKnots.count do (
                                local kp = guideKnots[ki]
                                if (distance [p1.x, p1.y, 0] [kp.x, kp.y, 0]) < 0.01 do (
                                    local prevK = if ki == 1 then guideKnots[guideKnots.count] else guideKnots[ki-1]
                                    local nextK = if ki == guideKnots.count then guideKnots[1] else guideKnots[ki+1]
                                    local vPrev = normalize ([kp.x - prevK.x, kp.y - prevK.y, 0])
                                    local vNext = normalize ([nextK.x - kp.x, nextK.y - kp.y, 0])
                                    if (abs (dot vPrev vNext)) < 0.999 do isSeam = true
                                )
                            )
                        )
                        if isSeam do (
                            if ef.count != 2 do seamValenceErr += 1
                        )
                    )
                )
            )
        ) catch ()
        local evalVol = 0.0d0
        local openEdges = 0
        local tmpMesh = undefined
        try (
            in coordsys world (tmpMesh = snapshotAsMesh nd)
            if tmpMesh != undefined do (
                local nf = tmpMesh.numFaces
                if nf > 0 do (
                    local v1 = getVert tmpMesh 1
                    for f = 1 to nf do (
                        local f3 = getFace tmpMesh f
                        local a = getVert tmpMesh (f3.x as integer)
                        local b_v = getVert tmpMesh (f3.y as integer)
                        local c = getVert tmpMesh (f3.z as integer)
                        local ax = (a.x as double) - (v1.x as double)
                        local ay = (a.y as double) - (v1.y as double)
                        local az = (a.z as double) - (v1.z as double)
                        local bx = (b_v.x as double) - (v1.x as double)
                        local b_y = (b_v.y as double) - (v1.y as double)
                        local bz = (b_v.z as double) - (v1.z as double)
                        local cx = (c.x as double) - (v1.x as double)
                        local cy = (c.y as double) - (v1.y as double)
                        local cz = (c.z as double) - (v1.z as double)
                        evalVol += (ax * (b_y * cz - bz * cy) + ay * (bz * cx - bx * cz) + az * (bx * cy - b_y * cx)) / 6.0
                    )
                    try ( openEdges = (meshop.getOpenEdges tmpMesh).numberSet ) catch ()
                )
                delete tmpMesh; tmpMesh = undefined
            )
        ) catch ( if tmpMesh != undefined do try ( delete tmpMesh ) catch () )
        format "ROW observation_id=% check_id=% target_id=% sample_id=% status=OK exists=true isHidden=% pos=[%,%,%] min=[%,%,%] max=[%,%,%] modCount=% baseCls=% mod1Cls=% innerAmt=% outerAmt=% segs=% straightenCorners=% nVerts=% nEdges=% dupVerts=% seamValenceErr=% tJunctions=% openEdges=% maxYDev=% vol=% signedVol=%\n" \
            "O4917f92238699614af532e62a8815c7b977ded33a9b92c952182eec8b466a7a" "CHK_PLACEMENT_03" "PLC_003" "Sd6cb76baba856021c993da8ed1b937a42ee82d4dbd8c0e1700c52680aa88f4e" isHidden (p.x as string) (p.y as string) (p.z as string) \
            (bMin.x as string) (bMin.y as string) (bMin.z as string) (bMax.x as string) (bMax.y as string) (bMax.z as string) \
            (modCount as string) baseCls mod1Cls (innerAmt as string) (outerAmt as string) (segs as string) (straightenCorners as string) (nVerts as string) (nEdges as string) (dupVerts as string) (seamValenceErr as string) (tJunctions as string) (openEdges as string) (maxYDev as string) ((abs evalVol) as string) (evalVol as string) to:__qa_out
    ) else (
        format "ROW observation_id=% check_id=% target_id=% sample_id=% status=NOT_FOUND exists=false\n" \
            "O4917f92238699614af532e62a8815c7b977ded33a9b92c952182eec8b466a7a" "CHK_PLACEMENT_03" "PLC_003" "Sd6cb76baba856021c993da8ed1b937a42ee82d4dbd8c0e1700c52680aa88f4e" to:__qa_out
    )
    -- Observation O1e358a126320cd0765bb8729b023e1290e7eba2470643fcddb3796c1ca06592 (CHK_CENSUS_EL1)
    local nd = getNodeByName "EL_001"
    if nd != undefined then (
        local p = nd.pos
        local bMin = nd.min
        local bMax = nd.max
        local modCount = nd.modifiers.count
        local isHidden = (nd.isHidden as string)
        local baseCls = if isProperty nd #baseObject and nd.baseObject != undefined then (classOf nd.baseObject as string) else (classOf nd as string)
        local mod1Cls = if modCount > 0 then (classOf nd.modifiers[1] as string) else "none"
        local innerAmt = 0.0d0; local outerAmt = 0.0d0; local segs = 0
        local straightenCorners = false
        if modCount > 0 and (classOf nd.modifiers[1]) == Shell do (
            local sm = nd.modifiers[1]
            try ( innerAmt = sm.innerAmount as double ) catch ()
            try ( outerAmt = sm.outerAmount as double ) catch ()
            try ( segs = sm.segments as integer ) catch ()
            try ( straightenCorners = sm.straightenCorners as booleanClass ) catch ()
        )
        local guideNd = getNodeByName (nd.name + "_InnerSpline")
        local guideKnots = #()
        if guideNd != undefined and (classOf guideNd) == SplineShape do (
            local nK = numKnots guideNd 1
            guideKnots = for k = 1 to nK collect (getKnotPoint guideNd 1 k)
        )
        local maxYDev = 0.0d0
        local nVerts = 0; local nEdges = 0; local dupVerts = 0; local seamValenceErr = 0; local tJunctions = 0
        try (
            if (classOf nd.baseObject) == Editable_Poly do (
                nVerts = polyop.getNumVerts nd.baseObject
                nEdges = polyop.getNumEdges nd.baseObject
                for vi = 1 to nVerts do (
                    local vp = polyop.getVert nd.baseObject vi
                    local dev = 0.0d0
                    if guideKnots.count > 0 then (
                        local minD = 1e9
                        local p2d = [vp.x, vp.y, 0]
                        for kp in guideKnots do (
                            local d = distance p2d [kp.x, kp.y, 0]
                            if d < minD do minD = d
                        )
                        dev = minD
                    ) else (
                        dev = abs (vp.y as double)
                    )
                    if dev > maxYDev do maxYDev = dev
                )
                if nVerts <= 1000 do (
                    for vi = 1 to (nVerts - 1) do (
                        local pvi = polyop.getVert nd.baseObject vi
                        for vj = (vi + 1) to nVerts do (
                            local pvj = polyop.getVert nd.baseObject vj
                            if (distance pvi pvj) < 0.001 do dupVerts += 1
                        )
                    )
                )
                for ei = 1 to nEdges do (
                    local ev = polyop.getEdgeVerts nd.baseObject ei
                    local p1 = polyop.getVert nd.baseObject ev[1]
                    local p2 = polyop.getVert nd.baseObject ev[2]
                    local ef = polyop.getEdgeFaces nd.baseObject ei
                    if ef.count > 2 do tJunctions += 1
                    if (abs (p1.x - p2.x) < 0.01) and (abs (p1.y - p2.y) < 0.01) and (abs (p1.z - p2.z) > 0.01) do (
                        local isSeam = true
                        if guideKnots.count >= 3 do (
                            isSeam = false
                            for ki = 1 to guideKnots.count do (
                                local kp = guideKnots[ki]
                                if (distance [p1.x, p1.y, 0] [kp.x, kp.y, 0]) < 0.01 do (
                                    local prevK = if ki == 1 then guideKnots[guideKnots.count] else guideKnots[ki-1]
                                    local nextK = if ki == guideKnots.count then guideKnots[1] else guideKnots[ki+1]
                                    local vPrev = normalize ([kp.x - prevK.x, kp.y - prevK.y, 0])
                                    local vNext = normalize ([nextK.x - kp.x, nextK.y - kp.y, 0])
                                    if (abs (dot vPrev vNext)) < 0.999 do isSeam = true
                                )
                            )
                        )
                        if isSeam do (
                            if ef.count != 2 do seamValenceErr += 1
                        )
                    )
                )
            )
        ) catch ()
        local evalVol = 0.0d0
        local openEdges = 0
        local tmpMesh = undefined
        try (
            in coordsys world (tmpMesh = snapshotAsMesh nd)
            if tmpMesh != undefined do (
                local nf = tmpMesh.numFaces
                if nf > 0 do (
                    local v1 = getVert tmpMesh 1
                    for f = 1 to nf do (
                        local f3 = getFace tmpMesh f
                        local a = getVert tmpMesh (f3.x as integer)
                        local b_v = getVert tmpMesh (f3.y as integer)
                        local c = getVert tmpMesh (f3.z as integer)
                        local ax = (a.x as double) - (v1.x as double)
                        local ay = (a.y as double) - (v1.y as double)
                        local az = (a.z as double) - (v1.z as double)
                        local bx = (b_v.x as double) - (v1.x as double)
                        local b_y = (b_v.y as double) - (v1.y as double)
                        local bz = (b_v.z as double) - (v1.z as double)
                        local cx = (c.x as double) - (v1.x as double)
                        local cy = (c.y as double) - (v1.y as double)
                        local cz = (c.z as double) - (v1.z as double)
                        evalVol += (ax * (b_y * cz - bz * cy) + ay * (bz * cx - bx * cz) + az * (bx * cy - b_y * cx)) / 6.0
                    )
                    try ( openEdges = (meshop.getOpenEdges tmpMesh).numberSet ) catch ()
                )
                delete tmpMesh; tmpMesh = undefined
            )
        ) catch ( if tmpMesh != undefined do try ( delete tmpMesh ) catch () )
        format "ROW observation_id=% check_id=% target_id=% sample_id=% status=OK exists=true isHidden=% pos=[%,%,%] min=[%,%,%] max=[%,%,%] modCount=% baseCls=% mod1Cls=% innerAmt=% outerAmt=% segs=% straightenCorners=% nVerts=% nEdges=% dupVerts=% seamValenceErr=% tJunctions=% openEdges=% maxYDev=% vol=% signedVol=%\n" \
            "O1e358a126320cd0765bb8729b023e1290e7eba2470643fcddb3796c1ca06592" "CHK_CENSUS_EL1" "EL_001" "S114142fa7b0bf5a3d236478df80bd6b0eab15f303696c9e4c88dfa5c67f474b" isHidden (p.x as string) (p.y as string) (p.z as string) \
            (bMin.x as string) (bMin.y as string) (bMin.z as string) (bMax.x as string) (bMax.y as string) (bMax.z as string) \
            (modCount as string) baseCls mod1Cls (innerAmt as string) (outerAmt as string) (segs as string) (straightenCorners as string) (nVerts as string) (nEdges as string) (dupVerts as string) (seamValenceErr as string) (tJunctions as string) (openEdges as string) (maxYDev as string) ((abs evalVol) as string) (evalVol as string) to:__qa_out
    ) else (
        format "ROW observation_id=% check_id=% target_id=% sample_id=% status=NOT_FOUND exists=false\n" \
            "O1e358a126320cd0765bb8729b023e1290e7eba2470643fcddb3796c1ca06592" "CHK_CENSUS_EL1" "EL_001" "S114142fa7b0bf5a3d236478df80bd6b0eab15f303696c9e4c88dfa5c67f474b" to:__qa_out
    )
    -- Observation Oe97b490ecc2b6e279730f3c6aecdea97ea7c9c82bb6b639f0b723c9b5abd29f (CHK_CENSUS_EL2)
    local nd = getNodeByName "EL_002"
    if nd != undefined then (
        local p = nd.pos
        local bMin = nd.min
        local bMax = nd.max
        local modCount = nd.modifiers.count
        local isHidden = (nd.isHidden as string)
        local baseCls = if isProperty nd #baseObject and nd.baseObject != undefined then (classOf nd.baseObject as string) else (classOf nd as string)
        local mod1Cls = if modCount > 0 then (classOf nd.modifiers[1] as string) else "none"
        local innerAmt = 0.0d0; local outerAmt = 0.0d0; local segs = 0
        local straightenCorners = false
        if modCount > 0 and (classOf nd.modifiers[1]) == Shell do (
            local sm = nd.modifiers[1]
            try ( innerAmt = sm.innerAmount as double ) catch ()
            try ( outerAmt = sm.outerAmount as double ) catch ()
            try ( segs = sm.segments as integer ) catch ()
            try ( straightenCorners = sm.straightenCorners as booleanClass ) catch ()
        )
        local guideNd = getNodeByName (nd.name + "_InnerSpline")
        local guideKnots = #()
        if guideNd != undefined and (classOf guideNd) == SplineShape do (
            local nK = numKnots guideNd 1
            guideKnots = for k = 1 to nK collect (getKnotPoint guideNd 1 k)
        )
        local maxYDev = 0.0d0
        local nVerts = 0; local nEdges = 0; local dupVerts = 0; local seamValenceErr = 0; local tJunctions = 0
        try (
            if (classOf nd.baseObject) == Editable_Poly do (
                nVerts = polyop.getNumVerts nd.baseObject
                nEdges = polyop.getNumEdges nd.baseObject
                for vi = 1 to nVerts do (
                    local vp = polyop.getVert nd.baseObject vi
                    local dev = 0.0d0
                    if guideKnots.count > 0 then (
                        local minD = 1e9
                        local p2d = [vp.x, vp.y, 0]
                        for kp in guideKnots do (
                            local d = distance p2d [kp.x, kp.y, 0]
                            if d < minD do minD = d
                        )
                        dev = minD
                    ) else (
                        dev = abs (vp.y as double)
                    )
                    if dev > maxYDev do maxYDev = dev
                )
                if nVerts <= 1000 do (
                    for vi = 1 to (nVerts - 1) do (
                        local pvi = polyop.getVert nd.baseObject vi
                        for vj = (vi + 1) to nVerts do (
                            local pvj = polyop.getVert nd.baseObject vj
                            if (distance pvi pvj) < 0.001 do dupVerts += 1
                        )
                    )
                )
                for ei = 1 to nEdges do (
                    local ev = polyop.getEdgeVerts nd.baseObject ei
                    local p1 = polyop.getVert nd.baseObject ev[1]
                    local p2 = polyop.getVert nd.baseObject ev[2]
                    local ef = polyop.getEdgeFaces nd.baseObject ei
                    if ef.count > 2 do tJunctions += 1
                    if (abs (p1.x - p2.x) < 0.01) and (abs (p1.y - p2.y) < 0.01) and (abs (p1.z - p2.z) > 0.01) do (
                        local isSeam = true
                        if guideKnots.count >= 3 do (
                            isSeam = false
                            for ki = 1 to guideKnots.count do (
                                local kp = guideKnots[ki]
                                if (distance [p1.x, p1.y, 0] [kp.x, kp.y, 0]) < 0.01 do (
                                    local prevK = if ki == 1 then guideKnots[guideKnots.count] else guideKnots[ki-1]
                                    local nextK = if ki == guideKnots.count then guideKnots[1] else guideKnots[ki+1]
                                    local vPrev = normalize ([kp.x - prevK.x, kp.y - prevK.y, 0])
                                    local vNext = normalize ([nextK.x - kp.x, nextK.y - kp.y, 0])
                                    if (abs (dot vPrev vNext)) < 0.999 do isSeam = true
                                )
                            )
                        )
                        if isSeam do (
                            if ef.count != 2 do seamValenceErr += 1
                        )
                    )
                )
            )
        ) catch ()
        local evalVol = 0.0d0
        local openEdges = 0
        local tmpMesh = undefined
        try (
            in coordsys world (tmpMesh = snapshotAsMesh nd)
            if tmpMesh != undefined do (
                local nf = tmpMesh.numFaces
                if nf > 0 do (
                    local v1 = getVert tmpMesh 1
                    for f = 1 to nf do (
                        local f3 = getFace tmpMesh f
                        local a = getVert tmpMesh (f3.x as integer)
                        local b_v = getVert tmpMesh (f3.y as integer)
                        local c = getVert tmpMesh (f3.z as integer)
                        local ax = (a.x as double) - (v1.x as double)
                        local ay = (a.y as double) - (v1.y as double)
                        local az = (a.z as double) - (v1.z as double)
                        local bx = (b_v.x as double) - (v1.x as double)
                        local b_y = (b_v.y as double) - (v1.y as double)
                        local bz = (b_v.z as double) - (v1.z as double)
                        local cx = (c.x as double) - (v1.x as double)
                        local cy = (c.y as double) - (v1.y as double)
                        local cz = (c.z as double) - (v1.z as double)
                        evalVol += (ax * (b_y * cz - bz * cy) + ay * (bz * cx - bx * cz) + az * (bx * cy - b_y * cx)) / 6.0
                    )
                    try ( openEdges = (meshop.getOpenEdges tmpMesh).numberSet ) catch ()
                )
                delete tmpMesh; tmpMesh = undefined
            )
        ) catch ( if tmpMesh != undefined do try ( delete tmpMesh ) catch () )
        format "ROW observation_id=% check_id=% target_id=% sample_id=% status=OK exists=true isHidden=% pos=[%,%,%] min=[%,%,%] max=[%,%,%] modCount=% baseCls=% mod1Cls=% innerAmt=% outerAmt=% segs=% straightenCorners=% nVerts=% nEdges=% dupVerts=% seamValenceErr=% tJunctions=% openEdges=% maxYDev=% vol=% signedVol=%\n" \
            "Oe97b490ecc2b6e279730f3c6aecdea97ea7c9c82bb6b639f0b723c9b5abd29f" "CHK_CENSUS_EL2" "EL_002" "S4d3618dad063cb95485ef2d8cc146d7dc0c3d60d74b372302b6c01526f401f6" isHidden (p.x as string) (p.y as string) (p.z as string) \
            (bMin.x as string) (bMin.y as string) (bMin.z as string) (bMax.x as string) (bMax.y as string) (bMax.z as string) \
            (modCount as string) baseCls mod1Cls (innerAmt as string) (outerAmt as string) (segs as string) (straightenCorners as string) (nVerts as string) (nEdges as string) (dupVerts as string) (seamValenceErr as string) (tJunctions as string) (openEdges as string) (maxYDev as string) ((abs evalVol) as string) (evalVol as string) to:__qa_out
    ) else (
        format "ROW observation_id=% check_id=% target_id=% sample_id=% status=NOT_FOUND exists=false\n" \
            "Oe97b490ecc2b6e279730f3c6aecdea97ea7c9c82bb6b639f0b723c9b5abd29f" "CHK_CENSUS_EL2" "EL_002" "S4d3618dad063cb95485ef2d8cc146d7dc0c3d60d74b372302b6c01526f401f6" to:__qa_out
    )
    format "END_BATCH batch_id=% rows=%\n" "batch_001" 11 to:__qa_out
    __qa_out as string
)
