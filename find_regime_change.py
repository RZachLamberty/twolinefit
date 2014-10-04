#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
module: find_regime_change.py
author: Zach Lamberty
created: 2014-10-04

Description:
    solution to the ecofactor regime change toy problem

Usage:
    <usage>

"""

import argparse
import os
import re
import matplotlib.pyplot as pyplot
import numpy
import scipy.stats as ss


#-----------------------#
#   Module Constants    #
#-----------------------#

HERE = os.path.dirname(os.path.realpath(__file__))
PLOTNAME = os.path.join(HERE, 'regime_change_plot.png')

#-----------------------#
#   Loading data        #
#-----------------------#

def find_regime_change(fname, sd=0.01, plotname=PLOTNAME):
    """ Given the file name of an xy data set with an assumed sd (suppose we
        could just calc it) find the "regime change" points, the points at which
        the valid fitting parameters change (see README for more info)

    """
    d = numpy.loadtxt(fname)

    lM, rM, bM = two_line_fit(d)

    publish_results(bM, d, fname, plotname)


def two_line_fit(d):
    """ assuming the data is truly represented by a regime change of two lines,
        a first-order solution of making the fit with two separate lines will be
        sufficient.

    """
    # find initialization values -- simple fits on the first and last .05
    # to init values
    iL = int(.05 * len(d))
    iH = len(d) - iL

    # brute force for now, binom later
    z = numpy.zeros((iH - iL, 2, 6))
    for i in range(iL, iH):
        z[i - iL, 0, :] = ss.linregress(d[:i]) + (i,)
        z[i - iL, 1, :] = ss.linregress(d[i:]) + (i,)

    leftMin = min(z[:, 0, :], key=lambda x: x[4])
    rightMin = min(z[:, 1, :], key=lambda x: x[4])
    bothMin = min(z, key=lambda x: x[0, 4] + x[1, 4])

    return leftMin, rightMin, bothMin


def fTwoLine(x, a1, b1, a2, b2, iChange):
    iChange = int(round(iChange))
    r = numpy.zeros(len(x))
    r[:iChange] += a1 * x[:iChange] + b1
    r[iChange:] += a2 * x[iChange:] + b2
    return r


def publish_results(bM, d, fname, plotname=PLOTNAME):
    """ print that shit """
    make_plots(bM, d, plotname)
    print_results(bM, d, fname)


def make_plots(bM, d, plotname=PLOTNAME):
    f = pyplot.figure()

    s = f.add_subplot(111)
    a1, b1, r1, p1, s1, iChange = bM[0]
    a2, b2, r2, p2, s2, iChange = bM[1]

    # Left with fit
    s.plot(
        d[:iChange, 0], d[:iChange, 1],
        ls='', marker='o', alpha=.25, color='b',
        label='{:<0.4f} * x + {:<0.4f}, sigma={:<0.3e}'.format(a1, b1, s1)
    )
    s.plot(d[:iChange, 0], a1 * d[:iChange, 0] + b1, color='r', alpha=0.75, lw=1)

    # Right with fit
    s.plot(
        d[iChange:, 0], d[iChange:, 1],
        ls='', marker='o', alpha=.25, color='g',
        label='{:<0.4f} * x + {:<0.4f}, sigma={:<0.3e}'.format(a2, b2, s2)
    )
    s.plot(d[:iChange, 0], a2 * d[:iChange, 0] + b2, color='r', alpha=0.75, lw=1)

    # formatting
    s.legend(loc='upper left')
    s.set_xlabel("x")
    s.set_ylabel("y")
    s.set_title("regime change at {}".format(iChange))

    f.savefig(plotname)


def print_results(bM, d, fname):
    """ print results to screen """
    a1, b1 = bM[0][:2]
    a2, b2 = bM[1][:2]
    iChange = int(bM[0][5])
    A1, B1, A2, B2, IChange = [float(el) for el in get_actual_params(fname)]
    print ''
    print '{:<13}  {:<12}  {:<12}  {:<12}'.format(
        'measurement', 'calculated', 'actual', 'error (%)'
    )
    print '{:-<13}  {:-<12}  {:-<12}  {:-<12}'.format('', '', '', '')
    print '{:<13}  {:<12}  {:<12}  {:<12}'.format(
        'change minute', iChange, IChange, 100 * abs(iChange - IChange) / IChange
    )
    decfmt = '{:<13}  {:<12.4f}  {:<12.4f}  {:<12.1f}'
    print decfmt.format('a1', a1, A1, 100 * abs(a1 - A1) / A1)
    print decfmt.format('b1', b1, B1, 100 * abs(b1 - B1) / B1)
    print decfmt.format('a2', a2, A2, 100 * abs(a2 - A2) / A2)
    print decfmt.format('b2', b2, B2, 100 * abs(b2 - B2) / B2)

    print '\nerror estimates:'
    print 'standard error of left fit  : {:.3e}'.format(bM[0][4])
    print 'standard error of right fit : {:.3e}'.format(bM[1][4])
    print ''


def get_actual_params(fname):
    """ Where files have the actual data input parameters in comments on the
        second and third lines, go grab them. Otherwise, leave unspecified

    """
    with open(fname, 'r') as fIn:
        for line in fIn:
            m = re.match('# a1 = ([\-\.e\d]*), b1 = ([\-\.e\d]*), a2 = ([\-\.e\d]*), b2 = ([\-\.e\d]*)\n', line)
            if m:
                a1, b1, a2, b2 = [float(el) for el in m.groups()]

            m = re.match('# Regime shift at minute (\d+)\n', line)
            if m:
                iChange = m.groups()[0]

    return a1, b1, a2, b2, iChange


#-------------------------------#
#   Main routine                #
#-------------------------------#

def parse_args():
    """ take in a data file from the command line """
    parser = argparse.ArgumentParser()

    fname = "Data file name. Should contain two columns of x/y data"
    parser.add_argument("fname", help=fname)

    std = "manually set the std error of input data"
    parser.add_argument("--std", help=std, default=0.01)

    plotname = "output name of plot we will generate"
    parser.add_argument("--plotname", help=plotname, default=PLOTNAME)

    args = parser.parse_args()

    return args


if __name__ == '__main__':

    args = parse_args()

    find_regime_change(args.fname, args.std, args.plotname)
