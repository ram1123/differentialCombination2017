import itertools

import ROOT
import plotting_utils as utils
from canvas import c, global_color_cycle

import logging
import differentials.logger

from array import array

class Legend(object):
    """Wrapper for TLegend class that allows flexible drawing of a legend on a multi panel plot"""
    def __init__(
            self,
            x1=None, y1=None, x2=None, y2=None,
            ):

        if x1 is None:
            self._x1 = lambda c: c.GetLeftMargin()
        else:
            self._x1 = x1

        if x2 is None:
            self._x2 = lambda c: 1. - c.GetRightMargin()
        else:
            self._x2 = x2

        if y1 is None:
            self._y1 = lambda c: 1. - c.GetTopMargin() - 0.15
        else:
            self._y1 = y1

        if y2 is None:
            self._y2 = lambda c: 1. - c.GetTopMargin()
        else:
            self._y2 = y2

        self._entries = []
        self.legend = ROOT.TLegend(0., 1., 0., 1.)
        self.legend.SetBorderSize(0)
        self.legend.SetFillStyle(0)

        ROOT.SetOwnership(self.legend, False)

        self.auto_n_columns = True


    def __getattr__(self, name):
        """
        Reroutes calls TLegendMultiPanel.xxxx to TLegendMultiPanel.legend.xxxx
        This method should only be called if the attribute could not be found in TLegendMultiPanel
        """
        return getattr(self.legend, name)

    def AddEntry(self, *args):
        """Save entries in a python list, but add them to the actual legend later"""
        self._entries.append(args)

    def SetNColumns(self, value):
        self.auto_n_columns = False
        self.legend.SetNColumns(value)

    def n_columns_heuristic(self):
        n_entries = len(self._entries)
        return min(n_entries, 4)

    def Draw(self, drawStr=''):
        logging.debug('Drawing Legend {0} on gPad {1} with {2} entries'.format(self, ROOT.gPad.GetName(), len(self._entries)))
        x1 = self._x1(ROOT.gPad) if callable(self._x1) else self._x1
        y1 = self._y1(ROOT.gPad) if callable(self._y1) else self._y1
        x2 = self._x2(ROOT.gPad) if callable(self._x2) else self._x2
        y2 = self._y2(ROOT.gPad) if callable(self._y2) else self._y2
        logging.debug('Coordinates: x1 = {0}, y1 = {1}, x2 = {2}, y2 = {3}'.format(x1, y1, x2, y2))

        self.legend.SetX1(x1)
        self.legend.SetY1(y1)
        self.legend.SetX2(x2)
        self.legend.SetY2(y2)

        if self.auto_n_columns:
            self.legend.SetNColumns(self.n_columns_heuristic())

        for args in self._entries:
            self.legend.AddEntry(*args)
        self.legend.Draw(drawStr)


class ContourDummyLegend(Legend):
    """Special instance of Legend that creates some default objects and stores them in the legend"""

    dummy1sigma = ROOT.TGraph( 1, array( 'f' , [-999.] ), array( 'f' , [-999.] )  )
    dummy1sigma.SetLineWidth(2)
    dummy1sigma.SetName('dummy1sigma')
    ROOT.SetOwnership( dummy1sigma, False )

    dummy2sigma = ROOT.TGraph( 1, array( 'f' , [-999.] ), array( 'f' , [-999.] )  )
    dummy2sigma.SetLineWidth(2)
    dummy2sigma.SetLineStyle(2)
    dummy2sigma.SetName('dummy2sigma')
    ROOT.SetOwnership( dummy2sigma, False )

    dummySM = ROOT.TGraph( 1, array( 'f' , [-999.] ), array( 'f' , [-999.] )  )
    dummySM.SetMarkerSize(2)
    dummySM.SetMarkerStyle(21)
    dummySM.SetMarkerColor(16)
    dummySM.SetName('dummySM')
    ROOT.SetOwnership( dummySM, False )

    dummybestfit = ROOT.TGraph( 1, array( 'f' , [-999.] ), array( 'f' , [-999.] )  )
    dummybestfit.SetMarkerSize(2)
    dummybestfit.SetMarkerStyle(34)
    dummybestfit.SetName('dummybestfit')
    ROOT.SetOwnership( dummybestfit, False )

    def __init__(self, *args, **kwargs):
        super(ContourDummyLegend, self).__init__(*args, **kwargs)
        self.disable_1sigma = False
        self.disable_2sigma = False
        self.disable_SM = False
        self.disable_bestfit = False

    def Draw(self, draw_str=''):
        if not self.disable_1sigma:
            self.AddEntry(self.dummy1sigma.GetName(), '1 #sigma', 'l')
            self.dummy1sigma.Draw('P')
        if not self.disable_2sigma:
            self.AddEntry(self.dummy2sigma.GetName(), '2 #sigma', 'l')
            self.dummy2sigma.Draw('P')
        if not self.disable_SM:
            self.AddEntry(self.dummySM.GetName(), 'SM', 'p')
            self.dummySM.Draw('P')
        if not self.disable_bestfit:
            self.AddEntry(self.dummybestfit.GetName(), 'Bestfit', 'p')
            self.dummybestfit.Draw('P')        
        super(ContourDummyLegend, self).Draw(draw_str)


