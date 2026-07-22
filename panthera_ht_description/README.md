# Panthera HT Description

This package contains the description files for the HighTorque Panthera HT manipulator with parallel gripper.

## 1. Build

```bash
cd ~/ht-deploy-ws
colcon build --packages-select panthera_ht_description panthera_ros2_control --symlink-install
```

## 2. Visualize the robot

### 2.1 Basic Arm Configuration (`type`)

Robot model is defined under `xacro/robot.xacro`. Use **`type`** to switch arm composition:

- `type:=single` (default): **single arm**
- `type:=left`: **left arm only** (prefixed `left_`)
- `type:=right`: **right arm only** (prefixed `right_`)
- `type:=dual`: **dual arm** (both `left_` and `right_`)

**OCS2** (`ocs2_arm_controller`) reads static files under `urdf/` (e.g. `panthera_ht.urdf`, `panthera_ht_dual.urdf`). Mesh paths use `package://panthera_ht_description/meshes/...` so they work on any machine after `colcon install`.

After editing xacro, regenerate URDF:

```bash
./scripts/generate_urdf.sh
```

Examples:

- Single Arm (default)

```bash
source ~/ht-deploy-ws/install/setup.bash
ros2 launch robot_common_launch manipulator.launch.py robot:=panthera_ht
```

- Dual Arm

```bash
source ~/ht-deploy-ws/install/setup.bash
ros2 launch robot_common_launch manipulator.launch.py robot:=panthera_ht type:=dual
```

- Left / Right only

```bash
source ~/ht-deploy-ws/install/setup.bash
ros2 launch robot_common_launch manipulator.launch.py robot:=panthera_ht type:=left
ros2 launch robot_common_launch manipulator.launch.py robot:=panthera_ht type:=right
```

### 2.2 Mount parameters (dual composition)

When `type` is `left/right/dual`, the model uses the following hierarchy:

- `world -> base_link -> body_link`
- `body_link -> left_mount -> left_base_link`
- `body_link -> right_mount -> right_base_link`

You can tune mounting offsets via xacro mappings:

- `body_xyz` / `body_rpy`
- `left_mount_xyz` / `left_mount_rpy`
- `right_mount_xyz` / `right_mount_rpy`

Example (widen arm spacing):

```bash
source ~/ht-deploy-ws/install/setup.bash
ros2 launch robot_common_launch manipulator.launch.py robot:=panthera_ht type:=dual
```

## 3. OCS2 Demo

### 3.1 OCS2 Arm Controller Demo

Mock simulation by default (`hardware:=mock_components`).

```bash
# Single arm (default)
source ~/ht-deploy-ws/install/setup.bash
ros2 launch ocs2_arm_controller demo.launch.py robot:=panthera_ht
```


```bash
# Dual arm planning
source ~/ht-deploy-ws/install/setup.bash
ros2 launch ocs2_arm_controller demo.launch.py robot:=panthera_ht type:=dual
```

```bash
source ~/ht-deploy-ws/install/setup.bash
ros2 launch ocs2_arm_controller demo.launch.py robot:=panthera_ht hardware:=isaac
```

### 3.3 Real robot

Requires submodule `ht-ros2-control` (`panthera_ros2_control` ROS package).
Default real mode is **`full_control`** (OCS2 MIX: position + velocity + effort + kp/kd).
Single and dual arm share one plugin `PantheraHardwareInterface` and one `hightorque_robot::robot`;
motor count is 7 (`Panthera.yaml`) or 14 (`PantheraDual.yaml`) based on `type`.
Gravity feedforward comes from OCS2’s Pinocchio model (`config/ocs2/single.info` / `task.info`,
with grippers in `removeJoints`).

Optional: `control_mode:=pd_control` or `position_velocity` if you only need position-style HI.

```bash
source ~/ht-deploy-ws/install/setup.bash
ros2 launch ocs2_arm_controller demo.launch.py robot:=panthera_ht hardware:=real
```

```bash
# Dual arm
source ~/ht-deploy-ws/install/setup.bash
ros2 launch ocs2_arm_controller demo.launch.py robot:=panthera_ht type:=dual hardware:=real
```

Dual-arm OCS2 uses `config/ocs2/task.info` (`eeFrame` / `eeFrame1`) and merges
`config/ros2_control/common.yaml` + `config/ros2_control/dual.yaml` when `type:=dual`.
Single-arm mode uses `config/ocs2/single.info` and `config/ros2_control/single.yaml`
when `type:=single` (required so launch does not compose dual EEF gripper joints).