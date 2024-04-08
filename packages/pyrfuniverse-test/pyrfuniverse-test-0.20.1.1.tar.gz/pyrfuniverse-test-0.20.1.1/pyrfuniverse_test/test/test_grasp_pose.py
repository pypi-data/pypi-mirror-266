import os
from .. import mesh_path
try:
    import pandas as pd
except ImportError:
    print("This feature requires pandas, please install with `pip install pandas`")
    raise
from pyrfuniverse.envs.base_env import RFUniverseBaseEnv
from ..extend.graspsim_attr import GraspSimAttr

mesh_path = os.path.join(mesh_path, "drink1/drink1.obj")
pose_path = os.path.join(mesh_path, "drink1/grasps_rfu.csv")

data = pd.read_csv(pose_path, usecols=["x", "y", "z", "qx", "qy", "qz", "qw"])
data = data.to_numpy()
positions = data[:, 0:3].reshape(-1).tolist()
quaternions = data[:, 3:7].reshape(-1).tolist()

env = RFUniverseBaseEnv(ext_attr=[GraspSimAttr])
grasp_sim = env.InstanceObject(id=123123, name="GraspSim", attr_type=GraspSimAttr)
grasp_sim.ShowGraspPose(
    mesh=os.path.abspath(mesh_path),
    gripper="SimpleFrankaGripper",
    positions=positions,
    quaternions=quaternions,
)

env.Pend()
env.close()
