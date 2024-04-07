#!/usr/bin/env python

import os
import re
import sys
from argparse import ArgumentParser
from optparse import OptionParser
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.ticker import AutoMinorLocator
import numpy
import numpy as np


class CLICommand:
    """能带绘制
    """

    @staticmethod
    def add_arguments(parser: ArgumentParser):
        add = parser.add_argument

        add('-f', '--file',
            action='store', type=str,
            dest='filename', default='OUTCAR',
            help='location of OUTCAR')

        add('--procar',
            action='store', type=str, dest='procar',
            default='PROCAR',
            help='location of the PROCAR')

        add('-z', '--zero',
            action='store', type=float,
            dest='efermi', default=None,
            help='energy reference of the band plot')

        add('--adjust_gap',
            action='store', type=float,
            dest='adjust_gap', default=None,
            help='基于当前gap进行调整')

        add('-o', '--output',
            action='store', type=str, dest='bandimage',
            default='band.png',
            help='output image name, "band.png" by default')

        add('-k', '--kpoints',
            action='store', type=str, dest='kpts',
            default=None,
            help='kpoint path')

        add('-s', '--size', nargs=2,
            action='store', type=float, dest='figsize',
            default=(3.0, 4.0),
            help='figure size of the output plot')

        add('-y', nargs=2,
            action='store', type=float, dest='ylim',
            default=(-3, 3),
            help='energy range of the band plot')

        add('--hline',
            action='append', type=float, dest='hlines',
            default=[],
            help='Add horizontal lines to the figure.')

        add('--vline',
            action='append', type=float, dest='vlines',
            default=[],
            help='Add vertical lines to the figure.')

        add('--save_gnuplot',
            action='store_true', dest='gnuplot',
            default=False,
            help='save output band energies in gnuplot format')

        add('--lw',
            action='store', type=float, dest='linewidth',
            default=1.0,
            help='linewidth of the band plot')

        add('--lc',
            action='store', type=str, dest='linecolors',
            default=None,
            help='line colors of the band plot')

        add('--dpi',
            action='store', type=int, dest='dpi',
            default=360,
            help='resolution of the output image')

        add('--occ',
            action='append', type=str, dest='occ',
            default=[],
            help='orbital contribution of each KS state')

        add('--occL',
            action='store_true', dest='occLC',
            default=False,
            help='use Linecollection or Scatter to show the orbital contribution')

        add('--occLC_cmap',
            action='store', type=str, dest='occLC_cmap',
            default='jet',
            help='colormap of the line collection')

        add('--occLC_lw',
            action='store', type=float, dest='occLC_lw',
            default=2.0,
            help='linewidth of the line collection')

        add('--occLC_cbar_pos',
            action='store', type=str, dest='occLC_cbar_pos',
            default='top',
            help='position of the colorbar')

        add('--occLC_cbar_ticks',
            action='store', type=str, dest='occLC_cbar_ticks',
            default=None,
            help='ticks for the colorbar')

        add('--occLC_cbar_vmin',
            action='store', type=float, dest='occLC_cbar_vmin',
            default=None,
            help='minimum value for the color plot')

        add('--occLC_cbar_vmax',
            action='store', type=float, dest='occLC_cbar_vmax',
            default=None,
            help='maximum value for the color plot')

        add('--occLC_cbar_ticklabels',
            action='store', type=str, dest='occLC_cbar_ticklabels',
            default=None,
            help='tick labels for the colorbar')

        add('--occLC_cbar_size',
            action='store', type=str, dest='occLC_cbar_size',
            default='3%',
            help='size of the colorbar, relative to the axis')

        add('--occLC_cbar_pad',
            action='store', type=float, dest='occLC_cbar_pad',
            default=0.02,
            help='pad between colorbar and axis')

        add('--occM',
            action='append', type=str, dest='occMarker',
            default=[],
            help='the marker used in the plot')

        add('--occMs',
            action='append', type=int, dest='occMarkerSize',
            default=[],
            help='the size of the marker')

        add('--occMc',
            action='append', type=str, dest='occMarkerColor',
            default=[],
            help='the color of the marker')

        add('--spd',
            action='append', type=str, dest='spdProjections',
            default=[],
            help='Spd-projected wavefunction character of each KS orbital.')

        add('--spin', action='store', dest='spin',
            default=None, choices=['x', 'y', 'z'],
            help='show the magnetization mx/y/z constributions to the states. Use this option along with --occ.')

        add('--lsorbit',
            action='store_true', dest='lsorbit',
            help='Spin orbit coupling on, special treament of PROCAR')

        add('-q', '--quiet',
            action='store_true', dest='quiet',
            help='not show the resulting image')

        add('--xlabel',
            action='store', type=str,
            dest='xlabel', default=None,
            help='设置x坐标描述')

        add('--ylabel',
            action='store', type=str,
            dest='ylabel', default=None,
            help='设置y坐标描述')

    @staticmethod
    def run(args, parser):

        if args.occ:

            Nocc = len(args.occ)
            occM = ['o' for ii in range(Nocc)]
            occMc = ['r' for ii in range(Nocc)]
            occMs = [20 for ii in range(Nocc)]
            for ii in range(min(len(args.occMarker), Nocc)):
                occM[ii] = args.occMarker[ii]
            for ii in range(min(len(args.occMarkerSize), Nocc)):
                occMs[ii] = args.occMarkerSize[ii]
            for ii in range(min(len(args.occMarkerColor), Nocc)):
                occMc[ii] = args.occMarkerColor[ii]
            args.occMarker = occM
            args.occMarkerColor = occMc
            args.occMarkerSize = occMs

            whts = []
            iterater = 0
            for occ in args.occ:
                # CCX 2020-01-31 parse input range of atoms
                # if '0' in the index, select all the atoms
                if '0' in occ.split():
                    occAtom = None
                else:
                    occAtom = parseList(occ)

                if args.spdProjections:  # and (Nocc == 1):
                    if len(args.spdProjections) != len(args.occ):
                        print("number of projections does not match number of occupations")
                        sys.exit(0)

                    # set angall to corresponding item of spdProjections
                    angularM = parseSpdProjection(args.spdProjections[iterater])

                    whts.append(WeightFromPro(args.procar, whichAtom=occAtom,
                                              spd=angularM, lsorbit=args.lsorbit,
                                              spin=args.spin))
                else:
                    whts.append(WeightFromPro(args.procar, whichAtom=occAtom,
                                              lsorbit=args.lsorbit,
                                              spin=args.spin))
                iterater += 1

        else:
            whts = None

        kpath, bands, efermi, kpt_bounds = get_bandInfo(args.filename)
        bands = numpy.array([bands[0]])
        if args.efermi is None:
            bands -= efermi
        else:
            bands -= args.efermi
        if args.adjust_gap:
            bands[bands > 0] += args.adjust_gap

        import matplotlib as mpl
        from matplotlib.ticker import AutoMinorLocator

        # Use non-interactive backend in case there is no display
        mpl.use('agg')
        import matplotlib.pyplot as plt

        mpl.rcParams['axes.unicode_minus'] = False

        mpl_default_colors_cycle = [mpl.colors.to_hex(xx) for xx in
                                    mpl.rcParams['axes.prop_cycle'].by_key()['color']]
        if args.linecolors:
            ctmp = [mpl.colors.to_hex(xx) for xx in args.linecolors.split()]
            nspin = bands.shape[0]
            if len(ctmp) <= nspin:
                args.linecolors = ctmp + \
                                  [xx for xx in mpl_default_colors_cycle if xx not in ctmp]
        else:
            args.linecolors = mpl_default_colors_cycle

        bandplot(kpath, bands, efermi, kpt_bounds, args, whts)
        saveband_dat(kpath, bands, args, whts)


