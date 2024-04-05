# API Documentation

The `RIMSSchemeDrawer` can be run without a GUI.
Here you find some documentation on how to use the library itself.

## Installation

The package can be installed via `pip`:

```bash
pip install rimsschemedrawer
```

This will install the package without the GUI.
If you want the GUI components as well,
install the package as:

```bash
pip install rimsschemedrawer[gui]
```

## Create a figure

In order to create a figure,
you need to have an available dictionary that holds the information for a given scheme.
Let us first look at an example, where a configuration file is available.
You can find an example file
[here](https://github.com/RIMS-Code/RIMSSchemeDrawer/blob/main/examples/example_titanium.json).

The following code snippet will create a figure for you that you can save.

```python
from pathlib import Path

from rimsschemedrawer import Plotter, json_reader

# Load the configuration file
config_file = Path("path_to_your_config_file.json")
config = json_reader(config_file)

# Plot the figure
plotter = Plotter(config)
fig = plotter.figure  # returns a matplotlib figure

# Save the figure
outname = Path("path_to_your_output_file.pdf")
fig.savefig(outname)
```

Of course, you can also create your own config dictionary.
To do so, please have a look at the example file given above.
If you need further examples,
you can create them by using the GUI and then save the configuration.
