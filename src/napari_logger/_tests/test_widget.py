import napari

from napari_logger import NapariLogger


def test_launch(make_napari_viewer):
    viewer: napari.Viewer = make_napari_viewer()
    viewer.window.add_dock_widget(NapariLogger())


def test_print():
    naplogger = NapariLogger()
    print(0)
    assert naplogger.logger.value == ""
    naplogger.checkboxes.printing.value = True
    print(0)
    assert naplogger.logger.value == "0\n"


def test_html():
    naplogger = NapariLogger()
    naplogger.checkboxes.printing.value = True
    print("<b>0</b>")
    assert naplogger.logger.value == "<b>0</b>\n"
    naplogger.logger.clear()
    naplogger.checkboxes.html.value = True
    print("<b>0</b>")
    assert naplogger.logger.value == "0\n\n"


def test_logging():
    import logging

    logger = logging.getLogger(__name__)
    naplogger = NapariLogger()
    rh_formatter = logging.Formatter("%(levelname)s|| %(message)s")
    naplogger.logger.setFormatter(rh_formatter)

    logger.warning("0")
    assert naplogger.logger.value == ""

    naplogger.checkboxes.logging.value = True
    logger.warning("0")
    assert naplogger.logger.value == "WARNING|| 0\n"


def test_matplotlib():
    import matplotlib.pyplot as plt

    naplogger = NapariLogger()
    naplogger.checkboxes.plotting.value = True

    plt.plot([0, 1, 2])
    plt.show()