def parseList(string):
    def parseRange(rng):
        # print(rng)
        m = re.match(r'(\d+)(?:[-:](\d+))?(?:[-:](\d+))?$', rng)
        if not m:
            raise ValueError(
                """
The index should be assigned with combination of the following ways:
-> 10, a single band with index 10
-> 20:30, or '20-30', a continuous range from 20 to 30, 30 included
-> 30:50:2, or '30-50:2', a continues range from 30 to 50, with step size 2
-> '1 2 3', all the patterns above in one string separated by spaces.
For example: '1 4:6 8:16:2' will be converted to '1 4 5 6 8 10 12 14 16'
"""
            )
        ii = m.group(1)
        jj = m.group(2) or ii
        ss = m.group(3) or 1
        return [x - 1 for x in range(int(ii), int(jj) + 1, int(ss))]

    ret = []
    for rng in string.split():
        ret += parseRange(rng)
    return list(set(ret))


def parseSpdProjection(spd):
    '''
    Parse spdProjections string.  str -> [int]

    # Ionizing
    '''
    spd_dict = {
        's': [0],
        'p': [1, 2, 3],
        'd': [4, 5, 6, 7, 8],
        'f': [9, 10, 11, 12, 13, 14, 15],
        'py': [1],
        'pz': [2],
        'px': [3],
        'dxy': [4],
        'dyz': [5],
        'dz2': [6],
        'dxz': [7],
        'dx2': [8],
        "fy(3x2-y2)": [9],
        "fxyz  ": [10],
        "fyz2  ": [11],
        "fz3   ": [12],
        "fxz2  ": [13],
        "fz(x2-y2)": [14],
        "fx(x2-3y2) ": [15],
    }

    ret = []
    for l in spd.split():
        try:
            assert int(l) <= 15, "Maximum spd index should be <= 15."
            ret += [int(l)]
        except:
            if l.lower() not in spd_dict:
                raise ValueError(
                    "Spd-projected wavefunction character of each KS orbital.\n"
                    "    s orbital: 0\n"
                    "    py, pz, px orbital: 1 2 3\n"
                    "    dxy, dyz, dz2, dxz, dx2 orbital: 4 5 6 7 8 \n"
                    "    fy(3x2-y2), fxyz, fyz2, fz3, fxz2, fz(x2-y2), fx(x2-3y2) orbital: 9 10 11 12 13 14 15\n"
                    "\nFor example, --spd 's dxy 10' specifies the s/dxy/fxyz components\n"
                )
            ret += spd_dict[l]

    return list(set(ret))


