#!/usr/bin/env python
"""
Thomas Klijnsma
"""

########################################
# Imports
########################################

import logging
import os, sys, re
from os.path import *
from glob import glob
from copy import deepcopy
from math import sqrt
import traceback

from OptionHandler import flag_as_option

sys.path.append('src')
import Commands
import PhysicsCommands
import TheoryCommands
import LatestPaths
import LatestPathsGetters
import LatestBinning
from Container import Container
import PlotCommands
import DifferentialTable
from differentialTools import *

import differentials
# import differentials.plotting

from time import strftime
datestr = strftime('%b%d')


########################################
# Plotting
########################################

#____________________________________________________________________
@flag_as_option
def plot_all_differentials(args):
    pth_smH_plot(args)
    pth_ggH_plot(args)
    njets_plot(args)
    ptjet_plot(args)
    rapidity_plot(args)

@flag_as_option
def plot_pth(args):
    pth_smH_plot(args)
    pth_ggH_plot(args)

#____________________________________________________________________
@flag_as_option
def pth_smH_plot(args):
    spectra = []
    TheoryCommands.SetPlotDir( 'plots_{0}'.format(datestr) )
    obs_name = 'pth_smH'
    obstuple = LatestBinning.obstuple_pth_smH
    scandict = LatestPaths.scan.pth_smH.asimov if args.asimov else LatestPaths.scan.pth_smH.observed

    hgg = differentials.scans.DifferentialSpectrum('hgg', scandict.hgg)
    hgg.color = differentials.core.safe_colors.red
    # hgg.no_overflow_label = True
    hgg.draw_method = 'repr_point_with_vertical_bar_and_horizontal_bar'
    hgg.set_sm(obstuple.hgg.crosssection_over_binwidth(normalize_by_second_to_last_bin_width=True))
    hgg.read()
    spectra.append(hgg)

    hzz = differentials.scans.DifferentialSpectrum('hzz', scandict.hzz)
    hzz.color = differentials.core.safe_colors.blue
    # hzz.no_overflow_label = True
    hzz.draw_method = 'repr_point_with_vertical_bar_and_horizontal_bar'
    hzz.set_sm(obstuple.hzz.crosssection_over_binwidth(normalize_by_second_to_last_bin_width=True))
    hzz.read()
    spectra.append(hzz)

    hbb = differentials.scans.DifferentialSpectrum('hbb', scandict.hbb)
    hbb.drop_first_bin()
    hbb.color = differentials.core.safe_colors.green
    # hbb.no_overflow_label = True
    hbb.draw_method = 'repr_point_with_vertical_bar_and_horizontal_bar'
    hbb.set_sm(obstuple.hbb.crosssection_over_binwidth(normalize_by_second_to_last_bin_width=True))
    hbb.read()
    spectra.append(hbb)

    # combination = differentials.scans.DifferentialSpectrum('combination', scandict.combination)
    # combination.color = 14
    # combination.no_overflow_label = True
    # combination.draw_method = 'repr_point_with_vertical_bar'
    # combination.set_sm(obstuple.combination.crosssection_over_binwidth(normalize_by_second_to_last_bin_width=True))
    # combination.read()
    # spectra.append(combination)

    combWithHbb = differentials.scans.DifferentialSpectrum('combWithHbb', scandict.combWithHbb)
    combWithHbb.color = 1
    combWithHbb.no_overflow_label = True
    # combWithHbb.draw_method = 'repr_point_with_vertical_bar'
    combWithHbb.draw_method = 'repr_point_with_vertical_bar_and_horizontal_bar'
    combWithHbb.title = 'Combination'
    combWithHbb.set_sm(obstuple.combWithHbb.crosssection_over_binwidth(normalize_by_second_to_last_bin_width=True))
    combWithHbb.read()
    spectra.append(combWithHbb)

    # Get syst only shape
    combWithHbb_statonly = differentials.scans.DifferentialSpectrum('combWithHbb_statonly', scandict.combWithHbb_statonly)
    combWithHbb_statonly.color = 1
    combWithHbb_statonly.no_overflow_label = True
    combWithHbb_statonly.draw_method = 'repr_point_with_vertical_bar'
    combWithHbb_statonly.set_sm(obstuple.combWithHbb.crosssection_over_binwidth(normalize_by_second_to_last_bin_width=True))
    combWithHbb_statonly.read()
    systshapemaker = differentials.systshapemaker.SystShapeMaker()
    systonly_histogram, systonly_histogram_xs = systshapemaker.get_systonly_histogram(combWithHbb, combWithHbb_statonly)

    if args.table:
        table = differentials.plotting.tables.SpectraTable('pth_smH', [s for s in spectra if not s is hbb] + [combWithHbb_statonly])
        table.add_symm_improvement_row(hgg, combWithHbb)
        # table.add_symm_improvement_row(hgg, combination)
        # table.add_symm_improvement_row(combination, combWithHbb)
        logging.info('Table:\n{0}'.format( table.repr_terminal() ))
        return

    plot = differentials.plotting.plots.SpectraPlot(
        'spectra_{0}'.format(obs_name) + ('_asimov' if args.asimov else ''),
        spectra
        )
    plot.draw_multiscans = True
    plot.obsname = obs_name
    plot.obsunit = 'GeV'
    plot.leg.SetNColumns(3)
    if systshapemaker.success:
        plot.add_top(systonly_histogram_xs, systonly_histogram_xs.draw_method, plot.leg)
        plot.add_bottom(systonly_histogram, systonly_histogram.draw_method)

    plot.bottom_y_min = -2.0
    plot.bottom_y_max = 4.0

    plot.draw()
    plot.wrapup()


