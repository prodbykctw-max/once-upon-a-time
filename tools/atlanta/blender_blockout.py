"""Blockout one Atlanta location from tools/atlanta/world/<key>.json.

Run inside Blender:
    blender --background --python tools/atlanta/blender_blockout.py -- mbs
    blender --python tools/atlanta/blender_blockout.py -- mbs        # with a UI

Rebuilds from scratch every run (idempotent) and saves
tools/atlanta/blender/<key>_blockout.blend.

Adapted from EBT-PRESENTS-CORNER-STORE-DASH's drive/tools/blender_blockout.py.
Three things carried over because they are hard-won, and three changed on
purpose — both lists are in the comments where they bite.
"""
import bpy, bmesh, json, math, os, sys

# ── CHANGED #1: no hard-coded path. ───────────────────────────────────────────
# The source script opens with ROOT = r"C:\\Users\\Owner\\Desktop\\..." which ties
# it to one laptop. Derive the repo from this file instead, with an env override,
# so it runs on the laptop, in a cloud session, or in CI unmodified.
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.environ.get("JANDE_ROOT") or os.path.normpath(os.path.join(HERE, "..", ".."))

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
KEY = argv[0] if argv else "mbs"

WORLD = os.path.join(HERE, "world", "%s.json" % KEY)
if not os.path.exists(WORLD):
    raise SystemExit(
        "no %s — run `node tools/atlanta/build_world.mjs %s` first.\n"
        "(From a cloud container that fetch does not complete; run it where the\n"
        " connection is ordinary. See tools/atlanta/README.md.)" % (WORLD, KEY))
W = json.load(open(WORLD, encoding="utf-8"))

# ── Heights OSM does not give us ──────────────────────────────────────────────
# The extractor emits h: null rather than inventing one. Guessing has to happen
# somewhere, so it happens HERE, where it is visible: every estimated building is
# flagged and gets its own material, so a glance at the viewport says what is
# surveyed and what is a guess. Never silently fold the two together.
LEVEL_M = 3.2
EST_H = {
    "house": 6.0, "detached": 6.0, "residential": 9.0, "apartments": 15.0,
    "retail": 7.0, "commercial": 12.0, "office": 20.0, "industrial": 9.0,
    "school": 9.0, "church": 12.0, "stadium": 35.0, "roof": 4.0, "garage": 3.0,
}
EST_DEFAULT = 8.0

# Road half-widths in metres. OSM gives `lanes` only sometimes, so this is the
# fallback table — also an estimate, also flagged in the object name.
LANE_M = 3.3
CLASS_W = {
    "motorway": 14.0, "trunk": 12.0, "primary": 11.0, "secondary": 10.0,
    "tertiary": 9.0, "residential": 7.5, "unclassified": 7.0, "service": 4.5,
    "living_street": 6.0, "pedestrian": 5.0, "footway": 2.0, "path": 1.8,
    "cycleway": 2.5, "steps": 1.6, "track": 3.0,
}
CLASS_DEFAULT = 6.0

bpy.ops.wm.read_homefile(use_empty=True)
scene = bpy.context.scene
scene.unit_settings.system = "METRIC"
scene.render.engine = "CYCLES"          # house style — see tools/blender/framework.py


def coll(name, parent=None):
    c = bpy.data.collections.new(name)
    (parent or scene.collection).children.link(c)
    return c


def mat(name, rgb, rough=0.85):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (rgb[0], rgb[1], rgb[2], 1)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (rgb[0], rgb[1], rgb[2], 1)
    b.inputs["Roughness"].default_value = rough
    return m


M = {
    "ground":  mat("ground",            (0.17, 0.18, 0.16)),
    "bld":     mat("building_surveyed", (0.56, 0.54, 0.51)),
    "bld_est": mat("building_ESTIMATED",(0.66, 0.46, 0.34)),   # orange = guessed height
    "road":    mat("road",              (0.07, 0.07, 0.08), 0.6),
    "foot":    mat("footway",           (0.30, 0.27, 0.24), 0.8),
    "park":    mat("park",              (0.18, 0.30, 0.16)),
    "water":   mat("water",             (0.10, 0.20, 0.32), 0.25),
    "route":   mat("route",             (1.00, 0.10, 0.10), 0.4),
}


def obj_from_bm(bm, name, collection, material):
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me); bm.free()
    me.materials.append(material)
    ob = bpy.data.objects.new(name, me)
    collection.objects.link(ob)
    return ob


def signed_area2(pts):
    return sum(x * pts[(i + 1) % len(pts)][1] - pts[(i + 1) % len(pts)][0] * y
               for i, (x, y) in enumerate(pts))