class Latex(object):
    """docstring"""
    def __init__(self, x, y, text):
        self.x = x
        self.y = y
        self.text = text
        self.tlatex = ROOT.TLatex()
        ROOT.SetOwnership(self.tlatex, False)

    def __getattr__(self, name):
        """
        Reroutes calls TLatexMultiPanel.xxxx to TLatexMultiPanel.tlatex.xxxx
        This method should only be called if the attribute could not be found in TLatexMultiPanel
        """
        return getattr(self.tlatex, name)

    def Draw(self, draw_str=None):
        x = self.x(ROOT.gPad) if callable(self.x) else self.x
        y = self.y(ROOT.gPad) if callable(self.y) else self.y
        logging.debug(
            'Drawing {0}; x={1}, y={2}, text={3}'
            .format(self, x, y, self.text)
            )
        self.tlatex.DrawLatex(x, y, self.text)


class CMS_Latex_type(Latex):
    """
    Specific implementation of Latex, that prints "CMS Preliminary" or
    "CMS Supplementary" at the default positions w.r.t. a TPad
    """
    CMS_type_str = 'Preliminary'
    apply_text_offset = True
    text_size    = 0.06

    def __init__(self, text=None, text_size=None):
        if text is None: text = self.CMS_type_str
        if not(text_size is None):
            self.text_size = text_size

        text = '#bf{{CMS}} #it{{#scale[0.75]{{{0}}}}}'.format(self.CMS_type_str)
        x = lambda c: c.GetLeftMargin()
        y = self._y
        super(CMS_Latex_type, self).__init__(x, y, text)

    def _y(self, c):
        """Internal use only"""
        return 1.-c.GetTopMargin() + self.get_text_offset()

    def get_text_offset(self):
        if self.apply_text_offset:
            return 0.25 * self.text_size

    def Draw(self, *args, **kwargs):
        self.tlatex.SetNDC()
        self.tlatex.SetTextAlign(11)
        self.tlatex.SetTextFont(42)
        self.tlatex.SetTextSize(self.text_size)
        super(CMS_Latex_type, self).Draw(*args, **kwargs)


class CMS_Latex_lumi(Latex):
    """
    Specific implementation of Latex, that prints "CMS Preliminary" or
    "CMS Supplementary" at the default positions w.r.t. a TPad
    """
    CMS_lumi = 35.9
    apply_text_offset = True
    text_size    = 0.06

    def __init__(self, lumi=None, text_size=None):
        if lumi is None: lumi = self.CMS_lumi
        if not(text_size is None):
            self.text_size = text_size

        text = '{0:.1f} fb^{{-1}} (13 TeV)'.format(lumi)
        x = lambda c: 1.-c.GetRightMargin()
        y = self._y
        super(CMS_Latex_lumi, self).__init__(x, y, text)

    def _y(self, c):
        """Internal use only"""
        return 1.-c.GetTopMargin() + self.get_text_offset()

    def get_text_offset(self):
        if self.apply_text_offset:
            return 0.25 * self.text_size

    def Draw(self, *args, **kwargs):
        self.tlatex.SetNDC()
        self.tlatex.SetTextAlign(31)
        self.tlatex.SetTextFont(42)
        self.tlatex.SetTextSize(self.text_size)
        super(CMS_Latex_lumi, self).Draw(*args, **kwargs)



