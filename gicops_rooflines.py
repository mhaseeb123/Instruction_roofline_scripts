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
#flist = fm.get_fontconfig_fonts()
#names = [fm.FontProperties(fname=fname).get_name() for fname in flist]
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
def plotKernelPerf(kname, axs, mark='s', label = True):

    #
    # Compute Instruction Intensities
    #

    # Compute Instruction Intensity (L1)
    kname['l1_ii'] = kname['smsp__thread_inst_executed.sum'] / (WARPSIZE * (kname['l1tex__t_sectors_pipe_lsu_mem_global_op_ld.sum'] + kname['l1tex__t_sectors_pipe_lsu_mem_global_op_st.sum'] + kname['l1tex__t_sectors_pipe_lsu_mem_local_op_ld.sum'] + kname['l1tex__t_sectors_pipe_lsu_mem_local_op_st.sum'] + 4 * (kname['l1tex__data_pipe_lsu_wavefronts_mem_shared_op_ld.sum'] + kname['l1tex__data_pipe_lsu_wavefronts_mem_shared_op_st.sum'])))

    # Compute Instruction Intensity (L2)
    # kname['l2_ii'] = kname['smsp__thread_inst_executed.sum'] / (WARPSIZE * (kname['lts__t_sectors_op_read.sum'] + kname['lts__t_sectors_op_atom.sum'] + kname['lts__t_sectors_op_red.sum'] + kname['lts__t_sectors_op_write.sum'] + kname['lts__t_sectors_op_atom.sum'] + kname['lts__t_sectors_op_red.sum']))

    # Compute Instruction Intensity (dram)
    kname['dram_ii'] = kname['smsp__thread_inst_executed.sum'] / (WARPSIZE * (kname['dram__sectors_read.sum'] + kname['dram__sectors_write.sum']))

    # Compute Global (ld/st) performance
    kname['perf(ldst)'] = (kname['smsp__inst_executed_op_global_ld.sum'] + kname['smsp__inst_executed_op_global_st.sum']) / (1e9 * kname['runtime'])

    # Compute Instruction Intensity (L1) for Mem Wall
    kname['global(ldst)'] = (kname['smsp__inst_executed_op_global_ld.sum'] + kname['smsp__inst_executed_op_global_st.sum']) / (kname['l1tex__t_sectors_pipe_lsu_mem_global_op_ld.sum'] + kname['l1tex__t_sectors_pipe_lsu_mem_global_op_st.sum'])

    print(f"Ceiling({kname['name'].value}) = {kname['perf'].value}")
    print(f"NoPredication({kname['name'].value}) = {kname['perf_nopredication'].value}")

    # Plot labels
    if (label==True):
        axs.scatter([1e-6],[1e-6], color='red', marker='o', label='L1 (tot_inst)', zorder=90)
        # axs.scatter([1e-6],[1e-6], color='limegreen', marker='o', label='L2 (tot_inst)', zorder=90)
        axs.scatter([1e-6],[1e-6], color='mediumblue', marker='o', label='DRAM (tot_inst)', zorder=90)
        axs.scatter([1e-6],[1e-6], color='darkorange', marker='o', label='Global (ldst)', zorder=90)

    # make label (only for multiple kernels)
    axs.scatter([1e-6],[1e-6], marker=mark, label=kname['name'].value, color='black', edgecolors='black', facecolors='none', linewidths=1.5, zorder=90)

    #
    # Scatter Plots
    #

    # plot no predication performance
    axs.plot(x, np.full(shape = len(x), fill_value=kname['perf_nopredication']), color='dimgray', linestyle=(0, (5, 5)), linewidth=1.5, zorder = 90)

    # plot l1
    axs.scatter(kname['l1_ii'], kname['perf'], color='red', marker=mark, zorder=100)

    # plot l2
    # axs.scatter(kname['l2_ii'], kname['perf'], color='limegreen', marker=mark, zorder=100)

    # plot dram
    axs.scatter(kname['dram_ii'], kname['perf'], color='mediumblue', marker=mark, zorder=100)

    # plot global (ldst)
    axs.scatter(kname['global(ldst)'], spspgemm['perf(ldst)'], marker=mark, color='darkorange', edgecolors='darkorange', facecolors='none', linewidths=1.5, zorder=150)

