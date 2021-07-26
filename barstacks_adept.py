# Required imports
import os
import numpy as np
import matplotlib as mpl

from matplotlib.ticker import ScalarFormatter
from matplotlib.ticker import MaxNLocator

# Use the pgf backend (must be set before pyplot imported)
# mpl.use('pgf')

import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

#plt.style.use("ggplot")

csfont = {'fontname':'Arial'}

# 
# MPL fonts
#

fm.findSystemFonts(fontpaths=None, fontext='ttf')
flist = fm.get_fontconfig_fonts()
names = [fm.FontProperties(fname=fname).get_name() for fname in flist]
plt.rcParams["font.family"] = ['Arial', 'STIX Math', 'Latin Modern Math', 'TeX Gyre Termes Math, ''DejaVu Serif', 'Liberation Serif', 'Times New Roman']


plt.rcParams['font.size'] = 14

# 
# MPL helpers
#

# markers
markers = ['.', ',', 'o', 'v', '^', '<', '>', '1', '2', '3', '4', 's', 'p', '*', 'h', 'H', '+', 'x', 'D', 'd', '|', '_']
# colors
colors = ['firebrick', 'dimgray', 'royalblue', 'goldenrod', 'violet', 'aqua', 'darkorchid', 'hotpink', 'dodgerblue', 'olive', 'chocolate','indigo', 'orange', 'blue', 'deepskyblue']
# dashes
dashes = ['-', '--', '-.', ':']

mlen = len(markers)
clen = len(colors)
dlen = len(dashes)

# plot the bar charts
def plotBars(Ds, Dc, name='dna_aa'):

    labels = ['Dataset 1', 'Dataset 2', 'Dataset 3']
 
    D1 = np.cumsum(np.array(Ds), axis=1).T
    D2 = np.cumsum(np.array(Dc), axis=1).T
    
    print(D1)
    print(D2)

    x = np.arange(len(labels))  # the label locations
    width = 0.3 # the width of the bars

    fig, ax = plt.subplots(1, 1, figsize=[8, 5])

    af = ax.bar(x - width/2, D1[3], width, edgecolor='k', label='d2h', color = 'tab:blue')
    ar = ax.bar(x - width/2, D1[2], width, edgecolor='k', label='h2d', color='moccasin')
    hd = ax.bar(x - width/2, D1[1], width, edgecolor='k', label='k(rev)', color='salmon')
    dh = ax.bar(x - width/2, D1[0], width, edgecolor='k', label='k(fwd)', color='lightgray')

    af2 = ax.bar(x + width/2, D2[3], width, edgecolor='k', color = 'tab:blue')
    ar = ax.bar(x + width/2, D2[2], width, edgecolor='k', color='moccasin')
    hd = ax.bar(x + width/2, D2[1], width, edgecolor='k', color='indianred')
    dh2 = ax.bar(x + width/2, D2[0], width, edgecolor='k', color='gray')
    
    # Add some text for labels, title and custom x-axis tick labels, etc.
    ax.set_ylabel('time(s)', fontsize=18)
    #ax.set_title('Comparison for Amino Acid Alignment Kernels', fontsize=20)
    ax.set_xticks(x)
    ax.set_yticks([0, 100, 200, 300, 400, 500, 600])
    ax.set_xticklabels(labels)
    ax.legend(fontsize=14, loc='best')
    
    #ax.bar_label(dh, padding=3)
    #ax.bar_label(dh2, padding=3)
    
    fig.tight_layout()
    
    os.makedirs(os.getcwd() +'/plots', exist_ok=True)
    plt.savefig(os.getcwd() +'/plots/' + name + '.pdf', format='pdf', bbox_inches = 'tight', pad_inches = 0.01)

# Protein Kernel Profiling

cuda1 = [71.6818, 20.7368, 0.125776, 0.0646583]
sycl1 = [186.138, 46.4694, 1.11046, 0.164979]

cuda2 = [117.553, 63.9799, 0.154441, 0.0872703]
sycl2 = [300.31, 240.211, 1.77345, 0.209188]

cuda3 = [49.236, 38.4121, 0.492032, 0.0258935]
sycl3 = [124.72, 102.04, 0.728756, 0.0537997]

CU = [cuda1, cuda2, cuda3]
SY = [sycl1, sycl2, sycl3]

# plot bars for amino acid data
plotBars(SY, CU, name = "amino_acid")

# DNA Kernel Profiling

sycl1 = [115.191,35.3759,1.35664,0.197609]
sycl2 = [49.9883,22.4056,0.559024,0.0480585]
sycl3 = [100.548,65.8414,1.12818,0.10884]


cuda1 = [46.5533,17.8212,1.35505,0.131255]
cuda2 = [20.6866,11.2452,0.556793,0.0385761]
cuda3 = [43.7064,27.0484,1.12607,0.071291]

CU = [cuda1, cuda2, cuda3]
SY = [sycl1, sycl2, sycl3]

# plot bars for amino acid data
plotBars(SY, CU, name = "dna")


a1 = np.array(np.sum(np.array(sycl1)), np.sum(np.array(sycl2)), np.sum(np.array(sycl3)))

a2 = np.array(np.sum(np.array(sycl1)) + 2.3124, np.sum(np.array(sycl2))+5.84, np.sum(np.array(sycl3))+3.25)