from OptionHandler import flag_as_option, flag_as_parser_options

import LatestPaths
import sys
sys.path.append('src')
import Commands
import CombineToolWrapper
import differentialTools

from time import strftime
datestr = strftime( '%b%d' )

import os
from os.path import *
import copy

#____________________________________________________________________
@flag_as_parser_options
def add_parser_options(parser):
    # parser.add_argument( '--lumiScale',  action='store_true' )
    pass

#____________________________________________________________________
def run_postfit_fastscan_scan(config):
    # Make sure no previous run directory is overwritten
    config.make_unique_directory()

    postfit = CombineToolWrapper.CombinePostfit(config)
    postfit.run()
    postfit_file = postfit.get_output()

    fastscan = CombineToolWrapper.CombineFastScan(config)
    fastscan.run(postfit_file)
    fastscan_file = fastscan.get_output()

    pointwisescan = CombineToolWrapper.CombinePointwiseScan(config)
    pointwisescan.run(postfit_file, fastscan_file)

def scan_directly(config):
    # Make sure no previous run directory is overwritten
    config.make_unique_directory()
    scan = CombineToolWrapper.CombineScan(config)
    scan.run()

def basic_config(args, hurry=False):
    config = CombineToolWrapper.CombineConfig(args)
    config.onBatch       = True
    config.queue         = 'all.q'
    if hurry:
        Commands.Warning( 'Running with quick settings' )
        config.nPointsPerJob = 5
        config.queue         = 'short.q'

    if args.hzz:
        config.nPointsPerJob = 320
        config.queue         = 'short.q'

    if args.asimov:
        config.asimov = True
    else:
        config.asimov = False

    config.decay_channel = differentialTools.get_decay_channel_tag(args)

    config.nPoints = 70*70
    kappab_ranges = [ -15., 15. ]
    kappac_ranges = [ -35., 35. ]
    if config.args.lumiScale:
        config.nPoints = 40*40
        kappab_ranges = [ -7., 7. ]
        kappac_ranges = [ -17., 17. ]

    config.POIs = [ 'kappab', 'kappac' ]
    config.PhysicsModelParameters = [ 'kappab=1.0', 'kappac=1.0' ]
    config.PhysicsModelParameterRanges = [
        'kappab={0},{1}'.format( kappab_ranges[0], kappab_ranges[1] ),
        'kappac={0},{1}'.format( kappac_ranges[0], kappac_ranges[1] )
        ]
    config.subDirectory = 'out/Scan_Yukawa_{0}_{1}'.format(datestr, config.decay_channel)
    config.deltaNLLCutOff = 70.
    return config

def nominal_datacard(args):
    try:
        # d = {
        #     'hgg' : LatestPaths.ws_hgg_Yukawa,
        #     'hzz' : LatestPaths.ws_hzz_Yukawa,
        #     'combination' : LatestPaths.ws_combined_Yukawa
        #     }
        d = {
        'hgg'         : 'out/workspaces_Feb23/hgg_Yukawa_reweighted_nominal.root',
        'hzz'         : 'out/workspaces_Feb23/hzz_Yukawa_reweighted_nominal.root',
        'combination' : 'out/workspaces_Feb23/combination_Yukawa_reweighted_nominal.root',
        }
        nominal_datacard = d[differentialTools.get_decay_channel_tag(args)]
    except KeyError:
        raise NotImplementedError('Only --hgg, --hzz and --combination implemented for this scan')
    return nominal_datacard

def assert_decay_channel(args, allowed_decay_channels=['combination']):
    decay_channel = differentialTools.get_decay_channel_tag(args)
    if not decay_channel in allowed_decay_channels:
        raise NotImplementedError(
            'Decay channel \'{0}\' is not allowed for this option '
            '(allowed: {1})'
            .format(decay_channel, allowed_decay_channels)
            )

def assert_asimov(args):
    if not args.asimov:
        raise RuntimeError(
            'Option is only allowed in combination with the flag --asimov'
            )

#____________________________________________________________________
def set_decay_channel(args, given_channel):
    for decay_channel in ['hgg', 'hzz', 'combination', 'hbb', 'combWithHbb']:
        setattr(args, decay_channel, False)
    setattr(args, given_channel, True)

import traceback
def try_call_function_with_args(fn, args):
    try:
        fn(args)
    except Exception as exc:
        print traceback.format_exc()
        print exc
        pass

@flag_as_option
def all_scans_Yukawa(args_original):
    args = copy.deepcopy(args_original)

    # for asimov in [ False, True ]:
    #     args.asimov = asimov
    #     for decay_channel in ['hgg', 'hzz', 'combination']:
    #         set_decay_channel(args, decay_channel)
    #         # t2ws_Yukawa_nominal(args)
    #         try_call_function_with_args(scan_yukawa, args)

    set_decay_channel(args, 'combination')
    args.asimov = True

    fns = [
        scan_yukawa_uncorrelatedTheoryUnc,
        # scan_yukawa_fitOnlyNormalization,
        # scan_yukawa_oneKappa,
        scan_yukawa_lumiScale,
        scan_yukawa_BRdependent,
        # scan_yukawa_BRdependent_and_profiledTotalXS,
        scan_yukawa_profiledTotalXS,
        ]
    for fn in fns:
        try_call_function_with_args(fn, args)



