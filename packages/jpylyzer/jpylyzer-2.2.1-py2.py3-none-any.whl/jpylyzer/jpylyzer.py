#! /usr/bin/env python3
"""Jpylyzer validator for JPEG 2000 Part 1 (JP2) images.

Requires: Python 3.2 or more recent.

Copyright (C) 2011 - 2017 Johan van der Knijff, Koninklijke Bibliotheek -
  National Library of the Netherlands

Contributors:
   Rene van der Ark, NL (refactoring of original code).
   Lars Buitinck, NL.
   Adam Retter, The National Archives, UK.
   Jaishree Davey, The National Archives, UK.
   Laura Damian, The National Archives, UK.
   Carl Wilson, Open Preservation Foundation, UK.
   Stefan Weil, UB Mannheim, DE.
   Adam Fritzler, Planet Labs, USA.
   Thomas Ledoux, Bibliotheque Nationale de France
   Tim Lander, Hexagon Geospatial
"""
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import sys
import os
import time
import datetime
import glob
import argparse
import codecs
from xml.dom import minidom
from . import config
from . import etpatch as ET
from . import boxvalidator as bv
from . import mix
from . import shared
try:
    import mmap
    NO_MMAP_LIB = False
except ImportError:
    NO_MMAP_LIB = True

SCRIPT_PATH, SCRIPT_NAME = os.path.split(sys.argv[0])

# SCRIPT_NAME is empty when called from Java/Jython, so this needs a fix
if not SCRIPT_NAME:
    SCRIPT_NAME = 'jpylyzer'

__version__ = "2.2.1"

# Create PARSER
PARSER = argparse.ArgumentParser(
    description="JP2 image validator and properties extractor")

# list of existing files to be analysed
EXISTING_FILES = []

# Name space and schema strings
NS_STRING_2 = 'http://openpreservation.org/ns/jpylyzer/v2/'
XSI_NS_STRING = 'http://www.w3.org/2001/XMLSchema-instance'
LOC_SCHEMA_STRING_2 = 'http://openpreservation.org/ns/jpylyzer/v2/ \
http://jpylyzer.openpreservation.org/jpylyzer-v-2-2.xsd'


