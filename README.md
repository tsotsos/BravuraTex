
# genSty

![GitHub release (latest by date including pre-releases)](https://img.shields.io/github/v/release/tsotsos/gensty?include_prereleases) ![PyPI - Status](https://img.shields.io/pypi/status/gensty) [![PyPI version](https://badge.fury.io/py/gensty.svg)](https://badge.fury.io/py/gensty) ![PyPI - Python Version](https://img.shields.io/pypi/pyversions/gensty) [![License](https://img.shields.io/github/license/tsotsos/gensty.svg)](https://github.com/tsotsos/gensty)

GenSty is a LaTex style package generator for OpenType fonts (otf/ttf) which
supports W3C SMuFL notation. With gensty you can generate your LaTeX package
based on any OpenType font; the generator parses ttf/otf files and creates LaTeX
commands for all Unicode Symbols. In the case of SMuFL fonts, you can also include
the glyphnames.json file, so it will create friendlier names and include
"Private Use" symbols.

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install foobar.

```bash
pip install gensty
```

## Installation (manual)

Clone the repository

```bash
git clone git@github.com:tsotsos/genSty.git
```

and then use via gensty/gensty folder. Eg.

```bash
python3 /the/path/of/gensty/gensty.py
```

## Usage

As referred above, the package can be used directly, installed from pip, and as
a module. In case of command line the script can be used :

```bash
usage: genSty [-h] [--version] [--all] [--smufl SMUFL]
                    [--description DESCRIPTION] [--author AUTHOR] [--ver VER]
                    path

LaTeX Style file generator for fonts

positional arguments:
  path                  Font(s) path. It can be either a directory in case of
                        multiple fonts or file path.

optional arguments:
  -h, --help            show this help message and exit
  --version, -v         show program's version number and exit
  --all, -a             If choosed genSty will generate LaTeX Styles for all
                        fonts in directory
  --smufl SMUFL, -s SMUFL
                        If choosed genSty will generate LaTeX Styles for all
                        fonts in directory based on glyphnames provided.
  --description DESCRIPTION
                        LaTeX Style package description. It is ignored in case
                        of --all flag.
  --author AUTHOR       Author's name.
  --ver VER             LaTeX package version.
```

### Use as a module

```python
import gensty

# create LaTeX packages for all fonts in directory 'folderPath'
# sumfPath is optional and should be glyphnames.json as refered to W3C
# Specifications here: https://www.w3.org/2019/03/smufl13/specification/glyphnames.html
# author, description, version are optional
fontfiles, result = gensty.handleFolder(folderPath, authorName, description,
                                        version, sumflPath)

# create LaTeX package for one font, otf/ttf must specified in `fontpath'
fontfiles, result = gensty.createStyleFile(fontpath, author, description,
                                            version, smufl)

# both functions return fontfiles list (stirng in 2nd case) and the content for
# sty file to passed in 'gensty.createPackage()'
#finally you can create the LaTeX package(s) via :
gensty.createPackage(fontfiles,result)

# that's it GenSty will create one folder for each font with sty and font files
# to be included directly in any LaTeX document.
```

## Contributing

Pull requests are welcome. For major changes, please open an issue first to
discuss what you would like to change.

## License

[GPLv2](LICENSE)
