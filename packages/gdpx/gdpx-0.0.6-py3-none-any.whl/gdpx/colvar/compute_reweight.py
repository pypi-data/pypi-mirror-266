#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import pathlib

import numpy as np

from ase.units import kB
from ase.io import read, write


def compute_diff(endiffs, temp=600):
    """"""
    beta = 1./(kB*temp)
    print(beta)
    print(np.average(np.exp(-beta*endiffs), axis=1))

    return (-beta**-1)*np.log(np.average(np.exp(-beta*endiffs), axis=1))


def reweight():
    frames = read(f"./post/bin_{step}.xyz", ":")
        
    nframes = len(frames)
    print(f"nframes: {nframes}")
    energies_dft = np.array([a.get_potential_energy() for a in frames])
    
    dp_frames = read(f"./post/bin_{step}/_data/2194d49907edfec2363c7f2619662c62_cache.xyz", ":")
    #dp_frames = read("./post/bin_5/_data/f62ddad7513a99cffa4fac6a3712fe46_cache.xyz", ":")
    nframes_dp = len(dp_frames)
    energies_dp = np.array([a.get_potential_energy() for a in dp_frames])
    print(energies_dft-energies_dp)
    
    assert nframes == nframes_dp
    
    #endiff = energies_dft - energies_dp
    endiff = np.array([0.3, 0.2, 0.1, 0.0, -0.1, -0.2, -0.3])
    
    print(compute_diff(endiff))

    return


wdir = pathlib.Path("./_spc/")
post = pathlib.Path("./post/")

steps = range(20)
binwidth = 64

for step in steps:
    print(f"step: {step}")
    if not (post/"bins"/f"bin_{step}.xyz").exists():
        confids = [i+step*binwidth for i in range(binwidth)]
        if any([not (wdir/f"cand{i}").exists() for i in confids]):
            print("NOT FINISHED!!!")
            continue
        
        frames = []
        for i in confids:
            frames.append(read(wdir/f"cand{i}"/"vasprun.xml"))
        write(post/"bins"/f"bin_{step}.xyz", frames)
    else:
        print("EXTRACTED !!!")

print("=====")

endiffs = []
for step in steps:
    print(f"step: {step}")
    if (post/f"bin_{step}"/"results"/"end_frames.xyz").exists():
        #print("FOUND !!!")
        dft_frames = read(post/"bins"/f"bin_{step}.xyz", ":")
        dft_energies = np.array([a.get_potential_energy() for a in dft_frames])
        dp_frames = read(post/f"bin_{step}"/"results"/"end_frames.xyz", ":")
        dp_energies = np.array([a.get_potential_energy() for a in dp_frames])
        endiffs.append(dft_energies - dp_energies)
    else:
        print("ZEROD!!!")
        endiffs.append(np.zeros((binwidth,)))
endiffs = np.array(endiffs)
np.savetxt("./diff.txt", endiffs, fmt="%8.4f")
#print(endiffs)
print("avg: ", np.average(endiffs, axis=1))
print("std: ", np.sqrt(np.var(endiffs, axis=1)))

weights = compute_diff(endiffs, temp=600)
for i in [4, 9, 13, 14, 19]:
    weights[i] = np.nan
print(weights)


if __name__ == "__main__":
    ...
