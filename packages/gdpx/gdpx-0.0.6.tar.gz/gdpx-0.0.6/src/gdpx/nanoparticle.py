#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import numpy as np


import matplotlib as mpl
mpl.use("Agg") #silent mode
from matplotlib import pyplot as plt
plt.style.use("presentation")


from ase.io import read, write


def project_positions(pos, positions):
    """"""
    sigma = 0.05
    intensity = np.sum(
        np.exp(-np.linalg.norm(pos - positions[:, :2], axis=1)**2/(2*sigma**2))
    )

    return intensity


def compute_nanoparticle_distribution():
    """"""
    atoms = read("/scratch/gpfs/jx1279/copper+alumina/dptrain/r9/_prod/Cu13+s001p32.xyz")

    # - find all copper atoms
    group_indices = [i for i, a in enumerate(atoms) if a.symbol == "Cu"]
    print(group_indices)

    # - 
    positions = atoms.positions[group_indices, :]
    print(positions)

    x, y = np.linspace(0, 15, 301), np.linspace(0, 15, 301)
    grid = np.meshgrid(x, y)
    pairs = np.array(list(zip(grid[0].flatten(), grid[1].flatten())))
    print(pairs)
    print(pairs.shape)

    intensities = [project_positions(pos, positions) for pos in pairs]
    print(intensities)

    # - plot
    fig, ax = plt.subplots(1, 1, figsize=(12, 8))
    cntr = ax.contour(x, y, np.reshape(intensities, (301, 301)))
    fig.colorbar(cntr)
    plt.savefig("./xxx.png")

    return


from jax import numpy as jnp
from jax import grad, value_and_grad

def circle_fit_kasa(positions):
    """"""
    n = positions.shape[0]

    #z = jnp.reshape(positions[:, 0]**2 + positions[:, 1]**2, (-1,1))
    z = positions[:, 0]**2 + positions[:, 1]**2
    print(f"z: {z}")

    xy1 = jnp.hstack((positions, jnp.ones((n, 1))))
    print(xy1)

    s = jnp.linalg.solve(xy1, z)

    #return (s[0]/2., s[1]/2., jnp.sqrt((s[0]**2+s[1]**2)/4.+s[2]))
    return jnp.sqrt((s[0]**2+s[1]**2)/4.+s[2])

dfn = value_and_grad(circle_fit_kasa, argnums=0)


def xxx():
    """"""
    positions = np.array(
        [[0, 0], [1, 1.1], [1, -0.9], [0, 2]], dtype=np.float32
        #[[0, 0], [1, 1.1], [0, 2]], dtype=np.float32
        #[[0, 0], [0, 2]], dtype=np.float32
    )
    
    params = circle_fit_kasa(positions=positions)
    print(params)

    #p = dfn(positions)
    #print(p)

    return


if __name__ == "__main__":
    #compute_nanoparticle_distribution()
    xxx()
    ...