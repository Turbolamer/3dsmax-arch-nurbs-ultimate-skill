-- Batch batch_001 for QA run live-run-001
(
    local __qa_out = stringStream ""
    format "START_BATCH batch_id=%\n" "batch_001" to:__qa_out
    local sysType = (units.SystemType as string)
    local sysScale = (units.SystemScale as string)
    format "GUARD units.SystemType=% units.SystemScale=%\n" sysType sysScale to:__qa_out
    -- Observation Ob68274c771d6215cf161825a6c77cda089880b4bb7f698ce6e7ddb1c30dcda8 (CHK_FORM_01 grid/0/0)
    local nd = getNodeByName "SUR_001_Vault"
    if nd != undefined then (
        local p = nd.pos
        local nset = getNURBSSet nd #relational
        local surf = undefined
        for s_i = 1 to nset.numObjects do (
            local obj = getObject nset s_i
            if (superClassOf obj) == NURBSSurface do ( surf = obj; exit )
        )
        if surf != undefined do (
            local u = surf.uParameterRangeMin + (surf.uParameterRangeMax - surf.uParameterRangeMin) * 0
            local v = surf.vParameterRangeMin + (surf.vParameterRangeMax - surf.vParameterRangeMin) * 0
            p = evalPos surf u v
        )
        local bMin = nd.min
        local bMax = nd.max
        local modCount = nd.modifiers.count
        local isHidden = (nd.isHidden as string)
        format "ROW observation_id=% check_id=% target_id=% sample_id=% status=OK exists=true isHidden=% pos=[%,%,%] min=[%,%,%] max=[%,%,%] modCount=%\n" \
            "Ob68274c771d6215cf161825a6c77cda089880b4bb7f698ce6e7ddb1c30dcda8" "CHK_FORM_01" "TGT-001" "S9d1e66a92de7d03701de63f72d672d7e4a68fbcfb68ab351ca7f3f17e25482a" isHidden (p.x as string) (p.y as string) (p.z as string) \
            (bMin.x as string) (bMin.y as string) (bMin.z as string) (bMax.x as string) (bMax.y as string) (bMax.z as string) (modCount as string) to:__qa_out
    ) else (
        format "ROW observation_id=% check_id=% target_id=% sample_id=% status=NOT_FOUND exists=false\n" \
            "Ob68274c771d6215cf161825a6c77cda089880b4bb7f698ce6e7ddb1c30dcda8" "CHK_FORM_01" "TGT-001" "S9d1e66a92de7d03701de63f72d672d7e4a68fbcfb68ab351ca7f3f17e25482a" to:__qa_out
    )
    -- Observation O9c52a1b79fcef5457f82e25fcdb10785ea9a2e75417488188d876ec731c1ab2 (CHK_FORM_01 grid/0/1)
    local nd = getNodeByName "SUR_001_Vault"
    if nd != undefined then (
        local p = nd.pos
        local nset = getNURBSSet nd #relational
        local surf = undefined
        for s_i = 1 to nset.numObjects do (
            local obj = getObject nset s_i
            if (superClassOf obj) == NURBSSurface do ( surf = obj; exit )
        )
        if surf != undefined do (
            local u = surf.uParameterRangeMin + (surf.uParameterRangeMax - surf.uParameterRangeMin) * 0
            local v = surf.vParameterRangeMin + (surf.vParameterRangeMax - surf.vParameterRangeMin) * 0.25
            p = evalPos surf u v
        )
        local bMin = nd.min
        local bMax = nd.max
        local modCount = nd.modifiers.count
        local isHidden = (nd.isHidden as string)
        format "ROW observation_id=% check_id=% target_id=% sample_id=% status=OK exists=true isHidden=% pos=[%,%,%] min=[%,%,%] max=[%,%,%] modCount=%\n" \
            "O9c52a1b79fcef5457f82e25fcdb10785ea9a2e75417488188d876ec731c1ab2" "CHK_FORM_01" "TGT-001" "S5317409976514c9805bb816e0c13e65ad70f493179dc54acd22d2a7dbacbb72" isHidden (p.x as string) (p.y as string) (p.z as string) \
            (bMin.x as string) (bMin.y as string) (bMin.z as string) (bMax.x as string) (bMax.y as string) (bMax.z as string) (modCount as string) to:__qa_out
    ) else (
        format "ROW observation_id=% check_id=% target_id=% sample_id=% status=NOT_FOUND exists=false\n" \
            "O9c52a1b79fcef5457f82e25fcdb10785ea9a2e75417488188d876ec731c1ab2" "CHK_FORM_01" "TGT-001" "S5317409976514c9805bb816e0c13e65ad70f493179dc54acd22d2a7dbacbb72" to:__qa_out
    )
    -- Observation O9da689b2d05821174ccc212b95a2ba18b44508c5d46e601c5610d0cf4f099b1 (CHK_FORM_01 grid/0/2)
    local nd = getNodeByName "SUR_001_Vault"
    if nd != undefined then (
        local p = nd.pos
        local nset = getNURBSSet nd #relational
        local surf = undefined
        for s_i = 1 to nset.numObjects do (
            local obj = getObject nset s_i
            if (superClassOf obj) == NURBSSurface do ( surf = obj; exit )
        )
        if surf != undefined do (
            local u = surf.uParameterRangeMin + (surf.uParameterRangeMax - surf.uParameterRangeMin) * 0
            local v = surf.vParameterRangeMin + (surf.vParameterRangeMax - surf.vParameterRangeMin) * 0.5
            p = evalPos surf u v
        )
        local bMin = nd.min
        local bMax = nd.max
        local modCount = nd.modifiers.count
        local isHidden = (nd.isHidden as string)
        format "ROW observation_id=% check_id=% target_id=% sample_id=% status=OK exists=true isHidden=% pos=[%,%,%] min=[%,%,%] max=[%,%,%] modCount=%\n" \
            "O9da689b2d05821174ccc212b95a2ba18b44508c5d46e601c5610d0cf4f099b1" "CHK_FORM_01" "TGT-001" "S113333d7f738b1cd286af8d6d15a229b374e6aebdc6703a50047f5288ac6dbe" isHidden (p.x as string) (p.y as string) (p.z as string) \
            (bMin.x as string) (bMin.y as string) (bMin.z as string) (bMax.x as string) (bMax.y as string) (bMax.z as string) (modCount as string) to:__qa_out
    ) else (
        format "ROW observation_id=% check_id=% target_id=% sample_id=% status=NOT_FOUND exists=false\n" \
            "O9da689b2d05821174ccc212b95a2ba18b44508c5d46e601c5610d0cf4f099b1" "CHK_FORM_01" "TGT-001" "S113333d7f738b1cd286af8d6d15a229b374e6aebdc6703a50047f5288ac6dbe" to:__qa_out
    )
    -- Observation O1ceedea9e69399cf79a250d4cde8f434c777897ca94ec1ae48b755adca2826b (CHK_FORM_01 grid/0/3)
    local nd = getNodeByName "SUR_001_Vault"
    if nd != undefined then (
        local p = nd.pos
        local nset = getNURBSSet nd #relational
        local surf = undefined
        for s_i = 1 to nset.numObjects do (
            local obj = getObject nset s_i
            if (superClassOf obj) == NURBSSurface do ( surf = obj; exit )
        )
        if surf != undefined do (
            local u = surf.uParameterRangeMin + (surf.uParameterRangeMax - surf.uParameterRangeMin) * 0
            local v = surf.vParameterRangeMin + (surf.vParameterRangeMax - surf.vParameterRangeMin) * 0.75
            p = evalPos surf u v
        )
        local bMin = nd.min
        local bMax = nd.max
        local modCount = nd.modifiers.count
        local isHidden = (nd.isHidden as string)
        format "ROW observation_id=% check_id=% target_id=% sample_id=% status=OK exists=true isHidden=% pos=[%,%,%] min=[%,%,%] max=[%,%,%] modCount=%\n" \
            "O1ceedea9e69399cf79a250d4cde8f434c777897ca94ec1ae48b755adca2826b" "CHK_FORM_01" "TGT-001" "Se1aa619c0d93dc3644a9d1c8dfec42eadf67c67f12b4771ef0f4483ea49a884" isHidden (p.x as string) (p.y as string) (p.z as string) \
            (bMin.x as string) (bMin.y as string) (bMin.z as string) (bMax.x as string) (bMax.y as string) (bMax.z as string) (modCount as string) to:__qa_out
    ) else (
        format "ROW observation_id=% check_id=% target_id=% sample_id=% status=NOT_FOUND exists=false\n" \
            "O1ceedea9e69399cf79a250d4cde8f434c777897ca94ec1ae48b755adca2826b" "CHK_FORM_01" "TGT-001" "Se1aa619c0d93dc3644a9d1c8dfec42eadf67c67f12b4771ef0f4483ea49a884" to:__qa_out
    )
    -- Observation O415e589dea4d4875dd0d778a1d85985fc81e0ffadcdef43e8d99aae33218b3f (CHK_FORM_01 grid/0/4)
    local nd = getNodeByName "SUR_001_Vault"
    if nd != undefined then (
        local p = nd.pos
        local nset = getNURBSSet nd #relational
        local surf = undefined
        for s_i = 1 to nset.numObjects do (
            local obj = getObject nset s_i
            if (superClassOf obj) == NURBSSurface do ( surf = obj; exit )
        )
        if surf != undefined do (
            local u = surf.uParameterRangeMin + (surf.uParameterRangeMax - surf.uParameterRangeMin) * 0
            local v = surf.vParameterRangeMin + (surf.vParameterRangeMax - surf.vParameterRangeMin) * 1
            p = evalPos surf u v
        )
        local bMin = nd.min
        local bMax = nd.max
        local modCount = nd.modifiers.count
        local isHidden = (nd.isHidden as string)
        format "ROW observation_id=% check_id=% target_id=% sample_id=% status=OK exists=true isHidden=% pos=[%,%,%] min=[%,%,%] max=[%,%,%] modCount=%\n" \
            "O415e589dea4d4875dd0d778a1d85985fc81e0ffadcdef43e8d99aae33218b3f" "CHK_FORM_01" "TGT-001" "S13aa21f0c9ade41740ad881fc5fec47cb2afcb5e1978894b8bdc6b4ca5966ae" isHidden (p.x as string) (p.y as string) (p.z as string) \
            (bMin.x as string) (bMin.y as string) (bMin.z as string) (bMax.x as string) (bMax.y as string) (bMax.z as string) (modCount as string) to:__qa_out
    ) else (
        format "ROW observation_id=% check_id=% target_id=% sample_id=% status=NOT_FOUND exists=false\n" \
            "O415e589dea4d4875dd0d778a1d85985fc81e0ffadcdef43e8d99aae33218b3f" "CHK_FORM_01" "TGT-001" "S13aa21f0c9ade41740ad881fc5fec47cb2afcb5e1978894b8bdc6b4ca5966ae" to:__qa_out
    )
    -- Observation O6ff59c74f5607baa6d22c7759086f08db65d06de2d50bdd611adb6b59c6848a (CHK_FORM_01 grid/1/0)
    local nd = getNodeByName "SUR_001_Vault"
    if nd != undefined then (
        local p = nd.pos
        local nset = getNURBSSet nd #relational
        local surf = undefined
        for s_i = 1 to nset.numObjects do (
            local obj = getObject nset s_i
            if (superClassOf obj) == NURBSSurface do ( surf = obj; exit )
        )
        if surf != undefined do (
            local u = surf.uParameterRangeMin + (surf.uParameterRangeMax - surf.uParameterRangeMin) * 0.25
            local v = surf.vParameterRangeMin + (surf.vParameterRangeMax - surf.vParameterRangeMin) * 0
            p = evalPos surf u v
        )
        local bMin = nd.min
        local bMax = nd.max
        local modCount = nd.modifiers.count
        local isHidden = (nd.isHidden as string)
        format "ROW observation_id=% check_id=% target_id=% sample_id=% status=OK exists=true isHidden=% pos=[%,%,%] min=[%,%,%] max=[%,%,%] modCount=%\n" \
            "O6ff59c74f5607baa6d22c7759086f08db65d06de2d50bdd611adb6b59c6848a" "CHK_FORM_01" "TGT-001" "Sa3806dd62c06391de017c18040812c5176a35364e89b94e673650148084592c" isHidden (p.x as string) (p.y as string) (p.z as string) \
            (bMin.x as string) (bMin.y as string) (bMin.z as string) (bMax.x as string) (bMax.y as string) (bMax.z as string) (modCount as string) to:__qa_out
    ) else (
        format "ROW observation_id=% check_id=% target_id=% sample_id=% status=NOT_FOUND exists=false\n" \
            "O6ff59c74f5607baa6d22c7759086f08db65d06de2d50bdd611adb6b59c6848a" "CHK_FORM_01" "TGT-001" "Sa3806dd62c06391de017c18040812c5176a35364e89b94e673650148084592c" to:__qa_out
    )
    -- Observation Od502c8b484dcb36d66c4c1a05592077be5c40e95779b3fd3f789db2d24a8ad9 (CHK_FORM_01 grid/1/1)
    local nd = getNodeByName "SUR_001_Vault"
    if nd != undefined then (
        local p = nd.pos
        local nset = getNURBSSet nd #relational
        local surf = undefined
        for s_i = 1 to nset.numObjects do (
            local obj = getObject nset s_i
            if (superClassOf obj) == NURBSSurface do ( surf = obj; exit )
        )
        if surf != undefined do (
            local u = surf.uParameterRangeMin + (surf.uParameterRangeMax - surf.uParameterRangeMin) * 0.25
            local v = surf.vParameterRangeMin + (surf.vParameterRangeMax - surf.vParameterRangeMin) * 0.25
            p = evalPos surf u v
        )
        local bMin = nd.min
        local bMax = nd.max
        local modCount = nd.modifiers.count
        local isHidden = (nd.isHidden as string)
        format "ROW observation_id=% check_id=% target_id=% sample_id=% status=OK exists=true isHidden=% pos=[%,%,%] min=[%,%,%] max=[%,%,%] modCount=%\n" \
            "Od502c8b484dcb36d66c4c1a05592077be5c40e95779b3fd3f789db2d24a8ad9" "CHK_FORM_01" "TGT-001" "S20944fa119054d8ccc25d38ebfcce4b0a2bfc438ecfa82c7541209b34cdbf95" isHidden (p.x as string) (p.y as string) (p.z as string) \
            (bMin.x as string) (bMin.y as string) (bMin.z as string) (bMax.x as string) (bMax.y as string) (bMax.z as string) (modCount as string) to:__qa_out
    ) else (
        format "ROW observation_id=% check_id=% target_id=% sample_id=% status=NOT_FOUND exists=false\n" \
            "Od502c8b484dcb36d66c4c1a05592077be5c40e95779b3fd3f789db2d24a8ad9" "CHK_FORM_01" "TGT-001" "S20944fa119054d8ccc25d38ebfcce4b0a2bfc438ecfa82c7541209b34cdbf95" to:__qa_out
    )
    -- Observation O0593b1d13cd49cff2bc167b887a0a915dae4ec418cad2f6a0e6ab8c78eaba36 (CHK_FORM_01 grid/1/2)
    local nd = getNodeByName "SUR_001_Vault"
    if nd != undefined then (
        local p = nd.pos
        local nset = getNURBSSet nd #relational
        local surf = undefined
        for s_i = 1 to nset.numObjects do (
            local obj = getObject nset s_i
            if (superClassOf obj) == NURBSSurface do ( surf = obj; exit )
        )
        if surf != undefined do (
            local u = surf.uParameterRangeMin + (surf.uParameterRangeMax - surf.uParameterRangeMin) * 0.25
            local v = surf.vParameterRangeMin + (surf.vParameterRangeMax - surf.vParameterRangeMin) * 0.5
            p = evalPos surf u v
        )
        local bMin = nd.min
        local bMax = nd.max
        local modCount = nd.modifiers.count
        local isHidden = (nd.isHidden as string)
        format "ROW observation_id=% check_id=% target_id=% sample_id=% status=OK exists=true isHidden=% pos=[%,%,%] min=[%,%,%] max=[%,%,%] modCount=%\n" \
            "O0593b1d13cd49cff2bc167b887a0a915dae4ec418cad2f6a0e6ab8c78eaba36" "CHK_FORM_01" "TGT-001" "S6c12a3c4332c08f481487d6a3c1a308335eed4b3547a980fd5902674d0940f6" isHidden (p.x as string) (p.y as string) (p.z as string) \
            (bMin.x as string) (bMin.y as string) (bMin.z as string) (bMax.x as string) (bMax.y as string) (bMax.z as string) (modCount as string) to:__qa_out
    ) else (
        format "ROW observation_id=% check_id=% target_id=% sample_id=% status=NOT_FOUND exists=false\n" \
            "O0593b1d13cd49cff2bc167b887a0a915dae4ec418cad2f6a0e6ab8c78eaba36" "CHK_FORM_01" "TGT-001" "S6c12a3c4332c08f481487d6a3c1a308335eed4b3547a980fd5902674d0940f6" to:__qa_out
    )
    -- Observation Oab09deae4004ad0c06126f608b9110d65f774b1089e38bd39dc43966def3056 (CHK_FORM_01 grid/1/3)
    local nd = getNodeByName "SUR_001_Vault"
    if nd != undefined then (
        local p = nd.pos
        local nset = getNURBSSet nd #relational
        local surf = undefined
        for s_i = 1 to nset.numObjects do (
            local obj = getObject nset s_i
            if (superClassOf obj) == NURBSSurface do ( surf = obj; exit )
        )
        if surf != undefined do (
            local u = surf.uParameterRangeMin + (surf.uParameterRangeMax - surf.uParameterRangeMin) * 0.25
            local v = surf.vParameterRangeMin + (surf.vParameterRangeMax - surf.vParameterRangeMin) * 0.75
            p = evalPos surf u v
        )
        local bMin = nd.min
        local bMax = nd.max
        local modCount = nd.modifiers.count
        local isHidden = (nd.isHidden as string)
        format "ROW observation_id=% check_id=% target_id=% sample_id=% status=OK exists=true isHidden=% pos=[%,%,%] min=[%,%,%] max=[%,%,%] modCount=%\n" \
            "Oab09deae4004ad0c06126f608b9110d65f774b1089e38bd39dc43966def3056" "CHK_FORM_01" "TGT-001" "S7e95379149d5a777c03cd78306c925eefab841647b60f0ba1a454e41f53639a" isHidden (p.x as string) (p.y as string) (p.z as string) \
            (bMin.x as string) (bMin.y as string) (bMin.z as string) (bMax.x as string) (bMax.y as string) (bMax.z as string) (modCount as string) to:__qa_out
    ) else (
        format "ROW observation_id=% check_id=% target_id=% sample_id=% status=NOT_FOUND exists=false\n" \
            "Oab09deae4004ad0c06126f608b9110d65f774b1089e38bd39dc43966def3056" "CHK_FORM_01" "TGT-001" "S7e95379149d5a777c03cd78306c925eefab841647b60f0ba1a454e41f53639a" to:__qa_out
    )
    -- Observation O8213f19cb0f87a5204c4bb7560d84340ed34131049674cb5ded49c62523c3b0 (CHK_FORM_01 grid/1/4)
    local nd = getNodeByName "SUR_001_Vault"
    if nd != undefined then (
        local p = nd.pos
        local nset = getNURBSSet nd #relational
        local surf = undefined
        for s_i = 1 to nset.numObjects do (
            local obj = getObject nset s_i
            if (superClassOf obj) == NURBSSurface do ( surf = obj; exit )
        )
        if surf != undefined do (
            local u = surf.uParameterRangeMin + (surf.uParameterRangeMax - surf.uParameterRangeMin) * 0.25
            local v = surf.vParameterRangeMin + (surf.vParameterRangeMax - surf.vParameterRangeMin) * 1
            p = evalPos surf u v
        )
        local bMin = nd.min
        local bMax = nd.max
        local modCount = nd.modifiers.count
        local isHidden = (nd.isHidden as string)
        format "ROW observation_id=% check_id=% target_id=% sample_id=% status=OK exists=true isHidden=% pos=[%,%,%] min=[%,%,%] max=[%,%,%] modCount=%\n" \
            "O8213f19cb0f87a5204c4bb7560d84340ed34131049674cb5ded49c62523c3b0" "CHK_FORM_01" "TGT-001" "S45935ffa21c92e5c13634bb33ad16159400566c6105dc5c63eb3eb4467cf9ec" isHidden (p.x as string) (p.y as string) (p.z as string) \
            (bMin.x as string) (bMin.y as string) (bMin.z as string) (bMax.x as string) (bMax.y as string) (bMax.z as string) (modCount as string) to:__qa_out
    ) else (
        format "ROW observation_id=% check_id=% target_id=% sample_id=% status=NOT_FOUND exists=false\n" \
            "O8213f19cb0f87a5204c4bb7560d84340ed34131049674cb5ded49c62523c3b0" "CHK_FORM_01" "TGT-001" "S45935ffa21c92e5c13634bb33ad16159400566c6105dc5c63eb3eb4467cf9ec" to:__qa_out
    )
    -- Observation Oc311dd6ac9d18c53a9db807a7c2bb907def8d87ed122f59a326a6d72e4ee563 (CHK_FORM_01 grid/2/0)
    local nd = getNodeByName "SUR_001_Vault"
    if nd != undefined then (
        local p = nd.pos
        local nset = getNURBSSet nd #relational
        local surf = undefined
        for s_i = 1 to nset.numObjects do (
            local obj = getObject nset s_i
            if (superClassOf obj) == NURBSSurface do ( surf = obj; exit )
        )
        if surf != undefined do (
            local u = surf.uParameterRangeMin + (surf.uParameterRangeMax - surf.uParameterRangeMin) * 0.5
            local v = surf.vParameterRangeMin + (surf.vParameterRangeMax - surf.vParameterRangeMin) * 0
            p = evalPos surf u v
        )
        local bMin = nd.min
        local bMax = nd.max
        local modCount = nd.modifiers.count
        local isHidden = (nd.isHidden as string)
        format "ROW observation_id=% check_id=% target_id=% sample_id=% status=OK exists=true isHidden=% pos=[%,%,%] min=[%,%,%] max=[%,%,%] modCount=%\n" \
            "Oc311dd6ac9d18c53a9db807a7c2bb907def8d87ed122f59a326a6d72e4ee563" "CHK_FORM_01" "TGT-001" "Saf3333f3b6bf6ce8f2cefc5673771214e88855834d219fbb576edc6ddd0b71f" isHidden (p.x as string) (p.y as string) (p.z as string) \
            (bMin.x as string) (bMin.y as string) (bMin.z as string) (bMax.x as string) (bMax.y as string) (bMax.z as string) (modCount as string) to:__qa_out
    ) else (
        format "ROW observation_id=% check_id=% target_id=% sample_id=% status=NOT_FOUND exists=false\n" \
            "Oc311dd6ac9d18c53a9db807a7c2bb907def8d87ed122f59a326a6d72e4ee563" "CHK_FORM_01" "TGT-001" "Saf3333f3b6bf6ce8f2cefc5673771214e88855834d219fbb576edc6ddd0b71f" to:__qa_out
    )
    -- Observation O86c3c75032d009d58e96ea9b5bcce20d44d91f21b053fbef55e07c521ee1716 (CHK_FORM_01 grid/2/1)
    local nd = getNodeByName "SUR_001_Vault"
    if nd != undefined then (
        local p = nd.pos
        local nset = getNURBSSet nd #relational
        local surf = undefined
        for s_i = 1 to nset.numObjects do (
            local obj = getObject nset s_i
            if (superClassOf obj) == NURBSSurface do ( surf = obj; exit )
        )
        if surf != undefined do (
            local u = surf.uParameterRangeMin + (surf.uParameterRangeMax - surf.uParameterRangeMin) * 0.5
            local v = surf.vParameterRangeMin + (surf.vParameterRangeMax - surf.vParameterRangeMin) * 0.25
            p = evalPos surf u v
        )
        local bMin = nd.min
        local bMax = nd.max
        local modCount = nd.modifiers.count
        local isHidden = (nd.isHidden as string)
        format "ROW observation_id=% check_id=% target_id=% sample_id=% status=OK exists=true isHidden=% pos=[%,%,%] min=[%,%,%] max=[%,%,%] modCount=%\n" \
            "O86c3c75032d009d58e96ea9b5bcce20d44d91f21b053fbef55e07c521ee1716" "CHK_FORM_01" "TGT-001" "S463d26a25b0fa899d71504f9a467a9737790606c2c50df5142d7c214ff4c8d9" isHidden (p.x as string) (p.y as string) (p.z as string) \
            (bMin.x as string) (bMin.y as string) (bMin.z as string) (bMax.x as string) (bMax.y as string) (bMax.z as string) (modCount as string) to:__qa_out
    ) else (
        format "ROW observation_id=% check_id=% target_id=% sample_id=% status=NOT_FOUND exists=false\n" \
            "O86c3c75032d009d58e96ea9b5bcce20d44d91f21b053fbef55e07c521ee1716" "CHK_FORM_01" "TGT-001" "S463d26a25b0fa899d71504f9a467a9737790606c2c50df5142d7c214ff4c8d9" to:__qa_out
    )
    -- Observation Ob60bfb247107fc24fac42d123fa7a27c802bc973df2ba6aceaf1e89ff421284 (CHK_FORM_01 grid/2/2)
    local nd = getNodeByName "SUR_001_Vault"
    if nd != undefined then (
        local p = nd.pos
        local nset = getNURBSSet nd #relational
        local surf = undefined
        for s_i = 1 to nset.numObjects do (
            local obj = getObject nset s_i
            if (superClassOf obj) == NURBSSurface do ( surf = obj; exit )
        )
        if surf != undefined do (
            local u = surf.uParameterRangeMin + (surf.uParameterRangeMax - surf.uParameterRangeMin) * 0.5
            local v = surf.vParameterRangeMin + (surf.vParameterRangeMax - surf.vParameterRangeMin) * 0.5
            p = evalPos surf u v
        )
        local bMin = nd.min
        local bMax = nd.max
        local modCount = nd.modifiers.count
        local isHidden = (nd.isHidden as string)
        format "ROW observation_id=% check_id=% target_id=% sample_id=% status=OK exists=true isHidden=% pos=[%,%,%] min=[%,%,%] max=[%,%,%] modCount=%\n" \
            "Ob60bfb247107fc24fac42d123fa7a27c802bc973df2ba6aceaf1e89ff421284" "CHK_FORM_01" "TGT-001" "S13ef18b3e3d81de26d055efa3fb67ff2979372af451e601f49be8dbcd7953a7" isHidden (p.x as string) (p.y as string) (p.z as string) \
            (bMin.x as string) (bMin.y as string) (bMin.z as string) (bMax.x as string) (bMax.y as string) (bMax.z as string) (modCount as string) to:__qa_out
    ) else (
        format "ROW observation_id=% check_id=% target_id=% sample_id=% status=NOT_FOUND exists=false\n" \
            "Ob60bfb247107fc24fac42d123fa7a27c802bc973df2ba6aceaf1e89ff421284" "CHK_FORM_01" "TGT-001" "S13ef18b3e3d81de26d055efa3fb67ff2979372af451e601f49be8dbcd7953a7" to:__qa_out
    )
    -- Observation O168350b9280d3dcf0871104346bd3e6986803ab8712a497b6370a5bf734253f (CHK_FORM_01 grid/2/3)
    local nd = getNodeByName "SUR_001_Vault"
    if nd != undefined then (
        local p = nd.pos
        local nset = getNURBSSet nd #relational
        local surf = undefined
        for s_i = 1 to nset.numObjects do (
            local obj = getObject nset s_i
            if (superClassOf obj) == NURBSSurface do ( surf = obj; exit )
        )
        if surf != undefined do (
            local u = surf.uParameterRangeMin + (surf.uParameterRangeMax - surf.uParameterRangeMin) * 0.5
            local v = surf.vParameterRangeMin + (surf.vParameterRangeMax - surf.vParameterRangeMin) * 0.75
            p = evalPos surf u v
        )
        local bMin = nd.min
        local bMax = nd.max
        local modCount = nd.modifiers.count
        local isHidden = (nd.isHidden as string)
        format "ROW observation_id=% check_id=% target_id=% sample_id=% status=OK exists=true isHidden=% pos=[%,%,%] min=[%,%,%] max=[%,%,%] modCount=%\n" \
            "O168350b9280d3dcf0871104346bd3e6986803ab8712a497b6370a5bf734253f" "CHK_FORM_01" "TGT-001" "S3f1af1a0dcde2bcd1e71e7c791092a92212f8ce6ea25e30205dd06722000fe4" isHidden (p.x as string) (p.y as string) (p.z as string) \
            (bMin.x as string) (bMin.y as string) (bMin.z as string) (bMax.x as string) (bMax.y as string) (bMax.z as string) (modCount as string) to:__qa_out
    ) else (
        format "ROW observation_id=% check_id=% target_id=% sample_id=% status=NOT_FOUND exists=false\n" \
            "O168350b9280d3dcf0871104346bd3e6986803ab8712a497b6370a5bf734253f" "CHK_FORM_01" "TGT-001" "S3f1af1a0dcde2bcd1e71e7c791092a92212f8ce6ea25e30205dd06722000fe4" to:__qa_out
    )
    -- Observation O7bb47b8ca6ee3bacd980b8910e5a20dc9adf40af344e57097a80a95cf0996f6 (CHK_FORM_01 grid/2/4)
    local nd = getNodeByName "SUR_001_Vault"
    if nd != undefined then (
        local p = nd.pos
        local nset = getNURBSSet nd #relational
        local surf = undefined
        for s_i = 1 to nset.numObjects do (
            local obj = getObject nset s_i
            if (superClassOf obj) == NURBSSurface do ( surf = obj; exit )
        )
        if surf != undefined do (
            local u = surf.uParameterRangeMin + (surf.uParameterRangeMax - surf.uParameterRangeMin) * 0.5
            local v = surf.vParameterRangeMin + (surf.vParameterRangeMax - surf.vParameterRangeMin) * 1
            p = evalPos surf u v
        )
        local bMin = nd.min
        local bMax = nd.max
        local modCount = nd.modifiers.count
        local isHidden = (nd.isHidden as string)
        format "ROW observation_id=% check_id=% target_id=% sample_id=% status=OK exists=true isHidden=% pos=[%,%,%] min=[%,%,%] max=[%,%,%] modCount=%\n" \
            "O7bb47b8ca6ee3bacd980b8910e5a20dc9adf40af344e57097a80a95cf0996f6" "CHK_FORM_01" "TGT-001" "Sca27fff7c5b48f8b2e919e8b38a14eb92b5cfa21b2f742a34a592961220ba94" isHidden (p.x as string) (p.y as string) (p.z as string) \
            (bMin.x as string) (bMin.y as string) (bMin.z as string) (bMax.x as string) (bMax.y as string) (bMax.z as string) (modCount as string) to:__qa_out
    ) else (
        format "ROW observation_id=% check_id=% target_id=% sample_id=% status=NOT_FOUND exists=false\n" \
            "O7bb47b8ca6ee3bacd980b8910e5a20dc9adf40af344e57097a80a95cf0996f6" "CHK_FORM_01" "TGT-001" "Sca27fff7c5b48f8b2e919e8b38a14eb92b5cfa21b2f742a34a592961220ba94" to:__qa_out
    )
    -- Observation O4a6c7a6382ffeeca968c4c8feddefbb3b5d7b3986ff36c6e023c4897f89249c (CHK_FORM_01 grid/3/0)
    local nd = getNodeByName "SUR_001_Vault"
    if nd != undefined then (
        local p = nd.pos
        local nset = getNURBSSet nd #relational
        local surf = undefined
        for s_i = 1 to nset.numObjects do (
            local obj = getObject nset s_i
            if (superClassOf obj) == NURBSSurface do ( surf = obj; exit )
        )
        if surf != undefined do (
            local u = surf.uParameterRangeMin + (surf.uParameterRangeMax - surf.uParameterRangeMin) * 0.75
            local v = surf.vParameterRangeMin + (surf.vParameterRangeMax - surf.vParameterRangeMin) * 0
            p = evalPos surf u v
        )
        local bMin = nd.min
        local bMax = nd.max
        local modCount = nd.modifiers.count
        local isHidden = (nd.isHidden as string)
        format "ROW observation_id=% check_id=% target_id=% sample_id=% status=OK exists=true isHidden=% pos=[%,%,%] min=[%,%,%] max=[%,%,%] modCount=%\n" \
            "O4a6c7a6382ffeeca968c4c8feddefbb3b5d7b3986ff36c6e023c4897f89249c" "CHK_FORM_01" "TGT-001" "S74d32c149cd732b342c8d50f39f82aef67328d68e2970caebe2b40043deb2b4" isHidden (p.x as string) (p.y as string) (p.z as string) \
            (bMin.x as string) (bMin.y as string) (bMin.z as string) (bMax.x as string) (bMax.y as string) (bMax.z as string) (modCount as string) to:__qa_out
    ) else (
        format "ROW observation_id=% check_id=% target_id=% sample_id=% status=NOT_FOUND exists=false\n" \
            "O4a6c7a6382ffeeca968c4c8feddefbb3b5d7b3986ff36c6e023c4897f89249c" "CHK_FORM_01" "TGT-001" "S74d32c149cd732b342c8d50f39f82aef67328d68e2970caebe2b40043deb2b4" to:__qa_out
    )
    -- Observation O17ff69a9124753e35e0f86a228ec234784a95e78624aaee014efeb966a1c56b (CHK_FORM_01 grid/3/1)
    local nd = getNodeByName "SUR_001_Vault"
    if nd != undefined then (
        local p = nd.pos
        local nset = getNURBSSet nd #relational
        local surf = undefined
        for s_i = 1 to nset.numObjects do (
            local obj = getObject nset s_i
            if (superClassOf obj) == NURBSSurface do ( surf = obj; exit )
        )
        if surf != undefined do (
            local u = surf.uParameterRangeMin + (surf.uParameterRangeMax - surf.uParameterRangeMin) * 0.75
            local v = surf.vParameterRangeMin + (surf.vParameterRangeMax - surf.vParameterRangeMin) * 0.25
            p = evalPos surf u v
        )
        local bMin = nd.min
        local bMax = nd.max
        local modCount = nd.modifiers.count
        local isHidden = (nd.isHidden as string)
        format "ROW observation_id=% check_id=% target_id=% sample_id=% status=OK exists=true isHidden=% pos=[%,%,%] min=[%,%,%] max=[%,%,%] modCount=%\n" \
            "O17ff69a9124753e35e0f86a228ec234784a95e78624aaee014efeb966a1c56b" "CHK_FORM_01" "TGT-001" "S3e52108bb82aa549fa7633ef6f5302ee196b9bf0b2773bec8da9bd72b430f8b" isHidden (p.x as string) (p.y as string) (p.z as string) \
            (bMin.x as string) (bMin.y as string) (bMin.z as string) (bMax.x as string) (bMax.y as string) (bMax.z as string) (modCount as string) to:__qa_out
    ) else (
        format "ROW observation_id=% check_id=% target_id=% sample_id=% status=NOT_FOUND exists=false\n" \
            "O17ff69a9124753e35e0f86a228ec234784a95e78624aaee014efeb966a1c56b" "CHK_FORM_01" "TGT-001" "S3e52108bb82aa549fa7633ef6f5302ee196b9bf0b2773bec8da9bd72b430f8b" to:__qa_out
    )
    -- Observation Oe99577f9459654b7201b34cee576ac92ae9a20be7b1efac2a00f281ed12fcaa (CHK_FORM_01 grid/3/2)
    local nd = getNodeByName "SUR_001_Vault"
    if nd != undefined then (
        local p = nd.pos
        local nset = getNURBSSet nd #relational
        local surf = undefined
        for s_i = 1 to nset.numObjects do (
            local obj = getObject nset s_i
            if (superClassOf obj) == NURBSSurface do ( surf = obj; exit )
        )
        if surf != undefined do (
            local u = surf.uParameterRangeMin + (surf.uParameterRangeMax - surf.uParameterRangeMin) * 0.75
            local v = surf.vParameterRangeMin + (surf.vParameterRangeMax - surf.vParameterRangeMin) * 0.5
            p = evalPos surf u v
        )
        local bMin = nd.min
        local bMax = nd.max
        local modCount = nd.modifiers.count
        local isHidden = (nd.isHidden as string)
        format "ROW observation_id=% check_id=% target_id=% sample_id=% status=OK exists=true isHidden=% pos=[%,%,%] min=[%,%,%] max=[%,%,%] modCount=%\n" \
            "Oe99577f9459654b7201b34cee576ac92ae9a20be7b1efac2a00f281ed12fcaa" "CHK_FORM_01" "TGT-001" "S99658d295805b21a8ca1f7f2ae531c9f6a8f61a679cf349bfe94af75d1a5e39" isHidden (p.x as string) (p.y as string) (p.z as string) \
            (bMin.x as string) (bMin.y as string) (bMin.z as string) (bMax.x as string) (bMax.y as string) (bMax.z as string) (modCount as string) to:__qa_out
    ) else (
        format "ROW observation_id=% check_id=% target_id=% sample_id=% status=NOT_FOUND exists=false\n" \
            "Oe99577f9459654b7201b34cee576ac92ae9a20be7b1efac2a00f281ed12fcaa" "CHK_FORM_01" "TGT-001" "S99658d295805b21a8ca1f7f2ae531c9f6a8f61a679cf349bfe94af75d1a5e39" to:__qa_out
    )
    -- Observation O37636961cf36ae5a33d279efffe0a66a02db63b7050462ebf11963b7a787d96 (CHK_FORM_01 grid/3/3)
    local nd = getNodeByName "SUR_001_Vault"
    if nd != undefined then (
        local p = nd.pos
        local nset = getNURBSSet nd #relational
        local surf = undefined
        for s_i = 1 to nset.numObjects do (
            local obj = getObject nset s_i
            if (superClassOf obj) == NURBSSurface do ( surf = obj; exit )
        )
        if surf != undefined do (
            local u = surf.uParameterRangeMin + (surf.uParameterRangeMax - surf.uParameterRangeMin) * 0.75
            local v = surf.vParameterRangeMin + (surf.vParameterRangeMax - surf.vParameterRangeMin) * 0.75
            p = evalPos surf u v
        )
        local bMin = nd.min
        local bMax = nd.max
        local modCount = nd.modifiers.count
        local isHidden = (nd.isHidden as string)
        format "ROW observation_id=% check_id=% target_id=% sample_id=% status=OK exists=true isHidden=% pos=[%,%,%] min=[%,%,%] max=[%,%,%] modCount=%\n" \
            "O37636961cf36ae5a33d279efffe0a66a02db63b7050462ebf11963b7a787d96" "CHK_FORM_01" "TGT-001" "S95e2ee180cd39abc1a5643b43cc1cc587a243244646604fac85c6d8ed1b6476" isHidden (p.x as string) (p.y as string) (p.z as string) \
            (bMin.x as string) (bMin.y as string) (bMin.z as string) (bMax.x as string) (bMax.y as string) (bMax.z as string) (modCount as string) to:__qa_out
    ) else (
        format "ROW observation_id=% check_id=% target_id=% sample_id=% status=NOT_FOUND exists=false\n" \
            "O37636961cf36ae5a33d279efffe0a66a02db63b7050462ebf11963b7a787d96" "CHK_FORM_01" "TGT-001" "S95e2ee180cd39abc1a5643b43cc1cc587a243244646604fac85c6d8ed1b6476" to:__qa_out
    )
    -- Observation Obcb46c39770bae6b59db73c94a9679d78ca21ccba639ecc7e688a299b0f1c82 (CHK_FORM_01 grid/3/4)
    local nd = getNodeByName "SUR_001_Vault"
    if nd != undefined then (
        local p = nd.pos
        local nset = getNURBSSet nd #relational
        local surf = undefined
        for s_i = 1 to nset.numObjects do (
            local obj = getObject nset s_i
            if (superClassOf obj) == NURBSSurface do ( surf = obj; exit )
        )
        if surf != undefined do (
            local u = surf.uParameterRangeMin + (surf.uParameterRangeMax - surf.uParameterRangeMin) * 0.75
            local v = surf.vParameterRangeMin + (surf.vParameterRangeMax - surf.vParameterRangeMin) * 1
            p = evalPos surf u v
        )
        local bMin = nd.min
        local bMax = nd.max
        local modCount = nd.modifiers.count
        local isHidden = (nd.isHidden as string)
        format "ROW observation_id=% check_id=% target_id=% sample_id=% status=OK exists=true isHidden=% pos=[%,%,%] min=[%,%,%] max=[%,%,%] modCount=%\n" \
            "Obcb46c39770bae6b59db73c94a9679d78ca21ccba639ecc7e688a299b0f1c82" "CHK_FORM_01" "TGT-001" "Sa7ed7c80db26396364bec4be02d3905e9ab4671883f8f25b6fba7c00d183cd8" isHidden (p.x as string) (p.y as string) (p.z as string) \
            (bMin.x as string) (bMin.y as string) (bMin.z as string) (bMax.x as string) (bMax.y as string) (bMax.z as string) (modCount as string) to:__qa_out
    ) else (
        format "ROW observation_id=% check_id=% target_id=% sample_id=% status=NOT_FOUND exists=false\n" \
            "Obcb46c39770bae6b59db73c94a9679d78ca21ccba639ecc7e688a299b0f1c82" "CHK_FORM_01" "TGT-001" "Sa7ed7c80db26396364bec4be02d3905e9ab4671883f8f25b6fba7c00d183cd8" to:__qa_out
    )
    -- Observation Ofd85417e1b77cb2af0145f6c11ac41acd81ba3756b1df582796507eefe20f96 (CHK_FORM_01 grid/4/0)
    local nd = getNodeByName "SUR_001_Vault"
    if nd != undefined then (
        local p = nd.pos
        local nset = getNURBSSet nd #relational
        local surf = undefined
        for s_i = 1 to nset.numObjects do (
            local obj = getObject nset s_i
            if (superClassOf obj) == NURBSSurface do ( surf = obj; exit )
        )
        if surf != undefined do (
            local u = surf.uParameterRangeMin + (surf.uParameterRangeMax - surf.uParameterRangeMin) * 1
            local v = surf.vParameterRangeMin + (surf.vParameterRangeMax - surf.vParameterRangeMin) * 0
            p = evalPos surf u v
        )
        local bMin = nd.min
        local bMax = nd.max
        local modCount = nd.modifiers.count
        local isHidden = (nd.isHidden as string)
        format "ROW observation_id=% check_id=% target_id=% sample_id=% status=OK exists=true isHidden=% pos=[%,%,%] min=[%,%,%] max=[%,%,%] modCount=%\n" \
            "Ofd85417e1b77cb2af0145f6c11ac41acd81ba3756b1df582796507eefe20f96" "CHK_FORM_01" "TGT-001" "S0d5c23dc5b5bc89c7ba6073b9043aebed014fa7d11e798f4bc6a8e096e6aa05" isHidden (p.x as string) (p.y as string) (p.z as string) \
            (bMin.x as string) (bMin.y as string) (bMin.z as string) (bMax.x as string) (bMax.y as string) (bMax.z as string) (modCount as string) to:__qa_out
    ) else (
        format "ROW observation_id=% check_id=% target_id=% sample_id=% status=NOT_FOUND exists=false\n" \
            "Ofd85417e1b77cb2af0145f6c11ac41acd81ba3756b1df582796507eefe20f96" "CHK_FORM_01" "TGT-001" "S0d5c23dc5b5bc89c7ba6073b9043aebed014fa7d11e798f4bc6a8e096e6aa05" to:__qa_out
    )
    -- Observation O610d5dde41f1658e4edc265032d949b9de617bb01ac15ae044d20d6e76b4165 (CHK_FORM_01 grid/4/1)
    local nd = getNodeByName "SUR_001_Vault"
    if nd != undefined then (
        local p = nd.pos
        local nset = getNURBSSet nd #relational
        local surf = undefined
        for s_i = 1 to nset.numObjects do (
            local obj = getObject nset s_i
            if (superClassOf obj) == NURBSSurface do ( surf = obj; exit )
        )
        if surf != undefined do (
            local u = surf.uParameterRangeMin + (surf.uParameterRangeMax - surf.uParameterRangeMin) * 1
            local v = surf.vParameterRangeMin + (surf.vParameterRangeMax - surf.vParameterRangeMin) * 0.25
            p = evalPos surf u v
        )
        local bMin = nd.min
        local bMax = nd.max
        local modCount = nd.modifiers.count
        local isHidden = (nd.isHidden as string)
        format "ROW observation_id=% check_id=% target_id=% sample_id=% status=OK exists=true isHidden=% pos=[%,%,%] min=[%,%,%] max=[%,%,%] modCount=%\n" \
            "O610d5dde41f1658e4edc265032d949b9de617bb01ac15ae044d20d6e76b4165" "CHK_FORM_01" "TGT-001" "S5ccbbfa99923f9f7053f90256e960ec15390e7ebae8d69414f1893f316a0f2d" isHidden (p.x as string) (p.y as string) (p.z as string) \
            (bMin.x as string) (bMin.y as string) (bMin.z as string) (bMax.x as string) (bMax.y as string) (bMax.z as string) (modCount as string) to:__qa_out
    ) else (
        format "ROW observation_id=% check_id=% target_id=% sample_id=% status=NOT_FOUND exists=false\n" \
            "O610d5dde41f1658e4edc265032d949b9de617bb01ac15ae044d20d6e76b4165" "CHK_FORM_01" "TGT-001" "S5ccbbfa99923f9f7053f90256e960ec15390e7ebae8d69414f1893f316a0f2d" to:__qa_out
    )
    -- Observation Oa21f2e009ceb1f210a82988e6f715a43f106c640b8d9a69e2883179962352a2 (CHK_FORM_01 grid/4/2)
    local nd = getNodeByName "SUR_001_Vault"
    if nd != undefined then (
        local p = nd.pos
        local nset = getNURBSSet nd #relational
        local surf = undefined
        for s_i = 1 to nset.numObjects do (
            local obj = getObject nset s_i
            if (superClassOf obj) == NURBSSurface do ( surf = obj; exit )
        )
        if surf != undefined do (
            local u = surf.uParameterRangeMin + (surf.uParameterRangeMax - surf.uParameterRangeMin) * 1
            local v = surf.vParameterRangeMin + (surf.vParameterRangeMax - surf.vParameterRangeMin) * 0.5
            p = evalPos surf u v
        )
        local bMin = nd.min
        local bMax = nd.max
        local modCount = nd.modifiers.count
        local isHidden = (nd.isHidden as string)
        format "ROW observation_id=% check_id=% target_id=% sample_id=% status=OK exists=true isHidden=% pos=[%,%,%] min=[%,%,%] max=[%,%,%] modCount=%\n" \
            "Oa21f2e009ceb1f210a82988e6f715a43f106c640b8d9a69e2883179962352a2" "CHK_FORM_01" "TGT-001" "Sfdd5519da7eb0503fb7ec9e741acb2a0bdeea09ac7dfb1df40a1124bb4eabf7" isHidden (p.x as string) (p.y as string) (p.z as string) \
            (bMin.x as string) (bMin.y as string) (bMin.z as string) (bMax.x as string) (bMax.y as string) (bMax.z as string) (modCount as string) to:__qa_out
    ) else (
        format "ROW observation_id=% check_id=% target_id=% sample_id=% status=NOT_FOUND exists=false\n" \
            "Oa21f2e009ceb1f210a82988e6f715a43f106c640b8d9a69e2883179962352a2" "CHK_FORM_01" "TGT-001" "Sfdd5519da7eb0503fb7ec9e741acb2a0bdeea09ac7dfb1df40a1124bb4eabf7" to:__qa_out
    )
    -- Observation O268ff168877cd392e643c21a51a282d3e06d297c9c04aeb9ffbb0d7a5534ed6 (CHK_FORM_01 grid/4/3)
    local nd = getNodeByName "SUR_001_Vault"
    if nd != undefined then (
        local p = nd.pos
        local nset = getNURBSSet nd #relational
        local surf = undefined
        for s_i = 1 to nset.numObjects do (
            local obj = getObject nset s_i
            if (superClassOf obj) == NURBSSurface do ( surf = obj; exit )
        )
        if surf != undefined do (
            local u = surf.uParameterRangeMin + (surf.uParameterRangeMax - surf.uParameterRangeMin) * 1
            local v = surf.vParameterRangeMin + (surf.vParameterRangeMax - surf.vParameterRangeMin) * 0.75
            p = evalPos surf u v
        )
        local bMin = nd.min
        local bMax = nd.max
        local modCount = nd.modifiers.count
        local isHidden = (nd.isHidden as string)
        format "ROW observation_id=% check_id=% target_id=% sample_id=% status=OK exists=true isHidden=% pos=[%,%,%] min=[%,%,%] max=[%,%,%] modCount=%\n" \
            "O268ff168877cd392e643c21a51a282d3e06d297c9c04aeb9ffbb0d7a5534ed6" "CHK_FORM_01" "TGT-001" "S1db610a130ec9d8a7404d008d9960e3346cf378fd86a764c52e16381b90f2d2" isHidden (p.x as string) (p.y as string) (p.z as string) \
            (bMin.x as string) (bMin.y as string) (bMin.z as string) (bMax.x as string) (bMax.y as string) (bMax.z as string) (modCount as string) to:__qa_out
    ) else (
        format "ROW observation_id=% check_id=% target_id=% sample_id=% status=NOT_FOUND exists=false\n" \
            "O268ff168877cd392e643c21a51a282d3e06d297c9c04aeb9ffbb0d7a5534ed6" "CHK_FORM_01" "TGT-001" "S1db610a130ec9d8a7404d008d9960e3346cf378fd86a764c52e16381b90f2d2" to:__qa_out
    )
    -- Observation O07f3849ce95c1df1d7690844c8b2e3dab4bb8cc6c23c979ffe3d19827611f54 (CHK_FORM_01 grid/4/4)
    local nd = getNodeByName "SUR_001_Vault"
    if nd != undefined then (
        local p = nd.pos
        local nset = getNURBSSet nd #relational
        local surf = undefined
        for s_i = 1 to nset.numObjects do (
            local obj = getObject nset s_i
            if (superClassOf obj) == NURBSSurface do ( surf = obj; exit )
        )
        if surf != undefined do (
            local u = surf.uParameterRangeMin + (surf.uParameterRangeMax - surf.uParameterRangeMin) * 1
            local v = surf.vParameterRangeMin + (surf.vParameterRangeMax - surf.vParameterRangeMin) * 1
            p = evalPos surf u v
        )
        local bMin = nd.min
        local bMax = nd.max
        local modCount = nd.modifiers.count
        local isHidden = (nd.isHidden as string)
        format "ROW observation_id=% check_id=% target_id=% sample_id=% status=OK exists=true isHidden=% pos=[%,%,%] min=[%,%,%] max=[%,%,%] modCount=%\n" \
            "O07f3849ce95c1df1d7690844c8b2e3dab4bb8cc6c23c979ffe3d19827611f54" "CHK_FORM_01" "TGT-001" "Sc8bd4aaf6964d777f796b2fa1cada2ec059d058eeb37c8e4190c496bc06b018" isHidden (p.x as string) (p.y as string) (p.z as string) \
            (bMin.x as string) (bMin.y as string) (bMin.z as string) (bMax.x as string) (bMax.y as string) (bMax.z as string) (modCount as string) to:__qa_out
    ) else (
        format "ROW observation_id=% check_id=% target_id=% sample_id=% status=NOT_FOUND exists=false\n" \
            "O07f3849ce95c1df1d7690844c8b2e3dab4bb8cc6c23c979ffe3d19827611f54" "CHK_FORM_01" "TGT-001" "Sc8bd4aaf6964d777f796b2fa1cada2ec059d058eeb37c8e4190c496bc06b018" to:__qa_out
    )
    format "END_BATCH batch_id=% rows=%\n" "batch_001" 25 to:__qa_out
    __qa_out as string
)