@flag_as_option
def scan_yukawa(args):
    config = basic_config(args)
    config.datacard = nominal_datacard(args)
    run_postfit_fastscan_scan(config)

@flag_as_option
def scan_yukawa_uncorrelatedTheoryUnc(args):
    config = basic_config(args)
    config.datacard = 'out/workspaces_Feb23/combination_Yukawa_reweighted_uncorrelatedTheoryUnc_uncorrelatedTheoryUnc.root'
    config.subDirectory += '_uncorrelatedTheoryUnc'
    run_postfit_fastscan_scan(config)

@flag_as_option
def scan_yukawa_fitOnlyNormalization(args):
    config = basic_config(args)
    config.datacard = LatestPaths.ws_combined_Yukawa_profiledTotalXS_fitOnlyNormalization
    config.subDirectory += '_fitOnlyNormalization'
    run_postfit_fastscan_scan(config)

@flag_as_option
def scan_yukawa_oneKappa(args):
    for kappa in ['kappac', 'kappab']:
        config = basic_config(args)
        config.datacard = nominal_datacard(args)

        config.nPoints       = 72
        config.nPointsPerJob = 3
        config.queue         = 'short.q'
        config.POIs          = [ kappa ]

        otherKappa = { 'kappab' : 'kappac', 'kappac' : 'kappab' }[kappa]
        config.floatNuisances.append(otherKappa)
        config.subDirectory += '_oneKappa_' + kappa

        if args.lumiScale:
            config.datacard = 'out/workspaces_Feb12/combinedCard_Nov03_CouplingModel_Yukawa_withTheoryUncertainties_lumiScale.root'
            config.subDirectory += '_lumiStudy'
            config.freezeNuisances.append('lumiScale')
            config.hardPhysicsModelParameters.append( 'lumiScale=8.356546' )
        scan_directly(config)

@flag_as_option
def scan_yukawa_lumiScale(args):
    assert_asimov(args)
    config = basic_config(args)
    # config.datacard = LatestPaths.ws_combined_Yukawa_lumiScalable
    # config.datacard = 'out/workspaces_Feb12/combinedCard_Nov03_CouplingModel_Yukawa_withTheoryUncertainties_lumiScale.root'
    config.datacard = 'out/workspaces_Feb23/combination_Yukawa_reweighted_lumiScale.root'
    config.freezeNuisances.append('lumiScale')
    config.hardPhysicsModelParameters.append( 'lumiScale=8.356546' )
    config.subDirectory += '_lumiStudy'
    # config.hardPhysicsModelParameters.append( 'lumiScale=83.56546' )
    # config.subDirectory += '_lumiStudy3000fb'
    run_postfit_fastscan_scan(config)

@flag_as_option
def scan_yukawa_BRdependent(args):
    assert_asimov(args)
    config = basic_config(args)
    # config.datacard = LatestPaths.ws_combined_Yukawa_couplingDependentBR
    config.datacard = 'out/workspaces_Feb23/combination_Yukawa_reweighted_BRcouplingDependency.root'
    config.subDirectory += '_couplingDependentBR'
   
    config.PhysicsModelParameters.append('kappa_V=0.999')

    # config.freezeNuisances.append('kappa_V')

    config.floatNuisances.append('kappa_V')
    config.PhysicsModelParameterRanges.append('kappa_V=-1000.0:1.0')
    config.subDirectory += '_floatKappaV'

    run_postfit_fastscan_scan(config)

@flag_as_option
def scan_yukawa_BRdependent_and_profiledTotalXS(args):
    assert_asimov(args)
    config = basic_config(args)
    config.datacard = LatestPaths.ws_combined_Yukawa_couplingDependentBR_profiledTotalXS
    config.subDirectory += '_couplingDependentBR_profiledTotalXS'
    config.fix_parameter_at_value('kappa_V', 0.999)
    run_postfit_fastscan_scan(config)

@flag_as_option
def scan_yukawa_profiledTotalXS(args):
    assert_asimov(args)
    config = basic_config(args)
    # config.datacard = LatestPaths.ws_combined_Yukawa_profiledTotalXS
    config.datacard = 'out/workspaces_Feb23/combination_Yukawa_reweighted_profiledTotalXS.root'
    config.subDirectory += '_profiledTotalXS'
    config.nPoints = 60*60
    config.nPointsPerJob = 15
    config.deltaNLLCutOff = 120.
    run_postfit_fastscan_scan(config)

