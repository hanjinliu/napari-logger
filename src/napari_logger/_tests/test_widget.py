import napari

from napari_logger import NapariLogger


def test_launch(make_napari_viewer):
    viewer: napari.Viewer = make_napari_viewer()
    viewer.window.add_dock_widget(NapariLogger())


def test_print():
    naplogger = NapariLogger()
    print(0)
    assert naplogger.logger.value == ""
    naplogger.checkboxes.printing = True
    print(0)
    assert naplogger.logger.value == "0\n"
