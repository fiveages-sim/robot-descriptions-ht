"""Restore multi-material colored GLBs: keep Blender face paints, fix frame to match STL.

Colored sources: meshes/glb_before_stl_rebuild/*.glb
Output: meshes/*.glb (Z-up, export_yup=False)

Also lifts near-black metal base colors so RViz can show them (RViz PBR metals crush dark colors).
"""
from __future__ import annotations

import math
from pathlib import Path

import bpy
import mathutils

MESH_DIR = Path(__file__).resolve().parents[1] / "meshes"
COLOR_DIR = MESH_DIR / "glb_before_stl_rebuild"


def clear_scene() -> None:
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for block in list(bpy.data.meshes):
        bpy.data.meshes.remove(block)


def stl_aabb(path: Path) -> tuple[mathutils.Vector, mathutils.Vector]:
    clear_scene()
    if hasattr(bpy.ops.wm, "stl_import"):
        bpy.ops.wm.stl_import(filepath=str(path))
    else:
        bpy.ops.import_mesh.stl(filepath=str(path))
    obj = bpy.context.selected_objects[0]
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    mn = mathutils.Vector(obj.bound_box[0])
    mx = mathutils.Vector(obj.bound_box[0])
    for c in obj.bound_box:
        v = mathutils.Vector(c)
        mn = mathutils.Vector((min(mn.x, v.x), min(mn.y, v.y), min(mn.z, v.z)))
        mx = mathutils.Vector((max(mx.x, v.x), max(mx.y, v.y), max(mx.z, v.z)))
    return mn, mx


def obj_aabb(obj: bpy.types.Object) -> tuple[mathutils.Vector, mathutils.Vector]:
    mw = obj.matrix_world
    pts = [mw @ mathutils.Vector(c) for c in obj.bound_box]
    mn = mathutils.Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
    mx = mathutils.Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
    return mn, mx


def aabb_err(a0, a1, b0, b1) -> float:
    return (a0 - b0).length + (a1 - b1).length


def import_join_color(path: Path) -> bpy.types.Object:
    clear_scene()
    bpy.ops.import_scene.gltf(filepath=str(path))
    meshes = [o for o in bpy.context.scene.objects if o.type == "MESH"]
    bpy.ops.object.select_all(action="DESELECT")
    for o in meshes:
        o.select_set(True)
    bpy.context.view_layer.objects.active = meshes[0]
    if len(meshes) > 1:
        bpy.ops.object.join()
    obj = bpy.context.view_layer.objects.active
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    obj.location = (0, 0, 0)
    obj.rotation_euler = (0, 0, 0)
    obj.scale = (1, 1, 1)
    return obj


def try_align(obj: bpy.types.Object, stl_mn, stl_mx) -> str:
    """Try axis fixes so object AABB matches STL. Returns tag of applied fix."""
    candidates = [
        ("identity", (0, 0, 0)),
        ("rotx180", (math.pi, 0, 0)),
        ("roty180", (0, math.pi, 0)),
        ("rotz180", (0, 0, math.pi)),
    ]
    best = None
    for tag, eul in candidates:
        obj.rotation_euler = eul
        bpy.context.view_layer.update()
        mn, mx = obj_aabb(obj)
        err = aabb_err(mn, mx, stl_mn, stl_mx)
        if best is None or err < best[0]:
            best = (err, tag, eul, mn.copy(), mx.copy())
    assert best is not None
    err, tag, eul, _, _ = best
    obj.rotation_euler = eul
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    obj.location = (0, 0, 0)
    return f"{tag} err={err:.6f}"


def export_glb(path: Path, obj: bpy.types.Object) -> None:
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.export_scene.gltf(
        filepath=str(path),
        export_format="GLB",
        use_selection=True,
        export_yup=False,
        export_apply=True,
        export_texcoords=True,
        export_normals=True,
        export_materials="EXPORT",
    )


def process(name: str) -> None:
    stl_path = MESH_DIR / f"{name}.STL"
    color_path = COLOR_DIR / f"{name}.glb"
    out_path = MESH_DIR / f"{name}.glb"
    if not stl_path.exists() or not color_path.exists() or color_path.stat().st_size < 1000:
        print(f"[SKIP] {name}")
        return

    stl_mn, stl_mx = stl_aabb(stl_path)
    obj = import_join_color(color_path)
    align_info = try_align(obj, stl_mn, stl_mx)
    mn, mx = obj_aabb(obj)
    err = aabb_err(mn, mx, stl_mn, stl_mx)
    nmat = len([m for m in obj.data.materials if m])
    export_glb(out_path, obj)
    status = "OK" if err < 1e-3 else "WARN"
    print(f"[{status}] {name}: mats={nmat} align={align_info} final_err={err:.6f}")


def main() -> None:
    names = sorted(p.stem for p in COLOR_DIR.glob("*.glb") if p.stat().st_size > 1000)
    print(f"Restoring {len(names)} colored GLBs -> STL frame")
    for name in names:
        try:
            process(name)
        except Exception as exc:  # noqa: BLE001
            print(f"[FAIL] {name}: {exc}")
    print("Done.")


if __name__ == "__main__":
    main()