class Base(object):
    """Alternative for get_plot_base"""

    def __init__(self, x_min=0., y_min=0., x_max=1., y_max=1., x_title='', y_title=''):
        self.x_min   = x_min
        self.x_max   = x_max
        self.y_min   = y_min
        self.y_max   = y_max
        self.x_title = x_title
        self.y_title = y_title
        self.H = utils.get_plot_base(
            x_min   = self.x_min,
            x_max   = self.x_max,
            y_min   = self.y_min,
            y_max   = self.y_max,
            x_title = self.x_title,
            y_title = self.y_title,
            )

    def __getattr__(self, name):
        return getattr(self.H, name)

    def set_x_min(self, x_min):
        self.x_min = x_min
        self.H.GetXaxis().SetLimits(self.x_min, self.x_max)

    def set_x_max(self, x_max):
        self.x_max = x_max
        self.H.GetXaxis().SetLimits(self.x_min, self.x_max)

    def set_y_min(self, y_min):
        self.y_min = y_min
        self.H.SetMinimum(self.y_min)

    def set_y_max(self, y_max):
        self.y_max = y_max
        self.H.SetMaximum(self.y_max)

    def set(self, x_min=None, x_max=None, y_min=None, y_max=None):
        if not(x_min is None): self.set_x_min(x_min)
        if not(x_max is None): self.set_x_max(x_max)
        if not(y_min is None): self.set_y_min(y_min)
        if not(y_max is None): self.set_y_max(y_max)

    def Draw(self, draw_str=''):
        self.H.Draw('P')


