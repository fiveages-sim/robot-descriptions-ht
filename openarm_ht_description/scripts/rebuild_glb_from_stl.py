"""Align colored GLBs to STL/ROS frame and re-export. Materials are never modified.

Uses meshes/glb_before_stl_rebuild as color source.
Geometry frame is corrected by rotation so AABB matches STL; face materials stay as painted.

  blender --background --python scripts/rebuild_glb_from_stl.py
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


def import_stl_aabb(path: Path) -> tuple[mathutils.Vector, mathutils.Vector]:
    clear_scene()
    if hasattr(bpy.ops.wm, "stl_import"):
        bpy.ops.wm.stl_import(filepath=str(path))
    else:
        bpy.ops.import_mesh.stl(filepath=str(path))
    obj = bpy.context.selected_objects[0]
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    return world_aabb(obj)


def import_join_glb(path: Path) -> bpy.types.Object:
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
    obj.location = (0.0, 0.0, 0.0)
    obj.rotation_euler = (0.0, 0.0, 0.0)
    obj.scale = (1.0, 1.0, 1.0)
    return obj


def world_aabb(obj: bpy.types.Object) -> tuple[mathutils.Vector, mathutils.Vector]:
    pts = [obj.matrix_world @ mathutils.Vector(c) for c in obj.bound_box]
    mn = mathutils.Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
    mx = mathutils.Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
    return mn, mx


def corners_aabb_after_rot(obj: bpy.types.Object, eul: tuple[float, float, float]):
    R = mathutils.Euler(eul).to_matrix().to_4x4()
    pts = [R @ mathutils.Vector(c) for c in obj.bound_box]
    mn = mathutils.Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
    mx = mathutils.Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
    return mn, mx


def align_to_stl(obj: bpy.types.Object, stl_mn, stl_mx) -> tuple[str, float]:
    candidates = [
        ("identity", (0.0, 0.0, 0.0)),
        ("rotx180", (math.pi, 0.0, 0.0)),
        ("roty180", (0.0, math.pi, 0.0)),
        ("rotz180", (0.0, 0.0, math.pi)),
    ]
    best = None
    for tag, eul in candidates:
        mn, mx = corners_aabb_after_rot(obj, eul)
        err = (mn - stl_mn).length + (mx - stl_mx).length
        if best is None or err < best[0]:
            best = (err, tag, eul)
    assert best is not None
    err, tag, eul = best
    obj.rotation_euler = eul
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    obj.location = (0.0, 0.0, 0.0)
    return tag, err


def export_glb(path: Path, obj: bpy.types.Object) -> None:
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    # Do not touch materials. Z-up for ROS/RViz.
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

    stl_mn, stl_mx = import_stl_aabb(stl_path)
    obj = import_join_glb(color_path)
    tag, err = align_to_stl(obj, stl_mn, stl_mx)
    nmat = len([m for m in obj.data.materials if m])
    # face hist
    from collections import Counter

    hist = Counter(p.material_index for p in obj.data.polygons)
    export_glb(out_path, obj)
    status = "OK" if err < 1e-3 else "WARN"
    print(f"[{status}] {name}: mats={nmat} face_hist={dict(hist)} align={tag} err={err:.6f}")


def main() -> None:
    names = sorted(p.stem for p in COLOR_DIR.glob("*.glb") if p.stat().st_size > 1000)
    print(f"Align+export {len(names)} colored GLBs (materials unchanged)")
    for name in names:
        try:
            process(name)
        except Exception as exc:  # noqa: BLE001
            print(f"[FAIL] {name}: {exc}")
    print("Done.")


if __name__ == "__main__":
    main()