def WeightFromPro(infile='PROCAR', whichAtom=None, spd=None, lsorbit=False, spin=None):
    """
    Contribution of selected atoms to the each KS orbital
    """

    assert os.path.isfile(infile), '%s cannot be found!' % infile
    FileContents = [line for line in open(infile) if line.strip()]

    # when the band number is too large, there will be no space between ";" and
    # the actual band number. A bug found by Homlee Guo.
    # Here, #kpts, #bands and #ions are all integers
    nkpts, nbands, nions = [int(xx) for xx in re.sub(
        '[^0-9]', ' ', FileContents[1]).split()]

    if spd:
        Weights = np.asarray([line.split()[1:-1] for line in FileContents
                              if not re.search('[a-zA-Z]', line)], dtype=float)
        Weights = np.sum(Weights[:, spd], axis=1)
    else:
        Weights = np.asarray([line.split()[-1] for line in FileContents
                              if not re.search('[a-zA-Z]', line)], dtype=float)

    nspin = Weights.shape[0] // (nkpts * nbands * nions)
    nspin //= 4 if lsorbit else 1

    if lsorbit:
        Weights.resize(nspin, nkpts, nbands, 4, nions)
        wid = [None, 'x', 'y', 'z'].index(spin)
        Weights = Weights[:, :, :, wid, :]
    else:
        Weights.resize(nspin, nkpts, nbands, nions)

    if whichAtom is None:
        return np.sum(Weights, axis=-1)
    else:
        # whichAtom = [xx - 1 for xx in whichAtom]
        whichAtom = [xx for xx in whichAtom]
        return np.sum(Weights[:, :, :, whichAtom], axis=-1)


############################################################


