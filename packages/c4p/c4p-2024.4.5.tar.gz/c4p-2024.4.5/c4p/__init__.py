from .case import PaleoSetup
from .case import CESMCase
from .pp import Archive, PPCase
from .visual import set_style
from .rotation import Rotation

set_style(style='journal', font_scale=1.2)

# get the version
from importlib.metadata import version
__version__ = version('c4p')


# mute future warnings from pkgs like pandas
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)