def generatePropertiesRemapTable():
    """Generate nested dictionary.

    Dictionary is used to map 'raw' property values (mostly integer values)
    to corresponding text descriptions.
    """
    # Master dictionary for mapping of text descriptions to enumerated values
    # Key: corresponds to parameter tag name
    # Value: sub-dictionary with mappings for all property values
    enumerationsMap = {}

    # Sub-dictionaries for individual properties

    # Generic 0 = no, 1=yes mapping (used for various properties)
    yesNoMap = {}
    yesNoMap[0] = "no"
    yesNoMap[1] = "yes"

    # Bits per component: sign (Image HeaderBox, Bits Per Component Box, SIZ header
    # in codestream)
    signMap = {}
    signMap[0] = "unsigned"
    signMap[1] = "signed"

    # Compression type (Image Header Box)
    cMap = {}
    cMap[7] = "jpeg2000"

    # meth (Colour Specification Box)
    methMap = {}
    methMap[1] = "Enumerated"
    methMap[2] = "Restricted ICC"
    methMap[3] = "Any ICC"  # JPH, JPX
    methMap[4] = "Vendor Colour"  # JPX
    methMap[5] = "Parameterized Colourspace"  # JPH

    # enumCS (Colour Specification Box)
    enumCSMap = {}
    enumCSMap[16] = "sRGB"
    enumCSMap[17] = "greyscale"
    enumCSMap[18] = "sYCC"

    # Profile Class (ICC)
    profileClassMap = {}
    profileClassMap[b'scnr'] = "Input Device Profile"
    profileClassMap[b'mntr'] = "Display Device Profile"
    profileClassMap[b'prtr'] = "Output Device Profile"
    profileClassMap[b'link'] = "DeviceLink Profile"
    profileClassMap[b'spac'] = "ColorSpace Conversion Profile"
    profileClassMap[b'abst'] = "Abstract Profile"
    profileClassMap[b'nmcl'] = "Named Colour Profile"

    # Primary Platform (ICC)
    primaryPlatformMap = {}
    primaryPlatformMap[b'APPL'] = "Apple Computer, Inc."
    primaryPlatformMap[b'MSFT'] = "Microsoft Corporation"
    primaryPlatformMap[b'SGI'] = "Silicon Graphics, Inc."
    primaryPlatformMap[b'SUNW'] = "Sun Microsystems, Inc."

    # Transparency (ICC)
    transparencyMap = {}
    transparencyMap[0] = "Reflective"
    transparencyMap[1] = "Transparent"

    # Glossiness (ICC)
    glossinessMap = {}
    glossinessMap[0] = "Glossy"
    glossinessMap[1] = "Matte"

    # Polarity (ICC)
    polarityMap = {}
    polarityMap[0] = "Positive"
    polarityMap[1] = "Negative"

    # Colour (ICC)
    colourMap = {}
    colourMap[0] = "Colour"
    colourMap[1] = "Black and white"

    # Rendering intent (ICC)
    renderingIntentMap = {}
    renderingIntentMap[0] = "Perceptual"
    renderingIntentMap[1] = "Media-Relative Colorimetric"
    renderingIntentMap[2] = "Saturation"
    renderingIntentMap[3] = "ICC-Absolute Colorimetric"

    # mTyp (Component Mapping box)
    mTypMap = {}
    mTypMap[0] = "direct use"
    mTypMap[1] = "palette mapping"

    # Channel type (Channel Definition Box)
    cTypMap = {}
    cTypMap[0] = "colour"
    cTypMap[1] = "opacity"
    cTypMap[2] = "premultiplied opacity"
    cTypMap[3] = "application-defined"
    cTypMap[65535] = "not specified"

    # Channel association (Channel Definition Box)
    cAssocMap = {}
    cAssocMap[0] = "all colours"
    cAssocMap[65535] = "no colours"

    # Precincts (Codestream, COD)
    precinctsMap = {}
    precinctsMap[0] = "default"
    precinctsMap[1] = "user defined"

    # Progression order (Codestream, COD)
    orderMap = {}
    orderMap[0] = "LRCP"
    orderMap[1] = "RLCP"
    orderMap[2] = "RPCL"
    orderMap[3] = "PCRL"
    orderMap[4] = "CPRL"

    # Transformation type (Codestream, COD)
    transformationMap = {}
    transformationMap[0] = "9-7 irreversible"
    transformationMap[1] = "5-3 reversible"

    # roiStyle parameter (Codestream, RGN)
    roiStyleMap = {}
    roiStyleMap[0] = "Implicit ROI (maximum shift)"

    # Quantization style (Codestream, QCD)
    qStyleMap = {}
    qStyleMap[0] = "no quantization"
    qStyleMap[1] = "scalar derived"
    qStyleMap[2] = "scalar expounded"

    # Registration value (Codestream, COM)
    registrationMap = {}
    registrationMap[0] = "binary"
    registrationMap[1] = "ISO/IEC 8859-15 (Latin)"

    # htCodeBlocks value (Codestream, CAP)
    htCodeBlocksMap = {}
    htCodeBlocksMap[0] = "HTONLY"
    htCodeBlocksMap[32768] = "HTDECLARED"
    htCodeBlocksMap[49152] = "MIXED"

    # htSets value (Codestream, CAP)
    htSetsMap = {}
    htSetsMap[0] = "SINGLEHT"
    htSetsMap[1] = "MULTIHT"

    # htRegion value (Codestream, CAP)
    htRegionMap = {}
    htRegionMap[0] = "RGNFREE"
    htRegionMap[1] = "RGN"

    # htHomogeneous value (Codestream, CAP)
    htHomogeneousMap = {}
    htHomogeneousMap[0] = "HOMOGENEOUS"
    htHomogeneousMap[1] = "HETEROGENEOUS"

    # htReversible value (Codestream, CAP)
    htReversibleMap = {}
    htReversibleMap[0] = "HTREV"
    htReversibleMap[1] = "HTIRV"

    # Add sub-dictionaries to master dictionary, using tag name as key
    enumerationsMap['unkC'] = yesNoMap
    enumerationsMap['iPR'] = yesNoMap
    enumerationsMap['profileClass'] = profileClassMap
    enumerationsMap['primaryPlatform'] = primaryPlatformMap
    enumerationsMap['embeddedProfile'] = yesNoMap
    enumerationsMap['vidFRng'] = yesNoMap
    enumerationsMap['profileCannotBeUsedIndependently'] = yesNoMap
    enumerationsMap['transparency'] = transparencyMap
    enumerationsMap['glossiness'] = glossinessMap
    enumerationsMap['polarity'] = polarityMap
    enumerationsMap['colour'] = colourMap
    enumerationsMap['renderingIntent'] = renderingIntentMap
    enumerationsMap['bSign'] = signMap
    enumerationsMap['mTyp'] = mTypMap
    enumerationsMap['precincts'] = precinctsMap
    enumerationsMap['sop'] = yesNoMap
    enumerationsMap['eph'] = yesNoMap
    enumerationsMap['multipleComponentTransformation'] = yesNoMap
    enumerationsMap['codingBypass'] = yesNoMap
    enumerationsMap['resetOnBoundaries'] = yesNoMap
    enumerationsMap['termOnEachPass'] = yesNoMap
    enumerationsMap['vertCausalContext'] = yesNoMap
    enumerationsMap['predTermination'] = yesNoMap
    enumerationsMap['segmentationSymbols'] = yesNoMap
    enumerationsMap['bPCSign'] = signMap
    enumerationsMap['ssizSign'] = signMap
    enumerationsMap['c'] = cMap
    enumerationsMap['meth'] = methMap
    enumerationsMap['enumCS'] = enumCSMap
    enumerationsMap['cTyp'] = cTypMap
    enumerationsMap['cAssoc'] = cAssocMap
    enumerationsMap['order'] = orderMap
    enumerationsMap['roiStyle'] = roiStyleMap
    enumerationsMap['transformation'] = transformationMap
    enumerationsMap['qStyle'] = qStyleMap
    enumerationsMap['rcom'] = registrationMap
    enumerationsMap['htCodeBlocks'] = htCodeBlocksMap
    enumerationsMap['htSets'] = htSetsMap
    enumerationsMap['htRegion'] = htRegionMap
    enumerationsMap['htHomogeneous'] = htHomogeneousMap
    enumerationsMap['htReversible'] = htReversibleMap
    return enumerationsMap