#____________________________________________________________________
@flag_as_option
def pth_ggH_plot(args):
    spectra = []
    TheoryCommands.SetPlotDir( 'plots_{0}'.format(datestr) )
    obs_name = 'pth_ggH'
    obstuple = LatestBinning.obstuple_pth_ggH
    scandict = LatestPaths.scan.pth_ggH.asimov if args.asimov else LatestPaths.scan.pth_ggH.observed

    # hgg = differentials.scans.DifferentialSpectrum('hgg', scandict.hgg)
    # hgg.color = differentials.core.safe_colors.red
    # hgg.no_overflow_label = True
    # hgg.draw_method = 'repr_point_with_vertical_bar_and_horizontal_bar'# 
    # hgg.set_sm(obstuple.hgg.crosssection_over_binwidth(normalize_by_second_to_last_bin_width=True))
    # hgg.read()
    # spectra.append(hgg)

    # hzz = differentials.scans.DifferentialSpectrum('hzz', scandict.hzz)
    # hzz.color = differentials.core.safe_colors.blue
    # hzz.no_overflow_label = True
    # hzz.draw_method = 'repr_point_with_vertical_bar_and_horizontal_bar'# 
    # hzz.set_sm(obstuple.hzz.crosssection_over_binwidth(normalize_by_second_to_last_bin_width=True))
    # hzz.read()
    # spectra.append(hzz)

    # hbb = differentials.scans.DifferentialSpectrum('hbb', scandict.hbb)
    # hbb.drop_first_bin()
    # hbb.color = differentials.core.safe_colors.green
    # hbb.no_overflow_label = True
    # hbb.draw_method = 'repr_point_with_vertical_bar_and_horizontal_bar'
    # hbb.set_sm(obstuple.hbb.crosssection_over_binwidth(normalize_by_second_to_last_bin_width=True))
    # hbb.read()
    # spectra.append(hbb)

    # combination = differentials.scans.DifferentialSpectrum('combination', scandict.combination)
    # combination.color = 14
    # combination.no_overflow_label = True
    # combination.draw_method = 'repr_point_with_vertical_bar'
    # combination.set_sm(obstuple.combination.crosssection_over_binwidth(normalize_by_second_to_last_bin_width=True))
    # combination.read()
    # spectra.append(combination)

    combWithHbb = differentials.scans.DifferentialSpectrum('combWithHbb', scandict.combWithHbb)
    combWithHbb.color = 1
    combWithHbb.no_overflow_label = True
    # combWithHbb.draw_method = 'repr_point_with_vertical_bar'
    combWithHbb.draw_method = 'repr_point_with_vertical_bar_and_horizontal_bar'
    combWithHbb.title = 'Combination'
    combWithHbb.set_sm(obstuple.combWithHbb.crosssection_over_binwidth(normalize_by_second_to_last_bin_width=True))
    combWithHbb.read()
    spectra.append(combWithHbb)

    # Get syst only shape
    combWithHbb_statonly = differentials.scans.DifferentialSpectrum('combWithHbb_statonly', scandict.combWithHbb_statonly)
    combWithHbb_statonly.color = 1
    combWithHbb_statonly.no_overflow_label = True
    combWithHbb_statonly.draw_method = 'repr_point_with_vertical_bar'
    combWithHbb_statonly.set_sm(obstuple.combWithHbb.crosssection_over_binwidth(normalize_by_second_to_last_bin_width=True))
    combWithHbb_statonly.read()
    systshapemaker = differentials.systshapemaker.SystShapeMaker()
    systonly_histogram, systonly_histogram_xs = systshapemaker.get_systonly_histogram(combWithHbb, combWithHbb_statonly)

    if args.table:
        table = differentials.plotting.tables.SpectraTable('pth_ggH', [s for s in spectra if not s is hbb])
        table.add_symm_improvement_row(hgg, combWithHbb)
        table.add_symm_improvement_row(hgg, combination)
        table.add_symm_improvement_row(combination, combWithHbb)
        logging.info('Table:\n{0}'.format( table.repr_terminal() ))
        return

    l = differentials.plotting.pywrappers.Latex(
        lambda c: 1.0 - c.GetRightMargin() - 0.11,
        lambda c: 1.0 - c.GetTopMargin() - 0.24,
        'gg #rightarrow H'
        )
    l.SetNDC()
    l.SetTextSize(0.06)
    l.SetTextAlign(33)

    plot = differentials.plotting.plots.SpectraPlot(
        'spectra_{0}'.format(obs_name) + ('_asimov' if args.asimov else ''),
        spectra
        )
    plot.leg.SetNColumns(3)
    if systshapemaker.success:
        plot.add_top(systonly_histogram_xs, systonly_histogram_xs.draw_method, plot.leg)
        plot.add_bottom(systonly_histogram, systonly_histogram.draw_method)
    plot.draw_multiscans = True
    plot.obsname = obs_name
    plot.obsunit = 'GeV'
    plot.add_top(l, '')
    plot.leg.SetNColumns(3)
    # plot.scans_x_min = -110.
    plot.draw()
    plot.wrapup()


