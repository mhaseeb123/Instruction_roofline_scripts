#!@PYTHON_EXECUTABLE@

# MIT License
#
# Copyright (c) 2020, The Regents of the University of California,
# through Lawrence Berkeley National Laboratory (subject to receipt of any
# required approvals from the U.S. Dept. of Energy).  All rights reserved.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# Import Packages

import os
import argparse
import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

csfont = {'fontname':'STIX Math'}

# 
# MPL fonts
#

fm.findSystemFonts(fontpaths=None, fontext='ttf')
flist = fm.get_fontconfig_fonts()
names = [fm.FontProperties(fname=fname).get_name() for fname in flist]
plt.rcParams["font.family"] = ['STIX Math', 'Times New Roman', 'Latin Modern Math', 'TeX Gyre Termes Math', 'DejaVu Sans', 'DejaVu Serif', 'Liberation Serif']
#print (names)

plt.rcParams['font.size'] = 14

# 
# MPL helpers
#

# markers
markers = ['.', ',', 'o', 'v', '^', '<', '>', '1', '2', '3', '4', 's', 'p', '*', 'h', 'H', '+', 'x', 'D', 'd', '|', '_']
# colors
colors = ['firebrick', 'dimgray', 'royalblue', 'goldenrod', 'violet', 'aqua', 'darkorchid', 'hotpink', 'dodgerblue', 'olive', 'chocolate','indigo', 'orange', 'green', 'deepskyblue']
# dashes
dashes = ['-', '--', '-.', ':']

mlen = len(markers)
clen = len(colors)
dlen = len(dashes)

linestyle_tuple = [
     ('loosely dotted',        (0, (1, 10))),
     ('dotted',                (0, (1, 1))),
     ('densely dotted',        (0, (1, 1))),

     ('loosely dashed',        (0, (5, 10))),
     ('dashed',                (0, (5, 5))),
     ('densely dashed',        (0, (5, 1))),

     ('loosely dashdotted',    (0, (3, 10, 1, 10))),
     ('dashdotted',            (0, (3, 5, 1, 5))),
     ('densely dashdotted',    (0, (3, 1, 1, 1))),

     ('dashdotdotted',         (0, (3, 5, 1, 5, 1, 5))),
     ('loosely dashdotdotted', (0, (3, 10, 1, 10, 1, 10))),
     ('densely dashdotdotted', (0, (3, 1, 1, 1, 1, 1)))]

# --------------------------------------------------------------------------------------------------- #

# 
# make_ceil
#
def make_ceil(ceil1, ceil2, bw, x, max_perf):
    for i in x:
        if (bw * i) < max_perf:
            ceil1.append(bw*i)
            ceil2.append(bw*i)
        else:
            ceil1.append(max_perf)

# --------------------------------------------------------------------------------------------------- #

#
# Auxiliary (empirical) ceilings
#
def makeAuxCeilings(ceil, x, bw, max_perf, mark='s'):
    for i in x:
        if i * bw >= max_perf:
            ceil.append(max_perf)

# --------------------------------------------------------------------------------------------------- #
#
# Function to plot kernel's performance
#
def plotKernelPerf(kname, axs, mark='o', label = True):

    # print the ceiling
    print(f"Ceiling({kname['name']}) = {kname['perf']}")

    # Plot labels
    if (label==True):
        axs.scatter([1e-6],[1e-6], color='red', marker='s', label='L3', zorder=90)
        axs.scatter([1e-6],[1e-6], color='limegreen', marker='s', label='SLM', zorder=90)
        axs.scatter([1e-6],[1e-6], color='mediumblue', marker='s', label='GTI', zorder=90)

    # make label
    axs.scatter([1e-6],[1e-6], marker=mark, label=kname['name'], color='black', edgecolors='black', facecolors='none', linewidths=1.5, zorder=90)

    #
    # Scatter Plots
    #

    # plot no predication performance
    # axs.plot(x, np.full(shape = len(x), fill_value=kname['perf_nopredication']), color='dimgray', linestyle=(0, (5, 5)), linewidth=1.5, zorder = 90)

    # plot l1
    axs.scatter(kname['l3_ii'], kname['perf'], color='red', marker=mark, zorder=100)

    # plot l2
    axs.scatter(kname['slm_ii'], kname['perf'], color='limegreen', marker=mark, zorder=100)

    # plot HBM
    axs.scatter(kname['gti_ii'], kname['perf'], color='mediumblue', marker=mark, zorder=100)

    # plot global (ldst)
    # axs.scatter(kname['global(ldst)'], adept_f['perf(ldst)'], marker=mark, color='darkorange', edgecolors='darkorange', facecolors='none', linewidths=1.5, zorder=150)

# --------------------------------------------------------------------------------------------------- #

# --------------------------------------------------------------------------------------------------- #

#
# Main function
#

#
# Machine parameters
#

# Machine performance
max_perf = 436.67  # 80 SM x 4 warps/SM x 1 inst/cycle x 1.53GHz
integer_ceiling = 219.51  # 80 SM x 4 warps/SM x 1 inst/cycle x 1.38GHz x 16 IPU/32threads
ldst_ceiling = 55.12 # 80 SM x 4 warps/SM x 1 inst/cycle x 1.38GHz x 8 LDSTU/32 threads

# bandwidths
l1_bw = 202.5
l2_bw = 76.8
hbm_bw = 35.05 # HBM bandwidth
shm_bw = 202.43 # transaction size is 128 bytes (4 x 32bytes)

# warpsize
WARPSIZE = 32

#
# Global x-axis
#
x = np.logspace(-2, 4, num=600, base=10)