# --------------------------------------------------------------------------------------------------- #

#
# Function to plot kernel's shared memory performance
#
def plotSharedPerf(kname, axs, mark='o', label=True):

    # Plot labels
    if (label==True):
        axs.scatter([1e-6],[1e-6], color='darkorchid', marker='s', label='Shared (ldst_inst)', zorder=90)

    # make label (only for multiple kernels)
    axs.scatter([1e-6],[1e-6], marker=mark, label=kname['name'].value, color='black', edgecolors='black', facecolors='none', linewidths=1.5, zorder=90)

    # plot performance
    kname['shm_perf'] = (kname['smsp__inst_executed_op_shared_ld_pred_on_any.sum'] + kname['smsp__inst_executed_op_shared_st_pred_on_any.sum']) / (1e9 * kname['runtime'])

    kname['shm_ii'] = (kname['smsp__inst_executed_op_shared_ld_pred_on_any.sum'] + kname['smsp__inst_executed_op_shared_st_pred_on_any.sum']) / (kname['l1tex__data_pipe_lsu_wavefronts_mem_shared_op_ld.sum'] + kname['l1tex__data_pipe_lsu_wavefronts_mem_shared_op_st.sum'])

    axs.scatter(kname['shm_ii'], kname['shm_perf'], marker=mark, color='darkorchid', edgecolors='darkorchid', facecolors='none', linewidths=1.5, zorder=150)

# --------------------------------------------------------------------------------------------------- #

#
# Main function
#

