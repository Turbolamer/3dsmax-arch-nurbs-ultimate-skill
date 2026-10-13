/*  ============================================================================
    snippets/sync_proto_materials.ms
    Prototype-to-Instance Material Synchronization for 3ds Max 2026 + cl0nazepamm/3dsmax-mcp

    PURPOSE & ARCHITECTURE (SKILL.md §5.1, agents/max-orchestrator.md §5.1-§5.2)
    ----------------------------------------------------------------------------
    * In 3ds Max, instance nodes (PLC_*) sharing baseObject with prototype
      nodes (PROTO_*) do NOT automatically inherit materials assigned to
      prototypes via the Material Editor UI.
    * Base object sharing (n.baseObject = proto.baseObject) shares geometric
      data in memory, but material references are stored at the node level.
    * This script scans all PROTO_* nodes with assigned materials, locates all
      scene objects sharing their exact baseObject, and synchronizes the
      material reference in milliseconds (~5 ms for 136 instances).
    * Retains G-81 compliance (0 modifiers) and preserves instance geometry.

    USAGE:
    ------
    fileIn "snippets/sync_proto_materials.ms"
    -- or call: syncProtoMaterials()
    ============================================================================
*/

fn syncProtoMaterials verbose:true =
(
    local protoCount = 0
    local syncedCount = 0
    local errorCount = 0

    try
    (
        -- Collect all prototype nodes with materials
        local protos = for o in objects where (matchPattern o.name pattern:"PROTO_*") and (o.material != undefined) collect o
        protoCount = protos.count

        for proto in protos do
        (
            local targetMat = proto.material
            local targetBase = proto.baseObject

            -- Find all instances sharing this baseObject
            for inst in objects where (inst != proto) and (inst.baseObject == targetBase) do
            (
                try
                (
                    if inst.material != targetMat do
                    (
                        inst.material = targetMat
                        syncedCount += 1
                    )
                )
                catch
                (
                    errorCount += 1
                    if verbose do
                    (
                        local err = getCurrentException()
                        format "ERROR syncing %: %\n" inst.name err
                    )
                )
            )
        )

        if verbose do
        (
            format "Material sync complete: % instances synchronized from % prototypes (% errors).\n" \
                syncedCount protoCount errorCount
        )
    )
    catch
    (
        local fatalErr = getCurrentException()
        format "FATAL ERROR during material synchronization: %\n" fatalErr
    )

    syncedCount
)

-- Execute when loaded via fileIn
syncProtoMaterials()
