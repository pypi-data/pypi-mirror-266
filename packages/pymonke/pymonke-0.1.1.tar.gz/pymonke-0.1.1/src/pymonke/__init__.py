"""Documentation of pymonke module"""
from .fit.fit import Fit
from .fit.fit_result import FitResult
from .fit.parse import RepetitionError
from .latex.tex_table import TexTable
from .latex.utils import transform_dataframe_to_latex_ready
from .mmath.rounding import roundup
from .mmath.statistics import reduced_chi_square

from .gui.main import run as run_gui
