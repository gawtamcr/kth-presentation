"""Replay archived cfm6_n10 STL-FM plans in the OGBench cube env and record mp4s.

Run from CODE/flow-3d with the ogb env. Plans are taken from results/ogbench/single/cfm6_n10/traj,
seeds from results_raw.csv; no planning is re-run.
"""
import csv, os, sys
import numpy as np
import imageio

sys.path.insert(0, os.getcwd())
from scripts.ogbench.run_ogbench import load_config
from scripts.utils.ogb_env import (CubeLimitsNormalizer, make_env, reset_scene, pd_rollout,
                                   to_spec_norm, add_obstacle, move_obstacle, EFF_XYZ)

OUT = sys.argv[1]
RES = "results/ogbench/single/cfm6_n10"
JOBS = [  # (spec_name, npz, spec_string prefix, run_id)
    ("pickplace", "F_pick1__F_place1___0-20__20-100_.npz", "F(pick1)^F(place1)_", int(sys.argv[2])),
    ("hold_and_place", "F_G_pick1__F_G_place1_____0-30__0-10__0-30__0-10_.npz", "F(G(pick1)", int(sys.argv[3])),
    ("pickplace_avoid", "F_pick1__F_place1__G__obs1___0-20__20-100__0-127_.npz", "F(pick1)^F(place1)^G", int(sys.argv[4])),
]

rows = list(csv.DictReader(open(f"{RES}/results_raw.csv")))
dcfg = load_config(name="default")
env = make_env(dcfg["dataset"])
norm = CubeLimitsNormalizer.from_npz(dcfg["normalizer_npz"])

for spec_name, npz, prefix, run_id in JOBS:
    cfg = load_config(name=spec_name)
    row = [r for r in rows if r["method"] == "cube_stl_guided" and r["spec_string"].startswith(prefix)
           and int(r["run_id"]) == run_id]
    assert len(row) == 1, (spec_name, len(row))
    row = row[0]
    d = np.load(f"{RES}/traj/{npz}", allow_pickle=True)
    idx = [i for i in range(len(d["method"])) if d["method"][i] == "cube_stl_guided" and int(d["run_id"][i]) == run_id]
    assert len(idx) == 1
    waypts = np.asarray(d["planned"][idx[0]])
    scene = reset_scene(env, norm, task_id=int(row["task_id"]), env_seed=int(row["env_seed"]))
    if spec_name == "pickplace_avoid":
        gid = add_obstacle(env, f"{spec_name}_obs1", list(cfg["obs1_size"]), list(cfg["obs1_rgba"]))
        move_obstacle(env, gid, (scene.init_metres + scene.goal_metres) / 2.0 + np.asarray(cfg["obs1_offset"]))
    env.reset(seed=int(scene.env_seed), options=dict(task_id=int(row["task_id"]), render_goal=False))
    goals_o = np.array([to_spec_norm(scene.init_metres), to_spec_norm(scene.goal_metres)])
    ro = pd_rollout(env=env, waypoints_o=np.ascontiguousarray(waypts[:, EFF_XYZ]), goals_o=goals_o,
                    kp=float(cfg.get("kp", 5.0)), save_frames=True)
    ex = d["executed"][idx[0]]
    dev = float(np.abs(np.asarray(ro.executed) - np.asarray(ex)).max()) if ex is not None and np.shape(ex) == np.shape(ro.executed) else None
    print(spec_name, "run", run_id, "archived sat", row["sat"], "success", row["task_success"],
          "| replay success", ro.task_success, "frames", len(ro.frames), "max |executed diff|", dev)
    imageio.mimwrite(f"{OUT}/cube_stlfm_{spec_name}.mp4", ro.frames, fps=10)
    imageio.imwrite(f"{OUT}/cube_stlfm_{spec_name}_poster.png", ro.frames[0])