class Histogram(object):
    """docstring for Histogram"""

    color_cycle = global_color_cycle
    fill_style_cycle = itertools.cycle([ 3245, 3254, 3205 ])

    def __init__(self, name, title, bin_boundaries, bin_values, color=None):
        super(Histogram, self).__init__()
        self.name = name
        self.title = title

        if len(bin_boundaries) != len(bin_values)+1:
            raise ValueError(
                'Inconsistent lengths; len(bin_boundaries)={0} != len(bin_values)+1={1}'
                '\nbin_boundaries: {2}'
                '\nbin_values: {3}'
                .format(
                    len(bin_boundaries), len(bin_values)+1,
                    bin_boundaries, bin_values
                    )
                )

        self.bin_values = bin_values[:]
        self.bin_boundaries = bin_boundaries[:]
        self.n_bins = len(bin_boundaries)-1

        self.has_uncertainties = False
        if color is None:
            self.color = self.color_cycle.next()
        else:
            self.color = color

        self.fill_style = self.fill_style_cycle.next()
        self.fill_color = self.color
        self.marker_style = 8
        self.marker_size = 0
        self.marker_color = self.color
        self.line_color = self.color
        self.line_width = 2

        self.last_bin_is_overflow = False
        self._legend = None


    def set_last_bin_is_overflow(self, flag=True, method='SECONDTOLASTBINWIDTH', hard_value=None):
        logging.debug('Last bin is specified to be overflow, so the last bin boundary will be modified')
        self.last_bin_is_overflow = True
        if method == 'SECONDTOLASTBINWIDTH':
            new_last_bin_boundary = self.bin_boundaries[-2] + (self.bin_boundaries[-2] - self.bin_boundaries[-3])
        elif method == 'HARDVALUE':
            if hard_value is None:
                raise TypeError('method \'HARDVALUE\' expects argument hard_value to be passed')
            new_last_bin_boundary = hard_value
        else:
            raise ValueError('Method \'{0}\' is not implemented'.format(method))
        logging.debug('Will replace last bin boundary {0} by {1}'.format(self.bin_boundaries[-1], new_last_bin_boundary))
        self.bin_boundaries[-1] = new_last_bin_boundary


    def x_min(self):
        return self.bin_boundaries[0]

    def x_max(self):
        return self.bin_boundaries[-1]

    def y_min(self, only_positive=False):
        if self.has_uncertainties:
            if only_positive:
                return min([b for b in self.bounds_down if b>0.])
            else:
                return min(self.bounds_down)
        else:
            if only_positive:
                return min([b for b in self.bin_values if b>0.])
            else:
                return min(self.bin_values)            

    def y_max(self, only_positive=False):
        if self.has_uncertainties:
            if only_positive:
                return max([b for b in self.bounds_up if b>0.])
            else:
                return max(self.bounds_up)
        else:
            if only_positive:
                return max([b for b in self.bin_values if b>0.])
            else:
                return max(self.bin_values)            

    def drop_first_bin(self):
        logging.debug('Dropping first bin from histogram (name={0})'.format(self.name))
        self.bin_boundaries.pop(0)
        self.bin_values.pop(0)
        self.n_bins -= 1
        if self.has_uncertainties:
            self.errs_up.pop(0)
            self.bounds_up.pop(0)
            self.errs_down.pop(0)
            self.bounds_down.pop(0)

    def set_err_up(self, errs_up):
        self.errs_up = [ abs(i) for i in errs_up ]
        self.bounds_up = [ c+e for c, e in zip(self.bin_values, self.errs_up) ]
        self.has_uncertainties = True

    def set_err_down(self, errs_down):
        self.errs_down = [ abs(i) for i in errs_down ]
        self.bounds_down = [ c-abs(e) for c, e in zip(self.bin_values, self.errs_down) ]
        self.has_uncertainties = True

    def get_bin_centers(self):
        return [ 0.5*(left+right) for left, right in zip(self.bin_boundaries[:-1], self.bin_boundaries[1:]) ]

    def get_bin_widths(self):
        return [ right-left for left, right in zip(self.bin_boundaries[:-1], self.bin_boundaries[1:]) ]

    def get_half_bin_widths(self):
        return [ 0.5*i for i in self.get_bin_widths() ]

    def get_zeroes(self):
        return [0.0 for i in xrange(self.n_bins)]


    def repr_basic_histogram(self, leg=None):
        H = ROOT.TH1F(
            utils.get_unique_rootname(), '',
            len(self.bin_boundaries)-1, array( 'f', self.bin_boundaries)
            )
        ROOT.SetOwnership( H, False )
        H.SetLineColor(self.color)
        H.SetLineWidth(2)
        for i_bin in xrange(self.n_bins):
            H.SetBinContent( i_bin+1, self.bin_values[i_bin] )

        if not(leg is None):
            leg.AddEntry(H.GetName(), self.title, 'l')

        return [ (H, 'HISTSAME') ]


    def repr_horizontal_bar_and_narrow_fill(self, leg=None):
        return self.repr_horizontal_bars() + self.repr_uncertainties_narrow_filled_area(leg)


    def repr_horizontal_bars(self):
        Tg = ROOT.TGraphErrors(
            self.n_bins,
            array( 'f', self.get_bin_centers() ),
            array( 'f', self.bin_values ),
            array( 'f', self.get_half_bin_widths() ),
            array( 'f', self.get_zeroes() ),
            )
        ROOT.SetOwnership( Tg, False )
        Tg.SetName( utils.get_unique_rootname() )

        Tg.SetMarkerSize(0)
        Tg.SetMarkerColor(self.color)
        Tg.SetLineColor(   getattr(self, 'setLineColor',   self.color ) )
        # Tg.SetLineWidth(   getattr(self, 'setLineWidth',   2 ) )

        return [ (Tg, 'EPSAME') ]


    def repr_uncertainties_filled_area(self, leg=None):
        Tg = ROOT.TGraphAsymmErrors(
            self.n_bins,
            array( 'f', self.get_bin_centers() ),
            array( 'f', self.bin_values ),
            array( 'f', [ 0.45*w for w in self.get_bin_widths() ] ),
            array( 'f', [ 0.45*w for w in self.get_bin_widths() ] ),
            array( 'f', self.errs_down ),
            array( 'f', self.errs_up ),
            )
        ROOT.SetOwnership( Tg, False )
        Tg.SetName( utils.get_unique_rootname() )
    
        Tg.SetFillStyle(   getattr(self, 'setFillStyle',   3245 ) )
        Tg.SetMarkerStyle( getattr(self, 'setMarkerStyle', 8 ) )
        Tg.SetMarkerSize(  getattr(self, 'setMarkerSize',  0 ) )
        Tg.SetFillColor(   getattr(self, 'setFillColor',   self.color ) )
        Tg.SetMarkerColor( getattr(self, 'setMarkerColor', self.color ) )
        Tg.SetLineColor(   getattr(self, 'setLineColor',   self.color ) )

        if not(leg is None):
            leg.AddEntry( Tg.GetName(), self.title, 'LF' )

        return [ (Tg, 'E2PSAME') ]


    def repr_uncertainties_narrow_filled_area(self, leg=None):
        Tg = ROOT.TGraphAsymmErrors(
            self.n_bins,
            array( 'f', self.get_bin_centers() ),
            array( 'f', self.bin_values ),
            array( 'f', [ 0.1*w for w in self.get_bin_widths() ] ),
            array( 'f', [ 0.1*w for w in self.get_bin_widths() ] ),
            array( 'f', self.errs_down ),
            array( 'f', self.errs_up ),
            )
        ROOT.SetOwnership( Tg, False )
        Tg.SetName( utils.get_unique_rootname() )
    
        Tg.SetMarkerStyle( getattr(self, 'setMarkerStyle', 8 ) )
        Tg.SetMarkerSize(  getattr(self, 'setMarkerSize',  0 ) )
        Tg.SetMarkerColor( getattr(self, 'setMarkerColor', self.color ) )
        Tg.SetLineColor(   getattr(self, 'setLineColor',   self.color ) )

        # Tg.SetFillStyle(   getattr(self, 'setFillStyle',   3245 ) )
        # Tg.SetFillColor(   getattr(self, 'setFillColor',   self.color ) )
        Tg.SetFillColorAlpha(self.color, 0.30)

        if not(leg is None):
            leg.AddEntry( Tg.GetName(), self.title, 'LF' )

        return [ (Tg, 'E2PSAME') ]


    def repr_uncertainties_fully_filled_area(self, leg=None):
        Tg = ROOT.TGraphAsymmErrors(
            self.n_bins,
            array( 'f', self.get_bin_centers() ),
            array( 'f', self.bin_values ),
            array( 'f', self.get_half_bin_widths() ),
            array( 'f', self.get_half_bin_widths() ),
            array( 'f', self.errs_down ),
            array( 'f', self.errs_up ),
            )
        ROOT.SetOwnership( Tg, False )
        Tg.SetName( utils.get_unique_rootname() )
    
        Tg.SetMarkerStyle( getattr(self, 'setMarkerStyle', 8 ) )
        Tg.SetMarkerSize(  getattr(self, 'setMarkerSize',  0 ) )
        Tg.SetMarkerColor( getattr(self, 'setMarkerColor', self.color ) )
        Tg.SetLineColor(   getattr(self, 'setLineColor',   self.color ) )

        # Tg.SetFillStyle(   getattr(self, 'setFillStyle',   3245 ) )
        # Tg.SetFillColor(   getattr(self, 'setFillColor',   self.color ) )
        Tg.SetFillColorAlpha(self.color, 0.30)

        if not(leg is None):
            leg.AddEntry( Tg.GetName(), self.title, 'LF' )

        return [ (Tg, 'E2PSAME') ]


    def repr_point_with_vertical_bar(self, leg=None):

        Tg = ROOT.TGraphAsymmErrors(
            self.n_bins,
            array( 'f', self.get_bin_centers() ),
            array( 'f', self.bin_values ),
            array( 'f', [ 0.0 for i in xrange(self.n_bins) ] ),
            array( 'f', [ 0.0 for i in xrange(self.n_bins) ] ),
            array( 'f', self.errs_down ),
            array( 'f', self.errs_up ),
            )
        ROOT.SetOwnership( Tg, False )
        Tg.SetName( utils.get_unique_rootname() )

        Tg.SetMarkerStyle( getattr(self, 'setMarkerStyle', 8 ) )
        Tg.SetFillColor(   getattr(self, 'setFillColor',   self.color ) )
        Tg.SetMarkerColor( getattr(self, 'setMarkerColor', self.color ) )
        Tg.SetLineColor(   getattr(self, 'setLineColor',   self.color ) )

        if not(leg is None):
            leg.AddEntry( Tg.GetName(), self.title, 'PE' )

        return [(Tg, 'PSAME')]

    def repr_point_with_vertical_bar_and_horizontal_bar(self, leg=None):
        return self.repr_point_with_vertical_bar(leg) + self.repr_horizontal_bars()

    def Draw(self, draw_style):
        logging.debug('Drawing Histogram {0} with draw_style {1}; legend: {2}'.format(self, draw_style, self._legend))
        for obj, draw_str in getattr(self, draw_style)(self._legend):
            obj.Draw(draw_str)



