from __future__ import annotations

from contextlib import suppress
from pathlib import Path
from typing import Union

from qtpy import QtCore, QtGui
from qtpy import QtWidgets as QtW
from qtpy.QtCore import Qt, Signal


class Output:
    """Logger output types."""

    TEXT = 0
    HTML = 1
    IMAGE = 2


Printable = Union[str, QtGui.QImage]


class QtLogger(QtW.QTextEdit):
    process = Signal(tuple)

    def __init__(self, parent=None, max_history: int = 500):
        super().__init__(parent=parent)
        self.setReadOnly(True)
        self.setWordWrapMode(QtGui.QTextOption.WrapMode.NoWrap)
        self._max_history = int(max_history)
        self._n_lines = 0
        self.process.connect(self.update)

        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)

        @self.customContextMenuRequested.connect
        def rightClickContextMenu(point):
            menu = self._make_contextmenu(point)
            if menu:
                menu.exec_(self.mapToGlobal(point))

        self._last_save_path = None

    def update(self, output: tuple[int, Printable]):
        with suppress(RuntimeError):
            output_type, obj = output
            if output_type == Output.TEXT:
                self.moveCursor(QtGui.QTextCursor.MoveOperation.End)
                self.insertPlainText(obj)
                self.moveCursor(QtGui.QTextCursor.MoveOperation.End)
            elif output_type == Output.HTML:
                self.moveCursor(QtGui.QTextCursor.MoveOperation.End)
                self.insertHtml(obj)
                self.moveCursor(QtGui.QTextCursor.MoveOperation.End)
            elif output_type == Output.IMAGE:
                cursor = self.textCursor()
                cursor.insertImage(obj)
                self.insertPlainText("\n\n")
                self.verticalScrollBar().setValue(
                    self.verticalScrollBar().maximum()
                )
            else:
                raise TypeError("Wrong type.")
            self._post_append()
        return None

    def appendText(self, text: str):
        """Append text in the main thread."""
        self.process.emit((Output.TEXT, text))

    def appendHtml(self, html: str):
        """Append HTML in the main thread."""
        self.process.emit((Output.HTML, html))

    def appendImage(self, qimage: QtGui.QImage):
        """Append image in the main thread."""
        self.process.emit((Output.IMAGE, qimage))

    def _post_append(self):
        """Check the history length."""
        if self._n_lines < self._max_history:
            self._n_lines += 1
            return None
        cursor = self.textCursor()
        cursor.movePosition(QtGui.QTextCursor.MoveOperation.Start)
        cursor.select(QtGui.QTextCursor.SelectionType.LineUnderCursor)
        cursor.removeSelectedText()
        cursor.movePosition(QtGui.QTextCursor.MoveOperation.Down)
        cursor.deletePreviousChar()
        cursor.movePosition(QtGui.QTextCursor.MoveOperation.End)
        self.setTextCursor(cursor)
        return None

    def _get_background_color(self) -> tuple[int, int, int, int]:
        return self.palette().color(self.backgroundRole()).getRgb()

    # These methods below are modified from qtconsole.rich_jupyter_widget.py

    def _make_contextmenu(self, pos):
        """Reimplemented to return a custom context menu for images."""
        format = self.cursorForPosition(pos).charFormat()
        name = format.stringProperty(QtGui.QTextFormat.Property.ImageName)
        if name:
            menu = QtW.QMenu(self)

            menu.addAction("Copy Image", lambda: self._copy_image(name))
            menu.addAction("Save Image As...", lambda: self._save_image(name))
            menu.addSeparator()
            return menu

    def _copy_image(self, name):
        image = self._get_image(name)
        return QtW.QApplication.clipboard().setImage(image)

    def _save_image(self, name, format="PNG"):
        """Shows a save dialog for the ImageResource with 'name'."""
        dialog = QtW.QFileDialog(self, "Save Image")
        dialog.setAcceptMode(QtW.QFileDialog.AcceptMode.AcceptSave)
        dialog.setDefaultSuffix(format.lower())
        if self._last_save_path is None:
            self._last_save_path = Path.cwd()
        dialog.setDirectory(str(self._last_save_path))
        dialog.setNameFilter(f"{format} file (*.{format.lower()})")
        if dialog.exec_():
            filename = dialog.selectedFiles()[0]
            image = self._get_image(name)
            image.save(filename, format)
            self._last_save_path = Path(filename).parent
        return None

    def _get_image(self, name):
        """Returns the QImage stored as the ImageResource with 'name'."""
        document = self.document()
        image = document.resource(
            QtGui.QTextDocument.ResourceType.ImageResource, QtCore.QUrl(name)
        )
        return image