def fileToBytes(filename):
    """Read file, return contents as a byte object."""
    fileData = ""
    # Open file
    with open(filename, "rb") as f:
        fileData = f.read()

    return fileData


def fileToMemoryMap(filename):
    """Read contents of filename to memory map object."""
    # Call to mmap is different on Linux and Windows, so we need to know
    # the current platform
    platform = config.PLATFORM
    # List for storing any warnings
    mmWarnings = []

    # Open filename
    with open(filename, "rb") as f:
        try:
            if platform == "win32":
                # Parameters for Windows may need further fine-tuning ...
                fileData = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
            else:
                # This works for Linux (and Cygwin on Windows). Not too sure
                # about other platforms like Mac OS though
                fileData = mmap.mmap(
                    f.fileno(), 0, mmap.MAP_SHARED, mmap.PROT_READ)
        except ValueError as e:
            fileSize = os.path.getsize(filename)
            if fileSize > sys.maxsize:
                # Report warning if file size exceeds system maximum size
                # on 32-bit Python
                msg = ("file " + filename + " too large to open (" +
                       str(round(fileSize / 1024**3, 1)) +
                       " GB). Try using 64-bit Python.")
                mmWarnings.append(msg)
                shared.printWarning(msg)
                fileData = ""
            elif str(e) == "cannot mmap an empty file":
                # mmap fails on empty files, so return empty string
                msg = "empty file " + filename
                mmWarnings.append(msg)
                shared.printWarning(msg)
                fileData = ""

    return fileData, mmWarnings


