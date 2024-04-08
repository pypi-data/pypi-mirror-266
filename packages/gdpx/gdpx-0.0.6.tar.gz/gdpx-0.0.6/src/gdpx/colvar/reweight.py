#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import pathlib

import numpy as np

from ase.io import read, write


def cut_frames(p, beg_step=0, end_step=5000000, period=500):
    """"""
    frames = read(p, ":")

    #return frames[int(beg_step/period):int(end_step/period)+1]
    return frames[beg_step:end_step+1]

def get_colvars(p, beg_step, end_step, period=500):
    """"""
    colvars = np.loadtxt(p)

    #return colvars[:int(maxstep/period), 1:3] # pos.a, pos.b
    #return colvars[int(beg_step/period)+1:int(end_step/period)+1, 4:6] # sx, sy
    return colvars[beg_step:end_step+1, 4:6] # sx, sy

def get_frames(p, beg_step=0, end_step=5000000, period=500):
    """"""
    p = pathlib.Path(p)
    frames = cut_frames(
        p/"traj.dump", beg_step=0, end_step=end_step-beg_step, period=period
    )
    nframes = len(frames)
    print(f"nframes: {nframes}")

    # NOTE: COLVAR has accumulated steps
    colvars = get_colvars(p/"COLVAR", beg_step, end_step, period=period)
    print(f"colvars: {colvars.shape}")
    #print(colvars)

    for a, cv in zip(frames, colvars):
        a.info["colvar"] = "{},{}".format(*cv)
    #write(p/"traj.xyz", frames)

    return frames

#frames = []
#curr_frames = get_frames("./0000.run", end_step=20000, period=250)
#frames.extend(curr_frames)
#
#curr_frames = get_frames("./0001.run", beg_step=20001, end_step=40001, period=255)
#frames.extend(curr_frames[1:])
#
#curr_frames = get_frames("./0002.run", beg_step=40002, end_step=60002, period=255)
#frames.extend(curr_frames[1:])
#
#write("traj.xyz", frames)

frames = read("traj.xyz", ":")
colvars = np.array(
    [a.info["colvar"] for a in frames], dtype=np.float32
)

nframes = len(frames)
print(f"nframes: {nframes}")
print(f"colvars: {colvars.shape}")

coordinates = np.loadtxt("./0002.run/fes/path.txt")
print(coordinates)

nbins = 10
size = 24 # 128
eps = 0.05 # eps = 0.05

groups = [[] for _ in range(nbins)]
for i, (com_x, com_y) in enumerate(colvars):
    for j, (x, y) in enumerate(coordinates):
        if x-eps < com_x < x+eps and y-eps < com_y < y+eps:
            #print(com_x, com_y)
            groups[j].append(i)
print([len(_) for _ in groups])
print(sum([len(_) for _ in groups]))

content = ""
for i, x in enumerate(groups):
    content += " ".join([str(_) for _ in x]) + "\n"

with open("eps.txt", "w") as fopen:
    fopen.write(content)

rng = np.random.default_rng(1112)

selected_indices = []
for g in groups:
    s = rng.choice(g, size=size, replace=False).tolist()
    print(s)
    selected_indices.extend(s)
nselected = len(selected_indices)
print(f"nselected: {nselected}")

selected_frames = [frames[i] for i in selected_indices]
write("frames_to_reweight.xyz", selected_frames)


if __name__ == "__main__":
    ...