#____________________________________________________________________
def get_POIs_oldstyle_scandir(scandir):
    root_files = glob(join(scandir, '*.root'))
    POIs = []
    for root_file in root_files:
        POI = basename(root_file).split('_')[1:6]
        try:
            differentials.core.str_to_float(POI[-1])
        except ValueError:
            POI = POI[:-1]
        POI = '_'.join(POI)
        POIs.append(POI)
    POIs = list(set(POIs))
    POIs.sort(key=differentials.core.range_sorter)
    logging.info('Retrieved following POIs from oldstyle {0}:\n{1}'.format(scandir, POIs))
    return POIs

#____________________________________________________________________
@flag_as_option
def njets_plot(args):
    obs_name = 'njets'
    obstuple = LatestBinning.obstuple_njets
    scandict = LatestPaths.scan[obs_name]['asimov' if args.asimov else 'observed']

    hgg = differentials.scans.DifferentialSpectrum('hgg', scandict.hgg)
    # hgg.POIs = get_POIs_oldstyle_scandir(scandict.hgg)
    hgg.color = differentials.core.safe_colors.red
    hgg.draw_method = 'repr_point_with_vertical_bar_and_horizontal_bar'
    hgg.set_sm(obstuple.hgg.crosssection_over_binwidth(normalize_by_second_to_last_bin_width=True))
    hgg.read()

    hzz = differentials.scans.DifferentialSpectrum('hzz', scandict.hzz)
    # hzz.POIs = get_POIs_oldstyle_scandir(scandict.hzz)
    hzz.color = differentials.core.safe_colors.blue
    hzz.draw_method = 'repr_point_with_vertical_bar_and_horizontal_bar'
    hzz.set_sm(obstuple.hzz.crosssection_over_binwidth(normalize_by_second_to_last_bin_width=True))
    hzz.read()

    combination = differentials.scans.DifferentialSpectrum('combination', scandict.combination)
    # combination.POIs = get_POIs_oldstyle_scandir(scandict.combination)
    combination.color = 1
    combination.no_overflow_label = True
    combination.draw_method = 'repr_point_with_vertical_bar'
    combination.set_sm(obstuple.combination.crosssection_over_binwidth(normalize_by_second_to_last_bin_width=True))
    combination.read()

    # Get syst only shape
    combination_statonly = differentials.scans.DifferentialSpectrum('combination_statonly', scandict.combination_statonly)
    combination_statonly.color = 1
    combination_statonly.no_overflow_label = True
    combination_statonly.draw_method = 'repr_point_with_vertical_bar'
    combination_statonly.set_sm(obstuple.combination.crosssection_over_binwidth(normalize_by_second_to_last_bin_width=True))
    combination_statonly.read()
    systshapemaker = differentials.systshapemaker.SystShapeMaker()
    systonly_histogram, systonly_histogram_xs = systshapemaker.get_systonly_histogram(combination, combination_statonly)

    if args.table:
        table = differentials.plotting.tables.SpectraTable('njets', [ hgg, hzz, combination ])
        table.add_symm_improvement_row(hgg, combination)
        logging.info('Table:\n{0}'.format(table.repr_terminal()))
        return

    plot = differentials.plotting.plots.SpectraPlot(
        'spectra_{0}'.format(obs_name) + ('_asimov' if args.asimov else ''),
        [ hgg, hzz, combination ]
        )
    plot.leg.SetNColumns(3)
    if systshapemaker.success:
        plot.add_top(systonly_histogram_xs, systonly_histogram_xs.draw_method, plot.leg)
        plot.add_bottom(systonly_histogram, systonly_histogram.draw_method)
    plot.draw_multiscans = True
    plot.obsname = obs_name
    plot.draw()
    plot.wrapup()

