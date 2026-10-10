-- Batch batch_002 for QA run live-run-001
(
    local __qa_out = stringStream ""
    format "START_BATCH batch_id=%\n" "batch_002" to:__qa_out
    local sysType = (units.SystemType as string)
    local sysScale = (units.SystemScale as string)
    format "GUARD units.SystemType=% units.SystemScale=%\n" sysType sysScale to:__qa_out
    -- Observation O3d9fa4c3adbc0da3deace44993990265a67e9d00f0a1a28688db4f7d0d2d74f (CHK_FORM_01 station/first/left)
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
            "O3d9fa4c3adbc0da3deace44993990265a67e9d00f0a1a28688db4f7d0d2d74f" "CHK_FORM_01" "TGT-001" "S4532bd751923417106eda8c5b532aa04946dbb3c33b89bb08bae7d1facee7f3" isHidden (p.x as string) (p.y as string) (p.z as string) \
            (bMin.x as string) (bMin.y as string) (bMin.z as string) (bMax.x as string) (bMax.y as string) (bMax.z as string) (modCount as string) to:__qa_out
    ) else (
        format "ROW observation_id=% check_id=% target_id=% sample_id=% status=NOT_FOUND exists=false\n" \
            "O3d9fa4c3adbc0da3deace44993990265a67e9d00f0a1a28688db4f7d0d2d74f" "CHK_FORM_01" "TGT-001" "S4532bd751923417106eda8c5b532aa04946dbb3c33b89bb08bae7d1facee7f3" to:__qa_out
    )
    -- Observation Oa523eefbd3179fa2241bf091b6eb25bf48003859287f04a9382060c93a4676c (CHK_FORM_01 station/first/crown)
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
            "Oa523eefbd3179fa2241bf091b6eb25bf48003859287f04a9382060c93a4676c" "CHK_FORM_01" "TGT-001" "Sca452ab8c7f52b50f54a3c57432fcf7c37f39ee5c35d691152982246871a444" isHidden (p.x as string) (p.y as string) (p.z as string) \
            (bMin.x as string) (bMin.y as string) (bMin.z as string) (bMax.x as string) (bMax.y as string) (bMax.z as string) (modCount as string) to:__qa_out
    ) else (
        format "ROW observation_id=% check_id=% target_id=% sample_id=% status=NOT_FOUND exists=false\n" \
            "Oa523eefbd3179fa2241bf091b6eb25bf48003859287f04a9382060c93a4676c" "CHK_FORM_01" "TGT-001" "Sca452ab8c7f52b50f54a3c57432fcf7c37f39ee5c35d691152982246871a444" to:__qa_out
    )
    -- Observation Oce500f8261ad0db8c4b71cf6d1779232b7acafa34b4bb39ebc64b723945bd29 (CHK_FORM_01 station/first/right)
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
            "Oce500f8261ad0db8c4b71cf6d1779232b7acafa34b4bb39ebc64b723945bd29" "CHK_FORM_01" "TGT-001" "S0aa01fb899abf8cc0b0139f28143ac8b3b9a22d0b65422be1bdc1e1a5dc6ca5" isHidden (p.x as string) (p.y as string) (p.z as string) \
            (bMin.x as string) (bMin.y as string) (bMin.z as string) (bMax.x as string) (bMax.y as string) (bMax.z as string) (modCount as string) to:__qa_out
    ) else (
        format "ROW observation_id=% check_id=% target_id=% sample_id=% status=NOT_FOUND exists=false\n" \
            "Oce500f8261ad0db8c4b71cf6d1779232b7acafa34b4bb39ebc64b723945bd29" "CHK_FORM_01" "TGT-001" "S0aa01fb899abf8cc0b0139f28143ac8b3b9a22d0b65422be1bdc1e1a5dc6ca5" to:__qa_out
    )
    -- Observation Oeb6094a266f7eccab0577f37550719508a455f80c5283b3d1f6070acdfe2440 (CHK_FORM_01 station/middle/left)
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
            "Oeb6094a266f7eccab0577f37550719508a455f80c5283b3d1f6070acdfe2440" "CHK_FORM_01" "TGT-001" "Se89dc7426392e703c617a64af734a4f1e6f98d8a22af26628d0b7ae37823c48" isHidden (p.x as string) (p.y as string) (p.z as string) \
            (bMin.x as string) (bMin.y as string) (bMin.z as string) (bMax.x as string) (bMax.y as string) (bMax.z as string) (modCount as string) to:__qa_out
    ) else (
        format "ROW observation_id=% check_id=% target_id=% sample_id=% status=NOT_FOUND exists=false\n" \
            "Oeb6094a266f7eccab0577f37550719508a455f80c5283b3d1f6070acdfe2440" "CHK_FORM_01" "TGT-001" "Se89dc7426392e703c617a64af734a4f1e6f98d8a22af26628d0b7ae37823c48" to:__qa_out
    )
    -- Observation Oaa7c39b7cc285f1cba59d3c4e84be3ab04df7ffc0e799c7929fb9bb33414d2e (CHK_FORM_01 station/middle/crown)
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
            "Oaa7c39b7cc285f1cba59d3c4e84be3ab04df7ffc0e799c7929fb9bb33414d2e" "CHK_FORM_01" "TGT-001" "Sa6f3d6d594dac02e442e0fd653468c362496110d978208b43855e7204be4ada" isHidden (p.x as string) (p.y as string) (p.z as string) \
            (bMin.x as string) (bMin.y as string) (bMin.z as string) (bMax.x as string) (bMax.y as string) (bMax.z as string) (modCount as string) to:__qa_out
    ) else (
        format "ROW observation_id=% check_id=% target_id=% sample_id=% status=NOT_FOUND exists=false\n" \
            "Oaa7c39b7cc285f1cba59d3c4e84be3ab04df7ffc0e799c7929fb9bb33414d2e" "CHK_FORM_01" "TGT-001" "Sa6f3d6d594dac02e442e0fd653468c362496110d978208b43855e7204be4ada" to:__qa_out
    )
    -- Observation Ofce2496aca8782e8513e4bb64b50842ff31b5921ff12a3cc1f678971584c134 (CHK_FORM_01 station/middle/right)
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
            "Ofce2496aca8782e8513e4bb64b50842ff31b5921ff12a3cc1f678971584c134" "CHK_FORM_01" "TGT-001" "S52e284e4ec1463d66b819dab11d2f982014a7bc9926bdb191f370b8d7803567" isHidden (p.x as string) (p.y as string) (p.z as string) \
            (bMin.x as string) (bMin.y as string) (bMin.z as string) (bMax.x as string) (bMax.y as string) (bMax.z as string) (modCount as string) to:__qa_out
    ) else (
        format "ROW observation_id=% check_id=% target_id=% sample_id=% status=NOT_FOUND exists=false\n" \
            "Ofce2496aca8782e8513e4bb64b50842ff31b5921ff12a3cc1f678971584c134" "CHK_FORM_01" "TGT-001" "S52e284e4ec1463d66b819dab11d2f982014a7bc9926bdb191f370b8d7803567" to:__qa_out
    )
    -- Observation O88ee685f644d2dc6592e0dd3456e02883d0c8879bbe7dadf182212ea49940c1 (CHK_FORM_01 station/last/left)
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
            "O88ee685f644d2dc6592e0dd3456e02883d0c8879bbe7dadf182212ea49940c1" "CHK_FORM_01" "TGT-001" "S2613cff1a2ca16df290cd7014f244530867e4887a6271500671c92e26333267" isHidden (p.x as string) (p.y as string) (p.z as string) \
            (bMin.x as string) (bMin.y as string) (bMin.z as string) (bMax.x as string) (bMax.y as string) (bMax.z as string) (modCount as string) to:__qa_out
    ) else (
        format "ROW observation_id=% check_id=% target_id=% sample_id=% status=NOT_FOUND exists=false\n" \
            "O88ee685f644d2dc6592e0dd3456e02883d0c8879bbe7dadf182212ea49940c1" "CHK_FORM_01" "TGT-001" "S2613cff1a2ca16df290cd7014f244530867e4887a6271500671c92e26333267" to:__qa_out
    )
    -- Observation O43031457d6da9d19762b4f8c0f804d03ebb09f9f6d38ab06be85a07cace7c9f (CHK_FORM_01 station/last/crown)
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
            "O43031457d6da9d19762b4f8c0f804d03ebb09f9f6d38ab06be85a07cace7c9f" "CHK_FORM_01" "TGT-001" "Se516a2671fad5d3c8a16653aea9ca9357b4086d0cd016e7f392d6fd24a7d164" isHidden (p.x as string) (p.y as string) (p.z as string) \
            (bMin.x as string) (bMin.y as string) (bMin.z as string) (bMax.x as string) (bMax.y as string) (bMax.z as string) (modCount as string) to:__qa_out
    ) else (
        format "ROW observation_id=% check_id=% target_id=% sample_id=% status=NOT_FOUND exists=false\n" \
            "O43031457d6da9d19762b4f8c0f804d03ebb09f9f6d38ab06be85a07cace7c9f" "CHK_FORM_01" "TGT-001" "Se516a2671fad5d3c8a16653aea9ca9357b4086d0cd016e7f392d6fd24a7d164" to:__qa_out
    )
    -- Observation O485ee22a60b4683b2eceb02f0816d2590fd772463ae755c94b83e33eac7918d (CHK_FORM_01 station/last/right)
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
            "O485ee22a60b4683b2eceb02f0816d2590fd772463ae755c94b83e33eac7918d" "CHK_FORM_01" "TGT-001" "S78824a0031f8c609f2e318942777063f730c4eaffdd42c038be88e5cf32e3b2" isHidden (p.x as string) (p.y as string) (p.z as string) \
            (bMin.x as string) (bMin.y as string) (bMin.z as string) (bMax.x as string) (bMax.y as string) (bMax.z as string) (modCount as string) to:__qa_out
    ) else (
        format "ROW observation_id=% check_id=% target_id=% sample_id=% status=NOT_FOUND exists=false\n" \
            "O485ee22a60b4683b2eceb02f0816d2590fd772463ae755c94b83e33eac7918d" "CHK_FORM_01" "TGT-001" "S78824a0031f8c609f2e318942777063f730c4eaffdd42c038be88e5cf32e3b2" to:__qa_out
    )
    -- Observation O11f742fa2f7aa3742de263ebb3b9a59f990b329b47fbc46ba8326f5c586df11 (CHK_FORM_01 endpoint/s0)
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
            "O11f742fa2f7aa3742de263ebb3b9a59f990b329b47fbc46ba8326f5c586df11" "CHK_FORM_01" "TGT-001" "S2a40a93cbf2bb0df417334fba01f25884585534bbb327c0f361e52f2a5a5f2f" isHidden (p.x as string) (p.y as string) (p.z as string) \
            (bMin.x as string) (bMin.y as string) (bMin.z as string) (bMax.x as string) (bMax.y as string) (bMax.z as string) (modCount as string) to:__qa_out
    ) else (
        format "ROW observation_id=% check_id=% target_id=% sample_id=% status=NOT_FOUND exists=false\n" \
            "O11f742fa2f7aa3742de263ebb3b9a59f990b329b47fbc46ba8326f5c586df11" "CHK_FORM_01" "TGT-001" "S2a40a93cbf2bb0df417334fba01f25884585534bbb327c0f361e52f2a5a5f2f" to:__qa_out
    )
    -- Observation O31283bb680dd16bba9ba9f1fb53a4976efabcdf46161b84e363380f910cf673 (CHK_FORM_01 endpoint/s1)
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
            "O31283bb680dd16bba9ba9f1fb53a4976efabcdf46161b84e363380f910cf673" "CHK_FORM_01" "TGT-001" "S4c4b6b13839e3995c3855b2d97f432887eed14326a770a368ce837b41929c30" isHidden (p.x as string) (p.y as string) (p.z as string) \
            (bMin.x as string) (bMin.y as string) (bMin.z as string) (bMax.x as string) (bMax.y as string) (bMax.z as string) (modCount as string) to:__qa_out
    ) else (
        format "ROW observation_id=% check_id=% target_id=% sample_id=% status=NOT_FOUND exists=false\n" \
            "O31283bb680dd16bba9ba9f1fb53a4976efabcdf46161b84e363380f910cf673" "CHK_FORM_01" "TGT-001" "S4c4b6b13839e3995c3855b2d97f432887eed14326a770a368ce837b41929c30" to:__qa_out
    )
    -- Observation O850fe36d952faac847cded819619e831d0405fa14a784eb1be4afd6f2306c10 (CHK_CENSUS_NURBS)
    local nd = getNodeByName "SUR_001_Vault"
    if nd != undefined then (
        local p = nd.pos
        local bMin = nd.min
        local bMax = nd.max
        local modCount = nd.modifiers.count
        local isHidden = (nd.isHidden as string)
        format "ROW observation_id=% check_id=% target_id=% sample_id=% status=OK exists=true isHidden=% pos=[%,%,%] min=[%,%,%] max=[%,%,%] modCount=%\n" \
            "O850fe36d952faac847cded819619e831d0405fa14a784eb1be4afd6f2306c10" "CHK_CENSUS_NURBS" "TGT-001" "S2a9ab830884cbe712525a2035f6c01a4b18ae7d9cdf1a7eef316d2cf8762164" isHidden (p.x as string) (p.y as string) (p.z as string) \
            (bMin.x as string) (bMin.y as string) (bMin.z as string) (bMax.x as string) (bMax.y as string) (bMax.z as string) (modCount as string) to:__qa_out
    ) else (
        format "ROW observation_id=% check_id=% target_id=% sample_id=% status=NOT_FOUND exists=false\n" \
            "O850fe36d952faac847cded819619e831d0405fa14a784eb1be4afd6f2306c10" "CHK_CENSUS_NURBS" "TGT-001" "S2a9ab830884cbe712525a2035f6c01a4b18ae7d9cdf1a7eef316d2cf8762164" to:__qa_out
    )
    -- Observation Ob178856d0a3c9d037289b0ee6b9a908a3c8cb3b5de0579355e7171e20caad25 (CHK_CENSUS_MASS)
    local nd = getNodeByName "EL_001"
    if nd != undefined then (
        local p = nd.pos
        local bMin = nd.min
        local bMax = nd.max
        local modCount = nd.modifiers.count
        local isHidden = (nd.isHidden as string)
        format "ROW observation_id=% check_id=% target_id=% sample_id=% status=OK exists=true isHidden=% pos=[%,%,%] min=[%,%,%] max=[%,%,%] modCount=%\n" \
            "Ob178856d0a3c9d037289b0ee6b9a908a3c8cb3b5de0579355e7171e20caad25" "CHK_CENSUS_MASS" "TGT_MASSING_01" "Sa9227d515b86e53dccec4cfb70d55112405c15b518c1836ed6c10c1679f53ec" isHidden (p.x as string) (p.y as string) (p.z as string) \
            (bMin.x as string) (bMin.y as string) (bMin.z as string) (bMax.x as string) (bMax.y as string) (bMax.z as string) (modCount as string) to:__qa_out
    ) else (
        format "ROW observation_id=% check_id=% target_id=% sample_id=% status=NOT_FOUND exists=false\n" \
            "Ob178856d0a3c9d037289b0ee6b9a908a3c8cb3b5de0579355e7171e20caad25" "CHK_CENSUS_MASS" "TGT_MASSING_01" "Sa9227d515b86e53dccec4cfb70d55112405c15b518c1836ed6c10c1679f53ec" to:__qa_out
    )
    format "END_BATCH batch_id=% rows=%\n" "batch_002" 13 to:__qa_out
    __qa_out as string
)
