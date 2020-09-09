#!/usr/bin/env python
"""gensty - Latex package generator ttf/otf and SMuFL."""
import os
import json
import sys
import shutil
import argparse
from datetime import datetime
from fontTools import ttLib
from fontTools.unicode import Unicode

__author__ = 'Georgios Tsotsos'
__email__ = 'tsotsos@gmail.com'
__version__ = '0.1.5'
__supported_fonts__ = ['ttf', 'otf']


def _latexFriendlyName(s):
    """Oneliner to return normalized name for LaTeX Style package."""
    return(" ".join(x.capitalize() for x in s.split(" ")).replace(" ", "").replace("-", ""))


def _isFontPath(path):
    """ Checks if the path is file or folder. In case of folder returns all
    included fonts."""
    if os.path.isfile(path):
        # TODO: verify file type.
        return True
    elif os.path.isdir(path):
        return False
    else:
        raise Exception("Error. Path must be a valid file or folder.")


def _findByExt(path, ext):
    """Finds file by extension. Returns list."""
    files = []
    if os.path.isfile(path) == True:
        if _checkExtension(path, ext) == True:
            files.append(path)
        else:
            return False
    else:
        for file in os.listdir(path):
            if file.endswith("."+ext):
                files.append(os.path.join(path, file))
    return files


def _createDir(dir):
    """Forces directory creation by removing any pre-existing folder with same
    name."""
    if os.path.exists(dir):
        shutil.rmtree(dir)
    os.makedirs(dir)


def _checkExtension(path, ext):
    """Defines if a file exists and its json."""
    if not os.path.isfile(path):
        return False
    if not path.endswith("."+ext):
        return False
    return True


def _writePackage(fontname, code):
    """Writes Style file."""
    sty = open(fontname+".sty", "w")
    sty.write(code)
    sty.close()


def _glyphnameParse(glyphnameFile):
    """Parses glyphname file according w3c/smufl reference."""
    result = []
    with open(glyphnameFile) as json_file:
        gnames = json.load(json_file)
        for gname in gnames:
            codepoint = gnames[gname]["codepoint"].split("+")[1]
            result.append((codepoint, gname))
    return result


def _ReplaceToken(dict_replace, target):
    """Based on dict, replaces key with the value on the target."""

    for check, replacer in list(dict_replace.items()):
        target = target.replace("["+check+"]", replacer)

    return target


def _getFontsByType(path):
    """Gets supported fonts by file extesion in a given folder."""
    files = []
    for ext in __supported_fonts__:
        fonts = _findByExt(path, ext)
        if not isinstance(fonts, list):
            continue
        for font in fonts:
            files.append(font)

    return files


def _fontName(fontfile):
    """Get the name from the font's names table.
    Customized function, original retrieved from: https://bit.ly/3lS4nMO
    """
    name = ""
    font = ttLib.TTFont(fontfile)
    for record in font['name'].names:
        if record.nameID == 4 and not name:
            if b'\000' in record.string:
                name = str(record.string, 'utf-16-be').encode('utf-8')
            else:
                name = record.string
                if name:
                    break
    font.close()
    # TODO: test for issues with multiple fonts
    name = name.decode('utf-8')
    return name.replace(" ", "").replace("-", "")

def _fontNameIdentifier(fontname, prefix=True):
    """Removes spaces and forces lowercase for font name, by default adds prefix
    'fnt' so we can avoid issues with simmilar names in other LaTeX packages."""
    result = fontname.lower().replace(" ", "")
    if prefix == True:
        return "fnt"+result
    return result


def _fontCodepoints(fontfile):
    """Creates a dict of codepoints and names for every character/symbol in the
    given font."""
    font = ttLib.TTFont(fontfile)
    charcodes = []
    for x in font["cmap"].tables:
        if not x.isUnicode():
            continue
        for y in x.cmap.items():
            charcodes.append(y)
    font.close()
    sorted(charcodes)
    return charcodes


