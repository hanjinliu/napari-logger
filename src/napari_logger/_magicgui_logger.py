from __future__ import annotations

import logging
import sys
from contextlib import contextmanager
from pathlib import Path
from typing import TYPE_CHECKING, Any

from magicgui.backends._qtpy.widgets import QBaseWidget
from magicgui.widgets import Widget
from qtpy import QtGui
from qtpy.QtCore import Qt

from napari_logger._qt_logger import QtLogger
from napari_logger._utils import rst_to_html

if TYPE_CHECKING:
    import numpy as np
    from matplotlib.figure import Figure as mpl_Figure

# https://stackoverflow.com/questions/28655198/best-way-to-display-logs-in-pyqt

# Variable "FigureCanvas" should globally updated to plot figure inside the
# logger However, importing FigureCanvasAgg should be done lazily. Here's
# how to hack this procedure.


class FigureCanvasType:
    def __init__(self):
        self._canvas_type = None

    @property
    def FigureCanvasAgg(self):
        if self._canvas_type is None:
            from matplotlib.backends.backend_agg import FigureCanvasAgg

            self._canvas_type = FigureCanvasAgg
        return self._canvas_type

    def __getattr__(self, name):
        return getattr(self.FigureCanvasAgg, name)

    def __call__(self, *args: Any, **kwds: Any) -> Any:
        return self.FigureCanvasAgg(*args, **kwds)


FigureCanvas = FigureCanvasType()


