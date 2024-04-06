# Sketchingpy
| Group | Badges |
|-------|--------|
| Status | ![build workflow status](https://ci.codeberg.org/api/badges/12963/status.svg?branch=main) [![Project Status: WIP – Initial development is in progress, but there has not yet been a stable, usable release suitable for the public.](https://www.repostatus.org/badges/latest/wip.svg)](https://www.repostatus.org/#wip) |
| Usage | [![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/release/python-370/) [![Pypi Badge](https://img.shields.io/pypi/v/sketchingpy)](https://pypi.org/project/sketchingpy/) [![License](https://img.shields.io/badge/License-BSD_3--Clause-blue.svg)](https://opensource.org/licenses/BSD-3-Clause) [![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/git/https%3A%2F%2Fcodeberg.org%2Fsketchingpy%2Fexample-jupyter-notebook.git/HEAD?labpath=Sketchingpy+in+Jupyter.ipynb) |
| Documentation | [![Website](https://img.shields.io/badge/website-sketchingpy.org-blue)](https://sketchingpy.org) [![Examples](https://img.shields.io/badge/website-examples-purple)](https://sketchingpy.org/examples.html) [![Reference](https://img.shields.io/badge/website-reference-red)](https://sketchingpy.org/reference.html) [![Guides](https://img.shields.io/badge/website-guides-orange)](https://sketchingpy.org/guides.html) |

Tiny tools for creative coding and interactive science in Python. Supporting portability across [desktop](https://sketchingpy.org/guide/start.html#local), [web](https://sketchingpy.org/guide/start.html#web), [mobile](https://sketchingpy.org/guide/start.html#mobile), [Jupyter notebooks](https://sketchingpy.org/guide/start.html#notebook), and [static images](https://sketchingpy.org/guide/start.html#static). Serving makers of all kinds from experienced designers and developers to educators and students. Includes tools for geospatial visualization.

Learn more online at https://sketchingpy.org.

<br>
<br>

## Quickstart
A first sketch in 7 lines of code ([edit and run this first sketch in your browser](https://sketchingpy.org/examples/web/example.html?sketch=hello_static)):

```
import sketchingpy

sketch = sketchingpy.Sketch2D(500, 500)

sketch.clear('#F0F0F0')
sketch.set_fill('#C0C0C0')
sketch.set_stroke('#000000')
sketch.draw_ellipse(250, 250, 20, 20)

sketch.show()
```

A tiny bit of example interactivity in just over 10 lines ([edit and run this little drawing program in your browser](https://sketchingpy.org/examples/web/example.html?sketch=hello_interactive)):

```
import sketchingpy

sketch = sketchingpy.Sketch2D(500, 500)

def draw():
  mouse = sketch.get_mouse()
  
  x = mouse.get_x()
  y = mouse.get_y()
  
  sketch.set_fill('#C0C0C0')
  sketch.set_stroke('#333333')
  sketch.draw_ellipse(x, y, 20, 20)

sketch.on_step(draw)

sketch.clear('#FFFFFF')

sketch.show()

```

<br>
<br>

## Install
There's multiple ways to use Sketchingpy with different dependencies for different platforms. It will try to operate with what is installed, turning off different functionality when libraries are not available. Note that sketchingpy in the browser will operate as a pure-Python wheel without additional requirements.

<br>

### Online sketchbook
No installation needed! Just get your browser and start quickly using an online private sketchbook (coming soon but a slimmed down editor is available at https://sketchingpy.org/examples/web/example.html).

<br>

### Plain Python: static sketches
Write Python scripts like you usually do and run them from the command line or your IDE. Just grab a few minimal dependencies:

```
$ pip install sketchingpy[static]
```

Note that this will use the `Sketch2DStatic` renderer by default. Learn more about [using sketches inside standard Python programs](https://sketchingpy.org/guide/start.html#local).

<br>

### Plain Python: interactive sketches
For interactive sketches, also install pygame-ce in addition to the static dependencies:

```
$ pip install sketchingpy[desktopall]
```

Note that this will use the `Sketch2DApp` renderer by default. Learn more about [using sketches inside standard Python programs](https://sketchingpy.org/guide/start.html#local). A slightly slimmer distribution without dialog support can also be installed with `sketchingpy[desktopall]`.

<br>

### Jupyter Notebook
Code creatively in Jupyter notebooks with minimal dependencies:

```
$ pip install sketchingpy[notebook]
```

Go deeper and review the [getting started instructions for Jupyter](https://sketchingpy.org/guide/start.html#notebook).

<br>

### Custom web applications
Embed Sketchingpy in your own websites. Simply add this to your [pyscript](https://pyscript.net/) `py-config`:

```
"packages": ["sketchingpy"]
```

Review documentation about [writing sketches for the browser](https://sketchingpy.org/guide/start.html#web) or adding [Sketchingpy into your own web pages](https://sketchingpy.org/guide/deploy.html#web). Note that no additional dependencies are needed and sketchingpy will install as a pure-Python wheel for maximum compatibility. Numpy, matplotlib, etc are not required.

<br>
<br>

## Use
More educational resources coming soon. See [examples](https://sketchingpy.org/examples.html) and [reference](https://sketchingpy.org/reference.html) for now. After you've made something you want to share, [take your creations to the web](https://sketchingpy.org/deploy.html#web) or export your work to [stand-alone executables](https://sketchingpy.org/deploy.html#desktop).

<br>
<br>

## Purpose
This interactive coding tool enables anyone to start creative coding in minutes using Python across multiple platforms including desktop and web. Heavily inspired by [Processing](https://processing.org/), Sketchingpy seeks to bring the philosophy of sketchingpy in code to portable technologies that allow programmers to take their work anywhere. We believe coding should be iterative, fun, and creative at any stage of someone's journey.

<br>

### Goals
Specifically, this project seeks to:

- Enable creative expression in computation through Python.
- Be simple to use, friendly for everyone from beginners to experts.
- Support Mac, Windows, Linux, the browser, Jupyter, and static image generation in headless environments.
- Work in plain old 100% Python with Sketchingpy available as a library, supporting you anywhere in your programming journey.

We hope to reach developers of all skill levels.

<br>

### Use cases
We imagine folks using Sketchingpy for:

- Interactive science
- Data visualization
- Visual art
- Immersive experience
- Simulation
- Sound design
- User experience (UX) prototyping
- Game development

We would love to see what you do and invite contributions to [our showcase](https://sketchingpy.org/showcase.html).

<br>

### Audience
We aim to support teachers, students, artists, designers, developers, and other makers as they make creative programs including visual art, games needing a bit more flexibility, and more. Specifically, this project hopes to embrace a wide group of people:

- Serve programmers no matter where they are in their journey from beginner to expert.
- Support portabilty across desktop (Mac, Windows, Linux), web (browser), notebooks (Jupyter), and static image generation.
- Foster inclusive community across different disciplines within and outside computer science.
- Assist in both formal and informal educational contexts.

If you are interested in this mission, we invite a diverse set of collaborators to join us.

<br>

### Scope
Currently we are only focused on 2D with no explicit console support though Steam Deck should work with the Linux builds.

<br>
<br>

## Grow Sketchingpy
Thank you for your interest in our humble project. Here is how to build Sketchingpy itself and how to participate in our community including contributing code to the project.

<br>

### Environment setup
The recommended packages for development can be installed with the following:

```
$ pip install .[dev]
```

Note that this assumes [pypi and Python3](https://docs.python-guide.org/starting/installation/) are installed.

<br>

### Testing
There are multiple layers of tests to ensure code quality and stability:

 - **Standard unit tests**: Executable with `$ nose2`, this will execute unit tests which do not require actual instantiation of a renderer.
 - **Static tests**: Execution of most static Pillow-based examples to ensure no errors are generated using the Docker image in `ci-image`.
 - **App tests**: Execution of most Pygame-ce-based examples to ensure no errors are generated using the Docker image in `ci-image` and xvfb.
 - **Web tests**: Execution of select web-based examples to ensure no errors are generated using the Docker image in `ci-image` and Selenium. The number of examples is kept low due to resource intensiveness of this stage.

Please ensure all tests pass before merging.

<br>

### Development standards
Please adhere to the following when contributing code to the project:

 - Precedent is most important: please follow the conventions you see in the repository already.
 - Where there isn't precedent, please use the [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html) where possible.
 - All private members should be prefaced with a single underscore.
 - All public members should have Google-style docstrings.
 - All public members should have type hints.
 - Across these different options, the project aims for 90% code coverage.
 - Getters and setters preferred over 

The above represent our ambitions as a project. Please do not let those stop you from opening pull requests if you are not sure how to contribute. We will work with you! Note that we also have formalized some exceptions to those guidelines:

 - Type hints are encouraged but not required for "renderer-native" types.
 - Type hints and docstrings not required for test code.
 - Guidelines encouraged but not required for "support" scripts that are not installed with the library itself.
 - Guidelines encouraged but not required for examples. Authors should determine when the guidelines either improve or hinder readability.

Code should pass pyflakes (`pyflakes sketchingpy/*.py`) and pycodestyle (`pycodestyle sketchingpy/*.py`) should both pass. Furthermore, please ensure mypy succeeds before opening a PR (`mypy sketchingpy/*.py`).

<br>

### Release
Please release using CI / CD where possible which is done automatically when merging to the `main` branch. However, if manual deployment is required:

```
pip install build twine
python3 -m build
twine check dist/*
python3 support/make_twine_config.py
twine upload --config-file ./pypirc dist/*
```

See `support/make_twine_config.py` for additional details.

<br>

### Get involved
Sketchingpy hopes to foster an inclusive community of makers.

- [Let us know about a bug or other issue](https://sketchingpy.org/community/issue.html).
- [Contribute to the code of Sketchingpy itself](https://sketchingpy.org/community/develop.html).
- [Help with documentation](https://sketchingpy.org/community/document.html).
- [Share your work in our showcase](https://sketchingpy.org/community/showcase.html).

Also, [join us in our Discord to share ideas](https://sketchingpy.org/community/discord.html)!

<br>
<br>

## Open Source
Sketchingpy both uses open source and is released under a permissive license.

<br>

### Libraries used
We use and thank the following open source libraries:

 - [Ace Editor](https://ace.c9.io/) under the [BSD License](https://github.com/ajaxorg/ace/blob/master/LICENSE) for the web editor.
 - [bezier](https://bezier.readthedocs.io/en/stable/index.html) under the [Apache v2 License](https://github.com/dhermes/bezier/blob/2023.7.28/LICENSE).
 - [Pillow](https://python-pillow.org/) under the [HPND License](https://github.com/python-pillow/Pillow/blob/main/LICENSE) for `Sketch2D` and `Sketch2DStatic` renderers.
 - [processing-geopoint](https://github.com/SchmidtDSE/processing-geopoint) under the [BSD License](https://github.com/SchmidtDSE/processing-geopoint/blob/main/LICENSE.md).
 - [Pygame-ce](https://pyga.me/) under the [LGPL License](https://github.com/pygame-community/pygame-ce#license) for `Sketch2D` renderer.
 - [Pyscript](https://pyscript.net/) under the [Apache v2 License](https://pyscript.github.io/docs/2023.11.2/license/) for the `Sketch2DWeb` renderer.
 - [Pyodide](https://pyodide.org/en/stable/) under the [MPL 2.0 License](https://github.com/pyodide/pyodide/blob/main/LICENSE) for the `Sketch2DWeb` renderer.

Other code and contributors listed in the code itself or within [the people section of the website](https://sketchingpy.org/community.html#people). Some documentation uses [IBM Plex](https://github.com/IBM/plex) under the [OFL 1.0](https://github.com/IBM/plex/blob/master/LICENSE.txt). Also, some examples colors from <a href="https://colorbrewer2.org">ColorBrewer 2.0</a>.

<br>

### License
Sketchingpy is permissively [BSD licensed](https://codeberg.org/sketchingpy/Sketchingpy/src/branch/main/LICENSE.md) meaning you can use it for commerical and non-commerical projects as well as for your hobbies and for your professional work.