def checkOneFile(path, validationFormat=config.VALIDATION_FORMAT,
                 verboseFlag=config.OUTPUT_VERBOSE_FLAG,
                 packetmarkersFlag=config.OUTPUT_PACKET_MARKERS_FLAG,
                 nullxmlFlag=config.EXTRACT_NULL_TERMINATED_XML_FLAG,
                 mixFlag=config.MIX_FLAG):
    """Process one file and return analysis result as element object."""
    # Element root name, name space and Schema location (legacy, current)
    elementRootName = 'file'

    # Create output elementtree object
    # Name space already declared in results element, so no need to do it
    # here
    root = ET.Element(elementRootName)

    # Create elements for file and status meta info
    fileInfo = ET.Element('fileInfo')
    statusInfo = ET.Element('statusInfo')

    # File name and path
    fileName = os.path.basename(path)
    filePath = os.path.abspath(path)

    # If file name / path contain any surrogate pairs, remove them to
    # avoid problems when writing to XML
    fileNameCleaned = stripSurrogatePairs(fileName)
    filePathCleaned = stripSurrogatePairs(filePath)

    # Produce some general tool and file meta info
    fileInfo.appendChildTagWithText("fileName", fileNameCleaned)
    fileInfo.appendChildTagWithText("filePath", filePathCleaned)
    fileInfo.appendChildTagWithText(
        "fileSizeInBytes", str(os.path.getsize(path)))
    try:
        dt = os.path.getmtime(path)
        lastModifiedDate = datetime.datetime.fromtimestamp(dt).isoformat()
    except ValueError:
        # Dates earlier than 1 Jan 1970 can raise ValueError on Windows
        # Workaround: replace by lowest possible value (typically 1 Jan 1970)
        dt = time.ctime(0)
        lastModifiedDate = datetime.datetime.fromtimestamp(dt).isoformat()
    fileInfo.appendChildTagWithText(
        "fileLastModified", lastModifiedDate)

    # Initialise success flag
    success = True
    # Initialise list with file to memorymap warnings
    fmmWarnings = []

    try:
        # Contents of file to memory map object
        if NO_MMAP_LIB:
            fileData = fileToBytes(path)
        else:
            fileData, fmmWarnings = fileToMemoryMap(path)

        # Set root box according to validation format
        if validationFormat in ['jp2', 'jph']:
            boxType = 'JP2'
        elif validationFormat in ['j2c', 'jhc']:
            boxType = 'contiguousCodestreamBox'

        # Create dictionary with BoxValidator options
        bvOptions = {}
        bvOptions['validationFormat'] = validationFormat
        bvOptions['verboseFlag'] = verboseFlag
        bvOptions['nullxmlFlag'] = nullxmlFlag
        bvOptions['packetmarkersFlag'] = packetmarkersFlag

        # Validate
        resultsJP2 = bv.BoxValidator(bvOptions, boxType, fileData).validate()

        fileIsValid = resultsJP2.isValid
        tests = resultsJP2.tests
        characteristics = resultsJP2.characteristics
        warnings = resultsJP2.warnings

        if not NO_MMAP_LIB and fileData != "":
            fileData.close()

        # Add any memory-mapping related warnings to warnings element
        for fmmWarning in fmmWarnings:
            warnings.appendChildTagWithText("warning", fmmWarning)

        # Generate property values remap table
        remapTable = generatePropertiesRemapTable()

        # Create printable version of tests, characteristics and warnings tree
        tests.makeHumanReadable()
        characteristics.makeHumanReadable(remapTable)
        warnings.makeHumanReadable()

    except Exception as ex:
        fileIsValid = False
        success = False
        exceptionType = type(ex)

        if exceptionType == MemoryError:
            failureMessage = "memory error (file size too large)"
        elif exceptionType == IOError:
            failureMessage = "I/O error (cannot open file)"
        elif exceptionType == RuntimeError:
            failureMessage = "runtime error, please report to developers by creating " + \
                             "an issue at https://github.com/openpreserve/jpylyzer/issues"
        else:
            failureMessage = "unknown error, please report to developers by creating " + \
                             "an issue at https://github.com/openpreserve/jpylyzer/issues"

        tests = ET.Element("tests")
        characteristics = ET.Element("properties")
        warnings = ET.Element("warnings")
        warnings.appendChildTagWithText("warning", failureMessage)
        shared.printWarning(failureMessage)

    if mixFlag != 0 and fileIsValid:
        mixProperties = mix.Mix(mixFlag).generateMix(characteristics)

    # Add status info
    statusInfo.appendChildTagWithText("success", str(success))
    if not success:
        statusInfo.appendChildTagWithText("failureMessage", failureMessage)

    # Append all results to root
    root.append(fileInfo)
    root.append(statusInfo)

    root.appendChildTagWithText("isValid", str(fileIsValid))
    # Set 'format' attribute of isValid element
    root.findall(".//isValid")[0].set("format", validationFormat)

    root.append(tests)
    root.append(characteristics)
    extension = ET.Element('propertiesExtension')
    if mixFlag != 0:
        root.append(extension)
        if validationFormat in ['jp2', 'jph'] and fileIsValid:
            extension.append(mixProperties)
    root.append(warnings)

    return root