class Graph(object):
    """docstring for Graph"""

    color_cycle = global_color_cycle
    fill_style_cycle = itertools.cycle([ 3245, 3254, 3205 ])

    def __init__(self, name, title, xs, ys, color=None):
        super(Graph, self).__init__()
        self.name = name
        self.title = title

        self.xs = xs
        self.ys = ys

        self.has_uncertainties = False
        if color is None:
            self.color = self.color_cycle.next()
        else:
            self.color = color

        self.fill_style = self.fill_style_cycle.next()
        self.line_width = 2

        # self.marker_style
        # self.marker_size

        # # self.fill_color = self.color
        # # self.marker_color = self.color
        # # self.line_color = self.color

        self._legend = None

        
    def set_err_up(self, errs_up):
        self.errs_up = [ abs(i) for i in errs_up ]
        self.bounds_up = [ c+e for c, e in zip(self.bin_values, self.errs_up) ]
        self.has_uncertainties = True

    def set_err_down(self, errs_down):
        self.errs_down = [ abs(i) for i in errs_down ]
        self.bounds_down = [ c+e for c, e in zip(self.bin_values, self.errs_down) ]
        self.has_uncertainties = True

    def filter(self, x_min=-10e9, x_max=10e9, y_min=-10e9, y_max=10e9, inplace=True):
        passed_x = []
        passed_y = []
        for x, y in zip(self.xs, self.ys):
            if (x < x_min or x > x_max) or (y < y_min or y > y_max):
                continue
            else:
                passed_x.append(x)
                passed_y.append(y)
        if inplace:
            self.xs = passed_x
            self.ys = passed_y
        else:
            return passed_x, passed_y

    def check_input_sanity(self):
        if len(self.xs) == 0:
            raise ValueError(
                'Graph {0} ({1}) has zero entries in self.xs'
                .format(self.name, self.title)
                )
        if len(self.xs) != len(self.ys):
            raise ValueError(
                'Graph {0} ({1}) has unidentical lengths xs and ys: xs={2}, ys={3}'
                .format(self.name, self.title, len(self.xs), len(self.ys))
                )

    def repr_basic_line(self, leg=None):
        self.check_input_sanity()

        Tg = ROOT.TGraph(len(self.xs), array('f', self.xs), array('f', self.ys))
        ROOT.SetOwnership(Tg, False)
        Tg.SetName(utils.get_unique_rootname())

        Tg.SetLineColor(self.color)
        Tg.SetLineWidth(self.line_width)

        if not(leg is None):
            leg.AddEntry( Tg.GetName(), self.title, 'L' )

        return [(Tg, 'SAMEL')]


    def repr_smooth_line(self, leg=None):
        Tg, _ = self.repr_basic_line(leg)[0]
        return [(Tg, 'SAMEC')]

    def repr_vertical_line_at_minimum(self, leg=None):
        x_at_minimum = self.xs[self.ys.index(min(self.ys))]
        logging.info('Vertical line: x minimum = {0}'.format(x_at_minimum))
        Tg = ROOT.TGraph(1,
            array('f', [x_at_minimum, x_at_minimum]),
            array('f', [0.0, 3.0])
            )
        ROOT.SetOwnership(Tg, False)
        Tg.SetName(utils.get_unique_rootname())
        Tg.SetLineColor(self.color)
        Tg.SetLineWidth(1)
        return [(Tg, 'LSAME')]

    def repr_smooth_and_vertical_line(self, leg=None):
        return self.repr_smooth_line(leg) + self.repr_vertical_line_at_minimum()

    def Draw(self, draw_style):
        for obj, draw_str in getattr(self, draw_style)(self._legend):
            obj.Draw(draw_str)