def get_bandInfo(inFile='OUTCAR'):
    """
    extract band energies from OUTCAR
    """

    outcar = [line for line in open(inFile) if line.strip()]

    for ii, line in enumerate(outcar):
        if 'NKPTS =' in line:
            nkpts = int(line.split()[3])
            nband = int(line.split()[-1])

        if 'ISPIN  =' in line:
            ispin = int(line.split()[2])

        if "k-points in reciprocal lattice and weights" in line:
            Lvkpts = ii + 1

        if 'reciprocal lattice vectors' in line:
            ibasis = ii + 1

        if 'E-fermi' in line:
            Efermi = float(line.split()[2])
            LineEfermi = ii + 1
            # break

    # basis vector of reciprocal lattice
    # B = np.array([line.split()[3:] for line in outcar[ibasis:ibasis+3]],

    # When the supercell is too large, spaces are missing between real space
    # lattice constants. A bug found out by Wei Xie (weixie4@gmail.com).
    B = np.array([line.split()[-3:] for line in outcar[ibasis:ibasis + 3]],
                 dtype=float)
    # k-points vectors and weights
    tmp = np.array([line.split() for line in outcar[Lvkpts:Lvkpts + nkpts]],
                   dtype=float)
    vkpts = tmp[:, :3]
    wkpts = tmp[:, -1]

    # for ispin = 2, there are two extra lines "spin component..."
    N = (nband + 2) * nkpts * ispin + (ispin - 1) * 2
    bands = []
    # vkpts = []
    for line in outcar[LineEfermi:LineEfermi + N]:
        if 'spin component' in line or 'band No.' in line:
            continue
        if 'k-point' in line:
            # vkpts += [line.split()[3:]]
            continue
        bands.append(float(line.split()[1]))

    bands = np.array(bands, dtype=float).reshape((ispin, nkpts, nband))

    if os.path.isfile('KPOINTS'):
        kp = open('KPOINTS').readlines()

    if os.path.isfile('KPOINTS') and kp[2][0].upper() == 'L':
        Nk_in_seg = int(kp[1].split()[0])
        Nseg = nkpts // Nk_in_seg
        vkpt_diff = np.zeros_like(vkpts, dtype=float)

        for ii in range(Nseg):
            start = ii * Nk_in_seg
            end = (ii + 1) * Nk_in_seg
            vkpt_diff[start:end, :] = vkpts[start:end, :] - vkpts[start, :]

        kpt_path = np.linalg.norm(np.dot(vkpt_diff, B), axis=1)
        # kpt_path = np.sqrt(np.sum(np.dot(vkpt_diff, B)**2, axis=1))
        for ii in range(1, Nseg):
            start = ii * Nk_in_seg
            end = (ii + 1) * Nk_in_seg
            kpt_path[start:end] += kpt_path[start - 1]

        # kpt_path /= kpt_path[-1]
        kpt_bounds = np.concatenate((kpt_path[0::Nk_in_seg], [kpt_path[-1], ]))
    else:
        # get band path
        vkpt_diff = np.diff(vkpts, axis=0)
        kpt_path = np.zeros(nkpts, dtype=float)
        kpt_path[1:] = np.cumsum(np.linalg.norm(np.dot(vkpt_diff, B), axis=1))
        # kpt_path /= kpt_path[-1]

        # get boundaries of band path
        xx = np.diff(kpt_path)
        kpt_bounds = np.concatenate(
            ([0.0, ], kpt_path[1:][np.isclose(xx, 0.0)], [kpt_path[-1], ]))

    return kpt_path, bands, Efermi, kpt_bounds


############################################################


