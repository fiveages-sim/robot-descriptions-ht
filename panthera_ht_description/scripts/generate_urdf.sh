#!/usr/bin/env bash
# Regenerate urdf/*.urdf from xacro/robot.xacro (package:// mesh paths for OCS2).
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PKG_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
XACRO="${PKG_DIR}/xacro/robot.xacro"
URDF_DIR="${PKG_DIR}/urdf"

if ! command -v xacro >/dev/null 2>&1; then
  echo "xacro not found; source ROS and: sudo apt install ros-\${ROS_DISTRO}-xacro" >&2
  exit 1
fi

mkdir -p "${URDF_DIR}"

gen() {
  local out="$1"
  shift
  echo "Generating ${out} ..."
  xacro "${XACRO}" "$@" -o "${URDF_DIR}/${out}"
}

gen panthera_ht.urdf
gen panthera_ht_dual.urdf type:=dual
gen panthera_ht_left.urdf type:=left
gen panthera_ht_right.urdf type:=right

echo "Done. URDF files use package://panthera_ht_description/meshes/ paths."