def checkNullArgs(args):
    """Check if the passed args list.

    Exits program if invalid or no input argument is supplied.
    """
    if not args:
        print('')
        PARSER.print_help()
        sys.exit(config.ERR_CODE_NO_IMAGES)


def checkNoInput(files):
    """Check passed input files list.

    Results in any existing input files at all (and exits if not).
    """
    if not files:
        shared.printWarning("no images to check!")
        sys.exit(config.ERR_CODE_NO_IMAGES)


def printHelpAndExit():
    """Print help message and exit."""
    print('')
    PARSER.print_help()
    sys.exit()


def stripSurrogatePairs(ustring):
    """Remove surrogate pairs from a Unicode string."""
    # Source: http://stackoverflow.com/q/19649463/1209004

    try:
        ustring.encode('utf-8')
    except UnicodeEncodeError:
        # Strip away surrogate pairs
        tmp = ustring.encode('utf-8', 'replace')
        ustring = tmp.decode('utf-8', 'ignore')

    return ustring


def getFiles(searchpattern):
    """Append paths of all files that match search pattern to EXISTING_FILES."""
    results = glob.glob(searchpattern)
    for f in results:
        if os.path.isfile(f):
            EXISTING_FILES.append(f)


def getFilesWithPatternFromTree(rootDir, pattern):
    """Recurse into directory tree and return list of all files.

    NOTE: directory names are disabled here!!
    """
    for dirname, dirnames, _ in os.walk(rootDir):
        # Suppress directory names
        for subdirname in dirnames:
            thisDirectory = os.path.join(dirname, subdirname)
            # find files matching the pattern in current path
            searchpattern = os.path.join(thisDirectory, pattern)
            getFiles(searchpattern)


def getFilesFromTree(rootDir):
    """Recurse into directory tree and return list of all files.

    NOTE: directory names are disabled here!!
    """
    for dirname, dirnames, filenames in os.walk(rootDir):
        # Suppress directory names
        for subdirname in dirnames:
            # pylint: disable=W0612
            thisDirectory = os.path.join(dirname, subdirname)

        for filename in filenames:
            thisFile = os.path.join(dirname, filename)
            EXISTING_FILES.append(thisFile)