def _fontCharList(charcodes, private=False, excluded=[]):
    """Accepts list of tuples with charcodes and codepoints and returns
    names and charcodes."""
    if not isinstance(charcodes, list):
        return False
    result = []
    for charcode, codepoint in charcodes:
        description = _latexFriendlyName(Unicode[charcode])
        curcodepoint = str(codepoint)
        if private == True and charcode >= 0xE000 and charcode <= 0xF8FF:
            continue
        if description in excluded:
            continue
        result.append((curcodepoint[1:], description))
    return result


def _latexDescription(fontname, version):
    """Creates default description text based on name and version."""
    currentDate = datetime.today().strftime('%Y-%m-%d')
    return "%s %s LaTeX package for %s" % (currentDate, version, fontname)


def _latexRequirements(requirements):
    """Creates LaTeX package requirements. By default fontspec is nessessary."""
    reqstr = "\\RequirePackage{fontspec}"
    if not isinstance(requirements, list):
        return reqstr
    for pkg in requirements:
        if pkg == "fontspec":
            continue
        reqstr += "\\RequirePackage{"+pkg+"}"
    return reqstr


def _latexCommands(fontname):
    """Creates command name, definition and command."""
    defCmd = "Define"+fontname
    return (defCmd, fontname)


def prepareStyle(fontfile, author, description, requirements=[]):
    """Prepares LaTeX package header, initialization commands and requirements."""
    genstyPath = os.path.abspath(os.path.dirname(__file__))
    fontname = _fontName(fontfile)
    fontfile = os.path.basename(fontfile)
    defcmd, cmd = _latexCommands(fontname)
    data = {
        'fontname': fontname+" Font",
        'packageName': _fontNameIdentifier(fontname, False),
        'year': datetime.today().strftime('%Y'),
        'author': author,
        'description': description,
        'fontfile': fontfile,
        'fontspath': "fonts",
        'fontfamily': _fontNameIdentifier(fontname),
        'fntidentifier': _fontNameIdentifier(fontname),
        'defcommand': defcmd,
        'command': cmd,
    }

    with open(genstyPath+"/template.sty") as templateFile:
        template = templateFile.read()
        output = _ReplaceToken(data, template)
    return output

def _optionalArguments(arguments):
    """Validates and ensure existance of optional arguments."""
    version = arguments.ver
    author = arguments.author

    if version == None:
        version = "v.0.1"
    if author == None:
        author = __author__

    return version, author


def _singleFontData(font, version):
    """Creates dict for single font to append into fonts dict on setupVariables
    hodling data for all fonts."""
        name = _fontName(font)
        defcmd, cmd = _latexCommands(name)
        return {
            'fontname': name,
            'fontnameN': _fontNameIdentifier(name),
            'fontpath': font,
            'fontbase': os.path.basename(font),
            'description': _latexDescription(name, version),
            'definition': defcmd,
            'command': cmd
        }

def setupVariables(arguments):
    """ Produces usable data for  font(s) and validates arguments. Used to
    create the final Style package."""

    # optional arguments.
    version, author = _optionalArguments(arguments)
    path = _isFontPath(arguments.path)
    fonts = _getFontsByType(arguments.path)

    if not isinstance(fonts, list):
        raise Exception("Error could not retrieve fonts")
    # font specific data.
    fontnames = {}
    for font in fonts:
        fontnames[_fontName(font)] = _singleFontData(font,version)

    if len(fontnames) == 0:
        raise Exception("Error cannot retrieve fonts")

    return {
        'isfile': path,
        'year': datetime.today().strftime('%Y'),
        'author': author,
        'fontnames': fontnames,
        'totalFonts': len(fonts),
    }


def retrieveCodes(filepath, smufl):
    """Retrieves the codepoints and symbols for the desired font, handles
    differently if its smufl font."""
    if smufl != None and _checkExtension(smufl, "json") == False:
        raise Exception("Error! Please provide a valid smufl json file")
    elif smufl != None and _checkExtension(smufl, "json") == True:
        #BUG: check what should return.
        print(_glyphnameParse(smufl))
        sys.exit()
        return _glyphnameParse(smufl)
    else:
        charcodes = _fontCodepoints(filepath)
        charcodes = _fontCharList(charcodes, excluded=["????"])
        if isinstance(charcodes, list):
            return charcodes
        else:
            raise Exception("Uknown font parse error")