class Point(object):
    """docstring for Point"""

    color_cycle = global_color_cycle

    def __init__(self, x, y, color=None, marker_style=21):
        super(Point, self).__init__()
        self.x = x
        self.y = y
        self._legend = None

        if color is None:
            self.color = self.color_cycle.next()
        else:
            self.color = color
        self.marker_style = marker_style # 21 for SM, 34 for bestfit

        self.Tg = ROOT.TGraph(1, array('f', [self.x]), array('f', [self.y]))
        ROOT.SetOwnership(self.Tg, False)
        self.Tg.SetName(utils.get_unique_rootname())

        self.Tg.SetMarkerSize(2)


    def __getattr__(self, name):
        return getattr(self.Tg, name)

    def set_x(self, x):
        self.x = x
        self.Tg.SetPoint(1, self.x, self.y)

    def set_y(self, y):
        self.y = y
        self.Tg.SetPoint(1, self.x, self.y)

    def SetMarkerStyle(self, marker_style):
        self.marker_style = marker_style

    def SetMarkerColor(self, color):
        self.color = color

    def repr_basic(self, leg=None):
        self.Tg.SetMarkerStyle(self.marker_style)
        self.Tg.SetMarkerColor(self.color)
        Tg_copy = self.Tg.Clone()
        ROOT.SetOwnership(Tg_copy, False)
        return [(Tg_copy, 'PSAME')]

    def repr_filled_diamond(self, leg=None):
        self.Tg.SetMarkerStyle(33)
        self.Tg.SetMarkerColor(self.color)
        Tg_copy = self.Tg.Clone()
        ROOT.SetOwnership(Tg_copy, False)
        return [(Tg_copy, 'PSAME')]

    def repr_SM_point(self, leg=None):
        self.Tg.SetMarkerStyle(21)
        self.Tg.SetMarkerColor(16)
        Tg_copy = self.Tg.Clone()
        ROOT.SetOwnership(Tg_copy, False)
        return [(Tg_copy, 'PSAME')]

    def repr_empty_diamond(self, leg=None):
        self.Tg.SetMarkerStyle(27)
        self.Tg.SetMarkerColor(1)
        Tg_copy = self.Tg.Clone()
        ROOT.SetOwnership(Tg_copy, False)
        return [(Tg_copy, 'PSAME')]

    def repr_diamond_with_border(self, leg=None):
        return self.repr_filled_diamond() + self.repr_empty_diamond()

    def Draw(self, draw_style='repr_basic'):
        for obj, draw_str in getattr(self, draw_style)(self._legend):
            obj.Draw(draw_str)
        