def findFiles(recurse, paths):
    """Find all files that match a wildcard expression and add their paths to EXISTING_FILES."""
    WILDCARD = "*"

    # process the list of input paths
    for root in paths:

        # WILDCARD IN PATH OR FILENAME
        # In Linux wildcard expansion done by bash so, add file to list
        if os.path.isfile(root):
            EXISTING_FILES.append(root)
        # Windows (& Linux with backslash prefix) does not expand wildcard '*'
        # Find files in the input path and add to list
        elif WILDCARD in root:
            # get the absolute path if not given
            if not os.path.isabs(root):
                root = os.path.abspath(root)

            # Expand wildcard in the input path. Returns a list of files,
            # folders
            filesList = glob.glob(root)

            # If the input path is a directory, then glob expands it to full
            # name
            if len(filesList) == 1 and os.path.isdir(filesList[0]):
                # set root to the expanded directory path
                root = filesList[0]

            # get files from directory

            # If the input path returned files list, add files to List

            if len(filesList) == 1 and os.path.isfile(filesList[0]):
                EXISTING_FILES.append(filesList[0])

            if len(filesList) > 1:
                for f in filesList:
                    if os.path.isfile(f):
                        EXISTING_FILES.append(f)

        elif not os.path.isdir(root) and not os.path.isfile(root):
            # One or more (but not all) paths do no exist - print a warning
            msg = root + " does not exist"
            shared.printWarning(msg)

        # RECURSION and WILDCARD IN RECURSION
        # Check if recurse in the input path
        if recurse:
            # get absolute input path if not given
            if not os.path.isabs(root):
                root = os.path.abspath(root)

            if WILDCARD in root:
                pathAndFilePattern = os.path.split(root)
                path = pathAndFilePattern[0]
                filePattern = pathAndFilePattern[1]
                filenameAndExtension = os.path.splitext(filePattern)
                # input path contains wildcard
                if WILDCARD in path:
                    filepath = glob.glob(path)
                    # if filepath is a folder, get files in current directory
                    if len(filepath) == 1:
                        getFilesWithPatternFromTree(filepath[0], filePattern)
                    # if filepath is a list of files/folder
                    # get all files in the tree matching the file pattern
                    if len(filepath) > 1:
                        for f in filepath:
                            if os.path.isdir(f):
                                getFilesWithPatternFromTree(f, filePattern)
                # file name or extension contains wildcard
                elif WILDCARD in filePattern:
                    getFilesWithPatternFromTree(path, filePattern)
                elif WILDCARD in filenameAndExtension:
                    filenameAndExtension = os.path.splitext(filePattern)
                    extension = WILDCARD + filenameAndExtension[1]
                    getFilesWithPatternFromTree(path, extension)
            # get files in the current folder and sub dirs w/o wildcard in path
            elif os.path.isdir(root):
                getFilesFromTree(root)


def writeElement(elt, codec):
    """Write element as XML to stdout using defined codec."""

    # Element to string
    xmlOut = ET.tostring(elt, 'unicode', 'xml')

    if not config.NO_PRETTY_XML_FLAG:
        # Make xml pretty
        xmlPretty = minidom.parseString(xmlOut).toprettyxml('    ')

        # Steps to get rid of xml declaration:
        # String to list
        xmlAsList = xmlPretty.split("\n")
        # Remove first item (xml declaration)
        del xmlAsList[0]
        # Convert back to string
        xmlOut = "\n".join(xmlAsList)

        # Write output
        codec.write(xmlOut)
    else:
        codec.write(xmlOut)


def checkFiles(recurse, paths):
    """Check the input argument path(s) for existing files and analyse them."""
    # Schema location
    locSchemaString = LOC_SCHEMA_STRING_2

    # Find existing files in the given input path(s)
    findFiles(recurse, paths)

    # If there are no valid input files then exit program
    checkNoInput(EXISTING_FILES)

    # Set encoding of the terminal to UTF-8
    out = codecs.getwriter(config.UTF8_ENCODING)(sys.stdout.buffer)

    # Wrap the xml output in <jpylyzer> element

    nsString = NS_STRING_2

    xmlHead = "<?xml version='1.0' encoding='UTF-8'?>\n"
    xmlHead += "<jpylyzer xmlns=\"" + nsString + "\" "
    xmlHead += "xmlns:xsi=\"" + XSI_NS_STRING + "\" "
    xmlHead += "xsi:schemaLocation=\"" + locSchemaString + "\">\n"

    out.write(xmlHead)

    # Create toolInfo element

    toolInfo = ET.Element('toolInfo')
    toolInfo.appendChildTagWithText("toolName", SCRIPT_NAME)
    toolInfo.appendChildTagWithText("toolVersion", __version__)
    # Write toolInfo to stdout
    writeElement(toolInfo, out)

    # Process the input files
    for path in EXISTING_FILES:

        # Analyse file
        xmlElement = checkOneFile(path,
                                  config.VALIDATION_FORMAT,
                                  config.OUTPUT_VERBOSE_FLAG,
                                  config.OUTPUT_PACKET_MARKERS_FLAG,
                                  config.EXTRACT_NULL_TERMINATED_XML_FLAG,
                                  config.MIX_FLAG)

        # Write output to stdout
        writeElement(xmlElement, out)

    # Close </results> element
    out.write("</jpylyzer>\n")


