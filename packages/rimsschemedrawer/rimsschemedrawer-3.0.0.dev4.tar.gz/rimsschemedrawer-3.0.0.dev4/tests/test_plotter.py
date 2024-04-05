# Test the plotter
import pytest

import rimsschemedrawer.json_parser
from rimsschemedrawer.plotter import Plotter


@pytest.mark.parametrize("darkmode", [True, False])
@pytest.mark.parametrize("transparent", [True, False])
def test_plotter(data_path, tmp_path, darkmode, transparent):
    """Run through the plotter with a simple scheme, assert no errors."""
    fin = data_path.joinpath("ti.json")
    data = rimsschemedrawer.json_parser.json_reader(fin)

    fname = tmp_path.joinpath("test.pdf")
    fig = Plotter(data, darkmode=darkmode, transparent=transparent)
    fig.savefig(fname)

    assert fname.exists()


def test_plotter_old_style(data_path):
    """Raise warning when old style file is detected."""
    fin = data_path.joinpath("ti_old_style.json")
    data = rimsschemedrawer.json_parser.json_reader(fin)

    with pytest.warns(UserWarning, match="Ti"):
        _ = Plotter(data)
