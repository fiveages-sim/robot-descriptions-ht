# Robot Descriptions - HighTorque (HT)

HighTorque Panthera HT robot description packages for ROS 2.

## Packages

| Package | Description |
|---------|-------------|
| [`panthera_ht_description`](panthera_ht_description/) | Panthera HT URDF/xacro, meshes, and ros2_control / OCS2 configs |

## Usage

Add this repository as a workspace submodule (recommended path `src/robot-descriptions-ht`). Colcon discovers `panthera_ht_description` under that tree.

```bash
git submodule add -b main git@github.com:fiveages-sim/robot-descriptions-ht.git src/robot-descriptions-ht
```

## Related

- Previous single-package remote: [`panthera_ht_description`](https://github.com/fiveages-sim/panthera_ht_description)
- Shared components: [`robot-descriptions-common`](https://github.com/fiveages-sim/robot-descriptions-common)
