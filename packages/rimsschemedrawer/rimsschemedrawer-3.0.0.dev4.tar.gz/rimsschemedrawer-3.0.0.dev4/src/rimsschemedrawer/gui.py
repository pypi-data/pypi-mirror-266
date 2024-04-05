"""GUI Application for plotting RIMS schemes."""

import importlib.metadata
import json
from pathlib import Path

from matplotlib.backends.backend_qtagg import (
    FigureCanvasQTAgg,
    NavigationToolbar2QT as NavigationToolbar,
)
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

import rimsschemedrawer.json_parser

try:
    from qtpy import QtCore, QtGui, QtWidgets
except ImportError as e:
    raise ImportError(
        "ImportError: No GUI environment found. "
        "Please install this package with 'pip install rimsschemedrawer[gui]'"
    ) from e

from rimsschemedrawer.plotter import Plotter
import rimsschemedrawer.utils as ut


class SchemeDrawer(QtWidgets.QMainWindow):
    """RIMSSchemeDrawer."""

    def __init__(self):
        # run in debug mode?
        self.rundebug = False

        # program info
        self.author = "Reto Trappitsch"
        self.version = importlib.metadata.version("rimsschemedrawer")

        # user settings - maybe to be remembered at some point
        self.user_path = Path.home()

        # initialize the thing
        super().__init__()
        self.title = "RIMS Scheme Drawer"
        self.left = 50
        self.top = 80
        self.width = 20
        self.height = 20

        # initialize the UI
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        # settings:
        self.numberofsteps = 7
        self.lineedit_size = QtCore.QSize(100, 20)

        # entries and labels necessary
        self._element = None
        self.rbtngrp_units = QtWidgets.QButtonGroup()
        self.rbtn_nm = QtWidgets.QRadioButton("nm")
        self.rbtn_cm = QtWidgets.QRadioButton()
        self.lbl_steps = []
        self.edt_level = []
        self.edt_term = []
        self.edt_transition_strengths = []
        self.edt_gslevel = QtWidgets.QLineEdit()
        self.edt_gsterm = QtWidgets.QLineEdit()
        self.edt_iplevel = QtWidgets.QLineEdit()
        self.edt_ipterm = QtWidgets.QLineEdit()
        self.cmb_element = None
        self.cmb_lasers = None
        self.chk_lowlying = []
        self.chk_forbidden = []

        # settings line edits
        self.edt_sett_plttitle = QtWidgets.QLineEdit()
        self.edt_sett_figwidth = QtWidgets.QLineEdit()
        self.edt_sett_figheight = QtWidgets.QLineEdit()
        self.edt_sett_fstitle = QtWidgets.QLineEdit()
        self.edt_sett_fsaxes = QtWidgets.QLineEdit()
        self.edt_sett_fsaxlbl = QtWidgets.QLineEdit()
        self.chk_sett_trans_strength = QtWidgets.QCheckBox("Transition strengths?")
        self.chk_sett_linebreaks = QtWidgets.QCheckBox("Line breaks?")
        self.chk_sett_showcmax = QtWidgets.QCheckBox()  # no label -> label in layout
        self.chk_sett_showcmax.setChecked(True)
        self.chk_sett_showevax = QtWidgets.QCheckBox("Show eV axis labels?")
        self.chk_sett_showevax.setChecked(True)
        self.drop_plot_style = QtWidgets.QComboBox()
        self.drop_plot_style.addItems(ut.PLOT_STYLES)
        self.edt_sett_fslbl = QtWidgets.QLineEdit()
        self.edt_sett_headspace = QtWidgets.QLineEdit()
        self.edt_sett_arrwidth = QtWidgets.QLineEdit()
        self.edt_sett_arrheadwidth = QtWidgets.QLineEdit()
        self.edt_sett_preclambda = QtWidgets.QLineEdit()
        self.edt_sett_preclevel = QtWidgets.QLineEdit()
        self.rbtngrp_iplabel = QtWidgets.QButtonGroup()
        self.rbtn_iplable_top = QtWidgets.QRadioButton("Top")
        self.rbtn_iplable_bottom = QtWidgets.QRadioButton("Bott.")
        self.rbtngrp_sett_forbidden = QtWidgets.QButtonGroup()
        self.rbtn_sett_xoutarrow = QtWidgets.QRadioButton("x-out")
        self.rbtn_sett_nodisparrow = QtWidgets.QRadioButton("Don't show")

        # push buttons
        self.btn_plot = QtWidgets.QPushButton("Plot")
        self.btn_test = QtWidgets.QPushButton("Test")
        self.btn_load_conf = QtWidgets.QPushButton("Load Config")
        self.btn_save_conf = QtWidgets.QPushButton("Save Config")
        self.btn_reset_formatting = QtWidgets.QPushButton("Reset Formatting")
        self.btn_about = QtWidgets.QPushButton("About")
        self.btn_quit = QtWidgets.QPushButton("Quit")

        # main widget
        self.mainwidget = QtWidgets.QWidget()
        self.setCentralWidget(self.mainwidget)

        # style forms
        self.fontheader = QtGui.QFont()
        self.fontheader.setBold(True)

        # initialize the UI
        self.init_ui()

        # set default values
        self.fill_default_values()

        # show the UI
        self.show()

    def init_ui(self):
        """
        Initialize the UI
        """
        # bottom most row:
        bottomrowindex = 13  # depends on how many settings entries there are!
        if self.numberofsteps + 2 > bottomrowindex:
            bottomrowindex = self.numberofsteps + 2

        # define the grid layout
        layout = QtWidgets.QGridLayout()  # columns

        # ### column 1: labels for states
        # radiobuttons for nm or cm-1
        self.rbtngrp_units.addButton(self.rbtn_nm)
        self.rbtngrp_units.addButton(self.rbtn_cm)
        # set default
        self.rbtn_nm.setChecked(True)
        cmlabel = QtWidgets.QLabel("cm<sup>-1</sup>")
        self.rbtn_nm.setToolTip("Enter steps of laser scheme in nm")
        self.rbtn_cm.setToolTip("Enter steps of laser scheme in cm<sup>-1</sup>.")
        cmlabel.setToolTip("Enter steps of laser scheme in cm<sup>-1</sup>.")
        # add to layout
        rbtn_layout = QtWidgets.QHBoxLayout()
        rbtn_layout.addWidget(self.rbtn_nm)
        rbtn_layout.addStretch()
        rbtn_layout.addWidget(self.rbtn_cm)
        # this is a workaround, since the Radiobutton cannot accept a rich text label. It works
        rbtn_layout.addWidget(cmlabel)
        layout.addLayout(rbtn_layout, 0, 0, 1, 1)

        # headers for all
        # level
        lbl_level = QtWidgets.QLabel("Level")
        lbl_level.setFont(self.fontheader)
        layout.addWidget(lbl_level, 0, 1, 1, 1)
        # term symbol
        lbl_trmsymb = QtWidgets.QLabel("Term Symbol")
        lbl_trmsymb.setFont(self.fontheader)
        layout.addWidget(lbl_trmsymb, 0, 2, 1, 1)
        # transition strength
        lbl_trsstrength = QtWidgets.QLabel("Tr. strength (s<sup>-1</sup>)")
        lbl_trsstrength.setFont(self.fontheader)
        layout.addWidget(lbl_trsstrength, 0, 3, 1, 1)
        # ground state manifold?
        lbl_gsmani = QtWidgets.QLabel("GS Manifold?")
        lbl_gsmani.setFont(self.fontheader)
        layout.addWidget(lbl_gsmani, 0, 4, 1, 1)
        # Forbidden transition
        lbl_forbidden = QtWidgets.QLabel("Forbidden?")
        lbl_forbidden.setFont(self.fontheader)
        layout.addWidget(lbl_forbidden, 0, 5, 1, 1)
        # Settings
        lbl_sett = QtWidgets.QLabel("Settings")
        lbl_sett.setFont(self.fontheader)
        layout.addWidget(lbl_sett, 0, 6, 1, 1)

        # ground state
        lbl_gs = QtWidgets.QLabel("Ground state (cm<sup>-1</sup>)")
        layout.addWidget(lbl_gs, 1, 0, 1, 1)
        layout.addWidget(self.edt_gslevel, 1, 1, 1, 1)
        layout.addWidget(self.edt_gsterm, 1, 2, 1, 1)
        self.edt_gslevel.setToolTip("Set the ground state level in cm<sup>-1</sup>.")
        tt_termsymbol = (
            "For example, 2P3 for <sup>2</sup>P<sub>3</sub>. If only J-state is "
            "known, you "
            "can also enter something like 'J=3'."
        )
        self.edt_gsterm.setToolTip(
            "Set the term symbol for the ground state. " + tt_termsymbol
        )

        # individual steps
        for it in range(self.numberofsteps):
            # make label and append
            self.lbl_steps.append(QtWidgets.QLabel())
            layout.addWidget(self.lbl_steps[it], 2 + it, 0, 1, 1)
            # level steps
            self.edt_level.append(QtWidgets.QLineEdit())
            self.edt_level[it].setFixedSize(self.lineedit_size)
            self.edt_level[it].setValidator(QtGui.QDoubleValidator())
            self.edt_level[it].setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
            self.edt_level[it].setToolTip(
                "Enter the level of the given step in the selected unit."
            )
            layout.addWidget(self.edt_level[it], 2 + it, 1, 1, 1)

            # term symbol steps
            self.edt_term.append(QtWidgets.QLineEdit())
            self.edt_term[it].setFixedSize(self.lineedit_size)
            self.edt_term[it].setToolTip(
                "Enter term symbol for selected step. " + tt_termsymbol
            )
            layout.addWidget(self.edt_term[it], 2 + it, 2, 1, 1)

            # transition strength
            self.edt_transition_strengths.append(QtWidgets.QLineEdit())
            self.edt_transition_strengths[it].setFixedSize(self.lineedit_size)
            self.edt_transition_strengths[it].setValidator(QtGui.QDoubleValidator())
            self.edt_transition_strengths[it].setAlignment(
                QtCore.Qt.AlignmentFlag.AlignRight
            )
            self.edt_transition_strengths[it].setToolTip(
                "Enter transition strength for selected step in s<sup>-1</sup>."
            )
            layout.addWidget(self.edt_transition_strengths[it], 2 + it, 3, 1, 1)

            # check boxes
            self.chk_lowlying.append(QtWidgets.QCheckBox("Low-lying state?"))
            layout.addWidget(self.chk_lowlying[it], 2 + it, 4, 1, 1)
            self.chk_lowlying[it].toggled.connect(self.set_label_names)
            self.chk_lowlying[it].setToolTip("Check if this is a low-lying state?")
            # forbidden transition
            self.chk_forbidden.append(QtWidgets.QCheckBox())
            tmplayout = QtWidgets.QHBoxLayout()
            tmplayout.addStretch()
            tmplayout.addWidget(self.chk_forbidden[it])
            tmplayout.addStretch()
            layout.addLayout(tmplayout, 2 + it, 5, 1, 1)
            self.chk_forbidden[it].setToolTip(
                "Check this box to mark the\n" "transition as forbidden."
            )

        # name the labels
        self.set_label_names()

        # add IP label:
        ip_lbl = QtWidgets.QLabel("IP (cm<sup>-1</sup>)")
        layout.addWidget(ip_lbl, 2 + len(self.lbl_steps), 0, 1, 1)
        layout.addWidget(self.edt_iplevel, 2 + len(self.lbl_steps), 1, 1, 1)
        layout.addWidget(self.edt_ipterm, 2 + len(self.lbl_steps), 2, 1, 1)
        self.edt_iplevel.setToolTip(
            "IP level is automatically set by choosing an element below!"
        )
        self.edt_iplevel.setEnabled(False)
        self.edt_ipterm.setToolTip("Set term symbol of IP. " + tt_termsymbol)

        # Set the elements
        element_lbl = QtWidgets.QLabel("Element")
        layout.addWidget(element_lbl, 4 + len(self.lbl_steps), 0, 1, 1)
        cmb_element = QtWidgets.QComboBox()
        cmb_element.addItems(ut.get_elements())
        layout.addWidget(cmb_element, 4 + len(self.lbl_steps), 1, 1, 1)
        cmb_element.setToolTip("Select the element to set the IP.")
        cmb_element.currentIndexChanged.connect(lambda x: self.set_ip(x))
        cmb_element.setCurrentIndex(0)
        cmb_element.currentIndexChanged.emit(0)  # emit the signal even if not changed!
        self.cmb_element = cmb_element

        # Laser selection
        laser_lbls = QtWidgets.QLabel("Lasers")
        layout.addWidget(laser_lbls, 5 + len(self.lbl_steps), 0, 1, 1)
        cmb_lasers = QtWidgets.QComboBox()
        cmb_lasers.addItems(ut.LASERS)
        cmb_lasers.setToolTip(
            "Select the lasers used in this scheme. "
            "While this is not used for the plot, "
            "this entry is important for submitting your scheme "
            "to the RIMS database website "
            "and its entry will be saved to the configuration file."
        )
        layout.addWidget(cmb_lasers, 5 + len(self.lbl_steps), 1, 1, 1)
        self.cmb_lasers = cmb_lasers

        # set sizes and validators of boxes defined outside loop
        self.edt_gslevel.setFixedSize(self.lineedit_size)
        self.edt_gslevel.setValidator(QtGui.QDoubleValidator())
        self.edt_gslevel.setAlignment(QtCore.Qt.AlignRight)
        self.edt_gsterm.setFixedSize(self.lineedit_size)
        self.edt_iplevel.setFixedSize(self.lineedit_size)
        self.edt_iplevel.setValidator(QtGui.QDoubleValidator())
        self.edt_iplevel.setAlignment(QtCore.Qt.AlignRight)
        self.edt_ipterm.setFixedSize(self.lineedit_size)

        # button group for ip label
        self.rbtngrp_iplabel.addButton(self.rbtn_iplable_top)
        self.rbtngrp_iplabel.addButton(self.rbtn_iplable_bottom)

        # button group for how to display forbidden transitions
        self.rbtngrp_sett_forbidden.addButton(self.rbtn_sett_xoutarrow)
        self.rbtngrp_sett_forbidden.addButton(self.rbtn_sett_nodisparrow)

        # labels for settings
        layout.addWidget(QtWidgets.QLabel("Plot Title"), 1, 6, 1, 1)
        layout.addWidget(QtWidgets.QLabel("Figure Width x Height:"), 2, 6, 1, 1)
        layout.addWidget(QtWidgets.QLabel("Font size title:"), 3, 6, 1, 1)
        layout.addWidget(QtWidgets.QLabel("Font size axes:"), 4, 6, 1, 1)
        layout.addWidget(QtWidgets.QLabel("Font size axes label:"), 5, 6, 1, 1)
        layout.addWidget(QtWidgets.QLabel("Font size labels:"), 6, 6, 1, 1)
        layout.addWidget(QtWidgets.QLabel("Headspace (cm<sup>-1</sup>):"), 7, 6, 1, 1)
        layout.addWidget(QtWidgets.QLabel("Arrow width:"), 8, 6, 1, 1)
        layout.addWidget(QtWidgets.QLabel("Arrow head width:"), 9, 6, 1, 1)
        layout.addWidget(QtWidgets.QLabel("Precision wavelength:"), 10, 6, 1, 1)
        layout.addWidget(QtWidgets.QLabel("Precision level:"), 11, 6, 1, 1)
        layout.addWidget(QtWidgets.QLabel("IP label position:"), 12, 6, 1, 1)
        layout.addWidget(
            QtWidgets.QLabel("Display forbidden transitions:"), 13, 6, 1, 1
        )
        # line edits and buttons, include tooltips
        tmplayout = QtWidgets.QHBoxLayout()
        tmplayout.addWidget(self.edt_sett_figwidth)
        layout.addWidget(self.edt_sett_plttitle, 1, 7, 1, 1)
        self.edt_sett_plttitle.setToolTip("Title of the plot.")
        self.edt_sett_figwidth.setToolTip("Width of figure in inches.")
        tmplayout.addStretch()
        tmplayout.addWidget(QtWidgets.QLabel("x"))
        tmplayout.addStretch()
        tmplayout.addWidget(self.edt_sett_figheight)
        self.edt_sett_figheight.setToolTip("Height of figure in inches.")
        layout.addLayout(tmplayout, 2, 7, 1, 1)
        layout.addWidget(self.edt_sett_fstitle, 3, 7, 1, 1)
        self.edt_sett_fstitle.setToolTip("Font size of the plot title.")
        layout.addWidget(self.edt_sett_fsaxes, 4, 7, 1, 1)
        self.edt_sett_fsaxes.setToolTip("Font size of axes ticks.")
        layout.addWidget(self.edt_sett_fsaxlbl, 5, 7, 1, 1)
        self.edt_sett_fsaxlbl.setToolTip("Font size of axes labels.")
        # transition_strengths
        tmplayout = QtWidgets.QHBoxLayout()
        tmplayout.addWidget(self.chk_sett_trans_strength)
        tmplayout.addStretch()
        layout.addLayout(tmplayout, 1, 8, 1, 1)
        self.chk_sett_trans_strength.setToolTip("Display the transition strength?")
        # line breaks
        tmplayout = QtWidgets.QHBoxLayout()
        tmplayout.addWidget(self.chk_sett_linebreaks)
        tmplayout.addStretch()
        layout.addLayout(tmplayout, 2, 8, 1, 1)
        self.chk_sett_linebreaks.setToolTip(
            "Should there be a line break between\n"
            "the state and the term symbol? Play\n"
            "with this to make the the plot look nicer."
        )
        layout.addWidget(self.edt_sett_fslbl, 6, 7, 1, 1)
        # check box show cm-1 axis
        tmplayout = QtWidgets.QHBoxLayout()
        tmplayout.addWidget(self.chk_sett_showcmax)
        tmplayout.addStretch()
        tmplabel = QtWidgets.QLabel("Show cm-1 axis labels?")
        tmplayout.addWidget(tmplabel)
        layout.addLayout(tmplayout, 3, 8, 1, 1)
        self.chk_sett_showcmax.setToolTip(
            "Show the cm<sup>-1</sup> (left) axis? You can turn this off in case you "
            "want to stich plots together afterwards! This function will also hide the "
            "ticks."
        )
        tmplabel.setToolTip(
            "Show the cm<sup>-1</sup> (left) axis? You can turn this off in case you "
            "want to stich plots together afterwards! This function will also hide the "
            "ticks."
        )
        self.edt_sett_fslbl.setToolTip("Font size of the labels.")
        layout.addWidget(self.edt_sett_headspace, 7, 7, 1, 1)
        # check box show eV axis
        tmplayout = QtWidgets.QHBoxLayout()
        tmplayout.addWidget(self.chk_sett_showevax)
        tmplayout.addStretch()
        layout.addLayout(tmplayout, 4, 8, 1, 1)
        self.chk_sett_showevax.setToolTip(
            "Show the eV (right) axis? You can turn this\n"
            " off in case you want to stich plots together\n"
            "afterwards! This function will also hide the\n"
            "ticks."
        )
        self.edt_sett_headspace.setToolTip(
            "Set how much space is added on top of the "
            "highest transition: the head space. Adjust this "
            "value whenever there is not enough space "
            "on top to fit all the text in. The value "
            "is given in cm<sup>-1</sup>."
        )
        layout.addWidget(self.edt_sett_arrwidth, 8, 7, 1, 1)
        self.edt_sett_arrwidth.setToolTip(
            "Set the width of the arrow line in\n"
            "undefine dunits. Play to get the ideal\n"
            "settings."
        )
        layout.addWidget(self.edt_sett_arrheadwidth, 9, 7, 1, 1)
        self.edt_sett_arrheadwidth.setToolTip(
            "Set the width of the arrwo head in\n"
            "undefined units. Play to get the ideal\n"
            "settings."
        )
        layout.addWidget(self.edt_sett_preclambda, 10, 7, 1, 1)
        self.edt_sett_preclambda.setToolTip(
            "Set the precision with which the wavelength\n" "is displayed on the plot."
        )
        layout.addWidget(self.edt_sett_preclevel, 11, 7, 1, 1)
        self.edt_sett_preclevel.setToolTip(
            "Set the precision with which the wavenumber\n" "is displayed on the plot."
        )
        tmplayout = QtWidgets.QHBoxLayout()
        tmplayout.addWidget(self.rbtn_iplable_top)
        self.rbtn_iplable_top.setChecked(True)  # set top as default
        tmplayout.addStretch()
        tmplayout.addWidget(self.rbtn_iplable_bottom)
        self.rbtn_iplable_top.setToolTip("Display the IP label above the line.")
        self.rbtn_iplable_bottom.setToolTip("Display the IP label below the line.")
        layout.addLayout(tmplayout, 12, 7, 1, 1)
        tmplayout = QtWidgets.QHBoxLayout()
        tmplayout.addWidget(self.rbtn_sett_xoutarrow)
        self.rbtn_sett_xoutarrow.setChecked(True)  # set top as default
        tmplayout.addStretch()
        tmplayout.addWidget(self.rbtn_sett_nodisparrow)
        self.rbtn_sett_xoutarrow.setToolTip(
            "Show an arrow for forbidden transitions\n" "but cross it out."
        )
        self.rbtn_sett_nodisparrow.setToolTip(
            "Don't show arrows for forbidden\n" "transitions."
        )
        layout.addLayout(tmplayout, 13, 7, 1, 1)

        # plot dark mode?
        plot_style_lbl = QtWidgets.QLabel("Plot Style")
        layout.addWidget(plot_style_lbl, 5, 8, 1, 1)
        layout.addWidget(self.drop_plot_style, 6, 8, 1, 1)
        self.drop_plot_style.setToolTip(
            "Select the plot style\n"
            "- light: Light mode\n"
            "- dark: Dark mode\n"
            "- light transparent: Light mode with transparent background\n"
            "- dark transparent: Dark mode with transparent background"
        )

        # validators
        self.edt_sett_figwidth.setValidator(QtGui.QDoubleValidator())
        self.edt_sett_figheight.setValidator(QtGui.QDoubleValidator())
        self.edt_sett_fstitle.setValidator(QtGui.QIntValidator())
        self.edt_sett_fsaxes.setValidator(QtGui.QIntValidator())
        self.edt_sett_fsaxlbl.setValidator(QtGui.QIntValidator())
        self.edt_sett_fslbl.setValidator(QtGui.QIntValidator())
        self.edt_sett_headspace.setValidator(QtGui.QDoubleValidator())
        self.edt_sett_arrwidth.setValidator(QtGui.QDoubleValidator())
        self.edt_sett_arrheadwidth.setValidator(QtGui.QDoubleValidator())
        self.edt_sett_preclambda.setValidator(QtGui.QIntValidator())
        self.edt_sett_preclevel.setValidator(QtGui.QIntValidator())
        # alignment
        self.edt_sett_figwidth.setAlignment(QtCore.Qt.AlignCenter)
        self.edt_sett_figheight.setAlignment(QtCore.Qt.AlignCenter)
        self.edt_sett_fstitle.setAlignment(QtCore.Qt.AlignRight)
        self.edt_sett_fsaxes.setAlignment(QtCore.Qt.AlignRight)
        self.edt_sett_fsaxlbl.setAlignment(QtCore.Qt.AlignRight)
        self.edt_sett_fslbl.setAlignment(QtCore.Qt.AlignRight)
        self.edt_sett_headspace.setAlignment(QtCore.Qt.AlignRight)
        self.edt_sett_arrwidth.setAlignment(QtCore.Qt.AlignRight)
        self.edt_sett_arrheadwidth.setAlignment(QtCore.Qt.AlignRight)
        self.edt_sett_preclambda.setAlignment(QtCore.Qt.AlignRight)
        self.edt_sett_preclevel.setAlignment(QtCore.Qt.AlignRight)

        # push buttons
        layout.addWidget(self.btn_plot, 0, 8, 1, 1)
        if self.rundebug:
            layout.addWidget(self.btn_test, bottomrowindex, 3, 1, 1)
        layout.addWidget(self.btn_load_conf, bottomrowindex - 4, 8, 1, 1)
        layout.addWidget(self.btn_save_conf, bottomrowindex - 3, 8, 1, 1)
        layout.addWidget(self.btn_reset_formatting, bottomrowindex - 2, 8, 1, 1)
        layout.addWidget(self.btn_about, bottomrowindex - 1, 8, 1, 1)
        layout.addWidget(self.btn_quit, bottomrowindex, 8, 1, 1)

        # connect it all up
        self.rbtn_nm.toggled.connect(self.set_label_names)
        self.rbtn_cm.toggled.connect(self.set_label_names)
        # buttons
        self.btn_plot.clicked.connect(self.plot)
        self.btn_plot.setToolTip("Plot the scheme.")
        self.btn_load_conf.clicked.connect(self.load_config)
        self.btn_load_conf.setToolTip("Load a saved configuration file.")
        self.btn_save_conf.clicked.connect(self.save_config)
        self.btn_save_conf.setToolTip("Save the current configuration in a file.")
        self.btn_test.clicked.connect(self.test)
        self.btn_test.setToolTip(
            "This button should not be visible. If it is\n"
            "visible, it means that the\n"
            "self.rundebug\n"
            "value in the software is set to True. This\n"
            "is only meant for debugging and could have\n"
            "weird effects when using the software."
        )
        self.btn_reset_formatting.clicked.connect(
            lambda: self.fill_default_values(True)
        )
        self.btn_reset_formatting.setToolTip(
            "Reset the formatting variables to default values."
        )
        self.btn_about.clicked.connect(self.about)
        self.btn_about.setToolTip("Displays an about page with info on the program")
        self.btn_quit.clicked.connect(self.close)
        self.btn_quit.setToolTip("Close the program")

        # set the layout to the widget
        self.mainwidget.setLayout(layout)

    def fill_default_values(self, reset: bool = False):
        """
        Routine to fill default values in check boxes if they are empty.
        This is such that the user can't leave required fields empty.

        :param reset: If True, will overwrite fields that contain values.
        """

        def fillme(field, value):
            """
            Fills values of line edits, if currently empty
            """
            if reset or field.text() == "":
                field.setText(value)

        def set_radiobutton(btn: QtWidgets.QRadioButton, field: str, comp):
            """Set a radiobutton's state by comparing field with comp.

            The radiobutton's state is set to field==comp

            :param btn: Radiobutton
            :param field: The field in 'settings' to use to compare
            :param comp: Comparator.
            """
            btn.setChecked(ut.DEFAULT_SETTINGS["settings"][field] == comp)

        def set_checkbox(box: QtWidgets.QCheckBox, field: str):
            """Set a checkbox' state by field value.

            The checkbox' state is set to boolean value of field.

            :param box: Checkbox to set
            :param field: The field in 'settings' to use to compare
            :param comp: Comparator.
            """
            box.setChecked(ut.DEFAULT_SETTINGS["settings"][field])

        # loop through line edits
        fillme(
            self.edt_sett_figwidth, str(ut.DEFAULT_SETTINGS["settings"]["fig_width"])
        )
        fillme(
            self.edt_sett_figheight,
            str(ut.DEFAULT_SETTINGS["settings"]["fig_height"]),
        )
        fillme(self.edt_sett_fstitle, str(ut.DEFAULT_SETTINGS["settings"]["fs_title"]))
        fillme(self.edt_sett_fsaxes, str(ut.DEFAULT_SETTINGS["settings"]["fs_axes"]))
        fillme(self.edt_sett_fslbl, str(ut.DEFAULT_SETTINGS["settings"]["fs_labels"]))
        fillme(
            self.edt_sett_fsaxlbl,
            str(ut.DEFAULT_SETTINGS["settings"]["fs_axes_labels"]),
        )
        fillme(
            self.edt_sett_headspace,
            str(ut.DEFAULT_SETTINGS["settings"]["headspace"]),
        )
        fillme(
            self.edt_sett_arrwidth,
            str(ut.DEFAULT_SETTINGS["settings"]["arrow_width"]),
        )
        fillme(
            self.edt_sett_arrheadwidth,
            str(ut.DEFAULT_SETTINGS["settings"]["arrow_head_width"]),
        )
        fillme(
            self.edt_sett_preclambda,
            str(ut.DEFAULT_SETTINGS["settings"]["prec_wavelength"]),
        )
        fillme(
            self.edt_sett_preclevel,
            str(ut.DEFAULT_SETTINGS["settings"]["prec_level"]),
        )

        # radiobuttons and checkboxes only to be set on reset:
        if reset:
            # set radiobuttons
            set_radiobutton(self.rbtn_iplable_top, "ip_label_pos", "Top")
            set_radiobutton(self.rbtn_iplable_bottom, "ip_label_pos", "Bottom")
            set_radiobutton(
                self.rbtn_sett_xoutarrow, "show_forbidden_transitions", "x-out"
            )
            set_radiobutton(
                self.rbtn_sett_nodisparrow, "show_forbidden_transitions", "noshow"
            )

            # set checkboxes
            set_checkbox(self.chk_sett_trans_strength, "show_transition_strength")
            set_checkbox(self.chk_sett_linebreaks, "line_breaks")
            set_checkbox(self.chk_sett_showcmax, "show_cm-1_axis")
            set_checkbox(self.chk_sett_showevax, "show_eV_axis")

            # set plot style
            self.drop_plot_style.setCurrentText(
                ut.DEFAULT_SETTINGS["settings"]["plot_style"]
            )

    def set_label_names(self):
        # get the unit
        unit = self.get_unit()
        # set the labels
        stepnumb = 0
        for it in range(self.numberofsteps):
            stepnumb += 1
            # appendix for step number in label
            app = "th"
            if stepnumb == 1:
                app = "st"
            elif stepnumb == 2:
                app = "nd"
            elif stepnumb == 3:
                app = "rd"
            # set the namestring according to if low-lying is toggled or not
            if self.chk_lowlying[it].isChecked():
                stepnumb -= 1
                namestring = "Low lying st (cm<sup>-1</sup>)"
            else:
                namestring = str(stepnumb) + app + " step " + "(" + unit + "):"
            self.lbl_steps[it].setText(namestring)

    def get_unit(self):
        """
        Returns the current unit
        :return unit:   <str>   'nm' or 'cm<sup>-1</sup>'
        """
        if self.rbtn_nm.isChecked():
            return "nm"
        else:
            return "cm<sup>-1</sup>"

    def check_fields(self):
        """
        Check if the required fields are filled in.
        """
        # throw an error if not at least one box is filled
        if self.edt_level[0].text() == "" or self.edt_gslevel.text() == "":
            QtWidgets.QMessageBox.warning(
                self,
                "No entries",
                "Need at least ground state and one level to make a plot!",
                QtWidgets.QMessageBox.Ok,
            )
            return False

        # ip value
        try:
            _ = float(self.edt_iplevel.text())
        except ValueError:
            QtWidgets.QMessageBox.warning(
                self,
                "Enter IP",
                "Please enter an ionization potential as a number and try again.",
                QtWidgets.QMessageBox.Ok,
            )
            return False
        return True

    # buttons
    def plot(self):
        """
        Call the plotting window
        """
        if not self.check_fields():
            return

        # fill default values - if not already there
        self.fill_default_values()

        # open the plotting window
        data = self.write_json()

        darkmode = "dark" in self.drop_plot_style.currentText()
        transparent = "transparent" in self.drop_plot_style.currentText()
        PlotDisplay(data, parent=self, darkmode=darkmode, transparent=transparent)

    def load_config(self, **kwargs):
        """
        Load a configuration file that has previously been saved

        :param kwargs:  <dict>  Dictionary with additional keyword arguments
            - fname: <Path>  Path to the file to load
        """
        filename = kwargs.get("fname", None)

        if filename is None:
            options = QtWidgets.QFileDialog.Options()
            filename, _ = QtWidgets.QFileDialog.getOpenFileName(
                self,
                "QtWidgets.QFileDialog.getOpenFileName()",
                str(self.user_path.absolute()),
                filter="JSON Files (*.json);;All Files (*.*)",
                options=options,
            )
            # user pressed cancel
            if filename == "":
                return

            filename = Path(filename)

        self.user_path = filename.parent

        # load the json file
        _load_dict = rimsschemedrawer.json_parser.json_reader(filename)
        try:
            config_parser = rimsschemedrawer.json_parser.ConfigParser(_load_dict)
        except Exception as err:
            QtWidgets.QMessageBox.warning(
                self,
                "Error",
                f"An error occurred while reading the file.\n{'\n'.join(err.args)}",
                QtWidgets.QMessageBox.Ok,
            )
            return

        # set the settings for the levels
        if config_parser.sett_unit_nm:
            self.rbtn_nm.setChecked(True)
        else:
            self.rbtn_cm.setChecked(True)

        self.edt_gslevel.setText(str(config_parser.gs_level))
        self.edt_gsterm.setText(config_parser.gs_term_no_formatting)
        for it in range(
            len(self.edt_level)
        ):  # only loop through as many entries as there are
            try:
                if config_parser.sett_unit_nm:
                    value_list = config_parser.step_nm
                else:
                    value_list = config_parser.step_levels
                self.edt_level[it].setText(str(value_list[it]))
                self.edt_term[it].setText(config_parser.step_terms_no_formatting[it])

                trans_strength = config_parser.transition_strengths[it]
                if trans_strength > 0:
                    self.edt_transition_strengths[it].setText(str(trans_strength))
                self.chk_lowlying[it].setChecked(config_parser.is_low_lying[it])
                self.chk_forbidden[it].setChecked(config_parser.step_forbidden[it])
            except IndexError:
                self.edt_level[it].setText("")
                self.edt_term[it].setText("")
                self.edt_transition_strengths[it].setText("")
                self.chk_lowlying[it].setChecked(False)
                self.chk_forbidden[it].setChecked(False)

        # IP level
        self.cmb_element.setCurrentText(config_parser.element)
        if config_parser.element_guessed:
            QtWidgets.QMessageBox.information(
                self,
                f"Element set to {config_parser.element}",
                "You used an old-style configuration file. "
                "The software automatically guessed the element from the given "
                "ionization potential. "
                "Please check if this is correct and adjust if necessary.",
            )
        self.edt_ipterm.setText(config_parser.ip_term_no_formatting)

        # set the lasers used
        self.cmb_lasers.setCurrentText(config_parser.lasers)

        # settings
        arrow_width, arrow_head_width = config_parser.sett_arrow_fmt
        self.edt_sett_arrwidth.setText(str(arrow_width))
        self.edt_sett_arrheadwidth.setText(str(arrow_head_width))

        fig_width, fig_height = config_parser.sett_fig_size
        self.edt_sett_figwidth.setText(str(fig_width))
        self.edt_sett_figheight.setText(str(fig_height))

        fs_axticks, fs_axlabels, fs_labels, fs_title = config_parser.sett_fontsize
        self.edt_sett_fsaxes.setText(str(fs_axticks))
        self.edt_sett_fsaxlbl.setText(str(fs_axlabels))
        self.edt_sett_fslbl.setText(str(fs_labels))
        self.edt_sett_fstitle.setText(str(fs_title))

        self.edt_sett_headspace.setText(str(config_parser.sett_headspace))

        if config_parser.sett_ip_label_pos == "Top":
            self.rbtn_iplable_top.setChecked(True)
        else:
            self.rbtn_iplable_bottom.setChecked(True)

        (
            show_cm1_axis,
            show_ev_axis,
            show_forbidden_transitions,
            show_transition_strength,
        ) = config_parser.sett_shows
        if show_forbidden_transitions == "x-out":
            self.rbtn_sett_xoutarrow.setChecked(True)
        else:
            self.rbtn_sett_nodisparrow.setChecked(True)

        self.chk_sett_trans_strength.setChecked(show_transition_strength)
        self.chk_sett_showcmax.setChecked(show_cm1_axis)
        self.chk_sett_showevax.setChecked(show_ev_axis)
        self.chk_sett_linebreaks.setChecked(config_parser.sett_line_breaks)
        self.drop_plot_style.setCurrentText(config_parser.sett_plot_style)

        self.edt_sett_plttitle.setText(config_parser.sett_title)
        lambda_prec, level_prec = config_parser.sett_prec
        self.edt_sett_preclambda.setText(str(lambda_prec))
        self.edt_sett_preclevel.setText(str(level_prec))

    def write_json(self) -> dict:
        """Write the json dictionary to save or pass on.

        :return: JSON dictionary that can either be directly plotted or can be saved.
        """
        # create the dictionary to save
        savedict = {}
        savedict["scheme"] = {}
        savedict["settings"] = {}

        # save the levels
        savedict["scheme"]["unit"] = self.get_unit()
        savedict["scheme"]["gs_level"] = self.edt_gslevel.text()
        savedict["scheme"]["gs_term"] = self.edt_gsterm.text()
        for it in range(len(self.lbl_steps)):
            savedict["scheme"][f"step_level{it}"] = self.edt_level[it].text()
            savedict["scheme"][f"step_term{it}"] = self.edt_term[it].text()
            savedict["scheme"][f"trans_strength{it}"] = self.edt_transition_strengths[
                it
            ].text()
            savedict["scheme"][f"step_lowlying{it}"] = self.chk_lowlying[it].isChecked()
            savedict["scheme"][f"step_forbidden{it}"] = self.chk_forbidden[
                it
            ].isChecked()
        savedict["scheme"]["ip_term"] = self.edt_ipterm.text()
        savedict["scheme"]["element"] = self.cmb_element.currentText()
        savedict["scheme"]["lasers"] = self.cmb_lasers.currentText()

        # save the settings
        savedict["settings"]["fig_width"] = self.edt_sett_figwidth.text()
        savedict["settings"]["fig_height"] = self.edt_sett_figheight.text()
        savedict["settings"]["fs_title"] = self.edt_sett_fstitle.text()
        savedict["settings"]["fs_axes"] = self.edt_sett_fsaxes.text()
        savedict["settings"]["fs_axes_labels"] = self.edt_sett_fsaxlbl.text()
        savedict["settings"]["fs_labels"] = self.edt_sett_fslbl.text()
        savedict["settings"]["headspace"] = self.edt_sett_headspace.text()
        savedict["settings"]["arrow_width"] = self.edt_sett_arrwidth.text()
        savedict["settings"]["arrow_head_width"] = self.edt_sett_arrheadwidth.text()
        savedict["settings"]["prec_wavelength"] = self.edt_sett_preclambda.text()
        savedict["settings"]["prec_level"] = self.edt_sett_preclevel.text()
        if self.rbtn_iplable_top.isChecked():
            iptablepos = "Top"
        else:
            iptablepos = "Bottom"
        savedict["settings"]["ip_label_pos"] = iptablepos
        if self.rbtn_sett_xoutarrow.isChecked():
            dispforbidden = "x-out"
        else:
            dispforbidden = "noshow"
        savedict["settings"]["show_forbidden_transitions"] = dispforbidden
        savedict["settings"]["plot_title"] = self.edt_sett_plttitle.text()
        savedict["settings"]["show_transition_strength"] = (
            self.chk_sett_trans_strength.isChecked()
        )
        savedict["settings"]["line_breaks"] = self.chk_sett_linebreaks.isChecked()
        savedict["settings"]["show_cm-1_axis"] = self.chk_sett_showcmax.isChecked()
        savedict["settings"]["show_eV_axis"] = self.chk_sett_showevax.isChecked()
        savedict["settings"]["plot_style"] = self.drop_plot_style.currentText()

        return savedict

    def save_config(self):
        """
        Save the current configuration as a .json file the user defines
        """
        options = QtWidgets.QFileDialog.Options()
        filename, _ = QtWidgets.QFileDialog.getSaveFileName(
            self,
            "QtWidgets.QFileDialog.getOpenFileName()",
            str(self.user_path.absolute()),
            filter="JSON Files (*.json);;All Files (*.*)",
            options=options,
        )
        # user pressed cancel
        if filename == "":
            return

        filename = Path(filename)
        filename = filename.with_suffix(".json")

        self.user_path = filename.parent

        savedict = self.write_json()

        with open(filename, "w") as write_file:
            json.dump(savedict, write_file, indent=4, sort_keys=True)

    def about(self):
        """
        Gives a QtWidgets.QMessageBox with an about thing
        :return:
        """
        about_msg = (
            "<center>"
            "<h1>RIMS Scheme drawer</h1>"
            "<br>Version: "
            + self.version
            + "<p>Author: "
            + self.author
            + "<p>Please see the github repository for bug reports, feature requests, "
            "and for contacting the"
            "author."
            "<p>Many tooltips are implemented that can help you with the software. "
            "Hover over entries"
            "with the mouse and check those tooltips out."
        )
        QtWidgets.QMessageBox.about(self, "About", about_msg)

    def set_ip(self, index: int) -> None:
        """Set the element name (to be written to json) and the ionization potential.

        :param index: Index of element in list
        """
        element = ut.get_elements()[index]
        self.edt_iplevel.setText(str(ut.get_ip(element)))
        self._element = element

    def test(self):
        """
        Development testing routine, with the according button
        """
        fname = Path.home().joinpath(
            "Documents/code/RIMSCode/RIMSSchemeDrawer/examples/example_titanium.json"
        )
        self.load_config(fname=fname)
        self.user_path = Path(
            "/home/reto/Documents/code/RIMSCode/rims-code.github.io/temp/out"
        )


class MplCanvas(FigureCanvasQTAgg):
    def __init__(self, width=5, height=4, dpi=100):
        super().__init__()
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super().__init__(fig)


class PlotDisplay(QtWidgets.QMainWindow):
    def __init__(
        self,
        json_data: dict,
        parent: QtWidgets.QWidget = None,
        darkmode: bool = False,
        transparent: bool = False,
    ):
        """Prepare the plot display window.

        :param json_data: Data according to rimsschemedrawer json format.
        :param parent: Parent widget.
        :param darkmode: Use dark background for plot?
        :param transparent: Use transparent background for plot?
        """
        super().__init__(parent=parent)

        if darkmode:
            plt.style.use("dark_background")
        else:
            plt.style.use("default")
        sc = MplCanvas(width=5, height=4, dpi=100)
        Plotter(json_data, fig_ax=(sc.figure, sc.axes))
        if transparent:
            sc.figure.patch.set_alpha(0.0)
            sc.axes.patch.set_alpha(0.0)

        toolbar = NavigationToolbar(sc, self)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(toolbar)
        layout.addWidget(sc)

        widget = QtWidgets.QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)
        self.show()
