"""Re-export colored GLBs for ROS/RViz: join parts, Z-up, origin at (0,0,0).

Run:
  blender --background --python scripts/fix_glb_for_ros.py
"""
from __future__ import annotations

from pathlib import Path

import bpy

MESH_DIR = Path(__file__).resolve().parents[1] / "meshes"
BACKUP_DIR = MESH_DIR / "glb_blender_raw"


def clear_scene() -> None:
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for block in bpy.data.meshes:
        bpy.data.meshes.remove(block)
    for block in bpy.data.materials:
        if block.users == 0:
            bpy.data.materials.remove(block)


def join_meshes() -> bpy.types.Object | None:
    meshes = [o for o in bpy.context.scene.objects if o.type == "MESH"]
    if not meshes:
        return None
    bpy.ops.object.select_all(action="DESELECT")
    for o in meshes:
        o.select_set(True)
    bpy.context.view_layer.objects.active = meshes[0]
    if len(meshes) > 1:
        bpy.ops.object.join()
    obj = bpy.context.view_layer.objects.active
    # Keep vertex positions in world frame, then move object origin to world origin
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    obj.location = (0.0, 0.0, 0.0)
    obj.rotation_euler = (0.0, 0.0, 0.0)
    obj.scale = (1.0, 1.0, 1.0)
    return obj


def export_glb(path: Path) -> None:
    # export_yup=False: keep Blender/ROS Z-up so RViz matches STL/URDF frames
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


def process_one(src: Path) -> None:
    clear_scene()
    bpy.ops.import_scene.gltf(filepath=str(src))
    obj = join_meshes()
    if obj is None:
        print(f"[SKIP] no mesh in {src.name}")
        return
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj

    BACKUP_DIR.mkdir(exist_ok=True)
    backup = BACKUP_DIR / src.name
    if not backup.exists():
        backup.write_bytes(src.read_bytes())

    export_glb(src)
    print(f"[OK] {src.name}")


def main() -> None:
    glbs = sorted(MESH_DIR.glob("*.glb"))
    print(f"Fixing {len(glbs)} GLBs in {MESH_DIR}")
    for path in glbs:
        try:
            process_one(path)
        except Exception as exc:  # noqa: BLE001
            print(f"[FAIL] {path.name}: {exc}")
    print("Done. Raw Blender exports backed up under meshes/glb_blender_raw/")


if __name__ == "__main__":
    main()
