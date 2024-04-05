from dataclasses import dataclass


@dataclass
class JointOperation:
    hq_node_index: int
    joint_operation_id: int
    planet_index: int