#____________________________________________________________________
@flag_as_option
def ptjet_plot(args):
    obs_name = 'ptjet'
    obstuple = LatestBinning.obstuple_ptjet
    scandict = LatestPaths.scan[obs_name]['asimov' if args.asimov else 'observed']

    hgg = differentials.scans.DifferentialSpectrum('hgg', scandict.hgg)
    # hgg.POIs = get_POIs_oldstyle_scandir(scandict.hgg)
    hgg.color = differentials.core.safe_colors.red
    hgg.draw_method = 'repr_point_with_vertical_bar_and_horizontal_bar'
    hgg.set_sm(obstuple.hgg.crosssection_over_binwidth(normalize_by_second_to_last_bin_width=True))
    hgg.read()

    hzz = differentials.scans.DifferentialSpectrum('hzz', scandict.hzz)
    # hzz.POIs = get_POIs_oldstyle_scandir(scandict.hzz)
    hzz.color = differentials.core.safe_colors.blue
    hzz.draw_method = 'repr_point_with_vertical_bar_and_horizontal_bar'
    hzz.set_sm(obstuple.hzz.crosssection_over_binwidth(normalize_by_second_to_last_bin_width=True))
    hzz.read()

    combination = differentials.scans.DifferentialSpectrum('combination', scandict.combination)
    # combination.POIs = get_POIs_oldstyle_scandir(scandict.combination)
    combination.color = 1
    combination.no_overflow_label = True
    combination.draw_method = 'repr_point_with_vertical_bar'
    combination.set_sm(obstuple.combination.crosssection_over_binwidth(normalize_by_second_to_last_bin_width=True))
    combination.read()

    # Get syst only shape
    combination_statonly = differentials.scans.DifferentialSpectrum('combination_statonly', scandict.combination_statonly)
    combination_statonly.color = 1
    combination_statonly.no_overflow_label = True
    combination_statonly.draw_method = 'repr_point_with_vertical_bar'
    combination_statonly.set_sm(obstuple.combination.crosssection_over_binwidth(normalize_by_second_to_last_bin_width=True))
    combination_statonly.read()
    systshapemaker = differentials.systshapemaker.SystShapeMaker()
    systonly_histogram, systonly_histogram_xs = systshapemaker.get_systonly_histogram(combination, combination_statonly)

    if args.table:
        table = differentials.plotting.tables.SpectraTable('ptjet', [ hgg, hzz, combination ])
        table.add_symm_improvement_row(hgg, combination)
        logging.info('Table:\n{0}'.format(table.repr_terminal()))
        return

    plot = differentials.plotting.plots.SpectraPlot(
        'spectra_{0}'.format(obs_name) + ('_asimov' if args.asimov else ''),
        [ hgg, hzz, combination ]
        )
    if systshapemaker.success:
        plot.add_top(systonly_histogram_xs, systonly_histogram_xs.draw_method, plot.leg)
        plot.add_bottom(systonly_histogram, systonly_histogram.draw_method)
    plot.draw_multiscans = True
    plot.top_y_max = 10.
    plot.obsname = obs_name
    plot.obsunit = 'GeV'
    plot.leg.SetNColumns(3)
    plot.draw()
    plot.leg.SetNColumns(3)
    plot.wrapup()

