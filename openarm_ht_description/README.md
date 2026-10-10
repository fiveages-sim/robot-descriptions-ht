# OpenArm HT Description

This package contains the description files for the HighTorque OpenArm HT dual-arm manipulator with parallel grippers.

模型源文件在 **`xacro/`**（不提交 / 不安装 `urdf/`）。Launch 与 OCS2 通过 xacro 现场展开。

## 1. Build

```bash
cd ~/open-deploy-ws
colcon build --packages-select openarm_ht_description --symlink-install
```

## 2. Visualize the robot

### 2.1 Arm configuration (`type`)

Robot model is defined under `xacro/robot.xacro`. Use **`type`** to switch arm composition:

- `type:=dual` (default): **dual arm** (both `left_` and `right_`)
- `type:=single`: **single arm** (unprefixed, left kinematics)
- `type:=left`: **left arm only** (unprefixed, left kinematics)
- `type:=right`: **right arm only** (unprefixed, right kinematics)

Composition:

- `world -> base_link -> torso_link` (pedestal split for configuration)
- `torso_link ->` arm(s) via mount offsets

Mesh paths use `file://$(find openarm_ht_description)/meshes/...`（由 xacro/`$(find)` 解析到包目录）。

Examples:

- Dual Arm (default)

```bash
source ~/open-deploy-ws/install/setup.bash
ros2 launch robot_common_launch manipulator.launch.py robot:=openarm_ht type:=dual
```

- Single / Left / Right

```bash
source ~/open-deploy-ws/install/setup.bash
ros2 launch robot_common_launch manipulator.launch.py robot:=openarm_ht type:=single
ros2 launch robot_common_launch manipulator.launch.py robot:=openarm_ht type:=left
ros2 launch robot_common_launch manipulator.launch.py robot:=openarm_ht type:=right
```

### 2.2 Mount parameters

Tune pedestal / arm mounts via xacro mappings:

- `torso_xyz` / `torso_rpy` (default `0 0 0.7`)
- `left_mount_xyz` / `left_mount_rpy` (default `0 0.096 0`)
- `right_mount_xyz` / `right_mount_rpy` (default `0 -0.096 0`)

## 3. OCS2 Demo

### 3.1 OCS2 Arm Controller Demo

Mock simulation by default (`hardware:=mock_components`).

```bash
# Dual arm (default)
source ~/open-deploy-ws/install/setup.bash
ros2 launch ocs2_arm_controller demo.launch.py robot:=openarm_ht type:=dual
```

```bash
# Single arm
source ~/open-deploy-ws/install/setup.bash
ros2 launch ocs2_arm_controller demo.launch.py robot:=openarm_ht type:=single
```

```bash
source ~/open-deploy-ws/install/setup.bash
ros2 launch ocs2_arm_controller demo.launch.py robot:=openarm_ht type:=dual hardware:=isaac
```

### 3.2 Real robot

Requires `ht_ros2_control` (plugin `PantheraHardwareInterface` with OpenArm motor YAML).
Default real mode is **`mit`**. Dual uses 14 arm joints (`OpenarmDual.yaml`);
single uses 7 (`Openarm.yaml`). Gravity feedforward comes from OCS2’s Pinocchio model
(`config/ocs2/dual.info` / `single.info`, grippers in `removeJoints`).

Optional: `control_mode:=effort` or `position`.

```bash
source ~/open-deploy-ws/install/setup.bash
ros2 launch ocs2_arm_controller demo.launch.py robot:=openarm_ht type:=dual hardware:=real
```

Dual-arm OCS2 uses `config/ocs2/dual.info` (`eeFrame` / `eeFrame1`) and
`config/ros2_control/dual.yaml` when `type:=dual`.
Single-arm mode uses `config/ocs2/single.info` and `config/ros2_control/single.yaml`.
