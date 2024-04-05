"""Plotting functions and class for the rims scheme drawer."""

import warnings

import matplotlib
import matplotlib.pyplot as plt
import numpy as np

from rimsschemedrawer.json_parser import ConfigParser
from rimsschemedrawer import utils as ut


class Plotter:
    def __init__(self, data: dict, **kwargs):
        """Initialize the plotting class.

        :param data: Dictionary with the data to plot, directly from json file.
        :param kwargs: Additional keyword arguments.
            - number_of_steps: How many scheme steps to consider, default is 7.
                This number can be higher than the number of available steps!
            - fig_ax: Tuple of matplotlib figure and axes to plot on. Defaults to
                creating new ones.
            - darkmode: Overwrite the darkmode settings from the config file.
            - transparent: Overwrite the transparency settings from the config file.
        """
        self.config_parser = ConfigParser(data)

        # check if old style
        if self.config_parser.element_guessed:
            warnings.warn(
                f"Old style input detected, where the IP is set manually. "
                f"The program guessed the element to be "
                f"{self.config_parser.element}. "
                f"Please update your input file."
            )

        # set kwargs
        self.number_of_steps = kwargs.get("number_of_steps", 7)

        # matplotlib parameters
        # tick size
        fsz_axes = self.config_parser.sett_fontsize[0]
        matplotlib.rc("xtick", labelsize=fsz_axes, direction="in")
        matplotlib.rc("ytick", labelsize=fsz_axes, direction="in")

        darkmode = kwargs.get("darkmode", self.config_parser.sett_plot_dark)
        self.transparent = kwargs.get(
            "transparent", self.config_parser.sett_plot_transparent
        )

        # figure stuff
        if darkmode:
            plt.style.use("dark_background")
        else:
            plt.style.use("default")

        self._figure, self._axes = kwargs.get("fig_ax", plt.subplots(1, 1))

        # Colors for arrows
        if darkmode:
            self.colmain = "#ffffff"
            self.colir = "#d27878"
            self.coluv = "#8c96df"
            self.colfuv = "#9365b2"
            self.colpump = "#60a55b"
            self.colhdr = "#4b5482"  # header color
        else:
            self.colmain = "#000000"
            self.colir = "#a00000"
            self.coluv = "#0012a0"
            self.colfuv = "#5f00a0"
            self.colpump = "#0aa000"
            self.colhdr = "#adbbff"  # header color

        # now plot the scheme
        self._plotit()

    @property
    def axes(self) -> plt.Axes:
        """Return the axes."""
        return self._axes

    @property
    def figure(self) -> plt.Figure:
        """Return the figure."""
        if self.transparent:
            self._figure.patch.set_alpha(0.0)
            self._figure.axes[0].patch.set_alpha(0.0)
        return self._figure

    def savefig(self, fout: str):
        """Save the figure to a file.

        :param fout: File name to save the plot to. The file extension determines
            the file type.
        """
        self._figure.savefig(fout)

    def _plotit(self):
        # textpad
        textpad = 0.4
        # percentage to increase for manifold
        mfld_yinc = 0.04  # in # of ipvalue
        firstarrowxmfl = 1.0

        # get formatting settings
        _, fsz_axes_labels, fsz_labels, fsz_title = self.config_parser.sett_fontsize
        sett_headspace = self.config_parser.sett_headspace
        sett_arr, sett_arr_head = self.config_parser.sett_arrow_fmt
        prec_lambda, prec_level = self.config_parser.sett_prec
        title_entry = self.config_parser.sett_title
        (
            show_cm_1_ax,
            show_ev_ax,
            show_forbidden_trans,
            show_trans_strength,
        ) = self.config_parser.sett_shows
        if self.config_parser.sett_line_breaks:
            lbreak = "\n"
        else:
            lbreak = ", "

        # ground state, IP, total wavenumber
        wavenumber_gs = self.config_parser.gs_level
        ipvalue = self.config_parser.ip_level
        totwavenumber_photons = self.config_parser.step_levels[-1]
        term_symb_ip = self.config_parser.ip_term
        term_symb_gs = self.config_parser.gs_term

        # get data for actual steps, low-lying excluded
        transition_strengths_steps = self.config_parser.transition_strengths[
            ~self.config_parser.is_low_lying
        ]

        transition_steps = self.config_parser.step_levels[
            ~self.config_parser.is_low_lying
        ]
        forbidden_steps = self.config_parser.step_forbidden[
            ~self.config_parser.is_low_lying
        ]
        lambda_steps = self.config_parser.step_nm[~self.config_parser.is_low_lying]
        wavenumber_steps = ut.nm_to_cm_2(lambda_steps)
        term_symb = self.config_parser.step_terms[~self.config_parser.is_low_lying]

        # get low-lying information
        wavenumber_es = self.config_parser.step_levels[self.config_parser.is_low_lying]
        lambda_step_es = self.config_parser.step_nm[self.config_parser.is_low_lying]
        transition_strengths_es = self.config_parser.transition_strengths[
            self.config_parser.is_low_lying
        ]
        forbidden_es = self.config_parser.step_forbidden[
            self.config_parser.is_low_lying
        ]
        term_symb_es_formatted = self.config_parser.step_terms[
            self.config_parser.is_low_lying
        ]

        # ymax:
        if ipvalue > totwavenumber_photons + wavenumber_gs:
            ymax = ipvalue + sett_headspace
        else:
            ymax = totwavenumber_photons + wavenumber_gs + sett_headspace

        # ### CREATE FIGURE ###
        a2 = self._axes.twinx()
        self._figure.set_size_inches(*self.config_parser.sett_fig_size, forward=True)

        # shade the level above the IP
        xshade = [0.0, 10.0]  # x-axis of the shade (which is never displayed)
        self._axes.fill_between(
            xshade, ipvalue, ymax * 10.0, facecolor=self.colhdr, alpha=0.5
        )

        # label the IP
        if self.config_parser.sett_ip_label_pos == "Top":
            iplabelypos = ipvalue + 0.01 * totwavenumber_photons
            iplabelyalign = "bottom"
        else:
            iplabelypos = ipvalue - 0.01 * totwavenumber_photons
            iplabelyalign = "top"
        iplabelstr = f"IP, {ipvalue:.{prec_level}f}$\\,$cm$^{{-1}}$"
        if term_symb_ip is not None:
            iplabelstr += f"{lbreak}{term_symb_ip}"
        # ip above or below
        self._axes.text(
            textpad,
            iplabelypos,
            iplabelstr,
            color=self.colmain,
            ha="left",
            va=iplabelyalign,
            size=fsz_labels,
        )

        # Draw the horizontal lines for every transition except last and for IP
        for it in transition_steps[:-1]:
            if it < ipvalue:
                self._axes.hlines(it, xmin=0, xmax=10, color=self.colmain)

        # draw the state we come out of, if not ground state
        if wavenumber_gs > 0.0:
            self._axes.hlines(wavenumber_gs, xmin=0, xmax=10, color=self.colmain)

        # draw the arrows and cross them out if forbidden
        deltax = 8.65 / (len(lambda_steps) + 1.0) - 0.5
        xval = 0.0
        yval_bott = wavenumber_gs
        # put in bottom level
        levelstr = f"{wavenumber_gs:.{prec_level}f}$\\,$cm$^{{-1}}$"
        if term_symb_gs is not None:
            levelstr += f"{lbreak}{term_symb_gs}"
        self._axes.text(
            10.0 - textpad,
            wavenumber_gs,
            levelstr,
            color=self.colmain,
            ha="right",
            va="bottom",
            size=fsz_labels,
        )

        # draw the arrows for the steps
        for it in range(len(lambda_steps)):
            if lambda_steps[it] >= 700:
                col = self.colir
            elif 500.0 < lambda_steps[it] < 700.0:
                col = self.colpump
            elif 350.0 < lambda_steps[it] <= 500.0:
                col = self.coluv
            else:
                col = self.colfuv
            # xvalue for arrow
            xval += deltax
            wstp = wavenumber_steps[it]
            tstp = transition_steps[it]
            # check if transition is forbidden and no show is activated for the arrow
            if not forbidden_steps[it] or show_forbidden_trans == "x-out":
                # look for where to plot the array
                if it == 0 and len(wavenumber_es) > 0:
                    xvalplot = firstarrowxmfl
                else:
                    xvalplot = xval
                # now plot the arrow
                self._axes.arrow(
                    xvalplot,
                    yval_bott,
                    0,
                    wstp,
                    width=sett_arr,
                    fc=col,
                    ec=col,
                    length_includes_head=True,
                    head_width=sett_arr_head,
                    head_length=totwavenumber_photons / 30.0,
                )

                # x-out forbidden arrow
                if forbidden_steps[it]:
                    yval_cross = yval_bott + wstp / 2.0
                    self._axes.plot(
                        xvalplot,
                        yval_cross,
                        "x",
                        color="r",
                        markersize=20,
                        markeredgewidth=5.0,
                    )

            # draw a little solid line for the last/end state
            if it == len(lambda_steps) - 1:
                self._axes.hlines(
                    tstp,
                    xmin=xval - 0.5,
                    xmax=xval + 0.5,
                    linestyle="solid",
                    color=self.colmain,
                )

            # alignment of labels
            if xval <= 5.0:
                halignlam = "left"
                halignlev = "right"
                xloc_levelstr = 10.0 - textpad
            else:
                halignlam = "right"
                halignlev = "left"
                xloc_levelstr = textpad

            if not forbidden_steps[it] or show_forbidden_trans == "x-out":
                # wavelength text and transition strength
                lambdastr = f"{lambda_steps[it]:.{prec_lambda}f}$\\,$nm"
                if (
                    show_trans_strength
                    and (tmp_strength := transition_strengths_steps[it]) != 0
                ):
                    lambdastr += (
                        f"\nA={ut.my_exp_formatter(tmp_strength, 1)}$\\,s^{{-1}}$"
                    )
                if it == 0 and len(wavenumber_es) > 0:
                    self._axes.text(
                        firstarrowxmfl + textpad,
                        tstp - wstp / 2.0,
                        lambdastr,
                        color=col,
                        ha=halignlam,
                        va="center",
                        ma="center",
                        rotation=90,
                        size=fsz_labels,
                    )
                else:
                    self._axes.text(
                        xval + textpad,
                        tstp - wstp / 2.0,
                        lambdastr,
                        color=col,
                        ha=halignlam,
                        va="center",
                        ma="center",
                        rotation=90,
                        size=fsz_labels,
                    )

            # level text
            levelstr = f"{tstp:.{prec_level}f}$\\,$cm$^{{-1}}$"
            if term_symb[it] is not None:
                levelstr += f"{lbreak}{term_symb[it]}"
            if it == len(lambda_steps) - 1:
                leveltextypos = tstp
                leveltextvaalign = "center"
            else:
                leveltextypos = tstp - 0.01 * totwavenumber_photons
                leveltextvaalign = "top"
            self._axes.text(
                xloc_levelstr,
                leveltextypos,
                levelstr,
                color=self.colmain,
                ha=halignlev,
                va=leveltextvaalign,
                size=fsz_labels,
            )

            # update yval_bott
            yval_bott = transition_steps[it]

        # now go through low-lying excited states
        x_spacing_es = (
            1.5
            if np.sum(transition_strengths_es) == 0 or not show_trans_strength
            else 2.0
        )

        # Lines for manifold ground states
        for it in range(np.sum(self.config_parser.is_low_lying)):
            self._axes.hlines(
                mfld_yinc * ipvalue * (1 + it),
                xmin=x_spacing_es * it + 2.3,
                xmax=x_spacing_es * it + 3.7,
                linestyle="solid",
                color=self.colmain,
            )

        for it in range(len(wavenumber_es)):
            if lambda_step_es[it] >= 700:
                col = self.colir
            elif 500.0 < lambda_step_es[it] < 700.0:
                col = self.colpump
            elif 350.0 < lambda_step_es[it] <= 500.0:
                col = self.coluv
            else:
                col = self.colfuv

            # values for spacing and distance
            xval = firstarrowxmfl + x_spacing_es + it * x_spacing_es
            yval = mfld_yinc * ipvalue * (1 + it)
            wstp = float(wavenumber_steps[0]) - yval

            if not forbidden_es[it] or show_forbidden_trans == "x-out":
                # xvalue for arrow
                self._axes.arrow(
                    xval,
                    yval,
                    0,
                    wstp,
                    width=sett_arr,
                    fc=col,
                    ec=col,
                    length_includes_head=True,
                    head_width=sett_arr_head,
                    head_length=totwavenumber_photons / 30.0,
                )

                # print cross out if necessary
                if forbidden_es[it]:
                    yval_cross = yval + wstp / 2.0
                    self._axes.plot(
                        xval,
                        yval_cross,
                        "x",
                        color="r",
                        markersize=20,
                        markeredgewidth=5.0,
                    )

                # wavelength text
                lambdastr = f"{lambda_step_es[it]:.{prec_lambda}f}$\\,$nm"
                if (
                    show_trans_strength
                    and (tmp_strength := transition_strengths_es[it]) != 0
                ):
                    lambdastr += (
                        f"\nA={ut.my_exp_formatter(tmp_strength, 1)}$\\,s^{{-1}}$"
                    )
                self._axes.text(
                    xval + textpad,
                    yval + wstp / 2.0,
                    lambdastr,
                    color=col,
                    ha="left",
                    va="center",
                    ma="center",
                    rotation=90,
                    size=fsz_labels,
                )

            # level text
            levelstr = f"{wavenumber_es[it]:.{prec_level}f}$\\,$cm$^{{-1}}$"
            if term_symb_es_formatted[it] is not None:
                # NO LINEBREAK HERE ON THESE LINES!
                levelstr += f", {term_symb_es_formatted[it]}"
            self._axes.text(
                xval + 0.5,
                yval,
                levelstr,
                color=self.colmain,
                ha="left",
                va="bottom",
                size=fsz_labels,
            )

        # Title:
        if title_entry != "":
            self._axes.set_title(title_entry, size=fsz_title)

        # ylabel
        self._axes.yaxis.set_major_formatter(ut.my_formatter)  # scientific labels
        if show_cm_1_ax:
            self._axes.set_ylabel("Wavenumber (cm$^{-1}$)", size=fsz_axes_labels)
        else:
            self._axes._axes.get_yaxis().set_ticks([])

        # axis limits
        self._axes.set_xlim([0.0, 10.0])
        self._axes.set_ylim([0.0, ymax])

        # eV axis on the right
        if show_ev_ax:
            a2.set_ylabel("Energy (eV)", size=fsz_axes_labels)
        else:
            a2._axes.get_yaxis().set_ticks([])
        a2.set_ylim([0.0, ymax / 8065.54429])

        # remove x ticks
        self._axes._axes.get_xaxis().set_ticks([])

        # tight layout of figure
        self._figure.tight_layout()