#____________________________________________________________________
@flag_as_option
def rapidity_plot(args):
    obs_name = 'rapidity'
    obstuple = LatestBinning.obstuple_rapidity
    scandict = LatestPaths.scan[obs_name]['asimov' if args.asimov else 'observed']

    hgg = differentials.scans.DifferentialSpectrum('hgg', scandict.hgg)
    # hgg.POIs = get_POIs_oldstyle_scandir(scandict.hgg)
    hgg.color = differentials.core.safe_colors.red
    hgg.draw_method = 'repr_point_with_vertical_bar_and_horizontal_bar'
    hgg.set_sm(obstuple.hgg.crosssection_over_binwidth(normalize_by_second_to_last_bin_width=False))
    hgg.read()

    hzz = differentials.scans.DifferentialSpectrum('hzz', scandict.hzz)
    # hzz.POIs = get_POIs_oldstyle_scandir(scandict.hzz)
    hzz.color = differentials.core.safe_colors.blue
    hzz.draw_method = 'repr_point_with_vertical_bar_and_horizontal_bar'
    hzz.set_sm(obstuple.hzz.crosssection_over_binwidth(normalize_by_second_to_last_bin_width=False))
    hzz.read()

    combination = differentials.scans.DifferentialSpectrum('combination', scandict.combination)
    # combination.POIs = get_POIs_oldstyle_scandir(scandict.combination)
    combination.color = 1
    combination.no_overflow_label = True
    combination.draw_method = 'repr_point_with_vertical_bar'
    combination.set_sm(obstuple.combination.crosssection_over_binwidth(normalize_by_second_to_last_bin_width=False))
    combination.read()

    # Get syst only shape
    combination_statonly = differentials.scans.DifferentialSpectrum('combination_statonly', scandict.combination_statonly)
    combination_statonly.color = 1
    combination_statonly.no_overflow_label = True
    combination_statonly.draw_method = 'repr_point_with_vertical_bar'
    combination_statonly.set_sm(obstuple.combination.crosssection_over_binwidth(normalize_by_second_to_last_bin_width=False))
    combination_statonly.read()
    systshapemaker = differentials.systshapemaker.SystShapeMaker()
    systonly_histogram, systonly_histogram_xs = systshapemaker.get_systonly_histogram(combination, combination_statonly)

    if args.table:
        table = differentials.plotting.tables.SpectraTable('rapidity', [ hgg, hzz, combination ])
        table.add_symm_improvement_row(hgg, combination)
        logging.info('Table:\n{0}'.format(table.repr_terminal()))
        return

    plot = differentials.plotting.plots.SpectraPlot(
        'spectra_{0}'.format(obs_name) + ('_asimov' if args.asimov else ''),
        [ hgg, hzz, combination ]
        )
    if systshapemaker.success:
        plot.add_top(systonly_histogram_xs, systonly_histogram_xs.draw_method, plot.leg)
        plot.add_bottom(systonly_histogram, systonly_histogram.draw_method)
    plot.draw_multiscans = True
    plot.top_y_max = 300
    plot.obsname = obs_name
    plot.leg.SetNColumns(3)
    plot.draw()
    plot.wrapup()



########################################
# Other plots
########################################

@flag_as_option
def plot_all_statsyst(args):
    njets_plot_statsyst(args)
    ptjet_plot_statsyst(args)
    rapidity_plot_statsyst(args)
    pth_ggH_plot_statsyst(args)
    pth_smH_plot_statsyst(args)

@flag_as_option
def pth_ggH_plot_statsyst(args):
    obs_name = 'pth_ggH'
    obstuple = LatestBinning.obstuple_pth_ggH
    scandict = LatestPaths.scan[obs_name]['asimov' if args.asimov else 'observed']
    plotname = 'spectra_{0}_statsyst'.format(obs_name) + ('_asimov' if args.asimov else '')

    combWithHbb = differentials.scans.DifferentialSpectrum('combWithHbb', scandict.combWithHbb)
    combWithHbb.color = 1
    combWithHbb.title = 'Total'
    combWithHbb.no_overflow_label = True
    combWithHbb.draw_method = 'repr_point_with_vertical_bar'
    combWithHbb.set_sm(obstuple.combWithHbb.crosssection_over_binwidth(normalize_by_second_to_last_bin_width=True))
    combWithHbb.read()

    combWithHbb_statonly = differentials.scans.DifferentialSpectrum('combWithHbb_statonly', scandict.combWithHbb_statonly)
    combWithHbb_statonly.color = 1
    combWithHbb_statonly.no_overflow_label = True
    combWithHbb_statonly.draw_method = 'repr_point_with_vertical_bar'
    combWithHbb_statonly.set_sm(obstuple.combWithHbb.crosssection_over_binwidth(normalize_by_second_to_last_bin_width=True))
    combWithHbb_statonly.read()
    combWithHbb_statonly.plot_scans(plotname + '_scans_combWithHbb_statonly')

    systonly_histogram, systonly_histogram_xs = get_systonly_histogram(combWithHbb, combWithHbb_statonly)

    plot = differentials.plotting.plots.SpectraPlot(
        plotname,
        [ combWithHbb ]
        )
    plot.draw_multiscans = True
    plot.obsname = obs_name
    plot.obsunit = 'GeV'
    plot.add_top(systonly_histogram_xs, systonly_histogram_xs.draw_method, plot.leg)
    plot.add_bottom(systonly_histogram, systonly_histogram.draw_method)
    plot.draw()
    plot.wrapup()