def bandplot(kpath, bands, efermi, kpt_bounds, opts, whts=None):
    '''
    Use matplotlib to plot band structure
    '''

    width, height = opts.figsize
    ymin, ymax = opts.ylim
    dpi = opts.dpi

    fig = plt.figure()
    fig.set_size_inches(width, height)
    ax = plt.subplot(111)

    nspin, nkpts, nbands = bands.shape

    clrs = ['r', 'b']

    if opts.occLC and (whts is not None):
        from matplotlib.collections import LineCollection
        from mpl_toolkits.axes_grid1 import make_axes_locatable

        LW = opts.occLC_lw
        DELTA = 0.3
        EnergyWeight = whts[0]
        norm = mpl.colors.Normalize(
            vmin=opts.occLC_cbar_vmin if opts.occLC_cbar_vmin else EnergyWeight.min(),
            vmax=opts.occLC_cbar_vmax if opts.occLC_cbar_vmax else EnergyWeight.max(),
        )
        # norm = mpl.colors.Normalize(0, 1)
        # create a ScalarMappable and initialize a data structure
        s_m = mpl.cm.ScalarMappable(cmap=opts.occLC_cmap, norm=norm)
        s_m.set_array([EnergyWeight])

        for Ispin in range(nspin):
            for jj in range(nbands):
                x = kpath
                y = bands[Ispin, :, jj]
                z = EnergyWeight[Ispin, :, jj]

                ax.plot(x, y,
                        lw=LW + 2 * DELTA,
                        color='gray', zorder=1)

                points = np.array([x, y]).T.reshape(-1, 1, 2)
                segments = np.concatenate([points[:-1], points[1:]], axis=1)
                lc = LineCollection(segments,
                                    # cmap=opts.occLC_cmap, # alpha=0.7,
                                    colors=[s_m.to_rgba(ww)
                                            for ww in (z[1:] + z[:-1]) / 2.]
                                    # norm=plt.Normalize(0, 1)
                                    )
                # lc.set_array((z[1:] + z[:-1]) / 2)
                lc.set_linewidth(LW)
                ax.add_collection(lc)

        divider = make_axes_locatable(ax)
        ax_cbar = divider.append_axes(opts.occLC_cbar_pos.lower(),
                                      size=opts.occLC_cbar_size, pad=opts.occLC_cbar_pad)

        if opts.occLC_cbar_pos.lower() == 'top' or opts.occLC_cbar_pos.lower() == 'bottom':
            ori = 'horizontal'
        else:
            ori = 'vertical'
        cbar = plt.colorbar(s_m, cax=ax_cbar,
                            # ticks=[0.0, 1.0],
                            orientation=ori)
        if opts.occLC_cbar_ticks:
            cbar.set_ticks([
                float(x) for x in
                opts.occLC_cbar_ticks.split()
            ])
            if opts.occLC_cbar_ticklabels:
                cbar.set_ticklabels(opts.occLC_cbar_ticklabels.split())

        if ori == 'horizontal':
            cbar.ax.xaxis.set_ticks_position('top')
        else:
            cbar.ax.yaxis.set_ticks_position('right')


    else:
        for Ispin in range(nspin):
            for Iband in range(nbands):
                # if Iband == 0 else line.get_color()
                lc = opts.linecolors[Ispin]
                line, = ax.plot(kpath, bands[Ispin, :, Iband], lw=opts.linewidth, zorder=0,
                                alpha=0.8,
                                color=lc,
                                )
                if whts is not None:
                    for ii in range(len(opts.occ)):
                        ax.scatter(kpath, bands[Ispin, :, Iband],
                                   color=opts.occMarkerColor[ii],
                                   s=whts[ii][Ispin, :, Iband] *
                                     opts.occMarkerSize[ii],
                                   marker=opts.occMarker[ii], zorder=1, lw=0.0,
                                   alpha=0.5)

    for bd in kpt_bounds:
        ax.axvline(x=bd, ls='-', color='k', lw=0.5, alpha=0.5)

    # add extra horizontal/vertical lines
    for xx in opts.hlines:
        ax.axhline(y=xx, ls=':', color='k', lw=0.5, alpha=0.5)
    for yy in opts.vlines:
        ax.axhline(x=yy, ls=':', color='k', lw=0.5, alpha=0.5)

    if opts.xlabel:
        ax.set_xlabel(opts.xlabel)
    if opts.ylabel:
        ax.set_ylabel(opts.ylabel)
    else:
        ax.set_ylabel('Energy (eV)',  # fontsize='small',
                      labelpad=5)
    ax.set_ylim(ymin, ymax)
    ax.set_xlim(kpath.min(), kpath.max())

    ax.set_xticks(kpt_bounds)
    if opts.kpts:
        kname = [x.upper() for x in opts.kpts]
        for ii in range(len(kname)):
            if kname[ii] == 'G':
                kname[ii] = r'$\mathrm{\mathsf{\Gamma}}$'
            else:
                kname[ii] = r'$\mathrm{\mathsf{%s}}$' % kname[ii]
        ax.set_xticklabels(kname)
    else:
        ax.set_xticklabels([])

    ax.yaxis.set_minor_locator(AutoMinorLocator(2))

    plt.tight_layout(pad=0.20)
    plt.savefig(opts.bandimage, dpi=opts.dpi)


