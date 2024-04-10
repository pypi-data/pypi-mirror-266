# GALAssify

**A tool to manually classify galaxies**

<img src="instructions/GALAssify.png" alt="galassyfy_default" height="700px">

We also provide help tools to:
- Download images from SDSS.
- Create an instructions pdf.

The main tool can be customized with the `config` file. See [Customizing the tool](#customizing-the-tool) for more information.

<!-- 
<!-- toc -->
<!--
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
- [Customizing the tool](#customizing-the-tool)
  - [Tag groups](#tag-groups)
  - [Tag group elements](#tag-group-elements)
-->
<!-- /toc -->

## Requirements

GALAssify is written in Python. The following requirements are mandatory:

* Python `>=3.9`
* pandas
* pyqt5
* matplotlib
* Pillow
* astropy
* pyds9 (to open fits files directly form the tool)
* requests (used by the help tool to download sdss images)

Should work with `python >= 3.9`. Feel free to try for lower versions.

## Installation

### Creating a virtual environment
Using a virtual enviroment is recommended to execute this tool:

```bash
cd DIR_GALAssify
python -m venv .env
source .env/bin/activate
```
Now, you can choose installing `GALAssify` by using [PIP](#installing-from-pip) or by cloning this repository for [installing from source](#installing-from-source).

### Installing from PIP
Install and update using [pip](https://pip.pypa.io/en/stable/getting-started/):

- For install with [pyds9](https://github.com/ericmandel/pyds9) support:
```
$ pip install "galassify[ds9] @ git+https://gitlab.com/astrogal/GALAssify.git"
```

- For standard installation:
```
$ pip install git+https://gitlab.com/astrogal/GALAssify.git
```

### Installing from source

First, clone the repository:
```bash
git clone https://gitlab.com/astrogal/GALAssify.git
cd galassify
```
Then, install `GALAssify` with [pyds9](https://github.com/ericmandel/pyds9) support:
```bash
pip install .[ds9]
```
or without it:
```bash
pip install .
```

### Installation troubleshooting
The installation could fail with the next message if the package `libxt-dev` is not found in your OS:
```bash
xtloop.c:9:10: fatal error: X11/Intrinsic.h: No such file or directory
    9 | #include <X11/Intrinsic.h>
      |          ^~~~~~~~~~~~~~~~~
```
To solve that, you can install it with the following commands:

- openSUSE: `sudo zypper install libXt-devel`
- Debian / Ubuntu: `sudo apt-get install libxt-dev`
- Fedora: `sudo dnf install libXt-devel`

Then, try installing `GALAssify` again using you prefered method.

## Usage

To run the included example, execute the following command on the installation directory (with the activated enviroment):
```python
galassify -i files/galaxies.csv -s files/output.csv -p img/ 
```

For the main tool check:
```python
galassify --help
```

For helper tools check:
```python
get_images_sdss --help
```

## Input data

Minimum required columns:
- galaxy: identifier or name of the galaxy

Additional columns:
- group: identifier or name of the group/person to which the galaxy was assigned. Used to filter the galaxies when executing the tool.
- filename: name of the image file to be displayed in the tool. Relative to the image path specified on execution.
- fits: name of the fits file to be displayed in the tool. Relative to the image path specified on execution.

Example: `galaxies.csv`
```csv
group,galaxy,ra,dec,filename
1,15,210.927048,-1.137346,img_1_15_.jpeg
1,254,211.020782,0.998166,img_1_254.jpeg
...
```

## Customizing the tool

GALAssify tags can be customized to meet users needs. The default `config` file provides the configuration used to perform the galaxy sample selection in the [CAVITY](https://cavity.caha.es/) (Calar Alto Void Integral-field Treasury surveY) project.

### Tag groups

Tags are grouped depending on the needs, each of this groups correspond to one type. The available types are:

- radiobutton: group of elements were only one element can be selected
- checkbox: group of elements were each element can be checked independetly
- text: a textbox to add comments

### Tag group options

Each group type mentioned above has options that can (or must) be changed. 
Options marked as `optional` are not required but provide a better customization and user experience.

Common options for all group types:

- id: group identifier. Must be unique as it will be used on the output csv file.
- name (optional, default: id is used): Text to be used on the tool.
- type: Type to be used to initalize the group (one of the above).

Options that only apply for the `text` type group:
- shortcut (optional, default: None) :Key press to be used to focus on the comment-box. Must be unique, and not used in other groups/group-elements.
- save (unimplemented, [Enter] is used currently): Key press to be used to save the content, only used if focus is set on the group.
- discard (unimplemented, [Esc] is used currently): Key press to be used to discard the content, only used if focus is set on the group.

Options that only apply for the `radiobutton` type groups:
- add_clear (optional, default: false): Boolean indicating to add a clear button to the group. Not added by default.
- clear_shortcut (optional): Key press to be used to clear on the radiobutton group. Must be unique, and not used in other groups/group-elements.

Options that apply for the `radiobutton` and `checkbox` type groups:
- ncolumns (optional, default: 2): number of columns to be used to display the elements.
- elements: list on elements to be included.

### Tag element options

Each element has the following options:

- id: element identifier. Must be unique as it will be used on the output csv file.
- name (optional, default: id is used): Text to be used on the tool.
- shortcut (optional, default: None): Key press to be used to check on the element.
- description (optional, default: None): Short text to be displayed when the mouse is over the element.