@flag_as_option
def pth_smH_plot_statsyst(args):
    obs_name = 'pth_smH'
    obstuple = LatestBinning.obstuple_pth_smH
    scandict = LatestPaths.scan[obs_name]['asimov' if args.asimov else 'observed']
    plotname = 'spectra_{0}_statsyst'.format(obs_name) + ('_asimov' if args.asimov else '')

    combWithHbb = differentials.scans.DifferentialSpectrum('combWithHbb', scandict.combWithHbb)
    combWithHbb.color = 1
    combWithHbb.title = 'Total'
    combWithHbb.no_overflow_label = True
    combWithHbb.draw_method = 'repr_point_with_vertical_bar'
    combWithHbb.set_sm(obstuple.combWithHbb.crosssection_over_binwidth(normalize_by_second_to_last_bin_width=True))
    combWithHbb.read()

    combWithHbb_statonly = differentials.scans.DifferentialSpectrum('combWithHbb_statonly', scandict.combWithHbb_statonly)
    combWithHbb_statonly.color = 1
    combWithHbb_statonly.no_overflow_label = True
    combWithHbb_statonly.draw_method = 'repr_point_with_vertical_bar'
    combWithHbb_statonly.set_sm(obstuple.combWithHbb.crosssection_over_binwidth(normalize_by_second_to_last_bin_width=True))
    combWithHbb_statonly.read()
    combWithHbb_statonly.plot_scans(plotname + '_scans_combWithHbb_statonly')

    systonly_histogram, systonly_histogram_xs = get_systonly_histogram(combWithHbb, combWithHbb_statonly)

    plot = differentials.plotting.plots.SpectraPlot(
        plotname,
        [ combWithHbb ]
        )
    plot.draw_multiscans = True
    plot.obsname = obs_name
    plot.obsunit = 'GeV'
    plot.add_top(systonly_histogram_xs, systonly_histogram_xs.draw_method, plot.leg)
    plot.add_bottom(systonly_histogram, systonly_histogram.draw_method)
    plot.draw()
    plot.wrapup()

@flag_as_option
def njets_plot_statsyst(args):
    obs_name = 'njets'
    obstuple = LatestBinning.obstuple_njets
    scandict = LatestPaths.scan[obs_name]['asimov' if args.asimov else 'observed']
    # scandict.combination_statonly = 'out/Scan_njets_Feb06_combination_statonly'

    combination = differentials.scans.DifferentialSpectrum('combination', scandict.combination)
    # combination.POIs = get_POIs_oldstyle_scandir(scandict.combination)
    combination.color = 1
    combination.title = 'Total'
    combination.no_overflow_label = True
    combination.draw_method = 'repr_point_with_vertical_bar'
    combination.set_sm(obstuple.combination.crosssection_over_binwidth(normalize_by_second_to_last_bin_width=True))
    combination.read()

    combination_statonly = differentials.scans.DifferentialSpectrum('combination_statonly', scandict.combination_statonly)
    # combination_statonly.POIs = get_POIs_oldstyle_scandir(scandict.combination_statonly)
    combination_statonly.color = 1
    combination_statonly.no_overflow_label = True
    combination_statonly.draw_method = 'repr_point_with_vertical_bar'
    combination_statonly.set_sm(obstuple.combination.crosssection_over_binwidth(normalize_by_second_to_last_bin_width=True))
    combination_statonly.read()

    systonly_histogram, systonly_histogram_xs = get_systonly_histogram(combination, combination_statonly)

    plot = differentials.plotting.plots.SpectraPlot(
        'spectra_{0}_statsyst'.format(obs_name) + ('_asimov' if args.asimov else ''),
        [ combination ]
        )
    plot.draw_multiscans = False
    plot.obsname = obs_name
    plot.add_top(systonly_histogram_xs, systonly_histogram_xs.draw_method, plot.leg)
    plot.add_bottom(systonly_histogram, systonly_histogram.draw_method)
    plot.draw()
    plot.wrapup()

@flag_as_option
def ptjet_plot_statsyst(args):
    obs_name = 'ptjet'
    obstuple = LatestBinning.obstuple_ptjet
    scandict = LatestPaths.scan[obs_name]['asimov' if args.asimov else 'observed']
    # scandict.combination_statonly = 'out/Scan_ptjet_Feb06_combination_statonly'

    combination = differentials.scans.DifferentialSpectrum('combination', scandict.combination)
    # combination.POIs = get_POIs_oldstyle_scandir(scandict.combination)
    combination.color = 1
    combination.title = 'Total'
    combination.no_overflow_label = True
    combination.draw_method = 'repr_point_with_vertical_bar'
    combination.set_sm(obstuple.combination.crosssection_over_binwidth(normalize_by_second_to_last_bin_width=True))
    combination.read()

    combination_statonly = differentials.scans.DifferentialSpectrum('combination_statonly', scandict.combination_statonly)
    # combination_statonly.POIs = get_POIs_oldstyle_scandir(scandict.combination_statonly)
    combination_statonly.color = 1
    combination_statonly.no_overflow_label = True
    combination_statonly.draw_method = 'repr_point_with_vertical_bar'
    combination_statonly.set_sm(obstuple.combination.crosssection_over_binwidth(normalize_by_second_to_last_bin_width=True))
    combination_statonly.read()

    systonly_histogram, systonly_histogram_xs = get_systonly_histogram(combination, combination_statonly)

    plot = differentials.plotting.plots.SpectraPlot(
        'spectra_{0}_statsyst'.format(obs_name) + ('_asimov' if args.asimov else ''),
        [ combination ]
        )
    plot.draw_multiscans = False
    plot.top_y_max = 10.
    plot.obsname = obs_name
    plot.obsunit = 'GeV'
    plot.add_top(systonly_histogram_xs, systonly_histogram_xs.draw_method, plot.leg)
    plot.add_bottom(systonly_histogram, systonly_histogram.draw_method)
    plot.draw()
    plot.wrapup()

