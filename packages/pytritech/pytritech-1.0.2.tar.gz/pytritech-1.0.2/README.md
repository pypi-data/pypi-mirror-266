# PyTritech

A python interface to the [Tritech](https://www.tritech.co.uk/) GLF files. This project is part of the [WATER Group](https://smru-water.wp.st-andrews.ac.uk/) research project at [SMRU](http://www.smru.st-andrews.ac.uk/), [University of St Andrews](https://www.st-andrews.ac.uk/).

## Installation

To use this library in your own python program we recommend including it as part of a python virtual environment.

    pip install pytritech

or, directly from this repository

    pipt install https://github.com/onidaito/pytritech.git


## Getting started

Once installed, you can begin to read pytritech files as follows:

    from pytritech.glf import GLF 
    import os
    
    assert os.path.exists(glf_path)
    
    with GLF(glf_path) as glf:
        image_data, image_size = glf.extract_image(glf.images[20])

## Documentation

Documentation is available at [https://onidaito.github.io/pytritech/](https://onidaito.github.io/pytritech/).

The documentation can be generated using mkdocs as follows:

    mkdocs serve

## Tests

In order to run the various tests you will need the test data files, which are held in a separate repository. These are automatically downloaded by pytest when the tests are run. If the test takes a while to finish on the first time around, this is why.

There are a number of test dependencies: pillow, gitpython, pyinstrument etc. These can be found in the pyproject.toml file.

You will need to install the git lfs extension for large data files first. Follow the instructions at [https://git-lfs.com/](https://git-lfs.com/).

run the following from the top of the pytritech directory:

    pytest


## Roadmap (or things we haven't implemented yet)

As of version 1.0.0, only the status and image records can be read. Records such as serial, analog video, V4 or generic are not yet supported. In addition, this library is only concerned with GLF files, not controlling the Tritech sonar itself.

In the future, we hope to add support for these remaining record types, but no timeline has been set.