def createLaTexCommands(charcodes, fontfile):
    """Generates LaTeX commands for each char code."""
    if not isinstance(charcodes, list):
        return False
    fontname = _fontName(fontfile)
    cmds = _latexCommands(fontname)
    commands = "\n"
    for codepoint, desc in charcodes:
        commands += "\\"+cmds[0]+"{"+desc+"}{\\char\""+codepoint+"\\relax}\n"
    if commands == "\n":
        raise Exception("Error. Cannot create LaTeX style commands")
    return commands


def createStyleFile(font, author, description, version, smufl):
    """ Creates LaTeX Style file."""
    charcodes = retrieveCodes(font, smufl)
    if description == None:
        description = _latexDescription(_fontName(font), version)
    header = prepareStyle(font, author, description)
    latexCommands = createLaTexCommands(charcodes, font)
    return font, (header + latexCommands)


def handleFolder(path, author, description, version, smufl):
    """Iterates through provided path and returns fontfiles and style files
    content."""
    fonts = _getFontsByType(path)
    result = []
    fontfiles = []
    for font in fonts:
        _, sty = createStyleFile(font, author, description, version, smufl)
        result.append(sty)
        fontfiles.append(font)
    return fontfiles, result


def singlePackage(fontfile, content):
    """Creates a single package folder and its files."""
    fontname = _fontName(fontfile)
    _createDir(fontname)
    packageFontsPath = fontname + "/fonts"
    _createDir(packageFontsPath)
    shutil.copy2(fontfile, packageFontsPath)
    _writePackage(fontname+"/"+fontname, content)


def createPackage(fontfiles, content):
    """Creates the final package with style and font files."""
    if isinstance(fontfiles, list) and isinstance(content, list):
        for font in fontfiles:
            for style in content:
                singlePackage(font, style)
    elif isinstance(fontfiles, str) and isinstance(content, str):
        singlePackage(fontfiles, content)
    else:
        raise Exception("Error, cannot save files.")


def main():
    parser = argparse.ArgumentParser(
        prog='genSty', description="LaTeX Style file generator for fonts")
    parser.add_argument('--version', '-v', action='version',
                        version='%(prog)s ' + __version__)
    parser.add_argument('path',
                        help='Font(s) path. It can be either a directory in case of multiple fonts or file path.')
    parser.add_argument('--all', '-a', action="store_true",
                        help='If choosed %(prog)s will generate LaTeX Styles for all fonts in directory')
    parser.add_argument('--smufl', '-s', type=str,
                        help='If choosed %(prog)s will generate LaTeX Styles for all fonts in directory based on glyphnames provided.')
    parser.add_argument('--name', '-n', type=str,
                        help='In case of single font provided forces specified name. Otherwise %(prog)s detects the name from file.')
    parser.add_argument('--description', type=str,
                        help='LaTeX Style package description. It is ignored in case of --all flag.')
    parser.add_argument('--author', type=str, help='Author\'s name.')
    parser.add_argument('--ver', type=str, help='LaTeX package version.')
    args = parser.parse_args()

    # Arguments preperation for use.
    arguments = setupVariables(args)
    import pprint
    pprint.pprint(arguments)
    sys.exit()
    # Handles different cases of command.
    # In case of "all" flag we create styles for every font in folder. For both
    # "all" true/false createPackage handles the package creation and
    # createStyleFile the LaTeX style content.
    if args.all == True and isdir(args.path) == False:
        raise Exception(
            "Error! flag --all must be defined along with directory only!")

    if args.all == True and isdir(args.path) == True:
        fontfiles, result = handleFolder(args.path, optionals["author"],
                                         optionals["description"], optionals["version"],
                                         args.smufl)
    if args.all == False and isfile(args.path) == True:
        fontfiles, result = createStyleFile(args.path, optionals["author"],
                                            optionals["description"], optionals["version"],
                                            args.smufl)
    # Create LaTeX package(s).
    # createPackage(fontfiles, result)
    print(result)


if __name__ == "__main__":
    main()