@flag_as_option
def rapidity_plot_statsyst(args):
    obs_name = 'rapidity'
    obstuple = LatestBinning.obstuple_rapidity
    scandict = LatestPaths.scan[obs_name]['asimov' if args.asimov else 'observed']
    # scandict.combination_statonly = 'out/Scan_rapidity_Feb06_combination_statonly'

    combination = differentials.scans.DifferentialSpectrum('combination', scandict.combination)
    # combination.POIs = get_POIs_oldstyle_scandir(scandict.combination)
    combination.color = 1
    combination.title = 'Total'
    combination.no_overflow_label = True
    combination.draw_method = 'repr_point_with_vertical_bar'
    combination.set_sm(obstuple.combination.crosssection_over_binwidth(normalize_by_second_to_last_bin_width=False))
    combination.read()

    combination_statonly = differentials.scans.DifferentialSpectrum('combination_statonly', scandict.combination_statonly)
    # combination_statonly.POIs = get_POIs_oldstyle_scandir(scandict.combination_statonly)
    combination_statonly.color = 1
    combination_statonly.no_overflow_label = True
    combination_statonly.draw_method = 'repr_point_with_vertical_bar'
    combination_statonly.set_sm(obstuple.combination.crosssection_over_binwidth(normalize_by_second_to_last_bin_width=False))
    combination_statonly.read()

    systonly_histogram, systonly_histogram_xs = get_systonly_histogram(combination, combination_statonly)

    plot = differentials.plotting.plots.SpectraPlot(
        'spectra_{0}_statsyst'.format(obs_name) + ('_asimov' if args.asimov else ''),
        [ combination ]
        )
    plot.draw_multiscans = False
    plot.top_y_max = 300
    plot.obsname = obs_name
    plot.add_top(systonly_histogram_xs, systonly_histogram_xs.draw_method, plot.leg)
    plot.add_bottom(systonly_histogram, systonly_histogram.draw_method)
    plot.draw()
    plot.wrapup()


#____________________________________________________________________
@flag_as_option
def pth_smH_plot_lumiscale(args):
    TheoryCommands.SetPlotDir( 'plots_{0}'.format(datestr) )
    containers = []

    lumi35 = prepare_container('lumi35', LatestPaths.ws_combined_smH, LatestPaths.scan_combination_pth_smH_asimov)
    lumi35.SMcrosssections = LatestBinning.obs_pth.crosssection_over_binwidth()
    lumi35.color = 1
    containers.append(lumi35)

    # lumi35_new = prepare_container('lumi35_new', LatestPaths.ws_combined_smH, 'out/Scan_pth_smH_Feb12_combination_asimov')
    # lumi35_new.SMcrosssections = LatestBinning.obs_pth.crosssection_over_binwidth()
    # lumi35_new.color = 4
    # containers.append(lumi35_new)

    lumi300 = prepare_container('lumi300', LatestPaths.ws_hgg_smH, 'out/Scan_pth_smH_Feb12_combination_lumiScale_asimov_1')
    lumi300.SMcrosssections = LatestBinning.obs_pth.crosssection_over_binwidth()
    lumi300.color = 2
    containers.append(lumi300)

    lumi3000 = prepare_container(
        'lumi3000', LatestPaths.ws_hgg_smH, 'out/Scan_pth_smH_Feb12_combination_lumiScale_asimov_1',
        scale_scans = 10.
        )
    lumi3000.SMcrosssections = LatestBinning.obs_pth.crosssection_over_binwidth()
    lumi3000.color = 4
    containers.append(lumi3000)

    # lumi35 = prepare_container('lumi35', LatestPaths.ws_hgg_smH, LatestPaths.scan_hgg_PTH)
    # lumi35.SMcrosssections = LatestBinning.obs_pth.crosssection_over_binwidth()
    # lumi35.color = 1
    # containers.append(lumi35)

    for container in containers:
        draw_parabolas(container)

    SM = prepare_SM_container(
        LatestBinning.obs_pth.crosssection_over_binwidth(normalize_by_second_to_last_bin_width=True),
        LatestBinning.obs_pth.binning
        )
    containers.append(SM)

    PlotCommands.PlotSpectraOnTwoPanel(
        'twoPanel_pthSpectrum' + ('_statsyst' if args.statsyst else ''),
        containers,
        xTitle = 'p_{T}^{H} (GeV)',
        yTitleTop = '#Delta#sigma/#Deltap_{T}^{H} (pb/GeV)',
        # 
        # yMinExternalTop = 0.0005,
        # yMaxExternalTop = 110.,
        )