class Logger(Widget, logging.Handler):
    """
    A widget for logging.

    Examples
    --------
    >>> logger = Logger(name="my logger")

    Print something in the widget

    >>> # print something in the widget.
    >>> logger.print("text")

    >>> # a context manager that change the destination of print function.
    >>> with logger.set_stdout():
    ...    print("text")
    ...    function_that_print_something()

    >>> # permanently change the destination of print function
    >>> sys.stdout = logger

    Logging in the widget

    >>> with logger.set_logger():
    >>>     function_that_log_something()

    >>> logging.getLogger(__name__).addHandler(logger)

    Inline plot in the widget

    >>> with logger.set_plt():
    >>>     plt.plot(np.random.random(100))

    """

    current_logger: Logger | None = None

    def __init__(self):
        logging.Handler.__init__(self)
        Widget.__init__(
            self, widget_type=QBaseWidget, backend_kwargs={"qwidg": QtLogger}
        )
        self.native: QtLogger
        self._stdout = False
        self._logging = False
        self._logger_name = None
        self._print_as_html = False

    def emit(self, record):
        """Handle the logging event."""
        msg = self.format(record)
        self.print(msg)
        return None

    def clear(self):
        """Clear all the histories."""
        self.native.clear()
        return None

    @property
    def value(self):
        return self.native.toPlainText()

    def print(self, *msg, sep=" ", end="\n"):
        """Print things in the end of the logger widget."""
        self.native.appendText(sep.join(map(str, msg)) + end)
        return None

    def print_html(self, html: str, end="<br></br>"):
        """Print things in the end of the logger widget using HTML string."""
        self.native.appendHtml(html + end)
        return None

    def print_rst(self, rst: str, end="\n"):
        """Print things in the end of the logger widget using rST string."""
        html = rst_to_html(rst, unescape=False)
        if end == "\n":
            end = "<br></br>"
        self.native.appendHtml(html + end)
        return None

    def print_table(
        self,
        table,
        header: bool = True,
        index: bool = True,
        precision: int | None = None,
    ):
        """
        Print object as a table in the logger widget.

        Parameters
        ----------
        table : table-like object
            Any object that can be passed to ``pandas.DataFrame`` can be used.
        header : bool, default is True
            Whether to show the header row.
        index : bool, default is True
            Whether to show the index column.
        precision: int, options
            If given, float value will be rounded by this parameter.
        """
        import pandas as pd

        df = pd.DataFrame(table)
        if precision is None:
            formatter = None
        else:
            formatter = lambda x: f"{x:.{precision}f}"  # noqa: E731
        self.native.appendHtml(
            df.to_html(header=header, index=index, float_format=formatter)
        )
        return None

    def print_image(
        self,
        arr: str | Path | np.ndarray,
        vmin=None,
        vmax=None,
        cmap=None,
        norm=None,
        width=None,
        height=None,
    ) -> None:
        """Print an array as an image in the logger widget. Can be a path."""
        try:
            from magicgui.widgets._image import _mpl_image
        except ImportError:  # pragma: no cover
            from magicgui import _mpl_image

        img = _mpl_image.Image()

        img.set_data(arr)
        img.set_clim(vmin, vmax)
        img.set_cmap(cmap)
        img.set_norm(norm)

        val: np.ndarray = img.make_image()
        h, w, _ = val.shape
        image = QtGui.QImage(val, w, h, QtGui.QImage.Format.Format_RGBA8888)

        # set scale of image
        if width is None and height is None:
            if w / 3 > h / 2:
                width = 360
            else:
                height = 240

        if width is None:
            image = image.scaledToHeight(
                height, Qt.TransformationMode.SmoothTransformation
            )
        else:
            image = image.scaledToWidth(
                width, Qt.TransformationMode.SmoothTransformation
            )

        self.native.appendImage(image)
        return None

    def print_figure(self, fig: mpl_Figure) -> None:
        """Print matplotlib Figure object like inline plot."""
        import numpy as np

        fig.canvas.draw()
        data = np.asarray(fig.canvas.renderer.buffer_rgba(), dtype=np.uint8)
        self.print_image(data)

        return None

    @property
    def print_as_html(self):
        return self._print_as_html

    @print_as_html.setter
    def print_as_html(self, val: bool):
        self._print_as_html = bool(val)

    def write(self, msg: str) -> None:
        """Handle the print event."""
        if self._print_as_html:
            self.print_html(msg)
        else:
            self.print(msg, end="")
        return None

    def flush(self):
        """Do nothing."""

    def close(self) -> None:
        # This method collides between magicgui.widgets.Widget and
        # logging.Handler. Since the close method in Widget is rarely
        # used, here just call the latter.
        return logging.Handler.close(self)

    @property
    def stdout(self):
        return self._stdout

    @stdout.setter
    def stdout(self, val: bool):
        if val:
            sys.stdout = self
        else:
            sys.stdout = sys.__stdout__
        self._stdout = val

    @contextmanager
    def set_stdout(self):
        """A context manager for printing things in this widget."""
        was_true = self.stdout
        self.stdout = True
        try:
            yield self
        finally:
            self.stdout = was_true

    @property
    def logging(self):
        return self._logging

    @logging.setter
    def logging(self, val: bool):
        if val:
            logging.getLogger(self._logger_name).addHandler(self)
        else:
            logging.getLogger(self._logger_name).removeHandler(self)
        self._logging = val

    @contextmanager
    def set_logger(self, name=None):
        """A context manager for logging things in this widget."""
        self.logging = True
        try:
            yield self
        finally:
            self.logging = False

    @contextmanager
    def set_plt(self, style: str = None, rc_context: dict[str, Any] = {}):
        """A context manager for inline plot in the logger widget."""
        try:
            import matplotlib as mpl
            import matplotlib.pyplot as plt
        except ImportError:
            yield self
            return None
        self.__class__.current_logger = self

        if isinstance(style, dict):
            if rc_context:
                raise TypeError("style must be str.")
            rc_context = style
            style = None

        if style is None:
            style = self._get_proper_plt_style()

        backend = mpl.get_backend()
        show._called = False
        orig_rcparams = plt.rcParams.copy()
        try:
            mpl.use(f"module://{self.__module__}")
            plt.style.use(style)
            plt.rcParams.update(rc_context)
            yield self
        finally:
            if not show._called:
                show()
            self.__class__.current_logger = None
            dict.update(plt.rcParams, orig_rcparams)
            mpl.use(backend)
        return None

    def _get_proper_plt_style(self) -> dict[str, Any]:
        import matplotlib.pyplot as plt

        color = self.native._get_background_color()[:3]
        is_dark = sum(color) < 382.5  # 255*3/2
        if is_dark:
            params = plt.style.library["dark_background"]
        else:
            keys = plt.style.library["dark_background"].keys()
            with plt.style.context("default"):
                params: dict[str, Any] = {}
                rcparams = plt.rcParams
                for key in keys:
                    params[key] = rcparams[key]
        bg = _tuple_to_color(color)
        params["figure.facecolor"] = bg
        params["axes.facecolor"] = bg
        return params


# The plt.show function will be overwriten to this.
# Modified from matplotlib_inline (BSD 3-Clause "New" or "Revised" License)
# https://github.com/ipython/matplotlib-inline
def show(close=True, block=None):
    logger = Logger.current_logger
    import matplotlib.pyplot as plt
    from matplotlib._pylab_helpers import Gcf

    try:
        for figure_manager in Gcf.get_all_fig_managers():
            logger.print_figure(figure_manager)
    finally:
        show._called = True
        if close and Gcf.get_all_fig_managers():
            plt.close("all")


def _tuple_to_color(tup: tuple[int, int, int]):
    return "#" + "".join(hex(int(t))[2:] for t in tup)
