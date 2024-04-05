"""Test the json_parser module."""

import json

import pytest
import numpy as np

import rimsschemedrawer.json_parser as jp
import rimsschemedrawer.utils as ut


@pytest.mark.parametrize("fname", ["ti.json", "w_nm.json"])
def test_config_parser(data_path, fname):
    """Run through parser with all json files in the data folder."""
    fin = data_path.joinpath(fname)
    data = jp.json_reader(fin)

    parser = jp.ConfigParser(data)

    assert parser.lasers == "Ti:Sa"


@pytest.mark.parametrize(
    "fname",
    [
        ["ti_new.json", "ti_new_mixed_units.json"],
        ["raised_ground_low_lying_cm.json", "raised_ground_low_lying_nm.json"],
        ["w_cm-1.json", "w_nm.json"],
        ["raised_ground_cm.json", "raised_ground_nm.json"],
    ],
)
def test_config_parser_mixed_units(data_path, fname):
    """Check parser returns the same for cm-1 and nm.

    We are checking multiple cases:
    - low-lying states present at ground level 0
    - low-lying states present at elevated ground level
    - no low-lying states at ground level 0
    - no low-lying states at elevated ground level
    """
    fin = data_path.joinpath(fname[0])
    fin_mixed = data_path.joinpath(fname[1])
    data = jp.json_reader(fin)
    data_mixed = jp.json_reader(fin_mixed)

    parser = jp.ConfigParser(data)
    parser_mixed = jp.ConfigParser(data_mixed)

    assert not parser.sett_unit_nm
    assert parser_mixed.sett_unit_nm

    # make sure the steps are the same!
    np.testing.assert_almost_equal(
        parser_mixed._step_levels_cm, parser._step_levels_cm, decimal=1
    )


@pytest.mark.parametrize(
    "params",
    [
        [
            "raised_ground_low_lying_cm.json",
            np.array([469.498, 474.324, 469.274, 416.158, 881.399]),
        ],
        ["w_cm-1.json", np.array([384.858, 407.469, 771.908])],
        ["ti.json", np.array([469.498, 474.324, 465.777, 416.158, 881.399])],
    ],
)
def test_config_parser_nm(data_path, params):
    """Check parser returns the correct nm for the steps."""
    fname, nm_exp = params

    fin = data_path.joinpath(fname)
    data = jp.json_reader(fin)
    parser = jp.ConfigParser(data)

    np.testing.assert_almost_equal(parser._steps_nm, nm_exp, decimal=3)


def test_config_parser_fmt_terms(data_path):
    """Ensure formatted and unformatted term symbols are available."""
    fin = data_path.joinpath("ti.json")
    data = jp.json_reader(fin)
    parser = jp.ConfigParser(data)

    gs_term_fmt_exp = ut.term_to_string(parser.gs_term_no_formatting)
    ip_term_fmt_exp = ut.term_to_string(parser.ip_term_no_formatting)
    step_terms_fmt_exp = [
        ut.term_to_string(term) for term in parser.step_terms_no_formatting
    ]

    assert parser.gs_term == gs_term_fmt_exp
    assert parser.ip_term == ip_term_fmt_exp
    assert (parser.step_terms == step_terms_fmt_exp).all()


def test_json_reader(data_path):
    """Check that a valid json file is returned."""
    fin = data_path.joinpath("ti.json")
    data = jp.json_reader(fin)

    assert isinstance(data, dict)
    assert "scheme" in data.keys()
    assert "settings" in data.keys()


def test_json_reader_new(data_path, tmp_path):
    """Check correct output with new json format."""
    # todo: replace this construction with an actual new file
    fin = data_path.joinpath("ti.json")
    data = jp.json_reader(fin)
    data_new = {"rims_scheme": data}
    fin_new = tmp_path.joinpath("ti_new.json")
    with open(fin_new, "w") as f:
        json.dump(data_new, f)

    data_in = jp.json_reader(fin_new)
    assert isinstance(data_in, dict)
    assert "scheme" in data_in.keys()
    assert "settings" in data_in.keys()
