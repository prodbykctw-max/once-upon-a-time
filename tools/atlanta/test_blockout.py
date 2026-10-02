#!/usr/bin/env python3
"""Run blender_blockout.py headless, against fake bpy/bmesh, on a known world.

    python3 tools/atlanta/test_blockout.py

Blender is not installed in the cloud container, and the bugs in a blockout
script are not Blender bugs — they are geometry bugs: rings wound the wrong way
so buildings extrude inside-out, OSM's repeated closing vertex making a
degenerate face, ribbon normals flipping on a doubled-back way. All of that is
plain arithmetic and can be tested without Blender, so it is.

The stubs record what the script ASKED to build, and the assertions check the
shapes rather than that it merely ran.
"""
import json, os, sys, types, math, tempfile, shutil

HERE = os.path.dirname(os.path.abspath(__file__))

# ── the scene the script thinks it built ─────────────────────────────────────
built = {"objects": [], "materials": [], "collections": []}


class V:
    def __init__(self, co): self.co = tuple(co)


class F:
    def __init__(self, verts): self.verts = list(verts)


class BM:
    def __init__(self):
        self._v, self._f = [], []
        self.verts = types.SimpleNamespace(new=self._vnew)
        self.faces = types.SimpleNamespace(new=self._fnew)

    def _vnew(self, co):
        v = V(co); self._v.append(v); return v

    def _fnew(self, verts):
        vs = list(verts)
        if len(set(id(v) for v in vs)) != len(vs):
            raise ValueError("duplicate vert in face")
        if len(vs) < 3:
            raise ValueError("degenerate face")
        f = F(vs); self._f.append(f); return f

    def to_mesh(self, me):
        me._verts = [v.co for v in self._v]
        me._faces = [[v.co for v in f.verts] for f in self._f]

    def free(self): pass


def _ops_create_grid(bm, x_segments=2, y_segments=2, size=1.0):
    for sx in (-size, size):
        for sy in (-size, size):
            bm._vnew((sx, sy, 0.0))
    bm._f.append(F(bm._v[-4:]))


def _ops_extrude(bm, geom=None):
    face = geom[0]
    newv = [bm._vnew(v.co) for v in face.verts]
    for i in range(len(newv)):
        bm._f.append(F([face.verts[i], face.verts[(i+1) % len(newv)],
                        newv[(i+1) % len(newv)], newv[i]]))
    bm._f.append(F(newv))
    return {"geom": newv}


def _ops_translate(bm, verts=None, vec=(0, 0, 0)):
    for v in verts:
        v.co = (v.co[0]+vec[0], v.co[1]+vec[1], v.co[2]+vec[2])


def _noop(*a, **k): pass


class Mesh:
    def __init__(self, name):
        self.name = name; self.materials = []; self._verts = []; self._faces = []
    @property
    def polygons(self):
        return [types.SimpleNamespace(vertices=list(range(len(f)))) for f in self._faces]


class Obj(dict):
    def __init__(self, name, data):
        super().__init__(); self.name = name; self.data = data
        self.type = "MESH" if isinstance(data, Mesh) else "OTHER"
        self.location = (0, 0, 0); self.rotation_euler = (0, 0, 0)


def install_stubs():
    bpy = types.ModuleType("bpy")
    bmesh = types.ModuleType("bmesh")

    scene = types.SimpleNamespace(
        unit_settings=types.SimpleNamespace(system=""),
        render=types.SimpleNamespace(engine="", resolution_x=0, resolution_y=0),
        collection=types.SimpleNamespace(
            children=types.SimpleNamespace(link=_noop),
            objects=types.SimpleNamespace(link=lambda o: built["objects"].append(o))),
        camera=None, objects=[])

    def coll_new(name):
        c = types.SimpleNamespace(
            name=name, objects=[],
            children=types.SimpleNamespace(link=_noop))
        c.objects = _ObjList()
        built["collections"].append(c)
        return c

    class _ObjList(list):
        def link(self, o):
            self.append(o); built["objects"].append(o); scene.objects.append(o)

    def mat_new(name):
        nt = types.SimpleNamespace(nodes={"Principled BSDF": types.SimpleNamespace(
            inputs={"Base Color": types.SimpleNamespace(default_value=None),
                    "Roughness": types.SimpleNamespace(default_value=None)})})
        m = types.SimpleNamespace(name=name, use_nodes=False, diffuse_color=None, node_tree=nt)
        built["materials"].append(m); return m

    class _Curve:
        def __init__(self, name, kind):
            self.name = name; self.dimensions = ""; self.bevel_depth = 0
            self.materials = []; self.splines = _Splines()

    class _Splines(list):
        def new(self, kind):
            s = types.SimpleNamespace(points=_Points()); self.append(s); return s

    class _Points(list):
        def add(self, n):
            for _ in range(n + 1):
                self.append(types.SimpleNamespace(co=None))

    bpy.ops = types.SimpleNamespace(
        wm=types.SimpleNamespace(read_homefile=_noop, save_as_mainfile=_noop))
    bpy.data = types.SimpleNamespace(
        collections=types.SimpleNamespace(new=coll_new),
        materials=types.SimpleNamespace(new=mat_new),
        meshes=types.SimpleNamespace(new=Mesh),
        objects=types.SimpleNamespace(new=Obj),
        curves=types.SimpleNamespace(new=_Curve),
        lights=types.SimpleNamespace(new=lambda n, t: types.SimpleNamespace(energy=0)),
        cameras=types.SimpleNamespace(new=lambda n: types.SimpleNamespace(
            type="", ortho_scale=0, clip_end=0)))
    bpy.context = types.SimpleNamespace(scene=scene, screen=None)

    bmesh.new = BM
    bmesh.types = types.SimpleNamespace(BMVert=V)
    bmesh.ops = types.SimpleNamespace(
        create_grid=_ops_create_grid, extrude_face_region=_ops_extrude,
        translate=_ops_translate, reverse_faces=_noop, scale=_noop,
        create_cube=_noop, create_cone=_noop)

    sys.modules["bpy"] = bpy
    sys.modules["bmesh"] = bmesh
    return scene


