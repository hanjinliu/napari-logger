from __future__ import annotations

from magicgui.widgets import CheckBox, Container

from napari_logger._magicgui_logger import Logger


class CheckBoxes(Container):
    def __init__(self):
        self.printing = CheckBox(
            text="Printing", tooltip="Print to logger widget"
        )
        self.html = CheckBox(text="HTML", tooltip="Print as HTML")
        self.logging = CheckBox(text="Logging", tooltip="Log to logger widget")
        self.plotting = CheckBox(
            text="Plotting", tooltip="Plot to logger widget"
        )

        kwargs = dict(labels=False, layout="horizontal")
        super().__init__(
            widgets=[
                Container(widgets=[self.printing, self.html], **kwargs),
                Container(widgets=[self.logging, self.plotting], **kwargs),
            ],
            labels=False,
        )
        self.margins = (0, 0, 0, 0)


class NapariLogger(Container):
    def __init__(self):
        self._logger = Logger()
        self._cboxes = CheckBoxes()
        self._cboxes.printing.changed.connect(self._toggle_print)
        self._cboxes.html.changed.connect(self._toggle_html)
        self._cboxes.logging.changed.connect(self._toggle_log)
        self._cboxes.plotting.changed.connect(self._toggle_plot)
        super().__init__(
            widgets=[self._cboxes, self._logger],
            labels=False,
        )
        self._printing_context = None
        self._logging_context = None
        self._plotting_context = None

    @property
    def logger(self):
        return self._logger

    @property
    def checkboxes(self):
        return self._cboxes

    def _toggle_print(self):
        if self._printing_context is None:
            self._printing_context = self._logger.set_stdout()
            self._printing_context.__enter__()
        else:
            self._printing_context.__exit__(None, None, None)
            self._printing_context = None

    def _toggle_html(self):
        self._logger.print_as_html = self._cboxes.html.value

    def _toggle_log(self):
        if self._logging_context is None:
            self._logging_context = self._logger.set_logger()
            self._logging_context.__enter__()
        else:
            self._logging_context.__exit__(None, None, None)
            self._logging_context = None

    def _toggle_plot(self):
        if self._plotting_context is None:
            self._plotting_context = self._logger.set_plt()
            self._plotting_context.__enter__()
        else:
            self._plotting_context.__exit__(None, None, None)
            self._plotting_context = None
