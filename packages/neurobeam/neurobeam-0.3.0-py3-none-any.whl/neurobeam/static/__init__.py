from pathlib import Path
import os


"""
A collection of paths for included files (e.g., default configurations, test paths, font files, etc)
"""


#: Path: The base path of the package
BASE_PATH = Path.cwd()

#: Path: The path to these static files
STATIC_PATH = Path(os.path.realpath(__file__)).parents[0]

#: Path: The path to the neurobeam package
PACKAGE_PATH = STATIC_PATH.parents[0]

#: Path: The path to the neurobeam's default audio intensity look-up table
LUT_PATH = STATIC_PATH.joinpath("LUT.csv")

#: Path: The path to the tests directory
TEST_PATH = PACKAGE_PATH.parents[0].joinpath("tests")

#: Path: The path to the test configurations
TEST_CONFIG_PATH = TEST_PATH.joinpath("test_configs")

#: Path: The path to the gui font file
GUI_FONT_PATH = STATIC_PATH.joinpath("MyriadPro-Regular.tff")

#: Path: The path to neurobeam's large logo
LARGE_ICON_PATH = STATIC_PATH.joinpath("large_logo.ico")

#: Path: The path to neurobeam's small logo
SMALL_ICON_PATH = STATIC_PATH.joinpath("small_logo.ico")

#: Path: The path to the default viewer configuration
DEFAULT_GUI_SETTINGS = STATIC_PATH.joinpath("default_viewer_configuration.ini")

#: Path: The path to the default save path
DEFAULT_SAVE_PATH = BASE_PATH.joinpath("probe_experiments")
if not DEFAULT_SAVE_PATH.exists():  # pragma: no cover
    DEFAULT_SAVE_PATH.mkdir(parents=True)

#: Tuple: Supported Microscopes
SUPPORTED_MICROSCOPES = ("PrairieView", "Thorlabs")