#
# L1 ceiling
#
ceilingl1 = []
ceilingl1b = []
xl1 = x[x*l1_bw < max_perf]

# make ceiling data
make_ceil(ceilingl1, ceilingl1b, l1_bw, x, max_perf)

# convert to np.arrays
ceilingl1 = np.array(ceilingl1)
ceilingl1b = np.array(ceilingl1b)

#
# L2 ceiling
#
ceilingl2 = []
ceilingl2b = []
xl2 = x[x*l2_bw < max_perf]

make_ceil(ceilingl2, ceilingl2b, l2_bw, x, max_perf)

# convert to np.arrays
ceilingl2 = np.array(ceilingl2)
ceilingl2b = np.array(ceilingl2b)

#
# HBM ceiling
#

ceilinghbm = []
ceilinghbmb = []
xhbm = x[x*hbm_bw < max_perf]

make_ceil(ceilinghbm, ceilinghbmb, hbm_bw, x, max_perf)

# convert to np.arrays
ceilinghbm = np.array(ceilinghbm)
ceilinghbmb = np.array(ceilinghbmb)

#
# Auxiliary Ceilings (int and ldst)
#

# integer ceiling 
int_roof = []
int_x = x[x * l1_bw >= integer_ceiling]
makeAuxCeilings(int_roof, x, l1_bw, integer_ceiling)

# ld_st ceiling
ldst_roof = []
ldst_x = x[x * l1_bw >= ldst_ceiling]
makeAuxCeilings(ldst_roof, x, l1_bw, ldst_ceiling)

#
# Memory Walls
#

# wall at stride-0
val0 = 32/32
#stride0 = np.array([ceilinghbmb[0]/1e8,l1_bw*val0])

# wall at stride-1
val1 = 1/4
#stride1 = np.array([ceilinghbmb[0]/1e8,l1_bw*val1])

# wall at stride-8
val8 = 1/32
#stride8 = np.array([ceilinghbmb[0]/1e8,l1_bw*val8])

#
# Figure for global memory performance
#
fig, ax = plt.subplots(figsize=[9,5])

# plot L1 ceiling
ax.plot(x, ceilingl1, color = 'black', linestyle = '-', linewidth=1.5)
ax.plot(xl1, ceilingl1b, color = 'red', linestyle = '-', linewidth=1.5)

# plot L2 ceiling
ax.plot(x, ceilingl2, color = 'black', linestyle = '-', linewidth=1.5)
ax.plot(xl2, ceilingl2b, color = 'limegreen', linestyle = '-', linewidth=1.5)

# plot HBM ceiling
ax.plot(x, ceilinghbm, color = 'black', linestyle = '-', linewidth=1.5)
ax.plot(xhbm, ceilinghbmb, color = 'mediumblue', linestyle = '-', linewidth=1.5)

# plot auxiliary ceilings
ax.plot(int_x, int_roof, color = 'black', linestyle =(0, (3, 1, 1, 1, 1, 1)), linewidth=1.5)
ax.plot(ldst_x, ldst_roof, color = 'black', linestyle =(0, (3, 1, 1, 1, 1, 1)), linewidth=1.5)

# plot memory walls
#ax.plot(np.array([val0,val0]), stride0, color = 'darkorange', linestyle ='-', linewidth=1.5)
#ax.plot(np.array([val1,val1]), stride1, color = 'darkorange', linestyle ='-', linewidth=1.5)
#ax.plot(np.array([val8,val8]), stride8, color = 'darkorange', linestyle ='-', linewidth=1.5)

#
# Read kernel metrics from NVPROF
#

adept_f = dict([])
adept_r = dict([])

# --------------------------------------------------------------------------------------------- #

# Compute performance in GIPS

# forward kernel (CHANGE ME ONLY)

adept_f['perf']  = 10.585

adept_f['l3_ii']  = 0.508
adept_f['slm_ii']  = 0.475
adept_f['gti_ii'] = 1985.988

# Reverse kernel (CHANGE ME ONLY)

adept_r['perf']  = 9.041

adept_r['l3_ii']  = 0.612
adept_r['slm_ii']  = 0.476
adept_r['gti_ii'] = 1396.03

# --------------------------------------------------------------------------------------------- #

# add kernel name
adept_f['name'] = 'Adept_F'
adept_r['name'] = 'Adept_R'

# plot Adept_F performance
plotKernelPerf(adept_f, ax)

# plot Adept_R performance
plotKernelPerf(adept_r, ax, 'd', False)

#
# Figure Properties
#

# set properties
ax.set_ylabel('Performance (GINTOPS)', fontsize=14)
ax.set_xlabel('Arithmetic Intensity (INT ops per Byte)', fontsize=14)

ax.set_xscale('log', base=10)
ax.set_yscale('log', base=10)

ax.grid(axis = 'y', linewidth='0.5', linestyle=':', which='both')


ax.set_ylim(bottom=1e-1, top=1.3e3, emit=True)
ax.set_xlim(left=1e-2, right=1.3e4, emit=True)

ax.set_xticks([1e-2, 1e0, 1e2, 1e4])
ax.set_yticks([1e-1, 1e-1, 1e0, 1e1, 1e2, 1e3])

ax.tick_params(axis="x", direction="in")
ax.tick_params(axis="y", direction="in")

ax.set_axisbelow(True)

ax.legend(loc='best', fontsize=12, ncol=2)
fig.show()

fig.savefig("./intel_roof_protein.pdf", format='pdf', dpi=300, bbox_inches = 'tight', pad_inches = 0.02)