# The main function
if __name__ == '__main__':

    # initialize arg parser
    parser = argparse.ArgumentParser(description='Instruction Rooflines for the Adept kernel(s)')

    # SpSpGEMM (open) CSV file
    parser.add_argument('-o', dest='opath', type=str, required=True,
                        help='Path to SpSpGEMM (open) csv file')

    # SpSpGEMM (open) kernel runtime
    parser.add_argument('-ot', '--otime', dest='gtime', type=float, required=True,
                        help='SpSpGEMM (open) kernel runtime in milliseconds (see: output_extended/clean.log)')
    
    # SpSpGEMM (restricted) kernel runtime
    parser.add_argument('-rt', '--rtime', dest='rtime', type=float, required=True,
                        help='SpSpGEMM (restricted) kernel runtime in milliseconds (see: output_extended/clean.log)')

    # SpSpGEMM (restricted) CSV file
    parser.add_argument('-r', '--idir', dest='rpath', type=str, required=True,
                        help='Path to SpSpGEMM (restricted) csv file')

    # parse arguments
    args = parser.parse_args()

    # path to the open CSV file
    fpath = args.opath.lstrip(' ').rstrip(' ')
    fpath = os.path.expanduser(fpath)

    # check if file exists
    if not os.path.exists(fpath):
        print ('ERROR: SpSpGEMM (open) CSV file does not exist\n')
        sys.exit (-1)

    # path to the SpSpGEMM (restricted) CSV file
    rpath = args.rpath.lstrip(' ').rstrip(' ')
    rpath = os.path.expanduser(rpath)

    # check if file exists
    if not os.path.exists(rpath):
        print ('ERROR: SpSpGEMM (restricted) CSV file does not exist\n')
        sys.exit (-1)
    #
    # Kernel runtimes
    #

    # runtime of open kernel
    spspgemm_runtime = args.gtime * 1e-3
    
    # runtime of restricted kernel
    spspr_runtime = args.rtime * 1e-3

    if (spspgemm_runtime <= 0 or spspr_runtime <= 0):
        print ('ERROR: --otime and --rtime must be > 0')
        sys.exit (-2)

    #
    # Machine parameters
    #

    # Machine performance
    # NVIDIA RTX A6000 48GB
    max_perf = 84 * 4 * 1 * 1.8  # 84 SM x 4 warps/SM x 1 inst/cycle x 1.8GHz (boost clock)
    integer_ceiling = 84 * 4 * 1 * 1.8 * 0.5  # 80 SM x 4 warps/SM x 1 inst/cycle x 1.41GHz x 16 IPU/32threads
    ldst_ceiling = 80 * 4 * 1 * 1.8 * 0.125 # 80 SM x 4 warps/SM x 1 inst/cycle x 1.41GHz x 4 LDSTU/32 threads

    # bandwidths
    l1_bw = 3.7725 * 1e3 / 32 # GB/s / Transaction size
    #l2_bw = 2.9968 * 1e3 / 32 # GB/s / Transaction size
    dram_bw = 698/32 # dram bandwidth
    shm_bw = l1_bw / 4 # transaction size is 128 bytes (4 x 32bytes)

    # warpsize
    WARPSIZE = 32

    #
    # Global x-axis
    #
    x = np.logspace(-4, 6, num=600, base=10)

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
    #ceilingl2 = []
    #ceilingl2b = []
    #xl2 = x[x*l2_bw < max_perf]

    #make_ceil(ceilingl2, ceilingl2b, l2_bw, x, max_perf)

    # convert to np.arrays
    #ceilingl2 = np.array(ceilingl2)
    #ceilingl2b = np.array(ceilingl2b)

    #
    # dram ceiling
    #

    ceilingdram = []
    ceilingdramb = []
    xdram = x[x*dram_bw < max_perf]

    make_ceil(ceilingdram, ceilingdramb, dram_bw, x, max_perf)

    # convert to np.arrays
    ceilingdram = np.array(ceilingdram)
    ceilingdramb = np.array(ceilingdramb)

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
    stride0 = np.array([ceilingdramb[0]/1e8,l1_bw*val0])

    # wall at stride-1
    val1 = 1/4
    stride1 = np.array([ceilingdramb[0]/1e8,l1_bw*val1])

    # wall at stride-8
    val8 = 1/32
    stride8 = np.array([ceilingdramb[0]/1e8,l1_bw*val8])

    #
    # Figure for global memory performance
    #
    fig, ax = plt.subplots(figsize=[9,5])

    # plot L1 ceiling
    ax.plot(x, ceilingl1, color = 'black', linestyle = '-', linewidth=1.5)
    ax.plot(xl1, ceilingl1b, color = 'red', linestyle = '-', linewidth=1.5)

    # plot L2 ceiling
    #ax.plot(x, ceilingl2, color = 'black', linestyle = '-', linewidth=1.5)
    #ax.plot(xl2, ceilingl2b, color = 'limegreen', linestyle = '-', linewidth=1.5)

    # plot dram ceiling
    ax.plot(x, ceilingdram, color = 'black', linestyle = '-', linewidth=1.5)
    ax.plot(xdram, ceilingdramb, color = 'mediumblue', linestyle = '-', linewidth=1.5)

    # plot auxiliary ceilings
    # ax.plot(int_x, int_roof, color = 'black', linestyle =(0, (3, 1, 1, 1, 1, 1))), linewidth=1.5)
    # ax.plot(ldst_x, ldst_roof, color = 'black', linestyle =(0, (3, 1, 1, 1, 1, 1))), linewidth=1.5)

    # plot memory walls
    ax.plot(np.array([val0,val0]), stride0, color = 'darkorange', linestyle ='-', linewidth=1.5)
    ax.plot(np.array([val1,val1]), stride1, color = 'darkorange', linestyle ='-', linewidth=1.5)
    ax.plot(np.array([val8,val8]), stride8, color = 'darkorange', linestyle ='-', linewidth=1.5)

    #
    # Read kernel metrics from NCU
    #

    spspgemm = pd.read_csv(fpath, sep=',', names=['metric', 'value'], dtype={'value': np.float64}).set_index('metric').transpose()
    spspr = pd.read_csv(rpath, sep=',', names=['metric', 'value'], dtype={'value': np.float64}).set_index('metric').transpose()

    # add kernel runtimes
    spspgemm['runtime'] = spspgemm_runtime
    spspr['runtime'] = spspr_runtime

    # Compute performance in GIPS
    spspgemm['perf']  = spspgemm['smsp__thread_inst_executed.sum'] / (WARPSIZE * 1e9 * spspgemm['runtime'])
    spspr['perf']  = spspr['smsp__thread_inst_executed.sum'] / (WARPSIZE * 1e9 * spspr['runtime'])

    # Compute unpredicated performance in GIPS
    spspgemm['perf_nopredication'] = spspgemm['smsp__inst_executed.sum'] / (1e9 * spspgemm['runtime'])
    spspr['perf_nopredication'] = spspr['smsp__inst_executed.sum'] / (1e9 * spspr['runtime'])

    # add kernel name
    spspgemm['name'] = 'DBSearch (open)'
    spspr['name'] = 'DBSearch (closed)'

    # plot SpSpGEMM performance
    plotKernelPerf(spspgemm, ax)

    # plot SpSpGEMM performance
    plotKernelPerf(spspr, ax, mark='d', label=False)

    #
    # Figure Properties
    #

    # set properties
    ax.set_ylabel('Performance (warp GIPS)', fontsize=14)
    ax.set_xlabel('Instruction Intensity (Warp Instructions per Transaction)', fontsize=14)

    ax.set_xscale('log', base=10)
    ax.set_yscale('log', base=10)

    ax.grid(axis = 'both', linewidth='0.5', linestyle=':', which='both')


    ax.set_ylim(bottom=1e-3, top=1.3e3, emit=True)
    ax.set_xlim(left=1e-4, right=1.3e4, emit=True)

    ax.set_xticks([1e-4, 1e-2, 1e0, 1e2, 1e4, 1e6])
    ax.set_yticks([1e-2, 1e-1, 1e0, 1e1, 1e2, 1e3])

    ax.tick_params(axis="x", direction="in")
    ax.tick_params(axis="y", direction="in")

    ax.set_axisbelow(True)

    ax.legend(loc='best', fontsize=12, ncol=2)
    fig.show()

    # save figure
    fig.savefig('./spspgemm.pdf', format='pdf', dpi=300, bbox_inches = 'tight', pad_inches = 0.02)


    # --------------------------------------------------------------------------------------------------- #

    #
    # Shared Memory
    #

    # Shared Memory ceilings data
    shm_ceil = []
    shm_ceil2 = []

    # x axis for shared memory
    xshm = x[x*shm_bw < max_perf]

    # make shared memory ceiling
    make_ceil(shm_ceil, shm_ceil2, shm_bw, x, max_perf)

    # convert to np.arrays
    shm_ceil = np.array(shm_ceil)
    shm_ceil2 = np.array(shm_ceil2)

    #
    # Memory Walls
    #

    # wall at no conflict
    val0 = 1
    noconflict = np.array([shm_ceil[0]/1e8, shm_bw*val0])

    # wall at 32-way conflict
    val32 = 1/32
    allconflict = np.array([shm_ceil[0]/1e8, shm_bw*val32])

    #
    # Figure for shared memory plot
    #

    fig2, ax2 = plt.subplots(figsize=[9,5])
    
    # plot the shared memory ceiling
    ax2.plot(x, shm_ceil, color = 'black', linestyle = '-', linewidth=1.5)
    ax2.plot(xshm, shm_ceil2, color = 'darkorchid', linestyle = '-', linewidth=1.5)

    # plot the memory walls
    ax2.plot(np.array([val0,val0]), noconflict, color = 'darkorchid', linestyle ='-', linewidth=1.5)
    ax2.plot(np.array([val32,val32]), allconflict, color = 'darkorchid', linestyle ='-', linewidth=1.5)


    # plot shared memory performance
    plotSharedPerf(spspgemm, ax2, 'o', True)
    plotSharedPerf(spspr, ax2, 'd', False)

    #
    # Figure Properties
    #

    # set properties
    ax2.set_ylabel('Performance (warp GIPS)', fontsize=14)
    ax2.set_xlabel('Instruction Intensity (Warp Instructions per Transaction)', fontsize=14)

    ax2.set_xscale('log', base=10)
    ax2.set_yscale('log', base=10)

    ax2.grid(axis = 'both', linewidth='0.5', linestyle='--', which='both')

    ax2.set_ylim(bottom=1e-2, top=1.3e3, emit=True)
    ax2.set_xlim(left=1e-4, right=1e4, emit=True)

    ax2.set_xticks([1e-2, 1e0, 1e2, 1e4, 1e6])
    ax2.set_yticks([1e-1, 1e0, 1e1, 1e2, 1e3])

    ax2.tick_params(axis="x", direction="in")
    ax2.tick_params(axis="y", direction="in")

    ax2.set_axisbelow(True)

    ax2.legend(loc='lower right', fontsize=12, ncol=1)
    fig2.show()

    # save figure
    fig2.savefig('./spspgemm_shared.pdf', format='pdf', dpi=300, bbox_inches = 'tight', pad_inches = 0.01)