############################################################


def saveband_dat(kpath, bands, opts, whts=None):
    '''
    save band info to txt files
    '''
    prefix = 'pyband'
    spinSuffix = ['up', 'do']
    nspin, nkpts, nbands = bands.shape

    if nspin == 1:
        if opts.gnuplot:
            with open(prefix + '.dat', 'w') as out:
                # line = "kpts      energy      [projection weight]"
                for jj in range(nbands):
                    line = ''
                    for ii in range(nkpts):
                        line = ''
                        line += '%8.4f ' % kpath[ii]
                        line += '%10.4f' % bands[0, ii, jj]
                        line += '\n'
                        out.write(line)
                    line = '\n'
                    out.write(line)
                line = '\n'
                out.write(line)
                if opts.occ:
                    for kk in range(len(opts.occ)):
                        for jj in range(nbands):
                            line = ''
                            for ii in range(nkpts):
                                line = ''
                                line += '%8.4f ' % kpath[ii]
                                line += '%10.4f ' % bands[0, ii, jj]
                                line += '%10.4f' % whts[kk][0, ii, jj]
                                line += '\n'
                                out.write(line)
                            line = '\n'
                            out.write(line)
                        line = '\n'
                        out.write(line)
        else:
            header = "set xran [{}:{}]\n".format(kpath.min(), kpath.max())
            header += "plot for [ii=2:{}] 'pyband.dat' u 1:ii with line lc rgb '#000' t ''\n".format(
                nbands + 1)
            np.savetxt(prefix + '.dat', np.c_[kpath, bands[0]], fmt='%10.4f',
                       header=header)
            if whts:
                for i in range(len(whts)):
                    np.savetxt(prefix + '_weights_component_{}.dat'.format(i + 1),
                               np.c_[kpath, whts[i][0]], fmt='%10.4f', header=header)

    else:
        if opts.gnuplot:
            for Ispin in range(nspin):
                filename = prefix + '_' + spinSuffix[Ispin] + '.dat'
                with open(filename, 'w') as out:
                    # line = "kpts      energy      [projection weight]"
                    for jj in range(nbands):
                        line = ''
                        for ii in range(nkpts):
                            line = ''
                            line += '%8.4f ' % kpath[ii]
                            line += '%10.4f' % bands[Ispin, ii, jj]
                            line += '\n'
                            out.write(line)
                        line = '\n'
                        out.write(line)
                    line = '\n'
                    out.write(line)
                    if opts.occ:
                        for kk in range(len(opts.occ)):
                            for jj in range(nbands):
                                line = ''
                                for ii in range(nkpts):
                                    line = ''
                                    line += '%8.4f ' % kpath[ii]
                                    line += '%10.4f' % bands[Ispin, ii, jj]
                                    line += '%10.4f' % whts[kk][Ispin, ii, jj]
                                    line += '\n'
                                    out.write(line)
                                line = '\n'
                                out.write(line)
                            line = '\n'
                            out.write(line)
        else:
            for Ispin in range(nspin):
                filename = prefix + '_' + spinSuffix[Ispin] + '.dat'
                header = "set xran [{}:{}]\n".format(kpath.min(), kpath.max())
                header += "plot for [ii=2:{}] '{}' u 1:ii with line lc rgb '#000' t ''\n".format(
                    nbands + 1, filename)
                np.savetxt(filename, np.c_[kpath, bands[Ispin]], fmt='%10.4f',
                           header=header)
                if whts:
                    for i in range(len(whts)):
                        filename = prefix + '_' + spinSuffix[Ispin] + '_weights_component_{}'.format(i + 1) + '.dat'
                        np.savetxt(filename, np.c_[kpath, whts[i][Ispin]], fmt='%10.4f',
                                   header=header)