# ── CARRIED #1: ground ────────────────────────────────────────────────────────
# CHANGED #2: the source lays a real elevation mesh from an Open-Meteo grid. Our
# extractor does not fetch elevation yet, so this is a FLAT plate and says so.
# Atlanta is not flat — Stone Mountain least of all — so this is a known gap, not
# an opinion about the terrain.
R = float(W["location"]["radius_m"])
c_ground = coll("Terrain")
bm = bmesh.new()
bmesh.ops.create_grid(bm, x_segments=2, y_segments=2, size=R * 2.2)
obj_from_bm(bm, "ground_FLAT_no_elevation_data", c_ground, M["ground"])

# ── CARRIED #2: one object per building ───────────────────────────────────────
# Deliberately NOT merged here. Later passes need per-building facades and LODs,
# and the draw-call budget is met by merging per tile at EXPORT, not at blockout.
# (Budget, from the source project and adopted on 10-02: 60 fps on a mid-range
# phone at <=150 draw calls and <=500k visible tris.)
c_b = coll("Buildings")
c_surv, c_est = coll("Surveyed", c_b), coll("EstimatedHeight", c_b)
n_surv = n_est = 0
for b in W["buildings"]:
    pts = b["pts"]
    if len(pts) >= 2 and pts[0] == pts[-1]:
        pts = pts[:-1]                      # OSM closes rings; bmesh must not see the repeat
    if len(pts) < 3:
        continue
    h, est = b.get("h"), False
    if h is None:
        h, est = EST_H.get(b.get("kind"), EST_DEFAULT), True
    # ── CARRIED #3, and it is the real trap ──────────────────────────────────
    # Wind the ring counter-clockwise before extruding, or the solidified normals
    # point INWARD and every building renders inside-out — which looks like a
    # lighting bug and is not one.
    if signed_area2(pts) < 0:
        pts = pts[::-1]
    bm = bmesh.new()
    try:
        f = bm.faces.new([bm.verts.new((x, y, 0.0)) for x, y in pts])
    except ValueError:                      # duplicate/degenerate ring
        bm.free(); continue
    r = bmesh.ops.extrude_face_region(bm, geom=[f])
    top = [e for e in r["geom"] if isinstance(e, bmesh.types.BMVert)]
    bmesh.ops.translate(bm, verts=top, vec=(0, 0, h))
    bmesh.ops.reverse_faces(bm, faces=[f])  # floor faces down
    nm = (b.get("name") or "bld_%s" % b["id"])[:58]
    ob = obj_from_bm(bm, ("EST_" if est else "") + nm, c_est if est else c_surv,
                     M["bld_est"] if est else M["bld"])
    ob["osm_id"], ob["height_m"], ob["height_estimated"] = b["id"], h, est
    ob["osm_kind"] = b.get("kind") or ""
    n_est += est; n_surv += (not est)

# ── roads: ribbons, MERGED PER CLASS ─────────────────────────────────────────
# One mesh per highway class rather than per way — this is where draw calls are
# actually saved, and roads need no per-object treatment later.
c_r = coll("Roads")
by_cls, n_road_w = {}, 0
for rd in W["roads"]:
    by_cls.setdefault(rd["kind"], []).append(rd)
for cls, rds in sorted(by_cls.items()):
    bm = bmesh.new()
    made = 0
    for rd in rds:
        p = rd["pts"]
        if len(p) < 2:
            continue
        lanes = rd.get("lanes")
        hw = (lanes * LANE_M if lanes else CLASS_W.get(cls, CLASS_DEFAULT)) / 2.0
        if not lanes:
            n_road_w += 1
        lift = 0.06 if not rd.get("foot") else 0.10
        left, right = [], []
        for i, (x, y) in enumerate(p):
            ax, ay = p[max(i - 1, 0)]
            bx, by = p[min(i + 1, len(p) - 1)]
            dx, dy = bx - ax, by - ay
            L = math.hypot(dx, dy) or 1.0
            nx, ny = -dy / L, dx / L
            left.append(bm.verts.new((x + nx * hw, y + ny * hw, lift)))
            right.append(bm.verts.new((x - nx * hw, y - ny * hw, lift)))
        for i in range(len(p) - 1):
            try:
                bm.faces.new((right[i], right[i + 1], left[i + 1], left[i]))
                made += 1
            except ValueError:
                pass                        # doubled-back vertex; skip the quad
    if made:
        foot = cls in ("footway", "path", "steps", "cycleway", "pedestrian")
        obj_from_bm(bm, "roads_%s" % cls, c_r, M["foot"] if foot else M["road"])
    else:
        bm.free()

