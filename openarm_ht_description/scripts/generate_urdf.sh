#!/usr/bin/env bash
# Optional helper: expand xacro/robot.xacro to local urdf/ for inspection.
# Runtime launch uses xacro directly; generated files are not installed or committed.
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

gen openarm_ht.urdf type:=dual
gen openarm_ht_dual.urdf type:=dual
gen openarm_ht_single.urdf type:=single
gen openarm_ht_left.urdf type:=left
gen openarm_ht_right.urdf type:=right

echo "Done (local only; do not commit urdf/). Mesh paths use file://\$(find openarm_ht_description)/meshes/."
