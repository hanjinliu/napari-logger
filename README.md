# napari-logger

[![License BSD-3](https://img.shields.io/pypi/l/napari-logger.svg?color=green)](https://github.com/hanjinliu/napari-logger/raw/main/LICENSE)
[![PyPI](https://img.shields.io/pypi/v/napari-logger.svg?color=green)](https://pypi.org/project/napari-logger)
[![Python Version](https://img.shields.io/pypi/pyversions/napari-logger.svg?color=green)](https://python.org)
[![tests](https://github.com/hanjinliu/napari-logger/workflows/tests/badge.svg)](https://github.com/hanjinliu/napari-logger/actions)
[![codecov](https://codecov.io/gh/hanjinliu/napari-logger/branch/main/graph/badge.svg)](https://codecov.io/gh/hanjinliu/napari-logger)
[![napari hub](https://img.shields.io/endpoint?url=https://api.napari-hub.org/shields/napari-logger)](https://napari-hub.org/plugins/napari-logger)

A logger widget for napari.

![](images/widget.png)

`print`, `logging`, `matplotlib` outputs can be optionally streamed to this widget. No need to rewrite your codes!

#### Magicgui Logger Widget

This plugin also provides a magicgui `Logger` widget. You can integrate logger in your plugins.

```python
from napari_logger import Logger
from magicgui.widgets import Container

container = Container()

logger = Logger()
container.append(logger)
```

----------------------------------

This [napari] plugin was generated with [Cookiecutter] using [@napari]'s [cookiecutter-napari-plugin] template.

<!--
Don't miss the full getting started guide to set up your new package:
https://github.com/napari/cookiecutter-napari-plugin#getting-started

and review the napari docs for plugin developers:
https://napari.org/stable/plugins/index.html
-->

## Installation

You can install `napari-logger` via [pip]:

    pip install napari-logger



To install latest development version :

    pip install git+https://github.com/hanjinliu/napari-logger.git


## Contributing

Contributions are very welcome. Tests can be run with [tox], please ensure
the coverage at least stays the same before you submit a pull request.

## License

Distributed under the terms of the [BSD-3] license,
"napari-logger" is free and open source software

## Issues

If you encounter any problems, please [file an issue] along with a detailed description.

[napari]: https://github.com/napari/napari
[Cookiecutter]: https://github.com/audreyr/cookiecutter
[@napari]: https://github.com/napari
[MIT]: http://opensource.org/licenses/MIT
[BSD-3]: http://opensource.org/licenses/BSD-3-Clause
[GNU GPL v3.0]: http://www.gnu.org/licenses/gpl-3.0.txt
[GNU LGPL v3.0]: http://www.gnu.org/licenses/lgpl-3.0.txt
[Apache Software License 2.0]: http://www.apache.org/licenses/LICENSE-2.0
[Mozilla Public License 2.0]: https://www.mozilla.org/media/MPL/2.0/index.txt
[cookiecutter-napari-plugin]: https://github.com/napari/cookiecutter-napari-plugin

[file an issue]: https://github.com/hanjinliu/napari-logger/issues

[napari]: https://github.com/napari/napari
[tox]: https://tox.readthedocs.io/en/latest/
[pip]: https://pypi.org/project/pip/
[PyPI]: https://pypi.org/
