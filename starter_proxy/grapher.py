#!/usr/bin/python

import sys
import numpy as np
import matplotlib as mpl
mpl.use('agg')
import matplotlib.pyplot as plt
import operator
from collections import defaultdict

USAGE = "%s <netsim-log> <logfile-0> <logfile-1>" % sys.argv[0]

def fairness(x,y):
    x = float(x)
    y = float(y)
    return ((x+y)*(x+y)) / (2*((x*x)+(y*y)))

if len(sys.argv) < 4:
    print USAGE
    exit(-1)

nsl = open(sys.argv[1]).read().split('\n')[:-1]

lfs = []
for i in xrange(2,len(sys.argv)):
    lfs.append(open(sys.argv[i]).read().split('\n')[:-1])


# Get BR
BRs = defaultdict(list)
TPUTs = defaultdict(list)
for i,lf in enumerate(lfs):
    for l in lf:
        (t, dur, t_new, avg, br, ip, seg) = l.split(' ')
        t = int(float(t))
        if t in BRs and [m for m in BRs[t] if m[0] == i]:
            # already have an entry at this second
            continue
        BRs[t].append((i,int(float(br))))
        
        dur = float(dur)
        t_new = float(t_new)
        while dur > 1:
            TPUTs[t].append((i,t_new))
            t -= 1
            dur -= 1
        TPUTs[t].append((i,t_new*dur))

BR_list = sorted(BRs.items(), key=lambda t: t[0])
TPUT_list = sorted(TPUTs.items(), key=lambda t: t[0])
t_0 = BR_list[0][0]
for i,l in enumerate(BR_list):
    BR_list[i] = (l[0] - t_0,) + l[1:]
for i,l in enumerate(TPUT_list):
    TPUT_list[i] = (l[0] - t_0,) + l[1:]

# for l in TPUT_list:
#     print l
# print len(TPUT_list), len(BR_list)

#TIMEOUT = 3
start = defaultdict(int)
end = defaultdict(int)
for (t,l) in BR_list:
    for (n,b) in l:
        if n not in start:
            start[n] = t
        end[n] = t            

BR_y = []
for i in xrange(max(end.values())+1):
    b = []
    for k in xrange(len(start)):
        if i < start[k] or i > end[k]: # hasn't started yet or ended already
            b.append(0)
        else:
            o = [m for m in BR_list if m[0] == i] # time in BR_list
            if o:
                o = [m for m in o[0][1] if m[0] == k] # my stream in timestep
            if o and o[0]:
                b.append(o[0][1])
            else: # inbetween items in list
                if i > 0:
                    b.append(BR_y[i-1][k])
                else:
                    b.append(0)
    BR_y.append(b)

TPUT_y = []
for i in xrange(max(end.values())+1):
    c = []
    for k in xrange(len(start)):
        if i < start[k] or i > end[k]: # hasn't started yet or ended already
            c.append(0)
        else:
            p = [m for m in TPUT_list if m[0] == i]
            if p:
                p = [m for m in p[0][1] if m[0] == k]
            if p and p[0]:
                c.append(p[0][1])
            else: # inbetween items in list
                c.append(0)
    TPUT_y.append(c)

# for l in TPUT_y:
#     print l


fair = []
for i, (x,y) in enumerate(BR_y):
    if i < start[0] or i < start[1]: 
        fair.append(1)
    else:
        fair.append(fairness(x,y))

smooth = []
for i in xrange(len(BR_y)):
    if i+1 < len(BR_y):
        s1 = BR_y[i+1][0] - BR_y[i][0]
        s2 = BR_y[i+1][1] - BR_y[i][1]
        smooth.append([s1,s2])

# Get Utility
BW = []
for l in nsl:
    print(l)
    print(l.split(" "))
    (t, ln, bw) = l.split(' ')
    t = int(float(t))
    t = max(t-t_0, 0)
    BW.append((t, bw))
#BW = 1000000 / 1000 # 1Mbit
util = []
t = (0,1000)
for i, (x,y) in enumerate(TPUT_y):
    for b in BW:
        if i >= b[0]:
            t = b
    x = float(x)
    y = float(y)
    util.append(100*((x+y) / float(t[1])))

#util = [100*((float(x)+float(y)) / 1000) for x, y in TPUT_y]


titles = ['Utilization', 'Fairness', 'Smoothness']
xlabels = ['Time (s)', 'Time (s)', 'Time (s)']
ylabels = ['% of link utilization', 'Jain Fairness', 'Derivative of BR wrt time']
labels = ('Host0', 'Host1')
outputs = ['utilization.png', 'fairness.png', 'smoothness.png']
colors = ['b','r']
style = ['-','--']
width = [1.0,1.0]
ymin = [0,0,0]
ymax = [150, 1.1, 0]

smooth = [(float(x)/1000,float(y)/1000) for x,y in smooth]

data = [[util], [fair], zip(*smooth)]
lines = []
for i in range(0,3):
    font = { 'size' : 22}
    plt.rc('font', **font)
    params = {'legend.fontsize': 20,
              #'legend.linewidth': 2,
              'xtick.major.size': 7,
              'xtick.major.width': 3,
              'ytick.major.size': 7,
              'ytick.major.width': 3,
              'ytick.labelsize': 16,
              'xtick.minor.size': 5,
              'xtick.minor.width': 2,
              'ytick.minor.size': 5,
              'ytick.minor.width': 2}
    plt.rcParams.update(params)

    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.set_xlabel(xlabels[i])
    ax.set_ylabel(ylabels[i])
    for q, pt in enumerate(data[i]):
        lines.append(plt.plot(pt, color=colors[q], 
                              linewidth=width[q], linestyle=style[q], label=labels[q]))
    y = ax.get_ylim()
    for l in start.values():
        if l:
            ax.vlines(l,0,y[1], colors='g', linestyles='dashdot', linewidth=2.0)

    for l in BW:
        if l[0]:
            ax.vlines(l[0],0,y[1], color='c', linestyles='dotted', linewidth=2.0)

    if i == 2:
        handles, labels = ax.get_legend_handles_labels()
        ax.legend(reversed(handles), reversed(labels), loc = 'lower right')
        ymax[i] = y[1]
        ymin[i] = y[0]
    x = ax.get_xlim()
    ax.axis([x[0],x[1],ymin[i],ymax[i]])
    plt.subplots_adjust(top=0.95) 
    plt.subplots_adjust(bottom=0.15) 
    #plt.show()
    plt.savefig(outputs[i])
