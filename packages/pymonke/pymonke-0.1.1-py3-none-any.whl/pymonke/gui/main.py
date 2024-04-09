from matplotlib.axes import Axes

from .app import App
from pymonke.fit import FitResult, Fit


def run() -> tuple[dict[str, FitResult], Fit]:
    app = App()
    app.mainloop()
    return app.fit_result, app.fit