def parseCommandLine():
    """Parse command line arguments."""
    # Add arguments
    PARSER.add_argument('--format', '-f',
                        action="store",
                        type=str,
                        dest="fmt",
                        default="jp2",
                        help="validation format; allowed values: jp2, jph, j2c, jhc (default: jp2)")
    PARSER.add_argument('--mix',
                        type=int, choices=[1, 2],
                        dest="mixFlag",
                        default=0,
                        help="report additional output in NISO MIX format (version 1.0 or 2.0)")
    PARSER.add_argument('--nopretty',
                        action="store_true",
                        dest="noPrettyXMLFlag",
                        default=False,
                        help="suppress pretty-printing of XML output")
    PARSER.add_argument('--nullxml',
                        action="store_true",
                        dest="extractNullTerminatedXMLFlag",
                        default=False,
                        help="extract null-terminated XML content from XML and UUID boxes \
                                (doesn't affect validation)")
    PARSER.add_argument('--recurse', '-r',
                        action="store_true",
                        dest="inputRecursiveFlag",
                        default=False,
                        help="when analysing a directory, recurse into subdirectories")
    PARSER.add_argument('--packetmarkers', '-p',
                        action="store_true",
                        dest="reportPacketMarkersFlag",
                        default=False,
                        help="Report packet-level codestream markers (plm, ppm, plt, ppt)")
    PARSER.add_argument('--verbose',
                        action="store_true",
                        dest="outputVerboseFlag",
                        default=False,
                        help="report test results in verbose format")
    PARSER.add_argument('--version', '-v',
                        action='version',
                        version=__version__)
    PARSER.add_argument('jp2In',
                        action="store",
                        type=str,
                        nargs='+',
                        help="input JP2 image(s), may be one or more (whitespace-separated) path \
                                expressions; prefix wildcard (*) with backslash (\\) in Linux")

    # Parse arguments
    args = PARSER.parse_args()

    return args


def main():
    """Main command line application."""
    # Get input from command line
    args = parseCommandLine()

    # Input images
    jp2In = args.jp2In

    # Print help message and exit if jp2In is empty
    if not jp2In:
        printHelpAndExit()

    # Makes user-specified flags available to any module that imports 'config.py'
    # (here: 'boxvalidator.py')
    config.OUTPUT_VERBOSE_FLAG = args.outputVerboseFlag
    config.OUTPUT_PACKET_MARKERS_FLAG = args.reportPacketMarkersFlag
    config.EXTRACT_NULL_TERMINATED_XML_FLAG = args.extractNullTerminatedXMLFlag
    config.INPUT_RECURSIVE_FLAG = args.inputRecursiveFlag
    config.NO_PRETTY_XML_FLAG = args.noPrettyXMLFlag
    config.VALIDATION_FORMAT = args.fmt.lower()
    config.MIX_FLAG = args.mixFlag

    # Exit in case of unsupported Python version
    if config.PYTHON_VERSION.startswith("2"):
        msg = "Jpylyzer needs Python 3.x (Python 2.7 is no longer supported)"
        shared.errorExit(msg)
    # Exit if validation format is unknown
    if config.VALIDATION_FORMAT not in ['jp2', 'jph', 'j2c', 'jhc']:
        msg = "'" + config.VALIDATION_FORMAT + "'  is not a supported value for --format"
        shared.errorExit(msg)
    # Reset value of mixFlag to 0 if format is 'j2c' or 'jhc'
    if config.VALIDATION_FORMAT in ['j2c', 'jhc']:
        config.MIX_FLAG = 0

    # Check files
    checkFiles(config.INPUT_RECURSIVE_FLAG, jp2In)


if __name__ == "__main__":
    main()