#____________________________________________________________________
@flag_as_option
def all_tables(args):
    Commands.DisableWarnings()
    pth_smH_tables(args)
    pth_ggH_tables(args)
    ptjet_tables(args)
    njets_tables(args)
    rapidity_tables(args)
    Commands.DisableWarnings(False)

@flag_as_option
def pth_smH_tables(args):
    TheoryCommands.SetPlotDir( 'plots_{0}'.format(datestr) )
    differentialTable = DifferentialTable.DifferentialTable(name='pth_smH', last_bin_is_overflow=True)
    for decay_channel in ['hgg', 'hzz', 'combination']:
        statsyst = read_container(args, 'pth_smH', pth_smH_obs(decay_channel).crosssection_over_binwidth(), decay_channel, statonly=False )
        statonly = read_container(args, 'pth_smH', pth_smH_obs(decay_channel).crosssection_over_binwidth(), decay_channel, statonly=True )
        differentialTable.calculate_stat_syst(statsyst.name, statsyst, statonly)
    print differentialTable.repr_twiki_symm()
    print
    # differentialTable.do_xs = True
    # print differentialTable.repr_twiki_symm()

@flag_as_option
def pth_ggH_tables(args):
    TheoryCommands.SetPlotDir( 'plots_{0}'.format(datestr) )
    differentialTable = DifferentialTable.DifferentialTable(name='pth_ggH', last_bin_is_overflow=True)
    for decay_channel in ['hgg', 'hzz', 'combination']:
        statsyst = read_container(args, 'pth_ggH', pth_ggH_obs(decay_channel).crosssection_over_binwidth(), decay_channel, statonly=False )
        statonly = read_container(args, 'pth_ggH', pth_ggH_obs(decay_channel).crosssection_over_binwidth(), decay_channel, statonly=True )
        differentialTable.calculate_stat_syst(statsyst.name, statsyst, statonly)
    print differentialTable.repr_twiki_symm()
    print
    # differentialTable.do_xs = True
    # print differentialTable.repr_twiki_symm()

@flag_as_option
def ptjet_tables(args):
    TheoryCommands.SetPlotDir( 'plots_{0}'.format(datestr) )
    differentialTable = DifferentialTable.DifferentialTable(name='ptjet', last_bin_is_overflow=True)
    for decay_channel in ['hgg', 'hzz', 'combination']:
        statsyst = read_container(args, 'ptjet', ptjet_obs(decay_channel).crosssection_over_binwidth(), decay_channel, statonly=False )
        statonly = read_container(args, 'ptjet', ptjet_obs(decay_channel).crosssection_over_binwidth(), decay_channel, statonly=True )
        differentialTable.calculate_stat_syst(statsyst.name, statsyst, statonly)
    print differentialTable.repr_twiki_symm()
    print
    # differentialTable.do_xs = True
    # print differentialTable.repr_twiki_symm()

@flag_as_option
def njets_tables(args):
    TheoryCommands.SetPlotDir( 'plots_{0}'.format(datestr) )
    differentialTable = DifferentialTable.DifferentialTable(name='njets', last_bin_is_overflow=True)
    for decay_channel in ['hgg', 'hzz', 'combination']:
        statsyst = read_container(args, 'njets', njets_obs(decay_channel).crosssection_over_binwidth(), decay_channel, statonly=False )
        statonly = read_container(args, 'njets', njets_obs(decay_channel).crosssection_over_binwidth(), decay_channel, statonly=True )
        differentialTable.calculate_stat_syst(statsyst.name, statsyst, statonly)
    print differentialTable.repr_twiki_symm()
    print
    # differentialTable.do_xs = True
    # print differentialTable.repr_twiki_symm()

@flag_as_option
def rapidity_tables(args):
    TheoryCommands.SetPlotDir( 'plots_{0}'.format(datestr) )
    differentialTable = DifferentialTable.DifferentialTable(name='rapidity', last_bin_is_overflow=False)
    for decay_channel in ['hgg', 'hzz', 'combination']:
        statsyst = read_container(args, 'rapidity', rapidity_obs(decay_channel).crosssection_over_binwidth(), decay_channel, statonly=False )
        statonly = read_container(args, 'rapidity', rapidity_obs(decay_channel).crosssection_over_binwidth(), decay_channel, statonly=True )
        differentialTable.calculate_stat_syst(statsyst.name, statsyst, statonly)
    print differentialTable.repr_twiki_symm()
    print
    # differentialTable.do_xs = True
    # print differentialTable.repr_twiki_symm()