# ── areas: parks, pitches, water — flat fills, merged per kind ───────────────
c_a = coll("Areas")
by_kind = {}
for a in W.get("areas", []):
    by_kind.setdefault(a["kind"], []).append(a)
for kind, items in sorted(by_kind.items()):
    bm = bmesh.new()
    made = 0
    for a in items:
        pts = a["pts"]
        if len(pts) >= 2 and pts[0] == pts[-1]:
            pts = pts[:-1]
        if len(pts) < 3:
            continue
        if signed_area2(pts) < 0:
            pts = pts[::-1]
        try:
            bm.faces.new([bm.verts.new((x, y, 0.03)) for x, y in pts])
            made += 1
        except ValueError:
            pass
    if made:
        obj_from_bm(bm, "area_%s" % kind, c_a, M["water"] if kind == "water" else M["park"])
    else:
        bm.free()

# ── CHANGED #3: a CANDIDATE route, not an authored one ───────────────────────
# The source project has an approved 1.1 km route baked into world.json. We do
# not have one yet, so the longest way through the extract is drawn in red as a
# starting point for whoever authors the run. It is named CANDIDATE so nobody
# mistakes it for a decision.
c_g = coll("Gameplay")
spine = None
best = 0.0
for rd in W["roads"]:
    p = rd["pts"]
    d = sum(math.hypot(p[i][0] - p[i-1][0], p[i][1] - p[i-1][1]) for i in range(1, len(p)))
    if d > best:
        best, spine = d, rd
if spine:
    cu = bpy.data.curves.new("ROUTE_CANDIDATE", "CURVE")
    cu.dimensions = "3D"; cu.bevel_depth = 0.9
    sp = cu.splines.new("POLY"); sp.points.add(len(spine["pts"]) - 1)
    for pt, (x, y) in zip(sp.points, spine["pts"]):
        pt.co = (x, y, 1.0, 1)
    cu.materials.append(M["route"])
    ob = bpy.data.objects.new("ROUTE_CANDIDATE_%s" % (spine.get("name") or spine["kind"]), cu)
    c_g.objects.link(ob)

# ── sun + camera ─────────────────────────────────────────────────────────────
sun = bpy.data.objects.new("sun", bpy.data.lights.new("sun", "SUN"))
sun.data.energy = 4.0
sun.rotation_euler = (math.radians(42), math.radians(12), math.radians(-35))
scene.collection.objects.link(sun)

cam = bpy.data.objects.new("cam_overview", bpy.data.cameras.new("cam_overview"))
cam.data.type = "ORTHO"; cam.data.ortho_scale = R * 2.4; cam.data.clip_end = 8000
cam.location = (0, -R * 0.9, R * 1.8)
cam.rotation_euler = (math.radians(32), 0, 0)
scene.collection.objects.link(cam); scene.camera = cam
scene.render.resolution_x, scene.render.resolution_y = 1600, 900

for area in (bpy.context.screen.areas if bpy.context.screen else []):
    if area.type == "VIEW_3D":
        s3 = area.spaces[0]
        s3.shading.type = "SOLID"; s3.shading.color_type = "MATERIAL"
        s3.clip_end = 20000

out_dir = os.path.join(HERE, "blender")
os.makedirs(out_dir, exist_ok=True)
path = os.path.join(out_dir, "%s_blockout.blend" % KEY)
bpy.ops.wm.save_as_mainfile(filepath=path)

# ── budget report ────────────────────────────────────────────────────────────
# The budgets are hard limits, so the script says where it stands rather than
# leaving it to be discovered at export. Blockout objects MERGE per tile later,
# so the object count here is not the draw-call count — the triangle count is the
# one that has to come down if it is over.
tris = 0
for ob in scene.objects:
    if ob.type == "MESH":
        tris += sum(max(0, len(p.vertices) - 2) for p in ob.data.polygons)
meshes = sum(1 for ob in scene.objects if ob.type == "MESH")

print("\n%s — %s, %.0f m radius" % (KEY, W["location"]["label"], R))
print("  buildings   %d surveyed + %d ESTIMATED height (%s)"
      % (n_surv, n_est, "orange in the viewport" if n_est else "none guessed"))
print("  roads       %d class meshes, %d ways fell back to a class width"
      % (len(c_r.objects), n_road_w))
print("  areas       %d kind meshes" % len(c_a.objects))
print("  ground      FLAT — no elevation grid in world.json yet")
print("  triangles   %s  (budget <=500k visible; LOD and culling come later)"
      % format(tris, ","))
print("  mesh objects %d  (NOT draw calls — merged per tile at export)" % meshes)
if tris > 500000:
    print("  !! over the 500k triangle budget already at blockout — cut radius or decimate")
print("  saved %s" % path)
print("  %s" % W["attribution"])