# ── a world with deliberately awkward shapes ─────────────────────────────────
WORLD = {
    "location": {"key": "test", "label": "Test Block", "osm": "way/0",
                 "lat": 33.75, "lon": -84.40, "radius_m": 200},
    "frame": {"origin": "centre", "units": "metres", "x": "east", "y": "north"},
    "attribution": "Map data © OpenStreetMap contributors (ODbL)",
    "buildings": [
        # CLOCKWISE ring, closed by a repeated final vertex — both traps at once
        {"id": 1, "pts": [[0, 0], [0, 10], [10, 10], [10, 0], [0, 0]], "h": 12.0, "kind": "office"},
        # counter-clockwise, no height given -> must be flagged ESTIMATED
        {"id": 2, "pts": [[20, 0], [30, 0], [30, 10], [20, 10]], "h": None, "kind": "house"},
        # degenerate: must be skipped, not crash
        {"id": 3, "pts": [[50, 50], [51, 51]], "h": 5.0, "kind": "shed"},
    ],
    "roads": [
        {"id": 10, "pts": [[-50, 0], [50, 0], [50, 40]], "kind": "residential", "lanes": 2},
        {"id": 11, "pts": [[-50, 20], [50, 20]], "kind": "footway", "foot": True},
    ],
    "areas": [
        {"id": 20, "pts": [[-40, -40], [-10, -40], [-10, -10], [-40, -10]], "kind": "park"},
    ],
}


def main():
    scene = install_stubs()
    tmp = tempfile.mkdtemp()
    wdir = os.path.join(HERE, "world")
    os.makedirs(wdir, exist_ok=True)
    wpath = os.path.join(wdir, "__test__.json")
    json.dump(WORLD, open(wpath, "w"))
    sys.argv = ["blender", "--", "__test__"]
    try:
        src = open(os.path.join(HERE, "blender_blockout.py"), encoding="utf-8").read()
        g = {"__name__": "__main__", "__file__": os.path.join(HERE, "blender_blockout.py")}
        exec(compile(src, "blender_blockout.py", "exec"), g)
    finally:
        os.remove(wpath); shutil.rmtree(tmp, ignore_errors=True)

    fails, ran = [], []

    def check(name, cond, detail=""):
        ran.append(name)
        print(("  PASS  " if cond else "  FAIL  ") + name + (("  — " + detail) if detail else ""))
        if not cond:
            fails.append(name)

    names = [o.name for o in built["objects"]]
    print("\nobjects built: %s\n" % ", ".join(names))

    # 1. the degenerate building is skipped, the two real ones are not
    blds = [o for o in built["objects"] if o.get("osm_id") in (1, 2, 3)]
    check("degenerate ring skipped, 2 buildings built", len(blds) == 2,
          "got %d" % len(blds))

    # 2. the missing height is flagged, not silently filled
    est = [o for o in blds if o.get("height_estimated")]
    check("building with h:null flagged ESTIMATED", len(est) == 1 and est[0]["height_m"] == 6.0,
          "house estimate should be 6.0 m, got %s" % (est[0]["height_m"] if est else None))
    check("estimated building is named so it is visible",
          any(o.name.startswith("EST_") for o in est))

    # 3. the surveyed height is used verbatim
    surv = [o for o in blds if not o.get("height_estimated")]
    check("surveyed height used as-is", surv and surv[0]["height_m"] == 12.0)

    # 4. THE WINDING TRAP: the closed clockwise ring must extrude UPWARD to h,
    #    with 4 base verts (not 5 — the repeated closing vertex must be dropped)
    b1 = [o for o in blds if o.get("osm_id") == 1][0]
    zs = sorted(set(round(c[2], 3) for c in b1.data._verts))
    check("closing vertex dropped (4 base verts, not 5)",
          len(b1.data._verts) == 8, "got %d verts" % len(b1.data._verts))
    check("extruded to the right height", zs == [0.0, 12.0], "z levels %s" % zs)

    # 5. ribbon width honours `lanes` when OSM gives it (2 lanes x 3.3 = 6.6 wide)
    road = [o for o in built["objects"] if o.name == "roads_residential"][0]
    ys = [c[1] for c in road.data._verts if abs(c[0] + 50) < 0.01]
    check("lane count drives width (2 lanes -> 6.6 m)",
          abs((max(ys) - min(ys)) - 6.6) < 0.01, "got %.2f m" % (max(ys) - min(ys)))

    # 6. footways get their own material/mesh, not lumped in with roads
    check("footway separated from carriageway",
          any(o.name == "roads_footway" for o in built["objects"]))

    # 7. areas built
    check("park area built", any(o.name == "area_park" for o in built["objects"]))

    # 8. a candidate route is proposed and clearly named as a candidate
    check("route proposed and marked CANDIDATE",
          any(o.name.startswith("ROUTE_CANDIDATE") for o in built["objects"]))

    # count the checks that actually ran — a hardcoded total is a summary that lies
    print("\n%d checks, %d failed" % (len(ran), len(fails)))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
