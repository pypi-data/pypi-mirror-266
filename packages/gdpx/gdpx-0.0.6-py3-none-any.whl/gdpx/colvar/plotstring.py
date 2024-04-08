#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
import matplotlib.pyplot as plt
plt.style.use("presentation")

from scipy.interpolate import griddata, interp1d
from scipy.optimize import minimize

# Load and reshape the data
#data = np.loadtxt("data.txt")
data = np.loadtxt("fes.dat")
print(f"data: {data.shape}")
data[:, 2] /= 96.485

# Guesses for where the basins go. Since the input data is malformed, 
# you need to also provide an intermediate point t.
#a = (-0.05, 0.25)
#b = (0.3, 0.25)
#t = (0.2, 0.1) #Transition basin
#a = (0.00, 0.05)
#b = (0.33, 0.05)
#t = (0.17, 0.05) #Transition basin
#a = (0.06, 0.00)
#b = (0.06, 0.50)
#t = (0.06, 0.25) #Transition basin
a = (0.28, 0.05)
b = (0.33, 0.05)
t = (0.30, 0.05) #Transition basin
npts = 10 #Number of intermediate points on the string.

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

# Basic input sanity check.
xdiff = np.diff(x, axis=0)
ydiff = np.diff(y, axis=1)
if (not np.all(np.abs(xdiff - xdiff[0]) < 1e-8)) or (not np.all(np.abs(ydiff - ydiff[0]) < 1e-8)):
	print("WARNING! The input data is not coming from an equally spaced grid. imshow will be subtly wrong as a result, as each pixel is assumed to represent the same area.")

gridpoints = np.vstack([x.flatten(), y.flatten()]).T
print(f"grids: {gridpoints.shape}")

# Make a figure and a axes
fig, ax = plt.subplots(1, 1, figsize=(12, 8))

# Use the guessed basins to make the original string, 
# a linear interpolation between points a, t, and b.
pts = np.vstack(
	[
		np.hstack([np.linspace(a[0], t[0], npts), np.linspace(t[0], b[0], npts)]),
		np.hstack([np.linspace(a[1], t[1], npts), np.linspace(t[1], b[1], npts)])
	]
).T
gradx, grady = np.gradient(z, np.unique(data[:,0]), np.unique(data[:,1]))
# Evolve points so that they respond to the gradients. 
# This is the "zero temperature string method"
stepmax = 100
for i in range(stepmax):
	#Find gradient interpolation
	Dx = griddata(gridpoints,gradx.flatten(),(pts[:,0],pts[:,1]), method='linear')
	Dy = griddata(gridpoints,grady.flatten(),(pts[:,0],pts[:,1]), method='linear')
	h = np.amax(np.sqrt(np.square(Dx)+np.square(Dy)))
	# Evolve
	pts -= 0.01 * np.vstack([Dx,Dy]).T / h
	# Reparameterize
	arclength = np.hstack([0,np.cumsum(np.linalg.norm(pts[1:] - pts[:-1],axis=1))])
	arclength /= arclength[-1]
	pts = np.vstack([interp1d(arclength,pts[:,0])(np.linspace(0,1,2*npts)), interp1d(arclength,pts[:,1])(np.linspace(0,1,2*npts))]).T
	if i % 10 == 0:
		print(i, np.sum(griddata(gridpoints, z.flatten(), (pts[:, 0], pts[:, 1]), method="linear")))
		# This draws the intermediate states to visualize how the string evolves.
		#ax.plot(pts[:, 0], pts[:, 1], color=plt.cm.spring(i/float(stepmax)))
		ax.plot(pts[:, 0], pts[:, 1], ls="--")

np.savetxt("./path.txt", pts, fmt="%.2f")
ax.plot(pts[:, 0], pts[:,1], color="k", linestyle="--") # converged pathway?

#heatmap = ax.imshow(
#	z.T, cmap=plt.cm.rainbow, vmin = np.nanmin(z), 
#	vmax=1.2 * np.nanmax(griddata(gridpoints,z.flatten(),(pts[:,0],pts[:,1]), method='linear')), 
#	origin='lower', aspect='auto', extent = (x[0][0], x[-1][-1],y[0][0], y[-1][-1]), 
#	interpolation="bicubic"
#)
#heatmap.cmap.set_over('white')
#ax.autoscale(False)
#bar = fig.colorbar(heatmap)
#bar.set_label("Free Energy [eV]", rotation=90, fontsize=12)
ax.set_xlabel("CV 1")
ax.set_ylabel("CV 2")
ax.set_xlim(0., 0.33)
ax.set_ylim(0., 0.50)
#cntr = ax.contourf(
#    x, y, z, levels=10,
#    #x, np.where(y < 0., y+1.0, y), z, levels=10,
#    #cmap="RdBu"
#)
#fig.colorbar(cntr, ax=ax, label="Free Energy [eV]")
#cn = ax.contour(
#    x, y, z, #cmap="RdBu"
#    #x, np.where(y < 0., y, y+1.0), z, levels=10,
#)
#plt.clabel(cn, inline=True, fontsize=10)

#ax.xaxis.set_ticks([1.25,1.50,1.75,2.0,2.25,2.50,2.75,3.0,3.25])
#ax.yaxis.set_ticks([1.25,1.50,1.75,2.0,2.25,2.50,2.75])
fig.savefig("demo.png", transparent=True)
#FYI this can also save .pdf or .svg or .eps, if you want to go in a vectorly direction.

# --- 
fig, ax = plt.subplots(1, 1, figsize=(12, 8))
ax.plot(
	np.linspace(0, 1, 2*npts), 
	griddata(gridpoints, z.flatten(), (pts[:, 0], pts[:, 1]), method="linear"),
    marker="o"
)
ax.set_ylabel("Free Energy [eV]")
ax.set_xlabel("Reaction Coordinate")
fig.savefig("pmf.png")

if __name__ == "__main__":
	...
