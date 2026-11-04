-- Main-only bounded controller/dependency/Shell reader calibration.
-- One exact disposable Box + one Shell; not production replay acceptance.
(
    local n = undefined
    local h = undefined
    local shellMod = undefined
    local shellHandle = undefined
    local made = false
    local cleanupOK = false
    local output = "P3_CONTROLLER_GRAPH"
    local beforeDirty = getSaveRequired()
    fn p3Text value =
    (
        local t = "<not-stringifiable>"
        try (t = value as string) catch ()
        t
    )
    fn p3Read label =
    (
        local value = undefined
        local threw = false
        local errorText = ""
        try
        (
            value = case label of
            (
                "visibility.controller": getPropertyController n #visibility
                "node.numSubs": n.numSubs
                "node.subNames": getSubAnimNames n
                "shell.numSubs": shellMod.numSubs
                "shell.subNames": getSubAnimNames shellMod
                "node.refsCount": refs.getNumRefs n
                "base.refsCount": refs.getNumRefs n.baseObject
                "shell.refsCount": refs.getNumRefs shellMod
                "node.dependents": refs.dependents n
                "base.dependents": refs.dependents n.baseObject
                "shell.dependents": refs.dependents shellMod
            )
        ) catch (threw = true; errorText = getCurrentException() as string)
        output += "|" + label + ";threw=" + (threw as string) + ";class=" + ((classOf value) as string) + ";value=" + (p3Text value) + ";error=" + errorText
        value
    )
    fn p3Controller label =
    (
        local c = undefined
        local threw = false
        local errorText = ""
        try
        (
            c = case label of
            (
                "node.controller": n.controller
                "position.controller": n.position.controller
                "rotation.controller": n.rotation.controller
                "scale.controller": n.scale.controller
                "shell.outerAmount.controller": shellMod.outerAmount.controller
                "shell.innerAmount.controller": shellMod.innerAmount.controller
            )
        ) catch (threw = true; errorText = getCurrentException() as string)
        output += "|" + label + ";threw=" + (threw as string) + ";class=" + ((classOf c) as string) + ";value=" + (p3Text c) + ";error=" + errorText
        c
    )
    try
    (
        if objects.count != 0 or selection.count != 0 or maxFilePath != "" or maxFileName != "" do throw "scene admission failed"
        if units.SystemType != #millimeters or units.SystemScale != 1.0 do throw "units mismatch"
        n = Box width:10.0 length:20.0 height:30.0 pos:[0,0,0]
        made = true
        h = getHandleByAnim n
        if h == undefined or not isValidNode n or (getAnimByHandle h) != n or objects.count != 1 do throw "node identity/census failed"
        shellMod = Shell innerAmount:0.0 outerAmount:1.0 segments:1
        addModifier n shellMod
        update n
        shellHandle = getHandleByAnim shellMod
        if shellHandle == undefined or (getAnimByHandle shellHandle) != shellMod or n.modifiers.count != 1 or n.modifiers[1] != shellMod do throw "Shell identity failed"
        output += "|setup;nodeHandle=" + (h as string) + ";shellHandle=" + (shellHandle as string) + ";baseClass=" + ((classOf n.baseObject) as string) + ";objects=" + (objects.count as string)
        p3Controller "node.controller"
        p3Controller "position.controller"
        p3Controller "rotation.controller"
        p3Controller "scale.controller"
        p3Read "visibility.controller"
        p3Read "node.numSubs"
        p3Read "node.subNames"
        local nodeSubs = undefined
        try (nodeSubs = n.numSubs) catch ()
        if nodeSubs != undefined and nodeSubs >= 0 and nodeSubs <= 64 do
        (
            for i = 1 to nodeSubs do
            (
                local sub = undefined
                local failed = false
                local err = ""
                try (sub = getSubAnim n i) catch (failed = true; err = getCurrentException() as string)
                output += "|node.sub[" + (i as string) + "];threw=" + (failed as string) + ";class=" + ((classOf sub) as string) + ";value=" + (p3Text sub) + ";error=" + err
                if not failed and sub != undefined do
                (
                    local subKeys = undefined
                    local keyThrew = false
                    local keyError = ""
                    try (subKeys = numKeys sub) catch (keyThrew = true; keyError = getCurrentException() as string)
                    output += "|node.sub[" + (i as string) + "].numKeys;threw=" + (keyThrew as string) + ";class=" + ((classOf subKeys) as string) + ";value=" + (p3Text subKeys) + ";error=" + keyError
                )
            )
        )
        p3Controller "shell.outerAmount.controller"
        p3Controller "shell.innerAmount.controller"
        p3Read "shell.numSubs"
        p3Read "shell.subNames"
        p3Read "node.refsCount"
        p3Read "base.refsCount"
        p3Read "shell.refsCount"
        p3Read "node.dependents"
        p3Read "base.dependents"
        p3Read "shell.dependents"
        local shellNames = getPropNames shellMod
        if shellNames == undefined or shellNames.count > 128 do throw "Shell property enumeration unavailable/over limit"
        output += "|shell.propertyCount=" + (shellNames.count as string)
        for p in shellNames do
        (
            local v = undefined
            local failed = false
            local err = ""
            try (v = getProperty shellMod p) catch (failed = true; err = getCurrentException() as string)
            output += "|shell.property=" + (p as string) + ";threw=" + (failed as string) + ";class=" + ((classOf v) as string) + ";value=" + (p3Text v) + ";error=" + err
        )
        local bogusPresent = isProperty shellMod #P3BogusShellPropertyA17
        local bogusThrew = false
        try (getProperty shellMod #P3BogusShellPropertyA17) catch (bogusThrew = true)
        output += "|shell.bogus;present=" + (bogusPresent as string) + ";threw=" + (bogusThrew as string)
    )
    catch (output += "|ERROR=" + ((getCurrentException()) as string))
    try
    (
        if made then
        (
            if n == undefined or h == undefined or not isValidNode n do throw "lost exact node"
            if (getHandleByAnim n) != h or (getAnimByHandle h) != n or objects.count != 1 or selection.count != 0 do throw "cleanup identity/census mismatch"
            if shellMod == undefined or shellHandle == undefined do throw "lost exact Shell"
            if (getHandleByAnim shellMod) != shellHandle or (getAnimByHandle shellHandle) != shellMod or n.modifiers.count != 1 or n.modifiers[1] != shellMod do throw "Shell cleanup identity mismatch"
            if n.children.count != 0 or (n.parent != undefined and n.parent != rootNode) do throw "unexpected node hierarchy"
            local users = for other in objects where other.baseObject == n.baseObject collect other
            if users.count != 1 or users[1] != n do throw "unexpected base sharing"
            delete n
            if isValidNode n or objects.count != 0 do throw "exact node removal not observed"
        )
        else if objects.count != 0 do throw "constructor outcome/census ambiguous"
        cleanupOK = true
    )
    catch (output += "|CLEANUP_ERROR=" + ((getCurrentException()) as string))
    if not cleanupOK do output += "|outcome=INCOMPLETE_RESIDUE_OR_IDENTITY"
    else output += "|outcome=BOUNDED_CONTROLLER_DEPENDENCY_OBSERVED_NOT_ACCEPTANCE"
    output += "|cleanup=" + (cleanupOK as string) + "|objects=" + (objects.count as string) + "|selection=" + (selection.count as string) + "|dirtyBefore=" + (beforeDirty as string) + "|dirtyAfter=" + ((getSaveRequired()) as string)
    output
)
