#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import argparse

import numpy as np
import matplotlib.pyplot as plt
plt.style.use("presentation")

from scipy.interpolate import griddata, interp1d
from scipy.optimize import minimize


def interpolate_string(a, b, t, npts: int=5, concat: bool=False):
    """"""
    # - use transition state
    if concat:
        npts_1 = int(npts/2.)
        npts_2 = npts - npts_1
        pts = np.vstack(
            [
                np.hstack([np.linspace(a[0], t[0], npts_1), np.linspace(t[0], b[0], npts_2)]),
                np.hstack([np.linspace(a[1], t[1], npts_1), np.linspace(t[1], b[1], npts_2)])
            ]
        ).T
    else:
        pts = np.vstack(
            [np.linspace(a[0], b[0], npts), np.linspace(a[1], b[1], npts)]
        ).T

    return pts

def prepare_data(data):
	""""""
	nx = np.size(np.unique(data[:, 0]))
	ny = np.size(np.unique(data[:, 1]))

	# Some people give input where the first column varies fastest. 
	# That is Fortran ordering, and you are liable to get things confused 
	# if you don't take this into account.
	order = "C"
	if data[0, 0] != data[1, 0]:
		order = "F"
	x = data[:, 0].reshape(nx, ny, order=order)
	y = data[:, 1].reshape(nx, ny, order=order)
	z = data[:, 2].reshape(nx, ny, order=order)
	#print(f"x: {x}")
	#print(f"y: {y}")

	# - basic input sanity check
	xdiff = np.diff(x, axis=0)
	ydiff = np.diff(y, axis=1)
	if (not np.all(np.abs(xdiff - xdiff[0]) < 1e-8)) or (not np.all(np.abs(ydiff - ydiff[0]) < 1e-8)):
		print("WARNING! The input data is not coming from an equally spaced grid. imshow will be subtly wrong as a result, as each pixel is assumed to represent the same area.")

	return x, y, z

def optimise_string(pts, gridpoints, gradx, grady, steps=100, stepsize=0.01):
	""""""
	npts = pts.shape[0]
	for i in range(steps):
		# - find gradient interpolation
		Dx = griddata(gridpoints, gradx.flatten(), (pts[:, 0], pts[:, 1]), method="linear")
		Dy = griddata(gridpoints, grady.flatten(), (pts[:, 0], pts[:, 1]), method="linear")
		h = np.amax(np.sqrt(np.square(Dx) + np.square(Dy)))

		# - evolve
		pts -= stepsize * np.vstack([Dx, Dy]).T / h

		# - reparameterize
		arclength = np.hstack([0, np.cumsum(np.linalg.norm(pts[1:] - pts[:-1], axis=1))])
		arclength /= arclength[-1]
		pts = np.vstack(
			[
				interp1d(arclength, pts[:, 0])(np.linspace(0, 1, npts)), 
				interp1d(arclength, pts[:, 1])(np.linspace(0, 1, npts))
			]
		).T

		# - save history?
		if i % 10 == 0:
			#print(i, np.sum(griddata(gridpoints, z.flatten(), (pts[:, 0], pts[:, 1]), method="linear")))
			print(i, np.sum(griddata(gridpoints, z.flatten(), (pts[:, 0], pts[:, 1]), method="linear")))

	return pts

def plot_pathways():
	""""""

	return

# ---
parser = argparse.ArgumentParser()
parser.add_argument("-f", "--file", help="free energy data", default="fes.dat", type=str)
parser.add_argument("-n", "--number", help="number of points", default=11, type=int)
parser.add_argument("-s", "--steps", help="number of steps", default=100, type=int)
parser.add_argument("-c", "--concat", help="interpolate mode", action="store_true")
args = parser.parse_args()

# Use the guessed basins to make the original string, 
# a linear interpolation between points a, t, and b.
npts = args.number #Number of intermediate points on the string.
steps = args.steps
concat = args.concat
fes_dat = args.file

# - preprocess data (load and reshape)
data = np.loadtxt(fes_dat)
print(f"data: {data.shape}")
data[:, 2] /= 96.485

x, y, z = prepare_data(data) # C-order 2D data

gridpoints = np.vstack([x.flatten(), y.flatten()]).T
print(f"grids: {gridpoints.shape}")
gradx, grady = np.gradient(z, np.unique(data[:, 0]), np.unique(data[:, 1]))

# Guesses for where the basins go. Since the input data is malformed, 
# you need to also provide an intermediate point t.
start_points = np.loadtxt("basin.dat").reshape(-1, 3, 2)
print(f"start_points: ")
print(start_points)

for i, (a, b, t) in enumerate(start_points):
	print(f"***** pathway {i} *****")
	pts = interpolate_string(a, b, t, npts=npts, concat=concat)

	# Evolve points so that they respond to the gradients. 
	# This is the "zero temperature string method"
	pts = optimise_string(pts, gridpoints, gradx, grady, steps=steps)
	ene = griddata(gridpoints, z.flatten(), (pts[:, 0], pts[:, 1]), method="linear")[:, np.newaxis]
	np.savetxt(f"./pmf-{i}.dat", np.hstack((np.linspace(0, 1, npts)[:, np.newaxis], pts, ene)), fmt="%.2f")

# ---
fig, ax = plt.subplots(1, 1, figsize=(12, 8))

ax.set_xlabel("CV 1")
ax.set_ylabel("CV 2")
#ax.set_xlim(0., 0.33)
#ax.set_ylim(0., 0.50)
cntr = ax.contourf(
    x, y, z, levels=10,
    #x, np.where(y < 0., y+1.0, y), z, levels=10,
    #cmap="RdBu"
)
fig.colorbar(cntr, ax=ax, label="Free Energy [eV]")
cn = ax.contour(
    x, y, z, #cmap="RdBu"
    #x, np.where(y < 0., y, y+1.0), z, levels=10,
)
plt.clabel(cn, inline=True, fontsize=10)

for i in range(start_points.shape[0]):
	pts = np.loadtxt(f"./pmf-{i}.dat")[:, 1:3]
	ax.plot(
		pts[:, 0], pts[:,1], linestyle="--", label=f"{i}"
	)
if start_points.shape[0] > 1:
    ax.legend()

fig.savefig("demo.png", transparent=False)
#fig.savefig("demo.png", transparent=True)

# --- 
fig, ax = plt.subplots(1, 1, figsize=(12, 8))
for i in range(start_points.shape[0]):
	pts = np.loadtxt(f"./pmf-{i}.dat")[:, 1:3]
	ax.plot(
		np.linspace(0, 1, npts), 
		griddata(gridpoints, z.flatten(), (pts[:, 0], pts[:, 1]), method="linear"),
	    marker="o", label=f"{i}"
	)
ax.legend()

ax.set_ylabel("Free Energy [eV]")
ax.set_xlabel("Reaction Coordinate")
fig.savefig("pmf.png")


if __name__ == "__main__":
	...
