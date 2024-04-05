# Test utility functions for the project

from hypothesis import given, strategies as st
import pytest

from rimsschemedrawer import utils as ut


def test_cm_2_to_nm():
    """Check that the conversion from cm^-1 to nm is correct."""
    assert ut.cm_2_to_nm(1e7) == 1
    assert ut.cm_2_to_nm(5e6) == 2
    assert ut.cm_2_to_nm(3.3333333333333335e6) == 3


def test_get_elements():
    """Check that elements are in list."""
    eles = ut.get_elements()
    assert "H" in eles
    assert "He" in eles
    assert "U" in eles
    assert "Pu" in eles


def test_get_ip():
    """Check that the ionization potentials are correct."""
    assert ut.get_ip("H") == 109678.77174307
    assert ut.get_ip("hE") == 198310.66637
    assert ut.get_ip("LI") == 43487.1142
    assert ut.get_ip("be") == 75192.64
    assert ut.get_ip("B") == 66928.04
    assert ut.get_ip("C") == 90820.348
    assert ut.get_ip("N") == 117225.7


def test_guess_element_from_ip():
    """Guess an element from the IP."""
    assert ut.guess_element_from_ip(90820.0)
    assert ut.guess_element_from_ip(117224) == "N"


@pytest.mark.parametrize(
    "values",
    [
        [1.2345e6, 3, "$1.234 \\times 10^{6}$"],
        [0.001, 2, "$1.00 \\times 10^{-3}$"],
        [1, 1, "$1.0 \\times 10^{0}$"],
    ],
)
def test_my_exp_formatter(values):
    """Format exponential values as LaTeX strings."""
    value = values[0]
    prec = values[1]
    str_exp = values[2]

    str_ret = ut.my_exp_formatter(value, prec)

    assert str_ret == str_exp


@given(value=st.floats(min_value=0, allow_infinity=False))
def test_my_formatter(value):
    """Return properly formatted LaTeX code."""
    ret = ut.my_formatter(value)

    # LaTeX key elements
    assert ret[0] == "$"
    assert ret[-1] == "$"

    if value <= 1e-9:  # ensure scientific notation
        assert ret == "$0$"
    elif value >= 10:
        assert "^{" in ret
        assert ret[-2] == "}"


def test_nm_to_cm_2():
    """Check that the conversion from nm to cm^-1 is correct."""
    assert ut.nm_to_cm_2(1) == 1e7
    assert ut.nm_to_cm_2(2) == 5e6
    assert ut.nm_to_cm_2(3) == 3.3333333333333335e6


@pytest.mark.parametrize("vals", [["3F2", "$^{3}$F$_{2}$"], ["4G1", "$^{4}$G$_{1}$"]])
def test_term_to_string(vals):
    """Check that the term symbols are converted correctly."""
    assert ut.term_to_string(vals[0]) == vals[1]


def test_term_to_string_latex():
    """Return a string surrounded by $ if LaTeX characters found."""
    str_in = "^{3}F_{2}"
    str_exp = f"${str_in}$"
    assert ut.term_to_string(str_in) == str_exp


@pytest.mark.parametrize("val", ["IP", "AI", "Rydberg", "Ryd"])
def test_term_to_string_no_change(val):
    """Leave these symbols / strings unchanged."""
    assert ut.term_to_string(val) == val
