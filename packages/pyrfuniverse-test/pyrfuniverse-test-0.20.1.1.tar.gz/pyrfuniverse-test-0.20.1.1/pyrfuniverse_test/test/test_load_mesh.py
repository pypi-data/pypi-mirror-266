import random
import os
from pyrfuniverse.envs.base_env import RFUniverseBaseEnv
from .. import mesh_path

env = RFUniverseBaseEnv()
env.step()
mesh = env.LoadMesh(
    path=os.path.join(mesh_path, "002_master_chef_can/google_16k/textured.obj")
)
mesh.SetTransform(
    position=[0, 1, 0],
    rotation=[random.random() * 360, random.random() * 360, random.random() * 360],
)

for i in range(100):
    env.step(20)
    new_mesh = mesh.Copy(new_id=mesh.id + i + 1)
    new_mesh.SetTransform(
        position=[0, 1, 0],
        rotation=[random.random() * 360, random.random() * 360, random.random() * 360],
    )
env.Pend()