class Histogram2D(object):
    """docstring for Histogram2D"""

    color_cycle = global_color_cycle
    default_value = 999.

    def __init__(
            self,
            name, title,
            color=None
            ):
        super(Histogram2D, self).__init__()
        self.name = name
        self.title = title

        self.has_uncertainties = False
        if color is None:
            self.color = self.color_cycle.next()
        else:
            self.color = color

        self._legend = None
        self.H2 = None
        self.entries = []


    def infer_bin_boundaries(self, bin_centers):
        bin_boundaries = []
        for i_bin in xrange(len(bin_centers)-1):
            bin_boundaries.append( 0.5*(bin_centers[i_bin]+bin_centers[i_bin+1]) )
        bin_boundaries = (
            [ bin_centers[0] - (bin_boundaries[0]-bin_centers[0]) ] +
            bin_boundaries +
            [ bin_centers[-1] + (bin_centers[-1]-bin_boundaries[-1]) ]
            )
        return bin_boundaries


    def bestfit(self):
        return self.entries[self.deltaNLL().index(0.0)]

    def x(self):
        return [e.x for e in self.entries]
    def y(self):
        return [e.y for e in self.entries]
    def z(self):
        return [e.z for e in self.entries]
    def deltaNLL(self):
        return [e.deltaNLL for e in self.entries]
    def two_times_deltaNLL(self):
        return [2.*e.deltaNLL for e in self.entries]

    def x_min(self):
        return min(self.x())
    def x_max(self):
        return max(self.x())
    def y_min(self):
        return min(self.y())
    def y_max(self):
        return max(self.y())

    def fill_from_entries(self, entries):
        self.entries = entries
        bestfit = self.bestfit()

        self.x_bin_centers = [ x for x in list(set(self.x())) if not x == bestfit.x ]
        self.y_bin_centers = [ y for y in list(set(self.y())) if not y == bestfit.y ]
        self.x_bin_centers.sort()
        self.y_bin_centers.sort()

        self.n_bins_x = len(self.x_bin_centers)
        self.n_bins_y = len(self.y_bin_centers)
        self.x_bin_boundaries = self.infer_bin_boundaries(self.x_bin_centers)
        self.y_bin_boundaries = self.infer_bin_boundaries(self.y_bin_centers)

        logging.trace('Found the following x_bin_boundaries:\n{0}'.format(self.x_bin_boundaries))
        logging.trace('Found the following y_bin_boundaries:\n{0}'.format(self.y_bin_boundaries))

        self.H2 = ROOT.TH2D(
            utils.get_unique_rootname(), '',
            self.n_bins_x, array('d', self.x_bin_boundaries),
            self.n_bins_y, array('d', self.y_bin_boundaries),
            )
        ROOT.SetOwnership(self.H2, False)

        for i_x in xrange(self.n_bins_x):
            for i_y in xrange(self.n_bins_y):
                self.H2.SetBinContent(i_x+1, i_y+1, self.default_value)

        logging.debug('Filling {0} entries'.format(len(self.entries)))
        for entry in self.entries:
            if entry.x == bestfit.x and entry.y == bestfit.y: continue
            try:
                i_bin_x = self.x_bin_centers.index(entry.x)
            except ValueError:
                logging.error(
                    '{0} could not be filled - x={1} does not match any bin'
                    .format(entry, entry.x)
                    )
            try:
                i_bin_y = self.y_bin_centers.index(entry.y)
            except ValueError:
                logging.error(
                    '{0} could not be filled - y={1} does not match any bin'
                    .format(entry, entry.y)
                    )

            logging.trace(
                'Filling i_x={0} (x={1}) / i_y={2} (y={3}) with 2*deltaNLL={4}'
                .format(i_bin_x, entry.x, i_bin_y, entry.y, 2.*entry.deltaNLL)
                )

            self.H2.SetBinContent(i_bin_x+1, i_bin_y+1, 2.*entry.deltaNLL)


    def repr_2D(self, leg=None):
        utils.set_color_palette()
        self.H2.SetMaximum(7.0)
        return [(self.H2, 'COLZ')]

    def repr_bestfitpoint(self, leg=None):
        bestfit = self.bestfit()
        Tg = ROOT.TGraph(1, array('f', [bestfit.x]), array('f', [bestfit.y]))
        ROOT.SetOwnership(Tg, False)
        Tg.SetMarkerSize(2)
        Tg.SetMarkerStyle(34)
        Tg.SetMarkerColor(self.color)
        Tg.SetName(utils.get_unique_rootname())
        return [(Tg, 'PSAME')]

    def repr_1sigma_contours(self, leg=None):
        Tgs = utils.get_contours_from_H2(self.H2, 2.30)
        for Tg in Tgs:
            Tg.SetLineColor(self.color)
            Tg.SetLineWidth(2)
        if not(leg is None):
            Tg = Tgs[0]
            Tg.SetName(utils.get_unique_rootname())
            leg.AddEntry(Tg.GetName(), self.title, 'l')
        return [ (Tg, 'LSAME') for Tg in Tgs ]

    def repr_2sigma_contours(self, leg=None):
        Tgs = utils.get_contours_from_H2(self.H2, 6.18)
        for Tg in Tgs:
            Tg.SetLineColor(self.color)
            Tg.SetLineWidth(2)
            Tg.SetLineStyle(2)
        if not(leg is None):
            Tg = Tgs[0]
            Tg.SetName(utils.get_unique_rootname())
            leg.AddEntry(Tg.GetName(), self.title, 'l')
        return [ (Tg, 'LSAME') for Tg in Tgs ]

    def repr_contours(self, leg=None):
        return self.repr_bestfitpoint() + self.repr_1sigma_contours(leg) + self.repr_2sigma_contours()

    def repr_2D_with_contours(self, leg=None):
        return self.repr_2D() + self.repr_1sigma_contours() + self.repr_2sigma_contours() + self.repr_bestfitpoint()

    def repr_2D_with_contours_no_bestfit(self, leg=None):
        return self.repr_2D() + self.repr_1sigma_contours() + self.repr_2sigma_contours()

    def Draw(self, draw_style):
        for obj, draw_str in getattr(self, draw_style)(self._legend):
            obj.Draw(draw_str)


    def get_most_probable_1sigma_contour(self):
        allcontours = utils.get_contours_from_H2(self.H2, 2.30)
        candidatecontours = []

        bestfit = self.bestfit()

        for Tg in allcontours:
            Tg.x, Tg.y = utils.get_x_y_from_TGraph(Tg)
            Tg.x_min = min(Tg.x)
            Tg.x_max = max(Tg.x)
            Tg.y_min = min(Tg.y)
            Tg.y_max = max(Tg.y)

            # Check if bestfit is at least inside minima and maxima
            if not (
                    Tg.x_min < bestfit.x
                    and Tg.x_max > bestfit.x
                    and Tg.y_min < bestfit.y
                    and Tg.y_max > bestfit.y
                    ):
                continue

            # Compute some numbers that may help in selection: minimum distance to bestfit
            Tg.minDist = min([ ( Tg.x[i] - bestfit.x )**2 + ( Tg.y[i] - bestfit.y )**2 for i in xrange(Tg.GetN()) ])

            # Distance to bestfit should be close to half the difference between xMax-xMin (or yMax-yMin)
            # Compute ratio of this, minus 1 - result *should* be close to zero
            Tg.distRatio = Tg.minDist / ( 0.5 * min( Tg.y_max-Tg.y_min, Tg.x_max-Tg.x_min ) )  -  1.0
            # if abs(Tg.distRatio) > 0.8: continue

            candidatecontours.append( Tg )

        if len(candidatecontours) == 0:
            raise RuntimeError('Can\'t find contour')
        elif len(candidatecontours) > 1:
            candidatecontours.sort( key = lambda Tg: Tg.minDist )
            candidatecontours = candidatecontours[:2]

        # # Pick the contour with the highest ratio (more likely to be the 'outer shell')
        # candidatecontours.sort( key = lambda Tg: Tg.distRatio, reverse=True )

        # Actually, pick the 'inner' shell, outer shell is too likely to be a misfit
        candidatecontours.sort( key = lambda Tg: Tg.distRatio )    

        contour = candidatecontours[0]

        return contour
        