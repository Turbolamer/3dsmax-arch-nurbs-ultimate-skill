"""Small live experiment, not the production wall builder.

Emit one short, self-cleaning MAXScript per case. Run each with fileIn through
3dsmax-mcp_execute_maxscript; save the returned wire strings in results.json.
Then run this file with --assess. Coordinates are canonical centimetres; the
experiment reads native Max units without changing them.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def area(points):
    return sum(a[0]*b[1]-a[1]*b[0] for a, b in zip(points, points[1:]+points[:1]))/2


def offset(points, distance):
    """Signed outward miter offset; simple fixtures only, NOT a robust offsetter."""
    result = []
    normals = []
    for a, b in zip(points, points[1:]+points[:1]):
        dx, dy = b[0]-a[0], b[1]-a[1]
        length = math.hypot(dx, dy)
        normals.append((dy/length, -dx/length))
    for i, p in enumerate(points):
        a, b = normals[i-1], normals[i]
        den = 1+a[0]*b[0]+a[1]*b[1]
        if den < 1e-8:
            raise ValueError("degenerate miter")
        result.append([p[0]+distance*(a[0]+b[0])/den,
                       p[1]+distance*(a[1]+b[1])/den])
    return result


RECT = [[0, 0], [600, 0], [600, 400], [0, 400]]
# opening rows: segment (1 based), s_min, s_max, z_min, z_max
CASES = [
    dict(id="rectangle_blind", points=RECT, openings=[]),
    dict(id="rectangle_openings", points=RECT,
         openings=[[1, 100, 200, 0, 210], [1, 320, 500, 90, 210],
                   [2, 100, 300, 110, 240]]),
    dict(id="L_openings", points=[[0, 0], [600, 0], [600, 250],
                                  [350, 250], [350, 500], [0, 500]],
         openings=[[1, 100, 200, 0, 210], [4, 60, 180, 90, 220]]),
    dict(id="U_openings", points=[[0, 0], [800, 0], [800, 600], [550, 600],
                                  [550, 250], [250, 250], [250, 600], [0, 600]],
         openings=[[1, 100, 200, 0, 210], [4, 100, 250, 100, 230],
                   [6, 90, 220, 80, 220]]),
    dict(id="oblique_openings", points=[[0, 0], [600, 0], [500, 400], [100, 400]],
         openings=[[1, 100, 200, 0, 210], [2, 100, 250, 90, 220]]),
    dict(id="outer_12x8", points=offset([[0, 0], [1200, 0], [1200, 800], [0, 800]], -30),
         openings=[[1, 100, 200, 0, 210], [2, 100, 300, 90, 210]]),
]


def prepare(case):
    points, ops = case["points"], case["openings"]
    thickness, height = 30, 300
    assert area(points) > 0
    outer = offset(points, thickness)
    zlevels = sorted({0, height, *(z for op in ops for z in op[3:])})
    cols = []
    for segment, (a, b) in enumerate(zip(points, points[1:]+points[:1]), 1):
        length = math.dist(a, b)
        cuts = sorted({0, length, *(s for op in ops if op[0] == segment for s in op[1:3])})
        for lo, hi in zip(cuts, cuts[1:]):
            cols.append(([a[0]+(b[0]-a[0])*lo/length, a[1]+(b[1]-a[1])*lo/length],
                         segment, lo, hi))
    vertices = [[*p, z] for z in zlevels for p, *_ in cols]
    faces, deleted = [], []
    count = len(cols)
    for row, (z0, z1) in enumerate(zip(zlevels, zlevels[1:])):
        for col, (_, seg, s0, s1) in enumerate(cols):
            nxt = (col+1) % count
            faces.append([row*count+col+1, row*count+nxt+1,
                          (row+1)*count+nxt+1, (row+1)*count+col+1])
            if any(op[0] == seg and op[1] <= s0 and s1 <= op[2]
                   and op[3] <= z0 and z1 <= op[4] for op in ops):
                deleted.append(len(faces))
    expected_volume = (area(outer)-area(points))*height - sum(
        (op[2]-op[1])*(op[4]-op[3])*thickness for op in ops)
    bounds = [min(p[0] for p in outer), min(p[1] for p in outer), 0,
              max(p[0] for p in outer), max(p[1] for p in outer), height]
    return dict(vertices=vertices, faces=faces, deleted=deleted, cols=cols,
                volume_cm3=expected_volume, bounds_cm=bounds,
                base_faces=len(faces)-len(deleted), thickness=thickness)


def mx_array(rows, points=False):
    def row(r):
        return ("[" if points else "#(")+",".join(str(float(x)) if points else str(x) for x in r)+( "]" if points else ")")
    return "#("+",".join(row(r) for r in rows)+")"


def emit(case, keep=False):
    data = prepare(case)
    name = ("CCSV2_DEMO_" if keep else "CCSV2_PROBE_")+case["id"]
    deletion = "#{"+",".join(map(str, data["deleted"]))+"}"
    # Full-floor Z union deliberately keeps shared corner vertices conforming.
    # No slice, weld, Boolean, extrude or guard/lease registry is involved.
    cleanup = ('''if isValidNode wall do (wall.wirecolor=color 190 203 218; wall.allEdges=true)
if isValidNode guide do guide.wirecolor=color 255 180 50'''
               if keep else '''if isValidNode wall do delete wall
if isValidNode guide do delete guide''')
    return f'''(
local wall=undefined
local guide=undefined
local tm=undefined
local out=""
local before=objects.count
try (
 if (getNodeByName "{name}") != undefined do throw "Probe name collision"
 local factor=units.decodeValue "1cm"
 local verts={mx_array(data['vertices'], True)}
 local polygons={mx_array(data['faces'])}
 guide=SplineShape name:"{name}_InnerSpline"
 addNewSpline guide
 for i=1 to {len(data['cols'])} do addKnot guide 1 #corner #line (verts[i]*factor)
 close guide 1
 updateShape guide
 guide.isHidden=true
 wall=Editable_mesh name:"{name}"
 convertTo wall Editable_Poly
 for p in verts do polyop.createVert wall (p*factor)
 for indices in polygons do (
   local idx=polyop.createPolygon wall indices
   if idx == 0 do throw "createPolygon returned zero"
 )
 polyop.deleteFaces wall {deletion} delIsoVerts:true
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
 out="CASE|id={case['id']}|baseFaces="+(baseFaces as string)+"|mods="+(wall.modifiers.count as string)+"|straight="+(sh.straightenCorners as string)+"|normal1="+(normal1 as string)+"|open="+(openCount as string)+"|badValence="+(badValence as string)+"|degenerate="+(degenerate as string)+"|volume="+(signedVol as string)+"|min="+(minV as string)+"|max="+(maxV as string)+"|triangles="+(tm.numfaces as string)
) catch (out="ERROR|id={case['id']}|message="+(getCurrentException()))
if tm != undefined do delete tm
{cleanup}
out+"|before="+(before as string)+"|after="+(objects.count as string)
)
'''


def assess():
    captured = json.loads((ROOT/"results.json").read_text(encoding="utf-8"))
    reports = []
    for case in CASES:
        expected = prepare(case)
        wire = captured[case["id"]]
        if isinstance(wire, dict):
            wire = wire["result"]
        if wire.startswith("{"):
            wire = json.loads(wire)["result"]
        fields = dict(part.split("=", 1) for part in wire.split("|")[1:])
        issues = []
        relative = None
        bound_error = None
        if not wire.startswith("CASE|"):
            issues.append(wire)
        else:
            for key in ("open", "badValence", "degenerate"):
                if fields[key] != "0":
                    issues.append(key+" != 0")
            if fields["mods"] != "1" or fields["straight"] != "true":
                issues.append("Shell stack")
            if fields["before"] != fields["after"]:
                issues.append("cleanup")
            if int(fields["baseFaces"]) != expected["base_faces"]:
                issues.append("base face count")
            measured = float(fields["volume"].replace("d", "e").replace("D", "e"))
            relative = abs(measured-expected["volume_cm3"])/expected["volume_cm3"]
            if relative > 1e-5:
                issues.append("volume")
            measured_bounds = [float(v) for key in ("min", "max")
                               for v in fields[key].strip("[]").split(",")]
            bound_error = max(abs(a-b) for a, b in zip(measured_bounds, expected["bounds_cm"]))
            if bound_error > .01:
                issues.append("bounds")
        reports.append(dict(id=case["id"], status="FAIL" if issues else "PASS",
                            issues=issues, expected_volume_cm3=expected["volume_cm3"],
                            relative_volume_error_from_rounded_wire=relative,
                            max_bound_error_cm_from_rounded_wire=bound_error,
                            measured=fields))
    (ROOT/"assessment.json").write_text(json.dumps(reports, indent=2), encoding="utf-8")
    print(json.dumps(reports, indent=2))
    return int(any(r["issues"] for r in reports))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--assess", action="store_true")
    parser.add_argument("--display", action="store_true")
    args = parser.parse_args()
    if args.assess:
        raise SystemExit(assess())
    if args.display:
        for case in CASES:
            (ROOT/("display_"+case["id"]+".ms")).write_text(emit(case, keep=True), encoding="utf-8")
        print("Emitted display scripts (leave geometry in Max).")
        raise SystemExit(0)
    for case in CASES:
        (ROOT/(case["id"]+".ms")).write_text(emit(case), encoding="utf-8")
    print("Emitted", len(CASES), "short live probes to", ROOT)
